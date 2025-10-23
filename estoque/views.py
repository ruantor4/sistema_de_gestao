from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.api import success
from django.db import transaction, IntegrityError
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View

from core.utils import registrar_log
from estoque.models import Produto, Movimentacao


# Lista todos produtos
class ListarEstoqueView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest) -> HttpResponse:
        try:
            produtos = Produto.objects.all()
        except Exception as e:
            messages.error(request, f"Erro ao carregar produtos: {str(e)}")
            registrar_log(request.user, "error", None, f"Erro ao listar produtos: {str(e)}")
            produtos = []
        return render(request, "estoque/listar.html", {"produtos": produtos})


# Lista de movimentações
class ListarMovimentacaoView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest) -> HttpResponse:
        try:
            movimentacoes = Movimentacao.objects.all()
        except Exception as e:
            messages.error(request, f"Erro ao carregar movimentacoes: {str(e)}")
            registrar_log(request.user, "error", None, f"Erro ao listar produtos: {str(e)}")
            movimentacoes = []
        return render(request, 'movimentacoes/listar_movimentacao.html', {'movimentacoes': movimentacoes})


# Registro das movimentações
class RegistrarMovimentacaoView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest) -> HttpResponse:
        try:
            produtos = Produto.objects.all()
        except Exception as e:
            messages.error(request, f"Erro ao carregar produtos: {str(e)}")
            registrar_log(request.user, "error", None, f"Erro ao carregar produtos no formulário de movimentação: {str(e)}")
            produtos = []
        return render(request, 'movimentacoes/form.html', {'produtos': produtos})

    def post(self, request: HttpRequest) -> HttpResponse:
        produto_id = request.POST.get('produto')
        tipo = request.POST.get('tipo')
        quantidade = int(request.POST.get('quantidade', 0))

        try:
            produto = get_object_or_404(Produto, id=produto_id)

            # Verifica o tipo de operação, soma ou subtrai
            if tipo == 'entrada':
                produto.quantidade += quantidade
            elif tipo == 'saida':
                if quantidade > produto.quantidade:
                    messages.error(request, f'Estoque insuficiente para saída de {quantidade} unidades.')
                    return redirect('registrar_movimentacao')
                produto.quantidade -= quantidade
            else:
                messages.error(request, 'tipo de movimentação inválida')
                return redirect('registrar_movimentacao')

            with transaction.atomic():
                produto.save()
                mov = Movimentacao.objects.create(
                    usuario=request.user,
                    produto=produto,
                    tipo=tipo,
                    quantidade=quantidade
                )
                registrar_log(request.user, success, mov, f"Movimentação '{tipo}' registrada com sucesso para o produto '{produto.nome}'.")
            messages.success(request, 'Movimentação registrada com sucesso!')
            return redirect('listar_movimentacao')

        except Exception as e:
            messages.error(request, f"Erro ao registrar movimentações: {str(e)}")
            registrar_log(request.user,"error", None, f"Erro ao registrar movimentações: {str(e)}")
            return redirect('listar_movimentacao')


# Realiza busca de produtos pelo nome.
class BuscarProdutosView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest) -> HttpResponse:
        termo = request.GET.get('q', '').strip()

        try:
            produtos = Produto.objects.filter(nome__icontains=termo) if termo else Produto.objects.none()
        except Exception as e:
            messages.error(request, f"Erro ao buscar produtos: {str(e)}")
            registrar_log(request.user, f"Erro ao buscar produtos: {str(e)}")
            produtos = Produto.objects.none()
        return render(request, 'estoque/listar.html', {'produtos': produtos, 'termo': termo})


# Exibe detalhes do produto, incluindo entradas, saidas e saldo em estoque
class DetalheProdutoView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        try:
            produto = get_object_or_404(Produto, id=produto_id)
            # Total das movimentaçoes
            entradas = (
                Movimentacao.objects.filter(tipo='entrada')
                .aggregate(Sum('quantidade'))['quantidade__sum'] or 0
            )
            saidas = (
                Movimentacao.objects.filter(tipo='saida')
                .aggregate(Sum('quantidade'))['quantidade__sum'] or 0
            )
            saldo = entradas - saidas
        except Exception as e:
            messages.error(request, f"Erro ao carregar detalhes do produto: {str(e)}")
            registrar_log(request.user,messages.ERROR, None, f"Erro ao carregar detalhes do produto: {str(e)}")

        return render(request, 'estoque/detalhe_produto.html', {
            'produto': produto,
            'entradas': entradas,
            'saidas': saidas,
            'saldo': saldo
        })


# Cria um novo produto no estoque.
class CriarProdutoView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "estoque/produtos_form.html")

    def post(self, request: HttpRequest) -> HttpResponse:
        nome = request.POST.get("nome")
        descricao = request.POST.get("descricao")
        quantidade = request.POST.get("quantidade")
        localizacao = request.POST.get("localizacao")
        imagem = request.FILES.get("imagem")
        datasheet = request.FILES.get("datasheet")

        try:
            with transaction.atomic():
                produto = Produto(
                    nome=nome,
                    descricao=descricao,
                    quantidade=quantidade,
                    localizacao=localizacao,
                    imagem=imagem,
                    datasheet=datasheet
                )
                produto.save()
                registrar_log(request.user, success, produto, f"Produto '{nome}' registrado com sucesso.")

            messages.success(request, "Produto criado com sucesso!")
            return redirect("listar_estoque")

        except IntegrityError as e:
            messages.error(request, "Erro de integridade ao criar produto")
            registrar_log(request.user, "error", None, "Erro de integridade ao criar produto.")
            return redirect("criar_produto")
        except Exception as e:
            messages.error(request, f"Erro ao criar produto: {str(e)}")
            registrar_log(request.user, "error", None, f"Erro ao criar produto: {str(e)}")
            return redirect("criar_produto")


# Edita os dados de um produto existente
class EditarProdutoView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        try:
            produto = get_object_or_404(Produto, id=produto_id)
        except Exception as e:
            messages.error(request, f"Erro ao carregar produto: {str(e)}")
            registrar_log(request.user, "error", None, f"Erro ao carregar produto para edição: {str(e)}.")
            return redirect("listar_estoque")
        return render(request, "estoque/produtos_form.html", {"produto": produto})

    def post(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        try:
            produto = get_object_or_404(Produto, id=produto_id)
            produto.nome = request.POST.get("nome")
            produto.descricao = request.POST.get("descricao")
            produto.quantidade = request.POST.get("quantidade")
            produto.localizacao = request.POST.get("localizacao")

            if request.FILES.get("imagem"):
                produto.imagem = request.FILES.get("imagem")

            if request.FILES.get("datasheet"):
                produto.datasheet = request.FILES.get("datasheet")

            produto.save()
            registrar_log(request.user,messages.SUCCESS, "Produto atualizado com sucesso.")
            messages.success(request, "Produto atualizado com sucesso!")
            return redirect("listar_estoque")

        except Exception as e:
            messages.error(request, f"Erro ao atualizar produto: {str(e)}")
            registrar_log(request.user, "error", None, f"Erro ao atualizar produto {produto_id}: {str(e)}")
            return redirect("editar_produto", produto_id=produto_id)

# Remove produtos do estoque
class DeletarProdutoView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        try:
            produto = get_object_or_404(Produto, id=produto_id)
        except Exception as e:
            messages.error(request, f"Erro ao carregar produto: {str(e)}")
            registrar_log(request.user, messages.ERROR, None, f"Erro ao carregar produto {produto_id} para exclusão: {str(e)}")
            return redirect("listar_estoque")
        return render(request, 'listar_estoque')

    def post(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        try:
            produto = get_object_or_404(Produto, id=produto_id)
            produto.delete()
            registrar_log(request.user, messages.SUCCESS, None, f"Produto '{produto.nome}' deletado com sucesso.")
            messages.success(request, "Produto deletado com sucesso!")
            return redirect('listar_estoque')

        except Exception as e:
            messages.error(request, f"Erro ao deletar produto: {str(e)}")
            registrar_log(request.user, messages.ERROR, None, f"Erro ao deletar produto {produto_id}: {str(e)}")
            return redirect('listar_estoque')
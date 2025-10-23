
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse, request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View

from estoque.models import Produto, Movimentacao


# Lista todos produtos
class ListarEstoqueView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest) -> HttpResponse:
        produtos = Produto.objects.all()
        return render(request, "estoque/listar.html", {"produtos": produtos})


# Lista de movimentações
class ListarMovimentacaoView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest) -> HttpResponse:
        movimentacoes = Movimentacao.objects.all()
        return render(request, 'movimentacoes/listar_movimentacao.html', {'movimentacoes': movimentacoes})


# Registro das movimentações
class RegistrarMovimentacaoView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest) -> HttpResponse:
        produtos = Produto.objects.all()
        return render(request, 'movimentacoes/form.html', {'produtos': produtos})

    def post(self, request: HttpRequest) -> HttpResponse:
        produto_id = request.POST.get('produto')
        tipo = request.POST.get('tipo')
        quantidade = int(request.POST.get('quantidade', 0))
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

        produto.save()
        # Pega o usuario logado e registra a movimentação
        Movimentacao.objects.create(
            usuario=request.user,
            produto=produto,
            tipo=tipo,
            quantidade=quantidade
        )
        messages.success(request, 'Movimentação registrada com sucesso!')
        return redirect('listar_movimentacao')



# Realiza busca de produtos pelo nome.
class BuscarProdutosView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest) -> HttpResponse:
        termo = request.GET.get('q', '').strip()
        produtos = Produto.objects.none()
        if termo:
            produtos = Produto.objects.filter(nome__icontains=termo)
        return render(request, 'estoque/listar.html', {'produtos': produtos, 'termo': termo})


# Exibe detalhes do produto, incluindo entradas, saidas e saldo em estoque
class DetalheProdutoView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, produto_id: int) -> HttpResponse:
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

    def post(self, request: HttpRequest, produto_id) -> HttpResponse:
        nome = request.POST.get("nome")
        descricao = request.POST.get("descricao")
        quantidade = request.POST.get("quantidade")
        localizacao = request.POST.get("localizacao")
        imagem = request.FILES.get("imagem")
        datasheet = request.FILES.get("datasheet")

        produto = Produto(
            nome=nome,
            descricao=descricao,
            quantidade=quantidade,
            localizacao=localizacao,
            imagem=imagem,
            datasheet=datasheet
        )
        produto.save()
        messages.success(request, "Produto criado com sucesso!")
        return redirect("listar_estoque")


# Edita os dados de um produto existente
class EditarProdutoView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        produto = get_object_or_404(Produto, id=produto_id)
        return render(request, "estoque/produtos_form.html", {"produto": produto})

    def post(self, request: HttpRequest, produto_id: int) -> HttpResponse:
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
        messages.success(request, "Produto atualizado com sucesso!")
        return redirect("listar_estoque")


# Remove produtos do estoque
class DeletarProdutoView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        produto = get_object_or_404(Produto, id=produto_id)
        return render(request, 'listar_estoque')

    def post(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        produto = get_object_or_404(Produto, id=produto_id)
        produto.delete()
        messages.success(request, "Produto deletado com sucesso!")
        return redirect('listar_estoque')

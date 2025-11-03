from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError, DatabaseError
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View

from core.utils import registrar_log
from estoque.models import Produto, Movimentacao
from estoque.utils import validar_produto


class ListarMovimentacaoView(LoginRequiredMixin, View):
    """
        View responsável por listar todas as movimentações de estoque.

        Métodos:
            get: Retorna a página com a listagem de movimentações.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Obtém todas as movimentações registradas no sistema e as exibe em uma tabela.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.

            Returns:
                django.http.HttpResponse: Página HTML contendo a lista de movimentações.
        """
        try:
            movimentacoes = Movimentacao.objects.all()

        except DatabaseError:
            messages.error(request, "Erro de banco de dados ao carregar movimentações.")
            movimentacoes = []

        except Exception as e:
            messages.error(request, f"Erro ao carregar movimentacoes: {str(e)}")
            registrar_log(request.user if request.user.is_authenticated else None, "Listar Movimentações", "ERROR", f"Erro ao listar movimentações: {str(e)}")
            movimentacoes = []

        return render(request, 'movimentacoes/listar_movimentacao.html', {'movimentacoes': movimentacoes})


class RegistrarMovimentacaoView(LoginRequiredMixin, View):
    """
         View responsável por registrar entradas e saídas de produtos no estoque.

         Métodos:
             get: Exibe o formulário de movimentação.
             post: Processa o registro de movimentação no banco de dados.
     """
    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Exibe o formulário para registrar uma nova movimentação.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.

            Returns:
                django.http.HttpResponse: Página HTML com o formulário de movimentação.
        """
        try:
            produtos = Produto.objects.all()

        except DatabaseError:
            messages.error(request, "Erro de banco de dados ao carregar produtos.")
            produtos = []

        except Exception as e:
            messages.error(request, f"Erro ao Registar Movimentação: {str(e)}")
            registrar_log(request.user if request.user.is_authenticated else None, "Registar Movimentação", "ERROR",
                          f"Erro ao carregar produtos no formulário de movimentação: {str(e)}")
            produtos = []

        return render(request, 'movimentacoes/form.html', {'produtos': produtos})

    def post(self, request: HttpRequest) -> HttpResponse:
        """
            Registra uma movimentação de entrada ou saída de produto.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.

            Returns:
                django.http.HttpResponse: Redireciona para a listagem de movimentações após o registro.
        """
        produto_id = request.POST.get('produto')
        tipo = request.POST.get('tipo')
        quantidade_str = request.POST.get('quantidade', "").strip()

        if not quantidade_str.isdigit() or int(quantidade_str) <= 0:
            messages.error(request, "Informe uma quantidade válida e positiva.")
            return redirect('registrar_movimentacao')

        quantidade = int(quantidade_str)

        try:
            with transaction.atomic():
                produto = Produto.objects.select_for_update().get(id=produto_id)

                if tipo not in ['entrada', 'saida']:
                    messages.error(request, "Tipo de movimentação invalido")
                    return redirect('registrar_movimentacao')

                if tipo == 'saida' and produto.quantidade < quantidade:
                    messages.error(request, f"Estoque insuficiente! O produto '{produto.nome}' possui apenas {produto.quantidade} unidades disponíveis.")
                    return redirect('registrar_movimentacao')

                if tipo == 'entrada':
                    produto.quantidade += quantidade
                else:
                    produto.quantidade -= quantidade

                produto.save()

                Movimentacao.objects.create(
                    usuario=request.user,
                    produto=produto,
                    tipo=tipo,
                    quantidade=quantidade
                )
            messages.success(request, 'Movimentação registrada com sucesso!')
            return redirect('listar_movimentacao')

        except Produto.DoesNotExist:
            messages.error(request, "Movimentação não encontrado.")
            return redirect('registrar_movimentacao')

        except Exception as e:
            messages.error(request, f"Erro ao registrar movimentações: {str(e)}")
            registrar_log(request.user if request.user.is_authenticated else None, "Registrar Movimentação", "ERROR", f"Erro ao registrar movimentações: {str(e)}")
            return redirect('listar_movimentacao')


class ListarEstoqueView(LoginRequiredMixin, View):
    """
         View responsável por listar todos os produtos disponíveis no estoque.

         Métodos:
             get: Exibe a lista de produtos cadastrados.
     """
    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Carrega e exibe todos os produtos disponíveis no estoque.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.

            Returns:
                django.http.HttpResponse: Página HTML com a lista de produtos.
        """
        try:
            produtos = Produto.objects.all()

        except DatabaseError:
            messages.error(request, "Erro de banco de dados ao carregar produtos.")
            produtos = []

        except Exception as e:
            messages.error(request, f"Erro ao carregar produtos: {str(e)}")
            registrar_log(request.user if request.user.is_authenticated else None, "Listar Produtos", "ERROR",
                          f"Erro ao listar produtos: {str(e)}")
            produtos = []

        return render(request, "estoque/listar.html", {"produtos": produtos})

class BuscarProdutosView(LoginRequiredMixin, View):
    """
        View responsável por realizar a busca de produtos no estoque.

        Métodos:
            get: Filtra os produtos pelo nome informado na busca.
    """
    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Busca produtos com base no termo informado pelo usuário.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.

            Returns:
                django.http.HttpResponse: Página HTML com os resultados da busca.
        """
        termo = request.GET.get('q', '').strip()

        try:
            produtos = Produto.objects.filter(nome__icontains=termo) if termo else Produto.objects.none()

        except Produto.DoesNotExist:
            messages.error(request, "Produto não encontrado.")
            return redirect('buscar_produtos')

        except Exception as e:
            messages.error(request, f"Erro ao buscar produtos: {str(e)}")
            registrar_log(request.user if request.user.is_authenticated else None, "Buscar Produtos", "ERROR", f"Erro ao buscar produtos: {str(e)}")
            produtos = Produto.objects.none()

        return render(request, 'estoque/listar.html', {'produtos': produtos, 'termo': termo})


class DetalheProdutoView(LoginRequiredMixin, View):
    """
         View responsável por exibir os detalhes de um produto específico.

         Métodos:
             get: Exibe as informações e movimentações do produto selecionado.
     """
    def get(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        """
            Exibe os detalhes, movimentações e saldo do produto.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.
                produto_id (int): ID do produto a ser detalhado.

            Returns:
                django.http.HttpResponse: Página HTML com os detalhes do produto.
        """
        try:
            produto = get_object_or_404(Produto, id=produto_id)
            entradas = (
                    Movimentacao.objects.filter(tipo='entrada', produto=produto)
                    .aggregate(Sum('quantidade'))['quantidade__sum'] or 0
            )
            saidas = (
                    Movimentacao.objects.filter(tipo='saida', produto=produto)
                    .aggregate(Sum('quantidade'))['quantidade__sum'] or 0
            )
            saldo = produto.quantidade

        except Exception as e:
            messages.error(request, f"Erro ao carregar detalhes do produto: {str(e)}")
            registrar_log(request.user if request.user.is_authenticated else None, "Detalhes Produto", "ERROR", f"Erro ao carregar detalhes do produto: {str(e)}")
            return redirect('listar_estoque')

        return render(request, 'estoque/detalhe_produto.html', {
            'produto': produto,
            'entradas': entradas,
            'saidas': saidas,
            'saldo': saldo
        })


class CriarProdutoView(LoginRequiredMixin, View):
    """
        View responsável pela criação de novos produtos no sistema.

        Métodos:
            get: Exibe o formulário de criação de produto.
            post: Processa e salva o novo produto no banco de dados.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Exibe o formulário para criação de um novo produto.
        """
        try:
            return render(request, "estoque/produtos_form.html")

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Criar Produto", "ERROR", f"Erro ao carregar pagina: {str(e)}")
            return redirect('listar_estoque')

    def post(self, request: HttpRequest) -> HttpResponse:
        """
            Cria um novo produto com base nas informações enviadas pelo formulário.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.

            Returns:
                django.http.HttpResponse: Redireciona para a listagem de produtos após criação.
        """
        nome = request.POST.get("nome")
        descricao = request.POST.get("descricao")
        quantidade_str = request.POST.get("quantidade", "").strip()
        localizacao = request.POST.get("localizacao")
        imagem = request.FILES.get("imagem")
        datasheet = request.FILES.get("datasheet")

        try:
            quantidade = int(quantidade_str)
        except ValueError:
            quantidade = None

        if not validar_produto(request, nome, localizacao, quantidade):
            return redirect('criar_produto')

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
                messages.success(request, "Produto criado com sucesso!")
            return redirect("listar_estoque")

        except ValidationError:
            messages.error(request, f"Erro de validação")
            return redirect("criar_produto")

        except IntegrityError:
            messages.error(request, "Erro de integridade ao criar produto")
            return redirect("criar_produto")

        except Exception as e:
            messages.error(request, f"Erro ao criar produto: {str(e)}")
            registrar_log(request.user if request.user.is_authenticated else None, "Criar Produto", "ERROR", f"Erro ao criar produto: {str(e)}")
            return redirect("criar_produto")


class EditarProdutoView(LoginRequiredMixin, View):
    """
        View responsável por editar produtos existentes no estoque.

        Métodos:
            get: Exibe o formulário com os dados do produto.
            post: Atualiza o produto no banco de dados.
    """
    def get(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        """
            Exibe o formulário preenchido com os dados do produto selecionado.
        """
        try:
            produto = get_object_or_404(Produto, id=produto_id)
            return render(request, "estoque/produtos_form.html", {"produto": produto})

        except Exception as e:
            messages.error(request, f"Erro ao carregar tela de edição: {str(e)}")
            registrar_log(request.user if request.user.is_authenticated else None, "Editar Produto", 'ERROR',
                          f"Erro ao carregar produto para edição: {str(e)}.")
            return redirect("listar_estoque")

    def post(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        """
            Atualiza os dados do produto após validação.
        """
        nome = request.POST.get("nome")
        descricao = request.POST.get("descricao")
        quantidade_str = request.POST.get("quantidade", "").strip()
        localizacao = request.POST.get("localizacao")

        try:
            quantidade = int(quantidade_str)
        except ValueError:
            quantidade = None

        if not validar_produto(request, nome, localizacao, quantidade):
            return redirect("editar_produto", produto_id=produto_id)

        try:
            with transaction.atomic():
                produto = get_object_or_404(Produto, id=produto_id)

                produto.nome = nome
                produto.descricao = descricao
                produto.localizacao = localizacao
                produto.quantidade = quantidade

                if request.FILES.get("imagem"):
                    produto.imagem = request.FILES.get("imagem")

                if request.FILES.get("datasheet"):
                    produto.datasheet = request.FILES.get("datasheet")

                produto.save()
                messages.success(request, "Produto atualizado com sucesso!")
            return redirect("listar_estoque")

        except ValidationError as e:
            messages.error(request, f"Erro ao atualizar produto: {str(e)}")
            return redirect('editar_produto', produto_id=produto_id)

        except IntegrityError:
            messages.error(request, "Erro de integridade ao atualizar produto.")
            return redirect("editar_produto", produto_id=produto_id)

        except Exception as e:
            messages.error(request, f"Erro inesperado ao atualizar produto: {str(e)}")
            registrar_log(request.user if request.user.is_authenticated else None, 'Atualizar Produto', 'ERROR',
                  f"Erro inesperado ao atualizar produto ID {produto_id}: {str(e)}")
            return redirect('editar_produto', produto_id=produto_id)


class DeletarProdutoView(LoginRequiredMixin, View):
    """
        View responsável por excluir produtos do sistema.

        Métodos:
            get: Exibe a página de confirmação de exclusão.
            post: Exclui o produto do banco de dados.
    """
    def get(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        """
            Exibe a página de confirmação para exclusão de um produto.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.
                produto_id (int): ID do produto a ser deletado.

            Returns:
                django.http.HttpResponse: Página HTML de confirmação.
        """
        try:
            produto = get_object_or_404(Produto, id=produto_id)
            return render(request, "estoque/produtos_confirm_delete.html", {"produto": produto})

        except Produto.DoesNotExist:
            messages.error(request, "Operação invalida")
            return redirect('listar_estoque')

        except Exception as e:
            messages.error(request, f"Erro ao carregar produto: {str(e)}")
            registrar_log(request.user if request.user.is_authenticated else None, "Deletar Produto", "ERROR",
                          f"Erro ao carregar produto {produto_id} para exclusão: {str(e)}")
            return redirect("listar_estoque")

    def post(self, request: HttpRequest, produto_id: int) -> HttpResponse:
        """
            Exclui definitivamente um produto do banco de dados.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.
                produto_id (int): ID do produto a ser excluído.

            Returns:
                django.http.HttpResponse: Redireciona para a listagem após exclusão.
        """
        try:
            produto = Produto.objects.get(id=produto_id)
            nome= produto.nome
            produto.delete()
            messages.success(request, "Produto deletado com sucesso!")
            return redirect('listar_estoque')

        except Produto.DoesNotExist:
            messages.error(request, "Produto não encontrado.")
            return redirect("listar_produtos")

        except Exception as e:
            messages.error(request, f"Erro ao deletar produto: {str(e)}")
            registrar_log(request.user if request.user.is_authenticated else None, "Deletar Produto", "ERROR",
                          f"Erro ao deletar produto {produto_id}: {str(e)}")
            return redirect('listar_estoque')


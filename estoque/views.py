from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from estoque.models import Produto, Movimentacao


# Lista todos produtos
@login_required(login_url='/login')
def listar_estoque(request):
    produtos = Produto.objects.all()
    return render(request, "produtos/listar.html", {"produtos": produtos})

# Lista de movimentações
@login_required(login_url='/login')
def listar_movimentacao(request):
    movimentacoes = Movimentacao.objects.all()
    return render(request, 'movimentacoes/listar_movimentacao.html', {'movimentacoes': movimentacoes})

# Registro das movimentações
@login_required(login_url='/login')
def registrar_movimentacao(request):
    if request.method == 'POST':
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
            messages.erro(request, 'tipo de movimentação inválida')
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

    produtos = Produto.objects.all()
    return render(request, 'movimentacoes/form.html', {'produtos': produtos})

# Realiza busca de produtos pelo nome.
@login_required(login_url='/login')
def buscar_produtos(request):
    termo = request.GET.get('q', '').strip()
    produtos = Produto.objects.none()

    if termo:
        produtos = Produto.objects.filter(nome__icontains=termo)
    return render(request, 'produtos/listar.html', {'produtos': produtos, 'termo': termo})

# Exibe detalhes do produto, incluindo entradas, saidas e saldo em estoque
@login_required(login_url='/login')
def detalhe_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    # Total das movimentaçoes
    entradas = Movimentacao.objects.filter(tipo='entrada').aggregate(Sum('quantidade'))['quantidade__sum'] or 0
    saidas = Movimentacao.objects.filter(tipo='saida').aggregate(Sum('quantidade'))['quantidade__sum'] or 0

    saldo = entradas - saidas

    return render(request, 'produtos/detalhe_produto.html', {
        'produto': produto,
        'entradas': entradas,
        'saidas': saidas,
        'saldo': saldo
    })

# Cria um novo produto no estoque.
@login_required(login_url='/login')
def criar_produto(request):
    if request.method == "POST":
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
    return render(request, "produtos/produtos_form.html")

# Edita os dados de um produto existente
@login_required(login_url='/login')
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == "POST":
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
    return render(request, "produtos/produtos_form.html", {"produto": produto})

# Remove produtos do estoque
@login_required(login_url='/login')
def deletar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    produto.delete()
    messages.success(request, "Produto deletado com sucesso!")
    return redirect('listar_estoque')

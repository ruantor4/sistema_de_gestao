from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from estoque.models import Produto


# Create your views here.
def listar_estoque(request):
    produtos = Produto.objects.all()
    return render(request, "produtos/listar.html", {"produtos": produtos})


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

@login_required(login_url='/login')
def deletar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    produto.delete()
    messages.success(request, "Produto deletado com sucesso!")
    return redirect('listar_estoque')

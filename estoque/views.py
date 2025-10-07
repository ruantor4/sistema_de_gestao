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

def criar_produto(request):
    if request.method == "POST":
        nome = request.POST.get("nome")

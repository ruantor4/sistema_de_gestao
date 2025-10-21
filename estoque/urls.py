"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from itertools import product

from django.contrib import admin
from django.urls import path, include

from estoque.views import ListarEstoqueView, DetalheProdutoView, BuscarProdutosView, CriarProdutoView, \
    EditarProdutoView, DeletarProdutoView, ListarMovimentacaoView, RegistrarMovimentacaoView

urlpatterns = [

    # Lista todos os produtos no estoque
    path('', ListarEstoqueView.as_view(), name='listar_estoque'),

    # Lista Produto especifico por ID
    path('<int:produto_id>/',DetalheProdutoView.as_view(), name='detalhe_produto'),

    # Busca produtos
    path('buscar/', BuscarProdutosView.as_view(), name='buscar_produtos'),

    # Criação de um novo produto
    path('criar_produto/', CriarProdutoView.as_view(), name='criar_produto'),

    # Edita um produto existente pelo ID
    path('editar_produto/<int:produto_id>/', EditarProdutoView.as_view(), name='editar_produto'),

    # Deleta um produto existente pelo ID
    path('deletar_produto/<int:produto_id>/', DeletarProdutoView.as_view(), name='deletar_produto'),

    # Lista todas as movimentações de estoque
    path('movimentacoes/', ListarMovimentacaoView.as_view(), name='listar_movimentacao'),

    # Registrar nova movimentação (entrada/saída)
    path('movimentacoes/registrar/', RegistrarMovimentacaoView.as_view(), name='registrar_movimentacao'),
]

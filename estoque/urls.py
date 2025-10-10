"""
URL configuration for gestao project.

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

from estoque import views

urlpatterns = [

    path('estoque/', views.listar_estoque, name='listar_estoque'),
    path('estoque/<int:produto_id>/', views.detalhe_produto, name='detalhe_produto'),
    path('buscar/', views.buscar_produtos, name='buscar_produtos'),
    path('criar_produto/', views.criar_produto, name='criar_produto'),
    path('editar_produto/<int:produto_id>/', views.editar_produto, name='editar_produto'),
    path('deletar_produto/<int:produto_id>/', views.deletar_produto, name='deletar_produto'),
    path('movimentacoes/', views.listar_movimentacao, name='listar_movimentacao'),
    path('movimentacoes/registrar/', views.registrar_movimentacao, name='registrar_movimentacao'),
]

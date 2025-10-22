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
from django.urls import path

from estoque.views import ListarEstoqueView
from user import views
from user.views import PedidoResetSenha, ConfirmacaoResetSenhaView, CriarUsuarioView, DeleteUsuarioView, \
    EditarUsuarioView, ListarUsuariosView

urlpatterns = [

    # Recuperação de senha
    path('reset-password/', PedidoResetSenha.as_view(), name='pedido_reset_senha'),
    path('reset_password/<uidb64>/<token>/', ConfirmacaoResetSenhaView.as_view(), name='confirmacao_reset_senha'),

    # Gestão de usuários
    path('listar/', ListarUsuariosView.as_view(), name='listar_usuarios'),
    path('criar/', CriarUsuarioView.as_view(), name='criar_usuario'),
    path('deletar/<int:usuario_id>/', DeleteUsuarioView.as_view(), name='deletar_usuario'),
    path('editar/<int:usuario_id>/', EditarUsuarioView.as_view(), name='editar_usuario'),

]


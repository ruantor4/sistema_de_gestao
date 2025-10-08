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
from django.urls import path

from user import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('reset-password/', views.pedido_reset_senha, name='pedido_reset_senha'),
    path('reset_password/<uidb64>/<token>/', views.confirmacao_reset_senha, name='confirmacao_reset_senha'),
    path('login/submit', views.submit_login),
    path('listar/', views.listar_usuarios, name='listar_usuarios'),
    path('criar/', views.criar_usuario, name='criar_usuario'),
    path('deletar/<int:usuario_id>/', views.deletar_usuario, name='deletar_usuario'),
    path('editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),

]

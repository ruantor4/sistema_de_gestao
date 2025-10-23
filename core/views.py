from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.messages import success
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from core.utils import registrar_log


class HomeView(LoginRequiredMixin, View): #
    """
        View da página inicial do sistema.

        Esta view exibe a página principal apenas para usuários autenticados.
        Caso o usuário não esteja logado, será redirecionado para a página de login.

        Attributes:
            login_url (str): URL para redirecionamento caso o usuário não esteja logado.
    """
    login_url = '/login/'

    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Renderiza a página inicial do sistema.

            Args:
                request (django.http.HttpRequest): Objeto de requisição HTTP.

            Returns:
                django.http.HttpResponse: Resposta HTTP com a página home.
        """
        try:
            return render(request, 'core/home.html')
        except Exception as e:
            registrar_log(request.user,'Acessar Home', 'ERROR', str(e))
            messages.error(request, "Erro ao carregar a página inicial do sistema.")
            return redirect('login')

class LoginView(View):
    """
        View para exibir e processar o formulário de login.

        Métodos:
            get: Renderiza o formulário de login.
            post: Processa os dados do formulário, autentica o usuário e realiza login.
    """
    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Exibe a página de login.

            Se o usuário já estiver autenticado, será redirecionado para a home.

            Args:
                request (django.http.HttpRequest): Objeto de requisição HTTP.

            Returns:
                django.http.HttpResponse: Resposta HTTP com a página de login ou redirecionamento.
        """
        try:
            if request.user.is_authenticated:
                return redirect('home')
            return render(request, 'core/login.html')
        except Exception as e:
            registrar_log(request.user,'Acessar Login', 'ERROR', str(e))
            messages.error(request, "Erro ao carregar a página de login.")
            return redirect('login')


    def post(self, request:HttpRequest) -> HttpResponse:
        """
            Processa o login do usuário.

            Captura os campos 'username' e 'password' do formulário,
            autentica o usuário e cria a sessão. Caso falhe,
            adiciona uma mensagem de erro e retorna ao login.

            Args:
                request (django.http.HttpRequest): Objeto de requisição HTTP.

            Returns:
                django.http.HttpResponse: Redireciona para home se login for bem-sucedido,
                ou retorna à página de login em caso de erro.
        """
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            usuario = authenticate(request, username=username, password=password)
            if usuario is not None:
                login(request, usuario)
                registrar_log(usuario, 'Login', 'SUCCESS', f'{username} fez login com sucesso!.')
                return redirect('home')
            else:
                messages.error(request, "Usuário ou senha incorretos.")
                return render(request, 'core/login.html')
        except Exception as e:
            registrar_log(request.user,'Login', 'ERROR', str(e))
            messages.error(request, "Erro inesperado ao processar o login." )
            return redirect('login')


class LogoutView(View):
    """
        View para realizar o logout do usuário.

        Este view encerra a sessão do usuário e redireciona para a página de login.
    """
    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Efetua o logout do usuário e redireciona para login.

            Args:
                request (django.http.HttpRequest): Objeto de requisição HTTP.

            Returns:
                django.http.HttpResponse: Redireciona para a página de login.
        """
        try:
            username = request.user.username if request.user.is_authenticated else 'Usuário desconhecido'
            if request.user.is_authenticated:
                logout(request)
                registrar_log(request.user, 'Logout', success, f'{username} fez logout com sucesso!.')

            return redirect('login')
        except Exception as e:
            registrar_log(request.user,'Logout', 'ERROR', str(e))
            messages.error(request, "Erro inesperado ao encerrar a sessão.")
            return redirect('login')


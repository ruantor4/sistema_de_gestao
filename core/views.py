from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from core.utils import registrar_log


class HomeView(LoginRequiredMixin, View):  #
    """
        Exibe a página inicial do sistema.

        Permite o acesso apenas a usuários autenticados. Caso o usuário não esteja
        logado, ele é redirecionado para a página de login.

        Attributes:
            login_url (str): URL para redirecionamento caso o usuário não esteja autenticado.
    """
    login_url = '/login/'

    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Renderiza a página principal do sistema.

            Args:
                request (HttpRequest): Objeto de requisição HTTP.

            Returns:
                HttpResponse: Página principal se carregada com sucesso,
                ou redirecionamento para a página de login em caso de erro.
        """
        try:
            return render(request, 'core/home.html')

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Acessar Home", "ERROR", f"Erro ao carregar pagina: {str(e)}")
            messages.error(request, "Erro ao carregar a página inicial do sistema.")
            return redirect('login')


class LoginView(View):
    """
        Gerencia o processo de autenticação de usuários.

        Métodos:
            get: Exibe o formulário de login.
            post: Processa as credenciais e autentica o usuário.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Exibe a página de login.

            Caso o usuário já esteja autenticado, é redirecionado para a página inicial.

            Args:
                request (HttpRequest): Objeto de requisição HTTP.

            Returns:
                HttpResponse: Página de login ou redirecionamento para a home.
        """
        try:
            if request.user.is_authenticated:
                return redirect('home')
            return render(request, 'core/login.html')

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Acessar Login", "ERROR", f"Erro inesperado:{str(e)}")
            messages.error(request, "Erro ao carregar a página de login.")
            return redirect('login')

    def post(self, request: HttpRequest) -> HttpResponse:
        """
            Processa a autenticação do usuário.

            Captura os campos 'username' e 'password' do formulário,
            realiza a autenticação e cria a sessão do usuário.
            Caso as credenciais estejam incorretas, exibe uma mensagem de erro.

            Args:
                request (HttpRequest): Objeto de requisição HTTP.

            Returns:
                HttpResponse: Redireciona para a home se o login for bem-sucedido,
                ou retorna à página de login em caso de falha.
        """
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            usuario = authenticate(request, username=username, password=password)
            if usuario is not None:
                login(request, usuario)
                return redirect('home')
            else:
                messages.error(request, "Usuário ou senha incorretos.")
                return render(request, 'core/login.html')

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Login", "ERROR", f"Erro inesperado: {str(e)}")
            messages.error(request, "Erro inesperado ao processar o login.")
            return redirect('login')


class LogoutView(View):
    """
        Gerencia o logout do usuário.

        Finaliza a sessão ativa do usuário e o redireciona para a página de login.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Encerra a sessão do usuário autenticado.

            Args:
                request (HttpRequest): Objeto de requisição HTTP.

            Returns:
                HttpResponse: Redirecionamento para a página de login.
        """
        try:
            username = request.user.username if request.user.is_authenticated else 'Usuário desconhecido'
            if request.user.is_authenticated:
                logout(request)
                messages.error(request, f'{username} fez logout com sucesso!.')
            return redirect('login')

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Logout", "ERROR", f"Erro inesperado: {str(e)}")
            messages.error(request, "Erro inesperado ao encerrar a sessão.")
            return redirect('login')


class Erro404View(View):
    """
        Classe responsável por tratar erros 404 (página não encontrada).

        Métodos:
            get: Captura requisições para URLs não existentes, registra log e exibe a página de erro.
    """

    def get(self, request: HttpRequest, exception=None) -> HttpResponse:
        """
            Exibe a página de erro 404 quando uma URL não é encontrada.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.
                exception (Exception, opcional): Exceção capturada pelo Django.

            Returns:
                django.http.HttpResponse: Página HTML customizada de erro 404.
        """
        try:
            registrar_log(
                request.user if request.user.is_authenticated else None, "Erro Global", "WARNING",
                f"404 - URL Não encontrada: {request.path}"

            )
            messages.warning(request, "Página não encontrada.")
            return render(request, 'core/404.html', status=404)

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None,"ERRO404", "ERROR", f"Erro inesperado: {str(e)}")
            return render(request, 'core/404.html', status=404)


class Erro500View(View):
    """
        Classe responsável por tratar erros 500 (erro interno do servidor).

        Métodos:
            get: Captura exceções inesperadas, registra log detalhado e exibe a página de erro.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Exibe a página de erro 500 quando ocorre um erro interno no servidor.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.
                exception (Exception, opcional): Exceção capturada pelo Django.

            Returns:
                django.http.HttpResponse: Página HTML customizada de erro 500.
        """
        try:
            registrar_log(
                request.user if request.user.is_authenticated else None, "Erro Global", "WARNING",
                f"500 - Erro interno do servidor em {request.path}erro_detalhes"
            )
            messages.error(request, "Ocorreu um erro inesperado. Entre em contato com o suporte.")
            return render(request, 'core/500.html', status=500)

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "ERRO500", "ERROR", f"Erro inesperado: {str(e)}")
            return render(request, 'core/500.html', status=500)

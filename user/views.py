from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction, IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View

from core.utils import registrar_log
from user.utils import validar_criacao_usuario, validar_edicao_usuario, validar_senha


class PedidoResetSenhaView(View):
    """
        Inicia o processo de redefinição de senha enviando um link seguro para o e-mail do usuário.

        Métodos:
            get: Exibe o formulário de solicitação.
            post: Gera o token e envia o link de redefinição.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
           Exibe a página para inserção do e-mail de recuperação.

           Args:
               request (HttpRequest): Objeto de requisição HTTP.

           Returns:
               HttpResponse: Página HTML com o formulário.
        """
        try:
            return render(request, "user/pedido_reset_senha.html")

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Reset de senha", "ERROR",
                          f"Erro ao abrir pagina de reset de senha {str(e)}")
            messages.error(request, "Erro ao abrir pagina de reset de senha")
            return redirect('login')

    def post(self, request: HttpRequest) -> HttpResponse:
        """
            Processa o envio do link de redefinição de senha.
                - Verifica se o e-mail existe no banco de dados.
                - Cria um token e UID de segurança.
                - Envia um link de redefinição de senha para o e-mail informado.

           Args:
               request (HttpRequest): Objeto de requisição HTTP.

           Returns:
               HttpResponse: Redireciona para a tela de login após envio.
        """
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            user = None

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Reset de senha", "ERROR",
                          f"Erro ao enviar solitação: {str(e)}")
            messages.error(request, "Ocorreu um erro inesperado. Tente novamente mais tarde.")
            return redirect('login')

        if user:
            try:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = request.build_absolute_uri(
                    reverse("confirm_reset_senha", kwargs={"uidb64": uid, "token": token})
                )

                subject = "Redefinição de senha"
                message = (
                    f"Olá {user.username},"
                    f"\n\nClique no link abaixo para redefinir sua senha:\n\n{reset_link}"
                    f"\n\nSe você não solicitou isso, ignore este e-mail."
                )

                send_mail(subject, message, None, [email])
                messages.success(request, "Um link de redefinição de senha foi enviado para seu e-mail.")
                redirect('login')

            except Exception as e:
                registrar_log(request.user if request.user.is_authenticated else None, "Reset de senha", "ERROR", f"Erro ao enviar e-mail de reset:{str(e)}")
                messages.error(request, "Não foi possível enviar o e-mail. Tente novamente mais tarde.")
                return redirect('login')
        else:
            messages.warning(request, "Se o e-mail existir, enviaremos um link de redefinição.")
        return redirect("login")


class ConfirmacaoResetSenhaView(View):
    """
        Confirma e conclui o processo de redefinição de senha.

        Métodos:
            get_user: Obtém o usuário pelo UID decodificado.
            get: Exibe o formulário de redefinição.
            post: Valida e aplica a nova senha.
    """

    def get_user(self, uidb64):
        """
            Decodifica o UID e obtém o usuário correspondente.

            Args:
                uidb64 (str): Identificador codificado do usuário.

            Returns:
                User | None: Usuário correspondente ou None.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=uid)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

        except Exception as e:
            registrar_log(None, "Reset de senha", "ERROR", f"Erro ao decodificar UID: {str(e)}")
            messages.error("Erro ao decodificar UID")
            return None

    def get(self, request: HttpRequest, uidb64, token) -> HttpResponse:
        """
            Exibe o formulário de redefinição de senha se o token for válido.

            Args:
                request (HttpRequest): Objeto da requisição HTTP.
                uidb64 (str): UID codificado.
                token (str): Token de verificação.

            Returns:
                HttpResponse: Página HTML ou redirecionamento.
        """
        try:
            user = self.get_user(uidb64)

            if user is not None and default_token_generator.check_token(user, token):
                return render(request, "user/confirm_reset_senha.html", {"user": user})
            else:
                messages.error(request, "Link inválido ou expirado.")
                return redirect("login")

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Confirmar reset de senha", "ERROR",
                          f"Erro na confirmação de reset:{str(e)}")
            return redirect("login")


    def post(self, request: HttpRequest, uidb64, token) -> HttpResponse:
        """
            Aplica a redefinição de senha após validação.

            Args:
                request (HttpRequest): Objeto da requisição HTTP.
                uidb64 (str): UID codificado.
                token (str): Token de verificação.

            Returns:
                HttpResponse: Redireciona para login após redefinir.
        """
        user = self.get_user(uidb64)
        if user is None or not default_token_generator.check_token(user, token):
            messages.error(request, "Link inválido ou expirado.")
            return redirect("login")

        senha1 = request.POST.get("senha1")
        senha2 = request.POST.get("senha2")

        if senha1 != senha2:
            messages.error(request, "As senhas não coincidem.")
            return redirect(request.path)

        if len(senha1) < 6:
            messages.warning(request, "A senha deve ter pelo menos 6 caracteres.")
            return redirect(request.path)

        try:
            user.password = make_password(senha1)
            user.save()
            messages.success(request, "Senha redefinida com sucesso! Faça login novamente.")

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Reset de senha", "ERROR", f"Erro ao definir senha: {str(e)}")
            messages.error(request,"Erro ao redefinir a senha. Tente novamente mais tarde.")
        return redirect("login")



class ListarUsuariosView(LoginRequiredMixin, View):
    """
        Lista todos os usuários cadastrados no sistema.

        Métodos:
            get: Renderiza a página com a lista de usuários.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Exibe a página de listagem de usuários.

            Args:
                request (HttpRequest): Objeto da requisição HTTP.

            Returns:
                HttpResponse: Página HTML com a lista de usuários.
        """
        try:
            usuarios = User.objects.all()
            return render(request, "user/listar.html", {"usuarios": usuarios})
        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Listar Usuários", "ERROR",
                          f"Erro ao carregar a lista de usuários: {str(e)}")
            messages.error(request, "Erro ao carregar a lista de usuários.")
            return redirect('home')


class CriarUsuarioView(LoginRequiredMixin, View):
    """
        Cria novos usuários no sistema.

        Métodos:
            get: Exibe o formulário de criação.
            post: Valida e salva o novo usuário.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Renderiza o formulário de criação de usuário.
        """
        try:
            return render(request, "user/usuarios_form.html")

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Criar Usuario", "ERROR",
                          f"Erro ao exibir pagina de criação de usuario `{str(e)}")
            messages.error(request, "Erro ao exibir pagina.")
            return redirect('criar_usuario')

    def post(self, request: HttpRequest) -> HttpResponse:
        """
             Processa a criação de um novo usuário, incluindo:
             - Validação de e-mail e senha;
             - Verificação de duplicidade;
             - Criação transacional com registro de log.

             Args:
                 request (django.http.HttpRequest): Objeto da requisição HTTP.

             Returns:
                 django.http.HttpResponse: Redireciona para listagem após sucesso ou erro.
         """
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not validar_criacao_usuario(request, username, email,):
            return redirect('criar_usuario')

        if not validar_senha(request, password):
            return redirect('criar_usuario')

        try:
            with transaction.atomic():
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
            messages.success(request, "Usuário criado com sucesso!.")
            return redirect('listar_usuarios')

        except IntegrityError:
            messages.error(request, "Erro de integridaade no banco. Tente novamente.")
            return redirect('listar_usuarios')

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Criar Usuário", "ERROR",
                          f"Erro de inesperado: {str(e)}")
            messages.error(request, f"Ocorreu um erro inesperado: {str(e)}")
        return redirect('criar_usuario')


class EditarUsuarioView(LoginRequiredMixin, View):
    """
        View responsável por editar informações de um usuário existente.

        Métodos:
            get: Exibe o formulário de edição.
            post: Aplica as alterações e salva no banco.
    """

    def get(self, request: HttpRequest, usuario_id) -> HttpResponse:
        """
            Exibe o formulário para edição de um usuário específico.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.
                usuario_id (int): ID do usuário a ser editado.

            Returns:
                django.http.HttpResponse: Página HTML com os dados preenchidos.
        """
        try:
            usuario = get_object_or_404(User, id=usuario_id)
            return render(request, "user/usuarios_form.html", {"usuario": usuario})

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Editar Usuario", "ERROR",
                          f"Erro ao editar usuario: {str(e)}")
            messages.error(request, "Erro ao exibir págine, tente novamente!.")
            return redirect('editar_usuario')

    def post(self, request: HttpRequest, usuario_id) -> HttpResponse:
        """
            post:
                Atualiza os dados de um usuário existente.

            Args:
                request (HttpRequest): Requisição HTTP.
                usuario_id (int): ID do usuário a ser atualizado.

            Returns:
                HttpResponse: Redireciona após sucesso ou erro.
        """
        usuario = get_object_or_404(User, id=usuario_id)
        username = request.POST.get('username','').strip()
        email = request.POST.get('email','').strip()
        senha = request.POST.get('senha','').strip()

        if not validar_edicao_usuario(request, usuario, username, email):
            return render(request, "user/usuarios_form.html", {"usuario": usuario})

        if not validar_senha(request, senha):
            return render(request, "user/usuarios_form.html", {"usuario": usuario})

        try:
            usuario.username = username
            usuario.email = email

            if senha:
                usuario.set_password(senha)
                messages.error(request, f"Senha do usuário '{usuario.username}' alterada.")

            usuario.save()
            messages.success(request, "Usuário atualizado com sucesso!")
            return redirect('listar_usuarios')

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Editar Usuário", "ERROR",
                          f"Erro ao atualizar usuário: {str(e)}")
            messages.error(request, "Erro ao atualizar usuário. Tente novamente.")
        return redirect('listar_usuarios')


class DeleteUsuarioView(LoginRequiredMixin, View):
    """
         View responsável por excluir usuários do sistema.

         Métodos:
             get: Exibe a página de confirmação de exclusão.
             post: Remove o usuário do banco de dados.
     """

    def get(self, request: HttpRequest, usuario_id) -> HttpResponse:
        """
            Exibe a página de confirmação para exclusão de um usuário.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.
                usuario_id (int): ID do usuário a ser deletado.

            Returns:
                django.http.HttpResponse: Página HTML de confirmação.
        """
        try:
            usuario = get_object_or_404(User, id=usuario_id)
            return render(request, 'user/confirmacao_delete.html', {"usuario": usuario})

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Deletar Usuario", "ERROR",
                          f"Erro ao exibir pagina de exclusão.")
            messages.error(request, "Erro inesperado")
            return redirect('listar_usuarios')

    def post(self, request: HttpRequest, usuario_id) -> HttpResponse:
        """
            Exclui definitivamente um usuário do banco de dados,
            com validações para impedir exclusão do admin principal.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.
                usuario_id (int): ID do usuário a ser excluído.

            Returns:
                django.http.HttpResponse: Redireciona para listagem após exclusão.
        """
        usuario = get_object_or_404(User, id=usuario_id)

        if usuario.username.lower() == 'admin':
            messages.error(request, "O usuário 'admin' não pode ser excluído.")
            return redirect('listar_usuarios')

        if not request.user.is_superuser:
            messages.error(request, "Apenas superusuários podem excluir usuários.")
            return redirect('listar_usuarios')
        try:
            usuario.delete()
            messages.success(request, f"Usuário '{usuario.username}' deletado com sucesso.")
            return redirect('listar_usuarios')

        except Exception as e:
            registrar_log(request.user if request.user.is_authenticated else None, "Excluir Usuário", "ERROR",
                          f"Erro ao deletar usuário: {str(e)}")
            messages.error(request, "Erro ao excluir o usuário. Tente novamente mais tarde.")
        return redirect('listar_usuarios')

from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import transaction, IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View

from core.utils import registrar_log


# Envia um email link de redefinição de senha para o usuario
class PedidoResetSenhaView(View):
    """
        View responsável por iniciar o processo de redefinição de senha.
        Envia um link de redefinição para o e-mail do usuário.

        Métodos:
            get: Exibe o formulário para informar o e-mail.
            post: Gera o link de redefinição e envia o e-mail.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Exibe a página para o usuário inserir seu e-mail de recuperação.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.

            Returns:
                django.http.HttpResponse: Página HTML com o formulário.
        """
        return render(request, "user/pedido_reset_senha.html")


    def post(self, request: HttpRequest) -> HttpResponse:
        """
             Processa o envio do formulário de recuperação de senha.

             - Verifica se o e-mail existe no banco de dados.
             - Cria um token e UID de segurança.
             - Envia um link de redefinição de senha para o e-mail informado.

             Args:
                 request (django.http.HttpRequest): Objeto da requisição HTTP.

             Returns:
                 django.http.HttpResponse: Redireciona para a tela de login após envio.
         """

        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        except Exception as e:
            registrar_log(request.user, "Reset de senha", "ERROR", f"Erro ao buscar usuário por e-mail: {str(e)}")
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
                registrar_log(request.user, "Reset de senha", "SUCCESS", "Link de redefinição enviado com sucesso.")
                messages.success(request, "Um link de redefinição de senha foi enviado para seu e-mail.")
            except Exception as e:
                registrar_log(request.user, "Reset de senha", "ERROR", f"Erro ao enviar e-mail de reset:{str(e)}")
                messages.error(request, "Não foi possível enviar o e-mail. Tente novamente mais tarde.")
        else:
            messages.warning(request, "Se o e-mail existir, enviaremos um link de redefinição.")
        return redirect("login")


class ConfirmacaoResetSenhaView(View):
    """
         View responsável por confirmar e concluir o processo de redefinição de senha.

         Métodos:
             get_user: Decodifica e retorna o usuário a partir do UID.
             get: Exibe o formulário para redefinição de senha.
             post: Valida e aplica a nova senha do usuário.
     """
    def get_user(self, uidb64):
        """
            Decodifica o UID e obtém o usuário correspondente.

            Args:
                uidb64 (str): Identificador codificado em base64 do usuário.

            Returns:
                User | None: Usuário encontrado ou None em caso de erro.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=uid)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

        except Exception as e:
            registrar_log(None, "Reset de senha", "ERROR", f"Erro ao decodificar UID: {str(e)}")
            return None


    def get(self, request: HttpRequest, uidb64, token) -> HttpResponse:
        """
            Exibe o formulário de redefinição de senha caso o token seja válido.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.
                uidb64 (str): UID codificado do usuário.
                token (str): Token temporário de verificação.

            Returns:
                django.http.HttpResponse: Página HTML ou redirecionamento.
        """

        user = self.get_user(uidb64)

        if user is not None and default_token_generator.check_token(user, token):
            return render(request, "user/confirm_reset_senha.html", {"user": user})
        else:
            messages.error(request, "Link inválido ou expirado.")
            return redirect("login")


    def post(self, request: HttpRequest, uidb64, token) -> HttpResponse:
        """
             Processa a redefinição de senha após validações.

             Args:
                 request (django.http.HttpRequest): Objeto da requisição HTTP.
                 uidb64 (str): UID codificado do usuário.
                 token (str): Token temporário de verificação.

             Returns:
                 django.http.HttpResponse: Redireciona para login após sucesso ou erro.
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
            registrar_log(request.user, "Reset de senha", "ERROR", f"Erro ao definir senha: {str(e)}")
            messages.error(request.user, "Reset de senha", "ERROR", "Erro ao redefinir a senha. Tente novamente mais tarde.")
        return redirect("login")



class ListarUsuariosView(LoginRequiredMixin, View):
    """
        View responsável por listar todos os usuários cadastrados no sistema.

        Métodos:
            get: Exibe a página com a listagem dos usuários.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Exibe a página de listagem de usuários.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.

            Returns:
                django.http.HttpResponse: Página HTML contendo a lista de usuários.
        """
        usuarios = User.objects.all()
        return render(request, "user/listar.html", {"usuarios": usuarios})


class CriarUsuarioView(LoginRequiredMixin, View):
    """
        View responsável pela criação de novos usuários.

        Métodos:
            get: Exibe o formulário de criação.
            post: Processa e salva o novo usuário no banco.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
            Exibe o formulário de criação de usuário.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.

            Returns:
                django.http.HttpResponse: Página HTML com o formulário.
        """
        return render(request, "user/usuarios_form.html")

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


        if not username or not email or not password:
            messages.error(request, "Todos campos são obrigatorios")
            return redirect('criar_usuario')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Já existe um usuário com este nome de usuário.")
            return redirect('criar_usuario')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está em uso.")
            return redirect('criar_usuario')

        try:
            validate_email(email)
        except ValidationError as e:
            messages.error(request, "Endereço de e-mail invalido")
            return redirect("criar_usuario")

        if len(password) < 6:
            messages.warning(request, "A senha deve ter pelo menos 6 caracteres.")
            return redirect(request.path)
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                registrar_log(request.user, "Criar Usuário", "SUCCESS", f"Usuário '{user.username}' criado com sucesso!.")
            messages.success(request, "Usuário criado com sucesso!.")
            return redirect('listar_usuarios')

        except IntegrityError:
            messages.error(request, "Erro de integridaade no banco. Tente novamente.")
        except Exception as e:
            registrar_log(request.user, "Criar Usuário", "SUCCESS", "Erro de integridade no banco de dados.")
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
        usuario = get_object_or_404(User, id=usuario_id)
        return render(request, "user/usuarios_form.html", {"usuario": usuario})

    def post(self, request: HttpRequest, usuario_id) -> HttpResponse:
        """
            Atualiza os dados de um usuário existente, verificando duplicidade
            de e-mail e nome de usuário antes da gravação.

            Args:
                request (django.http.HttpRequest): Objeto da requisição HTTP.
                usuario_id (int): ID do usuário a ser atualizado.

            Returns:
                django.http.HttpResponse: Redireciona após salvar ou exibir erro.
        """

        usuario = get_object_or_404(User, id=usuario_id)
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        if User.objects.filter(username=username).exclude(id=usuario_id).exists():
            messages.error(request, "Já existe outro usuário com este nome.")
            return redirect('editar_usuario', usuario_id=usuario_id)

        if User.objects.filter(email=email).exclude(id=usuario_id).exists():
            messages.error(request, "Este e-mail já está em uso por outro usuário.")
            return redirect('editar_usuario', usuario_id=usuario_id)

        usuario.username = username
        usuario.email = email

        if senha:
            usuario.set_password(senha)
        try:
            usuario.save()
            registrar_log(request.user, "Editar Usuário", "SUCCESS", f"Usuário '{usuario.username}' atualizado.")
            messages.success(request, "Usuário atualizado com sucesso!")
        except Exception as e:
            registrar_log(request.user, "Editar Usuário", "ERROR", f"Erro ao atualizar usuário: {str(e)}")
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
        usuario = get_object_or_404(User, id=usuario_id)
        return render(request, 'user/confirmacao_delete.html', {"usuario": usuario})

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
            registrar_log(request.user, "Excluir Usuário", "SUCCESS", f"Usuário '{usuario.username}' deletado.")
            messages.success(request, f"Usuário '{usuario.username}' deletado com sucesso.")
            return redirect('listar_usuarios')

        except Exception as e:
            registrar_log(request.user, "Excluir Usuário", "ERROR", f"Erro ao deletar usuário: {str(e)}")
            messages.error(request, "Erro ao excluir o usuário. Tente novamente mais tarde.")
        return redirect('listar_usuarios')

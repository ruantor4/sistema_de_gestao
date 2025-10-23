from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages import success
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

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "user/pedido_reset_senha.html")

    def post(self, request: HttpRequest) -> HttpResponse:
        email = request.POST.get('email')
        # Verifica o email e existente no cadastro
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        except Exception as e:
            registrar_log(None, messages.ERROR, None, f"Erro ao buscar usuário por e-mail: {str(e)}")
            messages.error(request, "Ocorreu um erro inesperado. Tente novamente mais tarde.")
            return redirect('login')

        # Se existir cria um identificador único e token de verificação temporario e gera o link
        if user:
            try:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = request.build_absolute_uri(
                    reverse("confirm_reset_senha", kwargs={"uidb64": uid, "token": token})
                )

                # Dados do email
                subject = "Redefinição de senha"
                message = (
                f"Olá {user.username},"
                f"\n\nClique no link abaixo para redefinir sua senha:\n\n{reset_link}"
                f"\n\nSe você não solicitou isso, ignore este e-mail."
                )

                send_mail(subject, message, None, [email])
                messages.success(request, "Um link de redefinição de senha foi enviado para seu e-mail.")
            except Exception as e:
                registrar_log(request.user, messages.ERROR, None, f"Erro ao enviar e-mail de reset:{str(e)}")
                messages.error(request, "Não foi possível enviar o e-mail. Tente novamente mais tarde.")
        else:
            messages.warning(request, "Se o e-mail existir, enviaremos um link de redefinição.")
        return redirect("login")


# Página de confirmação da redefinição de senha.
class ConfirmacaoResetSenhaView(View):

    def get_user(self, uidb64):
        # Decodifica o ID do usuario
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None
        except Exception as e:
            registrar_log(None, messages.ERROR, None, f"Erro ao decodificar usuário:{str(e)}")
            return None


    def get(self, request: HttpRequest, uidb64, token) -> HttpResponse:
        user = self.get_user(uidb64)
        # Verifica se é valido
        if user is not None and default_token_generator.check_token(user, token):
            return render(request, "user/confirm_reset_senha.html", {"user": user})
        else:
            messages.error(request, "Link inválido ou expirado.")
            return redirect("login")

    def post(self, request: HttpRequest, uidb64, token) -> HttpResponse:
        user = self.get_user(uidb64)
        if user is None or not default_token_generator.check_token(user, token):
            messages.error(request, "Link inválido ou expirado.")
            return redirect("login")

        senha1 = request.POST.get("senha1")
        senha2 = request.POST.get("senha2")

        # Validações de senha
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
            registrar_log(request.user, messages.ERROR, None, f"Erro ao definir senha: {str(e)}")
            messages.error(request.user, messages.ERROR, None, "Erro ao redefinir a senha. Tente novamente mais tarde.")
        return redirect("login")


#  Exibe a lista de usuários cadastrados no sistema.
class ListarUsuariosView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest) -> HttpResponse:
        usuarios = User.objects.all()
        return render(request, "user/listar.html", {"usuarios": usuarios})


#  Cria um novo usuário do sistema.

class CriarUsuarioView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "user/usuarios_form.html")

    def post(self, request: HttpRequest) -> HttpResponse:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            validate_email(email)
        except ValidationError as e:
            messages.error(request,"Endereço de e-mail invalido")
            return redirect("criar_usuario")

        if not username or not email or not password:
            messages.error(request, "Todos campos são obrigatorios")
            return redirect('criar_usuario')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Já existe um usuário com este nome de usuário.")
            return redirect('criar_usuario')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está em uso.")
            return redirect('criar_usuario')

        if len(password) < 6:
            messages.warning(request, "A senha deve ter pelo menos 6 caracteres.")
            return redirect(request.path)
        # Cria usuário de forma segura (com hash automático)
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                registrar_log(request.user, success, user, f"Usuário '{user.username}' criado com sucesso!.")
            messages.success(request, "Usuário criado com sucesso!.")
            return redirect('listar_usuarios')

        except IntegrityError:
            messages.error(request, "Erro de integridaade no banco. Tente novamente.")
        except Exception as e:
            messages.error(request, f"Ocorreu um erro inesperado: {str(e)}")
        return redirect('criar_usuario')


#  Edita informações de um usuário existente.
#     Permite alterar username, e-mail e senha.
class EditarUsuarioView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, usuario_id) -> HttpResponse:
        usuario = get_object_or_404(User, id=usuario_id)
        return render(request, "user/usuarios_form.html", {"usuario": usuario})

    def post(self, request: HttpRequest, usuario_id) -> HttpResponse:
        usuario = get_object_or_404(User, id=usuario_id)
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        # Verifica se já existe outro usuário com o mesmo nome de usuário
        if User.objects.filter(username=username).exclude(id=usuario_id).exists():
            messages.error(request, "Já existe outro usuário com este nome.")
            return redirect('editar_usuario', usuario_id=usuario_id)

        # Verifica se o email já está em uso por outro usuário
        if User.objects.filter(email=email).exclude(id=usuario_id).exists():
            messages.error(request, "Este e-mail já está em uso por outro usuário.")
            return redirect('editar_usuario', usuario_id=usuario_id)

        usuario.username = username
        usuario.email = email

        # Só altera a senha se o campo for preenchido
        if senha:
            usuario.set_password(senha)
        try:
            usuario.save()
            messages.success(request, "Usuário atualizado com sucesso!")
        except Exception as e:
            registrar_log(request.user, messages.ERROR, f"Erro ao atualizar usuário: {str(e)}")
            messages.error(request, "Erro ao atualizar usuário. Tente novamente.")
        return redirect('listar_usuarios')


# Remove usuarios do banco
class DeleteUsuarioView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, usuario_id) -> HttpResponse:
        usuario = get_object_or_404(User, id=usuario_id)
        return render(request, 'user/confirmacao_delete.html', {"usuario": usuario})

    def post(self, request: HttpRequest, usuario_id) -> HttpResponse:
        usuario = get_object_or_404(User, id=usuario_id)

        # Impede a exclusão do usuário admin principal
        if usuario.username.lower() == 'admin':
            messages.error(request, "O usuário 'admin' não pode ser excluído.")
            return redirect('listar_usuarios')

        # Verificação simples para evitar exclusão do admin
        if not request.user.is_superuser:
            messages.error(request, "Apenas superusuários podem excluir usuários.")
            return redirect('listar_usuarios')
        try:
            usuario.delete()
            messages.success(request, messages.SUCCESS, usuario, f"Usuário '{usuario.username}' deletado com sucesso!")
            return redirect('listar_usuarios')
        except Exception as e:
            registrar_log(request.user, messages.ERROR, 'Logout', None, f"Erro ao deletar usuário: {str(e)}")
            messages.error(request, "Erro ao excluir o usuário. Tente novamente mais tarde.")
        return redirect('listar_usuarios')
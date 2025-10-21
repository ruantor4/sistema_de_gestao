from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


# Envia um email link de redefinição de senha para o usuario
def pedido_reset_senha(request):
    if request.method == "POST":
        email = request.POST.get("email")
        # Verifica o email e existente no cadastro
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        # Se existir cria um identificador único e token de verificação temporario e gera o link
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                reverse("confirmacao_reset_senha", kwargs={"uidb64": uid, "token": token})
            )
            # Dados do email
            subject = "Redefinição de senha"
            message = (f"Olá {user.username},"
                       f"\n\nClique no link abaixo para redefinir sua senha:\n\n{reset_link}"
                       f"\n\nSe você não solicitou isso, ignore este e-mail.")
            from_email = None
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, "Um link de redefinição de senha foi enviado para seu e-mail.")
        else:
            messages.warning(request, "Se o e-mail existir, enviaremos um link de redefinição.")

        return redirect("login")

    return render(request, "user/pedido_reset_senha.html")

#Página de confirmação da redefinição de senha.
def confirmacao_reset_senha(request, uidb64, token):
    # Decodifica o ID do usuario
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # Verifica se é valido
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            senha1 = request.POST.get("senha1")
            senha2 = request.POST.get("senha2")

            # Validações de senha
            if senha1 != senha2:
                messages.error(request, "As senhas não coincidem.")
            elif len(senha1) < 6:
                messages.warning(request, "A senha deve ter pelo menos 6 caracteres.")
            else:
                user.password = make_password(senha1)
                user.save()
                messages.success(request, "Senha redefinida com sucesso! Faça login novamente.")
                return redirect("login")

        return render(request, "user/confirmacao_reset_senha.html", {"user": user})
    else:
        messages.error(request, "Link inválido ou expirado.")
        return redirect("login")





#  Exibe a lista de usuários cadastrados no sistema.
@login_required(login_url='login/')
def listar_usuarios(request):
    usuarios = User.objects.all()
    return render(request, "user/listar.html", {"usuarios": usuarios})

#  Cria um novo usuário do sistema.
@login_required(login_url='login/')
def criar_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Cria usuário de forma segura (com hash automático)
        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        usuario.save()
        messages.success(request, "Usuario criado com sucesso!.")
        return redirect('listar_usuarios')
    return render(request, "user/usuarios_form.html")

#  Edita informações de um usuário existente.
#     Permite alterar username, e-mail e senha.
@login_required(login_url='login/')
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        usuario.username = username
        usuario.email = email

        # Só altera a senha se o campo for preenchido
        if senha:
            usuario.set_password(senha)

        usuario.save()
        messages.success(request, "Usuario atualizado com sucesso!")
        return redirect('listar_usuarios')
    return render(request, "user/usuarios_form.html", {"usuario": usuario})

# Remove usuarios do banco
@login_required(login_url='login/')
def deletar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)

    # Impede a exclusão do usuário admin principal
    if usuario.username == 'admin':
        messages.error(request, "O usuário 'admin' não pode ser excluído.")
        return redirect('listar_usuarios')

    # Verificação simples para evitar exclusão do admin
    if request.user.is_superuser:
        usuario.delete()
        messages.success(request, f"Usuário '{usuario.username }' deletado com sucesso!")
    else:
        messages.error(request, "Apenas superusuários podem excluir usuários.")
    return redirect('listar_usuarios')

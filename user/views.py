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


# Create your views here.
def login_user(request):
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('home')

def pedido_reset_senha(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                reverse("confirmacao_reset_senha", kwargs={"uidb64": uid, "token": token})
            )

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

    return render(request, "usuarios/pedido_reset_senha.html")


def confirmacao_reset_senha(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            senha1 = request.POST.get("senha1")
            senha2 = request.POST.get("senha2")

            if senha1 != senha2:
                messages.error(request, "As senhas não coincidem.")
            elif len(senha1) < 6:
                messages.warning(request, "A senha deve ter pelo menos 6 caracteres.")
            else:
                user.password = make_password(senha1)
                user.save()
                messages.success(request, "Senha redefinida com sucesso! Faça login novamente.")
                return redirect("login")

        return render(request, "usuarios/confirmacao_reset_senha.html", {"user": user})
    else:
        messages.error(request, "Link inválido ou expirado.")
        return redirect("login")



def submit_login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        usuario = authenticate(username=username, password=password)
        if usuario is None:
            messages.error(request, " Usuário ou senha incorretos.")
        else:
            login(request, usuario)
            return redirect('home')
    return redirect('home')

@login_required(login_url='login/')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='login/')
def listar_usuarios(request):
    usuarios = User.objects.all()
    return render(request, "usuarios/listar.html", {"usuarios": usuarios})


@login_required(login_url='login/')
def criar_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        usuario = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password)
        usuario.save()
        messages.success(request, "Usuario criado com sucesso!.")
        return redirect('listar_usuarios')
    return render(request, "usuarios/usuarios_form.html")


@login_required(login_url='login/')
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        usuario.username = username
        usuario.email = email

        if senha:
            usuario.set_password(senha)

        usuario.save()
        messages.success(request, "Usuario atualizado com sucesso!")
        return redirect('listar_usuarios')
    return render(request, "usuarios/usuarios_form.html", {"usuario": usuario})


@login_required(login_url='login/')
def deletar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    if usuario.is_superuser:
        messages.error(request, "Não é permitido excluir o admin")
    else:
        usuario.delete()
        messages.success(request, "Usuario deletado com sucesso!")
    return redirect('listar_usuarios')
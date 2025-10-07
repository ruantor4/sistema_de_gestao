from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404


# Create your views here.
def login_user(request):
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('home')

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
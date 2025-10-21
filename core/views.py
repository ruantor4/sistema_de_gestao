from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


# Página inicial do sistema.
@login_required(login_url='/login/')
def home(request):
    return render(request, 'core/home.html')

# Exibe a pagina de login
def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'core/login.html')

# Efetua o logout do sistema e redireciona a pagina incial
def logout_user(request):
    logout(request)
    return redirect('login')

# Realiza a autenticação do usuário, verifica as credenciais, autentica e redireciona
def submit_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        usuario = authenticate(username=username, password=password)
        
        if usuario is not None:
            login(request, usuario)
            return redirect('home')
        else:
            messages.error(request, " Usuário ou senha incorretos.")
            return redirect('login')
            
    return redirect('login')
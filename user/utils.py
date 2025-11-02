from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def validar_criacao_usuario(request, username: str, email: str) -> bool:
    """
        Valida os campos obrigatórios e regras de criação de um usuário.

        Args:
            request (HttpRequest): Requisição HTTP (para exibir mensagens).
            username (str): Nome de usuário.
            email (str): Endereço de e-mail.
            password (str): Senha informada.

        Returns:
            bool: True se a validação for bem-sucedida, False caso contrário.
    """
    if not username and not email:
        messages.error(request, "Todos os campos são obrigatórios.")
        return False

    if User.objects.filter(username=username).exists():
        messages.error(request, "Já existe um usuário com este nome.")
        return False

    if User.objects.filter(email=email).exists():
        messages.error(request, "Este e-mail já está em uso.")
        return False

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, "Endereço de e-mail inválido.")
        return False

    return True

def validar_edicao_usuario(request, usuario: User, username: str, email: str) -> bool:
    """
        Valida os campos obrigatórios e regras de edição de um usuário.

        Args:
            request (HttpRequest): Requisição HTTP (para mensagens).
            usuario (User): Usuário que está sendo editado.
            username (str): Novo nome de usuário.
            email (str): Novo e-mail.

        Returns:
            bool: True se a validação for bem-sucedida, False caso contrário.
    """
    if not username or not email:
        messages.error(request, "Os campos 'Usuário' e 'E-mail' são obrigatórios.")
        return False

    # Verifica duplicidade de username (ignorando o próprio)
    if User.objects.filter(username=username).exclude(id=usuario.id).exists():
        messages.error(request, "Já existe outro usuário com este nome.")
        return False

    # Verifica duplicidade de e-mail (ignorando o próprio)
    if User.objects.filter(email=email).exclude(id=usuario.id).exists():
        messages.error(request, "Já existe outro usuário com este e-mail.")
        return False

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, "Endereço de e-mail inválido.")
        return False

    return True


def validar_senha(request, senha: str) -> bool:
    """
    Valida a senha informada pelo usuário.

    - Deve ter pelo menos 6 caracteres.
    - Pode ser expandido depois (ex: exigir número, letra maiúscula, etc).

    Retorna:
        True -> se a senha for válida.
        False -> se for inválida (mensagem será exibida automaticamente).
    """
    if not senha:
        return True  # Se o campo estiver vazio, não obriga trocar a senha

    if len(senha) < 6:
        messages.warning(request, " A senha deve ter pelo menos 6 caracteres.")
        return False

    return True

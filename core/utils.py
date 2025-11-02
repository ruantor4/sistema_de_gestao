from .models import LogSystem
from django.contrib.auth.models import User, AnonymousUser
import traceback


def registrar_log(user: User, action: str, status: str, message: str):
    """: 'Criar Usuário').
        :param status: Status da ação ('SUCESSO', 'ERRO', 'AVISO').
        :param message: Detalhes ou observações da ação.
    """
    if isinstance(user, AnonymousUser):
        user = None

        LogSystem.objects.create(
            user=user,
            action=action,
            status=status,
            message=message
        )


def registrar_error(user: User, action: str, error: Exception):
    """
        Registra um log genérico no banco de dados.

        :param user: Usuário responsável pela ação.
        :param action: Descrição da ação (ex
        Registra um log de erro automaticamente com rastreamento completo.

        :param user: Usuário que executava a ação.
        :param action: Ação onde ocorreu o erro.
        :param error: Exceção capturada no bloco try/except.
    """

    full_trace = traceback.format_exc()
    LogSystem.objects.create(
        user=user,
        action=action,
        status="ERROR",
        message=f"{str(error)}\n\n{full_trace}"
    )

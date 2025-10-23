from django.db import models
from django.contrib.auth.models import User


class LogSystem(models.Model):
    """
        Modelo responsável por registrar logs de ações e erros do sistema.

        Attributes
        ----------
        user : ForeignKey(User)
            Usuário responsável pela ação registrada.
        action : CharField
            Descrição curta da ação executada (ex: 'Criar Usuário', 'Login', 'Atualizar Produto').
        timestamp : DateTimeField
            Data e hora em que a ação foi registrada automaticamente.
        status : CharField
            Situação do log (ex: 'SUCESSO', 'ERRO', 'AVISO').
        message : TextField
            Detalhes adicionais ou mensagem de erro completa.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    message = models.TextField(null=True)

    def __str__(self):
        return f"{self.timestamp} - {self.user.username} - {self.action} - {self.status}"

    class Meta:
        db_table = 'log_system'
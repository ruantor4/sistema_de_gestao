from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Produto(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)
    descricao = models.TextField(blank=True, null=True)
    quantidade = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to='estoque/images/', null=True, blank=True)
    localizacao = models.CharField(max_length=100, null=True, blank=True)
    datasheet = models.FileField(upload_to='estoque/anexos/', null=True, blank=True)

    def __str__(self):
        return self.nome


    class Meta:
        db_table = 'produtos'


class Movimentacao(models.Model):
    TIPO_ENTRADA = [
            ("entrada", "Entrada"),
            ("saida", "Saida")
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=0)
    tipo = models.CharField(max_length=10,verbose_name="tipo", choices=TIPO_ENTRADA)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.componente.nome} ({self.quantidade})"

    class Meta:
        db_table = 'movimentacoes'
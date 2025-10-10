from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Produto(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False) # Nome obrigatorio, max 100 caracter, nao permite campo vazio
    descricao = models.TextField(blank=True, null=True) # Pode ficar vazio no formulário, # Pode armazenar NULL no banco
    quantidade = models.PositiveIntegerField(default=0) # Valor padrão caso não seja informado
    imagem = models.ImageField(upload_to='estoque/images/', null=True, blank=True) #Pasta onde será salva a imagem # Pode ser nulo no banco # Pode ser deixado vazio no formulário
    localizacao = models.CharField(max_length=100, null=True, blank=True) # Limite de 100 caracteres
    datasheet = models.FileField(upload_to='estoque/anexos/', null=True, blank=True)# Arquivo adicional do produto, como datasheet ou manual (opcional), Pasta para salvar o arquivo

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'produtos' # Nome da tabela no banco de dados


class Movimentacao(models.Model):
    TIPO_ENTRADA = [
        ("entrada", "Entrada"), # Valor banco / Valor exibido
        ("saida", "Saida")
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE) # Usuário que realizou a movimentação, modelo de usuario Django
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE) # Se o produto for deletado, remove as movimentações
    quantidade = models.IntegerField(default=0) # Valor padrão caso não seja informado
    tipo = models.CharField(max_length=10, verbose_name="tipo", choices=TIPO_ENTRADA) # Escolha das opções entrada
    data = models.DateTimeField(auto_now_add=True) # Data definida automaticamente ao criar


    def __str__(self):
        return f"{self.tipo} - {self.componente.nome} ({self.quantidade})"

    class Meta:
        db_table = 'movimentacoes' # Nome da tabela no banco de dados

from django.contrib import admin

from estoque.models import Movimentacao, Produto

# Register your models here.
admin.site.register(Produto)
admin.site.register(Movimentacao)

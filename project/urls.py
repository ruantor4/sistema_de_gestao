"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from itertools import product

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core.views import Erro404View, Erro500View

urlpatterns = [

    # Rota do Django Admin
    path('admin/', admin.site.urls),

    # Rota do modulo Core
    path('', include('core.urls')),

    # Rota do modulo Usuários
    path('user/', include('user.urls')),

    # Rota do modulo Usuários
    path('estoque/', include('estoque.urls')),
]

# Handlers globais
handler404 = Erro404View.as_view()
handler500 = Erro500View.as_view()

# Diz ao Django onde encontrar e servir arquivos de midea
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
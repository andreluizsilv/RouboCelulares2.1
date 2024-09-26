# urls.py do aplicativo (roubos_celulares/urls.py)

from django.urls import path
from .views import mapa_roubos, carregar_bairros, remover_bairro

urlpatterns = [
    path('', mapa_roubos, name='mapa_roubos'),
    path('carregar_bairros/', carregar_bairros, name='carregar_bairros'),
    path('remover_bairro/<int:id>/', remover_bairro, name='remover_bairro'),
]

from django.urls import path
from . import views


urlpatterns = [
    # Rota para a página inicial ou mapa de roubos
    path('', views.mapa_roubos, name='mapa_roubos'),

    ]
from django.urls import path
from . import views

urlpatterns = [
    # Rota para a página inicial ou mapa de roubos
    path('', views.mapa_roubos, name='mapa_roubos'),
    path('bairros-fora-sao-paulo/', views.bairros_fora_sao_paulo, name='bairros_fora_sao_paulo'),

    # Rota para a página de detalhes de uma ocorrência específica
    path('detalhes/<int:id>/', views.detalhes_ocorrencia, name='detalhes_ocorrencia'),
    path('pesquisa/', views.pesquisar_bairro, name='pesquisar_bairro'),
    path('ocorrencias/', views.listar_ocorrencias, name='listar_ocorrencias'),

    # Rotas para feedback
    path('feedback/', views.feedback, name='feedback'),
    path('feedback-success/', views.feedback_success, name='feedback_success'),

    # Rota para listar bairros (disponível apenas para usuários autenticados)
    path('bairros/', views.listar_bairros, name='listar_bairros'),

    # Rota para editar bairros (disponível apenas para usuários autenticados)
    path('bairros/editar/', views.editar_bairro, name='editar_bairro'),

    # Rota para deletar bairro (disponível apenas para usuários autenticados)
    path('bairros/deletar/', views.deletar_bairro, name='deletar_bairro'),
]

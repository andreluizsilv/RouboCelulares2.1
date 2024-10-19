from django.urls import path
from . import views

urlpatterns = [
    # Rota para a página inicial ou mapa de roubos
    path('', views.mapa_roubos, name='mapa_roubos'),
    path('bairros-fora-sao-paulo/', views.bairros_fora_sao_paulo, name='bairros_fora_sao_paulo'),

    # Rota para a página de detalhes de uma ocorrência específica
    path('detalhes/<int:id>/', views.detalhes_ocorrencia, name='detalhes_ocorrencia'),
    path('pesquisa/', views.pesquisar_bairro, name='pesquisar_bairro'),

    # Rotas para feedback
    path('feedback/', views.feedback, name='feedback'),
    path('feedback-success/', views.feedback_success, name='feedback_success'),

    # Rota para listar bairros (disponível apenas para usuários autenticados)
    path('gerenciar_bairros/', views.gerenciar_bairros, name='gerenciar_bairros'),
    path('bairros/<int:bairro_id>/', views.detalhes_bairro, name='detalhes_bairro'),

    # Rotas para editar e deletar bairros
    path('bairros/<int:bairro_id>/editar/', views.editar_bairro, name='editar_bairro'),  # Nova rota para editar bairro
    path('bairros/<int:bairro_id>/deletar/', views.deletar_bairro, name='deletar_bairro'),

    path('roubos/<int:roubo_id>/editar/', views.editar_roubo, name='editar_roubo'),
    path('roubos/<int:roubo_id>/deletar/', views.deletar_roubo, name='deletar_roubo'),
]

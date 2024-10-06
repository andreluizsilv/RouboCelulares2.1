from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from .models import Bairro, Roubo
from .mapa import gerar_mapa  # Importa a função de mapa.py

def mapa_roubos(request):
    # Filtra todos os roubos e calcula os 5 bairros mais atacados
    bairros_mais_atacados = (
        Roubo.objects.values('bairro__nome')
        .annotate(num_ocorrencias=Count('id'))
        .order_by('-num_ocorrencias')[:5]
    )

    # Coleta as informações dos bairros
    bairros_info = []
    for bairro_data in bairros_mais_atacados:
        bairro_obj = Bairro.objects.filter(nome__iexact=bairro_data['bairro__nome']).first()
        if bairro_obj and bairro_obj.latitude is not None and bairro_obj.longitude is not None:
            bairros_info.append({
                'id': bairro_obj.id,  # Adiciona o ID do bairro
                'nome': bairro_obj.nome,
                'num_ocorrencias': bairro_data['num_ocorrencias'],
                'latitude': bairro_obj.latitude,
                'longitude': bairro_obj.longitude
            })

    # Gera o mapa usando a função gerar_mapa
    mapa_html = gerar_mapa(bairros_info)

    context = {
        'bairros_info': bairros_info,
        'mapa_html': mapa_html,
    }

    return render(request, 'filtrar_roubos.html', context)


def detalhes_ocorrencia(request, id):
    # Obtém o bairro pelo ID
    bairro = get_object_or_404(Bairro, id=id)

    # Usa a função `contar_ocorrencias_por_bairro` apenas se quiser contagem geral (opcional)
    # ocor_por_bairro = Roubo.contar_ocorrencias_por_bairro().filter(bairro=bairro)

    # Filtra as ocorrências relacionadas ao bairro, usando diretamente o objeto `bairro`
    ocorrencias = (
        Roubo.objects.filter(bairro=bairro)
        .exclude(hora_ocorrencia='00:00:00')
        .exclude(rua__icontains='VEDAÇÃO DA DIVULGAÇÃO DOS DADOS RELATIVOS')
        .values('rua', 'hora_ocorrencia')
        .annotate(num_ocorrencias=Count('id'))
        .order_by('-num_ocorrencias')
    )

    # Agrupa as ocorrências por logradouro e horários, contando as ocorrências por hora
    ocorrencias_agrupadas = {}
    for ocorrencia in ocorrencias:
        rua = ocorrencia['rua']
        hora = ocorrencia['hora_ocorrencia'].strftime('%H:%M') if ocorrencia['hora_ocorrencia'] else 'Desconhecida'
        num_ocorrencias = ocorrencia['num_ocorrencias']

        if rua not in ocorrencias_agrupadas:
            ocorrencias_agrupadas[rua] = {'horas': {}, 'total': 0}

        if hora not in ocorrencias_agrupadas[rua]['horas']:
            ocorrencias_agrupadas[rua]['horas'][hora] = num_ocorrencias
        else:
            ocorrencias_agrupadas[rua]['horas'][hora] += num_ocorrencias

        ocorrencias_agrupadas[rua]['total'] += num_ocorrencias

    # Ordena os logradouros por número total de ocorrências de forma decrescente
    ocorrencias_agrupadas = dict(sorted(ocorrencias_agrupadas.items(), key=lambda x: x[1]['total'], reverse=True))

    # Ocorrências com horário '00:00:00' (horário manual)
    ocorrencias_sem_horario = Roubo.objects.filter(bairro=bairro, hora_ocorrencia='00:00:00').count()

    context = {
        'bairro': bairro,
        'ocorrencias_agrupadas': ocorrencias_agrupadas,
        'ocorrencias_sem_horario': ocorrencias_sem_horario,
    }

    return render(request, 'detalhes_ocorrencia.html', context)


def pesquisar_bairro(request):
    # Obtém o termo de busca enviado pelo formulário
    query = request.GET.get('q')

    # Inicializa uma variável para armazenar os resultados da busca
    bairros_encontrados = None

    # Se houver um termo de busca, realiza a busca no banco de dados
    if query:
        bairros_encontrados = Bairro.objects.filter(nome__icontains=query)

    # Cria um contexto para passar as informações para o template
    context = {
        'query': query,
        'bairros_encontrados': bairros_encontrados,
    }

    # Renderiza o template com os resultados da busca
    return render(request, 'pesquisa_bairro.html', context)

def feedback(request):
    return render(request, 'feedback.html')



def feedback_success(request):
    return render(request, 'feedback_success.html')


# Listar todos os bairros
def listar_bairros(request):

    return render(request, 'listar_bairros.html')


# Editar um bairro
def editar_bairro(request, bairro_id):
    return render(request, 'editar_bairro.html')


# Deletar um bairro
def deletar_bairro(request):
    return render(request, 'deletar_bairro.html')

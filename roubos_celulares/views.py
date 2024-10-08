from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404
from .models import Bairro, Roubo
from .mapa import gerar_mapa
from urllib.parse import unquote


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

    # Se houver um termo de busca, realiza a busca no banco de dados
    if query:
        # Decodifica o termo de busca e remove espaços extras no início ou fim
        query = unquote(query).strip()

        # Remove todos os espaços da query para criar uma busca mais flexível
        query_sem_espacos = query.replace(' ', '')

        # Faz a busca pelo nome do bairro, ignorando maiúsculas/minúsculas
        bairros_encontrados = Bairro.objects.filter(
            # Busca pelo nome do bairro com e sem espaços
            Q(nome__icontains=query) | Q(nome__icontains=query_sem_espacos)
        ).annotate(num_ocorrencias=Count('roubo'))

    # Constrói uma lista de dicionários com os dados necessários para o mapa
    bairros_info = []
    for bairro in bairros_encontrados:
        bairros_info.append({
            'nome': bairro.nome,
            'latitude': bairro.latitude,
            'longitude': bairro.longitude,
            'num_ocorrencias': bairro.num_ocorrencias
        })

    # Gera o mapa usando a função gerar_mapa
    mapa_html = gerar_mapa(bairros_info)

    # Cria um contexto para passar as informações para o template
    context = {
        'query': query,
        'bairros_encontrados': bairros_encontrados,
        'mapa_html': mapa_html,
    }

    # Renderiza o template com os resultados da busca
    return render(request, 'pesquisa_bairro.html', context)



def listar_ocorrencias(request):
    # Obtenha todas as ocorrências
    ocorrencias = Roubo.objects.all()
    ocorrencias_info = []

    # Contar ocorrências por bairro
    ocorrencias_por_bairro = Roubo.contar_ocorrencias_por_bairro()

    for ocorrencia in ocorrencias:
        # Verifica se a latitude e longitude são diferentes de 0.0
        if ocorrencia.bairro.latitude != 0.0 and ocorrencia.bairro.longitude != 0.0:
            # Conta o número de ocorrências para o bairro atual
            num_ocorrencias = next(
                (item['num_ocorrencias'] for item in ocorrencias_por_bairro if item['bairro__nome'] == ocorrencia.bairro.nome),
                0
            )

            ocorrencias_info.append({
                'bairro': ocorrencia.bairro.nome,
                'rua': ocorrencia.rua,
                'latitude': ocorrencia.bairro.latitude,
                'longitude': ocorrencia.bairro.longitude,
                'hora': ocorrencia.hora_ocorrencia.strftime('%H:%M'),
                'num_ocorrencias': num_ocorrencias  # Adiciona o número de ocorrências
            })
    print(ocorrencias_info)
    # Gera o mapa com todas as ocorrências
    mapa_html = gerar_mapa(ocorrencias_info)

    context = {
        'ocorrencias_info': ocorrencias_info,
        'mapa_html': mapa_html,
    }

    return render(request, 'listar_ocorrencias.html', context)


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

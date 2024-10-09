from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404
from .models import Bairro, Roubo
from .mapa import gerar_mapa
from urllib.parse import unquote
from .utils import contar_ocorrencias_por_bairro





def mapa_roubos(request):
    # Filtra todos os roubos e calcula os 5 bairros mais atacados, filtrando pela cidade
    bairros_mais_atacados = (
        Roubo.objects.filter(
            cidade__in=['S.PAULO']  # Agora filtrando diretamente pela cidade no modelo Roubo
        )
        .values('bairro__nome')
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


def bairros_fora_sao_paulo(request):
    # Filtra todos os roubos que não sejam em São Paulo
    bairros_mais_atacados_fora_saopaulo = (
        Roubo.objects.exclude(cidade__iexact='S.PAULO')  # Exclui registros com cidade 'S.PAULO'
        .values('bairro__nome', 'cidade')
        .annotate(num_ocorrencias=Count('id'))
        .order_by('-num_ocorrencias')[:5]  # Mostra os 5 bairros mais atacados
    )


    # Coleta as informações dos bairros
    bairros_info = []
    for bairro_data in bairros_mais_atacados_fora_saopaulo:
        bairro_obj = Bairro.objects.filter(nome__iexact=bairro_data['bairro__nome']).first()
        if bairro_obj and bairro_obj.latitude is not None and bairro_obj.longitude is not None:
            bairros_info.append({
                'id': bairro_obj.id,
                'nome': bairro_obj.nome,
                'cidade': bairro_data['cidade'],  # Adiciona o nome da cidade
                'num_ocorrencias': bairro_data['num_ocorrencias'],
                'latitude': bairro_obj.latitude,
                'longitude': bairro_obj.longitude
            })

    # Gera o mapa com os dados coletados
    mapa_html = gerar_mapa(bairros_info)

    context = {
        'bairros_info': bairros_info,
        'mapa_html': mapa_html,
    }

    return render(request, 'bairros_fora_sao_paulo.html', context)


def detalhes_ocorrencia(request, id):
    bairro = get_object_or_404(Bairro, id=id)

    # Chama a função auxiliar para obter os dados de ocorrências
    ocorrencias_agrupadas, ocorrencias_sem_horario = contar_ocorrencias_por_bairro(bairro)

    # Obtemos todas as ocorrências associadas ao bairro para pegar a cidade
    ocorrencias = Roubo.objects.filter(bairro=bairro)

    # Considerando que todas as ocorrências têm a mesma cidade, pegamos a cidade da primeira ocorrência
    cidade = ocorrencias.first().cidade if ocorrencias.exists() else 'Cidade não especificada'

    context = {
        'bairro': bairro,
        'cidade': cidade,  # Passando a cidade para o contexto
        'ocorrencias_agrupadas': ocorrencias_agrupadas,
        'ocorrencias_sem_horario': ocorrencias_sem_horario,
    }
    print(context)
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

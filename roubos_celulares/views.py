from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .mapa import gerar_mapa
from urllib.parse import unquote
from .utils import contar_ocorrencias_por_bairro
from .forms import *
from django.contrib import messages


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
            # Pega a cidade da primeira ocorrência de roubo associada ao bairro
            primeira_ocorrencia = Roubo.objects.filter(bairro=bairro_obj).first()
            cidade = primeira_ocorrencia.cidade if primeira_ocorrencia else 'Cidade não especificada'

            bairros_info.append({
                'id': bairro_obj.id,  # Adiciona o ID do bairro
                'nome': bairro_obj.nome,
                'cidade': cidade,  # Adiciona a cidade aqui
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

    return render(request, 'detalhes_ocorrencia.html', context)


def pesquisar_bairro(request):
    # Obtém o termo de busca enviado pelo formulário
    query = request.GET.get('q')

    # Inicializa uma lista vazia de bairros e a variável para o campo de pesquisa
    bairros_info = []
    bairros_encontrados = None

    # Se houver um termo de busca válido, realiza a busca no banco de dados
    if query and query.strip():  # Verifica se a query não é vazia ou composta apenas por espaços
        # Decodifica o termo de busca e remove espaços extras no início ou fim
        query = unquote(query).strip()
        # Remove todos os espaços da query para criar uma busca mais flexível
        query_sem_espacos = query.replace(' ', '')

        # Faz a busca pelo nome do bairro, ignorando maiúsculas/minúsculas
        bairros_encontrados = Bairro.objects.filter(
            Q(nome__icontains=query) | Q(nome__icontains=query_sem_espacos)
        ).annotate(num_ocorrencias=Count('roubo'))

        # Constrói uma lista de dicionários com os dados necessários para o mapa
        for bairro in bairros_encontrados:
            cidade = bairro.roubo_set.first().cidade if bairro.roubo_set.exists() else "Cidade não especificada"
            bairros_info.append({
                'id': bairro.id,
                'nome': bairro.nome,
                'latitude': bairro.latitude,
                'longitude': bairro.longitude,
                'num_ocorrencias': bairro.num_ocorrencias,
                'cidade': cidade,
            })

    # Gera o mapa usando a função gerar_mapa
    mapa_html = gerar_mapa(bairros_info)

    # Renderiza a página com ou sem resultados
    return render(request, 'pesquisa_bairro.html', {
        'query': query if query and query.strip() else '',  # Campo vazio se a query for vazia
        'bairros_info': bairros_info,
        'bairros_encontrados': bairros_encontrados,
        'mapa_html': mapa_html,  # Passa o mapa para o template
    })


def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            Feedback.objects.create(
                nome=form.cleaned_data['nome'],
                email=form.cleaned_data['email'],
                experiencia=form.cleaned_data['experiencia'],
                melhorias=form.cleaned_data['melhorias'],
                # Ajuste os comentários se necessário
                comentario=form.cleaned_data.get('comentario', ''),  # Usando o 'comentario' aqui
            )
            return redirect('feedback_success')
    else:
        form = FeedbackForm()

    return render(request, 'feedback.html', {'form': form})

def feedback_success(request):
    return render(request, 'feedback_success.html')


def gerenciar_bairros(request):
    query = request.GET.get('q')  # Captura o termo digitado
    if query:
        bairros = Bairro.objects.filter(nome__icontains=query)  # Filtro por nome do bairro
    else:
        bairros = Bairro.objects.all()  # Exibe todos os bairros se não houver query

    context = {
        'bairros': bairros,
        'query': query,
    }
    return render(request, 'gerenciar_bairros.html', context)

@login_required
def detalhes_bairro(request, bairro_id):
    bairro = get_object_or_404(Bairro, id=bairro_id)
    roubos = Roubo.objects.filter(bairro=bairro)

    context = {
        'bairro': bairro,
        'roubos': roubos,
    }
    return render(request, 'detalhes_bairro.html', context)

# Função para verificar se o usuário é superusuário
def is_superuser(user):
    return user.is_superuser


# View para editar um Bairro
@login_required
@user_passes_test(is_superuser)
def editar_bairro(request, bairro_id):
    bairro = get_object_or_404(Bairro, id=bairro_id)
    if request.method == 'POST':
        form = BairroForm(request.POST, instance=bairro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bairro atualizado com sucesso!')
            return redirect('detalhes_bairro', bairro_id=bairro.id)
    else:
        form = BairroForm(instance=bairro)

    contexto = {
        'form': form,
        'bairro': bairro,
    }
    return render(request, 'editar_bairro.html', contexto)


# View para deletar um Bairro
@login_required
@user_passes_test(is_superuser)
def deletar_bairro(request, bairro_id):
    bairro = get_object_or_404(Bairro, id=bairro_id)
    if request.method == 'POST':
        bairro.delete()
        messages.success(request, 'Bairro deletado com sucesso!')
        return redirect('gerenciar_bairros')

    contexto = {
        'bairro': bairro,
    }
    return render(request, 'deletar_bairro.html', contexto)


# View para editar uma ocorrência de Roubo
@login_required
@user_passes_test(is_superuser)
def editar_roubo(request, roubo_id):
    roubo = get_object_or_404(Roubo, id=roubo_id)
    if request.method == 'POST':
        form = RouboForm(request.POST, instance=roubo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ocorrência atualizada com sucesso!')
            return redirect('detalhes_bairro', bairro_id=roubo.bairro.id)
    else:
        form = RouboForm(instance=roubo)

    contexto = {
        'form': form,
        'roubo': roubo,
    }
    return render(request, 'editar_roubo.html', contexto)


# View para deletar uma ocorrência de Roubo
@login_required
@user_passes_test(is_superuser)
def deletar_roubo(request, roubo_id):
    roubo = get_object_or_404(Roubo, id=roubo_id)
    bairro_id = roubo.bairro.id
    if request.method == 'POST':
        roubo.delete()
        messages.success(request, 'Ocorrência deletada com sucesso!')
        return redirect('detalhes_bairro', bairro_id=bairro_id)

    contexto = {
        'roubo': roubo,
    }
    return render(request, 'deletar_roubo.html', contexto)



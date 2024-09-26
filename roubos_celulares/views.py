from django.db.models import Count
from django.shortcuts import render
from .models import *
from django.http import JsonResponse, HttpResponse
import folium

def mapa_roubos(request):
    quantidade_por_pagina = 5

    # Filtra os roubos
    roubos = Roubo.objects.all()

    # Calcula os 5 primeiros bairros com mais ocorrências de roubos
    bairros_mais_atacados = (
        roubos.values('bairro__nome')
        .annotate(num_ocorrencias=Count('bairro'))
        .order_by('-num_ocorrencias')[:quantidade_por_pagina]
    )

    # Cria um mapa Folium
    m = folium.Map(location=[-23.5505, -46.6333], zoom_start=12)

    # Adiciona marcadores para cada bairro
    for bairro_data in bairros_mais_atacados:
        bairro_obj = Bairro.objects.filter(nome__iexact=bairro_data['bairro__nome']).first()

        if bairro_obj and bairro_obj.latitude is not None and bairro_obj.longitude is not None:
            folium.Marker(
                location=[bairro_obj.latitude, bairro_obj.longitude],
                popup=f"{bairro_obj.nome}: {bairro_data['num_ocorrencias']} ocorrências",
                icon=folium.Icon(color='blue')
            ).add_to(m)

    # Renderiza o HTML do mapa
    mapa_html = m._repr_html_()

    context = {
        'bairros_mais_atacados': bairros_mais_atacados,
        'mapa_html': mapa_html,
    }

    return render(request, 'filtrar_roubos.html', context)

def carregar_bairros(request):
    try:
        offset = int(request.GET.get('offset', 0))
        limit = 5  # O número de bairros que você deseja carregar a cada requisição

        # Obtenha os próximos bairros a partir do offset
        bairros = Bairro.objects.all()[offset:offset + limit]

        # Verifique se 'related_name' está correto ou use 'roubo_set'
        bairros_lista = [{'bairro': bairro.nome, 'num_ocorrencias': bairro.roubo_set.count()} for bairro in bairros]

        return JsonResponse({'bairros': bairros_lista})

    except Exception as e:
        # Log da exceção para depuração
        print(f"Erro ao carregar bairros: {str(e)}")
        return JsonResponse({'error': 'Ocorreu um erro ao carregar os bairros.'}, status=500)


def remover_bairro(request, id):
    if request.method == 'DELETE':
        try:
            bairro = Bairro.objects.get(id=id)
            bairro.delete()
            return HttpResponse(status=204)  # Sucesso
        except Bairro.DoesNotExist:
            return JsonResponse({'error': 'Bairro não encontrado'}, status=404)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


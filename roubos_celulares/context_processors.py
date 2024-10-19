from django.db.models import Min, Max
from .models import Roubo


def datas_ocorrencias(request):
    # Filtrar apenas ocorrências do ano de 2024
    ocorrencias_2024 = Roubo.objects.filter(data_ocorrencia__year=2024)

    # Obter a primeira e a última data de 2024
    primeira_data = ocorrencias_2024.aggregate(Min('data_ocorrencia'))['data_ocorrencia__min']
    ultima_data = ocorrencias_2024.aggregate(Max('data_ocorrencia'))['data_ocorrencia__max']

    return {
        'primeira_data': primeira_data,
        'ultima_data': ultima_data,
    }

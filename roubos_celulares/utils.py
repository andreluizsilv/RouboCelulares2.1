from django.db.models import Count
from .models import Roubo

def contar_ocorrencias_por_bairro(bairro):
    # Filtra as ocorrências relacionadas ao bairro
    ocorrencias = (
        Roubo.objects.filter(bairro=bairro)
        .exclude(hora_ocorrencia='00:00:00')
        .exclude(rua__icontains='VEDAÇÃO DA DIVULGAÇÃO DOS DADOS RELATIVOS')
        .values('rua', 'hora_ocorrencia')
        .annotate(num_ocorrencias=Count('id'))
        .order_by('-num_ocorrencias')
    )

    # Agrupa as ocorrências por logradouro e horários
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

    # Ocorrências com horário '00:00:00'
    ocorrencias_sem_horario = Roubo.objects.filter(bairro=bairro, hora_ocorrencia='00:00:00').count()

    return ocorrencias_agrupadas, ocorrencias_sem_horario

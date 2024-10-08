from django.db import models
from django.db.models import Count
import datetime

class Bairro(models.Model):
    nome = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'Bairro:{self.nome}'


class Roubo(models.Model):
    data_ocorrencia = models.DateField()
    hora_ocorrencia = models.TimeField(default=datetime.time(0, 0, 0))
    rua = models.CharField(max_length=255)
    bairro = models.ForeignKey('Bairro', on_delete=models.CASCADE)
    cidade = models.CharField(max_length=255, default='Cidade não especificada')  # Adicione este campo



    @classmethod
    def contar_ocorrencias_por_bairro(cls):
        return cls.objects.values('bairro__nome').annotate(
            num_ocorrencias=Count('id'),
            horarios=Count('hora_ocorrencia')
        )

    def __str__(self):
        return f'Rua:{self.rua}, Bairro:{self.bairro.nome}, Cidade:{self.cidade}, Data da Ocorrencia:{self.data_ocorrencia}'


class Feedback(models.Model):
    nome = models.CharField(max_length=100, default='Anonimo')
    email = models.EmailField(default='no-reply@example.com')
    experiencia = models.CharField(max_length=20, choices=[
        ('excelente', 'Excelente'),
        ('boa', 'Boa'),
        ('regular', 'Regular'),
        ('ruim', 'Ruim'),
    ])
    melhorias = models.CharField(
        max_length=20,
        choices=[
            ('nada', 'Nada'),
            ('pequenas', 'Pequenas mudanças'),
            ('moderadas', 'Mudanças moderadas'),
            ('grandes', 'Mudanças grandes'),
        ],
        default='nada'  # Definindo um valor padrão aqui
    )

    deixar_informacao = models.CharField(
        max_length=3,
        choices=[('sim', 'Sim'), ('nao', 'Não')],
        default='nao'  # Definindo 'nao' como padrão
    )
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Nome: {self.nome} # Email:  {self.email} # Informação: {self.deixar_informacao}"

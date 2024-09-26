from django.db import models

class Bairro(models.Model):
    nome = models.CharField(max_length=255)  # Nome do bairro como um campo de texto
    latitude = models.FloatField(null=True, blank=True)  # Permitir valores nulos
    longitude = models.FloatField(null=True, blank=True)  # Permitir valores nulos

    def __str__(self):
        return self.nome

class Roubo(models.Model):
    data_ocorrencia = models.DateField()
    hora_ocorrencia = models.TimeField(null=True, blank=True)
    rua = models.CharField(max_length=255)
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE)
    cidade = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.rua}, {self.bairro.nome}, {self.data_ocorrencia}'


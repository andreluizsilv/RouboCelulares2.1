from django.db import models

class Roubo(models.Model):
    data_ocorrencia_bo = models.DateTimeField()
    hora_ocorrencia = models.CharField(max_length=8)
    rua = models.CharField(max_length=255)
    bairro = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.bairro}, {self.cidade} - {self.data_ocorrencia_bo} {self.hora_ocorrencia}"

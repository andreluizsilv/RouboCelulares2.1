from django import forms
from .models import *


class BairroForm(forms.ModelForm):
    class Meta:
        model = Bairro
        fields = ['nome', 'latitude', 'longitude']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class RouboForm(forms.ModelForm):
    class Meta:
        model = Roubo
        fields = ['rua', 'hora_ocorrencia', 'cidade', 'data_ocorrencia']
        widgets = {
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'hora_ocorrencia': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'data_ocorrencia': forms.DateInput(attrs={'class':'form-control', 'type': 'date'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['nome', 'email', 'experiencia', 'melhorias', 'deixar_informacao', 'comentario']

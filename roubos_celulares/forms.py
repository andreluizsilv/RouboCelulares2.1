from django import forms
from .models import Bairro, Feedback


class BairroForm(forms.ModelForm):
    class Meta:
        model = Bairro
        fields = ['nome', 'latitude', 'longitude']



class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['nome', 'email', 'experiencia', 'melhorias', 'deixar_informacao', 'comentario']

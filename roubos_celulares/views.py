from django.shortcuts import render

# Create your views here.
def mapa_roubos(request):
    return render(request,'filtrar_roubos.html')
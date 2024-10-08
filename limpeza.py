import os
import django
from geopy.geocoders import Nominatim
from time import sleep

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'celulares_subtraidos.settings')
django.setup()

# Importar os modelos necessários
from roubos_celulares.models import Bairro

# Inicializa o geolocalizador
geolocator = Nominatim(user_agent="celulares_subtraidos_app")


# Função para verificar bairros com coordenadas ausentes e preenchê-las
def verificar_bairros_sem_coordenadas():
    # Filtra os bairros onde latitude ou longitude é None ou 0.0
    bairros_sem_coordenadas = Bairro.objects.filter(
        latitude__isnull=True) | Bairro.objects.filter(
        longitude__isnull=True) | Bairro.objects.filter(
        latitude=0.0) | Bairro.objects.filter(
        longitude=0.0)

    if bairros_sem_coordenadas.exists():
        print(f"Encontrados {bairros_sem_coordenadas.count()} bairros com coordenadas ausentes:")
        for bairro in bairros_sem_coordenadas:
            print(f"Bairro: {bairro.nome}, Latitude: {bairro.latitude}, Longitude: {bairro.longitude}")

            # Buscar coordenadas com base no nome do bairro
            try:
                location = geolocator.geocode(bairro.nome)
                if location:
                    print(
                        f"Coordenadas encontradas para {bairro.nome}: Latitude {location.latitude}, Longitude {location.longitude}")
                    # Atualiza o bairro com as coordenadas encontradas
                    bairro.latitude = location.latitude
                    bairro.longitude = location.longitude
                    bairro.save()
                    print(f"Coordenadas atualizadas no banco de dados para o bairro {bairro.nome}.")
                else:
                    print(f"Não foi possível encontrar coordenadas para o bairro {bairro.nome}.")
            except Exception as e:
                print(f"Erro ao tentar buscar coordenadas para {bairro.nome}: {e}")

            # Pausa para evitar exceder o limite de requisições da API do Nominatim
            sleep(2)
    else:
        print("Nenhum bairro com coordenadas ausentes encontrado.")


if __name__ == "__main__":
    verificar_bairros_sem_coordenadas()

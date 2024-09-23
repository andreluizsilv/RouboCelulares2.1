from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd
from roubos_celulares.models import Roubo  # Importe seu modelo Django
from django.db import transaction

# Inicializar o geolocalizador
geolocator = Nominatim(user_agent="geoapiExercises")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Função para verificar se latitude ou longitude são inválidas (nulas ou 0.000000)
def coordenadas_invalidas(lat, lon):
    return pd.isnull(lat) or pd.isnull(lon) or lat == 0.000000 or lon == 0.000000

# Função para obter latitude e longitude a partir do nome do bairro (usando geopy)
def obter_coordenadas_por_bairro(bairro, cidade):
    try:
        location = geocode(f"{bairro}, {cidade}", language='pt')
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Erro ao geocodificar o bairro '{bairro}': {e}")
    return None, None

# Função principal para tratar os dados de latitude, longitude e bairro
def tratar_dados(df):
    for i, row in df.iterrows():
        if coordenadas_invalidas(row['LATITUDE'], row['LONGITUDE']) and pd.notnull(row['BAIRRO']):
            # Tentar obter coordenadas com base no bairro e cidade
            lat, lon = obter_coordenadas_por_bairro(row['BAIRRO'], row['CIDADE'])
            if lat and lon:
                df.at[i, 'LATITUDE'] = lat
                df.at[i, 'LONGITUDE'] = lon
    return df

# Ler o arquivo Excel
celulares_roubados_df = pd.read_excel('celulares_roubados_tratados.xlsx')

# Aplicar a função de tratamento no DataFrame
celulares_roubados_df = tratar_dados(celulares_roubados_df)

# Verificar quantos valores nulos ainda restam em LATITUDE e LONGITUDE
print("Valores nulos restantes após o tratamento:")
print(celulares_roubados_df[['LATITUDE', 'LONGITUDE']].isnull().sum())

# Exemplo de verificar os dados tratados
print(celulares_roubados_df[['BAIRRO', 'LATITUDE', 'LONGITUDE']].head())

# Função para salvar os dados no banco de dados Django
def salvar_dados_no_banco(df):
    with transaction.atomic():  # Garantir que todos os dados sejam salvos ou revertidos em caso de erro
        for i, row in df.iterrows():
            roubo = Roubo(
                data_ocorrencia=row['DATA_OCORRENCIA'],
                hora_ocorrencia=row['HORA_OCORRENCIA'],
                rua=row['RUA'],
                bairro=row['BAIRRO'],
                cidade=row['CIDADE'],
                latitude=row['LATITUDE'],
                longitude=row['LONGITUDE'],
            )
            roubo.save()  # Salvar cada registro no banco de dados

# Salvar os dados tratados no banco de dados
salvar_dados_no_banco(celulares_roubados_df)

import os
import django
import pandas as pd

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'celulares_subtraidos.settings')
django.setup()

# Importar os modelos necessários
from roubos_celulares.models import Roubo, Bairro

def processar_hora(hora):
    if pd.isna(hora) or hora == 'Hora desconhecida':
        return pd.to_datetime('00:00:00').time()  # Preencher com horário padrão
    try:
        hora_convertida = pd.to_datetime(hora, format='%H:%M:%S', errors='coerce')
        if pd.isna(hora_convertida):
            hora_convertida = pd.to_datetime(hora, format='%H:%M', errors='coerce')
        return hora_convertida.time() if not pd.isna(hora_convertida) else pd.to_datetime('00:00:00').time()
    except (ValueError, TypeError):
        return pd.to_datetime('00:00:00').time()  # Preencher com horário padrão

def limpar_e_salvar_bairros(bairros_df):
    try:
        bairros_df = bairros_df.dropna(subset=['LATITUDE', 'LONGITUDE', 'BAIRRO'])
        bairros_df = bairros_df.drop_duplicates(subset=['BAIRRO', 'LATITUDE', 'LONGITUDE'])

        bairros_agrupados_df = bairros_df.groupby('BAIRRO').agg({
            'LATITUDE': 'first',
            'LONGITUDE': 'first'
        }).reset_index()

        for index, row in bairros_agrupados_df.iterrows():
            if pd.isna(row['LATITUDE']) or pd.isna(row['LONGITUDE']):
                print(f"Bairro {row['BAIRRO']} possui coordenadas nulas e será ignorado.")
                continue

            obj, created = Bairro.objects.update_or_create(
                nome=row['BAIRRO'],
                defaults={'latitude': row['LATITUDE'], 'longitude': row['LONGITUDE']}
            )
            if created:
                print(f"Bairro {row['BAIRRO']} criado com sucesso!")
            else:
                print(f"Bairro {row['BAIRRO']} atualizado com sucesso!")

        print("Dados de bairros salvos no banco de dados com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar os dados de bairros: {str(e)}")

def limpar_e_salvar_roubos(celulares_df):
    try:
        celulares_df['HORA_OCORRENCIA'] = celulares_df['HORA_OCORRENCIA'].apply(processar_hora)
        celulares_df['RUA'] = celulares_df['RUA'].fillna('RUA desconhecida')
        celulares_df['BAIRRO'] = celulares_df['BAIRRO'].fillna('Bairro desconhecido')
        celulares_df['CIDADE'] = celulares_df['CIDADE'].fillna('Cidade desconhecida')  # Adicionei o preenchimento para cidade

        roubos = []
        for index, row in celulares_df.iterrows():
            try:
                bairro_obj = Bairro.objects.filter(nome=row['BAIRRO']).first()

                if not bairro_obj or bairro_obj.latitude is None or bairro_obj.longitude is None:
                    print(f"Bairro '{row['BAIRRO']}' não possui coordenadas válidas. Ignorando roubo na linha {index}.")
                    continue  # Ignora este roubo

                roubo = Roubo(
                    data_ocorrencia=row['DATA_OCORRENCIA'],  # Ajustado para o campo correto
                    hora_ocorrencia=row['HORA_OCORRENCIA'],
                    rua=row['RUA'],
                    bairro=bairro_obj,
                    cidade=row['CIDADE'],  # Adicionando o campo 'cidade'
                )
                roubos.append(roubo)
            except Exception as e:
                print(f"Erro ao processar o roubo na linha {index}: {str(e)}")

        if roubos:
            Roubo.objects.bulk_create(roubos)
            print("Dados de roubos salvos no banco de dados com sucesso!")
        else:
            print("Nenhum roubo foi salvo, todos os registros foram ignorados devido a erros.")
    except Exception as e:
        print(f"Erro ao salvar os dados de roubos: {str(e)}")

if __name__ == "__main__":
    df = pd.read_excel('celulares_roubados_normalizados.xlsx')
    bairros_df = df[['BAIRRO', 'LATITUDE', 'LONGITUDE']].drop_duplicates()

    limpar_e_salvar_bairros(bairros_df)  # Primeiro, salva os bairros
    limpar_e_salvar_roubos(df)  # Depois, salva os roubos

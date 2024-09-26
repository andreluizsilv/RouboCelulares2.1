import pandas as pd
from roubos_celulares.models import Roubo, Bairro

# Carregar o arquivo Excel com os dados tratados
df = pd.read_excel('dados_tratados_completos.xlsx')


# Função para salvar os dados no banco de dados
def salvar_dados_no_banco(df):
    registros_para_inserir = []

    for _, row in df.iterrows():
        # Obter o nome do bairro
        nome_bairro = row['BAIRRO']

        # Pular registros onde o bairro é "deletar"
        if nome_bairro == "deletar":
            print(f"Registro com bairro 'deletar' encontrado e será ignorado: {row}")
            continue  # Pula esta linha se o bairro for "deletar"

        # Verificar se o bairro não é nulo
        if pd.notnull(nome_bairro):
            # Criar ou obter o bairro
            bairro, created = Bairro.objects.get_or_create(
                nome=nome_bairro,
                defaults={
                    'latitude': row['LATITUDE'] if pd.notnull(row['LATITUDE']) else None,
                    'longitude': row['LONGITUDE'] if pd.notnull(row['LONGITUDE']) else None
                }
            )
        else:
            print(f"Bairro não encontrado para a linha: {row}")  # Log da linha sem bairro
            continue  # Pula esta linha se o bairro não for válido

        # Criar a instância do modelo Roubo
        roubo = Roubo(
            data_ocorrencia=row['DATA_OCORRENCIA'],
            hora_ocorrencia=row['HORA_OCORRENCIA'],
            rua=row['RUA'],
            bairro=bairro  # Atribuir a instância de Bairro
        )

        registros_para_inserir.append(roubo)

    # Salvar todos os registros no banco de dados de uma só vez
    if registros_para_inserir:
        Roubo.objects.bulk_create(registros_para_inserir)
        print(f"{len(registros_para_inserir)} registros inseridos com sucesso.")
    else:
        print("Nenhum registro foi inserido.")


# Chamar a função para salvar os dados no banco
salvar_dados_no_banco(df)

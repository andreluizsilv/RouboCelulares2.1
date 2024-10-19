import folium

def gerar_mapa(bairros):
    # Verifica se há apenas um bairro (caso de pesquisa)
    if len(bairros) == 1:
        bairro_data = bairros[0]  # Pega os dados do único bairro
        if bairro_data['latitude'] and bairro_data['longitude']:
            # Centraliza o mapa no bairro pesquisado
            m = folium.Map(location=[bairro_data['latitude'], bairro_data['longitude']], zoom_start=14)
        else:
            return "<p>Coordenadas ausentes para o bairro pesquisado.</p>"
    else:
        # Se houver mais de um bairro, centraliza o mapa em São Paulo
        m = folium.Map(location=[-23.5505, -46.6333], zoom_start=9)

    # Adiciona os marcadores para os bairros
    for bairro_data in bairros:
        if bairro_data['latitude'] and bairro_data['longitude']:
            folium.Marker(
                location=[bairro_data['latitude'], bairro_data['longitude']],
                popup=f"{bairro_data['nome']}: {bairro_data['num_ocorrencias']} ocorrências",
                icon=folium.Icon(color='blue')  # Ou vermelho, conforme desejado
            ).add_to(m)
        else:
            print(f"Coordenadas ausentes para o bairro: {bairro_data['nome']}")

    # Renderiza o mapa como HTML
    return m._repr_html_()

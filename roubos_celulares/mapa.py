import folium

def gerar_mapa(bairros):
    # Cria um mapa Folium
    m = folium.Map(location=[-23.5505, -46.6333], zoom_start=12)

    # Adiciona marcadores para os bairros
    for bairro_data in bairros:
        folium.Marker(
            location=[bairro_data['latitude'], bairro_data['longitude']],
            popup=f"{bairro_data['nome']}: {bairro_data['num_ocorrencias']} ocorrências",
            icon=folium.Icon(color='blue')
        ).add_to(m)

    # Renderiza o mapa como HTML
    return m._repr_html_()

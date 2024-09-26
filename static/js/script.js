
document.getElementById('carregar-mais').addEventListener('click', function() {
    let offset = document.querySelectorAll('#bairros-lista li').length;
    fetch(`/carregar_bairros/?offset=${offset}`)
    .then(response => response.json())
    .then(data => {
        let lista = document.getElementById('bairros-lista');
        data.bairros.forEach(bairro => {
            let li = document.createElement('li');
            li.id = `bairro-${bairro.id}`;
            li.innerHTML = `${bairro.bairro}: ${bairro.num_ocorrencias} ocorrências`;
            lista.appendChild(li);

            // Adicione o marcador no mapa
            // Aqui você deve criar um novo marcador no Folium ou no Leaflet
            addMarkerToMap(bairro); // Crie essa função para adicionar o marcador
        });
        if (data.bairros.length === 0) {
            document.getElementById('carregar-mais').style.display = 'none';
        }
    })
    .catch(error => console.log('Erro:', error));
});

// Função para adicionar um marcador ao mapa
function addMarkerToMap(bairro) {
    // Aqui você deve ter a lógica para adicionar um marcador
    // Para Folium, isso pode não ser direto, considere usar Leaflet
}

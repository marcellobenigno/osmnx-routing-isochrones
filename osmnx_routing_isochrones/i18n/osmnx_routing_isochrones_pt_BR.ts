<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="pt_BR" sourcelanguage="en">
<context>
    <name>OsmnxRouting</name>
    <message>
        <source>'{layer}' layer (directed)</source>
        <translation>camada '{layer}' (dirigida)</translation>
    </message>
    <message>
        <source>1. Download road network (OSM)</source>
        <translation>1. Baixar malha viária (OSM)</translation>
    </message>
    <message>
        <source>2. Inspect road network GeoPackage</source>
        <translation>2. Inspecionar GeoPackage da malha</translation>
    </message>
    <message>
        <source>3. Shortest path (one-way aware)</source>
        <translation>3. Menor caminho (mão e contramão)</translation>
    </message>
    <message>
        <source>4. Isochrones (reachable areas)</source>
        <translation>4. Isócronas (áreas de alcance)</translation>
    </message>
    <message>
        <source>&lt;b&gt;{layer}&lt;/b&gt; layer (directed graph written at download) — most reliable</source>
        <translation>camada &lt;b&gt;{layer}&lt;/b&gt; (grafo dirigido gravado no download) — mais confiável</translation>
    </message>
    <message>
        <source>&lt;p&gt;Builds polygons of the areas reachable within each time (e.g. &lt;b&gt;5, 10, 15&lt;/b&gt; min) over the road network.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Points&lt;/b&gt;: one point clicked on the map (… button) and/or a point layer (schools, health centres…). With &lt;i&gt;one isochrone per point&lt;/i&gt; unchecked, the points form a single coverage area (the nearest one counts).&lt;/p&gt;&lt;p&gt;&lt;b&gt;Car&lt;/b&gt;: travel time on the directed graph (one-way streets respected). &lt;b&gt;Direction&lt;/b&gt;: &lt;i&gt;from&lt;/i&gt; = where you can get to from the point; &lt;i&gt;to&lt;/i&gt; = where the point can be reached from (matters with one-way streets).&lt;br&gt;&lt;b&gt;Pedestrian&lt;/b&gt;: distance / walking speed, no direction.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Method&lt;/b&gt;: band around the reached roads (the last segment is cut in proportion to the remaining time) or concave hull of the reached nodes.&lt;/p&gt;&lt;p&gt;Optional output &lt;b&gt;Reached roads&lt;/b&gt;: each segment with its arrival time, great for gradient maps.&lt;/p&gt;</source>
        <translation>&lt;p&gt;Gera polígonos das áreas alcançáveis em cada tempo (ex.: &lt;b&gt;5, 10, 15&lt;/b&gt; min) pela malha viária.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Pontos&lt;/b&gt;: um ponto clicado no mapa (botão …) e/ou uma camada de pontos (escolas, UBS…). Com &lt;i&gt;uma isócrona por ponto&lt;/i&gt; desmarcado, os pontos formam uma única área de cobertura (vale o mais próximo).&lt;/p&gt;&lt;p&gt;&lt;b&gt;Carro&lt;/b&gt;: tempo de viagem pelo grafo dirigido (mão única respeitada). &lt;b&gt;Sentido&lt;/b&gt;: &lt;i&gt;saindo&lt;/i&gt; = até onde se chega a partir do ponto; &lt;i&gt;chegando&lt;/i&gt; = de onde se chega até o ponto (faz diferença com mão única).&lt;br&gt;&lt;b&gt;Pedestre&lt;/b&gt;: distância / velocidade de caminhada, sem sentido.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Método&lt;/b&gt;: faixa ao redor das vias alcançadas (o último trecho é cortado proporcionalmente ao tempo restante) ou envelope côncavo dos nós alcançados.&lt;/p&gt;&lt;p&gt;Saída opcional &lt;b&gt;Vias alcançadas&lt;/b&gt;: cada trecho com o tempo de chegada, ótima para mapas de gradiente.&lt;/p&gt;</translation>
    </message>
    <message>
        <source>&lt;p&gt;Computes the route between two points on the road network GeoPackage. Use the &lt;b&gt;…&lt;/b&gt; button next to Origin/Destination to click on the map.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Car&lt;/b&gt;: directed graph — one-way streets only in the allowed direction. Criterion distance (length) or time (travel_time, from OSM speed or a default per road type).&lt;br&gt;&lt;b&gt;Pedestrian&lt;/b&gt;: ignores direction; time from walking speed.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Ignore one-way&lt;/b&gt; (comparison): allows driving against traffic and flags those segments (field &lt;i&gt;wrong_way&lt;/i&gt;, dashed black), showing the error of an undirected graph.&lt;/p&gt;&lt;p&gt;Points snap to the nearest node of the largest connected component. For many routes, use &lt;i&gt;Run as Batch Process&lt;/i&gt;.&lt;/p&gt;</source>
        <translation>&lt;p&gt;Calcula a rota entre dois pontos sobre o GeoPackage da malha. Use o botão &lt;b&gt;…&lt;/b&gt; ao lado de Origem/Destino para clicar no mapa.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Carro&lt;/b&gt;: grafo dirigido — vias de mão única só no sentido permitido. Critério distância (length) ou tempo (travel_time, com a velocidade do OSM ou o padrão por tipo de via).&lt;br&gt;&lt;b&gt;Pedestre&lt;/b&gt;: ignora o sentido; tempo pela velocidade de caminhada.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Ignorar mão única&lt;/b&gt; (comparação): permite a contramão e marca esses trechos (campo &lt;i&gt;wrong_way&lt;/i&gt;, tracejado preto), mostrando o erro de um grafo não dirigido.&lt;/p&gt;&lt;p&gt;Os pontos são ligados ao nó mais próximo da maior componente conexa. Para várias rotas, use &lt;i&gt;Executar como processo em lote&lt;/i&gt;.&lt;/p&gt;</translation>
    </message>
    <message>
        <source>&lt;p&gt;Downloads the OpenStreetMap road network of a municipality (or any place Nominatim can geocode) and writes a GeoPackage with:&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&lt;b&gt;edges&lt;/b&gt;: one line per street segment (for display);&lt;/li&gt;&lt;li&gt;&lt;b&gt;arcs&lt;/b&gt;: one line per &lt;i&gt;direction of travel&lt;/i&gt; (two-way street = 2 arcs, one-way street = 1 arc digitised in the direction of traffic), used for routing;&lt;/li&gt;&lt;li&gt;&lt;b&gt;nodes&lt;/b&gt;: intersections;&lt;/li&gt;&lt;li&gt;&lt;b&gt;boundary&lt;/b&gt;: polygon of the place.&lt;/li&gt;&lt;/ul&gt;&lt;p&gt;Segments include &lt;b&gt;speed_kph&lt;/b&gt; (OSM maxspeed or a default per road type) and &lt;b&gt;travel_time&lt;/b&gt; (seconds).&lt;/p&gt;&lt;p&gt;Include state and country in the name, e.g. &lt;i&gt;Campina Grande, Paraíba, Brazil&lt;/i&gt;. Large cities may take several minutes.&lt;/p&gt;&lt;p&gt;Data © OpenStreetMap contributors (ODbL).&lt;/p&gt;</source>
        <translation>&lt;p&gt;Baixa a malha viária do OpenStreetMap de um município (ou de qualquer lugar que o Nominatim encontre) e grava um GeoPackage com:&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&lt;b&gt;edges&lt;/b&gt;: uma linha por trecho de via (para visualização);&lt;/li&gt;&lt;li&gt;&lt;b&gt;arcs&lt;/b&gt;: uma linha por &lt;i&gt;sentido de circulação&lt;/i&gt; (mão dupla = 2 arcos, mão única = 1 arco digitalizado no sentido do tráfego), usada no roteamento;&lt;/li&gt;&lt;li&gt;&lt;b&gt;nodes&lt;/b&gt;: cruzamentos;&lt;/li&gt;&lt;li&gt;&lt;b&gt;boundary&lt;/b&gt;: polígono do lugar.&lt;/li&gt;&lt;/ul&gt;&lt;p&gt;Os trechos já saem com &lt;b&gt;speed_kph&lt;/b&gt; (maxspeed do OSM ou padrão por tipo de via) e &lt;b&gt;travel_time&lt;/b&gt; (segundos).&lt;/p&gt;&lt;p&gt;Informe o nome com estado e país, ex.: &lt;i&gt;Campina Grande, Paraíba, Brasil&lt;/i&gt;. Cidades grandes podem levar vários minutos.&lt;/p&gt;&lt;p&gt;Dados © colaboradores do OpenStreetMap (ODbL).&lt;/p&gt;</translation>
    </message>
    <message>
        <source>&lt;p&gt;Writes an HTML report with, for each layer: CRS, geometry type, extent, feature count, fields with type and &lt;b&gt;% filled&lt;/b&gt; (cost attributes highlighted) and a data sample.&lt;/p&gt;&lt;p&gt;It ends with a routing feasibility diagnosis: distance, speed, direction (one-way streets) and which direction source will be used.&lt;/p&gt;</source>
        <translation>&lt;p&gt;Gera um relatório HTML com, para cada camada: SRC, tipo de geometria, extensão, nº de feições, campos com tipo e &lt;b&gt;% de preenchimento&lt;/b&gt; (atributos de custo destacados) e uma amostra dos dados.&lt;/p&gt;&lt;p&gt;Termina com um diagnóstico de viabilidade do roteamento: distância, velocidade, sentido (mão única) e qual fonte de sentido será usada.&lt;/p&gt;</translation>
    </message>
    <message>
        <source>Band around the reached roads (faithful to the network)</source>
        <translation>Faixa ao redor das vias alcançadas (fiel à rede)</translation>
    </message>
    <message>
        <source>Band width around the roads (m)</source>
        <translation>Largura da faixa ao redor das vias (m)</translation>
    </message>
    <message>
        <source>CRS</source>
        <translation>SRC</translation>
    </message>
    <message>
        <source>Car — respects one-way streets</source>
        <translation>Carro — respeita mão e contramão</translation>
    </message>
    <message>
        <source>Computing reach: {label}</source>
        <translation>Calculando alcance: {label}</translation>
    </message>
    <message>
        <source>Concave hull of the reached nodes (smoother)</source>
        <translation>Envelope côncavo dos nós alcançados (mais suave)</translation>
    </message>
    <message>
        <source>Could not open {path}</source>
        <translation>Não foi possível abrir {path}</translation>
    </message>
    <message>
        <source>Could not overwrite {path}. Remove that file's layers from the project or choose another name.</source>
        <translation>Não foi possível sobrescrever {path}. Remova do projeto as camadas desse arquivo ou escolha outro nome.</translation>
    </message>
    <message>
        <source>Could not reach the OpenStreetMap servers (Nominatim/Overpass). Check your internet connection or the proxy in Settings &gt; Options &gt; Network, or try again later.

Details: {error}</source>
        <translation>Não foi possível acessar os servidores do OpenStreetMap (Nominatim/Overpass). Verifique a conexão com a internet ou o proxy em Configurações &gt; Opções &gt; Rede, ou tente novamente mais tarde.

Detalhes: {error}</translation>
    </message>
    <message>
        <source>Criterion</source>
        <translation>Critério</translation>
    </message>
    <message>
        <source>Cross-check arcs x rebuilt edges: {pct:.2f}% identical u→v pairs</source>
        <translation>Validação cruzada arcos x reconstrução: {pct:.2f}% de pares u→v iguais</translation>
    </message>
    <message>
        <source>Destination</source>
        <translation>Destino</translation>
    </message>
    <message>
        <source>Direction (car)</source>
        <translation>Sentido (carro)</translation>
    </message>
    <message>
        <source>Direction (oneway)</source>
        <translation>Sentido (oneway)</translation>
    </message>
    <message>
        <source>Direction source</source>
        <translation>Fonte do sentido</translation>
    </message>
    <message>
        <source>Direction source: {source}</source>
        <translation>Fonte do sentido: {source}</translation>
    </message>
    <message>
        <source>Distance (km)</source>
        <translation>Distância (km)</translation>
    </message>
    <message>
        <source>Distance (length)</source>
        <translation>Distância (length)</translation>
    </message>
    <message>
        <source>Distance: {km:.2f} km | Time: {min:.1f} min | {n} segments</source>
        <translation>Distância: {km:.2f} km | Tempo: {min:.1f} min | {n} trechos</translation>
    </message>
    <message>
        <source>Distance: {km:.2f} km | Time: {min:.1f} min | {n} segments | {oneway} on one-way streets (allowed direction)</source>
        <translation>Distância: {km:.2f} km | Tempo: {min:.1f} min | {n} trechos | {oneway} em mão única (sentido permitido)</translation>
    </message>
    <message>
        <source>Done</source>
        <translation>Concluído</translation>
    </message>
    <message>
        <source>Downloading '{type}' network from Overpass (this may take a few minutes)...</source>
        <translation>Baixando a rede '{type}' do Overpass (pode levar alguns minutos)...</translation>
    </message>
    <message>
        <source>Enter a place name.</source>
        <translation>Informe o nome do lugar.</translation>
    </message>
    <message>
        <source>Enter at least one time (minutes) greater than zero.</source>
        <translation>Informe ao menos um tempo (minutos) maior que zero.</translation>
    </message>
    <message>
        <source>Extent (WGS84)</source>
        <translation>Extensão (WGS84)</translation>
    </message>
    <message>
        <source>Fastest (car only)</source>
        <translation>Mais rápida (só carro)</translation>
    </message>
    <message>
        <source>Features</source>
        <translation>Feições</translation>
    </message>
    <message>
        <source>Field</source>
        <translation>Campo</translation>
    </message>
    <message>
        <source>Field with the name of each point</source>
        <translation>Campo com o nome de cada ponto</translation>
    </message>
    <message>
        <source>Filled</source>
        <translation>Preenchido</translation>
    </message>
    <message>
        <source>Found: {name}</source>
        <translation>Encontrado: {name}</translation>
    </message>
    <message>
        <source>From the points (where you can get to)</source>
        <translation>Saindo dos pontos (até onde se chega)</translation>
    </message>
    <message>
        <source>Geocoding: {place}</source>
        <translation>Geocodificando: {place}</translation>
    </message>
    <message>
        <source>Geometry</source>
        <translation>Geometria</translation>
    </message>
    <message>
        <source>Give a point on the map and/or a point layer.</source>
        <translation>Informe um ponto no mapa e/ou uma camada de pontos.</translation>
    </message>
    <message>
        <source>Highlighted rows: cost / direction attributes.</source>
        <translation>Linhas destacadas: atributos de custo / sentido.</translation>
    </message>
    <message>
        <source>Ignore one-way streets (comparison — allows wrong way)</source>
        <translation>Ignorar mão única (comparação — permite contramão)</translation>
    </message>
    <message>
        <source>Invalid layer.</source>
        <translation>Camada inválida.</translation>
    </message>
    <message>
        <source>Invalid times: '{text}'. Use e.g. 5, 10, 15</source>
        <translation>Tempos inválidos: '{text}'. Use, por exemplo, 5, 10, 15</translation>
    </message>
    <message>
        <source>Isochrones</source>
        <translation>Isócronas</translation>
    </message>
    <message>
        <source>Layer</source>
        <translation>Camada</translation>
    </message>
    <message>
        <source>Layers</source>
        <translation>Camadas</translation>
    </message>
    <message>
        <source>Metres driven the wrong way</source>
        <translation>Metros em contramão</translation>
    </message>
    <message>
        <source>Missing layers: {layers} — routing will not work.</source>
        <translation>Camadas ausentes: {layers} — o roteamento não funcionará.</translation>
    </message>
    <message>
        <source>Missing library: {error}.

Install OSMnx into QGIS's Python from the Python Console (Plugins &gt; Python Console), then restart QGIS:

{code}

On macOS/Linux use sys.executable instead of python.exe.</source>
        <translation>Biblioteca ausente: {error}.

Instale o OSMnx no Python do QGIS pelo Terminal Python (Complementos &gt; Terminal Python) e reinicie o QGIS:

{code}

No macOS/Linux use sys.executable no lugar de python.exe.</translation>
    </message>
    <message>
        <source>Network already loaded in this session (cache).</source>
        <translation>Rede já carregada nesta sessão (cache).</translation>
    </message>
    <message>
        <source>Network type</source>
        <translation>Tipo de rede</translation>
    </message>
    <message>
        <source>No path between the points (disconnected network).</source>
        <translation>Não existe caminho entre os pontos (rede desconectada).</translation>
    </message>
    <message>
        <source>No result for '{place}'. Check the spelling and include state and country, e.g. 'Campina Grande, Paraíba, Brazil'.

Details: {error}</source>
        <translation>Nenhum resultado para '{place}'. Confira a grafia e inclua estado e país, ex.: 'Campina Grande, Paraíba, Brasil'.

Detalhes: {error}</translation>
    </message>
    <message>
        <source>Number of directed arcs</source>
        <translation>Número de arcos dirigidos</translation>
    </message>
    <message>
        <source>Number of nodes</source>
        <translation>Número de nós</translation>
    </message>
    <message>
        <source>OSMnx Routing &amp; Isochrones — road network, one-way aware routing and isochrones</source>
        <translation>OSMnx Routing &amp; Isochrones — malha viária, rotas com mão e contramão e isócronas</translation>
    </message>
    <message>
        <source>One isochrone per point (unchecked = combined coverage)</source>
        <translation>Uma isócrona por ponto (desmarcado = cobertura combinada)</translation>
    </message>
    <message>
        <source>Origin</source>
        <translation>Origem</translation>
    </message>
    <message>
        <source>Origin and destination snap to the same network node.</source>
        <translation>Origem e destino caem no mesmo nó da rede.</translation>
    </message>
    <message>
        <source>Output GeoPackage</source>
        <translation>GeoPackage de saída</translation>
    </message>
    <message>
        <source>Pedestrian — ignores street direction</source>
        <translation>Pedestre — ignora o sentido das vias</translation>
    </message>
    <message>
        <source>Pedestrian: shortest and fastest routes are the same.</source>
        <translation>Pedestre: a rota mais curta e a mais rápida coincidem.</translation>
    </message>
    <message>
        <source>Pedestrians ignore direction: 'from' and 'to' are the same.</source>
        <translation>Pedestres ignoram o sentido: saindo e chegando dão o mesmo resultado.</translation>
    </message>
    <message>
        <source>Place name (as in OSM, with state and country)</source>
        <translation>Lugar (nome no OSM, com estado e país)</translation>
    </message>
    <message>
        <source>Point (click on the map)</source>
        <translation>Ponto (clique no mapa)</translation>
    </message>
    <message>
        <source>Point layer (optional)</source>
        <translation>Camada de pontos (opcional)</translation>
    </message>
    <message>
        <source>Polygon method</source>
        <translation>Método do polígono</translation>
    </message>
    <message>
        <source>Profile</source>
        <translation>Perfil</translation>
    </message>
    <message>
        <source>Reached roads</source>
        <translation>Vias alcançadas</translation>
    </message>
    <message>
        <source>Reading nodes and edges...</source>
        <translation>Lendo nós e vias...</translation>
    </message>
    <message>
        <source>Report</source>
        <translation>Relatório</translation>
    </message>
    <message>
        <source>Road network GeoPackage</source>
        <translation>GeoPackage da malha</translation>
    </message>
    <message>
        <source>Road network inspection</source>
        <translation>Inspeção da malha viária</translation>
    </message>
    <message>
        <source>Road type (highway)</source>
        <translation>Tipo de via (highway)</translation>
    </message>
    <message>
        <source>Route</source>
        <translation>Rota</translation>
    </message>
    <message>
        <source>Routing diagnosis</source>
        <translation>Diagnóstico para roteamento</translation>
    </message>
    <message>
        <source>Sample</source>
        <translation>Amostra</translation>
    </message>
    <message>
        <source>Shortest distance</source>
        <translation>Menor distância</translation>
    </message>
    <message>
        <source>Speed (maxspeed)</source>
        <translation>Velocidade (maxspeed)</translation>
    </message>
    <message>
        <source>The 'arcs' layer overlaps 'edges' on the map; switch it off if you prefer.</source>
        <translation>A camada 'arcs' sobrepõe 'edges' no mapa; desligue-a se preferir.</translation>
    </message>
    <message>
        <source>The GeoPackage has no '{layer}' layer.</source>
        <translation>O GeoPackage não tem a camada '{layer}'.</translation>
    </message>
    <message>
        <source>The destination is {dist:.0f} m from the nearest network node.</source>
        <translation>O destino está a {dist:.0f} m do nó mais próximo da rede.</translation>
    </message>
    <message>
        <source>The origin is {dist:.0f} m from the nearest network node.</source>
        <translation>A origem está a {dist:.0f} m do nó mais próximo da rede.</translation>
    </message>
    <message>
        <source>Time (min)</source>
        <translation>Tempo (min)</translation>
    </message>
    <message>
        <source>Times in minutes (comma separated)</source>
        <translation>Tempos em minutos (separados por vírgula)</translation>
    </message>
    <message>
        <source>To the points (where they can be reached from)</source>
        <translation>Chegando aos pontos (de onde se chega até eles)</translation>
    </message>
    <message>
        <source>Type</source>
        <translation>Tipo</translation>
    </message>
    <message>
        <source>Units</source>
        <translation>Unidade</translation>
    </message>
    <message>
        <source>Using the proxy configured in QGIS.</source>
        <translation>Usando o proxy configurado no QGIS.</translation>
    </message>
    <message>
        <source>Walking speed (km/h)</source>
        <translation>Velocidade de caminhada (km/h)</translation>
    </message>
    <message>
        <source>Warning: point '{label}' is {dist:.0f} m away from the network.</source>
        <translation>Atenção: o ponto '{label}' está a {dist:.0f} m da rede.</translation>
    </message>
    <message>
        <source>Writing {path}</source>
        <translation>Gravando {path}</translation>
    </message>
    <message>
        <source>all — every road and path (incl. private)</source>
        <translation>all — todas as vias (inclui privadas)</translation>
    </message>
    <message>
        <source>all_public — every public road and path</source>
        <translation>all_public — todas as vias públicas</translation>
    </message>
    <message>
        <source>allowed direction</source>
        <translation>sentido permitido</translation>
    </message>
    <message>
        <source>basis for speed imputation</source>
        <translation>base da imputação de velocidade</translation>
    </message>
    <message>
        <source>bike — cycling network</source>
        <translation>bike — rede para bicicletas</translation>
    </message>
    <message>
        <source>clicked point</source>
        <translation>ponto clicado</translation>
    </message>
    <message>
        <source>defines one-way / two-way streets</source>
        <translation>define mão única / mão dupla</translation>
    </message>
    <message>
        <source>degrees (geographic)</source>
        <translation>graus (geográfico)</translation>
    </message>
    <message>
        <source>directed 'edges' layer</source>
        <translation>camada 'edges' dirigida</translation>
    </message>
    <message>
        <source>directed &lt;b&gt;edges&lt;/b&gt; layer (u, v, key)</source>
        <translation>camada &lt;b&gt;edges&lt;/b&gt; dirigida (u, v, key)</translation>
    </message>
    <message>
        <source>drive — public drivable roads</source>
        <translation>drive — vias públicas para veículos</translation>
    </message>
    <message>
        <source>drive_service — drivable roads + service roads</source>
        <translation>drive_service — vias para veículos + vias de serviço</translation>
    </message>
    <message>
        <source>highway (10 most common)</source>
        <translation>highway (10 mais comuns)</translation>
    </message>
    <message>
        <source>metres (projected)</source>
        <translation>metros (projetado)</translation>
    </message>
    <message>
        <source>metres; cost of the shortest path</source>
        <translation>metros; custo do menor caminho</translation>
    </message>
    <message>
        <source>rebuilt from 'edges' (from/to + oneway; {n:,} geometries re-oriented)</source>
        <translation>reconstrução a partir de 'edges' (from/to + oneway; {n:,} geometrias reorientadas)</translation>
    </message>
    <message>
        <source>rebuilt from &lt;b&gt;edges&lt;/b&gt; (from/to + oneway)</source>
        <translation>reconstrução a partir de &lt;b&gt;edges&lt;/b&gt; (from/to + oneway)</translation>
    </message>
    <message>
        <source>segments</source>
        <translation>trechos</translation>
    </message>
    <message>
        <source>the rest is imputed from the road type</source>
        <translation>o restante é imputado pelo tipo de via</translation>
    </message>
    <message>
        <source>walk — pedestrian network</source>
        <translation>walk — rede para pedestres</translation>
    </message>
    <message>
        <source>wrong way</source>
        <translation>contramão</translation>
    </message>
    <message>
        <source>{layer}: {crs}, {geom}, {n:,} features, {fields} fields</source>
        <translation>{layer}: {crs}, {geom}, {n:,} feições, {fields} campos</translation>
    </message>
    <message>
        <source>{nodes:,} nodes and {arcs:,} arcs</source>
        <translation>{nodes:,} nós e {arcs:,} arcos</translation>
    </message>
    <message>
        <source>{nodes:,} nodes | {arcs:,} arcs ({oneway:,} one-way) | largest strongly connected component: {pct:.1f}% of nodes | metric CRS {crs}</source>
        <translation>{nodes:,} nós | {arcs:,} arcos ({oneway:,} de mão única) | maior componente fortemente conexa: {pct:.1f}% dos nós | SRC métrico {crs}</translation>
    </message>
    <message>
        <source>{n} point(s) | times: {times} min | profile {profile} | direction {direction} | method {method}</source>
        <translation>{n} ponto(s) | tempos: {times} min | perfil {profile} | sentido {direction} | método {method}</translation>
    </message>
    <message>
        <source>{n} points</source>
        <translation>{n} pontos</translation>
    </message>
    <message>
        <source>{n} segment(s) driven the WRONG WAY: {m:.0f} m</source>
        <translation>{n} trecho(s) na CONTRAMÃO: {m:.0f} m</translation>
    </message>
</context>
</TS>

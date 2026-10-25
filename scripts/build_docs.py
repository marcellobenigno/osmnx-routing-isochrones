"""
Builds the documentation site in docs/ (GitHub Pages): docs/<lang>/index.html for English,
Brazilian Portuguese and Spanish from one layout, plus docs/index.html (language picker).

    python scripts/build_docs.py

Texts live in TEXTS below (same keys in every language). Figures are made by
scripts/build_docs_figures.py.
"""
import html
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
REPO = "https://github.com/marcellobenigno/osmnx-routing-isochrones"
LANGS = (("en", "English", "EN"), ("pt-br", "Português", "PT"), ("es", "Español", "ES"))
PANEL_SHOTS = {"en": "en", "pt-br": "pt", "es": "en"}     # the plugin UI has EN and PT-BR

INSTALL_CODE = """from pip._internal.cli.main import main as pip
pip(["install", "--user", "--no-deps", "osmnx"])"""

PYTHON_CODE = """import processing

# 1. download once
processing.run("osmnx_routing:download_network", {
    "PLACE": "Cabedelo, Paraíba, Brazil", "TYPE": 2,          # 2 = drive
    "OUTPUT": "/data/cabedelo.gpkg"})

# 2. route (car, fastest)
res = processing.run("osmnx_routing:shortest_path", {
    "NETWORK": "/data/cabedelo.gpkg", "PROFILE": 0, "CRITERION": 1,
    "ORIGIN": "-34.8410,-7.0323 [EPSG:4326]",
    "DESTINATION": "-34.8417,-7.0371 [EPSG:4326]",
    "OUTPUT": "TEMPORARY_OUTPUT"})
print(res["DISTANCE_KM"], res["TIME_MIN"])

# 3. isochrones of a point layer, one per point
processing.runAndLoadResults("osmnx_routing:isochrones", {
    "NETWORK": "/data/cabedelo.gpkg", "PROFILE": 1,           # 1 = pedestrian
    "POINTS": "/data/schools.gpkg", "ID_FIELD": "name", "SEPARATE": True,
    "MINUTES": "5, 10, 15", "OUTPUT": "TEMPORARY_OUTPUT", "ROADS": "TEMPORARY_OUTPUT"})"""

TEXTS = {
    # ------------------------------------------------------------------ English
    "en": {
        "title": "OSMnx Routing & Isochrones — QGIS plugin",
        "description": "Download OpenStreetMap road networks and compute one-way aware routes "
                       "and isochrones locally in QGIS, with no web service or API key.",
        "copy": "Copy",
        "nav": ["Features", "Install", "Quick start", "Map tools", "Algorithms",
                "Isochrones", "FAQ"],
        "hero_h1": "Routes and isochrones from OpenStreetMap, right inside QGIS",
        "hero_lead": "Download the street network of any town once, then calculate one-way "
                     "aware routes and reachable areas on your own computer — no routing "
                     "service, no API key, no limits.",
        "hero_badges": ["QGIS 3.28+", "Processing algorithms", "EN · PT-BR interface",
                        "GPL-2.0"],
        "hero_install": "Install the plugin", "hero_github": "Source on GitHub",
        "hero_alt": "Car isochrones of 1, 2, 3 and 4 minutes in Cabedelo, Brazil",
        "feat_k": "Why this plugin", "feat_h": "Everything runs locally, on real streets",
        "feat_intro": "The plugin wraps OSMnx and NetworkX in four Processing algorithms and "
                      "two interactive map tools.",
        "features": [
            ("🗺️", "t-green", "Your own network",
             "One click turns a place name into a GeoPackage with nodes, edges, directed "
             "arcs and the boundary."),
            ("↪️", "t-red", "One-way aware",
             "Cars follow the direction of traffic. A comparison mode shows which segments an "
             "undirected graph would drive the wrong way."),
            ("⏱️", "t-orange", "Isochrones",
             "Areas reachable in 5, 10, 15… minutes from (or to) points, with the arrival "
             "time on every road."),
            ("🖱️", "t-blue", "Click on the map",
             "Side panels keep the map free: click points, pan and zoom, and see the result "
             "at once."),
        ],
        "inst_k": "Installation", "inst_h": "Two steps, no administrator rights",
        "inst_intro": "QGIS already ships geopandas, networkx, shapely and pyproj; only "
                      "OSMnx has to be added to QGIS's Python.",
        "inst_steps": [
            ("Install OSMnx in QGIS's Python",
             "Open <b>Plugins → Python Console</b>, paste the code below and press Enter. "
             "Then restart QGIS."),
            ("Install the plugin",
             "<b>Plugins → Manage and Install Plugins</b>, search for <b>OSMnx Routing &amp; "
             "Isochrones</b>. While it is experimental, tick <i>Show also experimental "
             "plugins</i> in Settings. You can also use <i>Install from ZIP</i> with a file "
             "from the <a href='" + REPO + "/releases'>releases</a>."),
        ],
        "inst_note": "If an import error mentions another missing package (older QGIS on "
                     "Linux), run the same command without <code>--no-deps</code>. While a "
                     "library is missing, the plugin shows a warning with a <b>How to "
                     "install</b> button and its algorithms stay disabled.",
        "qs_k": "Quick start", "qs_h": "From a place name to a map in four steps",
        "qs_intro": "Download the network once; every other tool reads the GeoPackage.",
        "qs_steps": [
            ("Download the road network",
             "Processing Toolbox (<code>Ctrl+Alt+T</code>) → <b>OSMnx Routing &amp; "
             "Isochrones → 1. Download road network</b>. Type e.g. <i>Cabedelo, Paraíba, "
             "Brazil</i>, choose <i>drive</i> and pick an output file."),
            ("Check what you got (optional)",
             "<b>2. Inspect road network GeoPackage</b> writes an HTML report: CRS, fields, "
             "fill rate and a routing diagnosis."),
            ("Click a route",
             "Toolbar button <b>Route on the map</b>: click the origin, then the destination."),
            ("Click isochrones",
             "Toolbar button <b>Isochrones on the map</b>: every click adds a point and the "
             "areas are recalculated."),
        ],
        "wf": ["Place name", "1. Download", "GeoPackage", "nodes · edges · arcs · boundary",
               "2. Inspect", "HTML report", "3. Shortest path", "Route", "4. Isochrones",
               "Reachable areas"],
        "tools_k": "Map tools", "tools_h": "Click on the map, keep pan and zoom free",
        "tools_intro": "Both tools open a side panel that never covers the map. A click "
                       "picks a point, dragging pans, the wheel zooms, right click or "
                       "<code>Esc</code> clears. The road network GeoPackage is taken from the "
                       "layers already open in the project.",
        "route_h": "Route on the map",
        "route_p": "First click = <b style='color:#1a9641'>origin</b>, second click = "
                   "<b style='color:#d62728'>destination</b>; the route is calculated at "
                   "once in the background. <b>Swap</b> reverses it; a third click starts "
                   "a new origin. The clicks are kept in the <i>Route points</i> layer.",
        "route_cap": "The route panel next to the map: distance and time appear in the panel.",
        "iso_h": "Isochrones on the map",
        "iso_p": "Every click adds a point (P1, P2…) to the <i>Isochrone points</i> layer and "
                 "the isochrones are recalculated — untick <i>Calculate after each click</i> "
                 "to add several points first. The panel lists the area of every time band.",
        "iso_cap": "The isochrone panel: times, direction, method and the area of each band.",
        "tools_tip": "Previous results are replaced on each run; tick <b>Keep previous "
                     "results</b> to compare scenarios side by side.",
        "alg_k": "Reference", "alg_h": "The four Processing algorithms",
        "alg_intro": "They work in the dialog, in <i>Run as Batch Process</i>, in the "
                     "Graphical Modeler and from Python.",
        "param": "Parameter", "desc": "Description", "outputs": "Outputs",
        "algs": [
            ("1. Download road network (OSM)", "osmnx_routing:download_network", "icon",
             "var(--green)",
             "Geocodes a place with Nominatim, downloads its streets from Overpass and writes "
             "a GeoPackage. Uses the proxy configured in QGIS.",
             [("Place name", "Municipality, district or neighbourhood with state and country, "
                             "e.g. <i>Campina Grande, Paraíba, Brazil</i>."),
              ("Network type", "<code>all</code>, <code>all_public</code>, <code>drive</code>, "
                               "<code>drive_service</code>, <code>walk</code> or "
                               "<code>bike</code>."),
              ("Output GeoPackage", "File to write. A temporary output is deleted when QGIS "
                                    "closes — the log warns about it.")],
             "Layers <code>edges</code> (display), <code>arcs</code> (one feature per "
             "direction of travel), <code>nodes</code> and <code>boundary</code>, with "
             "<code>speed_kph</code> and <code>travel_time</code>."),
            ("2. Inspect road network GeoPackage", "osmnx_routing:inspect_network", "icon",
             "var(--blue)",
             "HTML report of every layer: CRS, geometry, extent, fields with % filled, a "
             "data sample and a routing diagnosis. Needs QGIS only.",
             [("Road network GeoPackage", "Any GeoPackage; layers may carry a prefix "
                                          "(<code>patos_nodes</code>…)."),
              ("Report", "HTML file to write.")],
             "An HTML report that opens in the browser."),
            ("3. Shortest path (one-way aware)", "osmnx_routing:shortest_path", "route",
             "var(--red)",
             "Route between two points on the directed graph (car) or ignoring direction "
             "(pedestrian).",
             [("Profile", "Car — respects one-way streets / Pedestrian — ignores direction."),
              ("Criterion", "Shortest distance or fastest (car; uses <code>travel_time</code>)."),
              ("Origin, Destination", "Points in any CRS; they snap to the nearest node of "
                                      "the largest connected component."),
              ("Ignore one-way streets", "Comparison: allows driving the wrong way and flags "
                                         "those segments."),
              ("Walking speed", "km/h, default 4.8.")],
             "<b>Route</b> lines with order, street name, road type, one-way, "
             "<code>wrong_way</code>, length, speed, time and cumulative values; <b>Route "
             "points</b>; numbers DISTANCE_KM, TIME_MIN, WRONG_WAY_M."),
            ("4. Isochrones (reachable areas)", "osmnx_routing:isochrones", "isochrones",
             "var(--orange)",
             "Polygons of the areas reachable within each time from a clicked point and/or a "
             "point layer.",
             [("Point / Point layer", "A clicked point, a layer (schools, clinics…) or both; "
                                      "the ID field names each point."),
              ("One isochrone per point", "Unchecked = one combined coverage (the nearest "
                                          "point counts)."),
              ("Direction (car)", "<i>From</i> the points (where you can get to) or "
                                  "<i>to</i> them (where they can be reached from)."),
              ("Times in minutes", "e.g. <code>5, 10, 15</code> (also <code>5;10;15</code>)."),
              ("Polygon method", "Band around the reached roads (faithful) or concave hull "
                                 "(smoother)."),
              ("Band width", "Metres around the roads, default 40.")],
             "<b>Isochrones</b> (source, minutes, area_km2, roads_km), <b>Reached roads</b> "
             "with start/end arrival time, <b>Isochrone points</b>."),
        ],
        "dir_k": "Why direction matters", "dir_h": "One-way streets change the route",
        "dir_intro": "Most routing on undirected graphs happily drives against traffic. The "
                     "plugin keeps a directed <code>arcs</code> layer so cars only use streets "
                     "in the allowed direction.",
        "arcs": ["two-way street", "2 arcs", "one-way street", "1 arc"],
        "legend": ["route", "wrong way", "origin", "destination"],
        "dir_side": "Each arc is one direction of travel. The car graph only has arcs where traffic "
                    "may go; the comparison mode adds the missing reverse arcs and flags them as "
                    "<code>wrong_way</code>.",
        "oneway_left": "<b>Car, one-way respected</b> — the real route is longer.",
        "oneway_right": "<b>Ignoring one-way streets</b> — shorter, but the dashed black "
                        "segment is driven the wrong way.",
        "iso_k": "Isochrones", "iso_gh": "See who is within reach",
        "iso_gintro": "From one point or hundreds: school catchments, clinic coverage, "
                      "delivery areas.",
        "cov_cap": "Walking isochrones (5, 10, 15 min) of four schools, one per point.",
        "meth_left": "<b>Band around the reached roads</b> — follows the network; the last "
                     "segment is cut in proportion to the remaining time.",
        "meth_right": "<b>Concave hull</b> — smoother shapes for presentations.",
        "roads_cap": "<b>Reached roads</b>: arrival time on foot on every street segment.",
        "near": "near", "far": "far",
        "py_k": "Automation", "py_h": "Batch runs, models and Python",
        "py_intro": "Every algorithm has a stable id; run it from the Python console or "
                    "your scripts.",
        "faq_k": "Help", "faq_h": "Troubleshooting",
        "faq": [
            ("The algorithms are disabled / “Missing Python libraries”",
             "OSMnx is not installed in QGIS's Python. Use the command of the Install section "
             "and restart QGIS."),
            ("“No result for …” or “no boundary polygon”",
             "Write the place as in OpenStreetMap with state and country. Points of interest "
             "or streets have no boundary: use a municipality, district or neighbourhood."),
            ("Download takes long or times out",
             "Big cities take minutes. If the server is busy (timeout / refused), wait a few "
             "minutes or try a smaller place. Check the proxy in Settings → Options → "
             "Network."),
            ("“… km from the road network”",
             "The point is outside the downloaded area (more than 5 km from any street). "
             "Click inside the town or download a larger place."),
            ("I saved the layers into another GeoPackage",
             "That works: prefixed names (<code>patos_nodes</code>…) are recognised and "
             "lon/lat layers that lost their CRS are taken as EPSG:4326. Keep one network per "
             "GeoPackage."),
            ("Where do speeds come from?",
             "From OSM <code>maxspeed</code> when present, otherwise from a default per road "
             "type (e.g. residential 30 km/h, primary 60 km/h)."),
        ],
        "limits_h": "Good to know",
        "limits": "Turn restrictions, traffic lights and live traffic are not modelled. The "
                  "network is read once per QGIS session and cached. Routes snap to the "
                  "largest strongly connected component, so a click on an isolated cul-de-sac "
                  "still gives a route.",
        "footer_data": "Map data © OpenStreetMap contributors (ODbL). Figures made with the "
                       "plugin in Cabedelo, Paraíba, Brazil.",
        "footer_license": "Plugin licensed under GPL-2.0-or-later.",
    },
    # ------------------------------------------------------------------ Português
    "pt-br": {
        "title": "OSMnx Routing & Isochrones — plugin para QGIS",
        "description": "Baixe malhas viárias do OpenStreetMap e calcule rotas que respeitam a "
                       "mão das ruas e isócronas localmente no QGIS, sem serviço web nem chave "
                       "de API.",
        "copy": "Copiar",
        "nav": ["Recursos", "Instalação", "Primeiros passos", "Ferramentas", "Algoritmos",
                "Isócronas", "Dúvidas"],
        "hero_h1": "Rotas e isócronas do OpenStreetMap, dentro do QGIS",
        "hero_lead": "Baixe a malha viária de qualquer cidade uma vez e calcule rotas que "
                     "respeitam a mão das ruas e áreas de alcance no seu computador — sem "
                     "serviço de roteamento, sem chave de API, sem limites.",
        "hero_badges": ["QGIS 3.28+", "Algoritmos de Processamento", "Interface PT-BR · EN",
                        "GPL-2.0"],
        "hero_install": "Instalar o plugin", "hero_github": "Código no GitHub",
        "hero_alt": "Isócronas de carro de 1, 2, 3 e 4 minutos em Cabedelo (PB)",
        "feat_k": "Por que usar", "feat_h": "Tudo roda localmente, em ruas de verdade",
        "feat_intro": "O plugin reúne OSMnx e NetworkX em quatro algoritmos de Processamento e "
                      "duas ferramentas interativas no mapa.",
        "features": [
            ("🗺️", "t-green", "Sua própria malha",
             "Um clique transforma o nome de um lugar num GeoPackage com nós, trechos, arcos "
             "dirigidos e o limite."),
            ("↪️", "t-red", "Mão e contramão",
             "O carro segue o sentido do trânsito. Um modo de comparação mostra os trechos que "
             "um grafo não dirigido percorreria na contramão."),
            ("⏱️", "t-orange", "Isócronas",
             "Áreas alcançáveis em 5, 10, 15… minutos saindo dos pontos (ou chegando a eles), "
             "com o tempo de chegada em cada via."),
            ("🖱️", "t-blue", "Clique no mapa",
             "Painéis laterais deixam o mapa livre: clique os pontos, mova, dê zoom e veja o "
             "resultado na hora."),
        ],
        "inst_k": "Instalação", "inst_h": "Dois passos, sem permissão de administrador",
        "inst_intro": "O QGIS já traz geopandas, networkx, shapely e pyproj; só falta "
                      "acrescentar o OSMnx ao Python do QGIS.",
        "inst_steps": [
            ("Instale o OSMnx no Python do QGIS",
             "Abra <b>Complementos → Console Python</b>, cole o código abaixo e tecle Enter. "
             "Depois reinicie o QGIS."),
            ("Instale o plugin",
             "<b>Complementos → Gerenciar e instalar complementos</b>, procure por <b>OSMnx "
             "Routing &amp; Isochrones</b>. Enquanto for experimental, marque <i>Mostrar "
             "também os complementos experimentais</i> nas Configurações. Também dá para usar "
             "<i>Instalar a partir do ZIP</i> com um arquivo das <a href='" + REPO +
             "/releases'>releases</a>."),
        ],
        "inst_note": "Se um erro de importação citar outro pacote ausente (QGIS antigo no "
                     "Linux), rode o mesmo comando sem <code>--no-deps</code>. Enquanto faltar "
                     "alguma biblioteca, o plugin mostra um aviso com o botão <b>Como "
                     "instalar</b> e os algoritmos ficam desativados.",
        "qs_k": "Primeiros passos", "qs_h": "Do nome de um lugar ao mapa em quatro passos",
        "qs_intro": "Baixe a malha uma vez; todas as outras ferramentas leem o GeoPackage.",
        "qs_steps": [
            ("Baixe a malha viária",
             "Caixa de Ferramentas de Processamento (<code>Ctrl+Alt+T</code>) → <b>OSMnx "
             "Routing &amp; Isochrones → 1. Baixar malha viária</b>. Digite, por exemplo, "
             "<i>Cabedelo, Paraíba, Brasil</i>, escolha <i>drive</i> e um arquivo de saída."),
            ("Confira o que veio (opcional)",
             "<b>2. Inspecionar GeoPackage da malha</b> gera um relatório HTML: SRC, campos, "
             "preenchimento e um diagnóstico de roteamento."),
            ("Clique uma rota",
             "Botão <b>Rota no mapa</b> na barra: clique a origem e depois o destino."),
            ("Clique isócronas",
             "Botão <b>Isócronas no mapa</b>: cada clique acrescenta um ponto e as áreas são "
             "recalculadas."),
        ],
        "wf": ["Nome do lugar", "1. Baixar", "GeoPackage", "nós · trechos · arcos · limite",
               "2. Inspecionar", "Relatório HTML", "3. Menor caminho", "Rota",
               "4. Isócronas", "Áreas de alcance"],
        "tools_k": "Ferramentas no mapa", "tools_h": "Clique no mapa com pan e zoom livres",
        "tools_intro": "As duas ferramentas abrem um painel lateral que nunca cobre o mapa. "
                       "Clique marca um ponto, arrastar move o mapa, a roda do mouse dá zoom, "
                       "botão direito ou <code>Esc</code> limpa. O GeoPackage da malha vem das "
                       "camadas já abertas no projeto.",
        "route_h": "Rota no mapa",
        "route_p": "Primeiro clique = <b style='color:#1a9641'>origem</b>, segundo = "
                   "<b style='color:#d62728'>destino</b>; a rota é calculada na hora, em "
                   "segundo plano. <b>Inverter</b> troca o sentido; um terceiro clique "
                   "começa nova origem. Os cliques ficam na camada <i>Pontos da rota</i>.",
        "route_cap": "O painel de rota ao lado do mapa: distância e tempo aparecem no painel.",
        "iso_h": "Isócronas no mapa",
        "iso_p": "Cada clique acrescenta um ponto (P1, P2…) à camada <i>Pontos das "
                 "isócronas</i> e as isócronas são recalculadas — desmarque <i>Calcular após "
                 "cada clique</i> para marcar vários pontos antes. O painel lista a área de "
                 "cada faixa de tempo.",
        "iso_cap": "O painel de isócronas: tempos, sentido, método e a área de cada faixa.",
        "tools_tip": "A cada execução o resultado anterior é substituído; marque <b>Manter "
                     "resultados anteriores</b> para comparar cenários lado a lado.",
        "alg_k": "Referência", "alg_h": "Os quatro algoritmos de Processamento",
        "alg_intro": "Funcionam no diálogo, em <i>Executar como processo em lote</i>, no "
                     "Modelador Gráfico e pelo Python.",
        "param": "Parâmetro", "desc": "Descrição", "outputs": "Saídas",
        "algs": [
            ("1. Baixar malha viária (OSM)", "osmnx_routing:download_network", "icon",
             "var(--green)",
             "Geocodifica o lugar no Nominatim, baixa as ruas do Overpass e grava um "
             "GeoPackage. Usa o proxy configurado no QGIS.",
             [("Nome do lugar", "Município, distrito ou bairro com estado e país, ex.: "
                                "<i>Campina Grande, Paraíba, Brasil</i>."),
              ("Tipo de rede", "<code>all</code>, <code>all_public</code>, <code>drive</code>, "
                               "<code>drive_service</code>, <code>walk</code> ou "
                               "<code>bike</code>."),
              ("GeoPackage de saída", "Arquivo a gravar. Uma saída temporária é apagada ao "
                                      "fechar o QGIS — o log avisa.")],
             "Camadas <code>edges</code> (exibição), <code>arcs</code> (um registro por "
             "sentido de circulação), <code>nodes</code> e <code>boundary</code>, com "
             "<code>speed_kph</code> e <code>travel_time</code>."),
            ("2. Inspecionar GeoPackage da malha", "osmnx_routing:inspect_network", "icon",
             "var(--blue)",
             "Relatório HTML de cada camada: SRC, geometria, extensão, campos com % "
             "preenchido, amostra e diagnóstico de roteamento. Só precisa do QGIS.",
             [("GeoPackage da malha", "Qualquer GeoPackage; as camadas podem ter prefixo "
                                      "(<code>patos_nodes</code>…)."),
              ("Relatório", "Arquivo HTML a gravar.")],
             "Um relatório HTML que abre no navegador."),
            ("3. Menor caminho (mão e contramão)", "osmnx_routing:shortest_path", "route",
             "var(--red)",
             "Rota entre dois pontos no grafo dirigido (carro) ou ignorando o sentido "
             "(pedestre).",
             [("Perfil", "Carro — respeita mão e contramão / Pedestre — ignora o sentido."),
              ("Critério", "Menor distância ou mais rápido (carro; usa "
                           "<code>travel_time</code>)."),
              ("Origem, Destino", "Pontos em qualquer SRC; ajustam-se ao nó mais próximo do "
                                  "maior componente conexo."),
              ("Ignorar mão única", "Comparação: permite a contramão e marca esses trechos."),
              ("Velocidade a pé", "km/h, padrão 4,8.")],
             "Linhas da <b>Rota</b> com ordem, nome da rua, tipo de via, mão única, "
             "<code>wrong_way</code>, comprimento, velocidade, tempo e acumulados; <b>Pontos "
             "da rota</b>; números DISTANCE_KM, TIME_MIN, WRONG_WAY_M."),
            ("4. Isócronas (áreas de alcance)", "osmnx_routing:isochrones", "isochrones",
             "var(--orange)",
             "Polígonos das áreas alcançáveis em cada tempo a partir de um ponto clicado e/ou "
             "de uma camada de pontos.",
             [("Ponto / Camada de pontos", "Um ponto clicado, uma camada (escolas, UBS…) ou "
                                           "ambos; o campo de nome identifica cada ponto."),
              ("Uma isócrona por ponto", "Desmarcado = uma cobertura combinada (vale o ponto "
                                         "mais próximo)."),
              ("Sentido (carro)", "<i>Saindo</i> dos pontos (até onde se chega) ou "
                                  "<i>chegando</i> a eles (de onde se chega)."),
              ("Tempos em minutos", "ex.: <code>5, 10, 15</code> (também "
                                    "<code>5;10;15</code>)."),
              ("Método do polígono", "Faixa ao redor das vias alcançadas (fiel) ou envoltória "
                                     "côncava (mais suave)."),
              ("Largura da faixa", "Metros ao redor das vias, padrão 40.")],
             "<b>Isócronas</b> (source, minutes, area_km2, roads_km), <b>Vias alcançadas</b> "
             "com tempo de chegada inicial/final, <b>Pontos das isócronas</b>."),
        ],
        "dir_k": "Por que o sentido importa", "dir_h": "A mão das ruas muda a rota",
        "dir_intro": "Roteamento em grafo não dirigido costuma andar na contramão sem "
                     "perceber. O plugin guarda a camada dirigida <code>arcs</code>, e o carro "
                     "só usa as ruas no sentido permitido.",
        "arcs": ["rua de mão dupla", "2 arcos", "rua de mão única", "1 arco"],
        "legend": ["rota", "contramão", "origem", "destino"],
        "dir_side": "Cada arco é um sentido de circulação. O grafo do carro só tem arcos onde o "
                    "trânsito pode passar; o modo de comparação acrescenta os arcos inversos que "
                    "faltam e os marca como <code>wrong_way</code>.",
        "oneway_left": "<b>Carro, respeitando a mão</b> — a rota real é mais longa.",
        "oneway_right": "<b>Ignorando a mão única</b> — mais curta, mas o trecho tracejado "
                        "preto é feito na contramão.",
        "iso_k": "Isócronas", "iso_gh": "Veja quem está ao alcance",
        "iso_gintro": "De um ponto ou de centenas: área de influência de escolas, cobertura "
                      "de unidades de saúde, áreas de entrega.",
        "cov_cap": "Isócronas a pé (5, 10, 15 min) de quatro escolas, uma por ponto.",
        "meth_left": "<b>Faixa ao redor das vias alcançadas</b> — segue a malha; o último "
                     "trecho é cortado em proporção ao tempo restante.",
        "meth_right": "<b>Envoltória côncava</b> — formas mais suaves para apresentações.",
        "roads_cap": "<b>Vias alcançadas</b>: tempo de chegada a pé em cada trecho de rua.",
        "near": "perto", "far": "longe",
        "py_k": "Automação", "py_h": "Lotes, modelos e Python",
        "py_intro": "Cada algoritmo tem um id estável; rode pelo Console Python ou pelos seus "
                    "scripts.",
        "faq_k": "Ajuda", "faq_h": "Dúvidas e problemas comuns",
        "faq": [
            ("Os algoritmos estão desativados / “Bibliotecas Python ausentes”",
             "O OSMnx não está instalado no Python do QGIS. Use o comando da seção "
             "Instalação e reinicie o QGIS."),
            ("“Nenhum resultado para …” ou “sem polígono de limite”",
             "Escreva o lugar como no OpenStreetMap, com estado e país. Pontos de interesse e "
             "ruas não têm limite: use município, distrito ou bairro."),
            ("O download demora ou dá tempo esgotado",
             "Cidades grandes levam minutos. Se o servidor estiver ocupado (tempo esgotado / "
             "recusado), aguarde alguns minutos ou tente um lugar menor. Confira o proxy em "
             "Configurações → Opções → Rede."),
            ("“… km da malha viária”",
             "O ponto está fora da área baixada (a mais de 5 km de qualquer rua). Clique "
             "dentro da cidade ou baixe um lugar maior."),
            ("Salvei as camadas em outro GeoPackage",
             "Funciona: nomes com prefixo (<code>patos_nodes</code>…) são reconhecidos e "
             "camadas lon/lat que perderam o SRC são tratadas como EPSG:4326. Mantenha uma "
             "malha por GeoPackage."),
            ("De onde vêm as velocidades?",
             "Do <code>maxspeed</code> do OSM quando existe; senão, de um padrão por tipo de "
             "via (ex.: residencial 30 km/h, primária 60 km/h)."),
        ],
        "limits_h": "Bom saber",
        "limits": "Restrições de conversão, semáforos e trânsito em tempo real não são "
                  "modelados. A malha é lida uma vez por sessão do QGIS e fica em cache. As "
                  "rotas se ajustam ao maior componente fortemente conexo, então um clique "
                  "numa rua sem saída isolada ainda gera rota.",
        "footer_data": "Dados © colaboradores do OpenStreetMap (ODbL). Figuras feitas com o "
                       "plugin em Cabedelo, Paraíba, Brasil.",
        "footer_license": "Plugin sob licença GPL-2.0-or-later.",
    },
    # ------------------------------------------------------------------ Español
    "es": {
        "title": "OSMnx Routing & Isochrones — complemento de QGIS",
        "description": "Descarga redes viales de OpenStreetMap y calcula rutas que respetan "
                       "el sentido de las calles e isócronas localmente en QGIS, sin servicio "
                       "web ni clave de API.",
        "copy": "Copiar",
        "nav": ["Funciones", "Instalación", "Inicio rápido", "Herramientas", "Algoritmos",
                "Isócronas", "Ayuda"],
        "hero_h1": "Rutas e isócronas de OpenStreetMap, dentro de QGIS",
        "hero_lead": "Descarga una vez la red de calles de cualquier ciudad y calcula rutas "
                     "que respetan el sentido de circulación y áreas de alcance en tu propio "
                     "equipo — sin servicio de ruteo, sin clave de API, sin límites.",
        "hero_badges": ["QGIS 3.28+", "Algoritmos de Procesos", "Interfaz EN · PT-BR",
                        "GPL-2.0"],
        "hero_install": "Instalar el complemento", "hero_github": "Código en GitHub",
        "hero_alt": "Isócronas en auto de 1, 2, 3 y 4 minutos en Cabedelo, Brasil",
        "feat_k": "Por qué usarlo", "feat_h": "Todo se ejecuta localmente, en calles reales",
        "feat_intro": "El complemento reúne OSMnx y NetworkX en cuatro algoritmos de Procesos "
                      "y dos herramientas interactivas en el mapa.",
        "features": [
            ("🗺️", "t-green", "Tu propia red",
             "Un clic convierte el nombre de un lugar en un GeoPackage con nodos, tramos, "
             "arcos dirigidos y el límite."),
            ("↪️", "t-red", "Respeta el sentido",
             "El auto sigue el sentido del tránsito. Un modo de comparación muestra los tramos "
             "que un grafo no dirigido recorrería a contramano."),
            ("⏱️", "t-orange", "Isócronas",
             "Áreas alcanzables en 5, 10, 15… minutos desde los puntos (o hacia ellos), con el "
             "tiempo de llegada en cada calle."),
            ("🖱️", "t-blue", "Clic en el mapa",
             "Paneles laterales dejan el mapa libre: marca puntos, desplaza, haz zoom y mira el "
             "resultado al instante."),
        ],
        "inst_k": "Instalación", "inst_h": "Dos pasos, sin permisos de administrador",
        "inst_intro": "QGIS ya incluye geopandas, networkx, shapely y pyproj; solo hay que "
                      "añadir OSMnx al Python de QGIS.",
        "inst_steps": [
            ("Instala OSMnx en el Python de QGIS",
             "Abre <b>Complementos → Consola de Python</b>, pega el código y pulsa Enter. "
             "Luego reinicia QGIS."),
            ("Instala el complemento",
             "<b>Complementos → Administrar e instalar complementos</b>, busca <b>OSMnx "
             "Routing &amp; Isochrones</b>. Mientras sea experimental, marca <i>Mostrar también "
             "complementos experimentales</i> en Configuración. También puedes usar "
             "<i>Instalar a partir de ZIP</i> con un archivo de las <a href='" + REPO +
             "/releases'>releases</a>."),
        ],
        "inst_note": "Si un error de importación menciona otro paquete faltante (QGIS antiguo "
                     "en Linux), ejecuta el mismo comando sin <code>--no-deps</code>. Mientras "
                     "falte una biblioteca, el complemento muestra un aviso con el botón "
                     "<b>How to install</b> y sus algoritmos quedan desactivados.",
        "qs_k": "Inicio rápido", "qs_h": "Del nombre de un lugar al mapa en cuatro pasos",
        "qs_intro": "Descarga la red una vez; todas las demás herramientas leen el GeoPackage.",
        "qs_steps": [
            ("Descarga la red vial",
             "Caja de herramientas de Procesos (<code>Ctrl+Alt+T</code>) → <b>OSMnx Routing "
             "&amp; Isochrones → 1. Download road network</b>. Escribe, por ejemplo, "
             "<i>Cabedelo, Paraíba, Brasil</i>, elige <i>drive</i> y un archivo de salida."),
            ("Revisa lo descargado (opcional)",
             "<b>2. Inspect road network GeoPackage</b> genera un informe HTML: SRC, campos, "
             "completitud y un diagnóstico de ruteo."),
            ("Marca una ruta",
             "Botón <b>Route on the map</b> de la barra: clic en el origen y luego en el "
             "destino."),
            ("Marca isócronas",
             "Botón <b>Isochrones on the map</b>: cada clic agrega un punto y las áreas se "
             "recalculan."),
        ],
        "wf": ["Nombre del lugar", "1. Descargar", "GeoPackage", "nodos · tramos · arcos · límite",
               "2. Inspeccionar", "Informe HTML", "3. Ruta más corta", "Ruta", "4. Isócronas",
               "Áreas de alcance"],
        "tools_k": "Herramientas en el mapa",
        "tools_h": "Clic en el mapa, con desplazamiento y zoom libres",
        "tools_intro": "Ambas herramientas abren un panel lateral que nunca tapa el mapa. Un "
                       "clic marca un punto, arrastrar desplaza, la rueda hace zoom, el botón "
                       "derecho o <code>Esc</code> borra. El GeoPackage de la red se toma de "
                       "las capas ya abiertas en el proyecto. <i>La interfaz del complemento "
                       "está en inglés y portugués; las capturas muestran la versión en "
                       "inglés.</i>",
        "route_h": "Ruta en el mapa",
        "route_p": "Primer clic = <b style='color:#1a9641'>origen</b>, segundo = "
                   "<b style='color:#d62728'>destino</b>; la ruta se calcula al instante en "
                   "segundo plano. <b>Swap</b> invierte el sentido; un tercer clic empieza un "
                   "nuevo origen. Los clics quedan en la capa <i>Route points</i>.",
        "route_cap": "El panel de ruta junto al mapa: distancia y tiempo aparecen en el panel.",
        "iso_h": "Isócronas en el mapa",
        "iso_p": "Cada clic agrega un punto (P1, P2…) a la capa <i>Isochrone points</i> y las "
                 "isócronas se recalculan — desmarca <i>Calculate after each click</i> para "
                 "marcar varios puntos antes. El panel lista el área de cada franja.",
        "iso_cap": "El panel de isócronas: tiempos, sentido, método y el área de cada franja.",
        "tools_tip": "Cada ejecución reemplaza el resultado anterior; marca <b>Keep previous "
                     "results</b> para comparar escenarios.",
        "alg_k": "Referencia", "alg_h": "Los cuatro algoritmos de Procesos",
        "alg_intro": "Funcionan en el diálogo, en <i>Ejecutar como proceso por lotes</i>, en "
                     "el Modelador gráfico y desde Python.",
        "param": "Parámetro", "desc": "Descripción", "outputs": "Salidas",
        "algs": [
            ("1. Download road network (OSM)", "osmnx_routing:download_network", "icon",
             "var(--green)",
             "Geocodifica el lugar con Nominatim, descarga sus calles de Overpass y escribe un "
             "GeoPackage. Usa el proxy configurado en QGIS.",
             [("Place name", "Municipio, distrito o barrio con estado y país, p. ej. "
                             "<i>Campina Grande, Paraíba, Brasil</i>."),
              ("Network type", "<code>all</code>, <code>all_public</code>, <code>drive</code>, "
                               "<code>drive_service</code>, <code>walk</code> o "
                               "<code>bike</code>."),
              ("Output GeoPackage", "Archivo a escribir. Una salida temporal se borra al cerrar "
                                    "QGIS — el registro lo advierte.")],
             "Capas <code>edges</code> (visualización), <code>arcs</code> (un registro por "
             "sentido de circulación), <code>nodes</code> y <code>boundary</code>, con "
             "<code>speed_kph</code> y <code>travel_time</code>."),
            ("2. Inspect road network GeoPackage", "osmnx_routing:inspect_network", "icon",
             "var(--blue)",
             "Informe HTML de cada capa: SRC, geometría, extensión, campos con % completo, "
             "muestra y diagnóstico de ruteo. Solo necesita QGIS.",
             [("Road network GeoPackage", "Cualquier GeoPackage; las capas pueden tener "
                                          "prefijo (<code>patos_nodes</code>…)."),
              ("Report", "Archivo HTML a escribir.")],
             "Un informe HTML que se abre en el navegador."),
            ("3. Shortest path (one-way aware)", "osmnx_routing:shortest_path", "route",
             "var(--red)",
             "Ruta entre dos puntos en el grafo dirigido (auto) o ignorando el sentido "
             "(peatón).",
             [("Profile", "Auto — respeta el sentido / Peatón — ignora el sentido."),
              ("Criterion", "Menor distancia o más rápida (auto; usa "
                            "<code>travel_time</code>)."),
              ("Origin, Destination", "Puntos en cualquier SRC; se ajustan al nodo más cercano "
                                      "del mayor componente conexo."),
              ("Ignore one-way streets", "Comparación: permite ir a contramano y marca esos "
                                         "tramos."),
              ("Walking speed", "km/h, por defecto 4,8.")],
             "Líneas de la <b>Route</b> con orden, nombre de la calle, tipo de vía, sentido "
             "único, <code>wrong_way</code>, longitud, velocidad, tiempo y acumulados; "
             "<b>Route points</b>; números DISTANCE_KM, TIME_MIN, WRONG_WAY_M."),
            ("4. Isochrones (reachable areas)", "osmnx_routing:isochrones", "isochrones",
             "var(--orange)",
             "Polígonos de las áreas alcanzables en cada tiempo desde un punto marcado y/o una "
             "capa de puntos.",
             [("Point / Point layer", "Un punto marcado, una capa (escuelas, centros de "
                                      "salud…) o ambos; el campo de nombre identifica cada "
                                      "punto."),
              ("One isochrone per point", "Desmarcado = una cobertura combinada (cuenta el "
                                          "punto más cercano)."),
              ("Direction (car)", "<i>Desde</i> los puntos (hasta dónde se llega) o "
                                  "<i>hacia</i> ellos (desde dónde se llega)."),
              ("Times in minutes", "p. ej. <code>5, 10, 15</code> (también "
                                   "<code>5;10;15</code>)."),
              ("Polygon method", "Franja alrededor de las calles alcanzadas (fiel) o "
                                 "envolvente cóncava (más suave)."),
              ("Band width", "Metros alrededor de las calles, por defecto 40.")],
             "<b>Isochrones</b> (source, minutes, area_km2, roads_km), <b>Reached roads</b> "
             "con tiempo de llegada inicial/final, <b>Isochrone points</b>."),
        ],
        "dir_k": "Por qué importa el sentido", "dir_h": "El sentido de las calles cambia la ruta",
        "dir_intro": "El ruteo en grafos no dirigidos suele ir a contramano sin avisar. El "
                     "complemento guarda la capa dirigida <code>arcs</code> y el auto solo usa "
                     "las calles en el sentido permitido.",
        "arcs": ["calle doble sentido", "2 arcos", "calle sentido único", "1 arco"],
        "legend": ["ruta", "contramano", "origen", "destino"],
        "dir_side": "Cada arco es un sentido de circulación. El grafo del auto solo tiene arcos donde"
                    " el tránsito puede pasar; el modo de comparación agrega los arcos inversos "
                    "faltantes y los marca como <code>wrong_way</code>.",
        "oneway_left": "<b>Auto, respetando el sentido</b> — la ruta real es más larga.",
        "oneway_right": "<b>Ignorando el sentido único</b> — más corta, pero el tramo negro "
                        "punteado va a contramano.",
        "iso_k": "Isócronas", "iso_gh": "Mira quién está al alcance",
        "iso_gintro": "Desde un punto o cientos: área de influencia de escuelas, cobertura de "
                      "centros de salud, zonas de reparto.",
        "cov_cap": "Isócronas a pie (5, 10, 15 min) de cuatro escuelas, una por punto.",
        "meth_left": "<b>Franja alrededor de las calles alcanzadas</b> — sigue la red; el "
                     "último tramo se corta según el tiempo restante.",
        "meth_right": "<b>Envolvente cóncava</b> — formas más suaves para presentaciones.",
        "roads_cap": "<b>Reached roads</b>: tiempo de llegada a pie en cada tramo de calle.",
        "near": "cerca", "far": "lejos",
        "py_k": "Automatización", "py_h": "Lotes, modelos y Python",
        "py_intro": "Cada algoritmo tiene un id estable; ejecútalo desde la consola de Python "
                    "o tus scripts.",
        "faq_k": "Ayuda", "faq_h": "Solución de problemas",
        "faq": [
            ("Los algoritmos están desactivados / “Missing Python libraries”",
             "OSMnx no está instalado en el Python de QGIS. Usa el comando de la sección "
             "Instalación y reinicia QGIS."),
            ("“No result for …” o “no boundary polygon”",
             "Escribe el lugar como en OpenStreetMap, con estado y país. Los puntos de interés "
             "y las calles no tienen límite: usa un municipio, distrito o barrio."),
            ("La descarga tarda o se agota el tiempo",
             "Las ciudades grandes tardan minutos. Si el servidor está ocupado (tiempo agotado "
             "/ rechazado), espera unos minutos o prueba un lugar más pequeño. Revisa el proxy "
             "en Configuración → Opciones → Red."),
            ("“… km from the road network”",
             "El punto está fuera del área descargada (a más de 5 km de cualquier calle). "
             "Marca dentro de la ciudad o descarga un lugar más grande."),
            ("Guardé las capas en otro GeoPackage",
             "Funciona: los nombres con prefijo (<code>patos_nodes</code>…) se reconocen y las "
             "capas lon/lat que perdieron el SRC se toman como EPSG:4326. Mantén una red por "
             "GeoPackage."),
            ("¿De dónde salen las velocidades?",
             "Del <code>maxspeed</code> de OSM cuando existe; si no, de un valor por tipo de "
             "vía (p. ej. residencial 30 km/h, primaria 60 km/h)."),
        ],
        "limits_h": "Para tener en cuenta",
        "limits": "No se modelan restricciones de giro, semáforos ni tránsito en tiempo real. "
                  "La red se lee una vez por sesión de QGIS y queda en caché. Las rutas se "
                  "ajustan al mayor componente fuertemente conexo, así que un clic en un "
                  "callejón aislado igual da una ruta.",
        "footer_data": "Datos © colaboradores de OpenStreetMap (ODbL). Figuras hechas con el "
                       "complemento en Cabedelo, Paraíba, Brasil.",
        "footer_license": "Complemento con licencia GPL-2.0-or-later.",
    },
}
SECTION_IDS = ["features", "install", "quick-start", "map-tools", "algorithms",
               "isochrones", "faq"]


def code(text):
    return f"<pre><code>{html.escape(text)}</code></pre>"


def workflow_svg(w):
    """Download -> GeoPackage -> inspect / route / isochrones."""
    def box(x, y, wd, title, sub, fill, stroke):
        return (f'<rect x="{x}" y="{y}" width="{wd}" height="64" rx="12" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="2"/>'
                f'<text x="{x + wd / 2}" y="{y + 28}" text-anchor="middle" font-weight="700" '
                f'font-size="15">{html.escape(title)}</text>'
                f'<text x="{x + wd / 2}" y="{y + 48}" text-anchor="middle" font-size="12" '
                f'opacity=".75">{html.escape(sub)}</text>')

    def arrow(x1, y1, x2, y2, color):
        return (f'<path d="M{x1} {y1} C{(x1 + x2) / 2} {y1} {(x1 + x2) / 2} {y2} {x2} {y2}" '
                f'fill="none" stroke="{color}" stroke-width="3" marker-end="url(#ah)"/>')
    parts = ['<svg viewBox="0 0 980 250" role="img" aria-label="workflow">'
             '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
             'markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#888"/></marker>'
             '</defs>',
             box(10, 93, 150, w[0], "", "#fff7e6", "#f2b134"),
             arrow(160, 125, 200, 125, "#888"),
             box(200, 93, 150, w[1], "Nominatim + Overpass", "#e3f4e6", "#1a9641"),
             arrow(350, 125, 390, 125, "#888"),
             box(390, 93, 220, w[2], w[3], "#ffffff", "#5b636d")]
    for i, (y, title, sub, fill, stroke) in enumerate((
            (13, w[4], w[5], "#e4f0f8", "#2b83ba"),
            (93, w[6], w[7], "#fde8e8", "#d62728"),
            (173, w[8], w[9], "#fdf0e1", "#f28e2b"))):
        parts.append(arrow(610, 125, 680, y + 32, stroke))
        parts.append(box(680, y, 290, title, sub, fill, stroke))
    parts.append("</svg>")
    return "".join(parts)


def arcs_svg(a):
    """Two-way street = 2 arcs; one-way street = 1 arc."""
    def street(y, label, n, arcs):
        s = (f'<line x1="40" y1="{y}" x2="300" y2="{y}" stroke="#b9b4aa" stroke-width="16" '
             f'stroke-linecap="round"/>'
             f'<circle cx="40" cy="{y}" r="9" fill="#fff" stroke="#333" stroke-width="2"/>'
             f'<circle cx="300" cy="{y}" r="9" fill="#fff" stroke="#333" stroke-width="2"/>'
             f'<text x="170" y="{y - 30}" text-anchor="middle" font-weight="700" '
             f'font-size="15">{html.escape(label)}</text>')
        for dy, d, color in arcs:
            x1, x2 = (70, 270) if d > 0 else (270, 70)
            s += (f'<line x1="{x1}" y1="{y + dy}" x2="{x2}" y2="{y + dy}" stroke="{color}" '
                  f'stroke-width="4" marker-end="url(#a{color[1:]})"/>')
        s += (f'<text x="340" y="{y + 5}" font-size="15" font-weight="700" '
              f'fill="{arcs[0][2]}">{html.escape(n)}</text>')
        return s
    return ('<svg viewBox="0 0 440 230" role="img" aria-label="arcs">'
            '<defs>' + "".join(
                f'<marker id="a{c}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" '
                f'markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="#{c}"/>'
                '</marker>' for c in ("1a9641", "d62728")) + '</defs>' +
            street(70, a[0], a[1], [(-20, 1, "#1a9641"), (20, -1, "#1a9641")]) +
            street(180, a[2], a[3], [(-20, 1, "#d62728")]) + "</svg>")


def page(lang):
    t = TEXTS[lang]
    shot = PANEL_SHOTS[lang]
    img = "../assets/img"
    nav = "".join(f'<a href="#{i}">{html.escape(n)}</a>' for i, n in zip(SECTION_IDS, t["nav"]))
    langs = "".join(
        f'<a href="../{code_}/" data-lang="{code_}" class="{"on" if code_ == lang else ""}" '
        f'hreflang="{code_}" title="{name}">{short}</a>' for code_, name, short in LANGS)
    alternates = "".join(f'<link rel="alternate" hreflang="{c}" href="../{c}/">'
                         for c, _, _ in LANGS)
    features = "".join(
        f'<div class="card"><div class="ico {tone}">{ico}</div><h4>{h}</h4><p>{p}</p></div>'
        for ico, tone, h, p in t["features"])

    def steps(items, extra=None):
        out = "".join(
            f"<li><h4>{h}</h4><p>{p}</p>{(extra or {}).get(i, '')}</li>"
            for i, (h, p) in enumerate(items))
        return f'<ol class="steps">{out}</ol>'

    algs = ""
    for name, alg_id, icon_name, color, text, params, outputs in t["algs"]:
        rows = "".join(f"<tr><td><b>{p}</b></td><td>{d}</td></tr>" for p, d in params)
        algs += (f'<div class="alg" style="--c:{color}"><h3><img src="../assets/{icon_name}.svg" '
                 f'alt="">{html.escape(name)}</h3><p class="id"><code>{alg_id}</code></p>'
                 f'<p>{text}</p><div class="table"><table><tr><th>{t["param"]}</th>'
                 f'<th>{t["desc"]}</th></tr>{rows}</table></div>'
                 f'<p><b>{t["outputs"]}:</b> {outputs}</p></div>')
    faq = "".join(f"<details><summary>{q}</summary><div>{a}</div></details>"
                  for q, a in t["faq"])
    iso_legend = (f'<span class="legend">{t["near"]} <span class="ramp iso"></span> '
                  f'{t["far"]}</span>')
    lg = t["legend"]
    legend = (f'<span class="legend"><span class="sw line" style="background:#d62728"></span>'
              f'{lg[0]}</span><span class="legend"><span class="sw dash"></span>{lg[1]}</span>'
              f'<span class="legend"><span class="sw dot" style="background:#1a9641"></span>'
              f'{lg[2]}</span><span class="legend"><span class="sw dot" '
              f'style="background:#d62728"></span>{lg[3]}</span>')
    roads_legend = (f'<span class="legend">{t["near"]} <span class="ramp roads"></span> '
                    f'{t["far"]}</span>')

    return f"""<!doctype html>
<html lang="{lang}" data-copy="{t['copy']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(t['title'])}</title>
<meta name="description" content="{html.escape(t['description'])}">
<meta property="og:title" content="{html.escape(t['title'])}">
<meta property="og:description" content="{html.escape(t['description'])}">
<meta property="og:image" content="{img}/hero.png">
{alternates}
<link rel="icon" href="../assets/icon.svg">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<header class="topbar"><div class="wrap">
  <a class="brand" href="#top"><img src="../assets/icon.svg" alt="">OSMnx Routing &amp; Isochrones</a>
  <nav class="topnav">{nav}</nav>
  <div class="lang">{langs}</div>
</div></header>

<div class="hero" id="top"><div class="wrap">
  <div>
    <div class="badges">{"".join(f"<span>{b}</span>" for b in t["hero_badges"])}</div>
    <h1>{t['hero_h1']}</h1>
    <p class="lead">{t['hero_lead']}</p>
    <a class="btn primary" href="#install">⬇ {t['hero_install']}</a>
    <a class="btn ghost" href="{REPO}">★ {t['hero_github']}</a>
  </div>
  <figure><img src="{img}/hero.png" alt="{html.escape(t['hero_alt'])}" width="1200" height="900"></figure>
</div></div>

<section id="features"><div class="wrap">
  <p class="kicker k-green">{t['feat_k']}</p><h2>{t['feat_h']}</h2>
  <p class="intro">{t['feat_intro']}</p>
  <div class="grid c4">{features}</div>
</div></section>

<section id="install"><div class="wrap">
  <p class="kicker k-orange">{t['inst_k']}</p><h2>{t['inst_h']}</h2>
  <p class="intro">{t['inst_intro']}</p>
  {steps(t['inst_steps'], {0: code(INSTALL_CODE)})}
  <div class="note warn">{t['inst_note']}</div>
</div></section>

<section id="quick-start"><div class="wrap">
  <p class="kicker k-blue">{t['qs_k']}</p><h2>{t['qs_h']}</h2>
  <p class="intro">{t['qs_intro']}</p>
  <div class="diagram" style="margin-bottom:22px">{workflow_svg(t['wf'])}</div>
  {steps(t['qs_steps'])}
</div></section>

<section id="map-tools"><div class="wrap">
  <p class="kicker k-red">{t['tools_k']}</p><h2>{t['tools_h']}</h2>
  <p class="intro">{t['tools_intro']}</p>
  <h3><img class="inline-ico" src="../assets/route.svg" alt=""> {t['route_h']}</h3>
  <p>{t['route_p']}</p>
  <figure class="shot"><img src="{img}/panel_route_{shot}.png"
    alt="{html.escape(t['route_h'])}" loading="lazy">
    <figcaption>{t['route_cap']}</figcaption></figure>
  <h3><img class="inline-ico" src="../assets/isochrones.svg" alt=""> {t['iso_h']}</h3>
  <p>{t['iso_p']}</p>
  <figure class="shot"><img src="{img}/panel_isochrones_{shot}.png"
    alt="{html.escape(t['iso_h'])}" loading="lazy">
    <figcaption>{t['iso_cap']} {iso_legend}</figcaption></figure>
  <div class="note tip">💡 {t['tools_tip']}</div>
</div></section>

<section id="algorithms"><div class="wrap">
  <p class="kicker k-blue">{t['alg_k']}</p><h2>{t['alg_h']}</h2>
  <p class="intro">{t['alg_intro']}</p>
  {algs}
  <h3>{t['dir_h']}</h3>
  <p>{t['dir_intro']}</p>
  <div class="grid c2" style="align-items:center">
    <div class="diagram">{arcs_svg(t['arcs'])}</div>
    <div><p class="kicker k-red">{t['dir_k']}</p><p>{t['dir_side']}</p>
      <p>{legend}</p></div>
  </div>
  <figure class="shot"><img src="{img}/oneway.png" alt="one-way" loading="lazy">
    <div class="pair"><div>{t['oneway_left']}</div><div>{t['oneway_right']}</div></div></figure>
</div></section>

<section id="isochrones"><div class="wrap">
  <p class="kicker k-orange">{t['iso_k']}</p><h2>{t['iso_gh']}</h2>
  <p class="intro">{t['iso_gintro']}</p>
  <figure class="shot"><img src="{img}/coverage.png" alt="coverage" loading="lazy">
    <figcaption>{t['cov_cap']} {iso_legend}</figcaption></figure>
  <figure class="shot"><img src="{img}/methods.png" alt="methods" loading="lazy">
    <div class="pair"><div>{t['meth_left']}</div><div>{t['meth_right']}</div></div></figure>
  <figure class="shot"><img src="{img}/reached_roads.png" alt="reached roads" loading="lazy">
    <figcaption>{t['roads_cap']} {roads_legend}</figcaption></figure>
  <p class="kicker k-blue" style="margin-top:40px">{t['py_k']}</p><h2>{t['py_h']}</h2>
  <p class="intro">{t['py_intro']}</p>
  {code(PYTHON_CODE)}
</div></section>

<section id="faq"><div class="wrap">
  <p class="kicker k-red">{t['faq_k']}</p><h2>{t['faq_h']}</h2>
  {faq}
  <div class="note tip"><b>{t['limits_h']}.</b> {t['limits']}</div>
</div></section>

<footer><div class="wrap">
  <span>{t['footer_data']}</span>
  <span>{t['footer_license']} · <a href="{REPO}">GitHub</a> · <a href="{REPO}/issues">Issues</a></span>
</div></footer>
<script src="../assets/site.js"></script>
</body>
</html>
"""


INDEX = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OSMnx Routing &amp; Isochrones — QGIS plugin</title>
<link rel="icon" href="assets/icon.svg">
<link rel="stylesheet" href="assets/style.css">
<script>
(function () {
  var langs = ["en", "pt-br", "es"], pick = null;
  try { pick = localStorage.getItem("osmnx-doc-lang"); } catch (e) {}
  if (langs.indexOf(pick) < 0) {
    var nav = (navigator.languages || [navigator.language || "en"]).map(function (l) {
      return l.toLowerCase(); });
    pick = "en";
    for (var i = 0; i < nav.length; i++) {
      if (nav[i].indexOf("pt") === 0) { pick = "pt-br"; break; }
      if (nav[i].indexOf("es") === 0) { pick = "es"; break; }
      if (nav[i].indexOf("en") === 0) { pick = "en"; break; }
    }
  }
  location.replace(pick + "/");
})();
</script>
</head>
<body>
<div class="hero"><div class="wrap" style="grid-template-columns:1fr">
  <div><h1>OSMnx Routing &amp; Isochrones</h1>
  <p class="lead">Documentation · Documentação · Documentación</p>
  <a class="btn primary" href="en/">English</a>
  <a class="btn primary" href="pt-br/">Português</a>
  <a class="btn primary" href="es/">Español</a></div>
</div></div>
</body>
</html>
"""


def main():
    keys = set(TEXTS["en"])
    for lang, t in TEXTS.items():
        missing = keys ^ set(t)
        assert not missing, f"{lang}: keys differ {sorted(missing)}"
    import shutil
    icons = os.path.join(ROOT, "osmnx_routing_isochrones", "icons")
    for name in ("icon.svg", "route.svg", "isochrones.svg"):
        shutil.copy(os.path.join(icons, name), os.path.join(DOCS, "assets", name))
    for lang, _, _ in LANGS:
        os.makedirs(os.path.join(DOCS, lang), exist_ok=True)
        with open(os.path.join(DOCS, lang, "index.html"), "w", encoding="utf-8") as f:
            f.write(page(lang))
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX)
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    print("written docs/index.html and docs/{en,pt-br,es}/index.html")


if __name__ == "__main__":
    main()

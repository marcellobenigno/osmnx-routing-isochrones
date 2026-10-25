<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="es" sourcelanguage="en">
<context>
    <name>OsmnxRouting</name>
    <message>
        <source>'{layer}' layer (directed)</source>
        <translation>capa '{layer}' (dirigida)</translation>
    </message>
    <message>
        <source>'{layer}' layer is in {crs}: reprojecting to EPSG:4326.</source>
        <translation>La capa '{layer}' está en {crs}: reproyectando a EPSG:4326.</translation>
    </message>
    <message>
        <source>'{place}' was found, but OpenStreetMap has no boundary polygon for it. Use the name of a municipality, district or neighbourhood, e.g. 'Campina Grande, Paraíba, Brazil'.</source>
        <translation>Se encontró '{place}', pero OpenStreetMap no tiene un polígono de límite para ese lugar. Usa el nombre de un municipio, distrito o barrio, p. ej. 'Campina Grande, Paraíba, Brasil'.</translation>
    </message>
    <message>
        <source>1. Download road network (OSM)</source>
        <translation>1. Descargar red vial (OSM)</translation>
    </message>
    <message>
        <source>2. Inspect road network GeoPackage</source>
        <translation>2. Inspeccionar GeoPackage de la red</translation>
    </message>
    <message>
        <source>3. Shortest path (one-way aware)</source>
        <translation>3. Ruta más corta (respeta el sentido)</translation>
    </message>
    <message>
        <source>4. Isochrones (reachable areas)</source>
        <translation>4. Isócronas (áreas de alcance)</translation>
    </message>
    <message>
        <source>&lt;b&gt;{km:.2f} km&lt;/b&gt; | &lt;b&gt;{min:.1f} min&lt;/b&gt;</source>
        <translation>&lt;b&gt;{km:.2f} km&lt;/b&gt; | &lt;b&gt;{min:.1f} min&lt;/b&gt;</translation>
    </message>
    <message>
        <source>&lt;b&gt;{layer}&lt;/b&gt; layer (directed graph written at download) — most reliable</source>
        <translation>capa &lt;b&gt;{layer}&lt;/b&gt; (grafo dirigido guardado en la descarga) — la más fiable</translation>
    </message>
    <message>
        <source>&lt;p&gt;&lt;b&gt;Tip:&lt;/b&gt; to click origin and destination with pan and zoom free, use &lt;b&gt;Route on the map (OSMnx)&lt;/b&gt; on the Plugins toolbar or in Vector &gt; OSMnx Routing &amp; Isochrones.&lt;/p&gt;</source>
        <translation>&lt;p&gt;&lt;b&gt;Consejo:&lt;/b&gt; para marcar origen y destino con desplazamiento y zoom libres, usa &lt;b&gt;Ruta en el mapa (OSMnx)&lt;/b&gt; en la barra de Complementos o en Vectorial &gt; OSMnx Routing &amp; Isochrones.&lt;/p&gt;</translation>
    </message>
    <message>
        <source>&lt;p&gt;&lt;b&gt;Tip:&lt;/b&gt; to click the points with pan and zoom free, use &lt;b&gt;Isochrones on the map (OSMnx)&lt;/b&gt; on the Plugins toolbar or in Vector &gt; OSMnx Routing &amp; Isochrones.&lt;/p&gt;</source>
        <translation>&lt;p&gt;&lt;b&gt;Consejo:&lt;/b&gt; para marcar los puntos con desplazamiento y zoom libres, usa &lt;b&gt;Isócronas en el mapa (OSMnx)&lt;/b&gt; en la barra de Complementos o en Vectorial &gt; OSMnx Routing &amp; Isochrones.&lt;/p&gt;</translation>
    </message>
    <message>
        <source>&lt;p&gt;Builds polygons of the areas reachable within each time (e.g. &lt;b&gt;5, 10, 15&lt;/b&gt; min) over the road network.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Points&lt;/b&gt;: one point clicked on the map (… button) and/or a point layer (schools, health centres…). With &lt;i&gt;one isochrone per point&lt;/i&gt; unchecked, the points form a single coverage area (the nearest one counts).&lt;/p&gt;&lt;p&gt;&lt;b&gt;Car&lt;/b&gt;: travel time on the directed graph (one-way streets respected). &lt;b&gt;Direction&lt;/b&gt;: &lt;i&gt;from&lt;/i&gt; = where you can get to from the point; &lt;i&gt;to&lt;/i&gt; = where the point can be reached from (matters with one-way streets).&lt;br&gt;&lt;b&gt;Pedestrian&lt;/b&gt;: distance / walking speed, no direction.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Method&lt;/b&gt;: band around the reached roads (the last segment is cut in proportion to the remaining time) or concave hull of the reached nodes.&lt;/p&gt;&lt;p&gt;Optional output &lt;b&gt;Reached roads&lt;/b&gt;: each segment with its arrival time, great for gradient maps.&lt;/p&gt;</source>
        <translation>&lt;p&gt;Genera polígonos de las áreas alcanzables en cada tiempo (p. ej. &lt;b&gt;5, 10, 15&lt;/b&gt; min) sobre la red vial.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Puntos&lt;/b&gt;: un punto marcado en el mapa (botón …) y/o una capa de puntos (escuelas, centros de salud…). Con &lt;i&gt;una isócrona por punto&lt;/i&gt; desmarcado, los puntos forman una sola área de cobertura (cuenta el más cercano).&lt;/p&gt;&lt;p&gt;&lt;b&gt;Auto&lt;/b&gt;: tiempo de viaje en el grafo dirigido (se respeta el sentido único). &lt;b&gt;Sentido&lt;/b&gt;: &lt;i&gt;desde&lt;/i&gt; = hasta dónde se llega desde el punto; &lt;i&gt;hacia&lt;/i&gt; = desde dónde se llega al punto (importa con calles de sentido único).&lt;br&gt;&lt;b&gt;Peatón&lt;/b&gt;: distancia / velocidad a pie, sin sentido.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Método&lt;/b&gt;: franja alrededor de las calles alcanzadas (el último tramo se corta en proporción al tiempo restante) o envolvente cóncava de los nodos alcanzados.&lt;/p&gt;&lt;p&gt;Salida opcional &lt;b&gt;Calles alcanzadas&lt;/b&gt;: cada tramo con su tiempo de llegada, ideal para mapas de gradiente.&lt;/p&gt;</translation>
    </message>
    <message>
        <source>&lt;p&gt;Computes the route between two points on the road network GeoPackage. Use the &lt;b&gt;…&lt;/b&gt; button next to Origin/Destination to click on the map.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Car&lt;/b&gt;: directed graph — one-way streets only in the allowed direction. Criterion distance (length) or time (travel_time, from OSM speed or a default per road type).&lt;br&gt;&lt;b&gt;Pedestrian&lt;/b&gt;: ignores direction; time from walking speed.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Ignore one-way&lt;/b&gt; (comparison): allows driving against traffic and flags those segments (field &lt;i&gt;wrong_way&lt;/i&gt;, dashed black), showing the error of an undirected graph.&lt;/p&gt;&lt;p&gt;Points snap to the nearest node of the largest strongly connected component (car) or of the largest connected component (pedestrian), so a route always exists; a point on an isolated street may snap some distance away. For many routes, use &lt;i&gt;Run as Batch Process&lt;/i&gt;.&lt;/p&gt;</source>
        <translation>&lt;p&gt;Calcula la ruta entre dos puntos sobre el GeoPackage de la red vial. Usa el botón &lt;b&gt;…&lt;/b&gt; junto a Origen/Destino para marcar en el mapa.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Auto&lt;/b&gt;: grafo dirigido — calles de sentido único solo en el sentido permitido. Criterio distancia (length) o tiempo (travel_time, a partir de la velocidad de OSM o de un valor por tipo de vía).&lt;br&gt;&lt;b&gt;Peatón&lt;/b&gt;: ignora el sentido; tiempo según la velocidad a pie.&lt;/p&gt;&lt;p&gt;&lt;b&gt;Ignorar sentido único&lt;/b&gt; (comparación): permite ir a contramano y marca esos tramos (campo &lt;i&gt;wrong_way&lt;/i&gt;, negro punteado), mostrando el error de un grafo no dirigido.&lt;/p&gt;&lt;p&gt;Los puntos se ajustan al nodo más cercano del mayor componente fuertemente conexo (auto) o del mayor componente conexo (peatón), así que siempre existe una ruta; un punto en una calle aislada puede ajustarse a un nodo a cierta distancia. Para muchas rutas, usa &lt;i&gt;Ejecutar como proceso por lotes&lt;/i&gt;.&lt;/p&gt;</translation>
    </message>
    <message>
        <source>&lt;p&gt;Downloads the OpenStreetMap road network of a municipality (or any place Nominatim can geocode) and writes a GeoPackage with:&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&lt;b&gt;edges&lt;/b&gt;: one line per street segment (for display);&lt;/li&gt;&lt;li&gt;&lt;b&gt;arcs&lt;/b&gt;: one line per &lt;i&gt;direction of travel&lt;/i&gt; (two-way street = 2 arcs, one-way street = 1 arc digitised in the direction of traffic), used for routing;&lt;/li&gt;&lt;li&gt;&lt;b&gt;nodes&lt;/b&gt;: intersections;&lt;/li&gt;&lt;li&gt;&lt;b&gt;boundary&lt;/b&gt;: polygon of the place.&lt;/li&gt;&lt;/ul&gt;&lt;p&gt;Segments include &lt;b&gt;speed_kph&lt;/b&gt; (OSM maxspeed or a default per road type) and &lt;b&gt;travel_time&lt;/b&gt; (seconds).&lt;/p&gt;&lt;p&gt;Include state and country in the name, e.g. &lt;i&gt;Campina Grande, Paraíba, Brazil&lt;/i&gt;. Large cities may take several minutes.&lt;/p&gt;&lt;p&gt;Data © OpenStreetMap contributors (ODbL).&lt;/p&gt;</source>
        <translation>&lt;p&gt;Descarga la red vial de OpenStreetMap de un municipio (o de cualquier lugar que Nominatim pueda geocodificar) y escribe un GeoPackage con:&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&lt;b&gt;edges&lt;/b&gt;: una línea por tramo de calle (para visualización);&lt;/li&gt;&lt;li&gt;&lt;b&gt;arcs&lt;/b&gt;: una línea por &lt;i&gt;sentido de circulación&lt;/i&gt; (calle de doble sentido = 2 arcos, calle de sentido único = 1 arco digitalizado en el sentido del tránsito), usada para el ruteo;&lt;/li&gt;&lt;li&gt;&lt;b&gt;nodes&lt;/b&gt;: intersecciones;&lt;/li&gt;&lt;li&gt;&lt;b&gt;boundary&lt;/b&gt;: polígono del lugar.&lt;/li&gt;&lt;/ul&gt;&lt;p&gt;Los tramos incluyen &lt;b&gt;speed_kph&lt;/b&gt; (maxspeed de OSM o un valor por tipo de vía) y &lt;b&gt;travel_time&lt;/b&gt; (segundos).&lt;/p&gt;&lt;p&gt;Incluye estado y país en el nombre, p. ej. &lt;i&gt;Campina Grande, Paraíba, Brasil&lt;/i&gt;. Las ciudades grandes pueden tardar varios minutos.&lt;/p&gt;&lt;p&gt;Datos © colaboradores de OpenStreetMap (ODbL).&lt;/p&gt;</translation>
    </message>
    <message>
        <source>&lt;p&gt;Writes an HTML report with, for each layer: CRS, geometry type, extent, feature count, fields with type and &lt;b&gt;% filled&lt;/b&gt; (cost attributes highlighted) and a data sample.&lt;/p&gt;&lt;p&gt;It ends with a routing feasibility diagnosis: distance, speed, direction (one-way streets) and which direction source will be used.&lt;/p&gt;</source>
        <translation>&lt;p&gt;Escribe un informe HTML con, para cada capa: SRC, tipo de geometría, extensión, número de objetos, campos con tipo y &lt;b&gt;% completado&lt;/b&gt; (atributos de costo resaltados) y una muestra de datos.&lt;/p&gt;&lt;p&gt;Termina con un diagnóstico de viabilidad del ruteo: distancia, velocidad, sentido (calles de sentido único) y qué fuente de sentido se usará.&lt;/p&gt;</translation>
    </message>
    <message>
        <source>Band around the reached roads (faithful to the network)</source>
        <translation>Franja alrededor de las calles alcanzadas (fiel a la red)</translation>
    </message>
    <message>
        <source>Band width around the roads (m)</source>
        <translation>Ancho de la franja alrededor de las calles (m)</translation>
    </message>
    <message>
        <source>CRS</source>
        <translation>SRC</translation>
    </message>
    <message>
        <source>Calculate</source>
        <translation>Calcular</translation>
    </message>
    <message>
        <source>Calculate after each click</source>
        <translation>Calcular después de cada clic</translation>
    </message>
    <message>
        <source>Calculating…</source>
        <translation>Calculando…</translation>
    </message>
    <message>
        <source>Car — respects one-way streets</source>
        <translation>Auto — respeta el sentido único</translation>
    </message>
    <message>
        <source>Choose the road network GeoPackage first.</source>
        <translation>Elige primero el GeoPackage de la red vial.</translation>
    </message>
    <message>
        <source>Clear</source>
        <translation>Limpiar</translation>
    </message>
    <message>
        <source>Click one or more points on the map. Drag to pan, wheel to zoom, right click or Esc to clear.</source>
        <translation>Marca uno o más puntos en el mapa. Arrastra para desplazar, rueda para zoom, clic derecho o Esc para limpiar.</translation>
    </message>
    <message>
        <source>Click origin and destination on the map to calculate a route, with pan and zoom free</source>
        <translation>Marca origen y destino en el mapa para calcular una ruta, con desplazamiento y zoom libres</translation>
    </message>
    <message>
        <source>Click points on the map to calculate isochrones, with pan and zoom free</source>
        <translation>Marca puntos en el mapa para calcular isócronas, con desplazamiento y zoom libres</translation>
    </message>
    <message>
        <source>Click the DESTINATION on the map.</source>
        <translation>Marca el DESTINO en el mapa.</translation>
    </message>
    <message>
        <source>Click the ORIGIN on the map. Drag to pan, wheel to zoom, right click or Esc to clear.</source>
        <translation>Marca el ORIGEN en el mapa. Arrastra para desplazar, rueda para zoom, clic derecho o Esc para limpiar.</translation>
    </message>
    <message>
        <source>Computing reach: {label}</source>
        <translation>Calculando alcance: {label}</translation>
    </message>
    <message>
        <source>Concave hull of the reached nodes (smoother)</source>
        <translation>Envolvente cóncava de los nodos alcanzados (más suave)</translation>
    </message>
    <message>
        <source>Could not open {path}</source>
        <translation>No se pudo abrir {path}</translation>
    </message>
    <message>
        <source>Could not open {path} as a GeoPackage.

Details: {error}</source>
        <translation>No se pudo abrir {path} como GeoPackage.

Detalles: {error}</translation>
    </message>
    <message>
        <source>Could not overwrite {path}. Remove that file's layers from the project or choose another name.</source>
        <translation>No se pudo sobrescribir {path}. Quita las capas de ese archivo del proyecto o elige otro nombre.</translation>
    </message>
    <message>
        <source>Could not reach the OpenStreetMap servers (Nominatim/Overpass). Check your internet connection or the proxy in Settings &gt; Options &gt; Network, or try again later.

Details: {error}</source>
        <translation>No se pudo acceder a los servidores de OpenStreetMap (Nominatim/Overpass). Revisa la conexión a internet o el proxy en Configuración &gt; Opciones &gt; Red, o inténtalo más tarde.

Detalles: {error}</translation>
    </message>
    <message>
        <source>Criterion</source>
        <translation>Criterio</translation>
    </message>
    <message>
        <source>Cross-check arcs x rebuilt edges: {pct:.2f}% identical u→v pairs</source>
        <translation>Verificación arcos x tramos reconstruidos: {pct:.2f}% de pares u→v idénticos</translation>
    </message>
    <message>
        <source>Destination</source>
        <translation>Destino</translation>
    </message>
    <message>
        <source>Direction (car)</source>
        <translation>Sentido (auto)</translation>
    </message>
    <message>
        <source>Direction (oneway)</source>
        <translation>Sentido (oneway)</translation>
    </message>
    <message>
        <source>Direction source</source>
        <translation>Fuente del sentido</translation>
    </message>
    <message>
        <source>Direction source: {source}</source>
        <translation>Fuente del sentido: {source}</translation>
    </message>
    <message>
        <source>Distance (km)</source>
        <translation>Distancia (km)</translation>
    </message>
    <message>
        <source>Distance (length)</source>
        <translation>Distancia (length)</translation>
    </message>
    <message>
        <source>Distance: {km:.2f} km | Time: {min:.1f} min | {n} segments</source>
        <translation>Distancia: {km:.2f} km | Tiempo: {min:.1f} min | {n} tramos</translation>
    </message>
    <message>
        <source>Distance: {km:.2f} km | Time: {min:.1f} min | {n} segments | {oneway} on one-way streets (allowed direction)</source>
        <translation>Distancia: {km:.2f} km | Tiempo: {min:.1f} min | {n} tramos | {oneway} en calles de sentido único (sentido permitido)</translation>
    </message>
    <message>
        <source>Done</source>
        <translation>Listo</translation>
    </message>
    <message>
        <source>Downloading '{type}' network from Overpass (this may take a few minutes)...</source>
        <translation>Descargando la red '{type}' desde Overpass (puede tardar unos minutos)...</translation>
    </message>
    <message>
        <source>Enter a place name.</source>
        <translation>Escribe el nombre de un lugar.</translation>
    </message>
    <message>
        <source>Enter at least one time (minutes) greater than zero.</source>
        <translation>Escribe al menos un tiempo (minutos) mayor que cero.</translation>
    </message>
    <message>
        <source>Extent (WGS84)</source>
        <translation>Extensión (WGS84)</translation>
    </message>
    <message>
        <source>Fastest (car only)</source>
        <translation>Más rápida (solo auto)</translation>
    </message>
    <message>
        <source>Features</source>
        <translation>Objetos</translation>
    </message>
    <message>
        <source>Field</source>
        <translation>Campo</translation>
    </message>
    <message>
        <source>Field with the name of each point</source>
        <translation>Campo con el nombre de cada punto</translation>
    </message>
    <message>
        <source>File not found: {path}</source>
        <translation>Archivo no encontrado: {path}</translation>
    </message>
    <message>
        <source>Filled</source>
        <translation>Completado</translation>
    </message>
    <message>
        <source>Found: {name}</source>
        <translation>Encontrado: {name}</translation>
    </message>
    <message>
        <source>From the points (where you can get to)</source>
        <translation>Desde los puntos (hasta dónde se llega)</translation>
    </message>
    <message>
        <source>Geocoding: {place}</source>
        <translation>Geocodificando: {place}</translation>
    </message>
    <message>
        <source>Geometry</source>
        <translation>Geometría</translation>
    </message>
    <message>
        <source>Give a point on the map and/or a point layer.</source>
        <translation>Indica un punto en el mapa y/o una capa de puntos.</translation>
    </message>
    <message>
        <source>Highlighted rows: cost / direction attributes.</source>
        <translation>Filas resaltadas: atributos de costo / sentido.</translation>
    </message>
    <message>
        <source>How to install</source>
        <translation>Cómo instalar</translation>
    </message>
    <message>
        <source>Ignore one-way streets (comparison — allows wrong way)</source>
        <translation>Ignorar sentido único (comparación — permite contramano)</translation>
    </message>
    <message>
        <source>Invalid layer.</source>
        <translation>Capa no válida.</translation>
    </message>
    <message>
        <source>Invalid times: '{text}'. Use e.g. 5, 10, 15</source>
        <translation>Tiempos no válidos: '{text}'. Usa p. ej. 5, 10, 15</translation>
    </message>
    <message>
        <source>Isochrone points</source>
        <translation>Puntos de las isócronas</translation>
    </message>
    <message>
        <source>Isochrones</source>
        <translation>Isócronas</translation>
    </message>
    <message>
        <source>Isochrones ({profile}) {times} min</source>
        <translation>Isócronas ({profile}) {times} min</translation>
    </message>
    <message>
        <source>Isochrones on the map (OSMnx)</source>
        <translation>Isócronas en el mapa (OSMnx)</translation>
    </message>
    <message>
        <source>Keep previous results</source>
        <translation>Mantener resultados anteriores</translation>
    </message>
    <message>
        <source>Layer</source>
        <translation>Capa</translation>
    </message>
    <message>
        <source>Layers</source>
        <translation>Capas</translation>
    </message>
    <message>
        <source>Metres driven the wrong way</source>
        <translation>Metros recorridos a contramano</translation>
    </message>
    <message>
        <source>Missing Python libraries: {modules}.</source>
        <translation>Faltan bibliotecas de Python: {modules}.</translation>
    </message>
    <message>
        <source>Missing Python libraries: {modules}.

Install OSMnx into QGIS's Python from the Python Console (Plugins &gt; Python Console), then restart QGIS:

{code}

If geopandas or networkx are also missing, run the same command without '--no-deps'.</source>
        <translation>Faltan bibliotecas de Python: {modules}.

Instala OSMnx en el Python de QGIS desde la Consola de Python (Complementos &gt; Consola de Python) y reinicia QGIS:

{code}

Si geopandas o networkx también faltan, ejecuta el mismo comando sin '--no-deps'.</translation>
    </message>
    <message>
        <source>Missing layers: {layers} — routing will not work.</source>
        <translation>Faltan capas: {layers} — el ruteo no funcionará.</translation>
    </message>
    <message>
        <source>More than one road network in this GeoPackage ({layers}): keep a single network per GeoPackage.</source>
        <translation>Más de una red vial en este GeoPackage ({layers}): mantén una sola red por GeoPackage.</translation>
    </message>
    <message>
        <source>Network already loaded in this session (cache).</source>
        <translation>Red ya cargada en esta sesión (caché).</translation>
    </message>
    <message>
        <source>Network type</source>
        <translation>Tipo de red</translation>
    </message>
    <message>
        <source>No '{type}' roads were found inside '{name}'. Try another network type or a larger place.</source>
        <translation>No se encontraron vías del tipo '{type}' en '{name}'. Prueba otro tipo de red o un lugar más grande.</translation>
    </message>
    <message>
        <source>No CRS: EPSG:4326 will be assumed if the coordinates are lon/lat.</source>
        <translation>Sin SRC: se asumirá EPSG:4326 si las coordenadas son lon/lat.</translation>
    </message>
    <message>
        <source>No arc of {path} connects two of its nodes: the network cannot be used for routing.</source>
        <translation>Ningún arco de {path} une dos de sus nodos: la red no se puede usar para el ruteo.</translation>
    </message>
    <message>
        <source>No path between the points (disconnected network).</source>
        <translation>No hay camino entre los puntos (red desconectada).</translation>
    </message>
    <message>
        <source>No point is near the road network (all are more than {km:g} km away). Check that the points and the GeoPackage cover the same area.</source>
        <translation>Ningún punto está cerca de la red vial (todos a más de {km:g} km). Verifica que los puntos y el GeoPackage cubran la misma área.</translation>
    </message>
    <message>
        <source>No result for '{place}'. Check the spelling and include state and country, e.g. 'Campina Grande, Paraíba, Brazil'.

Details: {error}</source>
        <translation>Sin resultados para '{place}'. Revisa la escritura e incluye estado y país, p. ej. 'Campina Grande, Paraíba, Brasil'.

Detalles: {error}</translation>
    </message>
    <message>
        <source>Number of directed arcs</source>
        <translation>Número de arcos dirigidos</translation>
    </message>
    <message>
        <source>Number of nodes</source>
        <translation>Número de nodos</translation>
    </message>
    <message>
        <source>OSMnx Routing &amp; Isochrones — road network, one-way aware routing and isochrones</source>
        <translation>OSMnx Routing &amp; Isochrones — red vial, ruteo que respeta el sentido e isócronas</translation>
    </message>
    <message>
        <source>OSMnx isochrones</source>
        <translation>Isócronas OSMnx</translation>
    </message>
    <message>
        <source>OSMnx route</source>
        <translation>Ruta OSMnx</translation>
    </message>
    <message>
        <source>One isochrone per point (unchecked = combined coverage)</source>
        <translation>Una isócrona por punto (desmarcado = cobertura combinada)</translation>
    </message>
    <message>
        <source>Origin</source>
        <translation>Origen</translation>
    </message>
    <message>
        <source>Origin and destination snap to the same network node.</source>
        <translation>El origen y el destino se ajustan al mismo nodo de la red.</translation>
    </message>
    <message>
        <source>Output GeoPackage</source>
        <translation>GeoPackage de salida</translation>
    </message>
    <message>
        <source>Pedestrian — ignores street direction</source>
        <translation>Peatón — ignora el sentido de las calles</translation>
    </message>
    <message>
        <source>Pedestrian: shortest and fastest routes are the same.</source>
        <translation>Peatón: la ruta más corta y la más rápida son la misma.</translation>
    </message>
    <message>
        <source>Pedestrians ignore direction: 'from' and 'to' are the same.</source>
        <translation>Los peatones ignoran el sentido: 'desde' y 'hacia' son lo mismo.</translation>
    </message>
    <message>
        <source>Pick on map</source>
        <translation>Marcar en el mapa</translation>
    </message>
    <message>
        <source>Place name (as in OSM, with state and country)</source>
        <translation>Nombre del lugar (como en OSM, con estado y país)</translation>
    </message>
    <message>
        <source>Point (click on the map)</source>
        <translation>Punto (clic en el mapa)</translation>
    </message>
    <message>
        <source>Point fid {fid} skipped: it could not be converted to WGS84.</source>
        <translation>Punto fid {fid} omitido: no se pudo convertir a WGS84.</translation>
    </message>
    <message>
        <source>Point layer (optional)</source>
        <translation>Capa de puntos (opcional)</translation>
    </message>
    <message>
        <source>Points</source>
        <translation>Puntos</translation>
    </message>
    <message>
        <source>Polygon method</source>
        <translation>Método del polígono</translation>
    </message>
    <message>
        <source>Press 'Pick on map' to choose the points.</source>
        <translation>Pulsa 'Marcar en el mapa' para elegir los puntos.</translation>
    </message>
    <message>
        <source>Profile</source>
        <translation>Perfil</translation>
    </message>
    <message>
        <source>Reached roads</source>
        <translation>Calles alcanzadas</translation>
    </message>
    <message>
        <source>Reached roads ({profile})</source>
        <translation>Calles alcanzadas ({profile})</translation>
    </message>
    <message>
        <source>Reading nodes and edges...</source>
        <translation>Leyendo nodos y tramos...</translation>
    </message>
    <message>
        <source>Report</source>
        <translation>Informe</translation>
    </message>
    <message>
        <source>Road network GeoPackage</source>
        <translation>GeoPackage de la red vial</translation>
    </message>
    <message>
        <source>Road network inspection</source>
        <translation>Inspección de la red vial</translation>
    </message>
    <message>
        <source>Road type (highway)</source>
        <translation>Tipo de vía (highway)</translation>
    </message>
    <message>
        <source>Route</source>
        <translation>Ruta</translation>
    </message>
    <message>
        <source>Route ({profile}) {km:.2f} km</source>
        <translation>Ruta ({profile}) {km:.2f} km</translation>
    </message>
    <message>
        <source>Route on the map (OSMnx)</source>
        <translation>Ruta en el mapa (OSMnx)</translation>
    </message>
    <message>
        <source>Route points</source>
        <translation>Puntos de la ruta</translation>
    </message>
    <message>
        <source>Routing diagnosis</source>
        <translation>Diagnóstico de ruteo</translation>
    </message>
    <message>
        <source>Sample</source>
        <translation>Muestra</translation>
    </message>
    <message>
        <source>Shortest distance</source>
        <translation>Menor distancia</translation>
    </message>
    <message>
        <source>Speed (maxspeed)</source>
        <translation>Velocidad (maxspeed)</translation>
    </message>
    <message>
        <source>Swap</source>
        <translation>Invertir</translation>
    </message>
    <message>
        <source>The 'arcs' layer overlaps 'edges' on the map; switch it off if you prefer.</source>
        <translation>La capa 'arcs' se superpone a 'edges' en el mapa; desactívala si prefieres.</translation>
    </message>
    <message>
        <source>The '{layer}' layer has no coordinate reference system (CRS). Assign one in QGIS (Layer Properties &gt; Source) or download the network again.</source>
        <translation>La capa '{layer}' no tiene sistema de referencia de coordenadas (SRC). Asígnale uno en QGIS (Propiedades de la capa &gt; Fuente) o descarga la red de nuevo.</translation>
    </message>
    <message>
        <source>The '{layer}' layer has no {fields} field(s): this does not look like a road network written by this plugin or by OSMnx.</source>
        <translation>La capa '{layer}' no tiene el/los campo(s) {fields}: no parece una red vial escrita por este complemento o por OSMnx.</translation>
    </message>
    <message>
        <source>The GeoPackage has no '{layer}' layer.</source>
        <translation>El GeoPackage no tiene la capa '{layer}'.</translation>
    </message>
    <message>
        <source>The OpenStreetMap server refused or could not complete the request (it is probably busy). Wait a few minutes and try again.

Details: {error}</source>
        <translation>El servidor de OpenStreetMap rechazó o no pudo completar la solicitud (probablemente está ocupado). Espera unos minutos e inténtalo de nuevo.

Detalles: {error}</translation>
    </message>
    <message>
        <source>The OpenStreetMap server took too long to answer (timeout). It may be overloaded: try again in a few minutes, or use a smaller place.

Details: {error}</source>
        <translation>El servidor de OpenStreetMap tardó demasiado en responder (tiempo agotado). Puede estar sobrecargado: inténtalo en unos minutos o usa un lugar más pequeño.

Detalles: {error}</translation>
    </message>
    <message>
        <source>The calculation failed.</source>
        <translation>El cálculo falló.</translation>
    </message>
    <message>
        <source>The destination</source>
        <translation>El destino</translation>
    </message>
    <message>
        <source>The destination is {dist:.0f} m from the nearest network node.</source>
        <translation>El destino está a {dist:.0f} m del nodo más cercano de la red.</translation>
    </message>
    <message>
        <source>The network was saved to a TEMPORARY file, deleted when QGIS closes: {path}
To keep it, run again choosing an 'Output GeoPackage' file, or copy that file. Use the GeoPackage itself in the other algorithms (its layers already have the right names and CRS).</source>
        <translation>La red se guardó en un archivo TEMPORAL, que se borra al cerrar QGIS: {path}
Para conservarla, ejecuta de nuevo eligiendo un archivo en 'GeoPackage de salida', o copia ese archivo. Usa el propio GeoPackage en los demás algoritmos (sus capas ya tienen los nombres y el SRC correctos).</translation>
    </message>
    <message>
        <source>The origin</source>
        <translation>El origen</translation>
    </message>
    <message>
        <source>The origin is {dist:.0f} m from the nearest network node.</source>
        <translation>El origen está a {dist:.0f} m del nodo más cercano de la red.</translation>
    </message>
    <message>
        <source>The point</source>
        <translation>El punto</translation>
    </message>
    <message>
        <source>The point layer has no valid coordinate reference system (CRS). Set it in Layer Properties &gt; Source and run again.</source>
        <translation>La capa de puntos no tiene un sistema de referencia de coordenadas (SRC) válido. Defínelo en Propiedades de la capa &gt; Fuente y ejecuta de nuevo.</translation>
    </message>
    <message>
        <source>The road network in {path} is empty.</source>
        <translation>La red vial en {path} está vacía.</translation>
    </message>
    <message>
        <source>Time (min)</source>
        <translation>Tiempo (min)</translation>
    </message>
    <message>
        <source>Times in minutes (comma separated)</source>
        <translation>Tiempos en minutos (separados por comas)</translation>
    </message>
    <message>
        <source>To the points (where they can be reached from)</source>
        <translation>Hacia los puntos (desde dónde se llega a ellos)</translation>
    </message>
    <message>
        <source>Type</source>
        <translation>Tipo</translation>
    </message>
    <message>
        <source>Units</source>
        <translation>Unidades</translation>
    </message>
    <message>
        <source>Using layers {nodes} and {edges}.</source>
        <translation>Usando las capas {nodes} y {edges}.</translation>
    </message>
    <message>
        <source>Using the proxy configured in QGIS.</source>
        <translation>Usando el proxy configurado en QGIS.</translation>
    </message>
    <message>
        <source>Walking speed (km/h)</source>
        <translation>Velocidad a pie (km/h)</translation>
    </message>
    <message>
        <source>Warning: point '{label}' is {dist:.0f} m away from the network.</source>
        <translation>Atención: el punto '{label}' está a {dist:.0f} m de la red.</translation>
    </message>
    <message>
        <source>Warning: point '{label}' skipped: {msg}</source>
        <translation>Atención: punto '{label}' omitido: {msg}</translation>
    </message>
    <message>
        <source>Warning: the '{layer}' layer has no CRS; its coordinates look like longitude/latitude, so EPSG:4326 is assumed.</source>
        <translation>Atención: la capa '{layer}' no tiene SRC; sus coordenadas parecen longitud/latitud, así que se asume EPSG:4326.</translation>
    </message>
    <message>
        <source>Writing {path}</source>
        <translation>Escribiendo {path}</translation>
    </message>
    <message>
        <source>all — every road and path (incl. private)</source>
        <translation>all — todas las vías y caminos (incl. privados)</translation>
    </message>
    <message>
        <source>all_public — every public road and path</source>
        <translation>all_public — todas las vías y caminos públicos</translation>
    </message>
    <message>
        <source>allowed direction</source>
        <translation>sentido permitido</translation>
    </message>
    <message>
        <source>basis for speed imputation</source>
        <translation>base para imputar la velocidad</translation>
    </message>
    <message>
        <source>bike — cycling network</source>
        <translation>bike — red ciclista</translation>
    </message>
    <message>
        <source>car</source>
        <translation>auto</translation>
    </message>
    <message>
        <source>clicked point</source>
        <translation>punto marcado</translation>
    </message>
    <message>
        <source>defines one-way / two-way streets</source>
        <translation>define calles de sentido único / doble sentido</translation>
    </message>
    <message>
        <source>degrees (geographic)</source>
        <translation>grados (geográfico)</translation>
    </message>
    <message>
        <source>destination</source>
        <translation>destino</translation>
    </message>
    <message>
        <source>directed 'edges' layer</source>
        <translation>capa 'edges' dirigida</translation>
    </message>
    <message>
        <source>directed &lt;b&gt;edges&lt;/b&gt; layer (u, v, key)</source>
        <translation>capa &lt;b&gt;edges&lt;/b&gt; dirigida (u, v, key)</translation>
    </message>
    <message>
        <source>drive — public drivable roads</source>
        <translation>drive — vías públicas para autos</translation>
    </message>
    <message>
        <source>drive_service — drivable roads + service roads</source>
        <translation>drive_service — vías para autos + vías de servicio</translation>
    </message>
    <message>
        <source>highway (10 most common)</source>
        <translation>highway (10 más frecuentes)</translation>
    </message>
    <message>
        <source>metres (projected)</source>
        <translation>metros (proyectado)</translation>
    </message>
    <message>
        <source>metres; cost of the shortest path</source>
        <translation>metros; costo de la ruta más corta</translation>
    </message>
    <message>
        <source>origin</source>
        <translation>origen</translation>
    </message>
    <message>
        <source>pedestrian</source>
        <translation>peatón</translation>
    </message>
    <message>
        <source>rebuilt from 'edges' (from/to + oneway; {n:,} geometries re-oriented)</source>
        <translation>reconstruida a partir de 'edges' (from/to + oneway; {n:,} geometrías reorientadas)</translation>
    </message>
    <message>
        <source>rebuilt from &lt;b&gt;edges&lt;/b&gt; (from/to + oneway)</source>
        <translation>reconstruida a partir de &lt;b&gt;edges&lt;/b&gt; (from/to + oneway)</translation>
    </message>
    <message>
        <source>segments</source>
        <translation>tramos</translation>
    </message>
    <message>
        <source>the rest is imputed from the road type</source>
        <translation>el resto se imputa por el tipo de vía</translation>
    </message>
    <message>
        <source>walk — pedestrian network</source>
        <translation>walk — red peatonal</translation>
    </message>
    <message>
        <source>wrong way</source>
        <translation>contramano</translation>
    </message>
    <message>
        <source>{layer}: {crs}, {geom}, {n:,} features, {fields} fields</source>
        <translation>{layer}: {crs}, {geom}, {n:,} objetos, {fields} campos</translation>
    </message>
    <message>
        <source>{m:.0f} m driven the wrong way</source>
        <translation>{m:.0f} m a contramano</translation>
    </message>
    <message>
        <source>{nodes:,} nodes and {arcs:,} arcs</source>
        <translation>{nodes:,} nodos y {arcs:,} arcos</translation>
    </message>
    <message>
        <source>{nodes:,} nodes | {arcs:,} arcs ({oneway:,} one-way) | largest strongly connected component: {pct:.1f}% of nodes | metric CRS {crs}</source>
        <translation>{nodes:,} nodos | {arcs:,} arcos ({oneway:,} de sentido único) | mayor componente fuertemente conexo: {pct:.1f}% de los nodos | SRC métrico {crs}</translation>
    </message>
    <message>
        <source>{n} point(s) | times: {times} min | profile {profile} | direction {direction} | method {method}</source>
        <translation>{n} punto(s) | tiempos: {times} min | perfil {profile} | sentido {direction} | método {method}</translation>
    </message>
    <message>
        <source>{n} points</source>
        <translation>{n} puntos</translation>
    </message>
    <message>
        <source>{n} segment(s) driven the WRONG WAY: {m:.0f} m</source>
        <translation>{n} tramo(s) recorrido(s) a CONTRAMANO: {m:.0f} m</translation>
    </message>
    <message>
        <source>{path} holds more than one road network ({layers}). Keep a single network per GeoPackage.</source>
        <translation>{path} contiene más de una red vial ({layers}). Mantén una sola red por GeoPackage.</translation>
    </message>
    <message>
        <source>{what} is {km:.1f} km from the road network. Is it inside the area of the GeoPackage?</source>
        <translation>{what} está a {km:.1f} km de la red vial. ¿Está dentro del área del GeoPackage?</translation>
    </message>
</context>
</TS>

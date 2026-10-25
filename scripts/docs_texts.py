"""
Texts of the documentation site, one dict per language with the same keys (checked by
scripts/build_docs.py). HTML is allowed in the values.

Editorial rules (see the review in melhorias.md):
- state conditions and limits instead of promises ("any town", "no limits", "instantly");
- results are estimates from OpenStreetMap data, not real-time traffic or navigation;
- explain a term the first time it appears, or point to the glossary;
- for every tool: use when, inputs, outputs, how to read the result, limitations.
Technical statements follow osmnx_routing_isochrones/core.py; update both together.
"""

REPO = "https://github.com/marcellobenigno/osmnx-routing-isochrones"
AUTHOR_LINKS = (("GitHub", "https://github.com/marcellobenigno"),
                ("LinkedIn", "https://linkedin.com/in/marcellobenigno"),
                ("E-mail", "mailto:marcello@ifpb.edu.br"))

INSTALL_CODE = """from pip._internal.cli.main import main as pip
pip(["install", "--user", "--no-deps", "osmnx"])"""

VERIFY_CODE = """import sys, osmnx, geopandas, networkx
print(sys.prefix)                       # should be inside the QGIS installation
print("osmnx", osmnx.__version__, "| geopandas", geopandas.__version__,
      "| networkx", networkx.__version__)"""

PYTHON_CODE = {
    "en": """import processing

# 1. download once (needs internet)
processing.run("osmnx_routing:download_network", {
    "PLACE": "Cabedelo, Paraíba, Brazil", "TYPE": 2,          # 2 = drive
    "OUTPUT": "/data/cabedelo.gpkg"})

# 2. route by car, minimum estimated time (runs locally)
res = processing.run("osmnx_routing:shortest_path", {
    "NETWORK": "/data/cabedelo.gpkg", "PROFILE": 0, "CRITERION": 1,
    "ORIGIN": "-34.8410,-7.0323 [EPSG:4326]",
    "DESTINATION": "-34.8417,-7.0371 [EPSG:4326]",
    "OUTPUT": "TEMPORARY_OUTPUT"})
print(res["DISTANCE_KM"], res["TIME_MIN"])

# 3. walking isochrones of a point layer, one per point
processing.runAndLoadResults("osmnx_routing:isochrones", {
    "NETWORK": "/data/cabedelo.gpkg", "PROFILE": 1,           # 1 = pedestrian
    "POINTS": "/data/schools.gpkg", "ID_FIELD": "name", "SEPARATE": True,
    "MINUTES": "5, 10, 15", "OUTPUT": "TEMPORARY_OUTPUT", "ROADS": "TEMPORARY_OUTPUT"})""",
    "pt-br": """import processing

# 1. baixar uma vez (precisa de internet)
processing.run("osmnx_routing:download_network", {
    "PLACE": "Cabedelo, Paraíba, Brasil", "TYPE": 2,          # 2 = drive
    "OUTPUT": "/dados/cabedelo.gpkg"})

# 2. rota de carro, menor tempo estimado (roda localmente)
res = processing.run("osmnx_routing:shortest_path", {
    "NETWORK": "/dados/cabedelo.gpkg", "PROFILE": 0, "CRITERION": 1,
    "ORIGIN": "-34.8410,-7.0323 [EPSG:4326]",
    "DESTINATION": "-34.8417,-7.0371 [EPSG:4326]",
    "OUTPUT": "TEMPORARY_OUTPUT"})
print(res["DISTANCE_KM"], res["TIME_MIN"])

# 3. isócronas a pé de uma camada de pontos, uma por ponto
processing.runAndLoadResults("osmnx_routing:isochrones", {
    "NETWORK": "/dados/cabedelo.gpkg", "PROFILE": 1,          # 1 = pedestre
    "POINTS": "/dados/escolas.gpkg", "ID_FIELD": "nome", "SEPARATE": True,
    "MINUTES": "5, 10, 15", "OUTPUT": "TEMPORARY_OUTPUT", "ROADS": "TEMPORARY_OUTPUT"})""",
    "es": """import processing

# 1. descargar una vez (requiere internet)
processing.run("osmnx_routing:download_network", {
    "PLACE": "Cabedelo, Paraíba, Brasil", "TYPE": 2,          # 2 = drive
    "OUTPUT": "/datos/cabedelo.gpkg"})

# 2. ruta en auto, menor tiempo estimado (se ejecuta localmente)
res = processing.run("osmnx_routing:shortest_path", {
    "NETWORK": "/datos/cabedelo.gpkg", "PROFILE": 0, "CRITERION": 1,
    "ORIGIN": "-34.8410,-7.0323 [EPSG:4326]",
    "DESTINATION": "-34.8417,-7.0371 [EPSG:4326]",
    "OUTPUT": "TEMPORARY_OUTPUT"})
print(res["DISTANCE_KM"], res["TIME_MIN"])

# 3. isócronas a pie de una capa de puntos, una por punto
processing.runAndLoadResults("osmnx_routing:isochrones", {
    "NETWORK": "/datos/cabedelo.gpkg", "PROFILE": 1,          # 1 = peatón
    "POINTS": "/datos/escuelas.gpkg", "ID_FIELD": "nombre", "SEPARATE": True,
    "MINUTES": "5, 10, 15", "OUTPUT": "TEMPORARY_OUTPUT", "ROADS": "TEMPORARY_OUTPUT"})""",
}

FIELDS = ("<code>speed_kph</code>", "<code>travel_time</code>", "<code>wrong_way</code>",
          "<code>DISTANCE_KM</code> · <code>TIME_MIN</code> · <code>WRONG_WAY_M</code>",
          "<code>minutes</code> · <code>area_km2</code> · <code>roads_km</code>",
          "<code>t_start_min</code> · <code>t_end_min</code>")

TEXTS = {
    # ================================================================== English
    "en": {
        "title": "OSMnx Routing & Isochrones — QGIS plugin",
        "description": "QGIS plugin that downloads OpenStreetMap road networks and computes "
                       "one-way aware routes and isochrones locally, without a routing API.",
        "copy": "Copy",
        "nav": ["Overview", "Install", "Quick start", "Map tools", "Algorithms",
                "How it works", "Help", "Author"],
        "hero_h1": "Routes and isochrones from OpenStreetMap, inside QGIS",
        "hero_lead": "Download the road network of a place once, save it as a GeoPackage, then "
                     "calculate routes that respect one-way streets and the areas reachable "
                     "in a given time — on your computer, without a routing service or API "
                     "key. Results are estimates based on the OpenStreetMap data of each "
                     "place.",
        "hero_badges": ["QGIS 3.34+ (tested)", "OSMnx 2.x", "EN · PT-BR · ES interface",
                        "GPL-2.0"],
        "hero_install": "Install the plugin", "hero_github": "Source on GitHub",
        "hero_alt": "Map of João Pessoa, Brazil, with car isochrones of 2, 4, 6 and 8 minutes "
                    "coloured from green (near) to red (far)",
        "before_h": "Before you start",
        "before": "Downloading a network needs an internet connection: the place is looked up "
                  "with Nominatim and the streets come from Overpass, two OpenStreetMap "
                  "services. Once the GeoPackage is saved on your computer, routes and "
                  "isochrones run locally. The results depend on the coverage and the "
                  "attributes available in OpenStreetMap, which vary from place to place.",
        "feat_k": "Overview", "feat_h": "What the plugin does",
        "feat_intro": "Four Processing algorithms and two interactive map tools built on "
                      "<a href='https://osmnx.readthedocs.io/'>OSMnx</a> (download and graph "
                      "handling) and NetworkX (shortest paths).",
        "features": [
            ("🗺️", "t-green", "A network of your own",
             "Turns a place name into a GeoPackage with nodes, street segments, directed "
             "arcs and the boundary of the place."),
            ("↪️", "t-red", "One-way streets",
             "Car routes follow the direction of travel recorded in OSM. A comparison mode "
             "shows where an undirected graph would drive the wrong way."),
            ("⏱️", "t-orange", "Isochrones",
             "Areas estimated as reachable in 5, 10, 15… minutes from points or to points, "
             "with the arrival time on every reached street."),
            ("🖱️", "t-blue", "Click on the map",
             "Side panels keep the map visible: click the points, pan and zoom freely; the "
             "calculation runs in the background."),
        ],
        "notdo_h": "What it does not do",
        "notdo": ["real-time or historical traffic, traffic lights or turn delays;",
                  "turn restrictions, barriers and access rules inside the downloaded network "
                  "(only the network type filters roads at download time);",
                  "public transport or multimodal trips;",
                  "turn-by-turn navigation: a calculated route is not a legal or recommended "
                  "driving route."],
        "choose_h": "Which tool should I use?",
        "choose_cols": ["I want to…", "Use", "You get"],
        "choose_rows": [
            ("work in a new place", "1. Download road network (OSM)",
             "a GeoPackage with the network (needs internet)"),
            ("check a GeoPackage before using it", "2. Inspect road network GeoPackage",
             "an HTML report: CRS, fields, fill rate, routing diagnosis"),
            ("try a route by clicking", "Route on the map (toolbar)",
             "route line, two points, distance and time in the panel"),
            ("compute many routes or use a model", "3. Shortest path (Processing)",
             "route layer and DISTANCE_KM / TIME_MIN outputs"),
            ("see what is reachable from or to places", "Isochrones on the map, or "
             "4. Isochrones (Processing) for a point layer",
             "isochrone polygons, reached roads and the points used"),
        ],
        "paths_note": "The map tools and the Processing algorithms are <b>two ways to do the "
                      "same calculation</b>: the panels are meant for exploring by clicking; "
                      "the algorithms suit point layers, <i>Run as Batch Process</i>, the "
                      "Graphical Modeler and Python scripts.",
        "inst_k": "Installation", "inst_h": "Install, restart, verify",
        "inst_intro": "QGIS already ships geopandas, networkx, shapely and pyproj. OSMnx has "
                      "to be added to the Python environment <i>that QGIS uses</i>, which is "
                      "usually not the same as other Python installations on your computer.",
        "req_h": "Requirements and tested versions",
        "req": ["Declared minimum: QGIS 3.28. Automated tests run on Linux with QGIS 3.34, "
                "the current LTR and the latest release; the plugin was also tested by hand "
                "on QGIS 3.44 (macOS). Windows has not been tested yet.",
                "OSMnx 2.x (tested with 2.1), which needs geopandas 1.0 or newer.",
                "Internet only to download networks; routing and isochrones run offline "
                "from the GeoPackage.",
                "No administrator rights: <code>--user</code> installs into your home "
                "folder."],
        "inst_steps": [
            ("Install OSMnx in QGIS's Python",
             "Open <b>Plugins → Python Console</b>, paste the code below and press Enter. "
             "<code>--no-deps</code> keeps the libraries that came with QGIS untouched (see "
             "below)."),
            ("Restart QGIS and verify",
             "After restarting, run this in the Python Console. The first line shows which "
             "Python is running; the second must print the versions without errors."),
            ("Install the plugin",
             "<b>Plugins → Manage and Install Plugins</b>, search for <b>OSMnx Routing &amp; "
             "Isochrones</b>. While it is experimental, tick <i>Show also experimental "
             "plugins</i> in Settings. You can also use <i>Install from ZIP</i> with a file "
             "from the <a href='" + REPO + "/releases'>releases</a>. Then check that "
             "<b>OSMnx Routing &amp; Isochrones</b> appears in the Processing Toolbox."),
        ],
        "inst_more": [
            ("Why <code>--no-deps</code>, and when to leave it out?",
             "OSMnx depends on numpy, pandas, geopandas, networkx, shapely and requests, which "
             "QGIS normally provides. Without <code>--no-deps</code>, pip may replace them "
             "with versions that QGIS's own modules (GDAL, scipy) were not built for, causing "
             "errors that are hard to trace. If the verification shows "
             "<code>ModuleNotFoundError</code> for another package, or a geopandas older than "
             "1.0 (older Linux packages), install just that package the same way, e.g. "
             "<code>pip([\"install\", \"--user\", \"--no-deps\", \"requests\"])</code>, or run "
             "the command without <code>--no-deps</code> as a last resort."),
            ("How do I know pip installed into QGIS's Python?",
             "Run the command in QGIS's own Python Console, not in a terminal. "
             "<code>sys.prefix</code> in the verification should point inside the QGIS "
             "installation (e.g. <code>/Applications/QGIS.app/…</code>, "
             "<code>C:\\Program Files\\QGIS …</code>, or <code>/usr</code> for Linux "
             "packages). If OSMnx is found in a terminal but not in QGIS, it went to another "
             "Python."),
            ("<code>--user</code> does not work",
             "In a conda or virtual environment pip refuses <code>--user</code>: remove it "
             "from the command. On recent Debian/Ubuntu, pip may stop with "
             "<code>externally-managed-environment</code>; adding "
             "<code>\"--break-system-packages\"</code> to the list is acceptable here because "
             "<code>--user</code> only writes to your home folder. With the OSGeo4W installer "
             "on Windows you can also use the <i>OSGeo4W Shell</i>: "
             "<code>python -m pip install --no-deps osmnx</code>."),
        ],
        "inst_note": "While a library is missing, the plugin shows a message with a <b>How to "
                     "install</b> button and its algorithms stay disabled; the message also "
                     "goes to <i>View → Panels → Log Messages</i>, tab <i>OSMnx Routing</i>.",
        "qs_k": "Quick start", "qs_h": "From a place name to a map",
        "qs_intro": "A complete first run in Cabedelo, a small coastal town in Brazil: it "
                    "downloads in under a minute on a normal connection.",
        "qs_steps": [
            ("Download the road network",
             "Processing Toolbox (<code>Ctrl+Alt+T</code>) → <b>OSMnx Routing &amp; "
             "Isochrones → 1. Download road network (OSM)</b>. Type <i>Cabedelo, Paraíba, "
             "Brazil</i>, choose <i>drive</i> and save to a file (not a temporary output). "
             "<b>Expected:</b> four layers in the project — <code>…_boundary</code>, "
             "<code>…_edges</code>, <code>…_nodes</code>, <code>…_arcs</code>."),
            ("Check what you got (optional)",
             "<b>2. Inspect road network GeoPackage</b> writes an HTML report. "
             "<b>Expected:</b> CRS EPSG:4326 and the <code>arcs</code> layer as the "
             "direction source."),
            ("Click a route",
             "Toolbar button <b>Route on the map</b>: click the origin, then the destination. "
             "<b>Expected:</b> a red line and the distance and estimated time in the panel."),
            ("Click isochrones",
             "Toolbar button <b>Isochrones on the map</b>: click a point. <b>Expected:</b> "
             "polygons for 5, 10 and 15 minutes, from green to red, and their areas in the "
             "panel."),
        ],
        "wf": ["Place name", "1. Download", "GeoPackage", "nodes · edges · arcs · boundary",
               "2. Inspect", "HTML report", "3. Shortest path", "Route", "4. Isochrones",
               "Reachable areas"],
        "tools_k": "Map tools", "tools_h": "Click on the map, keep pan and zoom free",
        "tools_intro": "Both tools open a side panel that does not cover the map. A click "
                       "picks a point, dragging pans, the wheel zooms, right click or "
                       "<code>Esc</code> clears. The road network GeoPackage is taken from "
                       "the layers already open in the project; you can also choose it in "
                       "the panel.",
        "route_h": "Route on the map",
        "route_p": "First click = <b style='color:#1a9641'>origin</b>, second click = "
                   "<b style='color:#d62728'>destination</b>; the route is then calculated in "
                   "the background. <b>Swap</b> reverses it; a third click starts a new "
                   "origin. The clicks are kept in the <i>Route points</i> layer.",
        "route_cap": "The route panel next to the map, with the distance and the estimated "
                     "time.",
        "iso_h": "Isochrones on the map",
        "iso_p": "Every click adds a point (P1, P2…) to the <i>Isochrone points</i> layer and "
                 "the isochrones are recalculated — untick <i>Calculate after each click</i> "
                 "to add several points first. The panel lists the area of every time band.",
        "iso_cap": "The isochrone panel: times, direction, method and the area of each band.",
        "tools_tip": "Each run replaces the previous result; tick <b>Keep previous "
                     "results</b> to compare scenarios side by side.",
        "tools_stop": "<b>Stopping a calculation.</b> Map tools run as QGIS background "
                      "tasks: cancel them from the progress bar at the bottom of the QGIS "
                      "window. In a Processing dialog, use <b>Cancel</b>. Errors appear in "
                      "the panel, or in the <i>Log</i> tab of the dialog.",
        "shots_note": "Screenshots: plugin 0.1, QGIS 3.44, interface in English.",
        "alg_k": "Reference", "alg_h": "The four Processing algorithms",
        "alg_intro": "They work in the dialog, in <i>Run as Batch Process</i>, in the "
                     "Graphical Modeler and from Python. Every block follows the same order: "
                     "when to use it, inputs, outputs, how to read the result and its "
                     "limitations.",
        "param": "Parameter", "desc": "Description", "outputs": "Outputs",
        "use_l": "Use when", "read_l": "How to read the result", "limits_l": "Limitations",
        "algs": [
            ("1. Download road network (OSM)", "osmnx_routing:download_network", "icon",
             "var(--green)",
             "you need a network for a place you have not downloaded yet.",
             [("Place name", "Municipality, district or neighbourhood with state and country, "
                             "e.g. <i>Campina Grande, Paraíba, Brazil</i>. Nominatim looks "
                             "it up and its boundary polygon limits the download."),
              ("Network type", "<code>drive</code> public drivable roads · "
                               "<code>drive_service</code> plus service roads · "
                               "<code>walk</code> pedestrian network · <code>bike</code> "
                               "cycling network · <code>all_public</code> every public way · "
                               "<code>all</code> including private ones. Choose one that "
                               "matches the profile you will use."),
              ("Output GeoPackage", "File to write. A temporary output is deleted when QGIS "
                                    "closes; the log warns about it.")],
             "Layers <code>edges</code> (one line per street segment, for display), "
             "<code>arcs</code> (one line per direction of travel, used for routing), "
             "<code>nodes</code> and <code>boundary</code> (with the query, the OSM name and "
             "the download date). Segments carry <code>speed_kph</code> and "
             "<code>travel_time</code>.",
             "The log gives the number of nodes and arcs. Show <code>edges</code> over a "
             "basemap to see whether the streets you need are there.",
             "Needs internet; uses the HTTP proxy set in <i>Settings → Options → Network</i>. "
             "Large places can take several minutes and Overpass may refuse heavy queries. "
             "Respect the usage policies of Nominatim and Overpass: avoid repeating requests "
             "in quick succession. Identical requests are answered from the OSMnx cache in "
             "<code>~/osmnx/cache</code>."),
            ("2. Inspect road network GeoPackage", "osmnx_routing:inspect_network", "icon",
             "var(--blue)",
             "you received or edited a GeoPackage and want to check it before routing. Needs "
             "QGIS only, not OSMnx.",
             [("Road network GeoPackage", "Any GeoPackage; layers may carry a prefix "
                                          "(<code>patos_nodes</code>…)."),
              ("Report", "HTML file to write.")],
             "An HTML report that opens in the browser: CRS, geometry, extent, fields with "
             "the share of filled values, a data sample and a routing diagnosis.",
             "A low fill rate of <code>maxspeed</code> means most times come from default "
             "speeds. The direction source should be the <code>arcs</code> layer.",
             "It describes the data; it does not correct it."),
            ("3. Shortest path (one-way aware)", "osmnx_routing:shortest_path", "route",
             "var(--red)",
             "you need the path between two points, its length and its estimated time.",
             [("Profile", "Car — follows one-way streets · Pedestrian — ignores the "
                          "direction."),
              ("Criterion", "<i>Shortest distance</i> minimises length in metres. "
                            "<i>Fastest</i> (car) minimises <code>travel_time</code>, an "
                            "estimate from speeds; see <a href='#how-it-works'>How it "
                            "works</a>."),
              ("Origin, Destination", "Points in any CRS. Each one is attached to the nearest "
                                      "node of the network, as explained below."),
              ("Ignore one-way streets", "For comparison or diagnosis only: allows driving "
                                         "against traffic and flags those segments."),
              ("Walking speed", "km/h, default 4.8.")],
             "<b>Route</b> lines with order, street name, road type, one-way, "
             "<code>wrong_way</code>, length, speed, time and cumulative values; <b>Route "
             "points</b>; the numbers DISTANCE_KM, TIME_MIN and WRONG_WAY_M.",
             "Compare the route with the basemap. The log warns when a point is more than "
             "150 m from its node: the route then starts or ends at that node, not at the "
             "click.",
             "The time does not include traffic, traffic lights or turn delays, and turn "
             "restrictions are not applied. One-way rules are only as complete as the OSM "
             "tags."),
            ("4. Isochrones (reachable areas)", "osmnx_routing:isochrones", "isochrones",
             "var(--orange)",
             "you want the area that can be reached within some minutes from points (or "
             "from which points can be reached).",
             [("Point / Point layer", "A clicked point, a layer (schools, clinics…) or both; "
                                      "the ID field names each point."),
              ("One isochrone per point", "Ticked: one set of polygons per point. Unticked: "
                                          "one combined coverage of all points."),
              ("Direction (car)", "<i>From</i> the points (where you can get to) or "
                                  "<i>to</i> them (where they can be reached from)."),
              ("Times in minutes", "e.g. <code>5, 10, 15</code> (also <code>5;10;15</code>)."),
              ("Polygon method", "Band around the reached roads, or concave hull of the "
                                 "reached nodes."),
              ("Band width", "Metres around the roads, default 40.")],
             "<b>Isochrones</b> (source, minutes, area_km2, roads_km), <b>Reached roads</b> "
             "with start and end arrival time, <b>Isochrone points</b>.",
             "Read the polygons together with <b>Reached roads</b>: the polygon is a map "
             "representation; the roads layer shows what the network actually reaches.",
             "Same limits as the routes. A pedestrian isochrone on a <code>drive</code> "
             "network misses footpaths: download <code>walk</code> or <code>all</code> for "
             "walking studies."),
        ],
        "fields_h": "Fields and outputs",
        "fields_cols": ["Field", "Meaning"],
        "fields": ["Speed of the segment in km/h (OSM <code>maxspeed</code> or a default).",
                   "Estimated time to travel the segment, in seconds.",
                   "<code>true</code> when the route uses the segment against traffic (only "
                   "with <i>Ignore one-way streets</i>).",
                   "Route length in km, estimated time in minutes and metres driven the "
                   "wrong way.",
                   "Time threshold of the polygon, its area in km² and the length of reached "
                   "roads in km (two-way streets counted once).",
                   "Arrival time in minutes at the start and at the end of a reached road "
                   "segment."],
        "py_h": "Automation with Python",
        "py_intro": "Every algorithm has a stable id; enum parameters take the position of "
                    "the option (0, 1, 2…).",
        "how_k": "How it works", "how_h": "Assumptions that change the result",
        "how_intro": "Knowing these choices helps to judge whether a result is reasonable.",
        "how": [
            ("Attaching points to the network",
             "Each point is attached to the nearest node of the network, measured in a local "
             "metric CRS. For cars, only nodes of the <b>largest strongly connected "
             "component</b> are candidates — nodes from which every other node can be "
             "reached and back, respecting one-way streets — so a route always exists. For "
             "pedestrians, the largest connected component is used. A point on an isolated "
             "street therefore attaches to the nearest node of the main network, which may "
             "be some distance away. Points more than 5 km from any candidate node are "
             "rejected (routes) or skipped (isochrones)."),
            ("Distance or time",
             "<i>Shortest distance</i> sums the length of the segments; <i>fastest</i> sums "
             "<code>travel_time</code>. The fastest route is the one with the lowest "
             "<i>estimated</i> time, not a guarantee of the shortest real trip. For "
             "pedestrians the speed is constant, so both criteria give the same path."),
            ("Speeds",
             "<code>travel_time</code> = length ÷ speed. The speed is the OSM "
             "<code>maxspeed</code> tag when present; otherwise a default per road type "
             "(motorway 100, primary 60, secondary 50, tertiary 40, residential 30, service "
             "20, living street 10 km/h); other types use the mean of tagged roads of the "
             "same type, or 30 km/h. These are urban defaults for free-flowing traffic."),
            ("One-way streets",
             "The <code>arcs</code> layer holds one feature per direction of travel: a "
             "two-way street gives two arcs, a one-way street one arc. Cars only use arcs; "
             "pedestrians walk both ways. How correct this is depends on the "
             "<code>oneway</code> tags in OpenStreetMap."),
        ],
        "arcs": ["two-way street", "2 arcs", "one-way street", "1 arc"],
        "legend": ["route", "wrong way", "origin", "destination"],
        "dir_side": "<i>Ignore one-way streets</i> adds the missing reverse arcs and marks them "
                    "<code>wrong_way</code>. It shows the error an undirected graph would make; "
                    "its result is not a route to drive.",
        "oneway_alt": "Two maps of the same trip: on the left the car route follows one-way "
                      "streets and is longer; on the right, ignoring them, it is shorter but "
                      "uses a segment against traffic, drawn dashed in black",
        "oneway_left": "<b>Car, one-way respected</b> — the route is longer.",
        "oneway_right": "<b>Ignoring one-way streets</b> — shorter, but the dashed black "
                        "segment is driven the wrong way.",
        "how2": [
            ("From or to the points",
             "<i>From the points</i> answers “how far can I get from here in 10 minutes?”. "
             "<i>To the points</i> answers “from where can people get here in 10 minutes?”: "
             "the calculation runs on the reversed graph. The two differ only for cars, "
             "because of one-way streets."),
            ("One isochrone per point or a combined coverage",
             "With one isochrone per point, every point gets its own polygons, which may "
             "overlap. The combined coverage starts from all points at once: each street "
             "gets the time of the point that reaches it <i>fastest along the network</i> "
             "(not the point that is closest in a straight line), and one polygon per time "
             "is produced."),
        ],
        "cov_alt": "Walking isochrones of 5, 10 and 15 minutes around four sample points, each "
                   "with its own overlapping polygons",
        "cov_cap": "Walking isochrones (5, 10, 15 min) of four sample points "
                   "(think of schools), one per point.",
        "how3": [
            ("Polygon methods",
             "<b>Band around the reached roads</b>: every reached segment is buffered by "
             "the band width; the last segment of each path is cut in proportion to the "
             "remaining time, assuming constant speed along it. The polygon follows the "
             "network. <b>Concave hull</b>: a smoother outline around the reached nodes and "
             "cut ends. It is easier to read, but its interior includes places the network "
             "does not reach (blocks, water, fenced areas)."),
        ],
        "meth_alt": "The same isochrone drawn with the two methods: on the left narrow bands "
                    "along the streets, on the right smoother concave outlines",
        "meth_left": "<b>Band around the reached roads</b> — follows the network.",
        "meth_right": "<b>Concave hull</b> — smoother; the interior is not all reachable.",
        "roads_alt": "Street segments coloured by walking arrival time, from blue (near) to "
                     "red (far)",
        "roads_cap": "<b>Reached roads</b>: estimated walking arrival time on every street "
                     "segment, from a point in Tambaú, by the sea.",
        "near": "near", "far": "far",
        "cache_h": "Loading and cache",
        "cache": "The first calculation on a GeoPackage reads it and builds the graphs; the "
                 "next ones reuse them while QGIS is open. If the file changes on disk it "
                 "is read again. Only one network is kept in memory at a time.",
        "gloss_h": "Glossary",
        "gloss": [
            ("OpenStreetMap (OSM)", "Collaborative geographic database. Coverage and detail "
                                    "vary between places and are not uniformly complete or "
                                    "up to date."),
            ("OSMnx", "Python library the plugin uses to download OSM networks and turn them "
                      "into graphs."),
            ("Nominatim / Overpass", "OSM services that find a place by name (geocoding) and "
                                     "return the map data inside an area."),
            ("GeoPackage", "Single <code>.gpkg</code> file that can hold several vector "
                           "layers and tables."),
            ("CRS", "Coordinate reference system: how a layer's coordinates relate to places "
                    "on Earth. The network is stored in EPSG:4326 (longitude/latitude); "
                    "distances are measured in a local metric CRS (UTM)."),
            ("Node", "Point of the network: an intersection or the end of a street."),
            ("Edge (segment)", "Piece of street between two nodes, used for display."),
            ("Directed arc", "Segment with one direction of travel. A two-way street is two "
                             "arcs; a one-way street, one arc in the allowed direction."),
            ("Directed graph", "Network in which every connection has a direction; needed to "
                               "model one-way streets."),
            ("Shortest path", "Path with the lowest total cost; the cost is distance or "
                              "estimated time."),
            ("Strongly connected component", "Largest set of nodes in which every node can "
                                             "reach every other one following the arc "
                                             "directions."),
            ("Isochrone", "Area estimated as reachable within a time limit along the network "
                          "and profile chosen. The polygon is a map representation."),
            ("Concave hull", "Outline that fits a set of points more closely than a convex "
                             "hull. It represents the data; it does not prove access to every "
                             "place inside."),
        ],
        "faq_k": "Help", "faq_h": "Troubleshooting",
        "faq_intro": "Each entry gives the likely cause and what to do.",
        "cause_l": "Likely cause", "action_l": "What to do",
        "faq": [
            ("The algorithms are disabled, or “Missing Python libraries”",
             "OSMnx (or another library) is not found in QGIS's Python.",
             "Follow the <a href='#install'>Install</a> steps, restart QGIS and run the "
             "verification code."),
            ("“No result for …” or “no boundary polygon”",
             "Nominatim did not find the place, or found it as a point or a line (a street, "
             "a point of interest).",
             "Write the name as in OpenStreetMap with state and country, and use a "
             "municipality, district or neighbourhood. Searching the name on "
             "openstreetmap.org shows what Nominatim finds."),
            ("The download fails or times out",
             "The area is large, the OSM servers are busy, the connection is slow or a proxy "
             "is required.",
             "Try again later or with a smaller place; check the proxy in <i>Settings → "
             "Options → Network</i>. Do not repeat the request in quick succession."),
            ("“… km from the road network”",
             "The point is more than 5 km from the network: outside the downloaded area, or "
             "in a layer whose CRS is wrong.",
             "Click inside the area of the GeoPackage, check the CRS of the point layer, or "
             "download a larger place."),
            ("“Origin and destination snap to the same network node”",
             "Both points attach to the same node (they are very close, or both lie on an "
             "isolated street).",
             "Pick points farther apart."),
            ("The route takes an odd street or starts away from my click",
             "The click attached to a node of the main network some distance away, or "
             "one-way tags are missing or wrong in OSM.",
             "Read the warnings in the log, look at the <code>arcs</code> layer around the "
             "point and, if the data is wrong, consider fixing it in OpenStreetMap and "
             "downloading again."),
            ("Pedestrian isochrones look too small",
             "The network was downloaded as <code>drive</code> and has no footpaths.",
             "Download the place again with <code>walk</code> or <code>all</code>."),
            ("I saved the layers into another GeoPackage",
             "Saving temporary layers may drop the CRS and add a prefix to the names.",
             "This works: prefixed names (<code>patos_nodes</code>…) are recognised and "
             "lon/lat layers without a CRS are taken as EPSG:4326 (the log says so). Keep "
             "one network per GeoPackage."),
        ],
        "report_h": "Reporting a problem",
        "report": "Open an <a href='" + REPO + "/issues'>issue</a> with: the plugin version "
                  "(Plugin Manager), the QGIS version and operating system (<i>Help → "
                  "About</i>), the place and network type, and the full message from the "
                  "panel, the <i>Log</i> tab of the dialog or <i>View → Panels → Log "
                  "Messages</i>.",
        "author_k": "About the author", "author_h": "Marcello Benigno",
        "author_role": "Lecturer in the Geoprocessing Technology programme at the Federal "
                       "Institute of Paraíba (IFPB), Brazil.",
        "author_bio": [
            "Marcello Benigno holds a master's degree in Geodetic Sciences and Geoinformation "
            "Technologies from UFPE and a degree in Civil Engineering from UFCG. For more than "
            "20 years he has taught and developed open source geospatial solutions.",
            "His work covers Web GIS development and spatial automation with Python — "
            "especially PyQGIS, OSMnx, NetworkX and Django —, geographic database modelling "
            "and Linux-based architectures. This experience guides the development of tools "
            "that bring spatial analysis and geoprocessing into the QGIS ecosystem."],
        "author_photo": "Photo of Marcello Benigno",
        "footer_data": "Map data © OpenStreetMap contributors (ODbL). Figures made with the "
                       "plugin on the network of João Pessoa, Paraíba, Brazil.",
        "footer_license": "Plugin licensed under GPL-2.0-or-later.",
    },
    # ================================================================== Português
    "pt-br": {
        "title": "OSMnx Routing & Isochrones — plugin para QGIS",
        "description": "Plugin do QGIS que baixa redes viárias do OpenStreetMap e calcula, "
                       "localmente, rotas que respeitam a mão das ruas e isócronas, sem API "
                       "de roteamento.",
        "copy": "Copiar",
        "nav": ["Visão geral", "Instalação", "Primeiros passos", "Ferramentas", "Algoritmos",
                "Como funciona", "Ajuda", "Autor"],
        "hero_h1": "Rotas e isócronas do OpenStreetMap, dentro do QGIS",
        "hero_lead": "Baixe uma vez a rede viária de um lugar, salve-a num GeoPackage e calcule "
                     "rotas que respeitam a mão das ruas e as áreas alcançáveis num dado "
                     "tempo — no seu computador, sem serviço de roteamento nem chave de API. "
                     "Os resultados são estimativas baseadas nos dados do OpenStreetMap de "
                     "cada lugar.",
        "hero_badges": ["QGIS 3.34+ (testado)", "OSMnx 2.x", "Interface PT-BR · EN · ES",
                        "GPL-2.0"],
        "hero_install": "Instalar o plugin", "hero_github": "Código no GitHub",
        "hero_alt": "Mapa de João Pessoa (PB) com isócronas de carro de 2, 4, 6 e 8 minutos, do "
                    "verde (perto) ao vermelho (longe)",
        "before_h": "Antes de começar",
        "before": "Para baixar uma rede é preciso conexão com a internet: o lugar é "
                  "localizado pelo Nominatim e as ruas vêm do Overpass, dois serviços do "
                  "OpenStreetMap. Depois que o GeoPackage está salvo no computador, rotas e "
                  "isócronas rodam localmente. Os resultados dependem da cobertura e dos "
                  "atributos disponíveis no OpenStreetMap, que variam de um lugar para outro.",
        "feat_k": "Visão geral", "feat_h": "O que o plugin faz",
        "feat_intro": "Quatro algoritmos de Processamento e duas ferramentas interativas no "
                      "mapa, construídos sobre o <a href='https://osmnx.readthedocs.io/'>OSMnx"
                      "</a> (download e manipulação do grafo) e o NetworkX (menores caminhos).",
        "features": [
            ("🗺️", "t-green", "Sua própria rede",
             "Transforma o nome de um lugar num GeoPackage com nós, trechos de rua, arcos "
             "dirigidos e o limite do lugar."),
            ("↪️", "t-red", "Mão e contramão",
             "As rotas de carro seguem o sentido de circulação registrado no OSM. Um modo de "
             "comparação mostra onde um grafo não dirigido andaria na contramão."),
            ("⏱️", "t-orange", "Isócronas",
             "Áreas estimadas como alcançáveis em 5, 10, 15… minutos saindo dos pontos ou "
             "chegando a eles, com o tempo de chegada em cada rua alcançada."),
            ("🖱️", "t-blue", "Clique no mapa",
             "Painéis laterais deixam o mapa visível: clique os pontos, mova e dê zoom à "
             "vontade; o cálculo roda em segundo plano."),
        ],
        "notdo_h": "O que ele não faz",
        "notdo": ["trânsito em tempo real ou histórico, semáforos e tempo de conversão;",
                  "restrições de conversão, barreiras e regras de acesso dentro da rede baixada "
                  "(só o tipo de rede filtra as vias no download);",
                  "transporte público ou viagens multimodais;",
                  "navegação curva a curva: a rota calculada não é uma rota legal ou "
                  "recomendada para dirigir."],
        "choose_h": "Qual ferramenta devo usar?",
        "choose_cols": ["Quero…", "Use", "Resultado"],
        "choose_rows": [
            ("trabalhar num lugar novo", "1. Baixar malha viária (OSM)",
             "um GeoPackage com a rede (precisa de internet)"),
            ("conferir um GeoPackage antes de usar", "2. Inspecionar GeoPackage da malha",
             "um relatório HTML: SRC, campos, preenchimento, diagnóstico de roteamento"),
            ("testar uma rota clicando", "Rota no mapa (barra de ferramentas)",
             "linha da rota, dois pontos, distância e tempo no painel"),
            ("calcular muitas rotas ou usar num modelo", "3. Menor caminho (Processamento)",
             "camada da rota e as saídas DISTANCE_KM / TIME_MIN"),
            ("ver o que se alcança a partir de lugares, ou até eles", "Isócronas no mapa, ou "
             "4. Isócronas (Processamento) para uma camada de pontos",
             "polígonos das isócronas, vias alcançadas e os pontos usados"),
        ],
        "paths_note": "As ferramentas no mapa e os algoritmos de Processamento são <b>dois "
                      "caminhos para o mesmo cálculo</b>: os painéis servem para explorar "
                      "clicando; os algoritmos servem para camadas de pontos, <i>Executar "
                      "como processo em lote</i>, o Modelador Gráfico e scripts Python.",
        "inst_k": "Instalação", "inst_h": "Instalar, reiniciar, verificar",
        "inst_intro": "O QGIS já traz geopandas, networkx, shapely e pyproj. O OSMnx precisa "
                      "ser acrescentado ao ambiente Python <i>que o QGIS usa</i>, que em geral "
                      "não é o mesmo de outras instalações de Python do computador.",
        "req_h": "Requisitos e versões testadas",
        "req": ["Mínimo declarado: QGIS 3.28. Os testes automáticos rodam no Linux com QGIS "
                "3.34, a LTR atual e a versão mais recente; o plugin também foi testado à "
                "mão no QGIS 3.44 (macOS). O Windows ainda não foi testado.",
                "OSMnx 2.x (testado com o 2.1), que exige geopandas 1.0 ou mais novo.",
                "Internet só para baixar redes; rotas e isócronas funcionam offline a partir "
                "do GeoPackage.",
                "Sem permissão de administrador: <code>--user</code> instala na sua pasta "
                "pessoal."],
        "inst_steps": [
            ("Instale o OSMnx no Python do QGIS",
             "Abra <b>Complementos → Console Python</b>, cole o código abaixo e tecle Enter. "
             "O <code>--no-deps</code> preserva as bibliotecas que vieram com o QGIS (veja "
             "abaixo)."),
            ("Reinicie o QGIS e verifique",
             "Depois de reiniciar, rode isto no Console Python. A primeira linha mostra qual "
             "Python está em uso; a segunda deve imprimir as versões, sem erros."),
            ("Instale o plugin",
             "<b>Complementos → Gerenciar e instalar complementos</b>, procure por <b>OSMnx "
             "Routing &amp; Isochrones</b>. Enquanto for experimental, marque <i>Mostrar "
             "também os complementos experimentais</i> nas Configurações. Também dá para usar "
             "<i>Instalar a partir do ZIP</i> com um arquivo das <a href='" + REPO +
             "/releases'>releases</a>. Depois confira se <b>OSMnx Routing &amp; "
             "Isochrones</b> aparece na Caixa de Ferramentas de Processamento."),
        ],
        "inst_more": [
            ("Por que <code>--no-deps</code>, e quando deixá-lo de fora?",
             "O OSMnx depende de numpy, pandas, geopandas, networkx, shapely e requests, que "
             "o QGIS normalmente já fornece. Sem <code>--no-deps</code>, o pip pode "
             "substituí-los por versões para as quais os módulos do próprio QGIS (GDAL, "
             "scipy) não foram compilados, gerando erros difíceis de rastrear. Se a "
             "verificação mostrar <code>ModuleNotFoundError</code> de outro pacote, ou um "
             "geopandas anterior ao 1.0 (pacotes antigos do Linux), instale só esse pacote "
             "do mesmo jeito, por exemplo <code>pip([\"install\", \"--user\", \"--no-deps\", "
             "\"requests\"])</code>, ou, em último caso, rode o comando sem "
             "<code>--no-deps</code>."),
            ("Como sei se o pip instalou no Python do QGIS?",
             "Rode o comando no Console Python do próprio QGIS, não num terminal. O "
             "<code>sys.prefix</code> da verificação deve apontar para dentro da instalação "
             "do QGIS (ex.: <code>/Applications/QGIS.app/…</code>, <code>C:\\Program "
             "Files\\QGIS …</code> ou <code>/usr</code> nos pacotes do Linux). Se o OSMnx é "
             "encontrado no terminal mas não no QGIS, ele foi para outro Python."),
            ("O <code>--user</code> não funciona",
             "Num ambiente conda ou virtual o pip recusa o <code>--user</code>: retire-o do "
             "comando. Em Debian/Ubuntu recentes, o pip pode parar com "
             "<code>externally-managed-environment</code>; acrescentar "
             "<code>\"--break-system-packages\"</code> à lista é aceitável aqui, porque o "
             "<code>--user</code> só grava na sua pasta pessoal. Com o instalador OSGeo4W no "
             "Windows, também dá para usar o <i>OSGeo4W Shell</i>: "
             "<code>python -m pip install --no-deps osmnx</code>."),
        ],
        "inst_note": "Enquanto faltar alguma biblioteca, o plugin mostra uma mensagem com o "
                     "botão <b>Como instalar</b> e os algoritmos ficam desativados; a mensagem "
                     "também vai para <i>Exibir → Painéis → Mensagens de log</i>, aba "
                     "<i>OSMnx Routing</i>.",
        "qs_k": "Primeiros passos", "qs_h": "Do nome de um lugar ao mapa",
        "qs_intro": "Um primeiro uso completo em Cabedelo (PB), cidade pequena do litoral: o "
                    "download leva menos de um minuto numa conexão comum.",
        "qs_steps": [
            ("Baixe a rede viária",
             "Caixa de Ferramentas de Processamento (<code>Ctrl+Alt+T</code>) → <b>OSMnx "
             "Routing &amp; Isochrones → 1. Baixar malha viária (OSM)</b>. Digite "
             "<i>Cabedelo, Paraíba, Brasil</i>, escolha <i>drive</i> e salve num arquivo (não "
             "numa saída temporária). <b>Resultado esperado:</b> quatro camadas no projeto — "
             "<code>…_boundary</code>, <code>…_edges</code>, <code>…_nodes</code>, "
             "<code>…_arcs</code>."),
            ("Confira o que veio (opcional)",
             "<b>2. Inspecionar GeoPackage da malha</b> gera um relatório HTML. "
             "<b>Resultado esperado:</b> SRC EPSG:4326 e a camada <code>arcs</code> como "
             "fonte do sentido."),
            ("Clique uma rota",
             "Botão <b>Rota no mapa</b> na barra: clique a origem e depois o destino. "
             "<b>Resultado esperado:</b> uma linha vermelha e, no painel, a distância e o "
             "tempo estimado."),
            ("Clique isócronas",
             "Botão <b>Isócronas no mapa</b>: clique um ponto. <b>Resultado esperado:</b> "
             "polígonos de 5, 10 e 15 minutos, do verde ao vermelho, e suas áreas no painel."),
        ],
        "wf": ["Nome do lugar", "1. Baixar", "GeoPackage", "nós · trechos · arcos · limite",
               "2. Inspecionar", "Relatório HTML", "3. Menor caminho", "Rota",
               "4. Isócronas", "Áreas de alcance"],
        "tools_k": "Ferramentas no mapa", "tools_h": "Clique no mapa com pan e zoom livres",
        "tools_intro": "As duas ferramentas abrem um painel lateral que não cobre o mapa. "
                       "Clique marca um ponto, arrastar move o mapa, a roda do mouse dá zoom, "
                       "botão direito ou <code>Esc</code> limpa. O GeoPackage da rede vem das "
                       "camadas já abertas no projeto; também dá para escolhê-lo no painel.",
        "route_h": "Rota no mapa",
        "route_p": "Primeiro clique = <b style='color:#1a9641'>origem</b>, segundo = "
                   "<b style='color:#d62728'>destino</b>; a rota é então calculada em "
                   "segundo plano. <b>Inverter</b> troca o sentido; um terceiro clique "
                   "começa nova origem. Os cliques ficam na camada <i>Pontos da rota</i>.",
        "route_cap": "O painel de rota ao lado do mapa, com a distância e o tempo estimado.",
        "iso_h": "Isócronas no mapa",
        "iso_p": "Cada clique acrescenta um ponto (P1, P2…) à camada <i>Pontos das "
                 "isócronas</i> e as isócronas são recalculadas — desmarque <i>Calcular após "
                 "cada clique</i> para marcar vários pontos antes. O painel lista a área de "
                 "cada faixa de tempo.",
        "iso_cap": "O painel de isócronas: tempos, sentido, método e a área de cada faixa.",
        "tools_tip": "A cada execução o resultado anterior é substituído; marque <b>Manter "
                     "resultados anteriores</b> para comparar cenários lado a lado.",
        "tools_stop": "<b>Como interromper um cálculo.</b> As ferramentas no mapa rodam como "
                      "tarefas em segundo plano do QGIS: cancele pela barra de progresso no "
                      "rodapé da janela do QGIS. Num diálogo de Processamento, use "
                      "<b>Cancelar</b>. Os erros aparecem no painel ou na aba <i>Log</i> do "
                      "diálogo.",
        "shots_note": "Capturas de tela: plugin 0.1, QGIS 3.44, interface em português.",
        "alg_k": "Referência", "alg_h": "Os quatro algoritmos de Processamento",
        "alg_intro": "Funcionam no diálogo, em <i>Executar como processo em lote</i>, no "
                     "Modelador Gráfico e pelo Python. Todos os blocos seguem a mesma ordem: "
                     "quando usar, entradas, saídas, como interpretar o resultado e "
                     "limitações.",
        "param": "Parâmetro", "desc": "Descrição", "outputs": "Saídas",
        "use_l": "Use quando", "read_l": "Como interpretar", "limits_l": "Limitações",
        "algs": [
            ("1. Baixar malha viária (OSM)", "osmnx_routing:download_network", "icon",
             "var(--green)",
             "você precisa da rede de um lugar que ainda não baixou.",
             [("Nome do lugar", "Município, distrito ou bairro com estado e país, ex.: "
                                "<i>Campina Grande, Paraíba, Brasil</i>. O Nominatim localiza "
                                "o lugar e o polígono do limite restringe o download."),
              ("Tipo de rede", "<code>drive</code> vias públicas para carro · "
                               "<code>drive_service</code> mais vias de serviço · "
                               "<code>walk</code> rede de pedestres · <code>bike</code> rede "
                               "cicloviária · <code>all_public</code> todas as vias públicas "
                               "· <code>all</code> incluindo as privadas. Escolha uma "
                               "compatível com o perfil que vai usar."),
              ("GeoPackage de saída", "Arquivo a gravar. Uma saída temporária é apagada ao "
                                      "fechar o QGIS; o log avisa.")],
             "Camadas <code>edges</code> (uma linha por trecho de rua, para exibição), "
             "<code>arcs</code> (uma linha por sentido de circulação, usada no roteamento), "
             "<code>nodes</code> e <code>boundary</code> (com a consulta, o nome no OSM e a "
             "data do download). Os trechos trazem <code>speed_kph</code> e "
             "<code>travel_time</code>.",
             "O log informa o número de nós e arcos. Exiba <code>edges</code> sobre um mapa "
             "de fundo para ver se as ruas de que você precisa estão lá.",
             "Precisa de internet; usa o proxy HTTP definido em <i>Configurações → Opções → "
             "Rede</i>. Lugares grandes podem levar vários minutos e o Overpass pode recusar "
             "consultas pesadas. Respeite as políticas de uso do Nominatim e do Overpass: "
             "evite repetir pedidos em sequência rápida. Pedidos idênticos são respondidos "
             "pelo cache do OSMnx em <code>~/osmnx/cache</code>."),
            ("2. Inspecionar GeoPackage da malha", "osmnx_routing:inspect_network", "icon",
             "var(--blue)",
             "você recebeu ou editou um GeoPackage e quer conferi-lo antes do roteamento. "
             "Só precisa do QGIS, não do OSMnx.",
             [("GeoPackage da malha", "Qualquer GeoPackage; as camadas podem ter prefixo "
                                      "(<code>patos_nodes</code>…)."),
              ("Relatório", "Arquivo HTML a gravar.")],
             "Um relatório HTML que abre no navegador: SRC, geometria, extensão, campos com a "
             "proporção de valores preenchidos, uma amostra e um diagnóstico de roteamento.",
             "Pouco preenchimento de <code>maxspeed</code> significa que a maior parte dos "
             "tempos vem das velocidades padrão. A fonte do sentido deve ser a camada "
             "<code>arcs</code>.",
             "Descreve os dados; não os corrige."),
            ("3. Menor caminho (mão e contramão)", "osmnx_routing:shortest_path", "route",
             "var(--red)",
             "você precisa do caminho entre dois pontos, do comprimento e do tempo estimado.",
             [("Perfil", "Carro — segue a mão das ruas · Pedestre — ignora o sentido."),
              ("Critério", "<i>Menor distância</i> minimiza o comprimento em metros. <i>Mais "
                           "rápido</i> (carro) minimiza o <code>travel_time</code>, uma "
                           "estimativa a partir das velocidades; veja <a "
                           "href='#how-it-works'>Como funciona</a>."),
              ("Origem, Destino", "Pontos em qualquer SRC. Cada um é ligado ao nó mais "
                                  "próximo da rede, como explicado abaixo."),
              ("Ignorar mão única", "Só para comparação ou diagnóstico: permite a contramão "
                                    "e marca esses trechos."),
              ("Velocidade a pé", "km/h, padrão 4,8.")],
             "Linhas da <b>Rota</b> com ordem, nome da rua, tipo de via, mão única, "
             "<code>wrong_way</code>, comprimento, velocidade, tempo e acumulados; <b>Pontos "
             "da rota</b>; os números DISTANCE_KM, TIME_MIN e WRONG_WAY_M.",
             "Compare a rota com o mapa de fundo. O log avisa quando um ponto fica a mais de "
             "150 m do seu nó: a rota então começa ou termina nesse nó, não no clique.",
             "O tempo não inclui trânsito, semáforos nem tempo de conversão, e as restrições "
             "de conversão não são aplicadas. As regras de mão única são tão completas "
             "quanto as etiquetas do OSM."),
            ("4. Isócronas (áreas de alcance)", "osmnx_routing:isochrones", "isochrones",
             "var(--orange)",
             "você quer a área que se alcança em alguns minutos a partir de pontos (ou de "
             "onde se chega até eles).",
             [("Ponto / Camada de pontos", "Um ponto clicado, uma camada (escolas, UBS…) ou "
                                           "ambos; o campo de nome identifica cada ponto."),
              ("Uma isócrona por ponto", "Marcado: um conjunto de polígonos por ponto. "
                                         "Desmarcado: uma cobertura combinada de todos os "
                                         "pontos."),
              ("Sentido (carro)", "<i>Saindo</i> dos pontos (até onde se chega) ou "
                                  "<i>chegando</i> a eles (de onde se chega)."),
              ("Tempos em minutos", "ex.: <code>5, 10, 15</code> (também "
                                    "<code>5;10;15</code>)."),
              ("Método do polígono", "Faixa ao redor das vias alcançadas, ou envoltória "
                                     "côncava dos nós alcançados."),
              ("Largura da faixa", "Metros ao redor das vias, padrão 40.")],
             "<b>Isócronas</b> (source, minutes, area_km2, roads_km), <b>Vias alcançadas</b> "
             "com tempo de chegada inicial e final, <b>Pontos das isócronas</b>.",
             "Leia os polígonos junto com as <b>Vias alcançadas</b>: o polígono é uma "
             "representação cartográfica; a camada de vias mostra o que a rede de fato "
             "alcança.",
             "Os mesmos limites das rotas. Uma isócrona de pedestre numa rede "
             "<code>drive</code> não tem calçadas nem caminhos: baixe <code>walk</code> ou "
             "<code>all</code> para estudos a pé."),
        ],
        "fields_h": "Campos e saídas",
        "fields_cols": ["Campo", "Significado"],
        "fields": ["Velocidade do trecho em km/h (<code>maxspeed</code> do OSM ou um "
                   "padrão).",
                   "Tempo estimado para percorrer o trecho, em segundos.",
                   "<code>true</code> quando a rota usa o trecho na contramão (só com "
                   "<i>Ignorar mão única</i>).",
                   "Comprimento da rota em km, tempo estimado em minutos e metros feitos na "
                   "contramão.",
                   "Limite de tempo do polígono, sua área em km² e o comprimento das vias "
                   "alcançadas em km (ruas de mão dupla contadas uma vez).",
                   "Tempo de chegada em minutos no início e no fim de um trecho alcançado."],
        "py_h": "Automação com Python",
        "py_intro": "Cada algoritmo tem um id estável; os parâmetros de lista recebem a "
                    "posição da opção (0, 1, 2…).",
        "how_k": "Como funciona", "how_h": "Pressupostos que mudam o resultado",
        "how_intro": "Conhecer estas escolhas ajuda a julgar se um resultado é razoável.",
        "how": [
            ("Ligação dos pontos à rede",
             "Cada ponto é ligado ao nó mais próximo da rede, medido num SRC métrico local. "
             "Para carro, só concorrem os nós do <b>maior componente fortemente conexo</b> — "
             "nós a partir dos quais se chega a qualquer outro e se volta, respeitando a mão "
             "das ruas —, de modo que sempre existe rota. Para pedestre, usa-se o maior "
             "componente conexo. Por isso, um ponto numa rua isolada é ligado ao nó mais "
             "próximo da rede principal, que pode estar a alguma distância. Pontos a mais de "
             "5 km de qualquer nó candidato são recusados (rotas) ou ignorados (isócronas)."),
            ("Distância ou tempo",
             "<i>Menor distância</i> soma o comprimento dos trechos; <i>mais rápido</i> soma "
             "o <code>travel_time</code>. A rota mais rápida é a de menor tempo "
             "<i>estimado</i>, não uma garantia da viagem real mais curta. Para pedestre a "
             "velocidade é constante, então os dois critérios dão o mesmo caminho."),
            ("Velocidades",
             "<code>travel_time</code> = comprimento ÷ velocidade. A velocidade é a etiqueta "
             "<code>maxspeed</code> do OSM quando existe; senão, um padrão por tipo de via "
             "(motorway 100, primary 60, secondary 50, tertiary 40, residential 30, service "
             "20, living_street 10 km/h); os demais tipos usam a média das vias etiquetadas "
             "do mesmo tipo, ou 30 km/h. São padrões urbanos para trânsito livre."),
            ("Mão única",
             "A camada <code>arcs</code> tem um registro por sentido de circulação: uma rua "
             "de mão dupla gera dois arcos; uma de mão única, um arco. O carro só usa arcos; "
             "o pedestre anda nos dois sentidos. A correção disso depende das etiquetas "
             "<code>oneway</code> do OpenStreetMap."),
        ],
        "arcs": ["rua de mão dupla", "2 arcos", "rua de mão única", "1 arco"],
        "legend": ["rota", "contramão", "origem", "destino"],
        "dir_side": "<i>Ignorar mão única</i> acrescenta os arcos inversos que faltam e os marca "
                    "como <code>wrong_way</code>. Mostra o erro que um grafo não dirigido "
                    "cometeria; o resultado não é uma rota para dirigir.",
        "oneway_alt": "Dois mapas do mesmo trajeto: à esquerda a rota de carro segue a mão das "
                      "ruas e é mais longa; à direita, ignorando-a, é mais curta mas usa um "
                      "trecho na contramão, tracejado em preto",
        "oneway_left": "<b>Carro, respeitando a mão</b> — a rota fica mais longa.",
        "oneway_right": "<b>Ignorando a mão única</b> — mais curta, mas o trecho tracejado "
                        "preto é feito na contramão.",
        "how2": [
            ("Saindo ou chegando",
             "<i>Saindo dos pontos</i> responde “até onde chego daqui em 10 minutos?”. "
             "<i>Chegando aos pontos</i> responde “de onde as pessoas chegam aqui em 10 "
             "minutos?”: o cálculo roda sobre o grafo invertido. Os dois só diferem para "
             "carro, por causa da mão única."),
            ("Uma isócrona por ponto ou cobertura combinada",
             "Com uma isócrona por ponto, cada ponto tem seus próprios polígonos, que podem "
             "se sobrepor. A cobertura combinada parte de todos os pontos ao mesmo tempo: "
             "cada rua recebe o tempo do ponto que a alcança <i>mais rápido pela rede</i> "
             "(não o mais próximo em linha reta), e sai um polígono por tempo."),
        ],
        "cov_alt": "Isócronas a pé de 5, 10 e 15 minutos em torno de quatro pontos, cada um "
                   "com seus polígonos, sobrepostos",
        "cov_cap": "Isócronas a pé (5, 10, 15 min) de quatro pontos de exemplo "
                   "(pense em escolas), uma por ponto.",
        "how3": [
            ("Métodos de polígono",
             "<b>Faixa ao redor das vias alcançadas</b>: cada trecho alcançado recebe um "
             "buffer da largura da faixa; o último trecho de cada caminho é cortado em "
             "proporção ao tempo restante, supondo velocidade constante nele. O polígono "
             "acompanha a rede. <b>Envoltória côncava</b>: um contorno mais suave em torno "
             "dos nós alcançados e das pontas cortadas. É mais fácil de ler, mas o interior "
             "inclui lugares que a rede não alcança (quadras, água, áreas cercadas)."),
        ],
        "meth_alt": "A mesma isócrona desenhada com os dois métodos: à esquerda faixas "
                    "estreitas ao longo das ruas, à direita contornos côncavos mais suaves",
        "meth_left": "<b>Faixa ao redor das vias alcançadas</b> — acompanha a rede.",
        "meth_right": "<b>Envoltória côncava</b> — mais suave; nem todo o interior é "
                      "alcançável.",
        "roads_alt": "Trechos de rua coloridos pelo tempo de chegada a pé, do azul (perto) ao "
                     "vermelho (longe)",
        "roads_cap": "<b>Vias alcançadas</b>: tempo estimado de chegada a pé em cada trecho de "
                     "rua, a partir de um ponto em Tambaú, à beira-mar.",
        "near": "perto", "far": "longe",
        "cache_h": "Leitura e cache",
        "cache": "O primeiro cálculo sobre um GeoPackage lê o arquivo e monta os grafos; os "
                 "seguintes os reaproveitam enquanto o QGIS estiver aberto. Se o arquivo mudar "
                 "no disco, ele é lido de novo. Só uma rede fica na memória por vez.",
        "gloss_h": "Glossário",
        "gloss": [
            ("OpenStreetMap (OSM)", "Base colaborativa de dados geográficos. A cobertura e o "
                                    "detalhe variam entre lugares e não são uniformemente "
                                    "completos nem atualizados."),
            ("OSMnx", "Biblioteca Python que o plugin usa para baixar redes do OSM e "
                      "transformá-las em grafos."),
            ("Nominatim / Overpass", "Serviços do OSM que encontram um lugar pelo nome "
                                     "(geocodificação) e devolvem os dados do mapa dentro de "
                                     "uma área."),
            ("GeoPackage", "Arquivo único <code>.gpkg</code> que pode guardar várias camadas "
                           "vetoriais e tabelas."),
            ("SRC", "Sistema de referência de coordenadas: como as coordenadas de uma camada "
                    "se relacionam com lugares na Terra. A rede é gravada em EPSG:4326 "
                    "(longitude/latitude); as distâncias são medidas num SRC métrico local "
                    "(UTM)."),
            ("Nó", "Ponto da rede: um cruzamento ou o fim de uma rua."),
            ("Trecho (edge)", "Pedaço de rua entre dois nós, usado na exibição."),
            ("Arco dirigido", "Trecho com um sentido de circulação. Uma rua de mão dupla são "
                              "dois arcos; uma de mão única, um arco no sentido permitido."),
            ("Grafo dirigido", "Rede em que cada ligação tem um sentido; necessário para "
                               "modelar a mão única."),
            ("Menor caminho", "Caminho de menor custo total; o custo é a distância ou o tempo "
                              "estimado."),
            ("Componente fortemente conexo", "Maior conjunto de nós em que cada nó alcança "
                                             "todos os outros seguindo o sentido dos arcos."),
            ("Isócrona", "Área estimada como alcançável dentro de um limite de tempo, pela "
                         "rede e perfil escolhidos. O polígono é uma representação "
                         "cartográfica."),
            ("Envoltória côncava", "Contorno que se ajusta a um conjunto de pontos mais que a "
                                   "envoltória convexa. Representa os dados; não comprova o "
                                   "acesso a todo lugar do interior."),
        ],
        "faq_k": "Ajuda", "faq_h": "Dúvidas e problemas comuns",
        "faq_intro": "Cada item traz a causa provável e o que fazer.",
        "cause_l": "Causa provável", "action_l": "O que fazer",
        "faq": [
            ("Os algoritmos estão desativados, ou “Bibliotecas Python ausentes”",
             "O OSMnx (ou outra biblioteca) não é encontrado no Python do QGIS.",
             "Siga os passos da <a href='#install'>Instalação</a>, reinicie o QGIS e rode o "
             "código de verificação."),
            ("“Nenhum resultado para …” ou “sem polígono de limite”",
             "O Nominatim não encontrou o lugar, ou o encontrou como ponto ou linha (uma rua, "
             "um ponto de interesse).",
             "Escreva o nome como no OpenStreetMap, com estado e país, e use município, "
             "distrito ou bairro. Pesquisar o nome em openstreetmap.org mostra o que o "
             "Nominatim encontra."),
            ("O download falha ou dá tempo esgotado",
             "A área é grande, os servidores do OSM estão ocupados, a conexão está lenta ou "
             "é preciso um proxy.",
             "Tente mais tarde ou com um lugar menor; confira o proxy em <i>Configurações → "
             "Opções → Rede</i>. Não repita o pedido em sequência rápida."),
            ("“… km da malha viária”",
             "O ponto está a mais de 5 km da rede: fora da área baixada, ou numa camada com "
             "o SRC errado.",
             "Clique dentro da área do GeoPackage, confira o SRC da camada de pontos ou "
             "baixe um lugar maior."),
            ("“Origem e destino caem no mesmo nó da rede”",
             "Os dois pontos se ligam ao mesmo nó (estão muito próximos ou ambos numa rua "
             "isolada).",
             "Escolha pontos mais afastados."),
            ("A rota usa uma rua estranha ou começa longe do clique",
             "O clique foi ligado a um nó da rede principal a alguma distância, ou as "
             "etiquetas de mão única faltam ou estão erradas no OSM.",
             "Leia os avisos do log, observe a camada <code>arcs</code> perto do ponto e, se "
             "o dado estiver errado, considere corrigi-lo no OpenStreetMap e baixar de novo."),
            ("As isócronas a pé parecem pequenas demais",
             "A rede foi baixada como <code>drive</code> e não tem calçadas nem caminhos.",
             "Baixe o lugar de novo com <code>walk</code> ou <code>all</code>."),
            ("Salvei as camadas em outro GeoPackage",
             "Salvar camadas temporárias pode perder o SRC e acrescentar um prefixo aos "
             "nomes.",
             "Funciona: nomes com prefixo (<code>patos_nodes</code>…) são reconhecidos e "
             "camadas lon/lat sem SRC são tratadas como EPSG:4326 (o log avisa). Mantenha uma "
             "rede por GeoPackage."),
        ],
        "report_h": "Como relatar um problema",
        "report": "Abra uma <a href='" + REPO + "/issues'>issue</a> com: a versão do plugin "
                  "(Gerenciador de complementos), a versão do QGIS e o sistema operacional "
                  "(<i>Ajuda → Sobre</i>), o lugar e o tipo de rede, e a mensagem completa do "
                  "painel, da aba <i>Log</i> do diálogo ou de <i>Exibir → Painéis → Mensagens "
                  "de log</i>.",
        "author_k": "Sobre o autor", "author_h": "Marcello Benigno",
        "author_role": "Professor do Curso Superior de Tecnologia em Geoprocessamento do "
                       "Instituto Federal da Paraíba (IFPB).",
        "author_bio": [
            "Marcello Benigno é mestre em Ciências Geodésicas e Tecnologias da Geoinformação "
            "pela UFPE e engenheiro civil pela UFCG. Atua há mais de 20 anos no ensino e no "
            "desenvolvimento de soluções geotecnológicas de código aberto.",
            "Sua experiência inclui desenvolvimento Web GIS e automação espacial com Python — "
            "especialmente PyQGIS, OSMnx, NetworkX e Django —, modelagem de bancos de dados "
            "geográficos e arquiteturas em ambiente Linux. Esse trabalho orienta o "
            "desenvolvimento de ferramentas que integram análise espacial e geoprocessamento "
            "ao ecossistema QGIS."],
        "author_photo": "Foto de Marcello Benigno",
        "footer_data": "Dados © colaboradores do OpenStreetMap (ODbL). Figuras feitas com o "
                       "plugin sobre a rede de João Pessoa, Paraíba, Brasil.",
        "footer_license": "Plugin sob licença GPL-2.0-or-later.",
    },
    # ================================================================== Español
    "es": {
        "title": "OSMnx Routing & Isochrones — complemento de QGIS",
        "description": "Complemento de QGIS que descarga redes viales de OpenStreetMap y "
                       "calcula localmente rutas que respetan el sentido de las calles e "
                       "isócronas, sin API de ruteo.",
        "copy": "Copiar",
        "nav": ["Resumen", "Instalación", "Inicio rápido", "Herramientas", "Algoritmos",
                "Cómo funciona", "Ayuda", "Autor"],
        "hero_h1": "Rutas e isócronas de OpenStreetMap, dentro de QGIS",
        "hero_lead": "Descarga una vez la red vial de un lugar, guárdala en un GeoPackage y "
                     "calcula rutas que respetan el sentido de las calles y las áreas "
                     "alcanzables en un tiempo dado — en tu equipo, sin servicio de ruteo ni "
                     "clave de API. Los resultados son estimaciones basadas en los datos de "
                     "OpenStreetMap de cada lugar.",
        "hero_badges": ["QGIS 3.34+ (probado)", "OSMnx 2.x", "Interfaz ES · EN · PT-BR",
                        "GPL-2.0"],
        "hero_install": "Instalar el complemento", "hero_github": "Código en GitHub",
        "hero_alt": "Mapa de João Pessoa, Brasil, con isócronas en auto de 2, 4, 6 y 8 minutos, "
                    "del verde (cerca) al rojo (lejos)",
        "before_h": "Antes de empezar",
        "before": "Para descargar una red se necesita conexión a internet: el lugar se busca "
                  "con Nominatim y las calles vienen de Overpass, dos servicios de "
                  "OpenStreetMap. Una vez guardado el GeoPackage en tu equipo, las rutas y las "
                  "isócronas se ejecutan localmente. Los resultados dependen de la cobertura y "
                  "de los atributos disponibles en OpenStreetMap, que varían de un lugar a "
                  "otro.",
        "feat_k": "Resumen", "feat_h": "Qué hace el complemento",
        "feat_intro": "Cuatro algoritmos de Procesos y dos herramientas interactivas en el "
                      "mapa, construidos sobre <a href='https://osmnx.readthedocs.io/'>OSMnx"
                      "</a> (descarga y manejo del grafo) y NetworkX (rutas más cortas).",
        "features": [
            ("🗺️", "t-green", "Tu propia red",
             "Convierte el nombre de un lugar en un GeoPackage con nodos, tramos de calle, "
             "arcos dirigidos y el límite del lugar."),
            ("↪️", "t-red", "Sentido de circulación",
             "Las rutas en auto siguen el sentido registrado en OSM. Un modo de comparación "
             "muestra dónde un grafo no dirigido iría a contramano."),
            ("⏱️", "t-orange", "Isócronas",
             "Áreas estimadas como alcanzables en 5, 10, 15… minutos desde los puntos o hacia "
             "ellos, con el tiempo de llegada en cada calle alcanzada."),
            ("🖱️", "t-blue", "Clic en el mapa",
             "Paneles laterales dejan el mapa visible: marca los puntos, desplaza y haz zoom "
             "libremente; el cálculo corre en segundo plano."),
        ],
        "notdo_h": "Lo que no hace",
        "notdo": ["tránsito en tiempo real o histórico, semáforos ni demoras de giro;",
                  "restricciones de giro, barreras y reglas de acceso dentro de la red "
                  "descargada (solo el tipo de red filtra las vías al descargar);",
                  "transporte público ni viajes multimodales;",
                  "navegación paso a paso: una ruta calculada no es una ruta legal ni "
                  "recomendada para conducir."],
        "choose_h": "¿Qué herramienta uso?",
        "choose_cols": ["Quiero…", "Usa", "Obtienes"],
        "choose_rows": [
            ("trabajar en un lugar nuevo", "1. Descargar red vial (OSM)",
             "un GeoPackage con la red (requiere internet)"),
            ("revisar un GeoPackage antes de usarlo", "2. Inspeccionar GeoPackage de la red",
             "un informe HTML: SRC, campos, completitud, diagnóstico de ruteo"),
            ("probar una ruta con clics", "Ruta en el mapa (barra de herramientas)",
             "línea de la ruta, dos puntos, distancia y tiempo en el panel"),
            ("calcular muchas rutas o usar un modelo", "3. Ruta más corta (Procesos)",
             "capa de la ruta y las salidas DISTANCE_KM / TIME_MIN"),
            ("ver qué se alcanza desde lugares o hacia ellos", "Isócronas en el mapa, o "
             "4. Isócronas (Procesos) para una capa de puntos",
             "polígonos de isócronas, calles alcanzadas y los puntos usados"),
        ],
        "paths_note": "Las herramientas en el mapa y los algoritmos de Procesos son <b>dos "
                      "formas de hacer el mismo cálculo</b>: los paneles sirven para explorar "
                      "con clics; los algoritmos, para capas de puntos, <i>Ejecutar como "
                      "proceso por lotes</i>, el Modelador gráfico y scripts de Python.",
        "inst_k": "Instalación", "inst_h": "Instalar, reiniciar, verificar",
        "inst_intro": "QGIS ya incluye geopandas, networkx, shapely y pyproj. OSMnx debe "
                      "añadirse al entorno de Python <i>que usa QGIS</i>, que en general no es "
                      "el mismo que otras instalaciones de Python del equipo.",
        "req_h": "Requisitos y versiones probadas",
        "req": ["Mínimo declarado: QGIS 3.28. Las pruebas automáticas corren en Linux con "
                "QGIS 3.34, la LTR actual y la versión más reciente; el complemento también "
                "se probó a mano en QGIS 3.44 (macOS). Windows aún no se ha probado.",
                "OSMnx 2.x (probado con 2.1), que requiere geopandas 1.0 o más reciente.",
                "Internet solo para descargar redes; rutas e isócronas funcionan sin conexión "
                "a partir del GeoPackage.",
                "Sin permisos de administrador: <code>--user</code> instala en tu carpeta "
                "personal."],
        "inst_steps": [
            ("Instala OSMnx en el Python de QGIS",
             "Abre <b>Complementos → Consola de Python</b>, pega el código y pulsa Enter. "
             "<code>--no-deps</code> conserva las bibliotecas que vienen con QGIS (ver "
             "abajo)."),
            ("Reinicia QGIS y verifica",
             "Tras reiniciar, ejecuta esto en la Consola de Python. La primera línea muestra "
             "qué Python se usa; la segunda debe imprimir las versiones sin errores."),
            ("Instala el complemento",
             "<b>Complementos → Administrar e instalar complementos</b>, busca <b>OSMnx "
             "Routing &amp; Isochrones</b>. Mientras sea experimental, marca <i>Mostrar también "
             "complementos experimentales</i> en Configuración. También puedes usar "
             "<i>Instalar a partir de ZIP</i> con un archivo de las <a href='" + REPO +
             "/releases'>releases</a>. Luego comprueba que <b>OSMnx Routing &amp; "
             "Isochrones</b> aparezca en la Caja de herramientas de Procesos."),
        ],
        "inst_more": [
            ("¿Por qué <code>--no-deps</code> y cuándo quitarlo?",
             "OSMnx depende de numpy, pandas, geopandas, networkx, shapely y requests, que "
             "QGIS normalmente ya trae. Sin <code>--no-deps</code>, pip puede reemplazarlos "
             "por versiones para las que no se compilaron los módulos de QGIS (GDAL, scipy), "
             "con errores difíciles de rastrear. Si la verificación muestra "
             "<code>ModuleNotFoundError</code> de otro paquete, o un geopandas anterior a 1.0 "
             "(paquetes antiguos de Linux), instala solo ese paquete de la misma forma, p. ej. "
             "<code>pip([\"install\", \"--user\", \"--no-deps\", \"requests\"])</code>, o, "
             "como último recurso, ejecuta el comando sin <code>--no-deps</code>."),
            ("¿Cómo sé si pip instaló en el Python de QGIS?",
             "Ejecuta el comando en la Consola de Python de QGIS, no en una terminal. "
             "<code>sys.prefix</code> en la verificación debe apuntar dentro de la "
             "instalación de QGIS (p. ej. <code>/Applications/QGIS.app/…</code>, "
             "<code>C:\\Program Files\\QGIS …</code> o <code>/usr</code> en los paquetes de "
             "Linux). Si OSMnx aparece en una terminal pero no en QGIS, se instaló en otro "
             "Python."),
            ("<code>--user</code> no funciona",
             "En un entorno conda o virtual pip rechaza <code>--user</code>: quítalo del "
             "comando. En Debian/Ubuntu recientes, pip puede detenerse con "
             "<code>externally-managed-environment</code>; añadir "
             "<code>\"--break-system-packages\"</code> a la lista es aceptable aquí porque "
             "<code>--user</code> solo escribe en tu carpeta personal. Con el instalador "
             "OSGeo4W en Windows también puedes usar el <i>OSGeo4W Shell</i>: "
             "<code>python -m pip install --no-deps osmnx</code>."),
        ],
        "inst_note": "Mientras falte una biblioteca, el complemento muestra un mensaje con el "
                     "botón <b>Cómo instalar</b> y sus algoritmos quedan desactivados; el "
                     "mensaje también va a <i>Ver → Paneles → Mensajes de registro</i>, "
                     "pestaña <i>OSMnx Routing</i>.",
        "qs_k": "Inicio rápido", "qs_h": "Del nombre de un lugar al mapa",
        "qs_intro": "Un primer uso completo en Cabedelo, una pequeña ciudad costera de Brasil: "
                    "la descarga tarda menos de un minuto con una conexión normal.",
        "qs_steps": [
            ("Descarga la red vial",
             "Caja de herramientas de Procesos (<code>Ctrl+Alt+T</code>) → <b>OSMnx Routing "
             "&amp; Isochrones → 1. Descargar red vial (OSM)</b>. Escribe <i>Cabedelo, "
             "Paraíba, Brasil</i>, elige <i>drive</i> y guarda en un archivo (no en una salida "
             "temporal). <b>Resultado esperado:</b> cuatro capas en el proyecto — "
             "<code>…_boundary</code>, <code>…_edges</code>, <code>…_nodes</code>, "
             "<code>…_arcs</code>."),
            ("Revisa lo descargado (opcional)",
             "<b>2. Inspeccionar GeoPackage de la red</b> genera un informe HTML. "
             "<b>Resultado esperado:</b> SRC EPSG:4326 y la capa <code>arcs</code> como "
             "fuente del sentido."),
            ("Marca una ruta",
             "Botón <b>Ruta en el mapa</b> de la barra: clic en el origen y luego en el "
             "destino. <b>Resultado esperado:</b> una línea roja y, en el panel, la distancia "
             "y el tiempo estimado."),
            ("Marca isócronas",
             "Botón <b>Isócronas en el mapa</b>: clic en un punto. <b>Resultado esperado:</b> "
             "polígonos de 5, 10 y 15 minutos, del verde al rojo, y sus áreas en el panel."),
        ],
        "wf": ["Nombre del lugar", "1. Descargar", "GeoPackage", "nodos · tramos · arcos · límite",
               "2. Inspeccionar", "Informe HTML", "3. Ruta más corta", "Ruta", "4. Isócronas",
               "Áreas de alcance"],
        "tools_k": "Herramientas en el mapa",
        "tools_h": "Clic en el mapa, con desplazamiento y zoom libres",
        "tools_intro": "Ambas herramientas abren un panel lateral que no tapa el mapa. Un "
                       "clic marca un punto, arrastrar desplaza, la rueda hace zoom, el botón "
                       "derecho o <code>Esc</code> borra. El GeoPackage de la red se toma de "
                       "las capas ya abiertas en el proyecto; también puedes elegirlo en el "
                       "panel.",
        "route_h": "Ruta en el mapa",
        "route_p": "Primer clic = <b style='color:#1a9641'>origen</b>, segundo = "
                   "<b style='color:#d62728'>destino</b>; la ruta se calcula entonces en "
                   "segundo plano. <b>Invertir</b> cambia el sentido; un tercer clic empieza un "
                   "nuevo origen. Los clics quedan en la capa <i>Puntos de la ruta</i>.",
        "route_cap": "El panel de ruta junto al mapa, con la distancia y el tiempo estimado.",
        "iso_h": "Isócronas en el mapa",
        "iso_p": "Cada clic agrega un punto (P1, P2…) a la capa <i>Puntos de las isócronas</i> y las "
                 "isócronas se recalculan — desmarca <i>Calcular después de cada clic</i> para "
                 "marcar varios puntos antes. El panel lista el área de cada franja.",
        "iso_cap": "El panel de isócronas: tiempos, sentido, método y el área de cada franja.",
        "tools_tip": "Cada ejecución reemplaza el resultado anterior; marca <b>Mantener resultados "
                     "anteriores</b> para comparar escenarios.",
        "tools_stop": "<b>Detener un cálculo.</b> Las herramientas en el mapa corren como "
                      "tareas en segundo plano de QGIS: cancélalas desde la barra de progreso "
                      "al pie de la ventana de QGIS. En un diálogo de Procesos, usa "
                      "<b>Cancelar</b>. Los errores aparecen en el panel o en la pestaña "
                      "<i>Registro</i> del diálogo.",
        "shots_note": "Capturas de pantalla: complemento 0.1, QGIS 3.44, interfaz en español.",
        "alg_k": "Referencia", "alg_h": "Los cuatro algoritmos de Procesos",
        "alg_intro": "Funcionan en el diálogo, en <i>Ejecutar como proceso por lotes</i>, en "
                     "el Modelador gráfico y desde Python. Cada bloque sigue el mismo orden: "
                     "cuándo usarlo, entradas, salidas, cómo leer el resultado y "
                     "limitaciones.",
        "param": "Parámetro", "desc": "Descripción", "outputs": "Salidas",
        "use_l": "Úsalo cuando", "read_l": "Cómo leer el resultado",
        "limits_l": "Limitaciones",
        "algs": [
            ("1. Descargar red vial (OSM)", "osmnx_routing:download_network", "icon",
             "var(--green)",
             "necesitas la red de un lugar que aún no descargaste.",
             [("Nombre del lugar", "Municipio, distrito o barrio con estado y país, p. ej. "
                                   "<i>Campina Grande, Paraíba, Brasil</i>. Nominatim lo busca "
                                   "y su polígono de límite acota la descarga."),
              ("Tipo de red", "<code>drive</code> vías públicas para auto · "
                              "<code>drive_service</code> más vías de servicio · "
                              "<code>walk</code> red peatonal · <code>bike</code> red ciclista "
                              "· <code>all_public</code> todas las vías públicas · "
                              "<code>all</code> incluidas las privadas. Elige una acorde al "
                              "perfil que vas a usar."),
              ("GeoPackage de salida", "Archivo a escribir. Una salida temporal se borra al "
                                       "cerrar QGIS; el registro lo advierte.")],
             "Capas <code>edges</code> (una línea por tramo de calle, para visualización), "
             "<code>arcs</code> (una línea por sentido de circulación, para el ruteo), "
             "<code>nodes</code> y <code>boundary</code> (con la consulta, el nombre en OSM y "
             "la fecha de descarga). Los tramos llevan <code>speed_kph</code> y "
             "<code>travel_time</code>.",
             "El registro indica el número de nodos y arcos. Muestra <code>edges</code> sobre "
             "un mapa base para ver si están las calles que necesitas.",
             "Requiere internet; usa el proxy HTTP definido en <i>Configuración → Opciones → "
             "Red</i>. Los lugares grandes pueden tardar varios minutos y Overpass puede "
             "rechazar consultas pesadas. Respeta las políticas de uso de Nominatim y "
             "Overpass: evita repetir pedidos en rápida sucesión. Los pedidos idénticos se "
             "responden desde la caché de OSMnx en <code>~/osmnx/cache</code>."),
            ("2. Inspeccionar GeoPackage de la red", "osmnx_routing:inspect_network", "icon",
             "var(--blue)",
             "recibiste o editaste un GeoPackage y quieres revisarlo antes del ruteo. Solo "
             "necesita QGIS, no OSMnx.",
             [("GeoPackage de la red vial", "Cualquier GeoPackage; las capas pueden tener "
                                            "prefijo (<code>patos_nodes</code>…)."),
              ("Informe", "Archivo HTML a escribir.")],
             "Un informe HTML que se abre en el navegador: SRC, geometría, extensión, campos "
             "con la proporción de valores completos, una muestra y un diagnóstico de ruteo.",
             "Un <code>maxspeed</code> poco completo significa que la mayoría de los tiempos "
             "vienen de velocidades por defecto. La fuente del sentido debe ser la capa "
             "<code>arcs</code>.",
             "Describe los datos; no los corrige."),
            ("3. Ruta más corta (respeta el sentido)", "osmnx_routing:shortest_path", "route",
             "var(--red)",
             "necesitas el camino entre dos puntos, su longitud y su tiempo estimado.",
             [("Perfil", "Auto — sigue el sentido de las calles · Peatón — ignora el "
                         "sentido."),
              ("Criterio", "<i>Menor distancia</i> minimiza la longitud en metros. <i>Más "
                           "rápida</i> (auto) minimiza <code>travel_time</code>, una "
                           "estimación a partir de velocidades; ver <a "
                           "href='#how-it-works'>Cómo funciona</a>."),
              ("Origen, Destino", "Puntos en cualquier SRC. Cada uno se une al nodo más "
                                  "cercano de la red, como se explica abajo."),
              ("Ignorar sentido único", "Solo para comparación o diagnóstico: permite ir a "
                                        "contramano y marca esos tramos."),
              ("Velocidad a pie", "km/h, por defecto 4,8.")],
             "Líneas de la <b>Ruta</b> con orden, nombre de la calle, tipo de vía, sentido "
             "único, <code>wrong_way</code>, longitud, velocidad, tiempo y acumulados; "
             "<b>Puntos de la ruta</b>; los números DISTANCE_KM, TIME_MIN y WRONG_WAY_M.",
             "Compara la ruta con el mapa base. El registro avisa cuando un punto está a más "
             "de 150 m de su nodo: la ruta entonces empieza o termina en ese nodo, no en el "
             "clic.",
             "El tiempo no incluye tránsito, semáforos ni demoras de giro, y no se aplican "
             "restricciones de giro. Las reglas de sentido único son tan completas como las "
             "etiquetas de OSM."),
            ("4. Isócronas (áreas de alcance)", "osmnx_routing:isochrones", "isochrones",
             "var(--orange)",
             "quieres el área alcanzable en algunos minutos desde puntos (o desde la que se "
             "llega a ellos).",
             [("Punto / Capa de puntos", "Un punto marcado, una capa (escuelas, centros de "
                                         "salud…) o ambos; el campo de nombre identifica cada "
                                         "punto."),
              ("Una isócrona por punto", "Marcado: un conjunto de polígonos por punto. "
                                         "Desmarcado: una cobertura combinada de todos los "
                                         "puntos."),
              ("Sentido (auto)", "<i>Desde</i> los puntos (hasta dónde se llega) o "
                                 "<i>hacia</i> ellos (desde dónde se llega)."),
              ("Tiempos en minutos", "p. ej. <code>5, 10, 15</code> (también "
                                     "<code>5;10;15</code>)."),
              ("Método del polígono", "Franja alrededor de las calles alcanzadas, o "
                                      "envolvente cóncava de los nodos alcanzados."),
              ("Ancho de la franja", "Metros alrededor de las calles, por defecto 40.")],
             "<b>Isócronas</b> (source, minutes, area_km2, roads_km), <b>Calles alcanzadas</b> "
             "con tiempo de llegada inicial y final, <b>Puntos de las isócronas</b>.",
             "Lee los polígonos junto con las <b>Calles alcanzadas</b>: el polígono es una "
             "representación cartográfica; la capa de calles muestra lo que la red alcanza "
             "de verdad.",
             "Los mismos límites que las rutas. Una isócrona peatonal sobre una red "
             "<code>drive</code> no tiene veredas ni senderos: descarga <code>walk</code> o "
             "<code>all</code> para estudios a pie."),
        ],
        "fields_h": "Campos y salidas",
        "fields_cols": ["Campo", "Significado"],
        "fields": ["Velocidad del tramo en km/h (<code>maxspeed</code> de OSM o un valor por "
                   "defecto).",
                   "Tiempo estimado para recorrer el tramo, en segundos.",
                   "<code>true</code> cuando la ruta usa el tramo a contramano (solo con "
                   "<i>Ignorar sentido único</i>).",
                   "Longitud de la ruta en km, tiempo estimado en minutos y metros recorridos "
                   "a contramano.",
                   "Umbral de tiempo del polígono, su área en km² y la longitud de calles "
                   "alcanzadas en km (las de doble sentido se cuentan una vez).",
                   "Tiempo de llegada en minutos al inicio y al final de un tramo "
                   "alcanzado."],
        "py_h": "Automatización con Python",
        "py_intro": "Cada algoritmo tiene un id estable; los parámetros de lista reciben la "
                    "posición de la opción (0, 1, 2…).",
        "how_k": "Cómo funciona", "how_h": "Supuestos que cambian el resultado",
        "how_intro": "Conocer estas decisiones ayuda a juzgar si un resultado es razonable.",
        "how": [
            ("Unión de los puntos a la red",
             "Cada punto se une al nodo más cercano de la red, medido en un SRC métrico "
             "local. Para auto solo cuentan los nodos del <b>mayor componente fuertemente "
             "conexo</b> — nodos desde los que se llega a cualquier otro y se vuelve, "
             "respetando el sentido —, así que siempre existe una ruta. Para peatón se usa el "
             "mayor componente conexo. Por eso, un punto en una calle aislada se une al nodo "
             "más cercano de la red principal, que puede estar a cierta distancia. Los puntos "
             "a más de 5 km de cualquier nodo candidato se rechazan (rutas) o se omiten "
             "(isócronas)."),
            ("Distancia o tiempo",
             "<i>Menor distancia</i> suma la longitud de los tramos; <i>más rápida</i> suma "
             "<code>travel_time</code>. La ruta más rápida es la de menor tiempo "
             "<i>estimado</i>, no una garantía del viaje real más corto. Para peatón la "
             "velocidad es constante, así que ambos criterios dan el mismo camino."),
            ("Velocidades",
             "<code>travel_time</code> = longitud ÷ velocidad. La velocidad es la etiqueta "
             "<code>maxspeed</code> de OSM cuando existe; si no, un valor por tipo de vía "
             "(motorway 100, primary 60, secondary 50, tertiary 40, residential 30, service "
             "20, living_street 10 km/h); los demás tipos usan el promedio de las vías "
             "etiquetadas del mismo tipo, o 30 km/h. Son valores urbanos para tránsito "
             "fluido."),
            ("Sentido único",
             "La capa <code>arcs</code> tiene un registro por sentido de circulación: una "
             "calle de doble sentido da dos arcos; una de sentido único, un arco. El auto "
             "solo usa arcos; el peatón camina en ambos sentidos. Su exactitud depende de "
             "las etiquetas <code>oneway</code> de OpenStreetMap."),
        ],
        "arcs": ["calle doble sentido", "2 arcos", "calle sentido único", "1 arco"],
        "legend": ["ruta", "contramano", "origen", "destino"],
        "dir_side": "<i>Ignorar sentido único</i> agrega los arcos inversos faltantes y los "
                    "marca como <code>wrong_way</code>. Muestra el error que cometería un "
                    "grafo no dirigido; su resultado no es una ruta para conducir.",
        "oneway_alt": "Dos mapas del mismo trayecto: a la izquierda la ruta en auto sigue el "
                      "sentido de las calles y es más larga; a la derecha, ignorándolo, es más "
                      "corta pero usa un tramo a contramano, punteado en negro",
        "oneway_left": "<b>Auto, respetando el sentido</b> — la ruta es más larga.",
        "oneway_right": "<b>Ignorando el sentido único</b> — más corta, pero el tramo negro "
                        "punteado va a contramano.",
        "how2": [
            ("Desde o hacia los puntos",
             "<i>Desde los puntos</i> responde «¿hasta dónde llego desde aquí en 10 "
             "minutos?». <i>Hacia los puntos</i> responde «¿desde dónde se llega aquí en 10 "
             "minutos?»: el cálculo corre sobre el grafo invertido. Solo difieren para auto, "
             "por el sentido único."),
            ("Una isócrona por punto o cobertura combinada",
             "Con una isócrona por punto, cada punto tiene sus propios polígonos, que pueden "
             "superponerse. La cobertura combinada parte de todos los puntos a la vez: cada "
             "calle recibe el tiempo del punto que la alcanza <i>más rápido por la red</i> "
             "(no el más cercano en línea recta), y se genera un polígono por tiempo."),
        ],
        "cov_alt": "Isócronas a pie de 5, 10 y 15 minutos alrededor de cuatro puntos, cada "
                   "uno con sus polígonos superpuestos",
        "cov_cap": "Isócronas a pie (5, 10, 15 min) de cuatro puntos de ejemplo "
                   "(piensa en escuelas), una por punto.",
        "how3": [
            ("Métodos de polígono",
             "<b>Franja alrededor de las calles alcanzadas</b>: cada tramo alcanzado recibe un "
             "buffer del ancho de la franja; el último tramo de cada camino se corta en "
             "proporción al tiempo restante, suponiendo velocidad constante en él. El "
             "polígono sigue la red. <b>Envolvente cóncava</b>: un contorno más suave "
             "alrededor de los nodos alcanzados y los extremos cortados. Es más fácil de "
             "leer, pero su interior incluye lugares que la red no alcanza (manzanas, agua, "
             "áreas cercadas)."),
        ],
        "meth_alt": "La misma isócrona dibujada con los dos métodos: a la izquierda franjas "
                    "estrechas a lo largo de las calles, a la derecha contornos cóncavos más "
                    "suaves",
        "meth_left": "<b>Franja alrededor de las calles alcanzadas</b> — sigue la red.",
        "meth_right": "<b>Envolvente cóncava</b> — más suave; no todo el interior es "
                      "alcanzable.",
        "roads_alt": "Tramos de calle coloreados por el tiempo de llegada a pie, del azul "
                     "(cerca) al rojo (lejos)",
        "roads_cap": "<b>Calles alcanzadas</b>: tiempo estimado de llegada a pie en cada tramo "
                     "de calle, desde un punto en Tambaú, junto al mar.",
        "near": "cerca", "far": "lejos",
        "cache_h": "Lectura y caché",
        "cache": "El primer cálculo sobre un GeoPackage lo lee y arma los grafos; los "
                 "siguientes los reutilizan mientras QGIS esté abierto. Si el archivo cambia en "
                 "el disco, se vuelve a leer. Solo se mantiene una red en memoria a la vez.",
        "gloss_h": "Glosario",
        "gloss": [
            ("OpenStreetMap (OSM)", "Base colaborativa de datos geográficos. La cobertura y "
                                    "el detalle varían entre lugares y no son uniformemente "
                                    "completos ni actualizados."),
            ("OSMnx", "Biblioteca de Python que el complemento usa para descargar redes de OSM "
                      "y convertirlas en grafos."),
            ("Nominatim / Overpass", "Servicios de OSM que encuentran un lugar por su nombre "
                                     "(geocodificación) y devuelven los datos del mapa dentro "
                                     "de un área."),
            ("GeoPackage", "Archivo único <code>.gpkg</code> que puede guardar varias capas "
                           "vectoriales y tablas."),
            ("SRC", "Sistema de referencia de coordenadas: cómo las coordenadas de una capa se "
                    "relacionan con lugares en la Tierra. La red se guarda en EPSG:4326 "
                    "(longitud/latitud); las distancias se miden en un SRC métrico local "
                    "(UTM)."),
            ("Nodo", "Punto de la red: una intersección o el final de una calle."),
            ("Tramo (edge)", "Parte de una calle entre dos nodos, usada para visualizar."),
            ("Arco dirigido", "Tramo con un sentido de circulación. Una calle de doble "
                              "sentido son dos arcos; una de sentido único, un arco en el "
                              "sentido permitido."),
            ("Grafo dirigido", "Red en la que cada conexión tiene un sentido; necesaria para "
                               "modelar el sentido único."),
            ("Ruta más corta", "Camino de menor costo total; el costo es la distancia o el "
                               "tiempo estimado."),
            ("Componente fuertemente conexo", "Mayor conjunto de nodos en el que cada nodo "
                                              "alcanza a todos los demás siguiendo el "
                                              "sentido de los arcos."),
            ("Isócrona", "Área estimada como alcanzable dentro de un límite de tiempo por la "
                         "red y el perfil elegidos. El polígono es una representación "
                         "cartográfica."),
            ("Envolvente cóncava", "Contorno que se ajusta a un conjunto de puntos más que la "
                                   "envolvente convexa. Representa los datos; no prueba el "
                                   "acceso a todo lugar interior."),
        ],
        "faq_k": "Ayuda", "faq_h": "Solución de problemas",
        "faq_intro": "Cada entrada indica la causa probable y qué hacer.",
        "cause_l": "Causa probable", "action_l": "Qué hacer",
        "faq": [
            ("Los algoritmos están desactivados, o «Faltan bibliotecas de Python»",
             "OSMnx (u otra biblioteca) no se encuentra en el Python de QGIS.",
             "Sigue los pasos de <a href='#install'>Instalación</a>, reinicia QGIS y ejecuta "
             "el código de verificación."),
            ("«Sin resultados para …» o «no tiene un polígono de límite»",
             "Nominatim no encontró el lugar, o lo encontró como punto o línea (una calle, un "
             "punto de interés).",
             "Escribe el nombre como en OpenStreetMap, con estado y país, y usa un municipio, "
             "distrito o barrio. Buscar el nombre en openstreetmap.org muestra lo que "
             "encuentra Nominatim."),
            ("La descarga falla o se agota el tiempo",
             "El área es grande, los servidores de OSM están ocupados, la conexión es lenta o "
             "se necesita un proxy.",
             "Inténtalo más tarde o con un lugar más pequeño; revisa el proxy en "
             "<i>Configuración → Opciones → Red</i>. No repitas el pedido en rápida "
             "sucesión."),
            ("«… km de la red vial»",
             "El punto está a más de 5 km de la red: fuera del área descargada, o en una capa "
             "con el SRC equivocado.",
             "Marca dentro del área del GeoPackage, revisa el SRC de la capa de puntos o "
             "descarga un lugar más grande."),
            ("«El origen y el destino se ajustan al mismo nodo de la red»",
             "Los dos puntos se unen al mismo nodo (están muy cerca o ambos en una calle "
             "aislada).",
             "Elige puntos más separados."),
            ("La ruta usa una calle extraña o empieza lejos de mi clic",
             "El clic se unió a un nodo de la red principal a cierta distancia, o las "
             "etiquetas de sentido único faltan o están mal en OSM.",
             "Lee los avisos del registro, mira la capa <code>arcs</code> cerca del punto y, "
             "si el dato está mal, considera corregirlo en OpenStreetMap y descargar de "
             "nuevo."),
            ("Las isócronas a pie parecen demasiado pequeñas",
             "La red se descargó como <code>drive</code> y no tiene veredas ni senderos.",
             "Descarga el lugar de nuevo con <code>walk</code> o <code>all</code>."),
            ("Guardé las capas en otro GeoPackage",
             "Guardar capas temporales puede perder el SRC y agregar un prefijo a los "
             "nombres.",
             "Funciona: los nombres con prefijo (<code>patos_nodes</code>…) se reconocen y las "
             "capas lon/lat sin SRC se toman como EPSG:4326 (el registro lo avisa). Mantén "
             "una red por GeoPackage."),
        ],
        "report_h": "Cómo informar un problema",
        "report": "Abre un <a href='" + REPO + "/issues'>issue</a> con: la versión del "
                  "complemento (Administrador de complementos), la versión de QGIS y el sistema "
                  "operativo (<i>Ayuda → Acerca de</i>), el lugar y el tipo de red, y el mensaje "
                  "completo del panel, de la pestaña <i>Registro</i> del diálogo o de <i>Ver → "
                  "Paneles → Mensajes de registro</i>.",
        "author_k": "Sobre el autor", "author_h": "Marcello Benigno",
        "author_role": "Profesor de la carrera de Tecnología en Geoprocesamiento del "
                       "Instituto Federal de Paraíba (IFPB), Brasil.",
        "author_bio": [
            "Marcello Benigno es magíster en Ciencias Geodésicas y Tecnologías de la "
            "Geoinformación por la UFPE e ingeniero civil por la UFCG. Desde hace más de 20 "
            "años trabaja en la enseñanza y el desarrollo de soluciones geotecnológicas de "
            "código abierto.",
            "Su experiencia incluye desarrollo Web GIS y automatización espacial con Python — "
            "especialmente PyQGIS, OSMnx, NetworkX y Django —, modelado de bases de datos "
            "geográficas y arquitecturas en entornos Linux. Ese trabajo orienta el desarrollo "
            "de herramientas que integran el análisis espacial y el geoprocesamiento al "
            "ecosistema QGIS."],
        "author_photo": "Foto de Marcello Benigno",
        "footer_data": "Datos © colaboradores de OpenStreetMap (ODbL). Figuras hechas con el "
                       "complemento sobre la red de João Pessoa, Paraíba, Brasil.",
        "footer_license": "Complemento con licencia GPL-2.0-or-later.",
    },
}

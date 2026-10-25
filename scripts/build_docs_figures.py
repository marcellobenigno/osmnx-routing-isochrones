"""
Builds the figures of the documentation site (docs/assets/img) with the plugin itself, inside
a headless QGIS: maps of real routes / isochrones and screenshots of the map panels.

    QT_QPA_PLATFORM=offscreen <QGIS python> scripts/build_docs_figures.py network.gpkg

network.gpkg: a road network written by '1. Download road network' (the site uses
'Cabedelo, Paraíba, Brazil', type 'drive'). Needs QGIS Python + osmnx.
"""
import os
import random
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "docs", "assets", "img")

from qgis.core import (QgsApplication, QgsProject, QgsVectorLayer, QgsMapSettings,  # noqa: E402
                       QgsMapRendererParallelJob, QgsCoordinateReferenceSystem,
                       QgsProcessingContext, QgsProcessingFeedback, QgsMapLayer,
                       QgsProcessingOutputLayerDefinition, QgsProcessingUtils, QgsSettings,
                       QgsFillSymbol, QgsLineSymbol, QgsSingleSymbolRenderer, QgsRectangle,
                       QgsCoordinateTransform, QgsPointXY, QgsFeature, QgsGeometry)
from qgis.PyQt.QtCore import QSize, Qt, QCoreApplication, QRectF  # noqa: E402
from qgis.PyQt.QtGui import QColor, QImage, QPainter, QFont  # noqa: E402

APP = QgsApplication([], True)
APP.initQgis()
for p in ("/usr/share/qgis/python/plugins",
          os.path.join(QgsApplication.pkgDataPath(), "python", "plugins")):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.append(p)
from processing.core.Processing import Processing  # noqa: E402
import processing  # noqa: E402

Processing.initialize()
from osmnx_routing_isochrones.provider import OsmnxRoutingProvider  # noqa: E402
from osmnx_routing_isochrones import core  # noqa: E402

PROVIDER = OsmnxRoutingProvider()      # keep a reference, or Python deletes it
QgsApplication.processingRegistry().addProvider(PROVIDER)
WEB = QgsCoordinateReferenceSystem("EPSG:3857")
BACKGROUND = QColor("#f4f1ea")
SCALE = 2                                   # retina-ready images


def run(alg, params, load=()):
    context = QgsProcessingContext()
    context.setProject(QgsProject.instance())
    feedback = QgsProcessingFeedback()
    for key in load:
        params[key] = QgsProcessingOutputLayerDefinition("TEMPORARY_OUTPUT",
                                                         QgsProject.instance())
    res = processing.run(f"osmnx_routing:{alg}", params, context=context, feedback=feedback)
    post = {d.outputName: d.postProcessor()
            for d in context.layersToLoadOnCompletion().values() if d.postProcessor()}
    layers = {}
    for key, value in res.items():
        lyr = value if isinstance(value, QgsMapLayer) else (
            QgsProcessingUtils.mapLayerFromString(value, context)
            if isinstance(value, str) else None)
        if lyr is not None:
            layers[key] = lyr
            if key in post:
                post[key].postProcessLayer(lyr, context, feedback)
            QgsProject.instance().addMapLayer(lyr, False)
    return res, layers


def base_layers(gpkg):
    boundary = QgsVectorLayer(f"{gpkg}|layername=boundary", "boundary", "ogr")
    boundary.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
        {"color": "255,255,255,255", "outline_color": "#c9c2b2", "outline_width": "0.4"})))
    edges = QgsVectorLayer(f"{gpkg}|layername=edges", "edges", "ogr")
    edges.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple(
        {"color": "#b9b4aa", "width": "0.28"})))
    for lyr in (boundary, edges):
        QgsProject.instance().addMapLayer(lyr, False)
    return boundary, edges


def opacity(layer, value):
    layer.setOpacity(value)
    return layer


def render(layers, extent, path, size=(1600, 900)):
    """layers: top first. extent in EPSG:4326, padded to the image ratio."""
    ms = QgsMapSettings()
    ms.setLayers(layers)
    ms.setDestinationCrs(WEB)
    xf = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"), WEB,
                                QgsProject.instance())
    ext = xf.transformBoundingBox(extent)
    ms.setExtent(ext)
    ms.setOutputSize(QSize(size[0] * SCALE // 2, size[1] * SCALE // 2))
    ms.setOutputDpi(96 * SCALE / 2 * 1.4)
    ms.setBackgroundColor(BACKGROUND)
    job = QgsMapRendererParallelJob(ms)
    job.start()
    job.waitForFinished()
    img = job.renderedImage()
    img.save(path)
    print("written", os.path.relpath(path, ROOT))
    return img


def around(points, pad=0.25, ratio=16 / 9):
    xs = [p[1] for p in points]
    ys = [p[0] for p in points]
    r = QgsRectangle(min(xs), min(ys), max(xs), max(ys))
    w, h = max(r.width(), 1e-3), max(r.height(), 1e-3)
    cx, cy = r.center().x(), r.center().y()
    w, h = w * (1 + 2 * pad), h * (1 + 2 * pad)
    if w / h < ratio:
        w = h * ratio
    else:
        h = w / ratio
    return QgsRectangle(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def extent_of(layer, pad=0.08, ratio=16 / 9):
    xf = QgsCoordinateTransform(layer.crs(), QgsCoordinateReferenceSystem("EPSG:4326"),
                                QgsProject.instance())
    e = xf.transformBoundingBox(layer.extent())
    return around([(e.yMinimum(), e.xMinimum()), (e.yMaximum(), e.xMaximum())], pad, ratio)


def pt(latlon):
    return f"{latlon[1]},{latlon[0]} [EPSG:4326]"


def side_by_side(images, path, gap=12):
    w = sum(i.width() for i in images) + gap * (len(images) - 1)
    h = max(i.height() for i in images)
    out = QImage(w, h, QImage.Format_ARGB32)
    out.fill(QColor(0, 0, 0, 0))
    p = QPainter(out)
    x = 0
    for img in images:
        p.drawImage(x, 0, img)
        x += img.width() + gap
    p.end()
    out.save(path)
    print("written", os.path.relpath(path, ROOT))


def node_latlon(net, node):
    d = net["G"].nodes[node]
    return d["y"], d["x"]


def find_oneway_case(net, rnd):
    """Origin/destination where ignoring one-way streets gives a shorter, wrong route."""
    nodes = list(net["nodes_drive"].index)
    best = None
    for _ in range(400):
        a, b = rnd.sample(nodes, 2)
        oa, ob = node_latlon(net, a), node_latlon(net, b)
        try:
            _, ok = core.route(net, oa, ob, "drive")
            _, bad = core.route(net, oa, ob, "drive", ignore_oneway=True)
        except ValueError:
            continue
        if 0.8 < ok["km"] < 3.0 and bad["wrong_m"] > 150 and ok["km"] - bad["km"] > 0.3:
            score = (ok["km"] - bad["km"]) / ok["km"]
            if best is None or score > best[0]:
                best = (score, oa, ob)
    return best[1], best[2]


def _xy(nodes_m):
    import numpy as np
    return np.c_[nodes_m.geometry.x.to_numpy(), nodes_m.geometry.y.to_numpy()]


def central_node(net, radius=400):
    """Node with the most neighbours within `radius` m: the dense centre of the town."""
    nm = net["nodes_drive"]
    xy = _xy(nm)
    d2 = ((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1)
    return int(nm.index[(d2 < radius ** 2).sum(1).argmax()])


def spread_nodes(net, center, rnd, n=4, within=2200, apart=900):
    """n nodes near the centre, at least `apart` m from each other (e.g. schools)."""
    nm = net["nodes_free"]
    xy = _xy(nm)
    c = xy[list(nm.index).index(center)] if center in nm.index else xy.mean(0)
    near = [i for i in range(len(xy)) if ((xy[i] - c) ** 2).sum() < within ** 2]
    rnd.shuffle(near)
    chosen = []
    for i in near:
        if all(((xy[i] - xy[j]) ** 2).sum() > apart ** 2 for j in chosen):
            chosen.append(i)
        if len(chosen) == n:
            break
    return [int(nm.index[i]) for i in chosen]


def main(gpkg):
    os.makedirs(OUT, exist_ok=True)
    rnd = random.Random(7)
    boundary, edges = base_layers(gpkg)
    net = core.load_network(gpkg)
    center = node_latlon(net, central_node(net))

    # 1. hero: car isochrones around the centre
    _, iso = run("isochrones", {"NETWORK": gpkg, "PROFILE": 0, "POINT": pt(center),
                                "MINUTES": "1, 2, 3, 4", "ROADS": None},
                 load=["OUTPUT", "USED_POINTS"])
    render([iso["USED_POINTS"], opacity(iso["OUTPUT"], 0.9), edges, boundary],
           extent_of(iso["OUTPUT"], 0.03, 4 / 3), os.path.join(OUT, "hero.png"), (1200, 900))

    # 2. one-way: correct route vs route ignoring one-way streets
    o, d = find_oneway_case(net, rnd)
    _, ok = run("shortest_path", {"NETWORK": gpkg, "ORIGIN": pt(o), "DESTINATION": pt(d)},
                load=["OUTPUT", "POINTS"])
    _, bad = run("shortest_path", {"NETWORK": gpkg, "ORIGIN": pt(o), "DESTINATION": pt(d),
                                   "IGNORE_ONEWAY": True}, load=["OUTPUT"])
    ext = around([o, d], 0.3, 4 / 3)
    a = render([ok["POINTS"], ok["OUTPUT"], edges, boundary], ext,
               os.path.join(OUT, "_route_ok.png"), (800, 600))
    b = render([ok["POINTS"], bad["OUTPUT"], edges, boundary], ext,
               os.path.join(OUT, "_route_bad.png"), (800, 600))
    side_by_side([a, b], os.path.join(OUT, "oneway.png"))

    # 3. coverage of several points (e.g. schools), walking, one isochrone per point
    sites = [node_latlon(net, n) for n in spread_nodes(net, central_node(net), rnd)]
    schools = QgsVectorLayer("Point?crs=EPSG:4326&field=name:string", "schools", "memory")
    feats = []
    for i, (lat, lon) in enumerate(sites, 1):
        f = QgsFeature(schools.fields())
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
        f["name"] = f"School {i}"
        feats.append(f)
    schools.dataProvider().addFeatures(feats)
    QgsProject.instance().addMapLayer(schools, False)
    _, cov = run("isochrones", {"NETWORK": gpkg, "PROFILE": 1, "POINTS": schools.id(),
                                "ID_FIELD": "name", "MINUTES": "5, 10, 15",
                                "ROADS": None}, load=["OUTPUT", "USED_POINTS"])
    render([cov["USED_POINTS"], opacity(cov["OUTPUT"], 0.8), edges, boundary],
           extent_of(cov["OUTPUT"], 0.08), os.path.join(OUT, "coverage.png"))

    # 4. polygon methods: band around roads vs concave hull
    common = {"NETWORK": gpkg, "PROFILE": 0, "POINT": pt(center), "MINUTES": "1, 2, 3",
              "ROADS": None}
    imgs = []
    for method in (0, 1):
        _, m = run("isochrones", dict(common, METHOD=method), load=["OUTPUT", "USED_POINTS"])
        imgs.append(render([m["USED_POINTS"], opacity(m["OUTPUT"], 0.85), edges, boundary],
                           extent_of(m["OUTPUT"], 0.15, 4 / 3),
                           os.path.join(OUT, f"_method{method}.png"), (800, 600)))
    side_by_side(imgs, os.path.join(OUT, "methods.png"))

    # 5. reached roads: arrival time on foot
    _, walk = run("isochrones", {"NETWORK": gpkg, "PROFILE": 1, "POINT": pt(center),
                                 "MINUTES": "4, 8, 12"},
                  load=["OUTPUT", "ROADS", "USED_POINTS"])
    render([walk["USED_POINTS"], walk["ROADS"], edges, boundary],
           extent_of(walk["ROADS"], 0.1), os.path.join(OUT, "reached_roads.png"))

    for f in os.listdir(OUT):
        if f.startswith("_"):
            os.remove(os.path.join(OUT, f))
    panels(gpkg, o, d, center)


def panels(gpkg, o, d, center):
    """Screenshots of the map panels next to the map, in English and Portuguese."""
    from qgis.PyQt.QtCore import QTranslator
    from qgis.gui import QgsMapCanvas
    from osmnx_routing_isochrones import map_tools
    import time
    qm = os.path.join(ROOT, "osmnx_routing_isochrones", "i18n",
                      "osmnx_routing_isochrones_pt_BR.qm")
    for lang in ("en", "pt"):
        translator = None
        if lang == "pt":
            translator = QTranslator()
            translator.load(qm)
            QCoreApplication.installTranslator(translator)
        for kind in ("route", "isochrones"):
            canvas = QgsMapCanvas()
            canvas.resize(900, 640)
            canvas.setDestinationCrs(WEB)
            cls = map_tools.RoutePanel if kind == "route" else map_tools.IsochronePanel
            panel = cls(canvas)
            panel.resize(380, 640)
            panel.network.setFilePath(gpkg)
            panel.pick.setChecked(True)
            if kind == "route":
                for p in (o, d):
                    panel._picked(QgsPointXY(*_to_web(p)))
            else:
                panel.minutes.setText("2, 4, 6")
                panel._picked(QgsPointXY(*_to_web(center)))
            end = time.time() + 120
            while panel.task is not None and time.time() < end:
                QgsApplication.processEvents()
                time.sleep(0.05)
            QgsApplication.processEvents()
            project = QgsProject.instance()
            layers = [project.mapLayer(i) for i in [panel.points_layer_id] + panel.outputs]
            layers = [lyr for lyr in layers if lyr is not None]
            gb = [lyr for lyr in project.mapLayers().values()
                  if lyr.name() in ("edges", "boundary")]
            gb.sort(key=lambda lyr: lyr.name() != "edges")
            ext = (around([o, d], 0.3, 900 / 640) if kind == "route"
                   else extent_of(layers[1], 0.1, 900 / 640))
            mp = render(layers + gb, ext, os.path.join(OUT, "_map.png"), (900, 640))
            panel.network.lineEdit().setText("cabedelo.gpkg")     # tidy path in the shot
            shot = panel.widget().grab().toImage()
            title = _title_bar(panel.windowTitle(), shot.width())
            out = QImage(mp.width() + shot.width(), max(mp.height(), shot.height() + 28),
                         QImage.Format_ARGB32)
            out.fill(QColor("#ececec"))
            p = QPainter(out)
            p.drawImage(0, 0, mp)
            p.drawImage(mp.width(), 0, title)
            p.drawImage(mp.width(), title.height(), shot)
            p.end()
            path = os.path.join(OUT, f"panel_{kind}_{lang}.png")
            out.save(path)
            print("written", os.path.relpath(path, ROOT))
            for lid in panel.outputs + [panel.points_layer_id]:
                if project.mapLayer(lid):
                    project.removeMapLayer(lid)
            panel.cleanup()
        if translator:
            QCoreApplication.removeTranslator(translator)
    os.remove(os.path.join(OUT, "_map.png"))


def _to_web(latlon):
    xf = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"), WEB,
                                QgsProject.instance())
    p = xf.transform(QgsPointXY(latlon[1], latlon[0]))
    return p.x(), p.y()


def _title_bar(text, width):
    img = QImage(width, 28, QImage.Format_ARGB32)
    img.fill(QColor("#dcdcdc"))
    p = QPainter(img)
    f = QFont()
    f.setBold(True)
    p.setFont(f)
    p.setPen(QColor("#333"))
    p.drawText(QRectF(10, 0, width - 20, 28), int(Qt.AlignVCenter | Qt.AlignLeft), text)
    p.end()
    return img


if __name__ == "__main__":
    QgsSettings().setValue("locale/overrideFlag", False)
    main(sys.argv[1])
    sys.stdout.flush()
    os._exit(0)

"""
Algorithm tests inside a real, headless QGIS (Processing framework, memory layers, styles,
translations).

    QT_QPA_PLATFORM=offscreen python -m pytest -v tests/test_qgis.py

Needs: QGIS Python bindings + osmnx in the same Python. The download test needs internet and
only runs with OSMNX_ONLINE=1.
"""
import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qgis.core import (QgsApplication, QgsProject, QgsVectorLayer, QgsFeature, QgsMapLayer,  # noqa: E402,E501
                       QgsGeometry, QgsPointXY, QgsProcessingContext, QgsProcessingFeedback,
                       QgsProcessingOutputLayerDefinition, QgsProcessingUtils, QgsWkbTypes,
                       QgsCategorizedSymbolRenderer, QgsGraduatedSymbolRenderer, QgsSettings)

APP = QgsApplication([], False)
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
import synthetic as S  # noqa: E402

PROVIDER = OsmnxRoutingProvider()
QgsApplication.processingRegistry().addProvider(PROVIDER)


def pt(i, j, crs="EPSG:4326"):
    lat, lon = S.latlon(i, j)
    return f"{lon},{lat} [{crs}]"


@pytest.fixture(scope="session")
def network(tmp_path_factory):
    path = str(tmp_path_factory.mktemp("net") / "grid.gpkg")
    core.export_gpkg(core.add_costs(S.build_graph()), path)
    return path


def run(alg, params, load=()):
    """Runs an algorithm; outputs listed in `load` go through the 'load on completion'
    path so the style post-processors run, as they would in the QGIS GUI."""
    context = QgsProcessingContext()
    context.setProject(QgsProject.instance())
    feedback = QgsProcessingFeedback()
    if alg in ("shortest_path", "isochrones"):
        params.setdefault("OUTPUT", "TEMPORARY_OUTPUT")
    for key in load:
        params[key] = QgsProcessingOutputLayerDefinition("TEMPORARY_OUTPUT",
                                                         QgsProject.instance())
    res = processing.run(f"osmnx_routing:{alg}", params, context=context, feedback=feedback)
    # processing.run() hands vector outputs back as layer objects (taken out of the context)
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
    return res, layers


def test_provider_registers_four_algorithms():
    ids = sorted(a.id() for a in PROVIDER.algorithms())
    assert ids == ["osmnx_routing:download_network", "osmnx_routing:inspect_network",
                   "osmnx_routing:isochrones", "osmnx_routing:shortest_path"]
    for a in PROVIDER.algorithms():
        assert a.displayName() and a.shortHelpString() and not a.icon().isNull()


def test_inspect_report(network, tmp_path):
    out = str(tmp_path / "report.html")
    res, _ = run("inspect_network", {"INPUT": network, "OUTPUT": out})
    html = open(res["OUTPUT"], encoding="utf-8").read()
    for text in ("Routing diagnosis", "arcs", "EPSG:4326", "travel_time"):
        assert text in html


def test_shortest_path_drive_respects_oneway(network):
    params = {"NETWORK": network, "PROFILE": 0, "CRITERION": 0, "IGNORE_ONEWAY": False,
              "ORIGIN": pt(2, 1), "DESTINATION": pt(2, 0)}
    res, layers = run("shortest_path", params, load=["OUTPUT"])
    lyr = layers["OUTPUT"]
    assert lyr.featureCount() >= 3 and res["WRONG_WAY_M"] == 0
    assert res["DISTANCE_KM"] == pytest.approx(0.333, abs=0.001)
    names = lyr.fields().names()
    assert names[:6] == ["order", "name", "highway", "maxspeed", "oneway", "wrong_way"]
    assert isinstance(lyr.renderer(), QgsCategorizedSymbolRenderer)
    # cumulative distance of the last segment equals the total
    last = max(lyr.getFeatures(), key=lambda f: f["order"])
    assert last["cum_m"] / 1000 == pytest.approx(res["DISTANCE_KM"], abs=0.001)


def test_shortest_path_ignoring_oneway_flags_wrong_way(network):
    res, layers = run("shortest_path", {
        "NETWORK": network, "PROFILE": 0, "CRITERION": 0, "IGNORE_ONEWAY": True,
        "ORIGIN": pt(2, 1), "DESTINATION": pt(2, 0)}, load=["OUTPUT"])
    assert res["WRONG_WAY_M"] == pytest.approx(111.0)
    assert [f["wrong_way"] for f in layers["OUTPUT"].getFeatures()] == ["yes"]


def test_shortest_path_fastest_and_projected_points(network):
    """Points given in SIRGAS 2000 / UTM 25S must be reprojected correctly."""
    from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform
    xf = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"),
                                QgsCoordinateReferenceSystem("EPSG:31985"),
                                QgsProject.instance())

    def utm(i, j):
        lat, lon = S.latlon(i, j)
        p = xf.transform(QgsPointXY(lon, lat))
        return f"{p.x()},{p.y()} [EPSG:31985]"

    res, _ = run("shortest_path", {"NETWORK": network, "PROFILE": 0, "CRITERION": 1,
                                   "ORIGIN": utm(0, 0), "DESTINATION": utm(7, 7)})
    assert res["DISTANCE_KM"] > 1.5 and res["TIME_MIN"] > 0


def test_walk_ignores_direction(network):
    res, _ = run("shortest_path", {"NETWORK": network, "PROFILE": 1, "CRITERION": 0,
                                   "WALK_SPEED": 4.8, "ORIGIN": pt(2, 1),
                                   "DESTINATION": pt(2, 0)})
    assert res["DISTANCE_KM"] == pytest.approx(0.111) and res["WRONG_WAY_M"] == 0
    assert res["TIME_MIN"] == pytest.approx(0.111 / 4.8 * 60, rel=0.01)


def test_isochrones_from_clicked_point(network):
    res, layers = run("isochrones", {
        "NETWORK": network, "PROFILE": 0, "POINT": pt(3, 3), "MINUTES": "0.5, 1, 2",
        "DIRECTION": 0, "METHOD": 0, "BUFFER": 40}, load=["OUTPUT", "ROADS"])
    iso = layers["OUTPUT"]
    assert iso.featureCount() == 3
    assert QgsWkbTypes.geometryType(iso.wkbType()) == QgsWkbTypes.PolygonGeometry
    areas = {f["minutes"]: f["area_km2"] for f in iso.getFeatures()}
    assert areas[0.5] < areas[1] < areas[2]
    assert all(f.geometry().isGeosValid() for f in iso.getFeatures())
    r = iso.renderer()
    assert isinstance(r, QgsCategorizedSymbolRenderer) and len(r.categories()) == 3
    roads = layers["ROADS"]
    assert roads.featureCount() > 0
    assert isinstance(roads.renderer(), QgsGraduatedSymbolRenderer)
    assert max(f["t_end_min"] for f in roads.getFeatures()) <= 2.0001


def test_isochrones_from_point_layer_per_point(network):
    lyr = QgsVectorLayer("Point?crs=EPSG:4326&field=school:string", "schools", "memory")
    feats = []
    for name, (i, j) in (("A", (2, 2)), ("B", (5, 5))):
        f = QgsFeature(lyr.fields())
        lat, lon = S.latlon(i, j)
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
        f["school"] = name
        feats.append(f)
    lyr.dataProvider().addFeatures(feats)
    QgsProject.instance().addMapLayer(lyr)
    res, layers = run("isochrones", {
        "NETWORK": network, "PROFILE": 1, "POINTS": lyr.id(), "ID_FIELD": "school",
        "SEPARATE": True, "MINUTES": "2 4", "METHOD": 1, "ROADS": None}, load=["OUTPUT"])
    iso = layers["OUTPUT"]
    assert sorted({f["source"] for f in iso.getFeatures()}) == ["A", "B"]
    assert iso.featureCount() == 4 and "ROADS" not in res


def test_isochrones_to_differs_from_from_with_oneway(network):
    common = {"NETWORK": network, "PROFILE": 0, "POINT": pt(3, 2), "MINUTES": "0.5"}
    _, a = run("isochrones", dict(common, DIRECTION=0), load=["OUTPUT"])
    _, b = run("isochrones", dict(common, DIRECTION=1), load=["OUTPUT"])
    ga = next(a["OUTPUT"].getFeatures()).geometry()
    gb = next(b["OUTPUT"].getFeatures()).geometry()
    assert not ga.equals(gb)


def test_bad_inputs_raise(network):
    from qgis.core import QgsProcessingException
    with pytest.raises(QgsProcessingException):
        run("isochrones", {"NETWORK": network, "POINT": pt(3, 3), "MINUTES": "abc"})
    with pytest.raises(QgsProcessingException):
        run("isochrones", {"NETWORK": network, "MINUTES": "5"})


def test_portuguese_translation_loads():
    from qgis.PyQt.QtCore import QCoreApplication
    from osmnx_routing_isochrones.osmnx_routing_isochrones import OsmnxRoutingPlugin
    s = QgsSettings()
    old = (s.value("locale/overrideFlag"), s.value("locale/userLocale"))
    s.setValue("locale/overrideFlag", True)
    s.setValue("locale/userLocale", "pt_BR")
    try:
        plugin = OsmnxRoutingPlugin(None)
        assert plugin.translator is not None
        alg = QgsApplication.processingRegistry().algorithmById("osmnx_routing:shortest_path")
        assert alg.displayName() == "3. Menor caminho (mão e contramão)"
        QCoreApplication.removeTranslator(plugin.translator)
        assert alg.displayName() == "3. Shortest path (one-way aware)"
    finally:
        s.setValue("locale/overrideFlag", old[0] if old[0] is not None else False)
        s.setValue("locale/userLocale", old[1] or "")


def test_download_unreachable_server_gives_clear_message(tmp_path):
    """A dead QGIS proxy makes the request fail fast: the user must get a readable message
    (not a traceback) and the QGIS proxy must actually be used."""
    from qgis.core import QgsProcessingException
    s = QgsSettings()
    keys = ("proxy/proxyEnabled", "proxy/proxyType", "proxy/proxyHost", "proxy/proxyPort")
    old = {k: s.value(k) for k in keys}
    for k, v in zip(keys, (True, "HttpProxy", "127.0.0.1", "9")):
        s.setValue(k, v)
    try:
        with pytest.raises(QgsProcessingException) as exc:
            run("download_network", {"PLACE": "Nowhere-test-place-12345, Brazil", "TYPE": 2,
                                     "OUTPUT": str(tmp_path / "x.gpkg")})
        msg = str(exc.value)
        assert "Could not reach the OpenStreetMap servers" in msg
        assert "Traceback" not in msg
    finally:
        for k, v in old.items():
            if v is None:
                s.remove(k)
            else:
                s.setValue(k, v)


@pytest.mark.skipif(os.environ.get("OSMNX_ONLINE") != "1", reason="needs internet")
def test_download_small_place(tmp_path):
    out = str(tmp_path / "net.gpkg")
    res, _ = run("download_network", {"PLACE": "Cabedelo, Paraíba, Brazil", "TYPE": 2,
                                      "OUTPUT": out})
    assert res["NODES"] > 100 and res["ARCS"] > res["NODES"]
    assert {"nodes", "edges", "arcs", "boundary"} <= set(core.list_layers(out))

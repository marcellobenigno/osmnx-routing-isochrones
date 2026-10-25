"""
Interactive map panels inside a headless (offscreen) QGIS: click vs drag on the map tool,
route and isochrones in a background task, point layers of the clicks, network GeoPackage
found in the project, plugin load / unload.

    QT_QPA_PLATFORM=offscreen python -m pytest -v tests/test_map_tools.py
"""
import time

import pytest

import test_qgis as T                   # starts QGIS + Processing and registers the provider
import synthetic as S
from qgis.core import QgsApplication, QgsProject, QgsPointXY, QgsCoordinateReferenceSystem
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent
from qgis.PyQt.QtCore import QEvent, QPoint, Qt
from qgis.PyQt.QtWidgets import QMainWindow

from osmnx_routing_isochrones import map_tools as R

network = T.network                     # session fixture: synthetic GeoPackage

PRESS = getattr(QEvent, "Type", QEvent).MouseButtonPress
MOVE = getattr(QEvent, "Type", QEvent).MouseMove
RELEASE = getattr(QEvent, "Type", QEvent).MouseButtonRelease
NO_BUTTON = getattr(Qt, "MouseButton", Qt).NoButton


@pytest.fixture
def canvas():
    c = QgsMapCanvas()
    c.resize(400, 400)
    c.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
    lat0, lon0 = S.latlon(0, 0)
    lat1, lon1 = S.latlon(7, 7)
    from qgis.core import QgsRectangle
    c.setExtent(QgsRectangle(lon0, lat0, lon1, lat1))
    yield c
    c.deleteLater()


def mouse(canvas, kind, x, y, button=R.LEFT):
    buttons = button if kind != RELEASE else NO_BUTTON
    return QgsMapMouseEvent(canvas, kind, QPoint(x, y), button, buttons)


def wait(panel, timeout=30):
    end = time.time() + timeout
    while panel.task is not None and time.time() < end:
        QgsApplication.processEvents()
        time.sleep(0.02)
    QgsApplication.processEvents()
    assert panel.task is None, "route task did not finish"


def map_px(canvas, i, j):
    """Pixel of grid node (i, j) on the canvas."""
    lat, lon = S.latlon(i, j)
    p = canvas.getCoordinateTransform().transform(QgsPointXY(lon, lat))
    return int(round(p.x())), int(round(p.y()))


def test_click_picks_and_drag_pans(canvas):
    tool = R.PointPickTool(canvas)
    picked = []
    tool.picked.connect(picked.append)
    tool.canvasPressEvent(mouse(canvas, PRESS, 100, 100))
    tool.canvasReleaseEvent(mouse(canvas, RELEASE, 101, 101))     # 2 px: still a click
    assert len(picked) == 1
    before = canvas.extent()
    tool.canvasPressEvent(mouse(canvas, PRESS, 100, 100))
    tool.canvasMoveEvent(mouse(canvas, MOVE, 150, 120))
    tool.canvasReleaseEvent(mouse(canvas, RELEASE, 150, 120))     # drag: pan, no point
    assert len(picked) == 1
    assert canvas.extent() != before
    cleared = []
    tool.cleared.connect(lambda: cleared.append(1))
    tool.canvasReleaseEvent(mouse(canvas, RELEASE, 10, 10, R.RIGHT))
    assert cleared == [1]


def click(panel, i, j):
    lat, lon = S.latlon(i, j)
    panel._picked(QgsPointXY(lon, lat))         # canvas in EPSG:4326


def names(layer):
    return [f["name"] for f in layer.getFeatures()]


def remove(*ids):
    for layer_id in ids:
        if layer_id and QgsProject.instance().mapLayer(layer_id):
            QgsProject.instance().removeMapLayer(layer_id)


def test_route_panel_clicks_points_layer_and_route(canvas, network):
    panel = R.RoutePanel(canvas)
    panel.network.setFilePath(network)
    panel.pick.setChecked(True)
    assert canvas.mapTool() is panel.tool
    click(panel, 2, 1)
    points = panel.points_layer(create=False)
    assert names(points) == ["origin"] and "DESTINATION" in panel.status.text()
    click(panel, 2, 0)                          # 2nd click runs the route
    assert names(points) == ["origin", "destination"]
    wait(panel)
    route = QgsProject.instance().mapLayer(panel.outputs[0])
    assert route is not None and route.featureCount() >= 3
    assert "0.33 km" in panel.result.text() and "0.33 km" in route.name()
    # clicked points stay drawn above the route
    root = QgsProject.instance().layerTreeRoot()
    assert root.children()[0].layerId() == points.id()
    # swap: the new route replaces the previous one (Keep previous results unchecked)
    first = panel.outputs[0]
    panel.swap_points()
    wait(panel)
    assert QgsProject.instance().mapLayer(first) is None
    assert "0.11 km" in panel.result.text()
    lon_first = next(points.getFeatures()).geometry().asPoint().x()
    assert lon_first == pytest.approx(S.latlon(2, 0)[1])
    click(panel, 5, 5)                          # 3rd click starts a new origin
    assert names(points) == ["origin"]
    panel.clear()
    assert points.featureCount() == 0 and panel.points == []
    remove(*panel.outputs, points.id())
    panel.cleanup()


def test_route_panel_keep_previous_results(canvas, network):
    panel = R.RoutePanel(canvas)
    panel.network.setFilePath(network)
    panel.keep.setChecked(True)
    click(panel, 2, 1)
    click(panel, 2, 0)
    wait(panel)
    first = panel.outputs[0]
    panel.swap_points()
    wait(panel)
    assert QgsProject.instance().mapLayer(first) is not None
    remove(first, *panel.outputs, panel.points_layer_id)
    panel.cleanup()


def test_route_panel_with_projected_canvas(canvas, network):
    """Clicks in a projected map CRS are converted to WGS84 before routing."""
    from qgis.core import QgsCoordinateTransform
    utm = QgsCoordinateReferenceSystem("EPSG:31985")
    canvas.setDestinationCrs(utm)
    xf = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"), utm,
                                QgsProject.instance())
    panel = R.RoutePanel(canvas)
    panel.network.setFilePath(network)
    for i, j in ((2, 1), (2, 0)):
        lat, lon = S.latlon(i, j)
        panel._picked(xf.transform(QgsPointXY(lon, lat)))
    assert panel.origin.y() == pytest.approx(S.latlon(2, 1)[0], abs=1e-6)
    wait(panel)
    assert "0.33 km" in panel.result.text()
    remove(*panel.outputs, panel.points_layer_id)
    panel.cleanup()


def test_route_panel_shows_errors(canvas, network, tmp_path):
    panel = R.RoutePanel(canvas)
    panel.network.setFilePath(str(tmp_path / "missing.gpkg"))
    click(panel, 2, 1)
    click(panel, 2, 0)
    assert "GeoPackage" in panel.result.text() and panel.task is None
    panel.network.setFilePath(network)
    panel.points[0] = ("origin", QgsPointXY(S.LON0, S.LAT0 + 1.0))     # ~110 km away
    panel.calculate()
    wait(panel)
    assert "km from the road network" in panel.result.text()
    remove(panel.points_layer_id)
    panel.cleanup()


def test_isochrone_panel(canvas, network):
    panel = R.IsochronePanel(canvas)
    panel.network.setFilePath(network)
    panel.minutes.setText("0.5, 1")
    panel.auto.setChecked(False)
    click(panel, 2, 2)
    click(panel, 5, 5)
    points = panel.points_layer(create=False)
    assert names(points) == ["P1", "P2"] and panel.count_label.text() == "2"
    assert panel.task is None                   # 'Calculate after each click' unchecked
    panel.separate.setChecked(True)
    panel.calculate()
    wait(panel)
    iso = QgsProject.instance().mapLayer(panel.outputs[0])
    roads = QgsProject.instance().mapLayer(panel.outputs[1])
    assert iso.featureCount() == 4 and roads.featureCount() > 0
    assert sorted({f["source"] for f in iso.getFeatures()}) == ["P1", "P2"]
    assert "P1: 0.5 min" in panel.result.text()
    # with auto on, the next click recalculates with all three points and replaces outputs
    old = list(panel.outputs)
    panel.auto.setChecked(True)
    panel.roads.setChecked(False)
    click(panel, 3, 6)
    wait(panel)
    assert all(QgsProject.instance().mapLayer(i) is None for i in old)
    assert len(panel.outputs) == 1
    iso = QgsProject.instance().mapLayer(panel.outputs[0])
    assert {f["source"] for f in iso.getFeatures()} == {"P1", "P2", "P3"}
    panel.clear()
    assert points.featureCount() == 0 and panel.count_label.text() == "0"
    assert not panel.run_button.isEnabled()
    remove(*panel.outputs, points.id())
    panel.cleanup()


def test_network_found_in_project(network, tmp_path):
    from qgis.core import QgsVectorLayer
    from osmnx_routing_isochrones.base import project_network, project_networks
    other = tmp_path / "other.gpkg"
    plain = QgsVectorLayer("Point?crs=EPSG:4326", "plain", "memory")
    lyr = QgsVectorLayer(f"{network}|layername=edges", "x_edges", "ogr")
    QgsProject.instance().addMapLayers([lyr, plain])
    try:
        assert project_network() == network and project_networks() == [network]
        # the algorithms' dialogs open with it, the panels pick it up
        reg = QgsApplication.processingRegistry()
        for alg_id, param in (("shortest_path", "NETWORK"), ("isochrones", "NETWORK"),
                              ("inspect_network", "INPUT")):
            alg = reg.createAlgorithmById(f"osmnx_routing:{alg_id}")
            assert alg.parameterDefinition(param).defaultValue() == network
        panel = R.RoutePanel(QgsMapCanvas())
        panel.network.setFilePath(str(other))
        panel.activate()
        assert panel.network.filePath() == network
        panel.cleanup()
    finally:
        remove(lyr.id(), plain.id())
    assert project_network() is None


class FakeIface:
    """Just enough of QgisInterface for initGui / unload."""

    def __init__(self):
        self.window, self.map = QMainWindow(), QgsMapCanvas()
        self.toolbar, self.menu, self.docks = [], [], []

    def mainWindow(self):
        return self.window

    def mapCanvas(self):
        return self.map

    def messageBar(self):
        raise AssertionError("no message expected: dependencies are installed")

    def addToolBarIcon(self, a):
        self.toolbar.append(a)

    def removeToolBarIcon(self, a):
        self.toolbar.remove(a)

    def addPluginToVectorMenu(self, name, a):
        self.menu.append(a)

    def removePluginVectorMenu(self, name, a):
        self.menu.remove(a)

    def addDockWidget(self, area, w):
        self.docks.append(w)

    def removeDockWidget(self, w):
        self.docks.remove(w)


def test_plugin_adds_and_removes_map_tools():
    from osmnx_routing_isochrones.osmnx_routing_isochrones import OsmnxRoutingPlugin
    iface = FakeIface()
    plugin = OsmnxRoutingPlugin(iface)
    registry = QgsApplication.processingRegistry()
    registry.removeProvider(T.PROVIDER)       # initGui registers its own provider
    try:
        plugin.initGui()
        assert len(iface.toolbar) == 2 and len(iface.menu) == 2 and not iface.docks
        route_action, iso_action = plugin.actions
        route_action.trigger()
        assert iface.map.mapTool() is plugin.panels["route"].tool
        iso_action.trigger()                    # switching panels switches the map tool
        assert len(iface.docks) == 2 and iface.map.mapTool() is plugin.panels["isochrones"].tool
        assert not plugin.panels["route"].pick.isChecked()
        plugin.unload()
        assert not iface.toolbar and not iface.menu and not iface.docks
        assert iface.map.mapTool() is None
    finally:
        if registry.providerById("osmnx_routing") is None:
            T.PROVIDER = type(T.PROVIDER)()
            registry.addProvider(T.PROVIDER)


def test_repeated_background_runs_do_not_crash(network):
    """pyproj 3.7 + reused QGIS pool threads: the 2nd background run used to segfault."""
    from qgis.core import QgsProcessingAlgRunnerTask, QgsProcessingContext, QgsProcessingFeedback
    alg = QgsApplication.processingRegistry().createAlgorithmById("osmnx_routing:shortest_path")
    for _ in range(4):
        context, feedback, done = QgsProcessingContext(), QgsProcessingFeedback(), []
        context.setProject(QgsProject.instance())
        task = QgsProcessingAlgRunnerTask(alg, {"NETWORK": network, "ORIGIN": T.pt(2, 1),
                                                "DESTINATION": T.pt(2, 0),
                                                "OUTPUT": "TEMPORARY_OUTPUT"},
                                          context, feedback)
        task.executed.connect(lambda ok, res: done.append((ok, res.get("DISTANCE_KM"))))
        QgsApplication.taskManager().addTask(task)
        end = time.time() + 30
        while not done and time.time() < end:
            QgsApplication.processEvents()
            time.sleep(0.02)
        assert done and done[0][0] and done[0][1] == pytest.approx(0.333, abs=0.001)

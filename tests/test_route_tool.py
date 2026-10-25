"""
Interactive route panel inside a headless (offscreen) QGIS: click vs drag on the map tool,
origin -> destination -> route in a background task, swap, errors, plugin unload.

    QT_QPA_PLATFORM=offscreen python -m pytest -v tests/test_route_tool.py
"""
import time

import pytest

import test_qgis as T                   # starts QGIS + Processing and registers the provider
import synthetic as S
from qgis.core import QgsApplication, QgsProject, QgsPointXY, QgsCoordinateReferenceSystem
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent
from qgis.PyQt.QtCore import QEvent, QPoint, Qt
from qgis.PyQt.QtWidgets import QMainWindow

from osmnx_routing_isochrones import route_tool as R

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


def test_panel_origin_destination_route(canvas, network):
    panel = R.RoutePanel(canvas)
    panel.network.setFilePath(network)
    panel.pick.setChecked(True)
    assert canvas.mapTool() is panel.tool
    lat, lon = S.latlon(2, 1)
    panel.add_point(QgsPointXY(lon, lat))
    assert panel.origin is not None and panel.destination is None
    assert "DESTINATION" in panel.status.text()
    lat, lon = S.latlon(2, 0)
    panel.add_point(QgsPointXY(lon, lat))       # 2nd click runs the route
    wait(panel)
    layer = QgsProject.instance().mapLayer(panel.last_layer_id)
    assert layer is not None and layer.featureCount() >= 3
    assert "0.33 km" in panel.result.text() and "0.33 km" in layer.name()
    assert set(panel.markers) == {"o", "d"}
    # swap: new route replaces the previous layer (Keep previous routes unchecked)
    first = panel.last_layer_id
    panel.swap_points()
    wait(panel)
    assert QgsProject.instance().mapLayer(first) is None
    assert "0.11 km" in panel.result.text()
    # 3rd click starts a new origin
    lat, lon = S.latlon(5, 5)
    panel.add_point(QgsPointXY(lon, lat))
    assert panel.destination is None and set(panel.markers) == {"o"}
    panel.clear()
    assert panel.origin is None and not panel.markers
    QgsProject.instance().removeMapLayer(panel.last_layer_id)
    panel.cleanup()


def test_panel_with_projected_canvas(canvas, network):
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
        panel.add_point(xf.transform(QgsPointXY(lon, lat)))
    assert panel.origin.y() == pytest.approx(S.latlon(2, 1)[0], abs=1e-6)
    wait(panel)
    assert "0.33 km" in panel.result.text()
    QgsProject.instance().removeMapLayer(panel.last_layer_id)
    panel.cleanup()


def test_panel_shows_errors(canvas, network, tmp_path):
    panel = R.RoutePanel(canvas)
    panel.network.setFilePath(str(tmp_path / "missing.gpkg"))
    for i, j in ((2, 1), (2, 0)):
        lat, lon = S.latlon(i, j)
        panel.add_point(QgsPointXY(lon, lat))
    assert "GeoPackage" in panel.result.text() and panel.task is None
    panel.network.setFilePath(network)
    panel.origin = QgsPointXY(S.LON0, S.LAT0 + 1.0)     # ~110 km away
    panel.calculate()
    wait(panel)
    assert "km from the road network" in panel.result.text()
    panel.cleanup()


def test_network_gpkg_found_in_project(network):
    from qgis.core import QgsVectorLayer
    lyr = QgsVectorLayer(f"{network}|layername=edges", "x_edges", "ogr")
    QgsProject.instance().addMapLayer(lyr)
    try:
        assert R.network_gpkg_in_project(QgsProject.instance()) == network
    finally:
        QgsProject.instance().removeMapLayer(lyr.id())


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


def test_plugin_adds_and_removes_route_tool():
    from osmnx_routing_isochrones.osmnx_routing_isochrones import OsmnxRoutingPlugin
    iface = FakeIface()
    plugin = OsmnxRoutingPlugin(iface)
    registry = QgsApplication.processingRegistry()
    registry.removeProvider(T.PROVIDER)       # initGui registers its own provider
    try:
        plugin.initGui()
        assert iface.toolbar and iface.menu and not iface.docks
        plugin.action.trigger()
        assert iface.docks and iface.map.mapTool() is plugin.panel.tool
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

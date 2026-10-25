# -*- coding: utf-8 -*-
"""
Interactive route tool: a side panel that stays open while origin and destination are
clicked on the map. Dragging pans and the wheel zooms as usual (a click is told from a drag
by the distance the mouse moved), so the map never jumps between the two clicks. The route
runs the 'shortest_path' Processing algorithm in a background task.
"""
import os

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
                                 QCheckBox, QPushButton, QLabel)
from qgis.core import (QgsApplication, QgsProject, QgsSettings, QgsCoordinateTransform,
                       QgsProcessingContext, QgsProcessingFeedback, QgsProcessingAlgRunnerTask,
                       QgsPointXY)
from qgis.gui import QgsMapTool, QgsVertexMarker, QgsDockWidget, QgsFileWidget

from .base import RouteStyle
from .compat import tr, WGS84, _first

FOLDER = os.path.dirname(__file__)
SETTINGS = "osmnx_routing/route_tool/"
CLICK_TOLERANCE_PX = 4                  # moved less than this between press and release = click
LEFT = _first((Qt, "MouseButton", "LeftButton"), (Qt, "LeftButton"))
RIGHT = _first((Qt, "MouseButton", "RightButton"), (Qt, "RightButton"))
KEY_ESCAPE = _first((Qt, "Key", "Key_Escape"), (Qt, "Key_Escape"))
ICON_CIRCLE = _first((QgsVertexMarker, "IconType", "ICON_CIRCLE"), (QgsVertexMarker, "ICON_CIRCLE"))
RIGHT_AREA = _first((Qt, "DockWidgetArea", "RightDockWidgetArea"), (Qt, "RightDockWidgetArea"))


class PointPickTool(QgsMapTool):
    """Left click = pick a point (map CRS); left drag = pan; right click / Esc = clear."""
    picked = pyqtSignal(QgsPointXY)
    cleared = pyqtSignal()

    def __init__(self, canvas):
        super().__init__(canvas)
        self._press = None
        self._dragging = False

    def canvasPressEvent(self, e):
        if e.button() == LEFT:
            self._press, self._dragging = e.pos(), False

    def canvasMoveEvent(self, e):
        if self._press is None:
            return
        if not self._dragging and ((e.pos() - self._press).manhattanLength()
                                   >= CLICK_TOLERANCE_PX):
            self._dragging = True
        if self._dragging:
            self.canvas().panAction(e)

    def canvasReleaseEvent(self, e):
        if e.button() == RIGHT:
            self.cleared.emit()
            return
        if e.button() != LEFT or self._press is None:
            return
        if self._dragging:
            self.canvas().panActionEnd(e.pos())
        else:
            self.picked.emit(self.toMapCoordinates(e.pos()))
        self._press, self._dragging = None, False

    def keyPressEvent(self, e):
        if e.key() == KEY_ESCAPE:
            self.cleared.emit()


class _Feedback(QgsProcessingFeedback):
    """Keeps the error messages of the background run to show them in the panel."""

    def __init__(self):
        super().__init__()
        self.errors = []

    def reportError(self, error, fatalError=False):
        self.errors.append(error)
        super().reportError(error, fatalError)


def network_gpkg_in_project(project):
    """Most recently added GeoPackage of the project that holds a road network layer."""
    for layer in reversed(list(project.mapLayers().values())):
        source = layer.source()
        path, _, opts = source.partition("|")
        name = opts.partition("layername=")[2].split("|")[0].lower()
        if (path.lower().endswith(".gpkg") and os.path.isfile(path)
                and name.endswith(("nodes", "edges", "arcs"))):
            return path
    return ""


class RoutePanel(QgsDockWidget):
    """Side panel: network, profile, origin/destination picked on the map, result."""

    def __init__(self, canvas, parent=None):
        super().__init__(tr("OSMnx route"), parent)
        self.setObjectName("OsmnxRoutePanel")
        self.canvas = canvas
        self.tool = PointPickTool(canvas)
        self.tool.picked.connect(self.add_point)
        self.tool.cleared.connect(self.clear)
        self.origin = self.destination = None        # QgsPointXY in WGS84
        self.markers = {}
        self.task = None
        self.last_layer_id = None

        s = QgsSettings()
        w = QWidget()
        form = QFormLayout()
        self.network = QgsFileWidget()
        self.network.setFilter("GeoPackage (*.gpkg)")
        self.network.setFilePath(s.value(SETTINGS + "gpkg", "") or "")
        form.addRow(tr("Road network GeoPackage"), self.network)
        self.profile = QComboBox()
        self.profile.addItems([tr("Car — respects one-way streets"),
                               tr("Pedestrian — ignores street direction")])
        self.profile.setCurrentIndex(int(s.value(SETTINGS + "profile", 0)))
        form.addRow(tr("Profile"), self.profile)
        self.criterion = QComboBox()
        self.criterion.addItems([tr("Shortest distance"), tr("Fastest (car only)")])
        self.criterion.setCurrentIndex(int(s.value(SETTINGS + "criterion", 0)))
        form.addRow(tr("Criterion"), self.criterion)
        self.ignore_oneway = QCheckBox(tr("Ignore one-way streets (comparison — allows wrong "
                                          "way)"))
        self.keep = QCheckBox(tr("Keep previous routes"))
        self.origin_label, self.dest_label = QLabel("—"), QLabel("—")
        form.addRow(tr("Origin"), self.origin_label)
        form.addRow(tr("Destination"), self.dest_label)

        self.pick = QPushButton(tr("Pick on map"))
        self.pick.setCheckable(True)
        self.pick.toggled.connect(self._toggle_tool)
        self.swap = QPushButton(tr("Swap"))
        self.swap.clicked.connect(self.swap_points)
        self.run_button = QPushButton(tr("Calculate"))
        self.run_button.clicked.connect(self.calculate)
        clear = QPushButton(tr("Clear"))
        clear.clicked.connect(self.clear)
        buttons = QHBoxLayout()
        for b in (self.pick, self.swap, self.run_button, clear):
            buttons.addWidget(b)

        self.status = QLabel()
        self.status.setWordWrap(True)
        self.result = QLabel()
        self.result.setWordWrap(True)
        self.result.setTextInteractionFlags(_first(
            (Qt, "TextInteractionFlag", "TextSelectableByMouse"), (Qt, "TextSelectableByMouse")))

        box = QVBoxLayout(w)
        box.addLayout(form)
        box.addWidget(self.ignore_oneway)
        box.addWidget(self.keep)
        box.addLayout(buttons)
        box.addWidget(self.status)
        box.addWidget(self.result)
        box.addStretch(1)
        self.setWidget(w)
        canvas.mapToolSet.connect(self._tool_changed)
        self._update()

    # --- map tool ----------------------------------------------------------------------
    def activate(self):
        if not self.network.filePath():
            self.network.setFilePath(network_gpkg_in_project(QgsProject.instance()))
        self.show()
        self.raise_()
        self.pick.setChecked(True)

    def _toggle_tool(self, on):
        if on:
            self.canvas.setMapTool(self.tool)
        elif self.canvas.mapTool() is self.tool:
            self.canvas.unsetMapTool(self.tool)
        self._update()

    def _tool_changed(self, new, old=None):
        if new is not self.tool and self.pick.isChecked():
            self.pick.blockSignals(True)
            self.pick.setChecked(False)
            self.pick.blockSignals(False)
            self._update()

    # --- points ------------------------------------------------------------------------
    def _to_wgs84(self, pt):
        crs = self.canvas.mapSettings().destinationCrs()
        return QgsCoordinateTransform(crs, WGS84, QgsProject.instance()).transform(pt)

    def add_point(self, map_point):
        """1st click = origin, 2nd = destination (then the route runs), 3rd = new origin."""
        pt = self._to_wgs84(map_point)
        if self.origin is None or self.destination is not None:
            self.origin, self.destination = pt, None
        else:
            self.destination = pt
        self._draw()
        if self.origin is not None and self.destination is not None:
            self.calculate()
        self._update()

    def swap_points(self):
        self.origin, self.destination = self.destination, self.origin
        self._draw()
        if self.origin is not None and self.destination is not None:
            self.calculate()
        self._update()

    def clear(self):
        self.origin = self.destination = None
        self.result.setText("")
        self._draw()
        self._update()

    def _draw(self):
        scene = self.canvas.scene()
        for m in self.markers.values():
            scene.removeItem(m)
        self.markers = {}
        crs = self.canvas.mapSettings().destinationCrs()
        back = QgsCoordinateTransform(WGS84, crs, QgsProject.instance())
        for key, pt, color in (("o", self.origin, "#1a9641"), ("d", self.destination, "#d7191c")):
            if pt is None:
                continue
            m = QgsVertexMarker(self.canvas)
            m.setCenter(back.transform(pt))
            m.setIconType(ICON_CIRCLE)
            m.setIconSize(14)
            m.setPenWidth(3)
            m.setColor(QColor(color))
            m.setFillColor(QColor(255, 255, 255, 200))
            self.markers[key] = m

    def _update(self):
        fmt = "{:.5f}, {:.5f}"
        self.origin_label.setText(fmt.format(self.origin.y(), self.origin.x())
                                  if self.origin else "—")
        self.dest_label.setText(fmt.format(self.destination.y(), self.destination.x())
                                if self.destination else "—")
        busy = self.task is not None
        both = self.origin is not None and self.destination is not None
        self.run_button.setEnabled(both and not busy)
        self.swap.setEnabled(both and not busy)
        if busy:
            text = tr("Calculating route…")
        elif not self.pick.isChecked():
            text = tr("Press 'Pick on map' to choose the points.")
        elif self.origin is None or self.destination is not None:
            text = tr("Click the ORIGIN on the map. Drag to pan, wheel to zoom, right click "
                      "or Esc to clear.")
        else:
            text = tr("Click the DESTINATION on the map.")
        self.status.setText(text)

    # --- route -------------------------------------------------------------------------
    def parameters(self):
        def fmt(p):
            return f"{p.x()},{p.y()} [EPSG:4326]"
        return {"NETWORK": self.network.filePath(), "PROFILE": self.profile.currentIndex(),
                "CRITERION": self.criterion.currentIndex(),
                "IGNORE_ONEWAY": self.ignore_oneway.isChecked(),
                "ORIGIN": fmt(self.origin), "DESTINATION": fmt(self.destination),
                "OUTPUT": "TEMPORARY_OUTPUT"}

    def calculate(self):
        if self.task is not None or self.origin is None or self.destination is None:
            return
        gpkg = self.network.filePath()
        if not gpkg or not os.path.isfile(gpkg):
            self.result.setText(tr("Choose the road network GeoPackage first."))
            return
        alg = QgsApplication.processingRegistry().createAlgorithmById(
            "osmnx_routing:shortest_path")
        ok, msg = alg.canExecute()
        if not ok:
            self.result.setText(msg)
            return
        s = QgsSettings()
        s.setValue(SETTINGS + "gpkg", gpkg)
        s.setValue(SETTINGS + "profile", self.profile.currentIndex())
        s.setValue(SETTINGS + "criterion", self.criterion.currentIndex())

        self.context = QgsProcessingContext()
        self.context.setProject(QgsProject.instance())
        self.feedback = _Feedback()
        self.task = QgsProcessingAlgRunnerTask(alg, self.parameters(), self.context,
                                               self.feedback)
        self.task.executed.connect(self._finished)
        self.result.setText("")
        self._update()
        QgsApplication.taskManager().addTask(self.task)

    def _finished(self, ok, results):
        self.task = None
        try:
            if not ok:
                errors = [e for e in self.feedback.errors if e.strip()]
                self.result.setText("<span style='color:#b00'>{}</span>".format(
                    (errors[-1] if errors else tr("The route could not be calculated."))
                    .replace("\n", "<br>")))
                return
            layer = self.context.takeResultLayer(results.get("OUTPUT", ""))
            if layer is None:
                return
            profile = (tr("pedestrian") if self.profile.currentIndex() == 1 else tr("car"))
            layer.setName(tr("Route ({profile}) {km:.2f} km").format(
                profile=profile, km=results["DISTANCE_KM"]))
            RouteStyle().postProcessLayer(layer, self.context, self.feedback)
            project = QgsProject.instance()
            if (not self.keep.isChecked() and self.last_layer_id
                    and project.mapLayer(self.last_layer_id)):
                project.removeMapLayer(self.last_layer_id)
            project.addMapLayer(layer)
            self.last_layer_id = layer.id()
            text = tr("<b>{km:.2f} km</b> | <b>{min:.1f} min</b>").format(
                km=results["DISTANCE_KM"], min=results["TIME_MIN"])
            if results.get("WRONG_WAY_M"):
                text += "<br>" + tr("{m:.0f} m driven the wrong way").format(
                    m=results["WRONG_WAY_M"])
            self.result.setText(text)
        finally:
            self._update()

    def closeEvent(self, e):
        self.pick.setChecked(False)
        self.clear()
        super().closeEvent(e)

    def cleanup(self):
        """Called when the plugin is unloaded."""
        try:
            self.canvas.mapToolSet.disconnect(self._tool_changed)
        except TypeError:
            pass
        if self.canvas.mapTool() is self.tool:
            self.canvas.unsetMapTool(self.tool)
        self.origin = self.destination = None
        self._draw()


def icon():
    return QIcon(os.path.join(FOLDER, "icons", "icon.png"))

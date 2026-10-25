# -*- coding: utf-8 -*-
"""
Interactive map tools: side panels that stay open while points are clicked on the map.

  RoutePanel     1st click = origin, 2nd = destination -> route ('shortest_path')
  IsochronePanel every click adds a point -> isochrones ('isochrones')

Dragging pans and the wheel zooms as usual (a click is told from a drag by the distance the
mouse moved), so the map never jumps between clicks. The clicks are kept in a point layer of
the project, the network GeoPackage is taken from the layers already open, and the
algorithms run in a background task.
"""
import os

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
                                 QCheckBox, QPushButton, QLabel, QLineEdit)
from qgis.core import (QgsApplication, QgsProject, QgsSettings, QgsCoordinateTransform,
                       QgsProcessingContext, QgsProcessingFeedback, QgsProcessingAlgRunnerTask,
                       QgsPointXY, QgsVectorLayer, QgsFeature, QgsGeometry,
                       QgsRendererCategory, QgsCategorizedSymbolRenderer, QgsMarkerSymbol)
from qgis.gui import QgsMapTool, QgsDockWidget, QgsFileWidget

from .base import RouteStyle, IsochroneStyle, ReachedRoadsStyle, project_networks
from .compat import tr, WGS84, _first

FOLDER = os.path.dirname(__file__)
SETTINGS = "osmnx_routing/map_tools/"
CLICK_TOLERANCE_PX = 4                  # moved less than this between press and release = click
LEFT = _first((Qt, "MouseButton", "LeftButton"), (Qt, "LeftButton"))
RIGHT = _first((Qt, "MouseButton", "RightButton"), (Qt, "RightButton"))
KEY_ESCAPE = _first((Qt, "Key", "Key_Escape"), (Qt, "Key_Escape"))
RIGHT_AREA = _first((Qt, "DockWidgetArea", "RightDockWidgetArea"), (Qt, "RightDockWidgetArea"))
SELECTABLE = _first((Qt, "TextInteractionFlag", "TextSelectableByMouse"),
                    (Qt, "TextSelectableByMouse"))


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


class PickPanel(QgsDockWidget):
    """Common part: network, 'Pick on map' tool, point layer of the clicks, background run,
    replacement of the previous outputs."""
    ALGORITHM = ""
    KEY = ""                            # settings / object name suffix

    def __init__(self, title, canvas, parent=None):
        super().__init__(title, parent)
        self.setObjectName(f"Osmnx{self.KEY.capitalize()}Panel")
        self.canvas = canvas
        self.tool = PointPickTool(canvas)
        self.tool.picked.connect(self._picked)
        self.tool.cleared.connect(self.clear)
        self.points = []                            # [(name, QgsPointXY in WGS84)]
        self.task = None
        self.outputs = []                           # layer ids of the last run
        self.points_layer_id = None

        self.network = QgsFileWidget()
        self.network.setFilter("GeoPackage (*.gpkg)")
        self.network.setFilePath(self._setting("gpkg", ""))
        self.form = QFormLayout()
        self.form.addRow(tr("Road network GeoPackage"), self.network)
        self.profile = QComboBox()
        self.profile.addItems([tr("Car — respects one-way streets"),
                               tr("Pedestrian — ignores street direction")])
        self.profile.setCurrentIndex(int(self._setting("profile", 0)))
        self.form.addRow(tr("Profile"), self.profile)
        self.build_options(self.form)

        self.keep = QCheckBox(tr("Keep previous results"))
        self.pick = QPushButton(tr("Pick on map"))
        self.pick.setCheckable(True)
        self.pick.toggled.connect(self._toggle_tool)
        self.run_button = QPushButton(tr("Calculate"))
        self.run_button.clicked.connect(self.calculate)
        clear = QPushButton(tr("Clear"))
        clear.clicked.connect(self.clear)
        self.buttons = QHBoxLayout()
        for b in (self.pick, self.run_button, clear):
            self.buttons.addWidget(b)
        self.status, self.result = QLabel(), QLabel()
        for label in (self.status, self.result):
            label.setWordWrap(True)
        self.result.setTextInteractionFlags(SELECTABLE)

        w = QWidget()
        box = QVBoxLayout(w)
        box.addLayout(self.form)
        box.addWidget(self.keep)
        box.addLayout(self.buttons)
        box.addWidget(self.status)
        box.addWidget(self.result)
        box.addStretch(1)
        self.setWidget(w)
        canvas.mapToolSet.connect(self._tool_changed)
        self._update()

    # --- to be specialised --------------------------------------------------------------
    def build_options(self, form):
        pass

    def add_point(self, pt):
        """pt in WGS84; returns True when the result should be calculated right away."""
        raise NotImplementedError

    def parameters(self):
        raise NotImplementedError

    def show_results(self, results):
        raise NotImplementedError

    def hint(self):
        return ""

    def ready(self):
        return bool(self.points)

    def style_points(self, layer):
        pass

    # --- settings ----------------------------------------------------------------------
    def _setting(self, key, default):
        return QgsSettings().value(f"{SETTINGS}{self.KEY}/{key}", default)

    def _save_setting(self, key, value):
        QgsSettings().setValue(f"{SETTINGS}{self.KEY}/{key}", value)

    # --- network & map tool ------------------------------------------------------------
    def detect_network(self):
        """Fewer clicks: use the network open in the project unless the chosen file is one
        of the project's networks too."""
        networks = project_networks(QgsProject.instance())
        if networks and self.network.filePath() not in networks:
            self.network.setFilePath(networks[0])

    def activate(self):
        self.detect_network()
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

    def _picked(self, map_point):
        crs = self.canvas.mapSettings().destinationCrs()
        pt = QgsCoordinateTransform(crs, WGS84, QgsProject.instance()).transform(map_point)
        run = self.add_point(pt)
        self._sync_points()
        if run:
            self.calculate()
        self._update()

    def clear(self):
        self.points = []
        self.result.setText("")
        self._sync_points()
        self._update()

    # --- point layer of the clicks -----------------------------------------------------
    def points_layer(self, create=True):
        project = QgsProject.instance()
        layer = project.mapLayer(self.points_layer_id) if self.points_layer_id else None
        if layer is None and create:
            layer = QgsVectorLayer("Point?crs=EPSG:4326&field=name:string(40)",
                                   self.points_layer_name(), "memory")
            self.style_points(layer)
            project.addMapLayer(layer)
            self.points_layer_id = layer.id()
        return layer

    def points_layer_name(self):
        return self.windowTitle()

    def _sync_points(self):
        layer = self.points_layer(create=bool(self.points))
        if layer is None:
            return
        provider = layer.dataProvider()
        provider.truncate()
        feats = []
        for name, pt in self.points:
            f = QgsFeature(layer.fields())
            f.setGeometry(QgsGeometry.fromPointXY(pt))
            f["name"] = name
            feats.append(f)
        provider.addFeatures(feats)
        layer.updateExtents()
        layer.triggerRepaint()

    def _raise_points(self):
        """Keeps the clicked points drawn above the results."""
        root = QgsProject.instance().layerTreeRoot()
        node = root.findLayer(self.points_layer_id) if self.points_layer_id else None
        if node is None or node.parent() is None:
            return
        parent = node.parent()
        if parent.children() and parent.children()[0] is node:
            return
        clone = node.clone()
        parent.insertChildNode(0, clone)
        parent.removeChildNode(node)

    # --- background run ----------------------------------------------------------------
    def _update(self):
        busy = self.task is not None
        self.run_button.setEnabled(self.ready() and not busy)
        if busy:
            text = tr("Calculating…")
        elif not self.pick.isChecked():
            text = tr("Press 'Pick on map' to choose the points.")
        else:
            text = self.hint()
        self.status.setText(text)

    def calculate(self):
        if self.task is not None or not self.ready():
            return
        gpkg = self.network.filePath()
        if not gpkg or not os.path.isfile(gpkg):
            self.result.setText(tr("Choose the road network GeoPackage first."))
            return
        alg = QgsApplication.processingRegistry().createAlgorithmById(self.ALGORITHM)
        ok, msg = alg.canExecute()
        if not ok:
            self.result.setText(msg)
            return
        self._save_setting("gpkg", gpkg)
        self._save_setting("profile", self.profile.currentIndex())
        self.context = QgsProcessingContext()
        self.context.setProject(QgsProject.instance())
        self.feedback = _Feedback()
        params = dict(self.parameters(), NETWORK=gpkg)
        self.task = QgsProcessingAlgRunnerTask(alg, params, self.context, self.feedback)
        self.task.executed.connect(self._finished)
        self.result.setText("")
        self._update()
        QgsApplication.taskManager().addTask(self.task)

    def _finished(self, ok, results):
        self.task = None
        try:
            if not ok:
                errors = [e for e in self.feedback.errors if e.strip()]
                text = errors[-1] if errors else tr("The calculation failed.")
                self.result.setText("<span style='color:#b00'>{}</span>".format(
                    text.replace("\n", "<br>")))
                return
            project = QgsProject.instance()
            if not self.keep.isChecked():
                for layer_id in self.outputs:
                    if project.mapLayer(layer_id):
                        project.removeMapLayer(layer_id)
            self.outputs = []
            self.show_results(results)
            self._raise_points()
        finally:
            self._update()

    def add_output(self, layer, name, style):
        layer.setName(name)
        style().postProcessLayer(layer, self.context, self.feedback)
        QgsProject.instance().addMapLayer(layer)
        self.outputs.append(layer.id())

    def profile_name(self):
        return tr("pedestrian") if self.profile.currentIndex() == 1 else tr("car")

    def closeEvent(self, e):
        self.pick.setChecked(False)
        super().closeEvent(e)

    def cleanup(self):
        """Called when the plugin is unloaded (the point layer stays in the project)."""
        try:
            self.canvas.mapToolSet.disconnect(self._tool_changed)
        except TypeError:
            pass
        if self.canvas.mapTool() is self.tool:
            self.canvas.unsetMapTool(self.tool)


def _point_symbol(color):
    return QgsMarkerSymbol.createSimple({"name": "circle", "color": color, "size": "3.4",
                                         "outline_color": "white", "outline_width": "0.6"})


# =============================================================================
# Route
# =============================================================================
class RoutePanel(PickPanel):
    ALGORITHM = "osmnx_routing:shortest_path"
    KEY = "route"

    def __init__(self, canvas, parent=None):
        super().__init__(tr("OSMnx route"), canvas, parent)
        self.swap = QPushButton(tr("Swap"))
        self.swap.clicked.connect(self.swap_points)
        self.buttons.insertWidget(1, self.swap)
        self._update()

    def build_options(self, form):
        self.criterion = QComboBox()
        self.criterion.addItems([tr("Shortest distance"), tr("Fastest (car only)")])
        self.criterion.setCurrentIndex(int(self._setting("criterion", 0)))
        form.addRow(tr("Criterion"), self.criterion)
        self.ignore_oneway = QCheckBox(tr("Ignore one-way streets (comparison — allows wrong "
                                          "way)"))
        form.addRow(self.ignore_oneway)
        self.origin_label, self.dest_label = QLabel("—"), QLabel("—")
        form.addRow(tr("Origin"), self.origin_label)
        form.addRow(tr("Destination"), self.dest_label)

    def points_layer_name(self):
        return tr("Route points")

    def style_points(self, layer):
        cats = [QgsRendererCategory(tr("origin"), _point_symbol("#1a9641"), tr("origin")),
                QgsRendererCategory(tr("destination"), _point_symbol("#d7191c"),
                                    tr("destination"))]
        layer.setRenderer(QgsCategorizedSymbolRenderer("name", cats))

    @property
    def origin(self):
        return self.points[0][1] if self.points else None

    @property
    def destination(self):
        return self.points[1][1] if len(self.points) > 1 else None

    def add_point(self, pt):
        """1st click = origin, 2nd = destination (then the route runs), 3rd = new origin."""
        if len(self.points) != 1:
            self.points = [(tr("origin"), pt)]
            return False
        self.points.append((tr("destination"), pt))
        return True

    def ready(self):
        return len(self.points) == 2

    def swap_points(self):
        if self.ready():
            self.points = [(tr("origin"), self.points[1][1]),
                           (tr("destination"), self.points[0][1])]
            self._sync_points()
            self.calculate()
        self._update()

    def hint(self):
        if len(self.points) == 1:
            return tr("Click the DESTINATION on the map.")
        return tr("Click the ORIGIN on the map. Drag to pan, wheel to zoom, right click or "
                  "Esc to clear.")

    def _update(self):
        super()._update()
        if not hasattr(self, "swap"):
            return
        fmt = "{:.5f}, {:.5f}"
        self.origin_label.setText(fmt.format(self.origin.y(), self.origin.x())
                                  if self.origin else "—")
        self.dest_label.setText(fmt.format(self.destination.y(), self.destination.x())
                                if self.destination else "—")
        self.swap.setEnabled(self.ready() and self.task is None)

    def parameters(self):
        self._save_setting("criterion", self.criterion.currentIndex())

        def fmt(p):
            return f"{p.x()},{p.y()} [EPSG:4326]"
        return {"PROFILE": self.profile.currentIndex(),
                "CRITERION": self.criterion.currentIndex(),
                "IGNORE_ONEWAY": self.ignore_oneway.isChecked(),
                "ORIGIN": fmt(self.origin), "DESTINATION": fmt(self.destination),
                "OUTPUT": "TEMPORARY_OUTPUT"}

    def show_results(self, results):
        layer = self.context.takeResultLayer(results.get("OUTPUT", ""))
        if layer is not None:
            self.add_output(layer, tr("Route ({profile}) {km:.2f} km").format(
                profile=self.profile_name(), km=results["DISTANCE_KM"]), RouteStyle)
        text = tr("<b>{km:.2f} km</b> | <b>{min:.1f} min</b>").format(
            km=results["DISTANCE_KM"], min=results["TIME_MIN"])
        if results.get("WRONG_WAY_M"):
            text += "<br>" + tr("{m:.0f} m driven the wrong way").format(
                m=results["WRONG_WAY_M"])
        self.result.setText(text)


# =============================================================================
# Isochrones
# =============================================================================
class IsochronePanel(PickPanel):
    ALGORITHM = "osmnx_routing:isochrones"
    KEY = "isochrones"

    def __init__(self, canvas, parent=None):
        super().__init__(tr("OSMnx isochrones"), canvas, parent)

    def build_options(self, form):
        self.minutes = QLineEdit(self._setting("minutes", "5, 10, 15"))
        form.addRow(tr("Times in minutes (comma separated)"), self.minutes)
        self.direction = QComboBox()
        self.direction.addItems([tr("From the points (where you can get to)"),
                                 tr("To the points (where they can be reached from)")])
        form.addRow(tr("Direction (car)"), self.direction)
        self.method = QComboBox()
        self.method.addItems([tr("Band around the reached roads (faithful to the network)"),
                              tr("Concave hull of the reached nodes (smoother)")])
        form.addRow(tr("Polygon method"), self.method)
        self.separate = QCheckBox(tr("One isochrone per point (unchecked = combined coverage)"))
        form.addRow(self.separate)
        self.roads = QCheckBox(tr("Reached roads"))
        self.roads.setChecked(True)
        form.addRow(self.roads)
        self.auto = QCheckBox(tr("Calculate after each click"))
        self.auto.setChecked(self._setting("auto", "true") in (True, "true"))
        form.addRow(self.auto)
        self.count_label = QLabel("0")
        form.addRow(tr("Points"), self.count_label)

    def points_layer_name(self):
        return tr("Isochrone points")

    def style_points(self, layer):
        layer.renderer().setSymbol(_point_symbol("#2b83ba"))

    def add_point(self, pt):
        self.points.append((f"P{len(self.points) + 1}", pt))
        return self.auto.isChecked()

    def hint(self):
        return tr("Click one or more points on the map. Drag to pan, wheel to zoom, right "
                  "click or Esc to clear.")

    def _update(self):
        super()._update()
        if hasattr(self, "count_label"):
            self.count_label.setText(str(len(self.points)))

    def parameters(self):
        self._save_setting("minutes", self.minutes.text())
        self._save_setting("auto", "true" if self.auto.isChecked() else "false")
        params = {"PROFILE": self.profile.currentIndex(), "POINTS": self.points_layer().id(),
                  "ID_FIELD": "name", "SEPARATE": self.separate.isChecked(),
                  "DIRECTION": self.direction.currentIndex(), "MINUTES": self.minutes.text(),
                  "METHOD": self.method.currentIndex(), "OUTPUT": "TEMPORARY_OUTPUT"}
        params["ROADS"] = "TEMPORARY_OUTPUT" if self.roads.isChecked() else None
        return params

    def show_results(self, results):
        times = self.minutes.text().strip()
        layer = self.context.takeResultLayer(results.get("OUTPUT", ""))
        lines = []
        if layer is not None:
            for f in sorted(layer.getFeatures(), key=lambda f: (str(f["source"]), f["minutes"])):
                lines.append(f"{f['source']}: {f['minutes']:g} min → {f['area_km2']:.2f} km²")
            self.add_output(layer, tr("Isochrones ({profile}) {times} min").format(
                profile=self.profile_name(), times=times), IsochroneStyle)
        roads = self.context.takeResultLayer(results.get("ROADS") or "")
        if roads is not None:
            self.add_output(roads, tr("Reached roads ({profile})").format(
                profile=self.profile_name()), ReachedRoadsStyle)
        self.result.setText("<br>".join(lines))


def icon():
    return QIcon(os.path.join(FOLDER, "icons", "icon.png"))

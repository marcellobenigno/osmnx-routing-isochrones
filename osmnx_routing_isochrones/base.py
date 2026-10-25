# -*- coding: utf-8 -*-
"""Common base for the algorithms: lazy import of the core and output styles."""

import os

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingException,
                       QgsProcessingLayerPostProcessorInterface, QgsVectorLayer, QgsSymbol,
                       QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsStyle, QgsClassificationEqualInterval,
                       QgsProject, QgsMarkerSymbol, QgsFields, QgsFeature, QgsGeometry,
                       QgsPointXY, QgsGradientColorRamp, QgsGradientStop)

from .compat import tr, field, WGS84, WKB_POINT, FAST_INSERT
from . import deps
from .layers import AmbiguousLayers, find_network_layers

FOLDER = os.path.dirname(__file__)


def install_message(missing):
    """How to install the missing Python libraries, shown in the dialog and the message bar."""
    return tr("Missing Python libraries: {modules}.\n\nInstall OSMnx into QGIS's Python from "
              "the Python Console (Plugins > Python Console), then restart QGIS:\n\n{code}\n\n"
              "If geopandas or networkx are also missing, run the same command without "
              "'--no-deps'.").format(modules=", ".join(missing), code=deps.INSTALL_HELP)


def _gpkg_has_network(path):
    from osgeo import ogr
    ds = ogr.Open(path)
    if ds is None:
        return False
    names = [ds.GetLayer(i).GetName() for i in range(ds.GetLayerCount())]
    ds = None
    try:
        roles = find_network_layers(names)
    except AmbiguousLayers:
        return False
    return "nodes" in roles and "edges" in roles


def project_networks(project=None):
    """GeoPackages with a road network among the layers of the project, most recently added
    first (fewer clicks: they become the default 'Road network GeoPackage')."""
    project = project or QgsProject.instance()
    found = []
    for layer in reversed(list(project.mapLayers().values())):
        path = layer.source().split("|")[0]
        if (path.lower().endswith(".gpkg") and path not in found and os.path.isfile(path)
                and _gpkg_has_network(path)):
            found.append(path)
    return found


def project_network(project=None):
    networks = project_networks(project)
    return networks[0] if networks else None


def import_core():
    """Imports the core only when an algorithm runs, with a clear message if OSMnx is missing
    (also for processing.run() and batch runs, which do not call canExecute)."""
    missing = deps.missing_modules()
    if missing:
        raise QgsProcessingException(install_message(missing))
    try:
        from . import core
    except ImportError as err:
        raise QgsProcessingException(install_message([getattr(err, "name", None) or str(err)]))
    core.keep_proj_context()            # runs in the Processing worker thread
    return core


def icon(name="icon"):
    """'icon' = plugin identity (manager, Processing group); 'route' / 'isochrones' = tools
    of the same family (same palette and strokes)."""
    svg = os.path.join(FOLDER, "icons", f"{name}.svg")
    return QIcon(svg if os.path.exists(svg) else os.path.join(FOLDER, "icons", "icon.png"))


class AlgorithmBase(QgsProcessingAlgorithm):
    _name = ""
    _icon = "icon"
    _needs_core = True                  # False: runs with QGIS alone (no OSMnx needed)

    def tr(self, text):
        return tr(text)

    def canExecute(self):
        """Disables the Run button (with the install instructions) when libraries are missing."""
        missing = deps.missing_modules() if self._needs_core else []
        return (False, install_message(missing)) if missing else (True, "")

    def createInstance(self):
        return type(self)()

    def name(self):
        return self._name

    def group(self):
        return ""

    def groupId(self):
        return ""

    def icon(self):
        return icon(self._icon)


# =============================================================================
# Styles applied when an output layer is loaded into the project
# (the post-processor must stay alive, so the instance is kept on the class)
# =============================================================================
RAMPS = {   # same colours as the QGIS ramps, used when the user's style library lacks them
    "RdYlGn": ("#d7191c", "#fdae61", "#ffffbf", "#a6d96a", "#1a9641"),
    "Spectral": ("#d7191c", "#fdae61", "#ffffbf", "#abdda4", "#2b83ba"),
}


def color_ramp(name):
    """Colour ramp from the style library, or a built-in copy (styles never fall back to a
    single colour because a ramp was renamed, deleted or not loaded)."""
    ramp = QgsStyle.defaultStyle().colorRamp(name)
    if ramp is not None:
        return ramp
    colors = [QColor(c) for c in RAMPS[name]]
    stops = [QgsGradientStop(i / (len(colors) - 1), c) for i, c in enumerate(colors[1:-1], 1)]
    return QgsGradientColorRamp(colors[0], colors[-1], False, stops)


class IsochroneStyle(QgsProcessingLayerPostProcessorInterface):
    instance = None

    def postProcessLayer(self, layer, context, feedback):
        if not isinstance(layer, QgsVectorLayer):
            return
        idx = layer.fields().indexOf("minutes")
        if idx < 0:
            return
        values = sorted(v for v in layer.uniqueValues(idx) if v is not None)
        ramp = color_ramp("RdYlGn")
        cats = []
        for i, v in enumerate(values):
            sym = QgsSymbol.defaultSymbol(layer.geometryType())
            pos = 1 - i / max(len(values) - 1, 1)          # near = green, far = red
            sym.setColor(ramp.color(pos))
            sym.setOpacity(0.55)
            sym.symbolLayer(0).setStrokeColor(QColor(60, 60, 60, 160))
            cats.append(QgsRendererCategory(v, sym, f"{v:g} min"))
        layer.setRenderer(QgsCategorizedSymbolRenderer("minutes", cats))
        layer.triggerRepaint()

    @staticmethod
    def create():
        IsochroneStyle.instance = IsochroneStyle()
        return IsochroneStyle.instance


class ReachedRoadsStyle(QgsProcessingLayerPostProcessorInterface):
    instance = None

    def postProcessLayer(self, layer, context, feedback):
        if not isinstance(layer, QgsVectorLayer) or layer.fields().indexOf("t_end_min") < 0:
            return
        ramp = color_ramp("Spectral")
        r = QgsGraduatedSymbolRenderer("t_end_min")
        r.setClassificationMethod(QgsClassificationEqualInterval())
        sym = QgsSymbol.defaultSymbol(layer.geometryType())
        sym.setWidth(0.9)
        r.setSourceSymbol(sym)
        ramp.invert()                                        # near = blue, far = red
        r.setSourceColorRamp(ramp)
        r.updateClasses(layer, 6)
        for i, rng in enumerate(r.ranges()):
            r.updateRangeLabel(i, f"{rng.lowerValue():.1f} – {rng.upperValue():.1f} min")
        layer.setRenderer(r)
        layer.triggerRepaint()

    @staticmethod
    def create():
        ReachedRoadsStyle.instance = ReachedRoadsStyle()
        return ReachedRoadsStyle.instance


class RouteStyle(QgsProcessingLayerPostProcessorInterface):
    """Normal segments in red; wrong-way segments dashed black."""
    instance = None

    def postProcessLayer(self, layer, context, feedback):
        if not isinstance(layer, QgsVectorLayer) or layer.fields().indexOf("wrong_way") < 0:
            return
        cats = []
        for value, color, label, dashed in (("no", "#d62728", tr("allowed direction"), False),
                                            ("yes", "#111111", tr("wrong way"), True)):
            sym = QgsSymbol.defaultSymbol(layer.geometryType())
            sym.setColor(QColor(color))
            sym.setWidth(1.4)
            if dashed:
                sym.symbolLayer(0).setPenStyle(Qt.PenStyle.DashLine)
            cats.append(QgsRendererCategory(value, sym, label))
        layer.setRenderer(QgsCategorizedSymbolRenderer("wrong_way", cats))
        layer.triggerRepaint()

    @staticmethod
    def create():
        RouteStyle.instance = RouteStyle()
        return RouteStyle.instance


def point_symbol(color):
    return QgsMarkerSymbol.createSimple({"name": "circle", "color": color, "size": "3.4",
                                         "outline_color": "white", "outline_width": "0.6"})


def style_points(layer):
    """Origin green / destination red; any other point (isochrones) blue."""
    names = {f["name"] for f in layer.getFeatures()} if layer.featureCount() < 1000 else set()
    if names and names <= {tr("origin"), tr("destination")}:
        cats = [QgsRendererCategory(tr("origin"), point_symbol("#1a9641"), tr("origin")),
                QgsRendererCategory(tr("destination"), point_symbol("#d7191c"),
                                    tr("destination"))]
        layer.setRenderer(QgsCategorizedSymbolRenderer("name", cats))
    else:
        layer.renderer().setSymbol(point_symbol("#2b83ba"))


class PointsStyle(QgsProcessingLayerPostProcessorInterface):
    instance = None

    def postProcessLayer(self, layer, context, feedback):
        if isinstance(layer, QgsVectorLayer) and layer.fields().indexOf("name") >= 0:
            style_points(layer)
            layer.triggerRepaint()

    @staticmethod
    def create():
        PointsStyle.instance = PointsStyle()
        return PointsStyle.instance


def write_points(alg, parameters, key, context, points):
    """Optional point output with the points used: [(name, lat, lon)] in WGS84."""
    if parameters.get(key) is None:
        return None
    fields = QgsFields()
    fields.append(field("name", "str"))
    sink, dest_id = alg.parameterAsSink(parameters, key, context, fields, WKB_POINT, WGS84)
    if sink is None:
        return None
    for name, lat, lon in points:
        f = QgsFeature(fields)
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
        f.setAttributes([str(name)])
        sink.addFeature(f, FAST_INSERT)
    apply_style(context, dest_id, PointsStyle.create)
    return dest_id


def apply_style(context, dest_id, factory):
    if dest_id and context.willLoadLayerOnCompletion(dest_id):
        context.layerToLoadOnCompletionDetails(dest_id).setPostProcessor(factory())

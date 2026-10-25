# -*- coding: utf-8 -*-
"""Common base for the algorithms: lazy import of the core and output styles."""

import os

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingException,
                       QgsProcessingLayerPostProcessorInterface, QgsVectorLayer, QgsSymbol,
                       QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsStyle, QgsClassificationEqualInterval)

from .compat import tr

FOLDER = os.path.dirname(__file__)

INSTALL_HELP = (
    "import os, sys, subprocess\n"
    "subprocess.run([os.path.join(sys.prefix, 'python.exe'), '-m', 'pip', 'install', "
    "'--user', '--no-deps', 'osmnx'])")


def import_core():
    """Imports the core only when an algorithm runs, with a clear message if OSMnx is missing."""
    try:
        from . import core
        return core
    except ImportError as err:
        raise QgsProcessingException(
            tr("Missing library: {error}.\n\nInstall OSMnx into QGIS's Python from the Python "
               "Console (Plugins > Python Console), then restart QGIS:\n\n{code}\n\n"
               "On macOS/Linux use sys.executable instead of python.exe.")
            .format(error=err, code=INSTALL_HELP))


class AlgorithmBase(QgsProcessingAlgorithm):
    _name = ""

    def tr(self, text):
        return tr(text)

    def createInstance(self):
        return type(self)()

    def name(self):
        return self._name

    def group(self):
        return ""

    def groupId(self):
        return ""

    def icon(self):
        return QIcon(os.path.join(FOLDER, "icons", "icon.png"))


# =============================================================================
# Styles applied when an output layer is loaded into the project
# (the post-processor must stay alive, so the instance is kept on the class)
# =============================================================================
class IsochroneStyle(QgsProcessingLayerPostProcessorInterface):
    instance = None

    def postProcessLayer(self, layer, context, feedback):
        if not isinstance(layer, QgsVectorLayer):
            return
        idx = layer.fields().indexOf("minutes")
        if idx < 0:
            return
        values = sorted(v for v in layer.uniqueValues(idx) if v is not None)
        ramp = QgsStyle.defaultStyle().colorRamp("RdYlGn")
        cats = []
        for i, v in enumerate(values):
            sym = QgsSymbol.defaultSymbol(layer.geometryType())
            pos = 1 - i / max(len(values) - 1, 1)          # near = green, far = red
            sym.setColor(ramp.color(pos) if ramp else QColor("#3182bd"))
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
        ramp = QgsStyle.defaultStyle().colorRamp("Spectral")
        r = QgsGraduatedSymbolRenderer("t_end_min")
        r.setClassificationMethod(QgsClassificationEqualInterval())
        sym = QgsSymbol.defaultSymbol(layer.geometryType())
        sym.setWidth(0.9)
        r.setSourceSymbol(sym)
        if ramp:
            ramp.invert()                                    # near = blue, far = red
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


def apply_style(context, dest_id, factory):
    if dest_id and context.willLoadLayerOnCompletion(dest_id):
        context.layerToLoadOnCompletionDetails(dest_id).setPostProcessor(factory())

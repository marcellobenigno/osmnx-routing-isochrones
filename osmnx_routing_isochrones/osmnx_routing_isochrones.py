# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtCore import QCoreApplication, QLocale, QTranslator
from qgis.core import QgsApplication, QgsSettings, QgsMessageLog

from . import deps
from .base import install_message
from .compat import tr, MSG_WARNING
from .provider import OsmnxRoutingProvider


MENU = "OSMnx Routing & Isochrones"


def _locale():
    s = QgsSettings()
    loc = ""
    if s.value("locale/overrideFlag", False, type=bool):
        loc = s.value("locale/userLocale", "") or ""
    return loc or QLocale().name()          # e.g. 'pt_BR'


class OsmnxRoutingPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.translator = None
        self.actions = []
        self.panels = {}
        self._load_translation()

    def _load_translation(self):
        loc = _locale()
        folder = os.path.join(os.path.dirname(__file__), "i18n")
        candidates = [loc, loc[:2]] + (["pt_BR"] if loc.startswith("pt") else [])
        for code in candidates:
            path = os.path.join(folder, f"osmnx_routing_isochrones_{code}.qm")
            if os.path.exists(path):
                self.translator = QTranslator()
                if self.translator.load(path):
                    QCoreApplication.installTranslator(self.translator)
                break

    def initProcessing(self):
        self.provider = OsmnxRoutingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()
        self.check_dependencies()
        if self.iface is None:
            return
        try:
            from qgis.PyQt.QtGui import QAction         # Qt6
        except ImportError:
            from qgis.PyQt.QtWidgets import QAction     # Qt5
        from .map_tools import icon
        for key, text, tip in (
                ("route", tr("Route on the map (OSMnx)"),
                 tr("Click origin and destination on the map to calculate a route, with pan "
                    "and zoom free")),
                ("isochrones", tr("Isochrones on the map (OSMnx)"),
                 tr("Click points on the map to calculate isochrones, with pan and zoom "
                    "free"))):
            action = QAction(icon(), text, self.iface.mainWindow())
            action.setToolTip(tip)
            action.setObjectName(f"osmnx_{key}_action")
            action.triggered.connect(lambda checked=False, k=key: self.show_panel(k))
            self.iface.addToolBarIcon(action)
            self.iface.addPluginToVectorMenu(MENU, action)
            self.actions.append(action)

    def show_panel(self, key):
        """Opens the 'route' or 'isochrones' side panel and its map tool."""
        if key not in self.panels:
            from .map_tools import RoutePanel, IsochronePanel, RIGHT_AREA
            cls = RoutePanel if key == "route" else IsochronePanel
            self.panels[key] = cls(self.iface.mapCanvas(), self.iface.mainWindow())
            self.iface.addDockWidget(RIGHT_AREA, self.panels[key])
        self.panels[key].activate()

    def check_dependencies(self):
        """Warns once at start-up if OSMnx & co. are missing; the algorithms that need them
        stay visible but disabled (see AlgorithmBase.canExecute). Returns the missing names."""
        missing = deps.missing_modules()
        if not missing:
            return missing
        text = install_message(missing)
        QgsMessageLog.logMessage(text, "OSMnx Routing", MSG_WARNING)
        if self.iface is not None:
            from qgis.PyQt.QtWidgets import QMessageBox, QPushButton
            bar = self.iface.messageBar()
            msg = bar.createMessage("OSMnx Routing & Isochrones",
                                    tr("Missing Python libraries: {modules}.").format(
                                        modules=", ".join(missing)))
            button = QPushButton(tr("How to install"), msg)
            button.clicked.connect(lambda: QMessageBox.information(
                self.iface.mainWindow(), "OSMnx Routing & Isochrones", text))
            msg.layout().addWidget(button)
            bar.pushWidget(msg, MSG_WARNING, 0)
        return missing

    def unload(self):
        for panel in self.panels.values():
            panel.cleanup()
            self.iface.removeDockWidget(panel)
            panel.deleteLater()
        self.panels = {}
        for action in self.actions:
            self.iface.removeToolBarIcon(action)
            self.iface.removePluginVectorMenu(MENU, action)
        self.actions = []
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)
        if self.translator:
            QCoreApplication.removeTranslator(self.translator)

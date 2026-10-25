# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtCore import QCoreApplication, QLocale, QTranslator
from qgis.core import QgsApplication, QgsSettings

from .provider import OsmnxRoutingProvider


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

    def unload(self):
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)
        if self.translator:
            QCoreApplication.removeTranslator(self.translator)

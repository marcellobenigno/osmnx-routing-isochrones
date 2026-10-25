# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from .compat import tr
from .alg_download import DownloadNetwork
from .alg_inspect import InspectNetwork
from .alg_route import ShortestPath
from .alg_isochrones import Isochrones


class OsmnxRoutingProvider(QgsProcessingProvider):
    def loadAlgorithms(self):
        for cls in (DownloadNetwork, InspectNetwork, ShortestPath, Isochrones):
            self.addAlgorithm(cls())

    def id(self):
        return "osmnx_routing"

    def name(self):
        return "OSMnx Routing & Isochrones"

    def longName(self):
        return tr("OSMnx Routing & Isochrones — road network, one-way aware routing and "
                  "isochrones")

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), "icons", "icon.png"))

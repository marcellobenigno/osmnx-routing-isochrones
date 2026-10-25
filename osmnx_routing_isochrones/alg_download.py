# -*- coding: utf-8 -*-
import re
import unicodedata

from qgis.core import (QgsProcessingParameterString, QgsProcessingParameterEnum,
                       QgsProcessingParameterFileDestination, QgsProcessingOutputNumber,
                       QgsProcessingContext, QgsProcessingException, QgsVectorLayer)

from .base import AlgorithmBase, import_core
from .compat import tr

NETWORK_TYPES = ["all", "all_public", "drive", "drive_service", "walk", "bike"]


def _network_labels():
    return [tr("all — every road and path (incl. private)"),
            tr("all_public — every public road and path"),
            tr("drive — public drivable roads"),
            tr("drive_service — drivable roads + service roads"),
            tr("walk — pedestrian network"),
            tr("bike — cycling network")]


def qgis_proxies():
    """HTTP proxy from Settings > Options > Network, in the format used by requests."""
    from urllib.parse import quote
    from qgis.core import QgsSettings
    s = QgsSettings()
    if not s.value("proxy/proxyEnabled", False, type=bool):
        return None
    if s.value("proxy/proxyType", "") not in ("HttpProxy", "HttpCachingProxy"):
        return None                 # system/default proxy: requests reads the environment
    host = s.value("proxy/proxyHost", "")
    port = s.value("proxy/proxyPort", "")
    if not host:
        return None
    user, pwd = s.value("proxy/proxyUser", ""), s.value("proxy/proxyPassword", "")
    auth = f"{quote(user, safe='')}:{quote(pwd, safe='')}@" if user else ""
    url = f"http://{auth}{host}:{port}" if port else f"http://{auth}{host}"
    return {"http": url, "https": url}


def _slug(text):
    text = unicodedata.normalize("NFKD", text.split(",")[0]).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "network"


class DownloadNetwork(AlgorithmBase):
    PLACE, TYPE, OUTPUT = "PLACE", "TYPE", "OUTPUT"
    _name = "download_network"

    def displayName(self):
        return tr("1. Download road network (OSM)")

    def shortHelpString(self):
        return tr(
            "<p>Downloads the OpenStreetMap road network of a municipality (or any place "
            "Nominatim can geocode) and writes a GeoPackage with:</p>"
            "<ul><li><b>edges</b>: one line per street segment (for display);</li>"
            "<li><b>arcs</b>: one line per <i>direction of travel</i> (two-way street = 2 arcs, "
            "one-way street = 1 arc digitised in the direction of traffic), used for routing;</li>"
            "<li><b>nodes</b>: intersections;</li>"
            "<li><b>boundary</b>: polygon of the place.</li></ul>"
            "<p>Segments include <b>speed_kph</b> (OSM maxspeed or a default per road type) and "
            "<b>travel_time</b> (seconds).</p>"
            "<p>Include state and country in the name, e.g. <i>Campina Grande, Paraíba, "
            "Brazil</i>. Large cities may take several minutes.</p>"
            "<p>Data © OpenStreetMap contributors (ODbL).</p>")

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterString(
            self.PLACE, tr("Place name (as in OSM, with state and country)"),
            defaultValue="João Pessoa, Paraíba, Brazil"))
        self.addParameter(QgsProcessingParameterEnum(
            self.TYPE, tr("Network type"), options=_network_labels(), defaultValue=0))
        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, tr("Output GeoPackage"), fileFilter="GeoPackage (*.gpkg)"))
        self.addOutput(QgsProcessingOutputNumber("NODES", tr("Number of nodes")))
        self.addOutput(QgsProcessingOutputNumber("ARCS", tr("Number of directed arcs")))

    def processAlgorithm(self, parameters, context, feedback):
        core = import_core()
        place = self.parameterAsString(parameters, self.PLACE, context).strip()
        network_type = NETWORK_TYPES[self.parameterAsEnum(parameters, self.TYPE, context)]
        path = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        if not place:
            raise QgsProcessingException(tr("Enter a place name."))
        if not path.lower().endswith(".gpkg"):
            path += ".gpkg"
        proxies = qgis_proxies()
        if proxies:
            feedback.pushInfo(tr("Using the proxy configured in QGIS."))
        try:
            res = core.download_network(place, network_type, path, feedback, proxies)
        except core.Canceled:
            return {}
        except core.NetworkError as err:
            raise QgsProcessingException(str(err))
        except PermissionError:
            raise QgsProcessingException(
                tr("Could not overwrite {path}. Remove that file's layers from the project or "
                   "choose another name.").format(path=path))

        slug = _slug(place)
        for layer_name in ("boundary", "edges", "nodes", "arcs"):
            lyr = QgsVectorLayer(f"{path}|layername={layer_name}", f"{slug}_{layer_name}", "ogr")
            if lyr.isValid():
                context.temporaryLayerStore().addMapLayer(lyr)
                context.addLayerToLoadOnCompletion(
                    lyr.id(), QgsProcessingContext.LayerDetails(lyr.name(), context.project(),
                                                                self.OUTPUT))
        feedback.pushInfo(tr("The 'arcs' layer overlaps 'edges' on the map; switch it off if "
                             "you prefer."))
        return {self.OUTPUT: path, "NODES": res["nodes"], "ARCS": res["arcs"]}

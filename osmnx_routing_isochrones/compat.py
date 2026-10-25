# -*- coding: utf-8 -*-
"""Translation helper and enum aliases that work on QGIS 3.28+ (Qt5) and QGIS 4 (Qt6)."""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (Qgis, QgsProcessing, QgsProcessingParameterNumber, QgsWkbTypes,
                       QgsFeatureSink, QgsFeatureRequest, QgsField,
                       QgsCoordinateReferenceSystem)

CONTEXT = "OsmnxRouting"
WGS84 = QgsCoordinateReferenceSystem("EPSG:4326")


def tr(text):
    return QCoreApplication.translate(CONTEXT, text)


def _first(*candidates):
    """Returns the first attribute path that exists, e.g. ('Qgis', 'WkbType', 'LineString')."""
    for owner, *path in candidates:
        obj = owner
        try:
            for name in path:
                obj = getattr(obj, name)
            return obj
        except AttributeError:
            continue
    raise AttributeError(str(candidates[-1]))


NUMBER_DOUBLE = _first((Qgis, "ProcessingNumberParameterType", "Double"),
                       (QgsProcessingParameterNumber, "Double"))
SOURCE_POINT = _first((Qgis, "ProcessingSourceType", "VectorPoint"),
                      (QgsProcessing, "TypeVectorPoint"))
SOURCE_LINE = _first((Qgis, "ProcessingSourceType", "VectorLine"),
                     (QgsProcessing, "TypeVectorLine"))
SOURCE_POLYGON = _first((Qgis, "ProcessingSourceType", "VectorPolygon"),
                        (QgsProcessing, "TypeVectorPolygon"))
WKB_LINESTRING = _first((Qgis, "WkbType", "LineString"), (QgsWkbTypes, "LineString"))
WKB_MULTIPOLYGON = _first((Qgis, "WkbType", "MultiPolygon"), (QgsWkbTypes, "MultiPolygon"))
FAST_INSERT = _first((QgsFeatureSink, "Flag", "FastInsert"), (QgsFeatureSink, "FastInsert"))
NO_GEOMETRY = _first((Qgis, "FeatureRequestFlag", "NoGeometry"),
                     (QgsFeatureRequest, "NoGeometry"))


def field(name, kind):
    """QgsField for 'int', 'double' or 'str' (QMetaType on new QGIS, QVariant on old)."""
    try:
        from qgis.PyQt.QtCore import QMetaType
        t = {"int": QMetaType.Type.Int, "double": QMetaType.Type.Double,
             "str": QMetaType.Type.QString}[kind]
        return QgsField(name, t)
    except (TypeError, AttributeError, ImportError):
        from qgis.PyQt.QtCore import QVariant
        return QgsField(name, {"int": QVariant.Int, "double": QVariant.Double,
                               "str": QVariant.String}[kind])

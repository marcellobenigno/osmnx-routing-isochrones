# -*- coding: utf-8 -*-
import re

from qgis.core import (QgsProcessingParameterFile, QgsProcessingParameterEnum,
                       QgsProcessingParameterPoint, QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField, QgsProcessingParameterBoolean,
                       QgsProcessingParameterString, QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink, QgsProcessingException,
                       QgsCoordinateTransform, QgsFields, QgsFeature, QgsGeometry,
                       QgsCsException, QgsProcessingMultiStepFeedback)

from .base import (AlgorithmBase, import_core, apply_style, IsochroneStyle,
                   ReachedRoadsStyle, project_network, write_points)
from .compat import (tr, field, WGS84, NUMBER_DOUBLE, SOURCE_POINT, SOURCE_LINE,
                     SOURCE_POLYGON, WKB_LINESTRING, WKB_MULTIPOLYGON, FAST_INSERT)

PROFILES = ["drive", "walk"]
DIRECTIONS = ["from", "to"]
METHODS = ["roads", "concave"]


class Isochrones(AlgorithmBase):
    NETWORK, PROFILE, POINT, POINTS, ID_FIELD = "NETWORK", "PROFILE", "POINT", "POINTS", "ID_FIELD"
    SEPARATE, DIRECTION, MINUTES, METHOD = "SEPARATE", "DIRECTION", "MINUTES", "METHOD"
    BUFFER, WALK_SPEED, OUTPUT, ROADS = "BUFFER", "WALK_SPEED", "OUTPUT", "ROADS"
    USED_POINTS = "USED_POINTS"
    _name = "isochrones"
    _icon = "isochrones"

    def displayName(self):
        return tr("4. Isochrones (reachable areas)")

    def shortHelpString(self):
        return tr(
            "<p>Builds polygons of the areas reachable within each time (e.g. <b>5, 10, 15</b> "
            "min) over the road network.</p>"
            "<p><b>Points</b>: one point clicked on the map (… button) and/or a point layer "
            "(schools, health centres…). With <i>one isochrone per point</i> unchecked, the "
            "points form a single coverage area (the nearest one counts).</p>"
            "<p><b>Car</b>: travel time on the directed graph (one-way streets respected). "
            "<b>Direction</b>: <i>from</i> = where you can get to from the point; <i>to</i> = "
            "where the point can be reached from (matters with one-way streets).<br>"
            "<b>Pedestrian</b>: distance / walking speed, no direction.</p>"
            "<p><b>Method</b>: band around the reached roads (the last segment is cut in "
            "proportion to the remaining time) or concave hull of the reached nodes.</p>"
            "<p>Optional output <b>Reached roads</b>: each segment with its arrival time, "
            "great for gradient maps.</p>") + tr(
            "<p><b>Tip:</b> to click the points with pan and zoom free, use <b>Isochrones on "
            "the map (OSMnx)</b> on the Plugins toolbar or in Vector > OSMnx Routing & "
            "Isochrones.</p>")

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.NETWORK, tr("Road network GeoPackage"), extension="gpkg",
            defaultValue=project_network()))      # network already open in the project
        self.addParameter(QgsProcessingParameterEnum(
            self.PROFILE, tr("Profile"),
            options=[tr("Car — respects one-way streets"),
                     tr("Pedestrian — ignores street direction")], defaultValue=0))
        self.addParameter(QgsProcessingParameterPoint(
            self.POINT, tr("Point (click on the map)"), optional=True))
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.POINTS, tr("Point layer (optional)"), [SOURCE_POINT], optional=True))
        self.addParameter(QgsProcessingParameterField(
            self.ID_FIELD, tr("Field with the name of each point"),
            parentLayerParameterName=self.POINTS, optional=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.SEPARATE, tr("One isochrone per point (unchecked = combined coverage)"),
            defaultValue=False))
        self.addParameter(QgsProcessingParameterEnum(
            self.DIRECTION, tr("Direction (car)"),
            options=[tr("From the points (where you can get to)"),
                     tr("To the points (where they can be reached from)")], defaultValue=0))
        self.addParameter(QgsProcessingParameterString(
            self.MINUTES, tr("Times in minutes (comma separated)"), defaultValue="5, 10, 15"))
        self.addParameter(QgsProcessingParameterEnum(
            self.METHOD, tr("Polygon method"),
            options=[tr("Band around the reached roads (faithful to the network)"),
                     tr("Concave hull of the reached nodes (smoother)")], defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(
            self.BUFFER, tr("Band width around the roads (m)"), NUMBER_DOUBLE, 40,
            minValue=1, maxValue=1000))
        self.addParameter(QgsProcessingParameterNumber(
            self.WALK_SPEED, tr("Walking speed (km/h)"), NUMBER_DOUBLE, 4.8,
            minValue=1, maxValue=20))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT, tr("Isochrones"), SOURCE_POLYGON))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.ROADS, tr("Reached roads"), SOURCE_LINE, optional=True, createByDefault=True))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.USED_POINTS, tr("Isochrone points"), SOURCE_POINT, optional=True,
            createByDefault=True))

    def _points(self, parameters, context, feedback):
        points = []
        if parameters.get(self.POINT):
            p = self.parameterAsPoint(parameters, self.POINT, context, WGS84)
            points.append((tr("clicked point"), p.y(), p.x()))
        source = self.parameterAsSource(parameters, self.POINTS, context)
        if source is not None:
            if not source.sourceCrs().isValid():
                raise QgsProcessingException(tr(
                    "The point layer has no valid coordinate reference system (CRS). Set it in "
                    "Layer Properties > Source and run again."))
            id_field = self.parameterAsString(parameters, self.ID_FIELD, context)
            xform = QgsCoordinateTransform(source.sourceCrs(), WGS84, context.transformContext())
            for f in source.getFeatures():
                if feedback.isCanceled():
                    break
                g = f.geometry()
                if g.isNull() or g.isEmpty():
                    continue
                g = QgsGeometry(g)
                try:
                    g.transform(xform)
                except QgsCsException:
                    feedback.pushWarning(tr("Point fid {fid} skipped: it could not be converted "
                                            "to WGS84.").format(fid=f.id()))
                    continue
                pt = g.centroid().asPoint()
                label = str(f[id_field]) if id_field else f"fid {f.id()}"
                points.append((label, pt.y(), pt.x()))
        return points

    def processAlgorithm(self, parameters, context, feedback):
        core = import_core()
        gpkg = self.parameterAsFile(parameters, self.NETWORK, context)
        profile = PROFILES[self.parameterAsEnum(parameters, self.PROFILE, context)]
        direction = DIRECTIONS[self.parameterAsEnum(parameters, self.DIRECTION, context)]
        method = METHODS[self.parameterAsEnum(parameters, self.METHOD, context)]
        separate = self.parameterAsBoolean(parameters, self.SEPARATE, context)
        buffer_m = self.parameterAsDouble(parameters, self.BUFFER, context)
        walk = self.parameterAsDouble(parameters, self.WALK_SPEED, context)
        text = self.parameterAsString(parameters, self.MINUTES, context)
        try:   # accepts "5, 10, 15", "5;10;15" or "5 10 15" (decimals with a dot: 7.5)
            minutes = [float(x) for x in re.split(r"[;,\s]+", text.strip()) if x]
        except ValueError:
            raise QgsProcessingException(
                tr("Invalid times: '{text}'. Use e.g. 5, 10, 15").format(text=text))
        points = self._points(parameters, context, feedback)
        if not points:
            raise QgsProcessingException(tr("Give a point on the map and/or a point layer."))
        if profile == "walk" and direction == "to":
            feedback.pushInfo(tr("Pedestrians ignore direction: 'from' and 'to' are the same."))
        feedback.pushInfo(tr("{n} point(s) | times: {times} min | profile {profile} | "
                             "direction {direction} | method {method}").format(
            n=len(points), times=sorted(set(minutes)), profile=profile,
            direction=direction, method=method))

        steps = QgsProcessingMultiStepFeedback(3, feedback)    # load, compute, write
        try:
            net = core.load_network(gpkg, steps)
            steps.setCurrentStep(1)
            polys, roads = core.isochrones(net, points, minutes, profile, direction, walk,
                                           method, buffer_m, separate, steps)
        except core.Canceled:
            return {}
        except ValueError as err:
            raise QgsProcessingException(str(err))
        steps.setCurrentStep(2)
        total = max(len(polys) + len(roads), 1)

        fields = QgsFields()
        for name, kind in (("source", "str"), ("minutes", "double"), ("area_km2", "double"),
                           ("roads_km", "double"), ("profile", "str"), ("direction", "str")):
            fields.append(field(name, kind))
        sink, dest_id = self.parameterAsSink(parameters, self.OUTPUT, context, fields,
                                             WKB_MULTIPOLYGON, WGS84)
        for i, p in enumerate(polys):
            if feedback.isCanceled():
                break
            steps.setProgress(100 * i / total)
            f = QgsFeature(fields)
            g = QgsGeometry.fromWkt(p["geometry"].wkt)
            g.convertToMultiType()
            f.setGeometry(g)
            f.setAttributes([str(p["source"]), p["minutes"], round(p["area_km2"], 4),
                             round(p["roads_km"], 2), profile,
                             direction if profile == "drive" else "-"])
            sink.addFeature(f, FAST_INSERT)
            feedback.pushInfo(f"  {p['source']}: {p['minutes']:g} min -> {p['area_km2']:.2f} km²")
        result = {self.OUTPUT: dest_id}
        apply_style(context, dest_id, IsochroneStyle.create)

        if parameters.get(self.ROADS) is not None:
            rf = QgsFields()
            for name, kind in (("source", "str"), ("t_start_min", "double"),
                               ("t_end_min", "double")):
                rf.append(field(name, kind))
            sink_r, roads_id = self.parameterAsSink(parameters, self.ROADS, context, rf,
                                                    WKB_LINESTRING, WGS84)
            if sink_r is not None:
                for i, r in enumerate(roads):
                    if feedback.isCanceled():
                        break
                    if i % 1000 == 0:
                        steps.setProgress(100 * (len(polys) + i) / total)
                    f = QgsFeature(rf)
                    f.setGeometry(QgsGeometry.fromWkt(r["geometry"].wkt))
                    f.setAttributes([str(r["source"]), round(r["t_start_min"], 2),
                                     round(r["t_end_min"], 2)])
                    sink_r.addFeature(f, FAST_INSERT)
                result[self.ROADS] = roads_id
                apply_style(context, roads_id, ReachedRoadsStyle.create)
        points_id = write_points(self, parameters, self.USED_POINTS, context, points)
        if points_id:
            result[self.USED_POINTS] = points_id
        return result

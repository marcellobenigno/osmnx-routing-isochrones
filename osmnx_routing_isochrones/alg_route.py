# -*- coding: utf-8 -*-
from qgis.core import (QgsProcessingParameterFile, QgsProcessingParameterEnum,
                       QgsProcessingParameterPoint, QgsProcessingParameterBoolean,
                       QgsProcessingParameterNumber, QgsProcessingParameterFeatureSink,
                       QgsProcessingOutputNumber, QgsProcessingException, QgsFields,
                       QgsFeature, QgsGeometry, QgsProcessingMultiStepFeedback)

from .base import AlgorithmBase, import_core, apply_style, RouteStyle, project_network
from .compat import (tr, field, WGS84, NUMBER_DOUBLE, SOURCE_LINE, WKB_LINESTRING,
                     FAST_INSERT)

PROFILES = ["drive", "walk"]
CRITERIA = ["distance", "time"]


class ShortestPath(AlgorithmBase):
    NETWORK, PROFILE, CRITERION = "NETWORK", "PROFILE", "CRITERION"
    ORIGIN, DESTINATION, IGNORE_ONEWAY = "ORIGIN", "DESTINATION", "IGNORE_ONEWAY"
    WALK_SPEED, OUTPUT = "WALK_SPEED", "OUTPUT"
    _name = "shortest_path"

    def displayName(self):
        return tr("3. Shortest path (one-way aware)")

    def shortHelpString(self):
        return tr(
            "<p>Computes the route between two points on the road network GeoPackage. Use the "
            "<b>…</b> button next to Origin/Destination to click on the map.</p>"
            "<p><b>Car</b>: directed graph — one-way streets only in the allowed direction. "
            "Criterion distance (length) or time (travel_time, from OSM speed or a default per "
            "road type).<br><b>Pedestrian</b>: ignores direction; time from walking speed.</p>"
            "<p><b>Ignore one-way</b> (comparison): allows driving against traffic and flags "
            "those segments (field <i>wrong_way</i>, dashed black), showing the error of an "
            "undirected graph.</p>"
            "<p>Points snap to the nearest node of the largest connected component. For many "
            "routes, use <i>Run as Batch Process</i>.</p>")

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.NETWORK, tr("Road network GeoPackage"), extension="gpkg",
            defaultValue=project_network()))      # network already open in the project
        self.addParameter(QgsProcessingParameterEnum(
            self.PROFILE, tr("Profile"),
            options=[tr("Car — respects one-way streets"),
                     tr("Pedestrian — ignores street direction")], defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(
            self.CRITERION, tr("Criterion"),
            options=[tr("Shortest distance"), tr("Fastest (car only)")], defaultValue=0))
        self.addParameter(QgsProcessingParameterPoint(self.ORIGIN, tr("Origin")))
        self.addParameter(QgsProcessingParameterPoint(self.DESTINATION, tr("Destination")))
        self.addParameter(QgsProcessingParameterBoolean(
            self.IGNORE_ONEWAY, tr("Ignore one-way streets (comparison — allows wrong way)"),
            defaultValue=False))
        self.addParameter(QgsProcessingParameterNumber(
            self.WALK_SPEED, tr("Walking speed (km/h)"), NUMBER_DOUBLE, 4.8,
            minValue=1, maxValue=20))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, tr("Route"),
                                                            SOURCE_LINE))
        for name, desc in (("DISTANCE_KM", tr("Distance (km)")),
                           ("TIME_MIN", tr("Time (min)")),
                           ("WRONG_WAY_M", tr("Metres driven the wrong way"))):
            self.addOutput(QgsProcessingOutputNumber(name, desc))

    def processAlgorithm(self, parameters, context, feedback):
        core = import_core()
        gpkg = self.parameterAsFile(parameters, self.NETWORK, context)
        profile = PROFILES[self.parameterAsEnum(parameters, self.PROFILE, context)]
        criterion = CRITERIA[self.parameterAsEnum(parameters, self.CRITERION, context)]
        ignore = self.parameterAsBoolean(parameters, self.IGNORE_ONEWAY, context)
        walk = self.parameterAsDouble(parameters, self.WALK_SPEED, context)
        po = self.parameterAsPoint(parameters, self.ORIGIN, context, WGS84)
        pd_ = self.parameterAsPoint(parameters, self.DESTINATION, context, WGS84)
        if profile == "walk" and criterion == "time":
            feedback.pushInfo(tr("Pedestrian: shortest and fastest routes are the same."))

        steps = QgsProcessingMultiStepFeedback(3, feedback)    # load, route, write
        try:
            net = core.load_network(gpkg, steps)
            steps.setCurrentStep(1)
            gdf, s = core.route(net, (po.y(), po.x()), (pd_.y(), pd_.x()),
                                profile, criterion, ignore, walk)
        except core.Canceled:
            return {}
        except ValueError as err:
            raise QgsProcessingException(str(err))
        steps.setCurrentStep(2)

        fields = QgsFields()
        for name, kind in (("order", "int"), ("name", "str"), ("highway", "str"),
                           ("maxspeed", "str"), ("oneway", "str"), ("wrong_way", "str"),
                           ("length_m", "double"), ("speed_kmh", "double"), ("time_s", "double"),
                           ("cum_m", "double"), ("cum_min", "double")):
            fields.append(field(name, kind))
        sink, dest_id = self.parameterAsSink(parameters, self.OUTPUT, context, fields,
                                             WKB_LINESTRING, WGS84)
        cum_m = cum_s = 0.0
        for i, (_, t) in enumerate(gdf.iterrows(), start=1):
            if feedback.isCanceled():
                break
            steps.setProgress(100 * i / len(gdf))
            cum_m += float(t["length"])
            cum_s += float(t["travel_time"])
            f = QgsFeature(fields)
            f.setGeometry(QgsGeometry.fromWkt(t.geometry.wkt))
            f.setAttributes([i, core.as_text(t.get("name")), core.as_text(t.get("highway")),
                             core.as_text(t.get("maxspeed")),
                             "yes" if core.as_bool(t.get("oneway")) else "no",
                             "yes" if bool(t.get("wrong_way")) else "no",
                             round(float(t["length"]), 1), round(float(t["speed_kph"]), 1),
                             round(float(t["travel_time"]), 1),
                             round(cum_m, 1), round(cum_s / 60, 2)])
            sink.addFeature(f, FAST_INSERT)

        feedback.pushInfo("")
        if profile == "drive":
            feedback.pushInfo(tr("Distance: {km:.2f} km | Time: {min:.1f} min | {n} segments | "
                                 "{oneway} on one-way streets (allowed direction)").format(
                km=s["km"], min=s["min"], n=s["segments"], oneway=s["oneway"]))
        else:
            feedback.pushInfo(tr("Distance: {km:.2f} km | Time: {min:.1f} min | "
                                 "{n} segments").format(km=s["km"], min=s["min"],
                                                        n=s["segments"]))
        if s["wrong"]:
            feedback.pushWarning(tr("{n} segment(s) driven the WRONG WAY: {m:.0f} m").format(
                n=s["wrong"], m=s["wrong_m"]))
        if s["snap_orig_m"] > 150:
            feedback.pushWarning(tr("The origin is {dist:.0f} m from the nearest network "
                                    "node.").format(dist=s["snap_orig_m"]))
        if s["snap_dest_m"] > 150:
            feedback.pushWarning(tr("The destination is {dist:.0f} m from the nearest network "
                                    "node.").format(dist=s["snap_dest_m"]))
        apply_style(context, dest_id, RouteStyle.create)
        return {self.OUTPUT: dest_id, "DISTANCE_KM": s["km"], "TIME_MIN": s["min"],
                "WRONG_WAY_M": s["wrong_m"]}

# -*- coding: utf-8 -*-
import html
from collections import Counter

from qgis.core import (QgsProcessingParameterFile, QgsProcessingParameterFileDestination,
                       QgsProcessingException, QgsVectorLayer, QgsWkbTypes,
                       QgsCoordinateTransform, QgsFeatureRequest, NULL)

from .base import AlgorithmBase, project_network
from .compat import tr, WGS84, NO_GEOMETRY
from .layers import AmbiguousLayers, find_network_layers

COST_FIELDS = {"length", "maxspeed", "oneway", "highway", "lanes", "speed_kph",
               "travel_time", "from", "to", "u", "v", "key", "reversed", "direction", "mao"}
CSS = """<style>
body{font-family:Segoe UI,Arial,sans-serif;margin:24px;color:#222;max-width:1100px}
h1{font-size:22px} h2{font-size:17px;margin-top:28px;border-bottom:2px solid #ddd}
table{border-collapse:collapse;margin:8px 0;font-size:13px}
td,th{border:1px solid #ddd;padding:4px 8px;text-align:left;vertical-align:top}
th{background:#f3f3f3} .cost{background:#fff6d6} .ok{color:#1a7f37} .warn{color:#b35900}
.bar{background:#3182bd;height:10px;display:inline-block}
</style>"""


def _null(v):
    return v is None or v == NULL or (isinstance(v, str) and not v.strip())


def _e(v):
    return html.escape(str(v))


class InspectNetwork(AlgorithmBase):
    INPUT, OUTPUT = "INPUT", "OUTPUT"
    _name = "inspect_network"
    _needs_core = False

    def displayName(self):
        return tr("2. Inspect road network GeoPackage")

    def shortHelpString(self):
        return tr(
            "<p>Writes an HTML report with, for each layer: CRS, geometry type, extent, "
            "feature count, fields with type and <b>% filled</b> (cost attributes highlighted) "
            "and a data sample.</p>"
            "<p>It ends with a routing feasibility diagnosis: distance, speed, direction "
            "(one-way streets) and which direction source will be used.</p>")

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, tr("Road network GeoPackage"), extension="gpkg",
            defaultValue=project_network()))      # network already open in the project
        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT, tr("Report"), fileFilter="HTML (*.html)"))

    def _layer(self, gpkg, name, feedback, line_layers=()):
        lyr = QgsVectorLayer(f"{gpkg}|layername={name}", name, "ogr")
        if not lyr.isValid():
            return (f"<h2>{_e(name)}</h2><p class='warn'>{_e(tr('Invalid layer.'))}</p>", None)
        crs = lyr.crs()
        ew = QgsCoordinateTransform(crs, WGS84, lyr.transformContext()).transformBoundingBox(
            lyr.extent())
        names = lyr.fields().names()
        filled, oneway, hwy, total = Counter(), Counter(), Counter(), 0
        for f in lyr.getFeatures(QgsFeatureRequest().setFlags(NO_GEOMETRY)):
            total += 1
            for n in names:
                if not _null(f[n]):
                    filled[n] += 1
            if "oneway" in names:
                oneway[str(f["oneway"])] += 1
            if "highway" in names:
                hwy[str(f["highway"])] += 1
            if feedback.isCanceled():
                break

        h = [f"<h2>{_e(tr('Layer'))}: {_e(name)}</h2><table>"]
        rows = ((tr("CRS"), f"{crs.authid()} — {crs.description()}"),
                (tr("Units"), tr("degrees (geographic)") if crs.isGeographic()
                 else tr("metres (projected)")),
                (tr("Geometry"), QgsWkbTypes.displayString(lyr.wkbType())),
                (tr("Features"), f"{lyr.featureCount():,}"),
                (tr("Extent (WGS84)"), f"lon {ew.xMinimum():.5f} … {ew.xMaximum():.5f} | "
                                       f"lat {ew.yMinimum():.5f} … {ew.yMaximum():.5f}"))
        for k, v in rows:
            h.append(f"<tr><th>{_e(k)}</th><td>{_e(v)}</td></tr>")
        if not crs.isValid():
            note = tr("No CRS: EPSG:4326 will be assumed if the coordinates are lon/lat.")
            h.append(f"<tr><th></th><td class='warn'>{_e(note)}</td></tr>")
        h.append(f"</table><table><tr><th>{_e(tr('Field'))}</th><th>{_e(tr('Type'))}</th>"
                 f"<th>{_e(tr('Filled'))}</th><th></th></tr>")
        for c in lyr.fields():
            pct = 100 * filled[c.name()] / total if total else 0
            cls = " class='cost'" if c.name() in COST_FIELDS else ""
            h.append(f"<tr{cls}><td>{_e(c.name())}</td><td>{_e(c.typeName())}</td>"
                     f"<td>{pct:.1f}%</td><td><span class='bar' style='width:{pct:.0f}px'>"
                     "</span></td></tr>")
        h.append(f"</table><p style='font-size:12px'>"
                 f"{_e(tr('Highlighted rows: cost / direction attributes.'))}</p>")
        if oneway:
            h.append("<p><b>oneway:</b> " +
                     ", ".join(f"{_e(k)}: {n:,}" for k, n in oneway.most_common()) + "</p>")
        if hwy and name in line_layers:
            h.append(f"<table><tr><th>{_e(tr('highway (10 most common)'))}</th>"
                     f"<th>{_e(tr('segments'))}</th></tr>" +
                     "".join(f"<tr><td>{_e(k)}</td><td>{n:,}</td></tr>"
                             for k, n in hwy.most_common(10)) + "</table>")
        sample = list(lyr.getFeatures(QgsFeatureRequest().setLimit(3)))
        if sample:
            h.append(f"<table><tr><th>{_e(tr('Sample'))}</th>" +
                     "".join(f"<th>fid {f.id()}</th>" for f in sample) + "</tr>")
            for n in names:
                h.append(f"<tr><td>{_e(n)}</td>" +
                         "".join(f"<td>{_e(str(f[n])[:40])}</td>" for f in sample) + "</tr>")
            h.append("</table>")
        feedback.pushInfo(tr("{layer}: {crs}, {geom}, {n:,} features, {fields} fields").format(
            layer=name, crs=crs.authid(), geom=QgsWkbTypes.displayString(lyr.wkbType()),
            n=total, fields=len(names)))
        return "".join(h), {"filled": filled, "total": total, "fields": names}

    def processAlgorithm(self, parameters, context, feedback):
        gpkg = self.parameterAsFile(parameters, self.INPUT, context)
        out = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        from osgeo import ogr
        ds = ogr.Open(gpkg)
        if ds is None:
            raise QgsProcessingException(tr("Could not open {path}").format(path=gpkg))
        layers = [ds.GetLayer(i).GetName() for i in range(ds.GetLayerCount())]
        ds = None

        try:
            roles = find_network_layers(layers)
            ambiguous = ""
        except AmbiguousLayers as err:
            roles, ambiguous = {}, str(err)
        line_layers = tuple(roles[r] for r in ("edges", "arcs") if r in roles)
        parts, infos = [], {}
        for i, name in enumerate(layers):
            feedback.setProgress(100 * i / max(len(layers), 1))
            body, info = self._layer(gpkg, name, feedback, line_layers)
            parts.append(body)
            infos[name] = info

        arc_layer = roles.get("arcs")
        edges = infos.get(roles["edges"]) if "edges" in roles else None
        e = edges or (infos.get(arc_layer) if arc_layer else None)
        diag = [f"<h2>{_e(tr('Routing diagnosis'))}</h2><table>"]
        if e:
            def pct(c):
                return 100 * e["filled"][c] / e["total"] if c in e["fields"] and e["total"] else 0
            for label, p, note, always_ok in (
                    (tr("Distance (length)"), pct("length"),
                     tr("metres; cost of the shortest path"), False),
                    (tr("Speed (maxspeed)"), pct("maxspeed"),
                     tr("the rest is imputed from the road type"), True),
                    (tr("Road type (highway)"), pct("highway"),
                     tr("basis for speed imputation"), False),
                    (tr("Direction (oneway)"), pct("oneway"),
                     tr("defines one-way / two-way streets"), False)):
                cls = "ok" if p > 95 or always_ok else "warn"
                diag.append(f"<tr><th>{_e(label)}</th><td class='{cls}'>{p:.1f}%</td>"
                            f"<td>{_e(note)}</td></tr>")
                feedback.pushInfo(f"{label}: {p:.1f}%")
        if arc_layer:
            source = tr("<b>{layer}</b> layer (directed graph written at download) — most "
                        "reliable").format(layer=arc_layer)
        elif edges and {"from", "to"}.issubset(edges["fields"]):
            source = tr("rebuilt from <b>edges</b> (from/to + oneway)")
        else:
            source = tr("directed <b>edges</b> layer (u, v, key)")
        diag.append(f"<tr><th>{_e(tr('Direction source'))}</th><td colspan='2'>{source}</td>"
                    "</tr></table>")
        missing = [c for c in ("nodes", "edges") if c not in roles]
        if ambiguous:
            msg = tr("More than one road network in this GeoPackage ({layers}): keep a single "
                     "network per GeoPackage.").format(layers=ambiguous)
            diag.append(f"<p class='warn'>{_e(msg)}</p>")
        elif missing:
            msg = tr("Missing layers: {layers} — routing will not work.").format(
                layers=", ".join(missing))
            diag.append(f"<p class='warn'>{_e(msg)}</p>")

        with open(out, "w", encoding="utf-8") as f:
            f.write(f"<!doctype html><html><head><meta charset='utf-8'>"
                    f"<title>{_e(tr('Road network inspection'))}</title>{CSS}</head><body>"
                    f"<h1>{_e(tr('Road network inspection'))}</h1><p>{_e(gpkg)}</p>"
                    f"<p>{_e(tr('Layers'))}: {_e(', '.join(layers))}</p>"
                    f"{''.join(diag)}{''.join(parts)}</body></html>")
        return {self.OUTPUT: out}

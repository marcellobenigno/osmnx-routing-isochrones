# -*- coding: utf-8 -*-
"""
Core of the OSMnx Routing & Isochrones plugin.

Pure Python (no QGIS imports required): it can be tested outside QGIS and runs
safely in the Processing background thread.

  download_network()  OSM -> GeoPackage (nodes, edges, arcs, boundary)
  load_network()      GeoPackage -> DIRECTED graph + "free" graph (no one-way rules), cached
  route()             shortest path (distance or time) with one-way / wrong-way audit
  isochrones()        areas reachable within N minutes (from / to points)
"""

import os
import ast
import site
from datetime import datetime

try:                                    # translated messages when running inside QGIS
    from qgis.PyQt.QtCore import QCoreApplication

    def tr(text):
        return QCoreApplication.translate("OsmnxRouting", text)
except ImportError:                     # standalone use / tests
    def tr(text):
        return text


def prepare_environment():
    """Packages installed with 'pip --user' + correct PROJ data (Windows/QGIS)."""
    try:
        user_site = site.getusersitepackages()
        if os.path.isdir(user_site):
            site.addsitedir(user_site)
    except Exception:
        pass
    if os.environ.get("PROJ_DATA"):
        os.environ["PROJ_LIB"] = os.environ["PROJ_DATA"]


prepare_environment()

import numpy as np                      # noqa: E402
import pandas as pd                     # noqa: E402
import geopandas as gpd                 # noqa: E402
import shapely                          # noqa: E402
import networkx as nx                   # noqa: E402
import osmnx as ox                      # noqa: E402
from shapely.geometry import Point      # noqa: E402
from shapely.ops import substring       # noqa: E402

OSMNX_FOLDER = os.path.join(os.path.expanduser("~"), "osmnx")
ox.settings.cache_folder = os.path.join(OSMNX_FOLDER, "cache")
ox.settings.data_folder = os.path.join(OSMNX_FOLDER, "data")
ox.settings.logs_folder = os.path.join(OSMNX_FOLDER, "logs")
ox.settings.requests_timeout = 600
ox.settings.log_console = False

# Speeds (km/h) for roads without "maxspeed" (urban defaults; edit to suit your region)
DEFAULT_SPEEDS_KMH = {
    "motorway": 100, "motorway_link": 60, "trunk": 80, "trunk_link": 50,
    "primary": 60, "primary_link": 40, "secondary": 50, "secondary_link": 40,
    "tertiary": 40, "tertiary_link": 30, "unclassified": 30, "residential": 30,
    "living_street": 10, "service": 20, "road": 30,
}
FALLBACK_SPEED_KMH = 30
WALK_SPEED_KMH = 4.8

LIST_FIELDS = ("highway", "maxspeed", "lanes", "name", "ref", "access", "width", "osmid")
ARC_LAYERS = ("arcs", "arcos")          # 'arcos' = files made by the earlier scripts


class Canceled(Exception):
    pass


def _report(feedback, msg, progress=None):
    if feedback is None:
        print(msg)
        return
    if progress is not None:
        feedback.setProgress(progress)
    feedback.pushInfo(msg)
    if feedback.isCanceled():
        raise Canceled()


# =============================================================================
# Attribute conversions (GeoPackage stores OSM lists as text)
# =============================================================================
def _as_list(v):
    if isinstance(v, str) and v.startswith("["):
        try:
            return ast.literal_eval(v)
        except (ValueError, SyntaxError):
            return v
    return v


def as_bool(v):
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return False
    return str(v).strip().lower() in ("true", "1", "yes", "-1")


def as_text(v):
    if isinstance(v, (list, tuple, set)):
        return " / ".join(str(x) for x in v)
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return ""
    return str(v)


def _lists_to_text(gdf):
    for c in gdf.columns:
        if c != "geometry" and gdf[c].dtype == object:
            gdf[c] = gdf[c].map(lambda x: str(x) if isinstance(x, (list, dict, set)) else x)
    return gdf


def list_layers(gpkg):
    try:
        import pyogrio
        return [str(n) for n in pyogrio.list_layers(gpkg)[:, 0]]
    except ImportError:
        pass
    try:
        import fiona
        return list(fiona.listlayers(gpkg))
    except ImportError:
        from osgeo import ogr
        ds = ogr.Open(gpkg)
        return [ds.GetLayer(i).GetName() for i in range(ds.GetLayerCount())]


def arc_layer_name(layers):
    return next((n for n in ARC_LAYERS if n in layers), None)


# =============================================================================
# 1. DOWNLOAD
# =============================================================================
def add_costs(G):
    G = ox.routing.add_edge_speeds(G, hwy_speeds=DEFAULT_SPEEDS_KMH, fallback=FALLBACK_SPEED_KMH)
    return ox.routing.add_edge_travel_times(G)


def export_gpkg(G, path, boundary=None, metadata=None):
    """nodes + edges (undirected, for display) + arcs (directed, for routing) + boundary."""
    ox.save_graph_geopackage(G, filepath=path, directed=False)
    arcs = ox.graph_to_gdfs(G, nodes=False).reset_index()
    arcs["direction"] = arcs["oneway"].map(lambda x: "one-way" if as_bool(x) else "two-way")
    _lists_to_text(arcs).to_file(path, layer="arcs", driver="GPKG")
    if boundary is not None:
        b = boundary[["geometry"]].copy()
        for k, v in (metadata or {}).items():
            b[k] = v
        b.to_file(path, layer="boundary", driver="GPKG")
    return len(arcs)


class NetworkError(Exception):
    """Download problem with a message that can be shown to the user as is."""


def download_network(place, network_type, path, feedback=None, proxies=None):
    """proxies: optional {'http': url, 'https': url}, e.g. taken from the QGIS proxy settings."""
    old_kwargs = dict(ox.settings.requests_kwargs or {})
    if proxies:
        ox.settings.requests_kwargs = dict(old_kwargs, proxies=proxies)
    try:
        return _download(place, network_type, path, feedback)
    except Canceled:
        raise
    except Exception as err:            # translate the usual failures into clear messages
        import requests
        if isinstance(err, requests.exceptions.RequestException):
            raise NetworkError(tr(
                "Could not reach the OpenStreetMap servers (Nominatim/Overpass). Check your "
                "internet connection or the proxy in Settings > Options > Network, or try again "
                "later.\n\nDetails: {error}").format(error=err)) from err
        if type(err).__name__ == "InsufficientResponseError":
            raise NetworkError(tr(
                "No result for '{place}'. Check the spelling and include state and country, "
                "e.g. 'Campina Grande, Paraíba, Brazil'.\n\nDetails: {error}").format(
                place=place, error=err)) from err
        raise
    finally:
        ox.settings.requests_kwargs = old_kwargs


def _download(place, network_type, path, feedback):
    _report(feedback, tr("Geocoding: {place}").format(place=place), 5)
    boundary = ox.geocode_to_gdf(place)
    osm_name = str(boundary["display_name"].iloc[0]) if "display_name" in boundary else place
    _report(feedback, tr("Found: {name}").format(name=osm_name), 10)

    _report(feedback, tr("Downloading '{type}' network from Overpass "
                         "(this may take a few minutes)...").format(type=network_type), 15)
    G = ox.graph_from_polygon(boundary.union_all(), network_type=network_type,
                              retain_all=True, truncate_by_edge=True)
    _report(feedback, tr("{nodes:,} nodes and {arcs:,} arcs").format(
        nodes=G.number_of_nodes(), arcs=G.number_of_edges()), 70)

    G = add_costs(G)
    if os.path.exists(path):
        os.remove(path)
    _report(feedback, tr("Writing {path}").format(path=path), 80)
    n_arcs = export_gpkg(G, path, boundary, {
        "query": place, "osm_name": osm_name, "network_type": network_type,
        "downloaded_at": datetime.now().strftime("%Y-%m-%d %H:%M")})
    _report(feedback, tr("Done"), 100)
    return {"nodes": G.number_of_nodes(), "arcs": n_arcs, "osm_name": osm_name}


# =============================================================================
# 2. DIRECTED GRAPH FROM THE GEOPACKAGE
# =============================================================================
def _prepare(gdf):
    for c in LIST_FIELDS:
        if c in gdf.columns:
            gdf[c] = gdf[c].map(_as_list)
    gdf["oneway"] = gdf["oneway"].map(as_bool) if "oneway" in gdf.columns else False
    return gdf


def _read_nodes(gpkg):
    nodes = gpd.read_file(gpkg, layer="nodes")
    nodes["osmid"] = nodes["osmid"].astype("int64")
    return nodes.set_index("osmid")


def _directed_arcs(gdf, nodes):
    e = gdf.copy()
    e[["u", "v"]] = e[["u", "v"]].astype("int64")
    return e[e["u"].isin(nodes.index) & e["v"].isin(nodes.index)].copy()


def rebuild_arcs(edges, nodes):
    """Undirected export -> directed arcs: from->to always; to->from only if oneway=False."""
    crs = edges.crs
    e = edges.drop(columns=[c for c in ("u", "v", "key", "reversed") if c in edges.columns])
    e = e.rename(columns={"from": "u", "to": "v"})
    e[["u", "v"]] = e[["u", "v"]].astype("int64")
    e = e[e["u"].isin(nodes.index) & e["v"].isin(nodes.index)].copy()

    geoms = e.geometry.to_numpy()
    p0 = shapely.get_point(geoms, 0)
    x0, y0 = shapely.get_x(p0), shapely.get_y(p0)
    ux, uy = nodes.loc[e["u"], "x"].to_numpy(), nodes.loc[e["u"], "y"].to_numpy()
    vx, vy = nodes.loc[e["v"], "x"].to_numpy(), nodes.loc[e["v"], "y"].to_numpy()
    flipped = (x0 - ux) ** 2 + (y0 - uy) ** 2 > (x0 - vx) ** 2 + (y0 - vy) ** 2
    geoms[flipped] = shapely.reverse(geoms[flipped])
    e["geometry"] = gpd.GeoSeries(geoms, index=e.index, crs=crs)

    back = e[~e["oneway"]].copy()
    back[["u", "v"]] = back[["v", "u"]].to_numpy()
    back["geometry"] = gpd.GeoSeries(shapely.reverse(back.geometry.to_numpy()),
                                     index=back.index, crs=crs)
    arcs = gpd.GeoDataFrame(pd.concat([e, back], ignore_index=True),
                            geometry="geometry", crs=crs)
    return arcs, int(flipped.sum())


def graph_without_oneway(G):
    """Copy where every one-way arc gets its reverse, flagged wrong_way=True."""
    H = G.copy()
    for u, v, d in list(G.edges(data=True)):
        if d.get("oneway"):
            r = dict(d)
            r["geometry"] = shapely.reverse(d["geometry"])
            r["wrong_way"] = True
            H.add_edge(v, u, **r)
    return H


def _largest_component(G, strongly):
    comps = nx.strongly_connected_components(G) if strongly else nx.weakly_connected_components(G)
    return max(comps, key=len)


def _metric_crs(gdf):
    try:
        return gdf.estimate_utm_crs(datum_name="SIRGAS 2000") if _in_brazil(gdf) \
            else gdf.estimate_utm_crs()
    except Exception:
        return gdf.estimate_utm_crs()


def _in_brazil(gdf):
    x0, y0, x1, y1 = gdf.total_bounds
    return -74.5 <= x0 and x1 <= -28.5 and -34.5 <= y0 and y1 <= 6.0


_CACHE = {}


def load_network(gpkg, feedback=None):
    """Reads the GeoPackage once per session (re-reads if the file changes)."""
    key = (os.path.abspath(gpkg), os.path.getmtime(gpkg))
    if key in _CACHE:
        _report(feedback, tr("Network already loaded in this session (cache)."))
        return _CACHE[key]

    layers = list_layers(gpkg)
    for required in ("nodes", "edges"):
        if required not in layers:
            raise ValueError(tr("The GeoPackage has no '{layer}' layer.").format(layer=required))

    _report(feedback, tr("Reading nodes and edges..."))
    nodes = _read_nodes(gpkg)
    edges = _prepare(gpd.read_file(gpkg, layer="edges"))
    undirected = {"from", "to"}.issubset(edges.columns)
    arc_layer = arc_layer_name(layers)

    check = None
    if arc_layer:
        arcs = _directed_arcs(_prepare(gpd.read_file(gpkg, layer=arc_layer)), nodes)
        source = tr("'{layer}' layer (directed)").format(layer=arc_layer)
        if undirected:
            rec, _ = rebuild_arcs(edges, nodes)
            a, r = set(zip(arcs["u"], arcs["v"])), set(zip(rec["u"], rec["v"]))
            check = 100 * len(a & r) / max(len(a | r), 1)
    elif undirected:
        arcs, n_flip = rebuild_arcs(edges, nodes)
        source = tr("rebuilt from 'edges' (from/to + oneway; {n:,} geometries "
                    "re-oriented)").format(n=n_flip)
    else:
        arcs = _directed_arcs(edges, nodes)
        source = tr("directed 'edges' layer")

    arcs["wrong_way"] = False
    arcs["key"] = arcs.groupby(["u", "v"]).cumcount()
    arcs = arcs.drop(columns=[c for c in ("speed_kph", "travel_time") if c in arcs.columns])
    G = add_costs(ox.graph_from_gdfs(nodes, arcs.set_index(["u", "v", "key"])))
    G_free = graph_without_oneway(G)

    nodes_g = ox.graph_to_gdfs(G, edges=False)
    crs_m = _metric_crs(nodes_g)
    nodes_m = nodes_g.to_crs(crs_m)
    scc = _largest_component(G, True)
    wcc = _largest_component(G_free, False)

    net = {"gpkg": gpkg, "layers": layers, "source": source, "check": check,
           "G": G, "G_free": G_free, "G_rev": None, "crs_m": crs_m,
           "nodes_drive": nodes_m.loc[list(scc)], "nodes_free": nodes_m.loc[list(wcc)],
           "n_oneway": sum(1 for *_, d in G.edges(data=True) if d.get("oneway"))}
    _report(feedback, tr("Direction source: {source}").format(source=source))
    if check is not None:
        _report(feedback, tr("Cross-check arcs x rebuilt edges: {pct:.2f}% identical "
                             "u→v pairs").format(pct=check))
    _report(feedback, tr("{nodes:,} nodes | {arcs:,} arcs ({oneway:,} one-way) | largest "
                         "strongly connected component: {pct:.1f}% of nodes | metric CRS "
                         "{crs}").format(nodes=G.number_of_nodes(), arcs=G.number_of_edges(),
                                         oneway=net["n_oneway"],
                                         pct=100 * len(scc) / len(nodes_g),
                                         crs=crs_m.to_string()))
    _CACHE.clear()
    _CACHE[key] = net
    return net


def nearest_node(nodes_m, lat, lon):
    pt = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(nodes_m.crs)
    idx, dist = nodes_m.sindex.nearest(pt, return_all=False, return_distance=True)
    return int(nodes_m.index[idx[1][0]]), float(dist[0])


# =============================================================================
# 3. ROUTE
# =============================================================================
def route(net, orig, dest, profile="drive", criterion="distance",
          ignore_oneway=False, walk_kmh=WALK_SPEED_KMH):
    """orig/dest = (lat, lon). Returns (GeoDataFrame of segments, summary dict)."""
    directed = profile == "drive" and not ignore_oneway
    G = net["G"] if directed else net["G_free"]
    nodes = net["nodes_drive"] if directed else net["nodes_free"]
    o, snap_o = nearest_node(nodes, *orig)
    d, snap_d = nearest_node(nodes, *dest)

    weight = "travel_time" if (profile == "drive" and criterion == "time") else "length"
    path = ox.routing.shortest_path(G, o, d, weight=weight)
    if path is None:
        raise ValueError(tr("No path between the points (disconnected network)."))
    if len(path) < 2:
        raise ValueError(tr("Origin and destination snap to the same network node."))
    gdf = ox.routing.route_to_gdf(G, path, weight=weight).reset_index()

    gdf["wrong_way"] = gdf["wrong_way"].fillna(False).astype(bool)
    if profile != "drive":              # pedestrians may walk both ways
        gdf["speed_kph"] = walk_kmh
        gdf["travel_time"] = gdf["length"] / (walk_kmh / 3.6)
        gdf["wrong_way"] = False
    wrong = gdf["wrong_way"]
    oneway = gdf["oneway"].map(as_bool) & ~wrong
    summary = {"km": float(gdf["length"].sum()) / 1000,
               "min": float(gdf["travel_time"].sum()) / 60,
               "segments": len(gdf), "oneway": int(oneway.sum()),
               "wrong": int(wrong.sum()), "wrong_m": float(gdf.loc[wrong, "length"].sum()),
               "node_orig": o, "node_dest": d, "snap_orig_m": snap_o, "snap_dest_m": snap_d}
    return gdf, summary


# =============================================================================
# 4. ISOCHRONES
# =============================================================================
def _iso_graph(net, profile, direction):
    if profile != "drive":
        return net["G_free"], net["nodes_free"], False
    if direction == "to":
        if net["G_rev"] is None:
            net["G_rev"] = net["G"].reverse(copy=False)
        return net["G_rev"], net["nodes_drive"], True
    return net["G"], net["nodes_drive"], False


def _cut(geom, frac, reverse):
    """Part of an arc reached when only `frac` of it can be travelled."""
    return (substring(geom, 1 - frac, 1, normalized=True) if reverse
            else substring(geom, 0, frac, normalized=True))


def isochrones(net, points, minutes, profile="drive", direction="from",
               walk_kmh=WALK_SPEED_KMH, method="roads", buffer_m=40.0,
               separate=False, feedback=None):
    """
    points    : list of (label, lat, lon)
    minutes   : list of thresholds, e.g. [5, 10, 15]
    profile   : 'drive' (travel_time, one-way respected) | 'walk' (length / walking speed)
    direction : 'from' (reach starting at the points) | 'to' (where the points are reached from)
    method    : 'roads'   -> buffer around reached roads; last arc cut in proportion to the
                             remaining time (faithful to the network)
                'concave' -> concave hull of reached nodes (smoother)
    Returns (polygons, roads): lists of dicts with 'geometry' in EPSG:4326.
    """
    G, nodes_m, reverse = _iso_graph(net, profile, direction)
    minutes = sorted({float(m) for m in minutes if float(m) > 0})
    if not minutes:
        raise ValueError(tr("Enter at least one time (minutes) greater than zero."))
    if profile == "drive":
        weight, factor = "travel_time", 60.0               # seconds per minute
    else:
        weight, factor = "length", 60.0 * walk_kmh / 3.6   # metres per minute
    max_cut = minutes[-1] * factor

    snapped = []
    for label, lat, lon in points:
        node, snap = nearest_node(nodes_m, lat, lon)
        snapped.append((label, node))
        if snap > 300:
            _report(feedback, tr("Warning: point '{label}' is {dist:.0f} m away from the "
                                 "network.").format(label=label, dist=snap))
    if separate:
        groups = [(lbl, [n]) for lbl, n in snapped]
    else:
        label = (", ".join(str(lbl) for lbl, _ in snapped) if len(snapped) <= 5
                 else tr("{n} points").format(n=len(snapped)))
        groups = [(label, [n for _, n in snapped])]

    polygons, roads = [], []
    for gi, (label, sources) in enumerate(groups):
        _report(feedback, tr("Computing reach: {label}").format(label=label),
                int(100 * gi / len(groups)))
        dist = nx.multi_source_dijkstra_path_length(G, set(sources), cutoff=max_cut,
                                                    weight=weight)
        arcs = []                                   # arcs leaving reached nodes
        for u, tu in dist.items():
            for v, keys in G[u].items():
                data = min(keys.values(), key=lambda a: a.get(weight, np.inf))
                w = float(data.get(weight, np.nan))
                if np.isfinite(w) and w > 0:
                    arcs.append((tu, w, data["geometry"]))

        for m in reversed(minutes):                 # largest first (drawn underneath)
            cut = m * factor
            geoms = [g if tu + w <= cut else _cut(g, (cut - tu) / w, reverse)
                     for tu, w, g in arcs if tu < cut]
            if not geoms:
                continue
            lines_m = gpd.GeoSeries(geoms, crs="EPSG:4326").to_crs(net["crs_m"])
            if method == "concave":
                pts = [nodes_m.geometry.loc[n] for n, t in dist.items()
                       if t <= cut and n in nodes_m.index]
                pts += list(shapely.get_point(lines_m.to_numpy(), -1))
                poly = shapely.concave_hull(shapely.MultiPoint(pts), ratio=0.25)
                poly = poly.buffer(buffer_m / 2)
            else:
                poly = shapely.union_all(lines_m.buffer(buffer_m, quad_segs=4))
            poly_wgs = gpd.GeoSeries([poly], crs=net["crs_m"]).to_crs("EPSG:4326").iloc[0]
            polygons.append({"source": label, "minutes": m, "area_km2": poly.area / 1e6,
                             # length without counting two-way roads twice
                             "roads_km": shapely.union_all(lines_m.to_numpy()).length / 1000,
                             "geometry": poly_wgs})

        cut = max_cut
        for tu, w, g in arcs:
            if tu >= cut:
                continue
            if tu + w <= cut:
                geom, t_end = g, tu + w
            else:
                geom, t_end = _cut(g, (cut - tu) / w, reverse), cut
            roads.append({"source": label, "t_start_min": tu / factor,
                          "t_end_min": t_end / factor, "geometry": geom})
    return polygons, roads

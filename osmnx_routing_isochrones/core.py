# -*- coding: utf-8 -*-
"""
Core of the OSMnx Routing & Isochrones plugin.

Pure Python (no QGIS imports required): it can be tested outside QGIS and runs
safely in the Processing background thread.

  download_network()  OSM -> GeoPackage (nodes, edges, arcs, boundary)
  load_network()      GeoPackage -> DIRECTED graph + "free" graph (no one-way rules), cached
  route()             shortest path (distance or time) with one-way / wrong-way audit
  isochrones()        areas reachable within N minutes (from / to points)

Errors meant for the user are raised as ValueError / NetworkError with a readable message;
Canceled is raised when the Processing feedback asks to stop.
"""
from __future__ import annotations

import os
import ast
import threading
from datetime import datetime
from typing import Any

try:                                    # translated messages when running inside QGIS
    from qgis.PyQt.QtCore import QCoreApplication

    def tr(text):
        return QCoreApplication.translate("OsmnxRouting", text)
except ImportError:                     # standalone use / tests
    def tr(text):
        return text


from .deps import prepare_environment  # noqa: E402
from .layers import AmbiguousLayers, find_network_layers  # noqa: E402

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
MAX_SNAP_M = 5000                       # farther than this, a point is outside the network
CANCEL_EVERY = 2000                     # loop iterations between two cancel checks


_PROJ_CONTEXTS: dict[int, Any] = {}


def keep_proj_context() -> None:
    """
    Call at the start of each run in a worker thread. pyproj 3.7 keeps the PROJ context
    pointer in native thread storage, but frees the context with the *Python* thread state.
    QGIS runs Processing algorithms on reused pool threads with a new Python thread state each
    time, so the 2nd run on a thread would use a freed context and crash QGIS (segfault).
    Holding the context manager per native thread keeps the pointer valid.
    """
    try:
        import pyproj
        from pyproj import _context
        tid = threading.get_native_id()
        if tid in _PROJ_CONTEXTS:
            return
        pyproj.CRS("EPSG:4326")                     # creates this thread's context
        manager = _context.get_context_manager()
        if manager is not None:
            _PROJ_CONTEXTS[tid] = manager
    except Exception:                               # other pyproj versions: nothing to do
        pass


class Canceled(Exception):
    """The user pressed Cancel in the Processing dialog."""


def _check(feedback: Any, progress: float | None = None) -> None:
    """Updates the progress bar (0-100) and stops if the user canceled."""
    if feedback is None:
        return
    if progress is not None:
        feedback.setProgress(progress)
    if feedback.isCanceled():
        raise Canceled()


def _report(feedback: Any, msg: str, progress: float | None = None) -> None:
    """Message to the Processing log (or stdout without feedback) + progress/cancel check."""
    if feedback is None:
        print(msg)
        return
    feedback.pushInfo(msg)
    _check(feedback, progress)


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


def list_layers(gpkg: str) -> list[str]:
    """Layer names of a GeoPackage (pyogrio, fiona or GDAL, whichever is available)."""
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


# =============================================================================
# 1. DOWNLOAD
# =============================================================================
def add_costs(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """Adds speed_kph (OSM maxspeed or a default per road type) and travel_time (s)."""
    G = ox.routing.add_edge_speeds(G, hwy_speeds=DEFAULT_SPEEDS_KMH, fallback=FALLBACK_SPEED_KMH)
    return ox.routing.add_edge_travel_times(G)


def export_gpkg(G: nx.MultiDiGraph, path: str, boundary: gpd.GeoDataFrame | None = None,
                metadata: dict[str, str] | None = None) -> int:
    """
    Writes nodes + edges (undirected, for display) + arcs (directed, for routing) + boundary.
    Returns the number of directed arcs.
    """
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


def _is(err: BaseException, name: str) -> bool:
    """True if err is an instance of the OSMnx error class `name` (checked by name, as the
    module holding OSMnx's errors is private and has moved between versions)."""
    return any(c.__name__ == name for c in type(err).__mro__)


def _server_message(err: BaseException) -> str | None:
    """Readable message for connection / server failures, None for anything else."""
    import requests
    if isinstance(err, requests.exceptions.Timeout):
        return tr("The OpenStreetMap server took too long to answer (timeout). It may be "
                  "overloaded: try again in a few minutes, or use a smaller place.\n\n"
                  "Details: {error}").format(error=err)
    if isinstance(err, requests.exceptions.RequestException):
        return tr("Could not reach the OpenStreetMap servers (Nominatim/Overpass). Check your "
                  "internet connection or the proxy in Settings > Options > Network, or try "
                  "again later.\n\nDetails: {error}").format(error=err)
    if _is(err, "ResponseStatusCodeError"):
        return tr("The OpenStreetMap server refused or could not complete the request (it is "
                  "probably busy). Wait a few minutes and try again.\n\nDetails: {error}"
                  ).format(error=err)
    return None


def download_network(place: str, network_type: str, path: str, feedback: Any = None,
                     proxies: dict[str, str] | None = None) -> dict[str, Any]:
    """
    Downloads the OSM road network of `place` and writes it to the GeoPackage `path`.

    network_type : 'all', 'all_public', 'drive', 'drive_service', 'walk' or 'bike'
    proxies      : optional {'http': url, 'https': url}, e.g. from the QGIS proxy settings
    Returns {'nodes', 'arcs', 'osm_name'}. Raises NetworkError (readable message) when the
    servers cannot be reached, time out, refuse the request or return nothing.
    """
    old_kwargs = dict(ox.settings.requests_kwargs or {})
    if proxies:
        ox.settings.requests_kwargs = dict(old_kwargs, proxies=proxies)
    try:
        return _download(place, network_type, path, feedback)
    except (Canceled, NetworkError):
        raise
    except Exception as err:            # translate the usual failures into clear messages
        msg = _server_message(err)
        if msg is None:
            raise
        raise NetworkError(msg) from err
    finally:
        ox.settings.requests_kwargs = old_kwargs


def _geocode(place: str) -> gpd.GeoDataFrame:
    try:
        boundary = ox.geocode_to_gdf(place)
    except TypeError as err:            # found, but as a point or a line
        raise NetworkError(tr(
            "'{place}' was found, but OpenStreetMap has no boundary polygon for it. Use the name "
            "of a municipality, district or neighbourhood, e.g. 'Campina Grande, Paraíba, "
            "Brazil'.").format(place=place)) from err
    except Exception as err:
        if _server_message(err) is None and _is(err, "InsufficientResponseError"):
            raise NetworkError(tr(
                "No result for '{place}'. Check the spelling and include state and country, "
                "e.g. 'Campina Grande, Paraíba, Brazil'.\n\nDetails: {error}").format(
                place=place, error=err)) from err
        raise
    if boundary.empty:
        raise NetworkError(tr(
            "No result for '{place}'. Check the spelling and include state and country, "
            "e.g. 'Campina Grande, Paraíba, Brazil'.\n\nDetails: {error}").format(
            place=place, error="empty answer"))
    return boundary


def _graph(polygon: Any, network_type: str, osm_name: str) -> nx.MultiDiGraph:
    no_roads = tr("No '{type}' roads were found inside '{name}'. Try another network type or "
                  "a larger place.").format(type=network_type, name=osm_name)
    try:
        G = ox.graph_from_polygon(polygon, network_type=network_type,
                                  retain_all=True, truncate_by_edge=True)
    except Exception as err:
        # empty Overpass answer / nothing left after truncation (both ValueError subclasses)
        if _server_message(err) is None and (_is(err, "InsufficientResponseError")
                                             or type(err) is ValueError):
            raise NetworkError(f"{no_roads}\n\nDetails: {err}") from err
        raise
    if G.number_of_edges() == 0:
        raise NetworkError(no_roads)
    return G


def _download(place: str, network_type: str, path: str, feedback: Any) -> dict[str, Any]:
    _report(feedback, tr("Geocoding: {place}").format(place=place), 5)
    boundary = _geocode(place)
    osm_name = str(boundary["display_name"].iloc[0]) if "display_name" in boundary else place
    _report(feedback, tr("Found: {name}").format(name=osm_name), 10)

    _report(feedback, tr("Downloading '{type}' network from Overpass "
                         "(this may take a few minutes)...").format(type=network_type), 15)
    G = _graph(boundary.union_all(), network_type, osm_name)
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


def _to_wgs84(gdf: gpd.GeoDataFrame, layer: str, feedback: Any = None) -> gpd.GeoDataFrame:
    """The graph is built in EPSG:4326 (as OSMnx writes it); a layer saved in another CRS,
    e.g. reprojected to UTM by the user, is converted back. A layer that lost its CRS (e.g.
    saved from a temporary layer) is taken as EPSG:4326 when its coordinates are lon/lat."""
    if gdf.crs is None:
        x0, y0, x1, y1 = gdf.total_bounds
        if gdf.empty or (-180 <= x0 and x1 <= 180 and -90 <= y0 and y1 <= 90):
            _report(feedback, tr("Warning: the '{layer}' layer has no CRS; its coordinates look "
                                 "like longitude/latitude, so EPSG:4326 is assumed.").format(
                layer=layer))
            return gdf.set_crs("EPSG:4326")
        raise ValueError(tr("The '{layer}' layer has no coordinate reference system (CRS). "
                            "Assign one in QGIS (Layer Properties > Source) or download the "
                            "network again.").format(layer=layer))
    if gdf.crs.to_epsg() == 4326:
        return gdf
    _report(feedback, tr("'{layer}' layer is in {crs}: reprojecting to EPSG:4326.").format(
        layer=layer, crs=gdf.crs.to_string()))
    return gdf.to_crs("EPSG:4326")


def _require(gdf: gpd.GeoDataFrame, layer: str, columns: tuple[str, ...]) -> None:
    missing = [c for c in columns if c not in gdf.columns]
    if missing:
        raise ValueError(tr("The '{layer}' layer has no {fields} field(s): this does not look "
                            "like a road network written by this plugin or by OSMnx.").format(
            layer=layer, fields=", ".join(missing)))


def _read_nodes(gpkg: str, feedback: Any = None, layer: str = "nodes") -> gpd.GeoDataFrame:
    nodes = gpd.read_file(gpkg, layer=layer)
    _require(nodes, layer, ("osmid",))
    nodes = _to_wgs84(nodes, layer, feedback)
    nodes["x"], nodes["y"] = nodes.geometry.x, nodes.geometry.y   # match the geometry CRS
    nodes["osmid"] = nodes["osmid"].astype("int64")
    return nodes.set_index("osmid")


def _directed_arcs(gdf, nodes):
    e = gdf.copy()
    e[["u", "v"]] = e[["u", "v"]].astype("int64")
    return e[e["u"].isin(nodes.index) & e["v"].isin(nodes.index)].copy()


def rebuild_arcs(edges: gpd.GeoDataFrame,
                 nodes: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, int]:
    """Undirected export -> directed arcs: from->to always; to->from only if oneway=False.
    Returns (arcs, number of geometries that had to be re-oriented)."""
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


def graph_without_oneway(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
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


def load_network(gpkg: str, feedback: Any = None) -> dict[str, Any]:
    """
    Reads a road network GeoPackage into routing graphs, once per session (re-reads if the
    file changes).

    Returns a dict with, among others: 'G' (directed graph, one-way rules), 'G_free' (every
    one-way arc also reversed, flagged wrong_way), 'crs_m' (local metric CRS used for
    distances and buffers) and the snapping nodes in that CRS ('nodes_drive', 'nodes_free').
    Raises ValueError with a readable message for missing, unreadable or incomplete files.
    """
    if not gpkg or not os.path.isfile(gpkg):
        raise ValueError(tr("File not found: {path}").format(path=gpkg))
    key = (os.path.abspath(gpkg), os.path.getmtime(gpkg))
    if key in _CACHE:
        _report(feedback, tr("Network already loaded in this session (cache)."))
        return _CACHE[key]

    try:
        layers = list_layers(gpkg)
    except Exception as err:
        raise ValueError(tr("Could not open {path} as a GeoPackage.\n\nDetails: {error}").format(
            path=gpkg, error=err)) from err
    try:
        roles = find_network_layers(layers)
    except AmbiguousLayers as err:
        raise ValueError(tr("{path} holds more than one road network ({layers}). Keep a single "
                            "network per GeoPackage.").format(path=gpkg, layers=err)) from err
    for required in ("nodes", "edges"):
        if required not in roles:
            raise ValueError(tr("The GeoPackage has no '{layer}' layer.").format(layer=required))
    if roles["nodes"] != "nodes":
        _report(feedback, tr("Using layers {nodes} and {edges}.").format(
            nodes=roles["nodes"], edges=roles["edges"]))

    _report(feedback, tr("Reading nodes and edges..."), 5)
    nodes = _read_nodes(gpkg, feedback, roles["nodes"])
    edges = _prepare(_to_wgs84(gpd.read_file(gpkg, layer=roles["edges"]), roles["edges"],
                               feedback))
    if nodes.empty or edges.empty:
        raise ValueError(tr("The road network in {path} is empty.").format(path=gpkg))
    undirected = {"from", "to"}.issubset(edges.columns)
    arc_layer = roles.get("arcs")
    if not arc_layer:
        _require(edges, roles["edges"], ("from", "to") if undirected else ("u", "v"))
    _check(feedback, 30)

    check = None
    if arc_layer:
        arcs = gpd.read_file(gpkg, layer=arc_layer)
        _require(arcs, arc_layer, ("u", "v"))
        arcs = _directed_arcs(_prepare(_to_wgs84(arcs, arc_layer, feedback)), nodes)
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

    if arcs.empty:
        raise ValueError(tr("No arc of {path} connects two of its nodes: the network cannot be "
                            "used for routing.").format(path=gpkg))
    _check(feedback, 50)
    arcs["wrong_way"] = False
    arcs["key"] = arcs.groupby(["u", "v"]).cumcount()
    arcs = arcs.drop(columns=[c for c in ("speed_kph", "travel_time") if c in arcs.columns])
    G = add_costs(ox.graph_from_gdfs(nodes, arcs.set_index(["u", "v", "key"])))
    G_free = graph_without_oneway(G)
    _check(feedback, 75)

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
                                         crs=crs_m.to_string()), 100)
    _CACHE.clear()
    _CACHE[key] = net
    return net


def nearest_node(nodes_m: gpd.GeoDataFrame, lat: float, lon: float) -> tuple[int, float]:
    """Nearest network node to (lat, lon) in WGS84: (node id, distance in metres)."""
    pt = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(nodes_m.crs)
    idx, dist = nodes_m.sindex.nearest(pt, return_all=False, return_distance=True)
    return int(nodes_m.index[idx[1][0]]), float(dist[0])


def _far_message(what: str, dist_m: float) -> str:
    return tr("{what} is {km:.1f} km from the road network. Is it inside the area of the "
              "GeoPackage?").format(what=what, km=dist_m / 1000)


# =============================================================================
# 3. ROUTE
# =============================================================================
def route(net: dict[str, Any], orig: tuple[float, float], dest: tuple[float, float],
          profile: str = "drive", criterion: str = "distance", ignore_oneway: bool = False,
          walk_kmh: float = WALK_SPEED_KMH) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    """
    Shortest path between orig and dest, both (lat, lon) in WGS84.

    profile   : 'drive' (directed graph, one-way rules) | 'walk' (direction ignored)
    criterion : 'distance' (length) | 'time' (travel_time; car only)
    ignore_oneway : drive on the graph without one-way rules, flagging wrong-way segments
    Returns (GeoDataFrame of segments in EPSG:4326, summary dict). Raises ValueError when a
    point is outside the network or no path exists.
    """
    directed = profile == "drive" and not ignore_oneway
    G = net["G"] if directed else net["G_free"]
    nodes = net["nodes_drive"] if directed else net["nodes_free"]
    o, snap_o = nearest_node(nodes, *orig)
    d, snap_d = nearest_node(nodes, *dest)
    for what, dist_m in ((tr("The origin"), snap_o), (tr("The destination"), snap_d)):
        if dist_m > MAX_SNAP_M:
            raise ValueError(_far_message(what, dist_m))

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


def isochrones(net: dict[str, Any], points: list[tuple[str, float, float]],
               minutes: list[float], profile: str = "drive", direction: str = "from",
               walk_kmh: float = WALK_SPEED_KMH, method: str = "roads", buffer_m: float = 40.0,
               separate: bool = False,
               feedback: Any = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Areas reachable within each time threshold. Distances, cuts and buffers are computed in
    the network's local metric CRS (net['crs_m']); results come back in EPSG:4326.

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
    for i, (label, lat, lon) in enumerate(points):
        if i % CANCEL_EVERY == 0:
            _check(feedback)
        node, snap = nearest_node(nodes_m, lat, lon)
        if snap > MAX_SNAP_M:
            _report(feedback, tr("Warning: point '{label}' skipped: {msg}").format(
                label=label, msg=_far_message(tr("The point"), snap)))
            continue
        snapped.append((label, node))
        if snap > 300:
            _report(feedback, tr("Warning: point '{label}' is {dist:.0f} m away from the "
                                 "network.").format(label=label, dist=snap))
    if not snapped:
        raise ValueError(tr("No point is near the road network (all are more than {km:g} km "
                            "away). Check that the points and the GeoPackage cover the same "
                            "area.").format(km=MAX_SNAP_M / 1000))
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
        for i, (u, tu) in enumerate(dist.items()):
            if i % CANCEL_EVERY == 0:
                _check(feedback)
            for v, keys in G[u].items():
                data = min(keys.values(), key=lambda a: a.get(weight, np.inf))
                w = float(data.get(weight, np.nan))
                if np.isfinite(w) and w > 0:
                    arcs.append((tu, w, data["geometry"]))

        for k, m in enumerate(reversed(minutes)):   # largest first (drawn underneath)
            _check(feedback, 100 * (gi + (k + 1) / (len(minutes) + 1)) / len(groups))
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
                # shapely directly: GeoSeries.buffer(quad_segs=) breaks on geopandas >= 1.1
                poly = shapely.union_all(shapely.buffer(lines_m.to_numpy(), buffer_m,
                                                        quad_segs=4))
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

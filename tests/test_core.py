"""
Tests of the pure-Python core (no QGIS needed): directed graph rebuild, routing with one-way
streets and isochrones on a synthetic grid.

    python -m pytest -v tests/test_core.py
"""
import math
import os
import sys

import geopandas as gpd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from osmnx_routing_isochrones import core  # noqa: E402
import synthetic as S  # noqa: E402


@pytest.fixture(scope="module")
def graph():
    return core.add_costs(S.build_graph())


@pytest.fixture(scope="module")
def gpkg(graph, tmp_path_factory):
    path = str(tmp_path_factory.mktemp("core") / "grid.gpkg")
    core.export_gpkg(graph, path)
    return path


@pytest.fixture(scope="module")
def net(gpkg):
    core._CACHE.clear()
    return core.load_network(gpkg)


def test_layers_written(gpkg):
    assert {"nodes", "edges", "arcs"} <= set(core.list_layers(gpkg))


def test_loaded_graph_equals_original(net, graph):
    assert set(net["G"].edges()) == set(graph.edges())
    assert net["check"] == pytest.approx(100.0)
    assert net["n_oneway"] == sum(1 for *_, d in graph.edges(data=True) if d["oneway"])


def test_rebuild_from_undirected_edges(gpkg, graph):
    edges = core._prepare(gpd.read_file(gpkg, layer="edges"))
    nodes = core._read_nodes(gpkg)
    arcs, _ = core.rebuild_arcs(edges, nodes)
    assert set(zip(arcs.u, arcs.v)) == set(graph.edges())
    for _, r in arcs.iterrows():           # every geometry starts at its 'u' node
        x0, y0 = r.geometry.coords[0]
        assert math.isclose(x0, nodes.loc[r.u, "x"]) and math.isclose(y0, nodes.loc[r.u, "y"])


def test_legacy_arcos_layer(gpkg, tmp_path):
    legacy = str(tmp_path / "legacy.gpkg")
    for layer in ("nodes", "edges"):
        gpd.read_file(gpkg, layer=layer).to_file(legacy, layer=layer, driver="GPKG")
    gpd.read_file(gpkg, layer="arcs").to_file(legacy, layer="arcos", driver="GPKG")
    core._CACHE.clear()
    try:
        assert "'arcos'" in core.load_network(legacy)["source"]
    finally:
        core._CACHE.clear()


def test_drive_route_avoids_wrong_way(net):
    _, ok = core.route(net, S.latlon(2, 1), S.latlon(2, 0), "drive")
    _, wrong = core.route(net, S.latlon(2, 1), S.latlon(2, 0), "drive", ignore_oneway=True)
    assert ok["wrong"] == 0 and ok["km"] == pytest.approx(0.333, abs=1e-3)
    assert wrong["wrong"] == 1 and wrong["wrong_m"] == pytest.approx(111.0)


def test_walk_route_ignores_direction(net):
    gdf, s = core.route(net, S.latlon(2, 1), S.latlon(2, 0), "walk", walk_kmh=4.8)
    assert s["km"] == pytest.approx(0.111) and s["wrong"] == 0
    assert s["min"] == pytest.approx(0.111 / 4.8 * 60, rel=0.01)


def test_fastest_prefers_primary_roads(net):
    _, short = core.route(net, S.latlon(0, 0), S.latlon(7, 7), "drive", "distance")
    _, fast = core.route(net, S.latlon(0, 0), S.latlon(7, 7), "drive", "time")
    assert fast["min"] <= short["min"] and fast["km"] >= short["km"]


def test_same_node_raises(net):
    with pytest.raises(ValueError):
        core.route(net, S.latlon(3, 3), S.latlon(3, 3), "drive")


def test_isochrones_grow_with_time(net):
    polys, roads = core.isochrones(net, [("A", *S.latlon(3, 3))], [0.5, 1, 2])
    areas = {p["minutes"]: p["area_km2"] for p in polys}
    assert areas[0.5] < areas[1] < areas[2]
    assert all(r["t_end_min"] <= 2 + 1e-9 for r in roads)


def test_isochrones_from_and_to_differ(net):
    a, _ = core.isochrones(net, [("A", *S.latlon(3, 2))], [0.5], direction="from")
    b, _ = core.isochrones(net, [("A", *S.latlon(3, 2))], [0.5], direction="to")
    assert not a[0]["geometry"].equals(b[0]["geometry"])


def test_isochrones_separate_and_concave(net):
    pts = [("A", *S.latlon(2, 2)), ("B", *S.latlon(5, 5))]
    polys, _ = core.isochrones(net, pts, [2, 4], "walk", method="concave", separate=True)
    assert sorted({p["source"] for p in polys}) == ["A", "B"] and len(polys) == 4
    assert all(p["geometry"].is_valid for p in polys)


def test_isochrones_need_positive_time(net):
    with pytest.raises(ValueError):
        core.isochrones(net, [("A", *S.latlon(3, 3))], [0])


# =============================================================================
# Robustness: CRS, bad files, points outside the network, cancel, server errors
# =============================================================================
class FakeFeedback:
    """Minimal stand-in for QgsProcessingFeedback."""

    def __init__(self, cancel_after=None):
        self.messages, self.progress, self.calls, self.cancel_after = [], [], 0, cancel_after

    def pushInfo(self, msg):
        self.messages.append(msg)

    def setProgress(self, value):
        self.progress.append(value)

    def isCanceled(self):
        self.calls += 1
        return self.cancel_after is not None and self.calls > self.cancel_after


def test_projected_geopackage_is_reprojected(gpkg, net, tmp_path):
    """A GeoPackage re-saved in SIRGAS 2000 / UTM 25S must give the same graph and routes."""
    utm = str(tmp_path / "utm.gpkg")
    for layer in core.list_layers(gpkg):
        gdf = gpd.read_file(gpkg, layer=layer).to_crs("EPSG:31985")
        gdf.to_file(utm, layer=layer, driver="GPKG")
    core._CACHE.clear()
    fb = FakeFeedback()
    try:
        net_utm = core.load_network(utm, fb)
    finally:
        core._CACHE.clear()
    assert any("EPSG:31985" in m for m in fb.messages)
    assert set(net_utm["G"].edges()) == set(net["G"].edges())
    _, a = core.route(net, S.latlon(0, 0), S.latlon(7, 7), "drive", "time")
    _, b = core.route(net_utm, S.latlon(0, 0), S.latlon(7, 7), "drive", "time")
    assert b["km"] == pytest.approx(a["km"], rel=1e-3)
    assert b["snap_orig_m"] < 1
    polys, _ = core.isochrones(net_utm, [("A", *S.latlon(3, 3))], [1])
    assert -35 < polys[0]["geometry"].centroid.x < -34   # results are back in EPSG:4326


def test_missing_or_bad_file_raises_readable_error(tmp_path):
    with pytest.raises(ValueError, match="File not found"):
        core.load_network(str(tmp_path / "nope.gpkg"))
    bad = tmp_path / "bad.gpkg"
    bad.write_text("not a geopackage")
    with pytest.raises(ValueError, match="Could not open"):
        core.load_network(str(bad))


def test_geopackage_without_network_fields_raises(gpkg, tmp_path):
    other = str(tmp_path / "other.gpkg")
    for layer in ("nodes", "edges"):
        gdf = gpd.read_file(gpkg, layer=layer)[["geometry"]]
        gdf.to_file(other, layer=layer, driver="GPKG")
    core._CACHE.clear()
    with pytest.raises(ValueError, match="osmid"):
        core.load_network(other)


def test_geopackage_without_crs(gpkg, net, tmp_path):
    """Lon/lat layers that lost their CRS are taken as EPSG:4326; projected ones cannot be."""
    lonlat, utm = str(tmp_path / "lonlat.gpkg"), str(tmp_path / "utm_nocrs.gpkg")
    for layer in ("nodes", "edges", "arcs"):
        gdf = gpd.read_file(gpkg, layer=layer)
        gdf.set_crs(None, allow_override=True).to_file(lonlat, layer=layer, driver="GPKG")
        gdf.to_crs("EPSG:31985").set_crs(None, allow_override=True).to_file(
            utm, layer=layer, driver="GPKG")
    core._CACHE.clear()
    fb = FakeFeedback()
    try:
        assert set(core.load_network(lonlat, fb)["G"].edges()) == set(net["G"].edges())
        assert any("EPSG:4326 is assumed" in m for m in fb.messages)
        core._CACHE.clear()
        with pytest.raises(ValueError, match="coordinate reference system"):
            core.load_network(utm)
    finally:
        core._CACHE.clear()


def test_layers_saved_with_place_prefix_and_no_crs(gpkg, net, tmp_path):
    """The reported case: layers loaded by the download (patos_nodes, patos_edges...) saved
    into a new GeoPackage, without CRS."""
    copy = str(tmp_path / "patos.gpkg")
    for layer in ("nodes", "edges", "arcs"):
        gdf = gpd.read_file(gpkg, layer=layer).set_crs(None, allow_override=True)
        gdf.to_file(copy, layer=f"patos_{layer}", driver="GPKG")
    core._CACHE.clear()
    fb = FakeFeedback()
    try:
        net2 = core.load_network(copy, fb)
    finally:
        core._CACHE.clear()
    assert "'patos_arcs'" in net2["source"]
    assert set(net2["G"].edges()) == set(net["G"].edges())
    assert any("patos_nodes" in m for m in fb.messages)
    _, a = core.route(net, S.latlon(2, 1), S.latlon(2, 0))
    _, b = core.route(net2, S.latlon(2, 1), S.latlon(2, 0))
    assert b["km"] == pytest.approx(a["km"])


def test_find_network_layers():
    from osmnx_routing_isochrones.layers import AmbiguousLayers, find_network_layers as find
    assert find(["nodes", "edges", "arcs", "boundary"]) == {
        "nodes": "nodes", "edges": "edges", "arcs": "arcs", "boundary": "boundary"}
    assert find(["patos_nodes", "patos_edges", "patos_arcs", "patos_boundary"]) == {
        "nodes": "patos_nodes", "edges": "patos_edges", "arcs": "patos_arcs",
        "boundary": "patos_boundary"}
    assert find(["Patos_Nodes", "Patos_Edges"]) == {"nodes": "Patos_Nodes",
                                                    "edges": "Patos_Edges"}
    assert find(["nodes", "edges", "arcos"])["arcs"] == "arcos"
    # exact names win over a second, prefixed network
    assert find(["nodes", "edges", "x_nodes", "x_edges"])["nodes"] == "nodes"
    assert find(["nodes", "other"]) == {"nodes": "nodes"}
    with pytest.raises(AmbiguousLayers):
        find(["a_nodes", "a_edges", "b_nodes", "b_edges"])


def test_two_networks_in_one_geopackage_raise(gpkg, tmp_path):
    both = str(tmp_path / "both.gpkg")
    for prefix in ("a_", "b_"):
        for layer in ("nodes", "edges"):
            gpd.read_file(gpkg, layer=layer).to_file(both, layer=prefix + layer, driver="GPKG")
    core._CACHE.clear()
    with pytest.raises(ValueError, match="more than one road network"):
        core.load_network(both)


def test_route_point_outside_network_raises(net):
    far = (S.LAT0 + 1.0, S.LON0)                  # ~110 km north of the grid
    with pytest.raises(ValueError, match="km from the road network"):
        core.route(net, far, S.latlon(3, 3))
    with pytest.raises(ValueError, match="km from the road network"):
        core.route(net, S.latlon(3, 3), far)


def test_isochrones_skip_far_points(net):
    far = ("far", S.LAT0 + 1.0, S.LON0)
    fb = FakeFeedback()
    polys, _ = core.isochrones(net, [("A", *S.latlon(3, 3)), far], [1], feedback=fb)
    assert polys and all(p["source"] == "A" for p in polys)
    assert any("'far' skipped" in m for m in fb.messages)
    with pytest.raises(ValueError, match="No point is near the road network"):
        core.isochrones(net, [far], [1])


def test_isochrones_report_progress_and_can_be_canceled(net):
    fb = FakeFeedback()
    core.isochrones(net, [("A", *S.latlon(3, 3))], [0.5, 1, 2], feedback=fb)
    assert fb.progress and max(fb.progress) <= 100
    assert fb.progress == sorted(fb.progress)
    with pytest.raises(core.Canceled):
        core.isochrones(net, [("A", *S.latlon(3, 3))], [0.5, 1, 2],
                        feedback=FakeFeedback(cancel_after=1))


def test_load_network_can_be_canceled(gpkg):
    core._CACHE.clear()
    with pytest.raises(core.Canceled):
        core.load_network(gpkg, FakeFeedback(cancel_after=0))
    assert not core._CACHE


# --- download errors, without internet: OSMnx calls are replaced by stubs ---
def _boundary():
    from shapely.geometry import box
    return gpd.GeoDataFrame({"display_name": ["Test place"]},
                            geometry=[box(-34.9, -7.2, -34.8, -7.1)], crs="EPSG:4326")


def _raiser(err):
    def f(*args, **kwargs):
        raise err
    return f


@pytest.mark.parametrize("stage, error, expected", [
    ("geocode", "timeout", "took too long"),
    ("geocode", "connection", "Could not reach the OpenStreetMap servers"),
    ("geocode", "no_result", "No result for 'X'"),
    ("geocode", "not_polygon", "no boundary polygon"),
    ("graph", "status", "refused or could not complete"),
    ("graph", "timeout", "took too long"),
    ("graph", "no_result", "No 'drive' roads were found"),
    ("graph", "empty_graph", "No 'drive' roads were found"),
])
def test_download_errors_become_readable_messages(monkeypatch, tmp_path, stage, error, expected):
    import networkx as nx
    import requests
    from osmnx import _errors
    errors = {"timeout": requests.exceptions.ReadTimeout("read timed out"),
              "connection": requests.exceptions.ConnectionError("refused"),
              "no_result": _errors.InsufficientResponseError("nothing"),
              "not_polygon": TypeError("point"),
              "status": _errors.ResponseStatusCodeError("504 Gateway Timeout")}
    monkeypatch.setattr(core.ox, "geocode_to_gdf",
                        _raiser(errors[error]) if stage == "geocode" else lambda q: _boundary())
    if error == "empty_graph":
        monkeypatch.setattr(core.ox, "graph_from_polygon",
                            lambda *a, **k: nx.MultiDiGraph(crs="epsg:4326"))
    else:
        monkeypatch.setattr(core.ox, "graph_from_polygon", _raiser(errors.get(error)))
    with pytest.raises(core.NetworkError, match=expected):
        core.download_network("X", "drive", str(tmp_path / "x.gpkg"), FakeFeedback())
    assert not (tmp_path / "x.gpkg").exists()


def test_download_unexpected_errors_are_not_hidden(monkeypatch, tmp_path):
    monkeypatch.setattr(core.ox, "geocode_to_gdf", _raiser(KeyError("bug")))
    with pytest.raises(KeyError):
        core.download_network("X", "drive", str(tmp_path / "x.gpkg"))


def test_download_restores_proxy_settings(monkeypatch, tmp_path):
    before = dict(core.ox.settings.requests_kwargs or {})
    monkeypatch.setattr(core.ox, "geocode_to_gdf", _raiser(TypeError("point")))
    with pytest.raises(core.NetworkError):
        core.download_network("X", "drive", str(tmp_path / "x.gpkg"),
                              proxies={"http": "http://p:1", "https": "http://p:1"})
    assert dict(core.ox.settings.requests_kwargs or {}) == before


def test_download_writes_geopackage_from_stub(monkeypatch, tmp_path):
    monkeypatch.setattr(core.ox, "geocode_to_gdf", lambda q: _boundary())
    monkeypatch.setattr(core.ox, "graph_from_polygon", lambda *a, **k: S.build_graph())
    out = str(tmp_path / "x.gpkg")
    fb = FakeFeedback()
    res = core.download_network("X", "drive", out, fb)
    assert res["osm_name"] == "Test place" and res["arcs"] == S.build_graph().number_of_edges()
    assert {"nodes", "edges", "arcs", "boundary"} <= set(core.list_layers(out))
    assert fb.progress[-1] == 100


# --- dependency check ---
def test_missing_modules():
    from osmnx_routing_isochrones import deps
    assert deps.missing_modules() == []
    assert deps.missing_modules(("osmnx", "no_such_module_xyz")) == ["no_such_module_xyz"]

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

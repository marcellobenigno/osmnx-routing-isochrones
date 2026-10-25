"""Synthetic 8x8 street grid (~110 m blocks) near João Pessoa, with one-way streets.

Rows 0 and 7: two-way primary roads (maxspeed 60). Inner rows: one-way residential streets,
even rows eastbound, odd rows westbound. Columns 2 and 5: one-way northbound; others two-way.
"""
import networkx as nx
from shapely.geometry import LineString

LAT0, LON0, STEP, N = -7.12, -34.88, 0.001, 8


def node_id(i, j):
    return 1000 + i * N + j


def latlon(i, j):
    return LAT0 + i * STEP, LON0 + j * STEP


def build_graph():
    G = nx.MultiDiGraph(crs="epsg:4326")
    for i in range(N):
        for j in range(N):
            G.add_node(node_id(i, j), x=LON0 + j * STEP, y=LAT0 + i * STEP, street_count=4)
    way = [1]

    def street(a, b, oneway, hwy, maxspeed=None):
        ga = (G.nodes[a]["x"], G.nodes[a]["y"])
        gb = (G.nodes[b]["x"], G.nodes[b]["y"])
        mid = ((ga[0] + gb[0]) / 2 + 0.00002, (ga[1] + gb[1]) / 2)
        d = dict(osmid=way[0], highway=hwy, oneway=oneway, length=111.0,
                 name=f"Street {way[0]}")
        if maxspeed:
            d["maxspeed"] = maxspeed
        G.add_edge(a, b, key=0, reversed=False, geometry=LineString([ga, mid, gb]), **d)
        if not oneway:
            G.add_edge(b, a, key=0, reversed=True, geometry=LineString([gb, mid, ga]), **d)
        way[0] += 1

    for i in range(N):
        for j in range(N - 1):
            if i in (0, N - 1):
                street(node_id(i, j), node_id(i, j + 1), False, "primary", "60")
            elif i % 2 == 0:
                street(node_id(i, j), node_id(i, j + 1), True, "residential")
            else:
                street(node_id(i, j + 1), node_id(i, j), True, "residential")
    for j in range(N):
        for i in range(N - 1):
            street(node_id(i, j), node_id(i + 1, j), j in (2, 5),
                   "tertiary" if j % 3 == 0 else "residential")
    return G

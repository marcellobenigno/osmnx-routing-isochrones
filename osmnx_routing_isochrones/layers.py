# -*- coding: utf-8 -*-
"""
Finds the layers of a road network inside a GeoPackage. Pure Python, no QGIS or OSMnx.

The download writes nodes / edges / arcs / boundary, but loads them into the project as
<place>_nodes, <place>_edges...; saving those layers into another GeoPackage keeps the
prefixed names, so both forms are accepted.
"""
from __future__ import annotations

ARC_LAYERS = ("arcs", "arcos")          # 'arcos' = files made by the earlier scripts


class AmbiguousLayers(ValueError):
    """More than one network in the same GeoPackage."""


def find_network_layers(names: list[str]) -> dict[str, str]:
    """
    Maps 'nodes', 'edges', 'arcs' and 'boundary' to the actual layer names of one network.
    Missing roles are left out. Exact names win over prefixed ones ('patos_nodes'); raises
    AmbiguousLayers when several prefixed networks are found and none has exact names.
    """
    lower = {n.lower(): n for n in names}
    prefixes = {n[:-len("nodes")] for n in lower
                if n == "nodes" or n.endswith("_nodes")}
    prefixes = sorted(p for p in prefixes if p + "edges" in lower)
    if "" in prefixes:
        prefix = ""
    elif len(prefixes) == 1:
        prefix = prefixes[0]
    elif prefixes:
        raise AmbiguousLayers(", ".join(lower[p + "nodes"] for p in prefixes))
    else:                               # no pair: report whatever exact names exist
        prefix = ""
    found = {}
    for role, options in (("nodes", ("nodes",)), ("edges", ("edges",)),
                          ("arcs", ARC_LAYERS), ("boundary", ("boundary",))):
        name = next((lower[prefix + o] for o in options if prefix + o in lower), None)
        if name:
            found[role] = name
    return found

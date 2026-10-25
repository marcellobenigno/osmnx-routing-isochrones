# -*- coding: utf-8 -*-
def classFactory(iface):
    from .osmnx_routing_isochrones import OsmnxRoutingPlugin
    return OsmnxRoutingPlugin(iface)

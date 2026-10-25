# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/) and this project
follows [Semantic Versioning](https://semver.org/).

<!--

Unreleased

## version_tag - YYYY-MM-DD

### Added

### Changed

### Removed

-->

## 0.1.0 - 2026-10-25

- Initial development release.
- Download an OSM road network to a GeoPackage with a directed `arcs` layer.
- Inspection report (CRS, fields, fill rate, routing diagnosis).
- One-way aware shortest path (car: distance or time; pedestrian) with wrong-way audit.
- Isochrones from points or point layers (from/to, per point or combined, road band or
  concave hull) with reached roads and arrival times.
- Uses the QGIS proxy settings; clear messages when OSM servers cannot be reached, time out,
  refuse the request or return no data, and when a place has no boundary polygon.
- Dependency check at start-up: warning with install instructions; the algorithms that need
  OSMnx stay disabled until it is installed.
- Accepts GeoPackages whose layers were saved from the project with the place prefix
  (`patos_nodes`, `patos_edges`...), layers in another CRS (reprojected to EPSG:4326) and
  lon/lat layers that lost their CRS.
- Clear errors for missing or invalid files, two networks in one GeoPackage, point layers
  without CRS and points outside the network; warning when the download is saved to a
  temporary file.
- Step-by-step progress and cancellation in routing and isochrones.
- *Route on the map* tool: side panel + map tool, origin/destination by clicking, free pan
  and zoom between the clicks, route calculated in the background.
- Fixed: QGIS could crash on the 2nd background run of an algorithm (pyproj 3.7 freed its
  PROJ context while the reused worker thread still pointed to it).
- Fixed: band isochrones failed with geopandas 1.1.
- English interface with Brazilian Portuguese translation.

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
- Uses the QGIS proxy settings; clear messages when OSM servers cannot be reached.
- English interface with Brazilian Portuguese translation.

# OSMnx Routing & Isochrones

[![CI](https://github.com/marcellobenigno/osmnx-routing-isochrones/actions/workflows/ci.yml/badge.svg)](https://github.com/marcellobenigno/osmnx-routing-isochrones/actions/workflows/ci.yml)
![QGIS](https://img.shields.io/badge/QGIS-%E2%89%A5%203.28-589632)
![License](https://img.shields.io/badge/license-GPL--2.0--or--later-blue)

**Network routing and isochrone generation powered by [OSMnx](https://osmnx.readthedocs.io).**

A QGIS Processing plugin that downloads an OpenStreetMap street network to a GeoPackage and
then computes **one-way aware** routes and **isochrones** locally, with no routing web service
and no API key.

<!-- Screenshots / GIFs: put them in docs/images/ and uncomment
![Isochrones of schools](docs/images/isochrones.png)
![Route avoiding a one-way street](docs/images/route.gif)
-->

## Features

| Algorithm | What it does |
|---|---|
| **1. Download road network (OSM)** | Place name → GeoPackage with `edges` (display), `arcs` (directed: one feature per direction of travel), `nodes` and `boundary`. Speeds (`speed_kph`) and travel times (`travel_time`) included. Uses the QGIS proxy settings. |
| **2. Inspect road network GeoPackage** | HTML report: CRS, extent, fields, fill rate, data sample and a routing diagnosis. |
| **3. Shortest path (one-way aware)** | Car (directed graph; shortest or fastest) or pedestrian. An *ignore one-way* comparison flags the segments that would be driven the wrong way. |
| **4. Isochrones (reachable areas)** | From a clicked point or a point layer (schools, clinics…); *from* or *to* the points; one per point or combined coverage; road band or concave hull; optional *reached roads* layer with arrival times. |

Interface in English and Brazilian Portuguese (follows the QGIS language).

## Installation

**1. Install OSMnx in QGIS's Python** (once; no administrator rights needed).
QGIS already ships geopandas, networkx, shapely, pyproj and pandas, so only `osmnx` is added.
Open *Plugins → Python Console* and run:

```python
import os, sys, subprocess
py = os.path.join(sys.prefix, "python.exe") if os.name == "nt" else sys.executable
print(subprocess.run([py, "-m", "pip", "install", "--user", "--no-deps", "osmnx"],
                     capture_output=True, text=True).stdout)
```

Restart QGIS. If an import error mentions another missing package, run the same command
without `--no-deps`.

**2. Install the plugin**: *Plugins → Manage and Install Plugins*, search for
**OSMnx Routing & Isochrones** (tick *Show also experimental plugins* while it is
experimental), or *Install from ZIP* with a file from the
[releases](https://github.com/marcellobenigno/osmnx-routing-isochrones/releases).

## Quick start

1. Open the Processing Toolbox (`Ctrl+Alt+T`) → **OSMnx Routing & Isochrones**.
2. **Download road network**: e.g. `João Pessoa, Paraíba, Brazil`, type `drive`.
3. **Shortest path**: choose the GeoPackage, click the **…** buttons to pick origin and
   destination on the map. Run it again with *Ignore one-way streets* to see what an
   undirected graph would get wrong.
4. **Isochrones**: choose a point (or a point layer), times `5, 10, 15`.

All algorithms work in *Run as Batch Process* and in the Graphical Modeler, and from Python:

```python
import processing
processing.run("osmnx_routing:isochrones", {
    "NETWORK": "C:/data/malha_joao_pessoa_drive.gpkg", "PROFILE": 0,
    "POINT": "-34.8641,-7.1153 [EPSG:4326]", "MINUTES": "5, 10, 15",
    "OUTPUT": "TEMPORARY_OUTPUT", "ROADS": "TEMPORARY_OUTPUT"})
```

## How it works

- The `arcs` layer stores the directed graph: a two-way street becomes two arcs, a one-way
  street one arc digitised in the direction of traffic. Older files without it still work:
  direction is rebuilt from `from`/`to` + `oneway` in `edges`.
- Speeds come from OSM `maxspeed`, otherwise from defaults per road type
  (`DEFAULT_SPEEDS_KMH` in `core.py`).
- Car routes and isochrones snap to the largest strongly connected component, so a click on
  an isolated one-way cul-de-sac does not produce "no path".
- The network is read once per QGIS session and cached in memory.
- Not modelled: turn restrictions, traffic signals, live traffic.

## Contributing

Issues and pull requests are welcome. Repository layout:

```
osmnx_routing_isochrones/   the plugin (this folder is what goes in the ZIP)
  core.py                   pure Python: download, graph, routing, isochrones (no QGIS imports)
  alg_*.py                  Processing algorithms
  i18n/                     compiled translations (.ts/.qm)
translations/<lang>.json    translation sources
scripts/                    build_translations.py, make_zip.py
tests/                      test_core.py (no QGIS) and test_qgis.py (headless QGIS)
```

Development commands (Linux/macOS: `make help`; Windows: run the scripts with Python):

| Task | Command |
|---|---|
| Core tests (no QGIS) | `python -m pytest tests/test_core.py` |
| All tests in QGIS | `QT_QPA_PLATFORM=offscreen python -m pytest tests` (QGIS Python + osmnx) |
| Lint | `flake8 --max-line-length 110 osmnx_routing_isochrones scripts tests` |
| Compile translations | `python scripts/build_translations.py` (needs Qt `lrelease`) |
| Build ZIP | `python scripts/make_zip.py` → `dist/` |

**Translations**: copy `translations/pt_BR.json` to `translations/<lang>.json`, translate the
values (keep the `{placeholders}`), run `scripts/build_translations.py`. The script refuses to
build if a text is missing or a placeholder changed.

**Releases**: bump `version=` in `metadata.txt`, add an entry to `CHANGELOG.md`, commit, then
push a tag with the same number (`git tag 0.2.0 && git push --tags`). GitHub Actions builds the
ZIP with [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci), attaches it to a GitHub
release and, if the `OSGEO_USER`/`OSGEO_PASSWORD` secrets are set, uploads it to
plugins.qgis.org.

## License

[GPL-2.0-or-later](LICENSE). Map data © OpenStreetMap contributors, ODbL.

Author: Marcello Benigno Borges de Barros Filho — Tecnologia em Geoprocessamento, IFPB (Brazil).

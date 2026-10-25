# -*- coding: utf-8 -*-
"""
Dependency check that is cheap enough to run at plugin start-up: it only looks the modules up
(importlib.util.find_spec), it does not import OSMnx. Pure Python, no QGIS imports.
"""
from __future__ import annotations

import contextlib
import importlib
import importlib.util
import os
import site

REQUIRED = ("osmnx", "geopandas", "networkx", "shapely", "pandas", "numpy")

# Works in the QGIS Python Console on Windows, macOS and Linux: on macOS sys.executable is the
# QGIS application itself, so pip is called in-process instead of through a subprocess.
INSTALL_HELP = (
    "from pip._internal.cli.main import main as pip\n"
    "pip(['install', '--user', '--no-deps', 'osmnx'])")


def prepare_environment() -> None:
    """Packages installed with 'pip --user' + correct PROJ data (Windows/QGIS)."""
    with contextlib.suppress(Exception):
        user_site = site.getusersitepackages()
        if os.path.isdir(user_site):
            site.addsitedir(user_site)
    if os.environ.get("PROJ_DATA"):
        os.environ["PROJ_LIB"] = os.environ["PROJ_DATA"]


def missing_modules(names: tuple[str, ...] | None = None) -> list[str]:
    """Names of the required modules that cannot be found in QGIS's Python."""
    prepare_environment()
    importlib.invalidate_caches()           # picks up a 'pip install' made in this session
    missing = []
    for name in REQUIRED if names is None else names:
        try:
            found = importlib.util.find_spec(name) is not None
        except (ImportError, ValueError):
            found = False
        if not found:
            missing.append(name)
    return missing

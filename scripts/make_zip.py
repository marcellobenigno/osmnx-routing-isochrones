"""
Builds dist/osmnx_routing_isochrones-<version>.zip, ready for plugins.qgis.org.

    python scripts/make_zip.py            # compiles translations (needs lrelease) and zips
    python scripts/make_zip.py --no-i18n  # zips with the .qm files already in the repo

Works on Windows, macOS and Linux (no make required).
"""
import configparser
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = "osmnx_routing_isochrones"
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache"}
EXCLUDE_EXT = (".pyc", ".pyo", ".zip")


def main():
    if "--no-i18n" not in sys.argv:
        subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build_translations.py")],
                       check=True)
    meta = configparser.ConfigParser()
    meta.read(os.path.join(ROOT, PLUGIN, "metadata.txt"), encoding="utf-8")
    version = meta["general"]["version"]
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    out = os.path.join(ROOT, "dist", f"{PLUGIN}-{version}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for folder, dirs, files in os.walk(os.path.join(ROOT, PLUGIN)):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
            for f in sorted(files):
                if not f.endswith(EXCLUDE_EXT):
                    full = os.path.join(folder, f)
                    z.write(full, os.path.relpath(full, ROOT))
    print("written", out)


if __name__ == "__main__":
    main()

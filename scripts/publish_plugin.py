"""
Uploads the plugin ZIP to plugins.qgis.org: first with the plugin token (QGIS_TOKEN), then,
if that is missing or fails, with the OSGeo user name and password (OSGEO_USER /
OSGEO_PASSWORD). Used by .github/workflows/release.yml after qgis-plugin-ci has built the ZIP.

    python scripts/publish_plugin.py osmnx_routing_isochrones.<version>.zip

Requires qgis-plugin-ci (its upload functions are reused). Without any credential it does
nothing and exits 0.
"""
import os
import sys

from qgispluginci.release import upload_plugin_to_osgeo_with_token, upload_plugin_to_osgeo_xml_rpc

PACKAGE = "osmnx_routing_isochrones"


def upload(how, func, *args):
    """True when the upload worked (qgis-plugin-ci calls sys.exit on errors)."""
    print(f"Uploading to plugins.qgis.org with {how}")
    try:
        func(*args)
    except SystemExit as e:
        if e.code:
            print(f"::warning::Upload with {how} failed (exit {e.code})")
            return False
    return True


def main():
    archive = sys.argv[1]
    token = os.environ.get("QGIS_TOKEN")
    user, password = os.environ.get("OSGEO_USER"), os.environ.get("OSGEO_PASSWORD")
    if not token and not user:
        print("No QGIS_TOKEN or OSGEO_USER secret: plugins.qgis.org upload skipped")
        return
    if token and upload("the plugin token", upload_plugin_to_osgeo_with_token,
                        archive, PACKAGE, token):
        return
    if user and upload("the OSGeo user name and password", upload_plugin_to_osgeo_xml_rpc,
                       user, password, archive):
        return
    sys.exit("plugins.qgis.org upload failed")


if __name__ == "__main__":
    main()

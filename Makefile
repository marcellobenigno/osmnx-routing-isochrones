# Convenience targets for Linux/macOS. On Windows run the same Python scripts directly
# (OSGeo4W Shell):  python scripts\make_zip.py
PYTHON ?= python3
PLUGIN  = osmnx_routing_isochrones

.PHONY: help translations zip test test-qgis lint deploy clean

help:
	@echo "make translations  compile translations/*.json -> $(PLUGIN)/i18n/*.qm (needs lrelease)"
	@echo "make zip           build dist/$(PLUGIN)-<version>.zip for plugins.qgis.org"
	@echo "make test          core tests, no QGIS needed (needs osmnx + pytest)"
	@echo "make test-qgis     all tests inside a real headless QGIS (QGIS Python + osmnx + pytest)"
	@echo "make lint          flake8"
	@echo "make deploy        copy the plugin into your QGIS profile (QGIS_PLUGINS=... to override)"

translations:
	$(PYTHON) scripts/build_translations.py

zip:
	$(PYTHON) scripts/make_zip.py

test:
	$(PYTHON) -m pytest -v tests/test_core.py

test-qgis:
	QT_QPA_PLATFORM=offscreen $(PYTHON) -m pytest -v tests

lint:
	$(PYTHON) -m flake8 --max-line-length 110 $(PLUGIN) scripts tests

QGIS_PLUGINS ?= $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins
deploy:
	rm -rf "$(QGIS_PLUGINS)/$(PLUGIN)"
	cp -r $(PLUGIN) "$(QGIS_PLUGINS)/"

clean:
	rm -rf dist
	find . -name __pycache__ -prune -exec rm -rf {} +

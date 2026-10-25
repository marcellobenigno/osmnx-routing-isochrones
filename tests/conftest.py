"""
Headless QGIS tends to segfault while Python tears down QgsApplication and project objects at
interpreter exit, after every test has already passed. When QGIS was loaded, leave right after
pytest's report with its exit status, skipping that teardown.
"""
import os
import sys

_STATUS = {}


def pytest_sessionfinish(session, exitstatus):
    _STATUS["code"] = int(exitstatus)


def pytest_unconfigure(config):
    if "qgis.core" in sys.modules and "code" in _STATUS:
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(_STATUS["code"])

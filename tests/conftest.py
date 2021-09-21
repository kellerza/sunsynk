import os
import sys
from importlib import import_module as _import_module
from pathlib import Path

import pytest

#
# Pytest Mark: https://stackoverflow.com/a/61193490
#


def pytest_addoption(parser):
    parser.addoption("--addon", action="store_true", help="include the addon tests")


def pytest_configure(config):
    config.addinivalue_line("markers", "addon: include the addon tests")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--addon"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_addon = pytest.mark.skip(reason="need --addon option to run")
    for item in items:
        if "addon" in item.keywords:
            item.add_marker(skip_addon)


def import_module(mod_name, folder: str):
    """import_module."""
    here = Path(os.getcwd()) / folder
    sys.path.insert(0, str(here))
    try:
        mod_obj = _import_module(mod_name)
        return mod_obj
    finally:
        sys.path.pop(0)

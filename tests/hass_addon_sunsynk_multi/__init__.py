"""Add-on tests."""
from pathlib import Path

from tests.conftest import import_module

MOD_FOLDER = Path(__file__).parent.name.replace("_", "-")
run = import_module("run", MOD_FOLDER)
state = import_module("state", MOD_FOLDER)
sensors = import_module("sensors", MOD_FOLDER)

"""Add-on tests."""
from pathlib import Path

from tests.conftest import import_module

MOD_FOLDER = Path(__file__).parent.name.replace("_", "-")
filter = import_module("filter", MOD_FOLDER)
run = import_module("run", MOD_FOLDER)
state = import_module("state", MOD_FOLDER)

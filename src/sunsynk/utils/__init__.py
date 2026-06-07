"""Utilities."""

import importlib
import sys
from pathlib import Path
from types import ModuleType

from .pretty_table import pretty_table, pretty_table_sensors, table_data
from .stats import percentile

__all__ = ["percentile", "pretty_table", "pretty_table_sensors", "table_data"]


def import_module(mod_name: str, folder: str | Path | None = None) -> ModuleType:
    """import_module."""
    if folder:
        sys.path.insert(0, str(folder))
    try:
        mod_obj = importlib.import_module(mod_name)
        return mod_obj
    finally:
        if folder and sys.path[0] == str(folder):
            sys.path.pop(0)

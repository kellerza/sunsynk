"""Utilities."""

import sys
from importlib import import_module as _import_module
from pathlib import Path
from types import ModuleType


def import_module(mod_name: str, folder: str | Path | None = None) -> ModuleType:
    """import_module."""
    if folder:
        sys.path.insert(0, str(folder))
    try:
        mod_obj = _import_module(mod_name)
        return mod_obj
    finally:
        if folder and sys.path[0] == str(folder):
            sys.path.pop(0)

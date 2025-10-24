"""Utilities."""

import importlib
import sys
from collections.abc import Callable, Iterable
from pathlib import Path
from textwrap import wrap
from types import ModuleType
from typing import Any

from prettytable import PrettyTable


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


def ensure_str(v: Any) -> str:
    """Ensure a value is a string."""
    return "" if v is None else str(v)


def pretty_table[T](
    headers: list[str],
    data: list[list[T]],
    /,
    wrap_length: int = 80,
    to_str: Callable[[T], str] = ensure_str,
    calculated_cols: dict[str, Callable[[list[T]], str]] | None = None,
) -> PrettyTable:
    """Print a table."""
    for row_any in data:
        if len(row_any) > len(headers):
            headers.extend([f"Extra {i}" for i in range(len(headers), len(row_any))])

    table = PrettyTable()
    table.field_names = headers

    if calculated_cols:
        calculated_cols = dict(calculated_cols)  # copy
        for colname in list(calculated_cols):
            if colname not in headers:
                headers.append(colname)
            idx = headers.index(colname)
            calculated_cols[str(idx)] = calculated_cols.pop(colname)

    for row_any in data:
        row = [to_str(v) for v in row_any]
        if calculated_cols:
            for colidx, func in calculated_cols.items():
                row[int(colidx)] = func(row_any)

        if wrap_length == 0 or not any(len(v) > wrap_length for v in row):
            table.add_row(row)
            continue

        row_wrap = [wrap(v, wrap_length) for v in row]
        while any(row_wrap):
            table.add_row([r[0] if r else "" for r in row_wrap])
            row_wrap = [r[1:] for r in row_wrap]

    return table


def table_data[T](
    data: Iterable[dict[str, T]], /, headers: list[str] | None = None
) -> tuple[list[str], list[list[T | None]]]:
    """Convert a list of dictionaries to a table data format."""
    if headers is None:
        headers = list({k for v in data for k in v.keys()})
    return headers, [[v.get(k) for k in headers] for v in data]

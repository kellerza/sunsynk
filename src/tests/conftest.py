"""Global fixtures."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from sunsynk.state import InverterState

# Pytest Mark: https://stackoverflow.com/a/61193490
MARKERS = ("mqtt",)


def pytest_addoption(parser: Any) -> None:
    """Support command line marks."""
    for mrk in MARKERS:
        parser.addoption(
            f"--{mrk}", action="store_true", help=f"include the {mrk} tests"
        )


def pytest_configure(config: Any) -> None:
    """Enable configuration."""
    for mrk in MARKERS:
        config.addinivalue_line("markers", f"{mrk}: include the {mrk} tests")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip tests."""
    for mrk in MARKERS:
        if not config.getoption(f"--{mrk}", None):
            skip_mrk = pytest.mark.skip(reason=f"need --{mrk} option to run")
            for item in items:
                if mrk in item.keywords:
                    item.add_marker(skip_mrk)


@pytest.fixture
def state() -> InverterState:
    """Sunsynk inverter state."""
    return InverterState(onchange=MagicMock())

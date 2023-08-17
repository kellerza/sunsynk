"""Global fixtures."""
from unittest.mock import MagicMock

import pytest

from sunsynk.state import InverterState


@pytest.fixture
def state() -> InverterState:
    return InverterState(onchange=MagicMock())

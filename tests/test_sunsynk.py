import pytest

from sunsynk.sunsynk import Sunsynk

pytestmark = pytest.mark.asyncio


def test_ss():
    assert Sunsynk()

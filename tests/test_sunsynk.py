import pytest

from sunsynk.sunsynk import Sunsynk

pytestmark = pytest.mark.asyncio


async def test_ss():
    s = Sunsynk()
    with pytest.raises(ConnectionError):
        await s.connect()

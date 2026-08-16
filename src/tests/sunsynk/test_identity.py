"""Tests for sunsynk.identity.Identity."""

from __future__ import annotations

from sunsynk.identity import Identity, suggested_sensor_definitions


class _FakeUnit:
    """Minimal HoldingUnit returning a fixed identity block."""

    connected = True

    def __init__(self, regs: list[int]) -> None:
        self._regs = regs

    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        return self._regs[address : address + count]


def _serial_regs(text: str) -> list[int]:
    """Pack ASCII into five holding registers (two chars per word)."""
    padded = (text + "\0" * 10)[:10]
    return [(ord(padded[i]) << 8) | ord(padded[i + 1]) for i in range(0, 10, 2)]


async def test_identity_decode() -> None:
    """Identity Component decodes device type, protocol, and serial."""
    regs = [0] * 8
    regs[0] = 3
    regs[2] = 0x0102
    regs[3:8] = _serial_regs("ABCDE12345")

    identity = Identity(_FakeUnit(regs))  # type: ignore[arg-type]
    await identity.async_update()

    assert identity.device_type_code == 3
    assert identity.device_type == "Single-phase hybrid"
    assert identity.protocol == "1.2"
    assert identity.serial == "ABCDE12345"
    assert suggested_sensor_definitions(3) == "single-phase"
    assert suggested_sensor_definitions(0x601) == "three-phase-hv"
    assert suggested_sensor_definitions(4) == "single-phase"
    assert suggested_sensor_definitions(0x999) == "single-phase"


async def test_identity_unknown_device_type() -> None:
    """Unknown device type code gets a fallback label; defs default to single-phase."""
    regs = [0x999] + [0] * 7
    identity = Identity(_FakeUnit(regs))  # type: ignore[arg-type]
    await identity.async_update()
    assert identity.device_type_code == 0x999
    assert identity.device_type == "Unknown (0x999)"
    assert suggested_sensor_definitions(identity.device_type_code) == "single-phase"

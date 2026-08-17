"""Tests for PVDynamicTotalSensor."""

from sunsynk import WATT
from sunsynk.definitions import COMMON
from sunsynk.sensors import PVDynamicTotalSensor, Sensor


def _pv_defs() -> dict[str, Sensor]:
    return {
        "pv1_power": Sensor(186, "PV1 power", WATT, -1),
        "pv2_power": Sensor(187, "PV2 power", WATT, -1),
        "pv3_power": Sensor(188, "PV3 power", WATT, -1),
    }


def test_common_lists_pv1_to_pv8() -> None:
    """One shared pv_power on COMMON; missing profile MPPTs are skipped."""
    total = COMMON.all["pv_power"]
    assert isinstance(total, PVDynamicTotalSensor)
    assert total.source_ids == tuple(f"pv{i}_power" for i in range(1, 9))


def test_resolve_subset() -> None:
    """pv1 + pv2 + pv_power → only those two registers; pv3-8 absent or unused."""
    defs = _pv_defs()
    total = PVDynamicTotalSensor(0, "PV power", WATT)
    pv1, pv2 = defs["pv1_power"], defs["pv2_power"]
    hidden = total.resolve(defs, {pv1, pv2, total})

    assert total.address == (186, 187)
    assert total.factors == (-1, -1)
    assert hidden == ()


def test_resolve_pv_power_only() -> None:
    """pv_power alone → all *defined* sources as hidden deps (not pv4-8)."""
    defs = _pv_defs()
    total = PVDynamicTotalSensor(0, "PV power", WATT)
    hidden = total.resolve(defs, {total})

    assert total.address == (186, 187, 188)
    assert hidden == tuple(defs.values())


def test_reg_to_value_hv_scale() -> None:
    """HV x10 sources decode like individual sensors."""
    defs = {
        "pv1_power": Sensor(672, "PV1 power", WATT, 10),
        "pv2_power": Sensor(673, "PV2 power", WATT, 10),
    }
    total = PVDynamicTotalSensor(0, "PV power", WATT)
    total.resolve(defs, set(defs.values()) | {total})

    assert total.reg_to_value((100, 50)) == 1500

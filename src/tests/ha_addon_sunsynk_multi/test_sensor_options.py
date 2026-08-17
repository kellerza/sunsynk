"""States."""

import logging

from ha_addon_sunsynk_multi.sensor_options import DEFS, OPT, SOPT, import_definitions

_LOG = logging.getLogger(__name__)


def _reload_defs(profile: str) -> None:
    OPT.sensor_definitions = profile
    import_definitions()


def test_pv_power_resolves_hidden_deps() -> None:
    """pv_power only adds hidden pvN_power sensors."""
    _reload_defs("single-phase")
    OPT.sensors = ["pv_power"]
    OPT.sensors_first_inverter = []
    SOPT.init_sensors()

    assert "pv_power" in {s.id for s in SOPT if SOPT[s].visible}
    hidden = {s.id for s in SOPT if not SOPT[s].visible}
    assert {"pv1_power", "pv2_power", "pv3_power"} <= hidden
    pv_total = DEFS.all["pv_power"]
    assert pv_total.address == (186, 187, 188)


def test_pv_power_subset_registers() -> None:
    """pv1 + pv_power reads only pv1 register for the total."""
    _reload_defs("three-phase")
    OPT.sensors = ["pv1_power", "pv_power"]
    OPT.sensors_first_inverter = []
    SOPT.init_sensors()

    pv_total = DEFS.all["pv_power"]
    assert pv_total.address == (672,)


def test_pv_power_hv_all_mppts() -> None:
    """HV pv_power alone tracks pv1-8."""
    _reload_defs("three-phase-hv")
    OPT.sensors = ["pv_power"]
    OPT.sensors_first_inverter = []
    SOPT.init_sensors()

    pv_total = DEFS.all["pv_power"]
    assert pv_total.address == (672, 673, 674, 675, 727, 728, 729, 730)


def test_power_flow_card_plus_pv1() -> None:
    """power_flow_card includes pv_power; pv1 limits the total to that MPPT."""
    _reload_defs("single-phase")
    OPT.sensors = ["power_flow_card", "pv1"]
    OPT.sensors_first_inverter = []
    SOPT.init_sensors()
    visible = {s.id for s in SOPT if SOPT[s].visible}
    assert {"pv_power", "pv1_power", "pv1_current", "pv1_voltage"} <= visible
    assert "pv2_power" not in {s.id for s in SOPT}
    assert DEFS.all["pv_power"].address == (186,)


def test_pv1_group() -> None:
    """pv1 group expands to power, current and voltage."""
    _reload_defs("single-phase")
    OPT.sensors = ["pv1"]
    OPT.sensors_first_inverter = []
    SOPT.init_sensors()
    assert {s.id for s in SOPT if SOPT[s].visible} == {
        "pv1_current",
        "pv1_power",
        "pv1_voltage",
    }


def test_pv8_group_hv_power_only() -> None:
    """pv8 on HV has power; voltage/current are not defined."""
    _reload_defs("three-phase-hv")
    OPT.sensors = ["pv8"]
    OPT.sensors_first_inverter = []
    SOPT.init_sensors()
    visible = {s.id for s in SOPT if SOPT[s].visible}
    assert visible == {"pv8_power"}


def test_opt1() -> None:
    """Sensors."""
    _reload_defs("single-phase")
    OPT.sensors = []
    OPT.sensors_first_inverter = []
    SOPT.init_sensors()
    assert sorted(s.id for s in SOPT) == [
        "rated_power",
    ]

    OPT.sensors = ["prog1_time"]
    OPT.sensors_first_inverter = []
    SOPT.init_sensors()
    assert sorted(s.id for s in SOPT) == [
        "prog1_time",
        "prog2_time",
        "prog3_time",
        "prog4_time",
        "prog5_time",
        "prog6_time",
        "rated_power",
    ]
    assert sorted(s.id for s in SOPT if SOPT[s].visible) == [
        "prog1_time",
    ]


def test_opt_1st() -> None:
    """Sensors."""
    _reload_defs("single-phase")
    OPT.sensors = ["rated_power"]
    OPT.sensors_first_inverter = ["prog1_time"]
    SOPT.init_sensors()

    assert sorted(s.id for s in SOPT) == [
        "prog1_time",
        "prog2_time",
        "prog3_time",
        "prog4_time",
        "prog5_time",
        "prog6_time",
        "rated_power",
    ]
    assert sorted(s.id for s in SOPT if SOPT[s].visible) == [
        "prog1_time",
        "rated_power",
    ]
    assert sorted(s.id for s in SOPT if SOPT[s].first) == [
        "prog1_time",
        "prog2_time",
        "prog3_time",
        "prog4_time",
        "prog5_time",
        "prog6_time",
    ]


def test_opt_1st_visible() -> None:
    """Sensors."""
    _reload_defs("single-phase")
    OPT.sensors = []
    OPT.sensors_first_inverter = ["rated_power"]
    SOPT.init_sensors()

    assert sorted(s.id for s in SOPT) == [
        "rated_power",
    ]
    assert sorted(s.id for s in SOPT if SOPT[s].visible) == [
        "rated_power",
    ]
    assert sorted(s.id for s in SOPT if SOPT[s].first) == []

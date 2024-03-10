from sunsynk.definitions3phhv import SENSORS as HV1
from sunsynk.definitions3phlv import SENSORS as LV1

from tests.sunsynk.migration.old_hv import SENSORS as HV0
from tests.sunsynk.migration.old_lv import SENSORS as LV0


# Check that all the factors are the same for old existing sensors
def test_migration():
    """Test definition migration."""
    for name, old_sensor in LV0.all.items():
        if name in LV1.deprecated:
            continue

        assert old_sensor.factor == LV1.all[name].factor

        # Expanded definition
        if name in (
            "device_type",
            "prog1_charge",
            "prog2_charge",
            "prog3_charge",
            "prog4_charge",
            "prog5_charge",
            "prog6_charge",
            "generator_charge_enabled",  # changed to a switch
        ):
            continue

        # added bitmask
        if name in ["use_timer"]:
            continue

        assert str(old_sensor) == str(LV1.all[name])

    for name, old_sensor in HV0.all.items():
        if name in HV1.deprecated:
            continue

        assert old_sensor.factor == HV1.all[name].factor

        # Expanded definition
        if name in (
            "battery_capacity_current",  # new unit
            "prog1_charge",
            "prog2_charge",
            "prog3_charge",
            "prog4_charge",
            "prog5_charge",
            "prog6_charge",
            "time_synchronization",  # You can't have 2 of the same options!
            "beep",  # You can't have 2 of the same options!
            "am_pm",  # You can't have 2 of the same options!
            "auto_dim",  # You can't have 2 of the same options!
            "allow_remote",  # You can't have 2 of the same options!
        ):
            continue

        # added bitmask
        if name in ["use_timer"]:
            continue

        assert str(old_sensor) == str(HV1.all[name])

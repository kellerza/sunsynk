"""Schedules."""
import logging

import attrs

from sunsynk import KWH, WATT, NumType, Sensor
from sunsynk.helpers import slug
from sunsynk.rwsensors import RWSensor

_LOGGER = logging.getLogger(__name__)

SCH_RWSENSOR = "rw"
SCH_ANY_UNIT = "any_unit"
SCH_NO_UNIT = "no_unit"


@attrs.define(slots=True)
class Schedule:
    """A schehdule."""

    key: str = attrs.field(default="", converter=slug, on_setattr=attrs.setters.convert)
    """Key can be: the sensor name, class (i.e. RWSensor) and unit."""

    read_once: bool = attrs.field(default=False)
    read_every: int = attrs.field(default=0)
    report_every: int = attrs.field(default=0)
    change_significant: float = attrs.field(default=0)
    """Significant change over last samples."""
    change_significant_percent: int = attrs.field(default=0)
    """Significant change percent over last samples."""
    change_any: bool = attrs.field(default=False)
    """Report any change to the last. Only use the last sample."""

    # def __attrs_post_init__(self):
    #     self.key = slug(self.key)

    def significant_change(self, history: list[NumType], last: NumType) -> bool:
        """Check if there is a significant change according to the schedule."""
        if self.change_any:
            if not history or last != history[-1]:
                return True
        if not history:
            return False
        avg = sum(history) / len(history)
        if self.change_significant:
            if abs(last - avg) >= self.change_significant:
                return True
        if self.change_significant_percent:
            chg = abs(avg * self.change_significant_percent / 100)
            if last > avg + chg or last < avg - chg:
                return True
        return False


def get_schedule(sensor: Sensor, schedules: dict[str, Schedule]) -> Schedule:
    """Get the schedule for the sensor."""
    search_keys = (
        ("name", sensor.name),
        ("RWSensor", SCH_RWSENSOR if isinstance(sensor, RWSensor) else None),
        ("Unit", sensor.unit),
        ("Any unit", SCH_ANY_UNIT if sensor.unit != "" else None),
        ("No unit", SCH_NO_UNIT if sensor.unit == "" else None),
    )
    for reason, key in search_keys:
        if key:
            key = slug(key)
            if key in schedules:
                _LOGGER.debug(
                    "Schedule %s used for %s (reason: %s)", key, sensor.name, reason
                )
                return schedules[key]
    raise ValueError(f"No schedule found for {sensor}")


# Always take the average over all samples
# except for any change_* match
SCHEDULES = {
    slug(s.key): s
    for s in (
        # Specific sensors
        Schedule(key="date_time", read_every=60, report_every=60, change_any=True),
        Schedule(key="rated_power", read_once=True),
        Schedule(key="serial", read_once=True),
        # Configuration (RWSensors) used if no name found
        Schedule(key=SCH_RWSENSOR, read_every=5, report_every=5 * 60, change_any=True),
        # Based on unit
        Schedule(
            key=WATT,
            read_every=5,
            report_every=60,
            change_significant=80,  # 80 Watts
            change_significant_percent=30,
        ),
        Schedule(key=KWH, read_every=5 * 60, report_every=5 * 60),
        # Units present, or not present
        Schedule(key=SCH_ANY_UNIT, read_every=15, report_every=5 * 60),
        Schedule(key=SCH_NO_UNIT, read_every=15, report_every=5 * 60, change_any=True),
    )
}


def init_schedules(schedules: list[Schedule]) -> None:
    """Initialize the schedules."""
    updated: set[str] = set()

    for sch in schedules:
        if sch.key in SCHEDULES:
            _LOGGER.info("Replaced %s", sch)
        else:
            _LOGGER.info("Added    %s", sch)
        updated.add(sch.key)
        SCHEDULES[sch.key] = sch

    for schn, sch in SCHEDULES.items():
        if schn not in updated:
            _LOGGER.info("Default  %s", sch)

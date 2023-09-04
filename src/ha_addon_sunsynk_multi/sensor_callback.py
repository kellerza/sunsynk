"""Sensor callback."""
import asyncio
import logging
from collections import defaultdict
from textwrap import wrap
from typing import Iterable

import attrs
from prettytable import PrettyTable

from ha_addon_sunsynk_multi.a_inverter import AInverter
from ha_addon_sunsynk_multi.a_sensor import ASensor, SensorOption
from ha_addon_sunsynk_multi.sensor_options import SOPT
from ha_addon_sunsynk_multi.timer_callback import AsyncCallback
from sunsynk import RWSensor, Sensor, ValType

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True)
class SensorRun:
    """Sensor run schedule."""

    next_run: int = attrs.field(default=0)
    sensors: set[SensorOption] = attrs.field(factory=set)


def _build_schedules(idx: int) -> tuple[dict[int, SensorRun], dict[int, SensorRun]]:
    """Build schedules."""
    read_s: dict[int, SensorRun] = defaultdict(SensorRun)
    report_s: dict[int, SensorRun] = defaultdict(SensorRun)
    first = idx == 0

    for sopt in SOPT.values():
        if not first and sopt.first:
            continue
        if sopt.schedule.read_every:
            read_s[sopt.schedule.read_every].sensors.add(sopt)
        if not sopt.visible:
            continue
        if sopt.schedule.report_every:
            report_s[sopt.schedule.report_every].sensors.add(sopt)

    if idx > 1:
        return read_s, report_s

    _print_table(
        data=(
            (e, ", ".join(s.sensor.id for s in r.sensors)) for e, r in read_s.items()
        ),
        field_names=["s", "Sensors"],
        title=f"Read every (inverter {'1' if first else '>1'})",
    )

    _print_table(
        data=(
            (e, ", ".join(s.sensor.id for s in r.sensors)) for e, r in report_s.items()
        ),
        field_names=["s", "Sensors"],
        title=f"Report every (inverter {'1' if first else '>1'})",
    )

    return read_s, report_s


def _print_table(
    data: Iterable[tuple[int, str]], field_names: list[str], title: str
) -> None:
    """Print a table."""
    tab = PrettyTable()
    tab.field_names = field_names
    for key, val in sorted(data, key=lambda x: x[0]):
        wrapped = wrap(str(val) or "", 80) or [""]
        tab.add_row([key, wrapped[0]])
        for more in wrapped[1:]:
            tab.add_row(["", more])
    _LOGGER.info("%s\n%s", title, tab.get_string())


def build_callback_schedule(ist: AInverter, idx: int) -> AsyncCallback:
    """Build the callback schedule."""
    read_s, report_s = _build_schedules(idx)

    async def callback_sensor(now: int) -> None:
        """read or write sensors"""
        # pylint: disable=too-many-branches
        sensors_to_read: set[Sensor] = set()
        sensors_to_publish: set[ASensor] = set()
        # add all read items
        for sec, srun in read_s.items():
            if now % sec == 0 or srun.next_run <= now:
                sensors_to_read.update(s.sensor for s in srun.sensors)
                srun.next_run = now + sec
        # perform the read
        if sensors_to_read:
            _LOGGER.debug("Read: %s", len(sensors_to_read))
            await ist.read_sensors(
                sensors=sensors_to_read,
                msg="poll_need_to_read",
            )
            sensors_to_publish.update(ist.ss[s.id] for s in sensors_to_read)

        # Flush pending writes
        while ist.write_queue:
            sensor, value = ist.write_queue.popitem()
            if not isinstance(sensor, RWSensor):
                continue
            await asyncio.sleep(0.02)
            await ist.inv.write_sensor(sensor, value)
            await ist.read_sensors(sensors=[sensor], msg=sensor.name)
            sensors_to_publish.add(ist.ss[sensor.id])

        # Publish to MQTT
        pub: dict[ASensor, ValType] = {}
        # Check significant change reporting
        for asen in sensors_to_publish:
            sensor = asen.opt.sensor
            if sensor in ist.inv.state.historynn:
                hist = ist.inv.state.historynn[sensor]
                chg = hist[0] != hist[-1]
                if chg and asen.opt.schedule.change_any:
                    pub[asen] = hist[-1]
            elif sensor in ist.inv.state.history:
                last = ist.inv.state.history[sensor][-1]
                if asen.opt.schedule.significant_change(
                    history=ist.inv.state.history[sensor][:-1],
                    last=last,
                ):
                    ist.inv.state.history[sensor].clear()
                    ist.inv.state.history[sensor].append(last)
                    pub[asen] = last

        # check fixed reporting
        for sec, srun in report_s.items():
            if now % sec == 0 or srun.next_run <= now:
                # get list of ASensor from SensorOption
                sens = [a for a in ist.ss.values() if a.opt in srun.sensors]
                for asen in sens:
                    if asen in pub:
                        continue
                    sensor = asen.opt.sensor
                    # Non-numeric value
                    if sensor in ist.inv.state.historynn:
                        pub[asen] = ist.inv.state.historynn[sensor][-1]
                        continue
                    # average value is n
                    try:
                        pub[asen] = ist.inv.state.history_average(sensor)
                    except ValueError:
                        _LOGGER.warning("No history for %s", sensor)
                srun.next_run = now + sec

        if pub:
            asyncio.create_task(ist.publish_sensors(states=pub))

    return AsyncCallback(
        name=f"read {ist.opt.ha_prefix}",
        every=1,
        callback=callback_sensor,
        keep_stats=True,
    )

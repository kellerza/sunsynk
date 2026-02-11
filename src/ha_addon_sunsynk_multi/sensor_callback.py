"""Sensor callback."""

import asyncio
import logging
from collections import defaultdict
from typing import Self

import attrs

from sunsynk import RWSensor, Sensor, ValType
from sunsynk.utils import pretty_table

from .a_inverter import AInverter
from .a_sensor import ASensor, SensorOption
from .sensor_options import SOPT
from .timer_callback import AsyncCallback

_LOG = logging.getLogger(__name__)


@attrs.define(slots=True)
class SensorRun:
    """Sensor run schedule."""

    next_run: int = 0
    sensors: set[SensorOption] = attrs.field(factory=set)


@attrs.define(slots=True)
class SensorSchedule:
    """Sensor run schedule."""

    read: dict[int, SensorRun] = attrs.field(factory=lambda: defaultdict(SensorRun))
    report: dict[int, SensorRun] = attrs.field(factory=lambda: defaultdict(SensorRun))

    def build_schedules(self, idx: int) -> Self:
        """Build schedules."""
        self.read.clear()
        self.report.clear()
        first = idx == 0

        for sopt in SOPT.values():
            if not first and sopt.first:
                continue
            if sopt.schedule.read_every:
                self.read[sopt.schedule.read_every].sensors.add(sopt)
            if not sopt.visible:
                continue
            if sopt.schedule.report_every:
                self.report[sopt.schedule.report_every].sensors.add(sopt)

        if idx < 2:
            self.print_schedule("Read every", idx, self.read)
            self.print_schedule("Report every", idx, self.report)

        return self

    def print_schedule(self, title: str, idx: int, sch: dict[int, SensorRun]) -> None:
        """Print the sensor schedule."""
        data = [[e, ", ".join(s.sensor.id for s in r.sensors)] for e, r in sch.items()]
        tab = pretty_table(["s", "Sensors"], data)
        inv_ref = ">1" if idx > 1 else "1"
        _LOG.debug("%s (inverter %s)\n%s", title, inv_ref, tab.get_string())


def build_callback_schedule(ist: AInverter) -> None:  # noqa: PLR0915
    """Build the callback schedule."""
    ist.sched = SensorSchedule().build_schedules(ist.index)
    atsk = None

    async def callback_sensor(now: int) -> None:  # noqa: PLR0915 PLR0912
        """Read or write sensors."""
        sensors_to_read: set[Sensor] = set()
        sensors_to_publish: set[ASensor] = set()

        await ist.inv.connect()  # Check that we are connected #395

        # Flush pending writes
        while ist.write_queue:
            sensor, value = ist.write_queue.popitem()
            if not isinstance(sensor, RWSensor):
                continue
            await asyncio.sleep(0.1)
            await ist.write_sensor(sensor, value)
            await asyncio.sleep(0.05)
            await ist.read_sensors(sensors=[sensor], msg=sensor.name)
            sensors_to_publish.add(ist.ss[sensor.id])

        # add all read items
        for sec, srun in ist.sched.read.items():
            if now % sec == 0 or srun.next_run <= now:
                sensors_to_read.update(s.sensor for s in srun.sensors)
                srun.next_run = now + sec
        # perform the read
        if sensors_to_read:
            _LOG.debug("Read: %s", len(sensors_to_read))
            await ist.read_sensors(
                sensors=sensors_to_read,
                msg="poll_need_to_read",
            )
            sensors_to_publish.update(ist.ss[s.id] for s in sensors_to_read)

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
            elif asen.opt.schedule.change_any:
                # make sure it is part of historynn
                last = (
                    ist.inv.state.history.pop(sensor)[-1]
                    if sensor in ist.inv.state.history
                    else None
                )
                if last is not None:
                    pub[asen] = last
                ist.inv.state.historynn[sensor] = [None, last]
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
        for sec, srun in ist.sched.report.items():
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
                        _LOG.warning("No history for %s", sensor)
                srun.next_run = now + sec

        if pub:
            nonlocal atsk
            atsk = asyncio.create_task(ist.publish_sensors(states=pub))

    ist.cb = AsyncCallback(
        name=f"read {ist.opt.ha_prefix}",
        every=1,
        callback=callback_sensor,
        keep_stats=True,
    )

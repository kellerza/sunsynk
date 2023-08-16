"""Sensor callback."""
import asyncio
import logging
from collections import defaultdict

import attrs

from ha_addon_sunsynk_multi.a_inverter import AInverter
from ha_addon_sunsynk_multi.a_sensor import ASensor, SensorOption
from ha_addon_sunsynk_multi.sensor_options import SOPT
from ha_addon_sunsynk_multi.timer_callback import Callback
from sunsynk import RWSensor, Sensor

_LOGGER = logging.getLogger(__name__)


@attrs.define(slots=True)
class SensorRun:
    """Sensor run schedule."""

    next_run: int = attrs.field(default=0)
    sensors: set[SensorOption] = attrs.field(factory=set)


def build_callback_schedule(ist: AInverter, first: bool) -> Callback:
    """Build schedules."""
    read_s: dict[int, SensorRun] = defaultdict(SensorRun)
    report_s: dict[int, SensorRun] = defaultdict(SensorRun)

    for sopt in SOPT.values():
        if not first and sopt.first:
            continue
        if sopt.schedule.read_every:
            read_s[sopt.schedule.read_every].sensors.add(sopt)
        if not sopt.visible:
            continue
        if sopt.schedule.report_every:
            report_s[sopt.schedule.report_every].sensors.add(sopt)

    async def callback_sensor(seconds: int) -> None:
        """read or write sensors"""
        # pylint: disable=too-many-branches
        sensors_to_read: set[Sensor] = set()
        sensors_to_publish: set[ASensor] = set()
        # add all read items
        for sec, srun in read_s.items():
            if seconds % sec == 0 or srun.next_run < seconds:
                sensors_to_read.update(s.sensor for s in srun.sensors)
            srun.next_run = seconds + sec
        # perform the read
        if sensors_to_read:
            _LOGGER.debug("Read: %s", len(sensors_to_read))
            if await ist.read_sensors(
                sensors=sensors_to_read,
                msg=" (poll_need_to_read)",
                retry_single=False,
            ):
                sensors_to_publish.update(ist.ss[s.id] for s in sensors_to_read)
            sensors_to_read.clear()

        # Flush pending writes
        while ist.write_queue:
            sensor, value = ist.write_queue.popitem()
            if not isinstance(sensor, RWSensor):
                continue
            await ist.inv.write_sensor(sensor, value)
            await ist.read_sensors(sensors=[sensor], msg=sensor.name)
            sensors_to_publish.add(ist.ss[sensor.id])

        # Publish to MQTT
        pub: set[ASensor] = set()
        # Check significant change reporting
        for asen in sensors_to_publish:
            sensor = asen.opt.sensor
            if sensor in ist.inv.state.historynn:
                hist = ist.inv.state.historynn[sensor]
                chg = hist[0] != hist[1]
                chg_any = isinstance(sensor, RWSensor) or asen.opt.schedule.change_any
                if chg and chg_any:
                    pub.add(asen)
            elif sensor in ist.inv.state.history:
                if asen.opt.schedule.significant_change(
                    history=ist.inv.state.history[sensor][:-1],
                    last=ist.inv.state.history[sensor][-1],
                ):
                    pub.add(asen)

        # check fixed reporting
        for sec, srun in report_s.items():
            if seconds % sec == 0 or srun.next_run < seconds:
                # get list of ASensor from SensorOption
                aaa = [a for a in ist.ss.values() if a.opt in srun.sensors]
                pub.update(aaa)
                srun.next_run = seconds + sec

        if pub:
            asyncio.create_task(ist.publish_sensors(states=list(pub)))

    return Callback(
        name=f"read {ist.opt.ha_prefix}",
        every=1,
        callback=callback_sensor,
        cbstat_time=[],  # Keep record of the execution time
        cbstat_slip=[],
    )

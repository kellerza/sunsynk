"""Profile read & write support."""
# pylint: disable=too-few-public-methods, invalid-name, too-many-instance-attributes
import asyncio
import logging
from itertools import chain
from pathlib import Path
from random import random
from typing import Dict, List, Sequence, Tuple

import attr
from mqtt import MQTT, Device, Entity, SelectEntity
from options import OPT, SS_TOPIC
from yaml import safe_dump, safe_load

from sunsynk import Sunsynk
from sunsynk.definitions import PROG_VOLT, PROGRAM
from sunsynk.sensor import RWSensor, ensure_tuple, slug

_LOGGER = logging.getLogger(__name__)
ROOT = "/share/hass-addon-sunsynk/"
UPDATE = "UPDATE"


@attr.s
class Profile:
    """All the elements of the profile: Name, sensors and MQTT entity."""

    sensors: Sequence[RWSensor] = attr.field()
    name: str = attr.field()
    entity: SelectEntity = attr.field(default=None)
    preset_data: Dict[str, Dict] = attr.field(factory=dict)
    preset_file: Dict[str, str] = attr.field(factory=dict)

    @property
    def id(self) -> str:
        """The profile ID."""
        return slug(self.name)

    def log_values(self) -> None:
        """Display the values for all sensors."""
        rws = [(s.name, s.reg_value) for s in self.sensors]
        _LOGGER.info("Profile %s: %s", self.name, rws)

    def loadfile(self, file: Path) -> Tuple[str, Dict]:
        """Load a single file."""
        _LOGGER.debug("Load %s", file)
        p_items = safe_load(file.read_text(encoding="utf-8"))
        p_name = p_items.pop("name", None) or file.stem[len(self.id) + 1 :]
        p_items = {n: ensure_tuple(v) for n, v in p_items.items()}

        expected_s = set(s.id for s in self.sensors)
        # Ensure all keys are present
        if expected_s != set(p_items.keys()):
            _LOGGER.warning(
                "%s missing: %s, extra: %s",
                file.name,
                expected_s - set(p_items.keys()),
                set(p_items.keys()) - expected_s,
            )
            return ("", {})

        # Ensure all value lengths are correct
        if not all(len(s.reg_value) == len(p_items[s.id]) for s in self.sensors):
            _LOGGER.warning("%s %s bad value length", file.name, p_name)
            return ("", {})

        # Save the preset
        self.preset_data[p_name] = p_items
        self.preset_file[p_name] = str(file)
        return p_name, p_items

    def load(self) -> Tuple[str, Sequence[str]]:
        """Load all presets for this profile from disk and see if one matches."""
        active_preset = ""
        self.preset_data.clear()
        self.preset_file.clear()

        for file in chain(Path(ROOT).glob("*.yml"), Path(ROOT).glob("*.yaml")):
            if not file.name.startswith(f"{self.id}__"):
                continue

            # Load preset file
            res = self.loadfile(file)
            if not res:
                continue
            p_name, p_items = res

            # check if this is the active preset
            # All values = sensors reg_values
            if all(s.reg_value == p_items[s.id] for s in self.sensors):
                active_preset = p_name

        if not active_preset:
            active_preset = self.save()

        return active_preset, list(sorted(self.preset_data.keys())) + [UPDATE]

    def save(self) -> str:
        """Save the preset using a random identifier."""
        pth = Path(ROOT)
        if not pth.exists():
            pth.mkdir(parents=True)
        active_preset = f"new_{int(random()*1000)}"
        pth /= f"{self.id}__{active_preset}.yml"
        value = dict(
            {
                s.id: list(s.reg_value) if len(s.reg_value) > 1 else s.reg_value[0]
                for s in self.sensors
                if s.reg_value
            },
            name=active_preset,
        )
        pth.write_text(safe_dump(value))
        return active_preset

    async def mqtt_update_action(self) -> None:
        """Use the reg_values of the sensors to determine the profile.

        1. determine active preset (from reg_values & all yaml files)
        2. create a name and save preset if new
        3. update the entity options (mqtt discovery)
        4. publish the active preset to HASS
        """
        # 1. & 2.
        (
            active_preset,
            preset_options,
        ) = await asyncio.get_running_loop().run_in_executor(None, self.load)
        # 3.
        if OPT.debug > 0:
            _LOGGER.info("Updating entity options: %s", preset_options)
        self.entity.options = preset_options
        await MQTT.publish_discovery_info(entities=[self.entity], remove_entities=False)
        # 4.
        if OPT.debug > 0:
            _LOGGER.info("publish %s %s", self.entity.state_topic, active_preset)
        await asyncio.sleep(0.05)
        await MQTT.publish(self.entity.state_topic, active_preset)

    async def write_preset(self, ss: Sunsynk, name: str) -> None:
        """Write the preset."""
        values = self.preset_data.get(name, {})
        if not values:
            _LOGGER.error("Preset %s does not exist", name)

        cntskip = 0
        for sen in self.sensors:
            newv = ensure_tuple(values[sen.id])
            if newv == sen.reg_value:
                cntskip += 1
                continue
            _LOGGER.info(
                "Preset %s: %s=%s  [old %s]", name, sen.id, newv, sen.reg_value
            )
            sen.reg_value = newv
            await ss.write_sensor(sen)
        _LOGGER.info(
            "Preset %s activated on %s (skipped %s, updated %s)",
            name,
            self.name,
            cntskip,
            len(self.sensors) - cntskip,
        )


async def profile_poll(ss: Sunsynk) -> None:
    """Poll the PROFILE_QUEUE."""
    if not PROFILE_QUEUE:
        return
    profile, action = PROFILE_QUEUE.pop(0)
    if OPT.debug > 0:
        if PROFILE_QUEUE:
            _LOGGER.info("In Queue %s", PROFILE_QUEUE)
        _LOGGER.info("Profile %s action %s", profile.name, action)

    await MQTT.publish(profile.entity.state_topic, action)

    if action == UPDATE:
        await ss.read_sensors(profile.sensors)
        # profile.log_values()
        await profile.mqtt_update_action()
        return

    filename = profile.preset_file.get(action)
    if filename:
        # not async, but best to ensure we have the latest
        preset_name0, _ = await asyncio.get_running_loop().run_in_executor(
            None, profile.loadfile, Path(filename)
        )

        if preset_name0 != action:
            _LOGGER.error(
                "Preset %s: File:%s contains:%s", action, filename, preset_name0
            )
            return

        await profile.write_preset(ss, preset_name0)


def profile_add_entities(entities: List[Entity], device: Device) -> None:
    """Add entities that will be discovered."""
    for pname in OPT.profiles:
        pro = ALL_PROFILES.get(pname)
        if not pro:
            _LOGGER.error("Invalid profile %s", pname)
            continue
        pro.entity = SelectEntity(
            name=f"{OPT.sensor_prefix} {pro.name}",
            unique_id=f"{OPT.sunsynk_id}_{pro.id}",
            state_topic=f"{SS_TOPIC}/{OPT.sunsynk_id}/{pro.id}",
            command_topic=f"{SS_TOPIC}/{OPT.sunsynk_id}/{pro.id}_set",
            options=[UPDATE],
            device=device,
            on_change=lambda val, p=pro: PROFILE_QUEUE.append((p, val)),
        )
        entities.append(pro.entity)

        # Make sure the values are read & updated on startup!
        PROFILE_QUEUE.append((pro, UPDATE))


PROFILE_QUEUE: List[Tuple[Profile, str]] = []

ALL_PROFILES = {
    p.id: p
    for p in (
        Profile(name="System Mode", sensors=PROGRAM),
        Profile(name="System Mode Voltages", sensors=PROG_VOLT),
    )
}

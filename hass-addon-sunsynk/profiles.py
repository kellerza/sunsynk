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
from sunsynk import definitions as ssd
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
    presets: Dict[str, Dict] = attr.field(factory=dict)

    @property
    def id(self) -> str:
        """The profile ID."""
        return slug(self.name)

    def log_values(self) -> None:
        """Display the values for all sensors."""
        rws = [(s.name, s.reg_value) for s in self.sensors]
        _LOGGER.info("Profile %s: %s", self.name, rws)

    def load(self) -> Tuple[str, Sequence[str]]:
        """Load all presets for this profile from disk and see if one matches."""
        active_preset = ""
        self.presets.clear()

        expected_s = set(s.id for s in self.sensors)
        for file in chain(Path(ROOT).glob("*.yml"), Path(ROOT).glob("*.yaml")):
            if not file.name.startswith(self.id):
                continue

            # Load preset file
            _LOGGER.info("%s", file)
            p_items = safe_load(file.read_text(encoding="utf-8"))
            p_name = p_items.pop("name", None) or file.stem[len(self.id) + 1 :]
            p_items = {n: ensure_tuple(v) for n, v in p_items.items()}

            # Ensure all keys are present
            if expected_s != set(p_items.keys()):
                _LOGGER.warning(
                    "%s missing: %s, extra: %s",
                    file.name,
                    expected_s - set(p_items.keys()),
                    set(p_items.keys()) - expected_s,
                )
                continue

            # Ensure all value lengths are correct
            if not all(len(s.reg_value) == len(p_items[s.id]) for s in self.sensors):
                _LOGGER.warning("%s %s bad value length", file.name, p_name)
                continue

            # Save the preset
            self.presets[p_name] = p_items

            # check if this is the active preset
            # All values = sensors reg_values
            if all(s.reg_value == p_items[s.id] for s in self.sensors):
                active_preset = p_name

        if not active_preset:
            active_preset = self.save()

        return active_preset, list(sorted(self.presets.keys())) + [UPDATE]

    def save(self) -> str:
        """Save the preset using a random identifier."""
        active_preset = f"new_{int(random()*1000)}"
        pth = Path(ROOT) / f"{self.id}_{active_preset}.yml"
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
        _LOGGER.info("Updating entity options: %s", preset_options)
        self.entity.options = preset_options
        await MQTT.publish_discovery_info(entities=[self.entity], remove_entities=False)
        # 4.
        _LOGGER.info("publish %s %s", self.entity.state_topic, active_preset)
        asyncio.create_task(MQTT.publish(self.entity.state_topic, active_preset))


async def write_preset_registers(
    ss: Sunsynk, profile: Profile, preset: Dict[str, Tuple[int, ...]]
) -> None:
    """Write the preset."""
    for sen in profile.sensors:
        newv = ensure_tuple(preset[sen.id])
        if newv != sen.reg_value:
            _LOGGER.info(
                "New value for %s, old: %s, new: %s", sen.id, sen.reg_value, newv
            )
        sen.reg_value = newv
        try:
            for adr, val in zip(sen.reg_address, newv):
                await asyncio.sleep(0.01)
                await ss.write(address=adr, value=val)
        except asyncio.TimeoutError:
            _LOGGER.critical(
                "timeout writing the settings %s=%s", sen.reg_address[0], newv
            )


async def profile_poll(ss: Sunsynk) -> None:
    """Poll the PROFILE_QUEUE."""
    if not PROFILE_QUEUE:
        return
    profile, action = PROFILE_QUEUE.pop(0)
    if PROFILE_QUEUE:
        _LOGGER.warning("Queue length %s", len(PROFILE_QUEUE))

    _LOGGER.critical("profile %s action %s", profile.name, action)

    await MQTT.publish(profile.entity.state_topic, action)

    if action == UPDATE:
        await ss.read(profile.sensors)
        # profile.log_values()
        await profile.mqtt_update_action()
        return

    new_preset = profile.presets.get(action)
    if new_preset:
        _LOGGER.info("Write the new settings! %s", action)
        await write_preset_registers(ss, profile, new_preset)


def profile_add_entities(entities: List[Entity], device: Device) -> None:
    """Add entities that will be discovered."""
    for pro in ALL_PROFILES:
        pro.entity = SelectEntity(
            name=f"{OPT.sensor_prefix} {pro.name}",
            unique_id=f"{OPT.sunsynk_id}_{pro.id}",
            state_topic=f"{SS_TOPIC}/{OPT.sunsynk_id}/{pro.id}",
            command_topic=f"{SS_TOPIC}/{OPT.sunsynk_id}/{pro.id}_set",
            options=[UPDATE],
            device=device,
            on_change=lambda val: PROFILE_QUEUE.append((pro, val)),
        )
        entities.append(pro.entity)

        # Make sure the values are read & updated on startup!
        PROFILE_QUEUE.append((pro, UPDATE))


PROFILE_QUEUE: List[Tuple[Profile, str]] = []

ALL_PROFILES = (
    Profile(
        name="System Mode",
        sensors=[
            ssd.prog1_capacity,
            ssd.prog2_capacity,
            ssd.prog3_capacity,
            ssd.prog4_capacity,
            ssd.prog5_capacity,
            ssd.prog6_capacity,
            ssd.prog1_time,
            ssd.prog2_time,
            ssd.prog3_time,
            ssd.prog4_time,
            ssd.prog5_time,
            ssd.prog6_time,
            ssd.prog1_power,
            ssd.prog2_power,
            ssd.prog3_power,
            ssd.prog4_power,
            ssd.prog5_power,
            ssd.prog6_power,
            ssd.prog1_charge,
            ssd.prog2_charge,
            ssd.prog3_charge,
            ssd.prog4_charge,
            ssd.prog5_charge,
            ssd.prog6_charge,
        ],
    ),
    Profile(
        name="System Mode Voltages",
        sensors=[
            ssd.prog1_voltage,
            ssd.prog2_voltage,
            ssd.prog3_voltage,
            ssd.prog4_voltage,
            ssd.prog5_voltage,
            ssd.prog6_voltage,
        ],
    ),
)

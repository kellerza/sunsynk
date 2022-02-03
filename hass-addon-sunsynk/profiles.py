"""Profile read & write support."""
import logging
from pathlib import Path
from typing import List, Sequence, Tuple

import attr
from mqtt import MQTT, Device, Entity, SelectEntity
from options import OPT, SS_TOPIC

from sunsynk import Sunsynk
from sunsynk import definitions as ssd
from sunsynk.sensor import RWSensor, Sensor, slug

_LOGGER = logging.getLogger(__name__)


@attr.s
class Profile:
    """All the elements of the profile: Name, sensors and MQTT entity."""

    sensors: Sequence[Sensor] = attr.field()
    name: str = attr.field()
    entity: SelectEntity = attr.field(default=None)

    @property
    def id(self) -> str:
        """The profile ID."""
        return slug(self.name)


P_MODE = Profile(
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
)

PROFILE_QUEUE: List[Tuple[Profile, str]] = []
UPDATE = "UPDATE"


async def profile_read(id: str) -> dict:
    """Activate a specific profile."""
    dirs = ("/", "/share", "/config", "/share/hass-addon-sunsynk")
    for dir in dirs:
        pth = Path(dir)
        _LOGGER.info(
            "%s %s %s", id, dir, list(pth.iterdir()) if pth.is_dir() else "no dir!!!"
        )
    return {}


async def profile_update_mqtt(profile: Profile) -> None:
    """Use the raw_values of the sensors to determine the profile.

    1. determine profile name (from raw_values)
    2. save if a new profile name
    3. update the entity options (mqtt discovery)
    4. publish the active profile to HASS
    """
    # 1.
    await profile_read(profile.id)
    profiles = ["a", "b"]
    active_profile = "a"

    # 3. Update the entity's options if different
    if not set(profiles) ^ set(profile.entity.options):
        profile.entity.options = profiles
        await MQTT.publish_discovery_info(
            entities=[profile.entity], remove_entities=False
        )

    # 4. Publish the active profile to HASS
    await MQTT.publish(profile.entity.state_topic, active_profile)


def profile_display_values(profile: Profile) -> None:
    """Display the values for all sensors."""
    rws = {
        s.name: s.raw_value if isinstance(s, RWSensor) else f"{s.value} *"
        for s in profile.sensors
    }
    _LOGGER.info("Profile %s: %s", profile.name, rws)


async def profile_poll(ss: Sunsynk) -> None:
    """Poll the PROFILE_QUEUE."""
    if not PROFILE_QUEUE:
        return
    profile, action = PROFILE_QUEUE.pop(0)
    if PROFILE_QUEUE:
        _LOGGER.warning("Queue length %s", len(PROFILE_QUEUE))

    _LOGGER.critical("profile %s action %s", profile.name, action)

    if action == UPDATE:
        await ss.read(profile.sensors)
        profile_display_values(profile)
        await profile_update_mqtt(profile)
        return

    profile

    await MQTT.publish(f"{SS_TOPIC}/{OPT.sunsynk_id}/{profile.id}", action)


def profile_add_entities(entities: List[Entity], device: Device) -> None:
    """Add entities that will be discovered."""
    for pro in (P_MODE,):
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

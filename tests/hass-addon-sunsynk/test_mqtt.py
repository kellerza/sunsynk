"""Test MQTT class."""
import asyncio
import logging
from types import ModuleType
from unittest.mock import patch

import pytest

from tests.conftest import import_module

_LOGGER = logging.getLogger(__name__)
MOD_FOLDER = "hass-addon-sunsynk"

MQTT_HOST = "192.168.1.8"
MQTT_PASS = "hass123"
MQTT_USER = "hass"


@pytest.fixture
def mqtt() -> ModuleType:
    """Import module."""
    return import_module("mqtt", MOD_FOLDER)


@pytest.fixture
def run() -> ModuleType:
    """Import module."""
    return import_module("run", MOD_FOLDER)


@pytest.fixture
def opt():
    """Import module."""
    return import_module("options", MOD_FOLDER)


def test_mqtt(mqtt):
    """Test MQTT."""
    assert mqtt.hass_device_class(unit="kWh") == "energy"


def test_mqtt_entity(mqtt):
    """Test MQTT."""
    dev = mqtt.Device(identifiers=["123"])

    ava = mqtt.Availability(topic="/blah")

    ent = mqtt.SensorEntity(
        name="test1",
        unique_id="789",
        device=dev,
        availability=[ava],
        state_topic="/test/a",
    )
    assert ent.asdict == {
        "name": "test1",
        "unique_id": "789",
        "device": {"identifiers": ["123"]},
        "availability": [{"topic": "/blah"}],
        "state_topic": "/test/a",
    }

    assert ent.topic == "homeassistant/sensor/123/789/config"


@pytest.mark.skip
@pytest.mark.asyncio
@pytest.mark.mqtt
async def test_mqtt_server(mqtt):
    """Test MQTT."""
    mqt = mqtt.MQTTClient()
    mqt.availability_topic = "test/available"
    await mqt.connect(username="hass", password="hass123", host="192.168.1.8")
    dev = mqtt.Device(identifiers=["test123"])
    dev2 = mqtt.Device(identifiers=["test789"])

    select_id = "t_select_1"
    select_id2 = "t_select_2"
    sense_id = "t_sense_1"

    async def select_select(msg):
        _LOGGER.error("onchange start: %s", msg)
        await mqt.publish(f"test/{select_id2}", "opt 4")
        await mqt.publish(f"test/{select_id}", msg)
        _LOGGER.error("onchange done: %s", msg)

    _loop = asyncio.get_running_loop()

    def select_select2(msg):
        _LOGGER.error("onchange no async: %s", msg)
        _loop.create_task(mqt.publish(f"test/{select_id2}", msg))
        _LOGGER.error("onchange no async done: %s", msg)

    ent = [
        mqtt.SelectEntity(
            name="Test select entity",
            unique_id=select_id,
            device=dev,
            command_topic=f"test/{select_id}_set",
            options=["opt 1", "opt 2"],
            on_change=select_select,
            state_topic=f"test/{select_id}",
        ),
        mqtt.SelectEntity(
            name="Test select entity 2",
            unique_id=select_id2,
            device=dev,
            command_topic=f"test/{select_id2}_set",
            options=["opt 3", "opt 4"],
            on_change=select_select2,
            state_topic=f"test/{select_id2}",
        ),
        mqtt.SensorEntity(
            name="Test sensor entity",
            unique_id=sense_id,
            device=dev2,
            state_topic=f"test/{sense_id}",
        ),
    ]
    await mqt.publish_discovery_info(entities=ent)
    await asyncio.sleep(0.1)

    await mqt.publish(f"test/{select_id}", "opt 2")
    await mqt.publish(f"test/{select_id2}", "opt 3")
    await mqt.publish(f"test/{sense_id}", "yay!")
    for i in range(100):
        await asyncio.sleep(0.5)
    await mqt.remove_discovery_info(device_ids=[dev.id, dev2.id], keep_topics=[])

    await mqt.disconnect()
    await asyncio.sleep(0.1)

    assert False


@pytest.mark.asyncio
@pytest.mark.mqtt
async def test_mqtt_discovery(mqtt):
    """Test MQTT."""
    root = "test2"
    mqt = mqtt.MQTTClient()
    mqt.availability_topic = f"{root}/available"
    await mqt.connect(username=MQTT_USER, password=MQTT_PASS, host=MQTT_HOST)
    dev = mqtt.Device(identifiers=[f"id_{root}"])

    sensor_id = [f"sen{i}" for i in range(3)]

    entities = [
        mqtt.SensorEntity(
            name="Test select entity",
            unique_id=id,
            device=dev,
            state_topic=f"{root}/{id}",
        )
        for id in sensor_id
    ]

    await mqt.publish_discovery_info(entities=entities)
    await asyncio.sleep(0.1)

    # Remove the first entiry
    entities.pop(1)

    with patch("mqtt._LOGGER") as mock_log:
        await mqt.publish_discovery_info(entities=entities)
        mock_log.info.assert_called_with(
            "Removing HASS MQTT discovery info %s",
            f"homeassistant/sensor/id_{root}/sen1/config",
        )

        mock_log.info.reset_mock()

        entities.pop(1)
        await mqt.remove_discovery_info(device_ids=[f"id_{root}"], keep_topics=[])
        assert mock_log.info.call_count == 2
        mock_log.info.assert_any_call(
            "Removing HASS MQTT discovery info %s",
            f"homeassistant/sensor/id_{root}/sen0/config",
        )
        mock_log.info.assert_any_call(
            "Removing HASS MQTT discovery info %s",
            f"homeassistant/sensor/id_{root}/sen2/config",
        )

    await mqt.disconnect()
    await asyncio.sleep(0.1)

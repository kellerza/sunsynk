"""Test ESP addon."""

import attrs

from ha_addon_esp.__main__ import Options


def test_load_esp() -> None:
    """Test."""
    opt = Options()
    opt.load_dict({"areas": [{"ha_PREFIX": "HA", "area_id": "1", "api_key": "xxx"}]})

    res = attrs.asdict(opt)

    assert res == {
        "areas": [
            {
                "api_key": "xxx",
                "area_id": "1",
                "ha_prefix": "HA",
            },
        ],
        "debug": 0,
        "mqtt_host": "core-mosquitto",
        "mqtt_password": "",
        "mqtt_port": 1883,
        "mqtt_username": "",
        "search_area": "",
    }

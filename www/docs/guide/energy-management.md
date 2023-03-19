## Home Assistant

### Energy Management

You can read more Energy Management in Home Assistant [here](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/) and [here](https://www.home-assistant.io/docs/energy/).

![HASS Energy management](https://github.com/kellerza/sunsynk/raw/main/images/energy.png)


The following sensors are required as a minimum to enable the Home Assistant Energy feaure for a hybrid inverter with PV and a battery.

```yaml
SENSORS:
  - total_grid_import
  - total_grid_export
  - total_pv_energy
  - total_battery_charge
  - total_battery_discharge
```

Once you included these sensors in your addon configuration, they should be available in Home Assistant and you can add them to the Energy Management configuration by following this link:
[![Open your Home Assistant instance and show your Energy configuration panel.](https://my.home-assistant.io/badges/config_energy.svg)](https://my.home-assistant.io/redirect/config_energy/)

Show the Energy panel (also available in your sidebar): [![Open your Home Assistant instance and show your Energy panel.](https://my.home-assistant.io/badges/energy.svg)](https://my.home-assistant.io/redirect/energy/)

You can also add individual devices to the energy tracking

```yaml
SENSORS:
  - total_load_energy
  - total_active_energy
```

# Getting Started

## Installation

1. Add the <https://github.com/kellerza/hass-addons> repository to your HA Supervisor

   [![Open your Home Assistant instance and add the kellerza/hass-addons URL](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fkellerza%2Fhass-addons)
   <br/><br/>

2. Install the "Sunsynk/Deye Inverter Add-on **(multi)**" from the **Add-On Store** and configure it through the UI.

   ![Install Sunsynk Addon](../images/addon-install.png)

## Available addons

### Modbus TCP to Modbus RTU Gateway Add-on

An [mbusd TCP to RTU gateway](./mbusd).

### Sunsynk/Deye Inverter Add-on (multi)

The recommended version of the add-on. It supports multiple inverters and custom sensors. The documentation available on this website is for the multi add-on version.

::: tip
This is the recommended version of the add-on!
:::

### Sunsynk/Deye Inverter Add-on (edge/dev)

The developer version of the add-on. Contains the latest changes committed to the Github repository.

### EskomSePush Add-on

The [ESP add-on](./esp) allows you to query loadshedding schedules for your area from the EskomSePush API.

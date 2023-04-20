# Home Assistant Examples

There are three categories of Home Assistant Examples:

- Lovelace cards
- Automations
- Templates

  Templates can be used to create template sensors and are the building blocks for UI elements

## Config packages

Config packages in Home Assistant allows you to bundle different component's configuration together. The examples on this site assumes that you have a package folder, referred to as `/config/packages/`, where you add the example yaml package files.

Read up on Packages and specifically how to [Create a packages folder](https://www.home-assistant.io/docs/configuration/packages/#create-a-packages-folder)

The short version: This config snippet will load packages from `/config/packages/`. If this is not clear, read the HA docs again.

```yaml
homeassistant:
  packages: !include_dir_named packages
```

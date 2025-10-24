"""Sensors."""

import asyncio
from collections import defaultdict
from pathlib import Path

from ha_addon_sunsynk_multi.sensor_options import SENSOR_GROUPS
from sunsynk import RWSensor, Sensor, SensorDefinitions
from sunsynk.definitions import import_all_defs
from sunsynk.utils import pretty_table, table_data


async def main() -> None:
    """Generate docs."""
    all_defs = import_all_defs()

    all_defs = {simple_def_name(k): v for k, v in all_defs.items()}

    generate_all_sensors(all_defs)
    generate_group_sensors(all_defs)


def generate_all_sensors(all_defs: dict[str, SensorDefinitions]) -> None:
    """Generate groups/all.html."""
    sensors = defaultdict[str, dict[str, Sensor]](dict)
    for name, defs in all_defs.items():
        for key, sen in defs.all.items():
            sensors[key][name] = sen

    def getname(row: list[Sensor | None]) -> str:
        """Get the name of the row."""
        for sen in row:
            if sen:
                if isinstance(sen, RWSensor):
                    return f"{sen.name} (R/W)"
                return sen.name
        return "?"

    def get_sensor_info(sensor: Sensor | None) -> str:
        """Sensor info."""
        if not sensor:
            return ""
        reg = (
            str(sensor.address[0]) if len(sensor.address) == 1 else str(sensor.address)
        )
        return reg

    headers = ["Name", *sorted(all_defs)]
    data = table_data(sensors.values(), headers)
    tab = pretty_table(
        *data, to_str=get_sensor_info, calculated_cols={"Name": getname}, wrap_length=0
    )
    print(tab.get_string())

    html = tab.get_html_string()
    html = html.replace("<table>", '<table style="overflow-x: unset;" class="bigt">')

    Path("www/docs/reference/groups/all.html").write_text(
        html, encoding="utf8", newline="\n"
    )


def simple_def_name(d_name: str) -> str:
    """Shorten the definition name."""
    return d_name.replace("single-phase", "1PH").replace("three-phase", "3PH")


def generate_group_sensors(all_defs: dict[str, SensorDefinitions]) -> None:
    """Generate groups/{name}.yml."""
    for g_name, s_name_in_group in SENSOR_GROUPS.items():
        if g_name == "all":
            continue
        g_res = "SENSORS:"
        for s_name in sorted(s_name_in_group):
            # a line per sensor, g_name as a comment
            defs_lst = list[str]()
            for d_name, sdef in all_defs.items():
                sen = sdef.all.get(s_name)
                if not sen:
                    continue
                defs_lst.append(simple_def_name(d_name))
            if len(defs_lst) == len(all_defs):
                g_res += f"\n - {s_name}"
            else:
                g_res += f"\n - {s_name} # {', '.join(defs_lst)}"
        Path(f"www/docs/reference/groups/{g_name}.yml").write_text(
            g_res, encoding="utf8", newline="\n"
        )


if __name__ == "__main__":
    asyncio.run(main())

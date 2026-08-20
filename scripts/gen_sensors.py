"""Sensors."""

import asyncio
import sys
from collections import defaultdict
from pathlib import Path

from ha_addon_sunsynk_multi.sensor_options import SENSOR_GROUPS
from sunsynk import RWSensor, Sensor, SensorDefinitions
from sunsynk.definitions import import_all_defs
from sunsynk.helpers import ensure_tuple
from sunsynk.utils import pretty_table, table_data


async def main() -> None:
    """Generate docs."""
    all_defs = import_all_defs()

    check_register_bit_conflicts(all_defs)

    all_defs = {simple_def_name(k): v for k, v in all_defs.items()}

    sen_groups = generate_group_sensors(all_defs)
    generate_all_sensors(all_defs, sen_groups)


def check_register_bit_conflicts(all_defs: dict[str, SensorDefinitions]) -> None:
    """Fail if any definition has two sensors claiming the same register bits."""
    lines: list[str] = []
    for name, defs in all_defs.items():
        for addr, a, b, bits in defs.register_bit_conflicts():
            lines.append(
                f"  {name}: reg {addr} bit overlap 0x{bits:X} — "
                f"{a.id} (0x{a.bitmask:X}) vs {b.id} (0x{b.bitmask:X})"
            )
    if lines:
        print("Register bit conflicts in sensor definitions:", file=sys.stderr)
        print("\n".join(lines), file=sys.stderr)
        raise SystemExit(1)


TAB_ATTR = {"style": "overflow-x: unset;", "class": "bigt"}


def generate_all_sensors(
    all_defs: dict[str, SensorDefinitions], sen_groups: dict[str, set[str]]
) -> None:
    """Generate groups/all.html."""
    sensors = defaultdict[str, dict[str, Sensor | str]](dict[str, Sensor | str])
    for name, defs in all_defs.items():
        for key, sen in defs.all.items():
            if key != sen.id:
                continue  # alias slug → same Sensor; Name column already lists aliases
            sensors[key][name] = sen
            sensors[key]["Group"] = "<br>".join(sorted(sen_groups.get(sen.id, [])))

    def getname(row: list[Sensor | str | None]) -> str:
        """Get the name of the row (HTML: name, then aliases on separate lines)."""
        for sen in row:
            if not sen or isinstance(sen, str):
                continue
            base = f"{sen.name} (R/W)" if isinstance(sen, RWSensor) else sen.name
            aliases = ensure_tuple(sen.alias)
            if aliases:
                return "<br>".join((base, *aliases))
            return base
        return "?"

    def get_sensor_info(sensor: Sensor | str | None) -> str:
        """Sensor info."""
        if not sensor:
            return ""
        return sensor if isinstance(sensor, str) else sensor.source

    headers = ["Name", *sorted(all_defs), "Group"]
    data = table_data(sensors.values(), headers)
    tab = pretty_table(
        *data, to_str=get_sensor_info, calculated_cols={"Name": getname}, wrap_length=0
    )
    print(tab.get_string())

    html = tab.get_html_string(attributes=TAB_ATTR, escape_data=False)
    # html = html.replace("<table>", '<table style="overflow-x: unset;" class="bigt">')

    Path("www/docs/reference/groups/all.html").write_text(
        html, encoding="utf8", newline="\n"
    )


def simple_def_name(d_name: str) -> str:
    """Shorten the definition name."""
    return d_name.replace("single-phase", "1PH").replace("three-phase", "3PH")


def generate_group_sensors(
    all_defs: dict[str, SensorDefinitions],
) -> dict[str, set[str]]:
    """Generate groups/{name}.yml."""
    res: dict[str, set[str]] = defaultdict(set)
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
                res[sen.id].add(g_name)
                defs_lst.append(simple_def_name(d_name))

            if len(defs_lst) == len(all_defs):
                g_res += f"\n - {s_name}"
            else:
                g_res += f"\n - {s_name} # {', '.join(defs_lst)}"
        Path(f"www/docs/reference/groups/{g_name}.yml").write_text(
            g_res, encoding="utf8", newline="\n"
        )
    return res


if __name__ == "__main__":
    asyncio.run(main())

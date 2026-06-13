# Sunsynk — align with Cursor rules

This project keeps its agent and contributor policies in **`.cursor/rules/`** as
Markdown-with-frontmatter files (**`*.mdc`**). **Follow those files as the source of truth** for how
to work in this repository.

## What to do

1. **Before** suggesting or applying changes in an area covered by a rule’s `globs` (see the YAML
   frontmatter at the top of each `.mdc` file), **read the relevant `.cursor/rules/*.mdc` file** in
   the repo and obey its body (the markdown after the closing `---` of the frontmatter block).
2. **Repository-wide / always-on rules:** if a rule sets `alwaysApply: true` in its frontmatter,
   treat it as binding for **all** work in this repo unless the user explicitly overrides it in the
   current conversation.
3. **When new rules are added** under `.cursor/rules/`, use them the same way: prefer the rule text
   over assumptions from similar projects.

## Current rule files (index)

| Path | Typical scope | Topic |
| ------ | ---------------- | -------- |
| `.cursor/rules/sunsynk-addons.mdc` | Home Assistant add-ons, add-on Python (`src/ha_addon_sunsynk_multi/`), `www/docs/reference/multi-options.md` | Edit **`hass-addon-sunsynk-edge/`** for packaging; do not hand-edit **`hass-addon-sunsynk-multi/`** unless the user explicitly asks for stable-multi work; keep Supervisor options, docs, and `options.py` in sync as described in the rule. |
| `.cursor/rules/sunsynk-definitions.mdc` | `src/sunsynk/definitions/**` | Inverter Modbus definitions: profiles, inheritance, single- vs three-phase; how to extend `ALL_DEFS` and avoid wrong cross-profile register assumptions. |

If this index drifts, **trust the `.mdc` files**; update this table when you add or rename rules.

## Conflicts

If another document in the repo disagrees with a **`.cursor/rules/*.mdc`** rule,
**follow the `.mdc` rule** unless the user or maintainer explicitly says otherwise in the current
thread.

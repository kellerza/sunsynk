---
name: release
description: >-
  Bump sunsynk version (major/minor/bugfix), rewrite the Unreleased changelog
  heading, commit, push to main, and open a draft GitHub release with a v-prefixed
  tag. Use when the user asks to release, bump version, or cut a
  major/minor/bugfix release.
disable-model-invocation: true
---

# Release

Bump version, push to `main`, and open a **draft** GitHub release (`v0.0.0` tag). Publishing the
draft (not creating it) starts CI.

## Parameter

Require one bump kind (ask if missing):

| Input    | Semver effect         |
| -------- | --------------------- |
| `major`  | `X.Y.Z` → `(X+1).0.0` |
| `minor`  | `X.Y.Z` → `X.(Y+1).0` |
| `bugfix` | `X.Y.Z` → `X.Y.(Z+1)` |

## Preconditions (abort if unmet)

Run from the **sunsynk** repo root. Stop with a clear message unless **all** pass:

1. Current branch is `main`
2. Working tree is clean (`git status --porcelain` empty)
3. Bump parameter is one of `major` | `minor` | `bugfix`

## Steps

1. Rebase against the current head: `git pull --rebase`
2. Bump the version in `pyproject.toml` according to the input
3. Use the new version string and change the `## Unreleased` heading in
   `hass-addon-sunsynk-edge/CHANGELOG.md` to `## Release x.x.x`
4. Copy `hass-addon-sunsynk-edge/CHANGELOG.md` to `hass-addon-sunsynk-multi/CHANGELOG.md`
5. In `www/docs/reference/multi-options.md`, remove every edge-only option prefix
   `<i-mdi-dev-to class="vp-edge-option-icon" />` (list items and table cells). Leave the `::: tip`
   block unchanged — it stays for future edge-only options.
6. Commit using the release number (`0.0.0` form) as the message and push to GitHub
7. Create a draft GitHub release with tag `v0.0.0` (semantic version preceded by `v`)
8. Notify the user to review and **publish** the draft release on GitHub to start the release
   process

## Implementation notes

- Read current version from `[project]` → `version = "..."` in `pyproject.toml`.
- Heading match is case-insensitive for `## Unreleased`; write `## Release <new_version>` (no `v`
  prefix).
- Stage only `pyproject.toml`, `hass-addon-sunsynk-edge/CHANGELOG.md`,
  `hass-addon-sunsynk-multi/CHANGELOG.md`, and `www/docs/reference/multi-options.md` (if the edge
  prefixes were present). Include `uv.lock` if the version bump changed it. The multi CHANGELOG copy
  is the one allowed hand-edit under `hass-addon-sunsynk-multi/` in this skill (overwrite; do not
  merge).
- When stripping edge prefixes, delete the HTML tag and the space after it so bullets stay
  `- \`OPTION\`` (or the table cell starts with the backtick). Do not touch the tip, and do not
  rewrite surrounding option text.
- Do not copy `config.yaml` here. On a published release, `deployer2.yml` copies edge `config.yaml`,
  `translations/`, and `apparmor.txt` onto stable except `name`/`slug`, then sets `version` to the
  tag.
- Commit message is exactly the new version string (e.g. `0.9.4`), nothing else.
- Push: `git push` to `origin` on `main` (this skill authorizes push).
- Draft release (after push), with network/`gh` permissions as needed:

  ```bash
  gh release create "v${VER}" --draft --generate-notes --target main --title "v${VER}"
  ```

  Tag must be `v` + version (e.g. `v0.9.4`). CI strips the leading `v` when checking against
  `pyproject.toml`. Do **not** use `--latest` on a draft.
- Do **not** publish the release; leave it draft so the user can review notes first.
  `release.published` is what starts CI.

## Done message

Tell the user the new version, that the commit was pushed, link the draft release URL from `gh`, and
that they should publish the draft on GitHub when ready to start CI (PyPI + add-ons).

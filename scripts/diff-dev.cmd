@echo off
set a=hass-addon-sunsynk
set d=hass-addon-sunsynk-dev
git diff --no-index %a%\mqtt.py %d%\mqtt.py
git diff --no-index %a%\filter.py %d%\filter.py
git diff --no-index %a%\profiles.py %d%\profiles.py
git diff --no-index %a%\options.py %d%\options.py
git diff --no-index %a%\run.py %d%\run.py
git diff --no-index %a%\config.yaml %d%\config.yaml
git diff --no-index %a%\DOCS.md %d%\DOCS.md
git diff --no-index %a%\Dockerfile %d%\Dockerfile

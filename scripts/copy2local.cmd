@echo off
CALL :copy_ss hass-addon-sunsynk-multi,\\192.168.1.8\addons\hass-addon-sunsynk-multi
CALL :copy_addon hass-addon-mbusd,\\192.168.1.8\addons\hass-addon-mbusd

EXIT /B %ERRORLEVEL%

:copy_ss

echo # Copy sunsynk package
for %%f in (pyproject.toml,MANIFEST.in,LICENSE,README.md,uv.lock) do xcopy /Y "%%f" %~2\sunsynk\
xcopy /Y /S /EXCLUDE:scripts\copyexclude.txt src %~2\sunsynk\src\


:copy_addon
echo # Modify Config for local testing
set cf=%~1\config.localtest.yaml
cp %~1\config.yaml %cf%
sed -i 's/image:/# image:/' %cf%
sed -i 's/name: /name: A_LOCAL /' %cf%
xcopy /Y %cf% %~2\config.yaml

echo # Copy '%~1' to '%~2'
xcopy /Y /S /EXCLUDE:scripts\copyexclude.txt %~1 %~2

EXIT /B 0

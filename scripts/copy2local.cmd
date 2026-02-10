@echo off
CALL :copy_ss \\192.168.1.8\addons\hass-addon-sunsynk-multi
CALL :copy_config hass-addon-sunsynk-edge,\\192.168.1.8\addons\hass-addon-sunsynk-multi
CALL :copy__addon hass-addon-sunsynk-multi,\\192.168.1.8\addons\hass-addon-sunsynk-multi

CALL :copy_config hass-addon-mbusd,\\192.168.1.8\addons\hass-addon-mbusd
CALL :copy__addon hass-addon-mbusd,\\192.168.1.8\addons\hass-addon-mbusd

EXIT /B %ERRORLEVEL%

:copy_ss
echo # Copy sunsynk package
for %%f in (pyproject.toml,MANIFEST.in,LICENSE,README.md,uv.lock) do xcopy /Y "%%f" %~1\sunsynk\
xcopy /Y /S /EXCLUDE:scripts\copyexclude.txt src %~1\sunsynk\src\
EXIT /B 0

:copy_config
echo # Modify Config for local testing
set cf=%~1\config.localtest.yaml
cp %~1\config.yaml %cf%
sed -i 's/image:/# image:/' %cf%
sed -i 's/name: /name: A_LOCAL /' %cf%
xcopy /Y %cf% %~2\config.yaml
EXIT /B 0

:copy__addon
echo 0.0.0 > %~1\VERSION
echo # Copy '%~1' to '%~2'
xcopy /Y /S /EXCLUDE:scripts\copyexclude.txt %~1 %~2
EXIT /B 0

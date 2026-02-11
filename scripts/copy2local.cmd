@echo off
set DEST=\\192.168.1.8\addons
CALL :copy_sunsynk hass-addon-sunsynk-edge
CALL :copy_addon hass-addon-sunsynk-edge
CALL :copy_builder hass-addon-sunsynk-edge

rem CALL :copy_config hass-addon-mbusd,\\192.168.1.8\addons\hass-addon-mbusd
rem CALL :copy__addon hass-addon-mbusd,\\192.168.1.8\addons\hass-addon-mbusd

EXIT /B %ERRORLEVEL%

:copy_sunsynk
CALL :print "Copy sunsynk package for '%~1'"
for %%f in (pyproject.toml,MANIFEST.in,LICENSE,README.md,uv.lock) do xcopy /Y "%%f" %DEST%\%~1\sunsynk\
xcopy /Y /S /EXCLUDE:scripts\copyexclude.txt src %DEST%\%~1\sunsynk\src\

:copy_addon
CALL :print "Copy '%~1' to '%DEST%\%~1'"
xcopy /Y /S /EXCLUDE:scripts\copyexclude.txt %~1 %DEST%\%~1
EXIT /B 0

CALL :print "Modify Config for local testing"
set cf=%~1\config.localtest.yaml
cp %~1\config.yaml %cf%
sed -i 's/image:/# image:/' %cf%
sed -i 's/name: /name: A_LOCAL /' %cf%
xcopy /Y %cf% %DEST%\%~1\config.yaml*
EXIT /B 0

:copy_builder
CALL :print "Copy builder files for '%~1'"
xcopy /Y hass-addon-sunsynk-multi\Dockerfile %DEST%\%~1\
xcopy /Y hass-addon-sunsynk-multi\build.yaml %DEST%\%~1\
xcopy /Y /S hass-addon-sunsynk-multi\rootfs %DEST%\%~1\rootfs\
echo 0.0.0 > %DEST%\%~1\VERSION
EXIT /B 0

:print
echo.
echo %~1
echo ===========================================================
echo.
EXIT /B 0

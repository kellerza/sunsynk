@echo off
rem CALL :copy2 hass-addon-sunsynk,\\192.168.1.7\addons\hass-addon-sunsynk\
CALL :copy2 hass-addon-sunsynk-multi,\\192.168.1.8\addons\hass-addon-sunsynk-multi\
rem xcopy /Y hass-addon-mbusd \\192.168.1.7\addons\hass-addon-mbusd\

EXIT /B %ERRORLEVEL%

:copy2
echo # Copy '%~1' to '%~2'
xcopy /Y %~1 %~2
xcopy /Y setup.* %~2\sunsynk\
xcopy /Y README.md %~2\sunsynk\
xcopy /Y /S %~1\rootfs %~2\rootfs\
xcopy /Y /S %~1\translations %~2\translations\
xcopy /Y /S /EXCLUDE:scripts\copyexclude.txt src %~2\sunsynk\src\

for /f %%i in ('application arg0 arg1') do set ID=%%i
echo %ID%
echo # Modify Config for local testing
set cf=%~1\config.localtest.yaml
cp %~1\config.yaml %cf%
sed -i 's/image:/# image:/' %cf%
sed -i 's/name: /name: LOCAL /' %cf%
@REM echo %TIME%| sed -r 's/([0-9]+:)+//'> .id
@REM set /p "VER=" < .id
@REM echo Version: "%VER%"
@REM sed -i 's/version:.*\"/version: \"%VER%\"/' %cf%
xcopy /Y %cf% %~2\config.yaml

@REM echo # Modify Dockerfile
@REM cp %~1\Dockerfile %~1\Dockerfile.local
@REM rem Comment out installing sunsynk from pypi
@REM sed -i 's/RUN pip3/# RUN pip3/' %~1\Dockerfile.local
@REM rem Uncomment local test commands
@REM sed -i -E 's/#! (# )?//' %~1\Dockerfile.local
@REM rem sed -i 's/#! //' %~1\Dockerfile.local
@REM xcopy /Y %~1\Dockerfile.local %~2\Dockerfile
xcopy /Y %~1\Dockerfile.local %~2\Dockerfile

EXIT /B 0

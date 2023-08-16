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
echo # Modify Dockerfile
cp %~1\Dockerfile %~1\Dockerfile.local
rem Comment out installing sunsynk from pypi
sed -i 's/RUN pip3/# RUN pip3/' %~1\Dockerfile.local
rem Uncomment local test commands
sed -i -E 's/#! (# )?//' %~1\Dockerfile.local
rem sed -i 's/#! //' %~1\Dockerfile.local
xcopy /Y %~1\Dockerfile.local %~2\Dockerfile


cp %~1\config.yaml config.tmp
sed -i 's/name: /name: LOCAL /' config.tmp
xcopy /Y config.tmp %~2\config.yaml
rm config.tmp

EXIT /B 0

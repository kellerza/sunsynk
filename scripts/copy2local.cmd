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
xcopy /Y sunsynk %~2\sunsynk\sunsynk\
echo # Modify Dockerfile
cp %~1\Dockerfile Dockerfile.tmp
sed -i '/    sunsynk/d'  Dockerfile.tmp
cat Dockerfile.tmp | grep sunsynk
sed -i 's/# RUN pip3 install -e/RUN pip3 install -e/' Dockerfile.tmp
xcopy /Y Dockerfile.tmp %~2\Dockerfile
rm Dockerfile.tmp


cp %~1\config.yaml config.tmp
sed -i 's/name: /name: LOCAL /' config.tmp
xcopy /Y config.tmp %~2\config.yaml
rm config.tmp

EXIT /B 0

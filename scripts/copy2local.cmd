@echo off
CALL :copy2 hass-addon-sunsynk,\\192.168.1.7\addons\hass-addon-sunsynk\
CALL :copy2 hass-addon-sunsynk-dev,\\192.168.1.7\addons\hass-addon-sunsynk-dev\
xcopy /Y hass-addon-mbusd \\192.168.1.7\addons\hass-addon-mbusd\

EXIT /B %ERRORLEVEL%

:copy2
echo # Copy '%~1' to '%~2'
xcopy /Y %~1 %~2
xcopy /Y setup.py %~2\sunsynk\
xcopy /Y README.md %~2\sunsynk\
xcopy /Y requirements.txt %~2\sunsynk\
xcopy /Y sunsynk %~2\sunsynk\sunsynk\
echo # Modify Dockerfile
cp %~1\Dockerfile Dockerfile.tmp
sed -i 's/ sunsynk==[0-9.]*$//' Dockerfile.tmp
sed -i 's/# RUN pip3 install -e/RUN pip3 install -e/' Dockerfile.tmp
xcopy /Y Dockerfile.tmp %~2\Dockerfile
rm Dockerfile.tmp
EXIT /B 0

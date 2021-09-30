@echo off
set dest=\\192.168.88.3\addons\hass-addon-sunsynk\
echo # Copy to %dest%
xcopy /Y hass-addon-sunsynk %dest%
xcopy /Y setup.py %dest%\sunsynk\
xcopy /Y README.md %dest%\sunsynk\
xcopy /Y requirements.txt %dest%\sunsynk\
xcopy /Y sunsynk %dest%\sunsynk\sunsynk\
echo # Modify Dockerfile
cp hass-addon-sunsynk\Dockerfile Dockerfile.local
sed -i 's/ sunsynk==[0-9.]*$//' Dockerfile.local
sed -i 's/# RUN pip3 install -e/RUN pip3 install -e/' Dockerfile.local
xcopy /Y Dockerfile.local %dest%\Dockerfile
rm Dockerfile.local


set dest=\\192.168.88.3\addons\hass-addon-mbusd\
xcopy /Y hass-addon-mbusd %dest%

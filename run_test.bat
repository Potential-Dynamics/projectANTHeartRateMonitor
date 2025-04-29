@echo off

:: Activate the virtual environment
call .\myenv\Scripts\activate

:: Change directory to 'examples'
@REM cd examples

:: Run the Python script
python3 src\heart_rate_mqtt_broker.py
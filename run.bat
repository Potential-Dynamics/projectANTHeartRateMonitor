@echo off

:: Activate the virtual environment
call .\myenv\Scripts\activate

:: Run the Python script
python src\heart_rate_mqtt_broker.py
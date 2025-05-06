@echo on
REM Display current directory
echo Current directory: %CD%

REM Activate with full path (adjust as needed)
call "%CD%\myenv\Scripts\activate"

REM Verify python location
where python

REM Run script with full path
"%CD%\myenv\Scripts\python.exe" "src\gui_script.py" 

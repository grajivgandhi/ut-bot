@echo off
cd /d "%~dp0"
:loop
python main.py
echo Bot stopped. Restarting in 5 seconds...
timeout /t 5
goto loop

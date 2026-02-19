@echo off
:: RedTeam AI Launcher
:: Launches the app without a console window using pythonw
cd /d "%~dp0"
start "" "C:\Python314\pythonw.exe" "%~dp0main.py"

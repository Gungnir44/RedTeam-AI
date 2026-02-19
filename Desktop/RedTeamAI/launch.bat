@echo off
:: RedTeam AI Launcher
:: Auto-installs dependencies on first run, then launches the app.

cd /d "%~dp0"

:: Check if PyQt6 is installed
"C:\Python314\python.exe" -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo Installing dependencies, please wait...
    "C:\Python314\python.exe" -m pip install -r "%~dp0requirements.txt" --quiet
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies.
        echo Please run: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo Dependencies installed.
)

:: Launch without console window
start "" "C:\Python314\pythonw.exe" "%~dp0main.py"

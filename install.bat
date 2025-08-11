@echo off
echo Installing Quotex Signal Bot...
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Installing required packages...
pip install -r requirements.txt

echo.
echo Installation complete!
echo Run 'start.bat' to launch the application
pause

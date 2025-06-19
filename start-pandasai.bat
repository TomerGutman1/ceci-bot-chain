@echo off
echo Starting PandasAI Service...
echo ==========================

cd /d "%~dp0\server\src\services\python"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements_pandasai.txt

REM Run the PandasAI service
echo.
echo Starting PandasAI service on http://localhost:8001
echo Press Ctrl+C to stop
echo.
python pandasai_service.py

pause

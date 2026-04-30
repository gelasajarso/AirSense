@echo off
echo ========================================
echo AirSense - Running without Java/Spark
echo ========================================
echo.
echo NOTE: Java is not installed, so Spark pipeline cannot run.
echo This script will start the API and Dashboard only.
echo.
echo To use the full system with data processing:
echo 1. Install Java 11+ from https://adoptium.net/
echo 2. Set JAVA_HOME environment variable
echo 3. Run run_system.bat
echo.
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then run: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo Using Python from virtual environment...
.venv\Scripts\python.exe --version
echo.

REM Check if processed data exists
if not exist "data\processed\*.parquet" (
    echo WARNING: No processed data found!
    echo The API will work but data endpoints will return 404.
    echo.
    echo To process data, you need to:
    echo 1. Install Java 11+
    echo 2. Run: .venv\Scripts\python.exe src\main.py pipeline
    echo.
    echo Press any key to continue anyway...
    pause
)

echo Starting API server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Starting Dashboard on http://localhost:8501
echo.
echo Press Ctrl+C to stop the servers
echo.

REM Start API in background
start "AirSense API" /MIN .venv\Scripts\python.exe src\main.py api

REM Wait a bit for API to start
timeout /t 5 /nobreak >nul

REM Start Dashboard
start "AirSense Dashboard" .venv\Scripts\python.exe src\main.py dashboard

echo.
echo ========================================
echo AirSense is running!
echo ========================================
echo API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Dashboard: http://localhost:8501
echo.
echo Close the terminal windows to stop the servers.
echo ========================================

pause

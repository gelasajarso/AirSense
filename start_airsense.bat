@echo off
title AirSense System Launcher
color 0A
echo.
echo  ================================================
echo   AirSense - Air Quality Monitoring System
echo  ================================================
echo.

REM -------------------------------------------------------
REM  Find Python
REM -------------------------------------------------------
set PYTHON=
python --version >nul 2>&1
if %errorlevel%==0 (
    set PYTHON=python
    goto :found_python
)
py --version >nul 2>&1
if %errorlevel%==0 (
    set PYTHON=py
    goto :found_python
)
python3 --version >nul 2>&1
if %errorlevel%==0 (
    set PYTHON=python3
    goto :found_python
)

echo  [ERROR] Python not found in PATH.
echo  Please install Python 3.9+ from https://www.python.org
pause
exit /b 1

:found_python
echo  [OK] Found Python:
%PYTHON% --version
echo.

REM -------------------------------------------------------
REM  Install / update requirements
REM -------------------------------------------------------
echo  Installing requirements...
%PYTHON% -m pip install --upgrade pip --quiet
%PYTHON% -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to install requirements.
    pause
    exit /b 1
)
echo  [OK] Requirements installed.
echo.

REM -------------------------------------------------------
REM  Generate processed data (if not already present)
REM -------------------------------------------------------
echo  Checking for processed data...
dir /b data\processed\*.parquet >nul 2>&1
if %errorlevel% neq 0 (
    echo  No processed data found - running data processor...
    %PYTHON% process_data_simple.py
    if %errorlevel% neq 0 (
        echo  [ERROR] Data processing failed.
        pause
        exit /b 1
    )
) else (
    echo  [OK] Processed data already exists.
)
echo.

REM -------------------------------------------------------
REM  Start API server in a new window
REM -------------------------------------------------------
echo  Starting API server on http://localhost:8000 ...
start "AirSense API" cmd /k "%PYTHON% -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a moment for the API to initialise
timeout /t 4 /nobreak >nul

REM -------------------------------------------------------
REM  Start Streamlit dashboard in a new window
REM -------------------------------------------------------
echo  Starting Dashboard on http://localhost:8501 ...
start "AirSense Dashboard" cmd /k "%PYTHON% -m streamlit run frontend/dashboard.py --server.port 8501 --server.headless true"

REM Wait for dashboard to start
timeout /t 4 /nobreak >nul

REM -------------------------------------------------------
REM  Open browser
REM -------------------------------------------------------
echo  Opening dashboard in browser...
start http://localhost:8501

echo.
echo  ================================================
echo   System is running!
echo    Dashboard : http://localhost:8501
echo    API       : http://localhost:8000
echo    API Docs  : http://localhost:8000/docs
echo  ================================================
echo.
echo  Close the API and Dashboard windows to stop the system.
echo.
pause

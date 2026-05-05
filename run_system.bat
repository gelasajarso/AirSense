@echo off
echo AirSense System Startup Script
echo ==============================
echo.

REM Try different Python installations
echo Checking for Python installations...

REM Try standard python command
python --version >nul 2>&1
if %errorlevel% == 0 (
    REM Check if pip is available
    python -m pip --version >nul 2>&1
    if %errorlevel% == 0 (
        echo Found Python with pip:
        python --version
        python -m pip --version
        echo.
        echo Installing dependencies...
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
        echo.
        echo Starting AirSense system...
        python -m src.main all
        goto :end
    ) else (
        echo Found Python but pip is not available, skipping...
        echo.
    )
)

REM Try py command
py --version >nul 2>&1
if %errorlevel% == 0 (
    REM Check if pip is available
    py -m pip --version >nul 2>&1
    if %errorlevel% == 0 (
        echo Found Python with pip:
        py --version
        py -m pip --version
        echo.
        echo Installing dependencies...
        py -m pip install --upgrade pip
        py -m pip install -r requirements.txt
        echo.
        echo Starting AirSense system...
        py -m src.main all
        goto :end
    ) else (
        echo Found Python but pip is not available, skipping...
        echo.
    )
)

REM Try python3 command
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    REM Check if pip is available
    python3 -m pip --version >nul 2>&1
    if %errorlevel% == 0 (
        echo Found Python with pip:
        python3 --version
        python3 -m pip --version
        echo.
        echo Installing dependencies...
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
        echo.
        echo Starting AirSense system...
        python3 -m src.main all
        goto :end
    ) else (
        echo Found Python but pip is not available, skipping...
        echo.
    )
)

REM Try PostgreSQL Python (bundled - last resort)
"C:\Program Files\PostgreSQL\18\pgAdmin 4\python.exe" --version >nul 2>&1
if %errorlevel% == 0 (
    REM Check if pip is available
    "C:\Program Files\PostgreSQL\18\pgAdmin 4\python.exe" -m pip --version >nul 2>&1
    if %errorlevel% == 0 (
        echo Found Python with pip (PostgreSQL bundled):
        "C:\Program Files\PostgreSQL\18\pgAdmin 4\python.exe" --version
        "C:\Program Files\PostgreSQL\18\pgAdmin 4\python.exe" -m pip --version
        echo.
        echo Installing dependencies...
        "C:\Program Files\PostgreSQL\18\pgAdmin 4\python.exe" -m pip install --upgrade pip
        "C:\Program Files\PostgreSQL\18\pgAdmin 4\python.exe" -m pip install -r requirements.txt
        echo.
        echo Starting AirSense system...
        "C:\Program Files\PostgreSQL\18\pgAdmin 4\python.exe" -m src.main all
        goto :end
    ) else (
        echo Found Python but pip is not available, skipping...
        echo.
    )
)

REM Try Nmap Python (bundled - last resort)
"C:\Program Files (x86)\Nmap\zenmap\bin\python.exe" --version >nul 2>&1
if %errorlevel% == 0 (
    REM Check if pip is available
    "C:\Program Files (x86)\Nmap\zenmap\bin\python.exe" -m pip --version >nul 2>&1
    if %errorlevel% == 0 (
        echo Found Python with pip (Nmap bundled):
        "C:\Program Files (x86)\Nmap\zenmap\bin\python.exe" --version
        "C:\Program Files (x86)\Nmap\zenmap\bin\python.exe" -m pip --version
        echo.
        echo Installing dependencies...
        "C:\Program Files (x86)\Nmap\zenmap\bin\python.exe" -m pip install --upgrade pip
        "C:\Program Files (x86)\Nmap\zenmap\bin\python.exe" -m pip install -r requirements.txt
        echo.
        echo Starting AirSense system...
        "C:\Program Files (x86)\Nmap\zenmap\bin\python.exe" -m src.main all
        goto :end
    ) else (
        echo Found Python but pip is not available, skipping...
        echo.
    )
)

echo No Python installation with pip found!
echo.
echo Please ensure Python 3.9+ is installed from https://python.org
echo and that it is added to your system PATH.
echo.
echo To verify: Open a new command prompt and run 'python --version'
echo Then check pip with: 'python -m pip --version'
echo.

:end
pause

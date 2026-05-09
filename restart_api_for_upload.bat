@echo off
echo ========================================
echo Restarting AirSense API Server
echo ========================================
echo.

echo Stopping any running API servers...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting API server with upload endpoint...
echo.

python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

pause

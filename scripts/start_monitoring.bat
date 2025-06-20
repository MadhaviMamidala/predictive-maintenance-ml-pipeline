@echo off
echo ========================================
echo    ML Monitoring Automation Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if Docker is running
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo Starting ML Monitoring Automation...
echo.
echo This will:
echo - Start the Predictive Maintenance API
echo - Start Prometheus and Grafana containers
echo - Generate test traffic
echo - Verify dashboard functionality
echo.
echo Press any key to continue...
pause >nul

REM Run the automation script
python automate_monitoring.py

echo.
echo Automation completed!
pause 
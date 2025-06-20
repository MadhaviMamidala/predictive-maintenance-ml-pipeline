@echo off
setlocal

REM ############################################################################
REM #
REM # CoreDefender ML Lifecycle - Local Monitoring Stack Management Script
REM #
REM # This script provides a single, reliable interface to manage the
REM # local monitoring environment (API, Prometheus, Grafana).
REM #
REM # Usage:
REM #   start_local_monitoring.bat [command]
REM #
REM # Commands:
REM #   start   - Build and start all services in detached mode. (Default)
REM #   up      - Start all services in the foreground to see live logs.
REM #   stop    - Stop all services.
REM #   down    - Stop and remove all services.
REM #   logs    - Follow the logs of all running services.
REM #   clean   - Stop services and remove all data volumes for a fresh start.
REM #   ps      - Show the status of running containers.
REM #   help    - Display this help message.
REM #
REM ############################################################################

set COMPOSE_FILE=docker-compose.prod.yml

IF /I "%1" == "start" GOTO start_services
IF /I "%1" == "up" GOTO up_services
IF /I "%1" == "stop" GOTO stop_services
IF /I "%1" == "down" GOTO down_services
IF /I "%1" == "logs" GOTO follow_logs
IF /I "%1" == "clean" GOTO clean_services
IF /I "%1" == "ps" GOTO show_status
IF /I "%1" == "help" GOTO show_help
IF /I "%1" == "" GOTO start_services

echo Invalid command: %1
GOTO show_help

:start_services
echo.
echo ==========================================================
echo =  Starting CoreDefender Local Monitoring Stack...
echo ==========================================================
docker-compose -f %COMPOSE_FILE% up --build -d
GOTO end

:up_services
echo.
echo ==========================================================
echo =  Starting Services in Foreground (Press Ctrl+C to stop)
echo ==========================================================
docker-compose -f %COMPOSE_FILE% up --build
GOTO end

:stop_services
echo.
echo ==========================================================
echo =  Stopping CoreDefender Local Monitoring Stack...
echo ==========================================================
docker-compose -f %COMPOSE_FILE% stop
GOTO end

:down_services
echo.
echo ==========================================================
echo =  Stopping and Removing CoreDefender Containers...
echo ==========================================================
docker-compose -f %COMPOSE_FILE% down
GOTO end

:follow_logs
echo.
echo ==========================================================
echo =  Following Logs... (Press Ctrl+C to exit)
echo ==========================================================
docker-compose -f %COMPOSE_FILE% logs -f
GOTO end

:clean_services
echo.
echo ==========================================================
echo =  Cleaning Environment (Removing Containers and Volumes)
echo ==========================================================
docker-compose -f %COMPOSE_FILE% down -v
GOTO end

:show_status
echo.
echo ==========================================================
echo =  Current Container Status
echo ==========================================================
docker-compose -f %COMPOSE_FILE% ps
GOTO end

:show_help
echo.
echo Usage: start_local_monitoring.bat [command]
echo.
echo Commands:
echo   start   - Build and start all services. (Default)
echo   up      - Start services in foreground to see live logs.
echo   stop    - Stop all services.
echo   down    - Stop and remove all services.
echo   logs    - Follow the logs of all running services.
echo   clean   - Stop services and remove data volumes.
echo   ps      - Show the status of running containers.
echo   help    - Display this help message.
echo.
GOTO end

:end
endlocal 
@echo off
setlocal enabledelayedexpansion

REM Production Deployment Script for ML Lifecycle (Windows)
REM This script deploys the entire ML system to production

echo 🚀 Production Deployment for ML Lifecycle
echo ==================================================

REM Configuration
set PROJECT_NAME=ml-lifecycle
set DOMAIN=%1
if "%DOMAIN%"=="" set DOMAIN=localhost
set EMAIL=%2
if "%EMAIL%"=="" set EMAIL=admin@example.com

echo Domain: %DOMAIN%
echo Email: %EMAIL%
echo.

REM Check prerequisites
echo Checking prerequisites...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ✗ Docker is not running. Please start Docker Desktop.
    exit /b 1
)
echo ✓ Docker is running

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Docker Compose is not installed.
    exit /b 1
)
echo ✓ Docker Compose is available

REM Create necessary directories
echo Creating directories...
if not exist logs mkdir logs
if not exist nginx\ssl mkdir nginx\ssl
if not exist nginx\logs mkdir nginx\logs
if not exist data\backups mkdir data\backups
echo ✓ Directories created

REM Generate SSL certificates (self-signed for development)
echo Generating SSL certificates...
if not exist nginx\ssl\cert.pem (
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx\ssl\key.pem -out nginx\ssl\cert.pem -subj "/C=US/ST=State/L=City/O=Organization/CN=%DOMAIN%"
    echo ✓ SSL certificates generated
) else (
    echo ✓ SSL certificates already exist
)

REM Check if model exists
echo Checking model files...
if not exist models\best_model.pkl (
    echo ⚠ Model file not found. Training model...
    python src\training\train_random_forest.py
    if not exist models\best_model.pkl (
        echo ✗ Model training failed. Please check the training script.
        exit /b 1
    )
    echo ✓ Model trained successfully
) else (
    echo ✓ Model file exists
)

REM Stop any existing containers
echo Stopping existing containers...
docker-compose -f docker-compose.production.yml down --remove-orphans >nul 2>&1
echo ✓ Existing containers stopped

REM Build and start services
echo Building and starting services...
docker-compose -f docker-compose.production.yml up -d --build

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check service health
echo Checking service health...

REM Check API health
curl -f -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ✗ API health check failed
    docker-compose -f docker-compose.production.yml logs predictive-maintenance-api
    exit /b 1
) else (
    echo ✓ API is healthy
)

REM Check Prometheus
curl -f -s http://localhost:9090/-/healthy >nul 2>&1
if errorlevel 1 (
    echo ✗ Prometheus health check failed
) else (
    echo ✓ Prometheus is healthy
)

REM Check Grafana
curl -f -s http://localhost:3000/api/health >nul 2>&1
if errorlevel 1 (
    echo ✗ Grafana health check failed
) else (
    echo ✓ Grafana is healthy
)

REM Check PostgreSQL
docker exec postgres-prod pg_isready -U ml_user -d ml_predictions >nul 2>&1
if errorlevel 1 (
    echo ✗ PostgreSQL health check failed
) else (
    echo ✓ PostgreSQL is healthy
)

REM Check Redis
docker exec redis-prod redis-cli -a redis123 ping >nul 2>&1
if errorlevel 1 (
    echo ✗ Redis health check failed
) else (
    echo ✓ Redis is healthy
)

REM Generate test traffic
echo Generating test traffic...
python -c "
import requests
import time
import random

# Generate test predictions
for i in range(10):
    data = {
        'machineID': random.randint(1, 100),
        'volt': random.uniform(170, 250),
        'rotate': random.uniform(1168, 2886),
        'pressure': random.uniform(100, 200),
        'vibration': random.uniform(40, 60),
        'age': random.randint(0, 20)
    }
    
    try:
        response = requests.post('http://localhost:8000/predict', json=data, timeout=5)
        if response.status_code == 200:
            print(f'Test prediction {i+1}: Success')
        else:
            print(f'Test prediction {i+1}: Failed - {response.status_code}')
    except Exception as e:
        print(f'Test prediction {i+1}: Error - {e}')
    
    time.sleep(0.5)
"
echo ✓ Test traffic generated

REM Display deployment information
echo.
echo 🎉 Production Deployment Complete!
echo ==================================================
echo.
echo Service URLs:
echo   API Documentation: https://%DOMAIN%/docs
echo   API Health Check:  https://%DOMAIN%/health
echo   Monitoring Dashboard: https://%DOMAIN%/monitoring
echo   Prometheus:        http://localhost:9090
echo   Grafana:           http://localhost:3000
echo.
echo Credentials:
echo   Grafana:           admin / admin123
echo   PostgreSQL:        ml_user / ml_password123
echo   Redis:             password: redis123
echo.
echo Management Commands:
echo   View logs:         docker-compose -f docker-compose.production.yml logs -f
echo   Stop services:     docker-compose -f docker-compose.production.yml down
echo   Restart services:  docker-compose -f docker-compose.production.yml restart
echo   Update services:   docker-compose -f docker-compose.production.yml up -d --build
echo.
echo Monitoring:
echo   Check all services: docker-compose -f docker-compose.production.yml ps
echo   View resource usage: docker stats
echo.

REM Create deployment info file
echo Production Deployment Information > deployment_info.txt
echo ================================ >> deployment_info.txt
echo. >> deployment_info.txt
echo Deployment Date: %date% %time% >> deployment_info.txt
echo Domain: %DOMAIN% >> deployment_info.txt
echo Email: %EMAIL% >> deployment_info.txt
echo. >> deployment_info.txt
echo Service URLs: >> deployment_info.txt
echo - API Documentation: https://%DOMAIN%/docs >> deployment_info.txt
echo - API Health Check: https://%DOMAIN%/health >> deployment_info.txt
echo - Monitoring Dashboard: https://%DOMAIN%/monitoring >> deployment_info.txt
echo - Prometheus: http://localhost:9090 >> deployment_info.txt
echo - Grafana: http://localhost:3000 >> deployment_info.txt
echo. >> deployment_info.txt
echo Credentials: >> deployment_info.txt
echo - Grafana: admin / admin123 >> deployment_info.txt
echo - PostgreSQL: ml_user / ml_password123 >> deployment_info.txt
echo - Redis: password: redis123 >> deployment_info.txt
echo. >> deployment_info.txt
echo Management Commands: >> deployment_info.txt
echo - View logs: docker-compose -f docker-compose.production.yml logs -f >> deployment_info.txt
echo - Stop services: docker-compose -f docker-compose.production.yml down >> deployment_info.txt
echo - Restart services: docker-compose -f docker-compose.production.yml restart >> deployment_info.txt
echo - Update services: docker-compose -f docker-compose.production.yml up -d --build >> deployment_info.txt

echo ✓ Deployment information saved to deployment_info.txt

echo ✅ Production deployment completed successfully!
pause 
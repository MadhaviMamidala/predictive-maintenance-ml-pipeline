#!/bin/bash

# Production Deployment Script for ML Lifecycle
# This script deploys the entire ML system to production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ml-lifecycle"
DOMAIN="${1:-localhost}"
EMAIL="${2:-admin@example.com}"

echo -e "${BLUE}🚀 Production Deployment for ML Lifecycle${NC}"
echo "=================================================="
echo -e "Domain: ${YELLOW}$DOMAIN${NC}"
echo -e "Email: ${YELLOW}$EMAIL${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi
print_status "Docker is running"

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed."
    exit 1
fi
print_status "Docker Compose is available"

# Create necessary directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p logs
mkdir -p nginx/ssl
mkdir -p nginx/logs
mkdir -p data/backups
print_status "Directories created"

# Generate SSL certificates (self-signed for development)
echo -e "${BLUE}Generating SSL certificates...${NC}"
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
    print_status "SSL certificates generated"
else
    print_status "SSL certificates already exist"
fi

# Set proper permissions
chmod 600 nginx/ssl/key.pem
chmod 644 nginx/ssl/cert.pem

# Check if model exists
echo -e "${BLUE}Checking model files...${NC}"
if [ ! -f models/best_model.pkl ]; then
    print_warning "Model file not found. Training model..."
    python src/training/train_random_forest.py
    if [ ! -f models/best_model.pkl ]; then
        print_error "Model training failed. Please check the training script."
        exit 1
    fi
    print_status "Model trained successfully"
else
    print_status "Model file exists"
fi

# Stop any existing containers
echo -e "${BLUE}Stopping existing containers...${NC}"
docker-compose -f docker-compose.production.yml down --remove-orphans 2>/dev/null || true
print_status "Existing containers stopped"

# Build and start services
echo -e "${BLUE}Building and starting services...${NC}"
docker-compose -f docker-compose.production.yml up -d --build

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to be ready...${NC}"
sleep 30

# Check service health
echo -e "${BLUE}Checking service health...${NC}"

# Check API health
if curl -f -s http://localhost:8000/health > /dev/null; then
    print_status "API is healthy"
else
    print_error "API health check failed"
    docker-compose -f docker-compose.production.yml logs predictive-maintenance-api
    exit 1
fi

# Check Prometheus
if curl -f -s http://localhost:9090/-/healthy > /dev/null; then
    print_status "Prometheus is healthy"
else
    print_error "Prometheus health check failed"
fi

# Check Grafana
if curl -f -s http://localhost:3000/api/health > /dev/null; then
    print_status "Grafana is healthy"
else
    print_error "Grafana health check failed"
fi

# Check PostgreSQL
if docker exec postgres-prod pg_isready -U ml_user -d ml_predictions > /dev/null 2>&1; then
    print_status "PostgreSQL is healthy"
else
    print_error "PostgreSQL health check failed"
fi

# Check Redis
if docker exec redis-prod redis-cli -a redis123 ping > /dev/null 2>&1; then
    print_status "Redis is healthy"
else
    print_error "Redis health check failed"
fi

# Generate test traffic
echo -e "${BLUE}Generating test traffic...${NC}"
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
print_status "Test traffic generated"

# Display deployment information
echo ""
echo -e "${GREEN}🎉 Production Deployment Complete!${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}Service URLs:${NC}"
echo -e "  API Documentation: ${YELLOW}https://$DOMAIN/docs${NC}"
echo -e "  API Health Check:  ${YELLOW}https://$DOMAIN/health${NC}"
echo -e "  Monitoring Dashboard: ${YELLOW}https://$DOMAIN/monitoring${NC}"
echo -e "  Prometheus:        ${YELLOW}http://localhost:9090${NC}"
echo -e "  Grafana:           ${YELLOW}http://localhost:3000${NC}"
echo ""
echo -e "${BLUE}Credentials:${NC}"
echo -e "  Grafana:           ${YELLOW}admin / admin123${NC}"
echo -e "  PostgreSQL:        ${YELLOW}ml_user / ml_password123${NC}"
echo -e "  Redis:             ${YELLOW}password: redis123${NC}"
echo ""
echo -e "${BLUE}Management Commands:${NC}"
echo -e "  View logs:         ${YELLOW}docker-compose -f docker-compose.production.yml logs -f${NC}"
echo -e "  Stop services:     ${YELLOW}docker-compose -f docker-compose.production.yml down${NC}"
echo -e "  Restart services:  ${YELLOW}docker-compose -f docker-compose.production.yml restart${NC}"
echo -e "  Update services:   ${YELLOW}docker-compose -f docker-compose.production.yml up -d --build${NC}"
echo ""
echo -e "${BLUE}Monitoring:${NC}"
echo -e "  Check all services: ${YELLOW}docker-compose -f docker-compose.production.yml ps${NC}"
echo -e "  View resource usage: ${YELLOW}docker stats${NC}"
echo ""

# Create deployment info file
cat > deployment_info.txt << EOF
Production Deployment Information
================================

Deployment Date: $(date)
Domain: $DOMAIN
Email: $EMAIL

Service URLs:
- API Documentation: https://$DOMAIN/docs
- API Health Check: https://$DOMAIN/health
- Monitoring Dashboard: https://$DOMAIN/monitoring
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Credentials:
- Grafana: admin / admin123
- PostgreSQL: ml_user / ml_password123
- Redis: password: redis123

Management Commands:
- View logs: docker-compose -f docker-compose.production.yml logs -f
- Stop services: docker-compose -f docker-compose.production.yml down
- Restart services: docker-compose -f docker-compose.production.yml restart
- Update services: docker-compose -f docker-compose.production.yml up -d --build
EOF

print_status "Deployment information saved to deployment_info.txt"

echo -e "${GREEN}✅ Production deployment completed successfully!${NC}" 
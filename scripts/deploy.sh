#!/bin/bash

# Production Deployment Script for Predictive Maintenance API

set -e

echo "🚀 Starting Production Deployment..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if required files exist
print_status "Checking required files..."

REQUIRED_FILES=(
    "models/random_forest_model.joblib"
    "src/api/main.py"
    "docker/Dockerfile.api"
    "docker-compose.prod.yml"
    "requirements.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file not found: $file"
        exit 1
    fi
done

print_status "All required files found."

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p nginx/ssl
mkdir -p monitoring

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down --remove-orphans || true

# Build and start the application
print_status "Building and starting application..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check if services are healthy
print_status "Checking service health..."

# Check API health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ API is healthy"
else
    print_error "❌ API health check failed"
    docker-compose -f docker-compose.prod.yml logs predictive-maintenance-api
    exit 1
fi

# Check nginx
if curl -f http://localhost:80 > /dev/null 2>&1; then
    print_status "✅ Nginx is healthy"
else
    print_warning "⚠️  Nginx health check failed (this might be expected if no SSL is configured)"
fi

# Display service information
echo ""
echo "🎉 Deployment completed successfully!"
echo "====================================="
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo "Nginx Proxy: http://localhost:80"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose -f docker-compose.prod.yml down"
echo ""

# Run a quick test
print_status "Running deployment test..."
if curl -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"machineID": 1, "volt": 220.5, "rotate": 1200, "pressure": 95.0, "vibration": 0.5, "age": 12, "model": "model_A"}' \
    > /dev/null 2>&1; then
    print_status "✅ API prediction test passed"
else
    print_warning "⚠️  API prediction test failed"
fi

print_status "Deployment script completed!" 
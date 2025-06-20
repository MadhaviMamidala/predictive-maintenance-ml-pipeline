#!/bin/bash

echo "========================================"
echo "   ML Monitoring Automation Script"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker and try again"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker daemon is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "Starting ML Monitoring Automation..."
echo
echo "This will:"
echo "- Start the Predictive Maintenance API"
echo "- Start Prometheus and Grafana containers"
echo "- Generate test traffic"
echo "- Verify dashboard functionality"
echo
read -p "Press Enter to continue..."

# Make the script executable
chmod +x automate_monitoring.py

# Run the automation script
python3 automate_monitoring.py

echo
echo "Automation completed!" 
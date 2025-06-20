#!/usr/bin/env python3
"""
Continuous ML Monitoring Script
===============================
This script runs continuously in the background to maintain the monitoring system.
It performs periodic health checks and restarts services if needed.
"""

import subprocess
import time
import requests
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('continuous_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ContinuousMonitor:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.grafana_url = "http://localhost:3000"
        self.prometheus_url = "http://localhost:9090"
        self.check_interval = 60  # Check every 60 seconds
        self.traffic_interval = 300  # Generate traffic every 5 minutes
        
    def check_api_health(self):
        """Check if the API is healthy"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def check_prometheus_health(self):
        """Check if Prometheus is healthy"""
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/targets", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def check_grafana_health(self):
        """Check if Grafana is healthy"""
        try:
            response = requests.get(f"{self.grafana_url}/api/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def generate_traffic(self):
        """Generate test traffic to keep metrics flowing"""
        test_data_samples = [
            # Normal operation
            {"volt": 170.0, "rotate": 450.0, "pressure": 100.0, "vibration": 40.0, "age": 10, "failure": "none"},
            # Higher pressure - potential failure
            {"volt": 180.0, "rotate": 460.0, "pressure": 120.0, "vibration": 50.0, "age": 15, "failure": "comp2"},
            # Higher vibration - potential failure
            {"volt": 160.0, "rotate": 440.0, "pressure": 90.0, "vibration": 60.0, "age": 5, "failure": "comp4"},
            # Old machine
            {"volt": 175.0, "rotate": 455.0, "pressure": 105.0, "vibration": 45.0, "age": 20, "failure": "none"},
        ]
        
        success_count = 0
        for _ in range(10):  # Generate 10 requests
            sample = random.choice(test_data_samples)
            
            # Decide whether to send feedback directly or via the /feedback endpoint
            if random.random() > 0.5:
                # Send to /predict with ground truth
                endpoint = "/predict"
                payload = sample
            else:
                # Send to /predict without ground truth, then send to /feedback
                endpoint = "/predict"
                payload = {k: v for k, v in sample.items() if k != "failure"}
                
                # Send feedback separately
                try:
                    requests.post(
                        f"{self.api_url}/feedback",
                        json=sample,
                        headers={"Content-Type": "application/json", "Authorization": "Bearer test_token_for_testing"},
                        timeout=5
                    )
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Failed to send feedback: {e}")

            try:
                response = requests.post(
                    f"{self.api_url}{endpoint}",
                    json=payload,
                    headers={"Content-Type": "application/json", "Authorization": "Bearer test_token_for_testing"},
                    timeout=5
                )
                if response.status_code == 200:
                    success_count += 1
                else:
                    logger.warning(f"Request to {endpoint} failed with status {response.status_code}: {response.text}")
                time.sleep(0.5)
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to send request to {endpoint}: {e}")

        if success_count > 0:
            logger.info(f"Generated {success_count} test requests")
        else:
            logger.warning("Failed to generate test traffic")
    
    def restart_services(self):
        """Restart all services using Docker Compose"""
        logger.info("Restarting all services via Docker Compose...")
        try:
            subprocess.run(['docker', 'compose', 'down'], capture_output=True, text=True, check=False)
            time.sleep(5)
            subprocess.run(['docker', 'compose', 'up', '-d'], capture_output=True, text=True, check=True)
            
            # Wait for services to start
            logger.info("Waiting for services to become healthy...")
            for _ in range(30):
                if self.check_api_health() and self.check_prometheus_health() and self.check_grafana_health():
                    logger.info("All services restarted and healthy.")
                    return True
                time.sleep(2)
            
            logger.error("Services failed to become healthy after restart.")
            return False
            
        except Exception as e:
            logger.error(f"Failed to restart services: {e}")
            return False
    
    def log_status(self):
        """Log the current status of all services"""
        api_status = "UP" if self.check_api_health() else "DOWN"
        prometheus_status = "UP" if self.check_prometheus_health() else "DOWN"
        grafana_status = "UP" if self.check_grafana_health() else "DOWN"
        
        logger.info(f"Status Check - API: {api_status} | Prometheus: {prometheus_status} | Grafana: {grafana_status}")
    
    def run(self):
        """Run the continuous monitoring"""
        logger.info("Starting Continuous ML Monitoring...")
        logger.info(f"Health checks every {self.check_interval} seconds")
        logger.info(f"Traffic generation every {self.traffic_interval} seconds")
        
        last_traffic_time = time.time()
        
        try:
            while True:
                current_time = time.time()
                
                # Log status
                self.log_status()
                
                # Check all services and restart if any are down
                if not all([self.check_api_health(), self.check_prometheus_health(), self.check_grafana_health()]):
                    logger.warning("One or more services are down. Attempting a full restart...")
                    self.restart_services()
                
                # Generate traffic periodically
                if current_time - last_traffic_time >= self.traffic_interval:
                    logger.info("Generating periodic test traffic...")
                    self.generate_traffic()
                    last_traffic_time = current_time
                
                # Wait for next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("\nContinuous monitoring stopped by user")
        except Exception as e:
            logger.error(f"Continuous monitoring failed: {e}")
            return 1
        
        return 0

def main():
    """Main function"""
    monitor = ContinuousMonitor()
    return monitor.run()

if __name__ == "__main__":
    sys.exit(main()) 
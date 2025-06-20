#!/usr/bin/env python3
"""
Background ML Monitoring Script
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('background_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BackgroundMonitor:
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
        test_data = {
            "machineID": 1,
            "volt": 220.5,
            "rotate": 1500,
            "pressure": 95.7,
            "vibration": 0.5,
            "age": 12,
            "model": "model_A"
        }
        
        success_count = 0
        for i in range(5):  # Generate 5 requests
            try:
                response = requests.post(
                    f"{self.api_url}/predict",
                    json=test_data,
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )
                if response.status_code == 200:
                    success_count += 1
                time.sleep(0.5)
            except requests.exceptions.RequestException:
                pass
        
        if success_count > 0:
            logger.info(f"✅ Generated {success_count} test requests")
        else:
            logger.warning("⚠️ Failed to generate test traffic")
    
    def log_status(self):
        """Log the current status of all services"""
        api_status = "✅" if self.check_api_health() else "❌"
        prometheus_status = "✅" if self.check_prometheus_health() else "❌"
        grafana_status = "✅" if self.check_grafana_health() else "❌"
        
        logger.info(f"📊 Status Check - API: {api_status} | Prometheus: {prometheus_status} | Grafana: {grafana_status}")
    
    def run(self):
        """Run the background monitoring"""
        logger.info("🔄 Starting Background ML Monitoring...")
        logger.info(f"📊 Health checks every {self.check_interval} seconds")
        logger.info(f"🚀 Traffic generation every {self.traffic_interval} seconds")
        
        last_traffic_time = time.time()
        
        try:
            while True:
                current_time = time.time()
                
                # Log status
                self.log_status()
                
                # Generate traffic periodically
                if current_time - last_traffic_time >= self.traffic_interval:
                    logger.info("🚀 Generating periodic test traffic...")
                    self.generate_traffic()
                    last_traffic_time = current_time
                
                # Wait for next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Background monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Background monitoring failed: {e}")
            return 1
        
        return 0

def main():
    """Main function"""
    monitor = BackgroundMonitor()
    return monitor.run()

if __name__ == "__main__":
    sys.exit(main()) 
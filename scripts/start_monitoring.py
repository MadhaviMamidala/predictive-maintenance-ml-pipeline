#!/usr/bin/env python3
"""
Automated ML Monitoring Setup Script
====================================
This script automates the entire monitoring setup for the Predictive Maintenance API.
It handles API startup, Docker containers, health checks, and dashboard verification.
"""

import subprocess
import time
import requests
import json
import logging
import sys
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MonitoringAutomation:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.grafana_url = "http://localhost:3000"
        self.prometheus_url = "http://localhost:9090"
        
    def check_docker_running(self):
        """Check if Docker is running"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info("✅ Docker is available")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ Docker is not available. Please start Docker Desktop.")
            return False
    
    def start_api(self):
        """Start the Predictive Maintenance API"""
        logger.info("🚀 Starting Predictive Maintenance API...")
        
        # Check if API is already running
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API is already running")
                return True
        except requests.exceptions.RequestException:
            pass
        
        # Start API in background
        try:
            # Use start_api.py if it exists, otherwise start directly
            if Path("start_api.py").exists():
                subprocess.Popen([sys.executable, "start_api.py"], 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                subprocess.Popen([sys.executable, "-m", "uvicorn", "src.api.main:app", 
                                "--host", "0.0.0.0", "--port", "8000"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for API to start
            for i in range(30):
                try:
                    response = requests.get(f"{self.api_url}/health", timeout=5)
                    if response.status_code == 200:
                        logger.info("✅ API started successfully")
                        return True
                except requests.exceptions.RequestException:
                    pass
                time.sleep(1)
            
            logger.error("❌ API failed to start within 30 seconds")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start API: {e}")
            return False
    
    def start_monitoring_stack(self):
        """Start Prometheus and Grafana using Docker Compose"""
        logger.info("🐳 Starting monitoring stack (Prometheus + Grafana)...")
        
        try:
            # Stop any existing containers
            subprocess.run(['docker', 'compose', 'down'], 
                         capture_output=True, text=True)
            
            # Start monitoring stack
            result = subprocess.run(['docker', 'compose', 'up', '-d', 'prometheus', 'grafana'],
                                  capture_output=True, text=True, check=True)
            
            logger.info("✅ Monitoring stack started")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to start monitoring stack: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
    
    def wait_for_services(self):
        """Wait for all services to be ready"""
        logger.info("⏳ Waiting for services to be ready...")
        
        services = [
            ("API", self.api_url + "/health"),
            ("Prometheus", self.prometheus_url + "/api/v1/targets"),
            ("Grafana", self.grafana_url + "/api/health")
        ]
        
        for service_name, url in services:
            logger.info(f"Waiting for {service_name}...")
            for i in range(60):  # Wait up to 60 seconds per service
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        logger.info(f"✅ {service_name} is ready")
                        break
                except requests.exceptions.RequestException:
                    if i == 59:  # Last attempt
                        logger.error(f"❌ {service_name} failed to start")
                        return False
                    time.sleep(1)
        
        return True
    
    def generate_test_traffic(self):
        """Generate test traffic to populate the dashboard"""
        logger.info("📊 Generating test traffic...")
        
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
        for i in range(20):
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
        
        logger.info(f"✅ Generated {success_count} test requests")
        return success_count > 0
    
    def verify_dashboard(self):
        """Verify that the dashboard is working"""
        logger.info("🔍 Verifying dashboard functionality...")
        
        try:
            # Check if Prometheus has data
            response = requests.get(f"{self.prometheus_url}/api/v1/query?query=http_requests_total")
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('result'):
                    logger.info("✅ Prometheus has collected metrics")
                else:
                    logger.warning("⚠️ Prometheus has no metrics yet")
            
            # Check Grafana dashboards
            response = requests.get(f"{self.grafana_url}/api/search")
            if response.status_code == 200:
                dashboards = response.json()
                if any('ML' in d.get('title', '') for d in dashboards):
                    logger.info("✅ Grafana dashboards are available")
                else:
                    logger.warning("⚠️ No ML dashboards found")
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Dashboard verification failed: {e}")
            return False
    
    def print_access_info(self):
        """Print access information for the user"""
        logger.info("\n" + "="*60)
        logger.info("🎉 MONITORING SYSTEM IS READY!")
        logger.info("="*60)
        logger.info("📊 Access your dashboards:")
        logger.info(f"   Grafana: {self.grafana_url}")
        logger.info("   Login: admin / admin")
        logger.info("   Dashboard: 'ML Predictive Maintenance Dashboard'")
        logger.info("")
        logger.info("📈 API Endpoints:")
        logger.info(f"   API: {self.api_url}")
        logger.info(f"   Health: {self.api_url}/health")
        logger.info(f"   Metrics: {self.api_url}/metrics")
        logger.info("")
        logger.info("🔍 Monitoring Tools:")
        logger.info(f"   Prometheus: {self.prometheus_url}")
        logger.info(f"   Grafana: {self.grafana_url}")
        logger.info("")
        logger.info("📝 Logs:")
        logger.info("   API logs: Check the terminal where you ran this script")
        logger.info("   Monitoring logs: monitoring.log")
        logger.info("="*60)
    
    def run(self):
        """Run the complete automation"""
        logger.info("🤖 Starting ML Monitoring Automation...")
        
        # Check prerequisites
        if not self.check_docker_running():
            return False
        
        # Start services
        if not self.start_api():
            return False
        
        if not self.start_monitoring_stack():
            return False
        
        # Wait for services
        if not self.wait_for_services():
            return False
        
        # Generate test traffic
        self.generate_test_traffic()
        
        # Verify dashboard
        self.verify_dashboard()
        
        # Print access information
        self.print_access_info()
        
        logger.info("✅ Automation completed successfully!")
        return True

def main():
    """Main function"""
    automation = MonitoringAutomation()
    
    try:
        success = automation.run()
        if success:
            logger.info("🎯 Your ML monitoring system is now automated and running!")
            logger.info("💡 To stop: Press Ctrl+C or run 'docker compose down'")
            
            # Keep the script running to maintain the setup
            try:
                while True:
                    time.sleep(60)  # Check every minute
                    # Optional: Add periodic health checks here
            except KeyboardInterrupt:
                logger.info("\n🛑 Shutting down monitoring system...")
                subprocess.run(['docker', 'compose', 'down'], 
                             capture_output=True, text=True)
                logger.info("✅ Monitoring system stopped")
        
    except Exception as e:
        logger.error(f"❌ Automation failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
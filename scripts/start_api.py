#!/usr/bin/env python3
"""
Startup script for the Predictive Maintenance API
"""

import subprocess
import sys
import time
import requests
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required files exist"""
    required_files = [
        "models/random_forest_model.joblib",
        "model_metrics.json",
        "src/api/main.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Missing required files: {missing_files}")
        logger.error("Please run the model training pipeline first.")
        return False
    
    return True

def start_api():
    """Start the FastAPI application"""
    try:
        logger.info("Starting Predictive Maintenance API...")
        
        # Check if port 8000 is available
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                logger.warning("API is already running on port 8000")
                return True
        except requests.exceptions.RequestException:
            pass
        
        # Start the API
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "src.api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        process = subprocess.Popen(cmd)
        
        # Wait for API to start
        logger.info("Waiting for API to start...")
        time.sleep(5)
        
        # Check if API is running
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ API is running successfully!")
                    logger.info("📖 API Documentation: http://localhost:8000/docs")
                    logger.info("🔍 Health Check: http://localhost:8000/health")
                    logger.info("🛑 Press Ctrl+C to stop the API")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
            logger.info(f"Waiting for API... (attempt {i+1}/{max_retries})")
        
        logger.error("❌ API failed to start")
        return False
        
    except KeyboardInterrupt:
        logger.info("🛑 API stopped by user")
        return True
    except Exception as e:
        logger.error(f"❌ Error starting API: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Predictive Maintenance API Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start API
    if start_api():
        logger.info("API startup completed successfully")
    else:
        logger.error("API startup failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 
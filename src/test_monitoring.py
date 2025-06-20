import requests
import time
import random
import json
from datetime import datetime

def generate_test_data():
    """Generate realistic test data for monitoring"""
    base_data = {
        "machineID": 1,
        "volt": 170.0,
        "rotate": 1388.0,
        "pressure": 113.0,
        "vibration": 40.0,
        "age": 15,
        "model": "model1"
    }
    
    # Add some variation
    variations = [
        {"pressure": 150.0, "vibration": 45.0},  # High pressure
        {"vibration": 60.0, "age": 25},           # High vibration
        {"volt": 175.0, "rotate": 1400.0},        # High voltage
        {"age": 50, "pressure": 105.0},           # Old equipment
        {"volt": 165.0, "rotate": 1350.0},        # Low voltage
    ]
    
    return base_data, variations

def test_api_endpoints():
    """Test various API endpoints to generate metrics"""
    base_url = "http://localhost:8000"
    
    print("🚀 Starting API monitoring test...")
    
    # Test health endpoint
    print("📊 Testing health endpoint...")
    for i in range(5):
        response = requests.get(f"{base_url}/health")
        print(f"  Health check {i+1}: {response.status_code}")
        time.sleep(0.5)
    
    # Test model info
    print("📊 Testing model info endpoint...")
    for i in range(3):
        response = requests.get(f"{base_url}/model-info")
        print(f"  Model info {i+1}: {response.status_code}")
        time.sleep(0.5)
    
    # Test predictions
    print("📊 Testing prediction endpoints...")
    base_data, variations = generate_test_data()
    
    # Test normal predictions
    for i in range(10):
        response = requests.post(
            f"{base_url}/predict",
            json=base_data,
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        print(f"  Prediction {i+1}: {result['prediction']} (confidence: {result['confidence']})")
        time.sleep(0.3)
    
    # Test varied predictions
    for i, variation in enumerate(variations):
        test_data = base_data.copy()
        test_data.update(variation)
        test_data["machineID"] = i + 2
        
        response = requests.post(
            f"{base_url}/predict",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        print(f"  Varied prediction {i+1}: {result['prediction']} (confidence: {result['confidence']})")
        time.sleep(0.3)
    
    # Test batch predictions
    print("📊 Testing batch predictions...")
    batch_data = []
    for i in range(5):
        test_data = base_data.copy()
        test_data["machineID"] = i + 10
        test_data["volt"] += random.uniform(-5, 5)
        test_data["pressure"] += random.uniform(-10, 10)
        batch_data.append(test_data)
    
    response = requests.post(
        f"{base_url}/batch-predict",
        json={"data": batch_data},
        headers={"Content-Type": "application/json"}
    )
    print(f"  Batch prediction: {response.status_code}")
    
    print("✅ API monitoring test completed!")

if __name__ == "__main__":
    test_api_endpoints() 
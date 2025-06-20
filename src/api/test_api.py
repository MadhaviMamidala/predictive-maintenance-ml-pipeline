import requests
import json
import time
from typing import Dict, List

# API configuration
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Model loaded: {data['model_loaded']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_single_prediction():
    """Test single prediction endpoint"""
    print("\nTesting single prediction...")
    
    # Sample data
    sample_data = {
        "machineID": 1,
        "volt": 170.0,
        "rotate": 450.0,
        "pressure": 100.0,
        "vibration": 40.0,
        "age": 100,
        "model": "model1",
        "errorID": "none",
        "failure": "none",
        "comp_maint": "none"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json=sample_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Single prediction successful:")
            print(f"   Prediction: {data['prediction']} ({'Maintenance needed' if data['prediction'] == 1 else 'No maintenance'})")
            print(f"   Probability: {data['probability']:.3f}")
            print(f"   Confidence: {data['confidence']}")
            print(f"   Request ID: {data['request_id']}")
            return True
        else:
            print(f"❌ Single prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Single prediction error: {e}")
        return False

def test_batch_prediction():
    """Test batch prediction endpoint"""
    print("\nTesting batch prediction...")
    
    # Sample batch data
    batch_data = {
        "data": [
            {
                "machineID": 1,
                "volt": 170.0,
                "rotate": 450.0,
                "pressure": 100.0,
                "vibration": 40.0,
                "age": 100,
                "model": "model1",
                "errorID": "none",
                "failure": "none",
                "comp_maint": "none"
            },
            {
                "machineID": 2,
                "volt": 180.0,
                "rotate": 500.0,
                "pressure": 110.0,
                "vibration": 50.0,
                "age": 150,
                "model": "model2",
                "errorID": "none",
                "failure": "none",
                "comp_maint": "none"
            },
            {
                "machineID": 3,
                "volt": 160.0,
                "rotate": 400.0,
                "pressure": 90.0,
                "vibration": 30.0,
                "age": 50,
                "model": "model1",
                "errorID": "none",
                "failure": "none",
                "comp_maint": "none"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/batch-predict",
            json=batch_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batch prediction successful:")
            print(f"   Batch ID: {data['batch_id']}")
            print(f"   Number of predictions: {len(data['predictions'])}")
            
            for i, pred in enumerate(data['predictions']):
                print(f"   Prediction {i+1}: {pred['prediction']} (prob: {pred['probability']:.3f}, conf: {pred['confidence']})")
            return True
        else:
            print(f"❌ Batch prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Batch prediction error: {e}")
        return False

def test_model_info():
    """Test model info endpoint"""
    print("\nTesting model info...")
    
    try:
        response = requests.get(f"{BASE_URL}/model-info")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model info retrieved:")
            print(f"   Model type: {data['model_type']}")
            print(f"   Performance metrics: {list(data['performance_metrics'].keys())}")
            print(f"   Feature importance: {list(data['feature_importance'].keys())}")
            return True
        else:
            print(f"❌ Model info failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Model info error: {e}")
        return False

def test_api_documentation():
    """Test API documentation endpoint"""
    print("\nTesting API documentation...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API documentation available at /docs")
            return True
        else:
            print(f"❌ API documentation not available: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API documentation error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Starting API Tests...")
    print("=" * 50)
    
    # Wait a moment for API to be ready
    time.sleep(2)
    
    tests = [
        test_health_check,
        test_single_prediction,
        test_batch_prediction,
        test_model_info,
        test_api_documentation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API logs for details.")

if __name__ == "__main__":
    main() 
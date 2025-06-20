import requests
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_file():
    """Test if model file exists and can be loaded"""
    try:
        model_path = Path('models/best_model.pkl')
        if not model_path.exists():
            logger.error("❌ Model file not found!")
            return False
            
        model = joblib.load(model_path)
        logger.info("✅ Model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error loading model: {str(e)}")
        return False

def test_model_predictions():
    """Test model predictions with sample data"""
    try:
        # Load model
        model = joblib.load('models/best_model.pkl')
        
        # Create sample data
        sample_data = pd.DataFrame({
            'volt': [220.5, 210.0, 225.0],
            'rotate': [1200, 1180, 1250],
            'pressure': [95.0, 85.0, 100.0],
            'vibration': [0.5, 1.5, 0.2],
            'age': [12, 24, 6]
        })
        
        # Make predictions
        predictions = model.predict(sample_data)
        probabilities = model.predict_proba(sample_data)
        
        logger.info("\nSample Predictions:")
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            status = "Failure" if pred == 1 else "Normal"
            failure_prob = prob[1]
            logger.info(f"Machine {i+1}: {status} (Failure Probability: {failure_prob:.2%})")
            
        logger.info("✅ Model predictions working")
        return True
    except Exception as e:
        logger.error(f"❌ Error testing predictions: {str(e)}")
        return False

def test_api_health():
    """Test if API is running and healthy"""
    try:
        response = requests.get('http://localhost:8000/health')
        if response.status_code == 200:
            logger.info("✅ API health check passed")
            return True
        else:
            logger.error(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Error checking API health: {str(e)}")
        return False

def test_api_prediction():
    """Test API prediction endpoint"""
    try:
        # Sample data for prediction
        test_data = {
            "machineID": 1,
            "volt": 220.5,
            "rotate": 1200,
            "pressure": 95.0,
            "vibration": 0.5,
            "age": 12,
            "model": "model_A"
        }
        
        # Make prediction request
        response = requests.post(
            'http://localhost:8000/predict',
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("\nAPI Prediction Test:")
            logger.info(f"Input: {json.dumps(test_data, indent=2)}")
            logger.info(f"Response: {json.dumps(result, indent=2)}")
            logger.info("✅ API prediction endpoint working")
            return True
        else:
            logger.error(f"❌ API prediction failed: {response.status_code}")
            logger.error(f"Error message: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing API prediction: {str(e)}")
        return False

def run_all_tests():
    """Run all system tests"""
    logger.info("Starting system verification...")
    
    tests = [
        ("Model File Check", test_model_file),
        ("Model Predictions", test_model_predictions),
        ("API Health Check", test_api_health),
        ("API Prediction Test", test_api_prediction)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n=== {test_name} ===")
        result = test_func()
        results.append(result)
    
    # Summary
    logger.info("\n=== Test Summary ===")
    all_passed = all(results)
    for (test_name, _), result in zip(tests, results):
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    if all_passed:
        logger.info("\n✅ All tests passed! System is working correctly!")
    else:
        logger.error("\n❌ Some tests failed. Please check the logs above.")

if __name__ == '__main__':
    run_all_tests() 
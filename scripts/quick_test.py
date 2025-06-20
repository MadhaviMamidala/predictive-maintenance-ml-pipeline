import requests
import json
import time
import random

# Test data for predictions - using correct field names
test_data = [
    {"volt": 220, "rotate": 1800, "pressure": 120, "vibration": 30, "age": 5},
    {"volt": 225, "rotate": 1850, "pressure": 125, "vibration": 35, "age": 6},
    {"volt": 218, "rotate": 1820, "pressure": 118, "vibration": 32, "age": 4},
    {"volt": 230, "rotate": 1900, "pressure": 130, "vibration": 40, "age": 7},
    {"volt": 222, "rotate": 1810, "pressure": 122, "vibration": 31, "age": 5}
]

# API endpoint
url = "http://localhost:8000/predict"
headers = {"Authorization": "Bearer test_token_for_testing"}

print("Generating test predictions...")

for i, data in enumerate(test_data):
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"Prediction {i+1}: {result}")
        else:
            print(f"Error {i+1}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Request {i+1} failed: {e}")
    
    time.sleep(0.5)  # Small delay between requests

print("Test data generation complete!") 
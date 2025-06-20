import requests
import json
import time
import random

# API endpoint
API_URL = "http://localhost:8000"
PREDICT_URL = f"{API_URL}/predict"
headers = {"Authorization": "Bearer test_token_for_testing"}

def generate_prediction_with_feedback():
    """Generates a single prediction and sends feedback to calculate accuracy."""
    # Realistic test data
    data = {
        "volt": random.uniform(210, 240),
        "rotate": random.uniform(1700, 2200),
        "pressure": random.uniform(110, 140),
        "vibration": random.uniform(25, 45),
        "age": random.randint(3, 10)
    }

    # Simulate ground truth - let's assume 'none' is the most common outcome
    ground_truth = "none" if random.random() < 0.9 else "failure_type_1"
    data["failure"] = ground_truth

    try:
        response = requests.post(PREDICT_URL, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            prediction = result.get('prediction')
            print(f"Prediction: {prediction}, Ground Truth: {ground_truth} -> {'Correct' if prediction == ground_truth else 'Incorrect'}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("Starting advanced test data generation with feedback...")
    print("Running for 30 seconds to generate metrics. Check your Grafana dashboard.")
    
    start_time = time.time()
    while time.time() - start_time < 30:
        generate_prediction_with_feedback()
        time.sleep(2)  # 2-second delay between requests

    print("\nAdvanced test data generation complete!")
    print("Check the 'Model Accuracy' panel in Grafana.") 
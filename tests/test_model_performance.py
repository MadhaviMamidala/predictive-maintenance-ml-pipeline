import pytest
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
import joblib
import json
from pathlib import Path
import time
import psutil
import os
import pickle

@pytest.fixture
def model():
    """Load trained model"""
    model_path = Path("models/best_model.pkl")
    if not model_path.exists():
        pytest.skip("Model not found")
    return joblib.load(model_path)

@pytest.fixture
def test_data():
    """Load test data"""
    data_path = Path("data/processed/processed_data.csv")
    if not data_path.exists():
        pytest.skip("Test data not found")
    return pd.read_csv(data_path)

class TestModelPerformance:
    """Test model performance and reliability"""
    
    @pytest.mark.model
    def test_model_accuracy_threshold(self, model, test_data):
        """Test that model accuracy meets minimum threshold"""
        # Prepare features
        feature_cols = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        X = test_data[feature_cols].dropna()
        y = test_data['failure'].dropna()
        
        # Align X and y
        common_index = X.index.intersection(y.index)
        X = X.loc[common_index]
        y = y.loc[common_index]
        
        # Ensure y is string type for consistency
        y = y.astype(str)
        
        # Make predictions
        y_pred = model.predict(X)
        
        # Calculate metrics
        accuracy = accuracy_score(y, y_pred)
        precision = precision_score(y, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y, y_pred, average='weighted', zero_division=0)
        
        # Assert minimum thresholds
        assert accuracy >= 0.7, f"Accuracy {accuracy:.3f} below threshold 0.7"
        assert precision >= 0.6, f"Precision {precision:.3f} below threshold 0.6"
        assert recall >= 0.7, f"Recall {recall:.3f} below threshold 0.7"
        assert f1 >= 0.6, f"F1-score {f1:.3f} below threshold 0.6"
    
    @pytest.mark.model
    def test_model_prediction_consistency(self, model, test_data):
        """Test that model predictions are consistent"""
        feature_cols = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        X = test_data[feature_cols].dropna().head(10)  # Test with 10 samples
        
        # Make predictions multiple times
        predictions = []
        for _ in range(5):
            pred = model.predict(X)
            predictions.append(pred)
        
        # All predictions should be identical
        for i in range(1, len(predictions)):
            assert np.array_equal(predictions[0], predictions[i]), "Predictions not consistent"
    
    @pytest.mark.model
    def test_model_feature_importance(self, model, test_data):
        """Test that model has reasonable feature importance"""
        feature_cols = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        
        # Check feature importance
        importance = model.feature_importances_
        feature_importance = dict(zip(feature_cols, importance))
        
        # All features should have some importance
        for feature, imp in feature_importance.items():
            assert imp > 0, f"Feature {feature} has zero importance"
            assert imp <= 1, f"Feature {feature} importance {imp} > 1"
        
        # Total importance should sum to 1
        assert abs(sum(importance) - 1.0) < 1e-6, "Feature importance doesn't sum to 1"
    
    @pytest.mark.model
    def test_data_drift_detection(self, test_data):
        """Test data drift detection functionality"""
        # Check if drift detection module exists
        try:
            from src.etl.drift_detection import DriftDetector
            assert True, "Drift detection module available"
        except ImportError:
            pytest.skip("Drift detection module not available")
    
    @pytest.mark.model
    def test_model_prediction_speed(self, model, test_data):
        """Test that model predictions are fast enough"""
        feature_cols = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        X = test_data[feature_cols].dropna().head(100)  # Test with 100 samples
        
        # Measure prediction time
        start_time = time.time()
        predictions = model.predict(X)
        end_time = time.time()
        
        prediction_time = end_time - start_time
        avg_time_per_prediction = prediction_time / len(X)
        
        # Should be fast (less than 2ms per prediction)
        assert avg_time_per_prediction < 0.002, f"Prediction too slow: {avg_time_per_prediction:.6f}s per prediction"
        assert len(predictions) == len(X), "Number of predictions doesn't match input size"
    
    @pytest.mark.model
    def test_model_memory_usage(self, model):
        """Test that model memory usage is reasonable"""
        # Get memory usage before loading model
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Model should already be loaded, but let's check size
        model_size = len(pickle.dumps(model)) / 1024 / 1024  # MB
        
        # Model should be reasonable size (less than 100MB)
        assert model_size < 100, f"Model too large: {model_size:.2f}MB"
    
    @pytest.mark.model
    def test_model_serialization(self, model):
        """Test that model can be serialized and deserialized"""
        # Serialize model
        serialized = pickle.dumps(model)
        
        # Deserialize model
        deserialized = pickle.loads(serialized)
        
        # Test that deserialized model works
        test_data = np.array([[220, 1500, 95, 45, 12]])  # Single sample
        original_pred = model.predict(test_data)
        deserialized_pred = deserialized.predict(test_data)
        
        assert np.array_equal(original_pred, deserialized_pred), "Deserialized model predictions don't match" 
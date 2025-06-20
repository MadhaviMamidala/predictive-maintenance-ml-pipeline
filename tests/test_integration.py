import pytest
import requests
import pandas as pd
import numpy as np
from pathlib import Path
import time
import subprocess
import sys
import json

class TestIntegration:
    """Integration tests for the complete MLOps pipeline"""
    
    def get_auth_headers(self):
        """Get authentication headers for testing"""
        return {"Authorization": "Bearer test_token_for_testing"}
    
    @pytest.fixture
    def api_url(self):
        """API base URL"""
        return "http://localhost:8000"
    
    @pytest.mark.integration
    def test_complete_pipeline_flow(self):
        """Test the complete pipeline from data to prediction"""
        # 1. Check data exists
        data_path = Path("data/processed/processed_data.csv")
        assert data_path.exists(), "Processed data not found"
        
        # 2. Check model exists
        model_path = Path("models/best_model.pkl")
        assert model_path.exists(), "Trained model not found"
        
        # 3. Check API is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            assert response.status_code == 200, "API not responding"
        except requests.exceptions.RequestException:
            pytest.skip("API not running")
        
        # 4. Test prediction endpoint with authentication
        test_data = {
            "volt": 220,
            "rotate": 1500,
            "pressure": 95,
            "vibration": 45.0,  # Updated to match actual data range
            "age": 12
        }
        
        response = requests.post("http://localhost:8000/predict", 
                               json=test_data, 
                               headers=self.get_auth_headers())
        assert response.status_code == 200, "Prediction failed"
        
        # Check response format
        result = response.json()
        assert "prediction" in result, "Prediction result missing"
        assert "probability" in result, "Probability missing"
        assert "timestamp" in result, "Timestamp missing"
    
    @pytest.mark.integration
    def test_monitoring_integration(self):
        """Test monitoring system integration"""
        try:
            # Test metrics endpoint
            response = requests.get("http://localhost:8000/metrics", timeout=5)
            assert response.status_code == 200, "Metrics endpoint not responding"
            
            # Check for key metrics
            metrics_text = response.text
            assert "http_requests_total" in metrics_text, "Request metrics missing"
            assert "http_request_duration_seconds" in metrics_text, "Duration metrics missing"
            
        except requests.exceptions.RequestException:
            pytest.skip("API not running")
    
    @pytest.mark.integration
    def test_data_quality_pipeline(self):
        """Test data quality checks"""
        # Load processed data
        data_path = Path("data/processed/processed_data.csv")
        if not data_path.exists():
            pytest.skip("Processed data not found")
        
        df = pd.read_csv(data_path)
        
        # Check data quality
        assert not df.empty, "Data is empty"
        assert len(df.columns) >= 5, "Insufficient columns"
        
        # Check for required columns
        required_cols = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        for col in required_cols:
            assert col in df.columns, f"Required column {col} missing"
        
        # Check for reasonable data ranges (updated to match actual data)
        assert df['volt'].between(100, 300).all(), "Voltage values out of range"
        assert df['rotate'].between(500, 3000).all(), "Rotation values out of range"
        assert df['pressure'].between(50, 150).all(), "Pressure values out of range"
        assert df['vibration'].between(0, 100).all(), "Vibration values out of range"  # Updated range
        assert df['age'].between(0, 50).all(), "Age values out of range"
    
    @pytest.mark.integration
    def test_model_performance_monitoring(self):
        """Test model performance monitoring"""
        # Load model metrics
        metrics_path = Path("models/metrics.json")
        if not metrics_path.exists():
            pytest.skip("Model metrics not found")
        
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        # Check required metrics
        required_metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        for metric in required_metrics:
            assert metric in metrics, f"Required metric {metric} missing"
            assert isinstance(metrics[metric], (int, float)), f"Metric {metric} should be numeric"
            assert 0 <= metrics[metric] <= 1, f"Metric {metric} should be between 0 and 1"
        
        # Check feature importance
        assert 'feature_importance' in metrics, "Feature importance missing"
        assert len(metrics['feature_importance']) > 0, "Feature importance empty"
    
    @pytest.mark.integration
    def test_automation_scripts(self):
        """Test automation scripts exist and are executable"""
        # Check for key automation scripts
        scripts = [
            "scripts/run_tests.py",
            "scripts/generate_performance_report.py",
            "scripts/check_model_drift.py"
        ]
        
        for script in scripts:
            script_path = Path(script)
            assert script_path.exists(), f"Script {script} not found"
    
    @pytest.mark.integration
    def test_docker_integration(self):
        """Test Docker configuration"""
        # Check for Docker files
        docker_files = [
            "docker/Dockerfile.api",
            "docker-compose.production.yml"
        ]
        
        for docker_file in docker_files:
            docker_path = Path(docker_file)
            assert docker_path.exists(), f"Docker file {docker_file} not found"
    
    @pytest.mark.integration
    def test_documentation_completeness(self):
        """Test documentation completeness"""
        # Check for key documentation
        docs = [
            "docs/MASTER_PROJECT_HISTORY_AND_GUIDE.md"
        ]
        
        for doc in docs:
            doc_path = Path(doc)
            assert doc_path.exists(), f"Documentation {doc} not found"
    
    @pytest.mark.integration
    def test_error_handling(self):
        """Test error handling across the pipeline"""
        # Test API error handling
        try:
            # Test with invalid data
            response = requests.post("http://localhost:8000/predict",
                                   json={"invalid": "data"}, 
                                   headers=self.get_auth_headers(),
                                   timeout=5)
            assert response.status_code in [400, 422], "Should handle invalid data gracefully"
            
            # Test with missing authentication
            response = requests.post("http://localhost:8000/predict",
                                   json={"volt": 220, "rotate": 1500, "pressure": 95, "vibration": 45, "age": 12},
                                   timeout=5)
            assert response.status_code == 403, "Should require authentication"
            
        except requests.exceptions.RequestException:
            pytest.skip("API not running")
    
    @pytest.mark.integration
    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        # Test API response time
        try:
            start_time = time.time()
            response = requests.get("http://localhost:8000/health", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 5.0, f"API response too slow: {response_time:.3f}s"  # Increased timeout
            assert response.status_code == 200, "Health check failed"
            
        except requests.exceptions.RequestException:
            pytest.skip("API not running") 
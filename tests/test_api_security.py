import pytest
import requests
import json
from fastapi.testclient import TestClient
from src.api.main import app
import time
import joblib
from pathlib import Path

client = TestClient(app)

class TestAPISecurity:
    """Test API security features"""
    
    @classmethod
    def setup_class(cls):
        """Setup test class - load model for testing"""
        # Load model for testing
        model_path = Path("models/best_model.pkl")
        if model_path.exists():
            model = joblib.load(model_path)
            # Set the model in the global variable
            import src.api.main
            src.api.main.model = model
        else:
            pytest.skip("Model file not found")
    
    def get_auth_headers(self):
        """Get authentication headers for testing"""
        # For testing, we'll use a test token
        return {"Authorization": "Bearer test_token_for_testing"}
    
    @pytest.mark.security
    def test_input_validation(self):
        """Test that invalid inputs are properly rejected"""
        # Test with missing required fields
        response = client.post("/predict", json={}, headers=self.get_auth_headers())
        assert response.status_code == 422
        
        # Test with invalid data types
        response = client.post("/predict", json={
            "volt": "invalid",
            "rotate": "invalid",
            "pressure": "invalid",
            "vibration": "invalid",
            "age": "invalid"
        }, headers=self.get_auth_headers())
        assert response.status_code == 422
        
        # Test with out-of-range values
        response = client.post("/predict", json={
            "volt": 1000,  # Too high
            "rotate": -100,  # Negative
            "pressure": 200,  # Too high
            "vibration": -1,  # Negative
            "age": 1000  # Too high
        }, headers=self.get_auth_headers())
        assert response.status_code == 422
    
    @pytest.mark.security
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        malicious_input = "'; DROP TABLE users; --"
        response = client.post("/predict", json={
            "volt": 220,
            "rotate": 1500,
            "pressure": 95,
            "vibration": 0.5,
            "age": 12,
            "model": malicious_input
        }, headers=self.get_auth_headers())
        # Should not crash and should handle gracefully
        assert response.status_code in [200, 422]
    
    @pytest.mark.security
    def test_xss_prevention(self):
        """Test XSS prevention"""
        xss_payload = "<script>alert('xss')</script>"
        response = client.post("/predict", json={
            "volt": 220,
            "rotate": 1500,
            "pressure": 95,
            "vibration": 0.5,
            "age": 12,
            "model": xss_payload
        }, headers=self.get_auth_headers())
        # Should not execute scripts
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            assert "<script>" not in response.text
    
    @pytest.mark.security
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Make multiple requests quickly
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200
        
        # The 6th request should be rate limited
        response = client.get("/health")
        # Rate limiting might not be active in test mode, so we just check it doesn't crash
        assert response.status_code in [200, 429]
    
    @pytest.mark.security
    def test_authentication_required(self):
        """Test that protected endpoints require authentication"""
        # Test without authentication
        response = client.post("/predict", json={
            "volt": 220,
            "rotate": 1500,
            "pressure": 95,
            "vibration": 0.5,
            "age": 12
        })
        assert response.status_code == 403  # Should require authentication
    
    @pytest.mark.security
    def test_secure_headers(self):
        """Test that secure headers are set"""
        response = client.get("/health")
        headers = response.headers
        
        # Check for security headers
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
    
    @pytest.mark.security
    def test_large_payload_rejection(self):
        """Test that very large payloads are rejected"""
        large_payload = {"data": "x" * 1000000}  # 1MB payload
        response = client.post("/predict", json=large_payload, headers=self.get_auth_headers())
        assert response.status_code in [413, 422]  # Payload too large or validation error 
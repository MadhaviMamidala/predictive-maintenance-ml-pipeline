"""
Enhanced FastAPI application with security features
"""

import os
import logging
import joblib
import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import time

from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer
import uvicorn

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import psutil

# Import security modules
from .security import (
    PredictionRequest, BatchPredictionInput, FeedbackRequest, validate_rate_limit,
    get_current_user, security_middleware, sanitize_input,
    Authentication, RateLimiter, SecurityHeaders
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CoreDefender Predictive Maintenance API",
    description="MLOps API for predictive maintenance with security features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
app.middleware("http")(security_middleware)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
PREDICTION_COUNT = Counter('predictions_total', 'Total predictions made')
PREDICTION_LATENCY = Histogram('prediction_duration_seconds', 'Prediction latency')
PREDICTION_ERRORS = Counter('prediction_errors_total', 'Total prediction errors')
MODEL_ACCURACY = Gauge('model_accuracy', 'Current model accuracy')
FEEDBACK_COUNT = Counter('feedback_total', 'Total feedback received')

# Global variables
model = None
model_metadata = {}
startup_time = None
prediction_history = [] # For accuracy calculation
MAX_HISTORY_LENGTH = 1000 # Max predictions to store for accuracy calculation

# Security
security = HTTPBearer(auto_error=False)

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    global model, model_metadata, startup_time
    
    logger.info("Starting CoreDefender Predictive Maintenance API...")
    startup_time = datetime.now()
    
    # Load model
    model_path = Path("models/best_model.pkl")
    if not model_path.exists():
        logger.error("Model file not found. Please run the training pipeline first.")
        raise RuntimeError("Model file not found")
    
    try:
        model = joblib.load(model_path)
        logger.info("Model loaded successfully")
        
        # Load model metadata
        metadata_path = Path("models/metrics.json")
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                model_metadata = json.load(f)
        
        # Load feature names
        feature_names_path = Path("models/feature_names.json")
        if feature_names_path.exists():
            with open(feature_names_path, 'r') as f:
                feature_names = json.load(f)
                model_metadata['feature_names'] = feature_names
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise RuntimeError(f"Model loading failed: {str(e)}")
    
    logger.info("API startup completed successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down CoreDefender Predictive Maintenance API...")

# Dependency for rate limiting
async def check_rate_limit(request: Request):
    """Check rate limit for all requests"""
    validate_rate_limit(request)

# Health check endpoint
@app.get("/health", dependencies=[Depends(check_rate_limit)])
async def health_check():
    """Health check endpoint"""
    global model, startup_time
    
    uptime = datetime.now() - startup_time if startup_time else None
    
    health_status = {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_performance": model_metadata.get('metrics', {}),
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": uptime.total_seconds() if uptime else None,
        "version": "2.0.0"
    }
    
    # Add system metrics
    health_status.update({
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    })
    
    return health_status

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Prediction endpoint with security
@app.post("/predict", dependencies=[Depends(check_rate_limit)])
async def predict(
    input_data: PredictionRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Make a single prediction with security validation"""
    global model
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    start_time = time.time()
    
    try:
        # Sanitize input
        sanitized_data = {
            'volt': input_data.volt,
            'rotate': input_data.rotate,
            'pressure': input_data.pressure,
            'vibration': input_data.vibration,
            'age': input_data.age
        }
        
        # Prepare features
        features = np.array([[
            sanitized_data['volt'],
            sanitized_data['rotate'],
            sanitized_data['pressure'],
            sanitized_data['vibration'],
            sanitized_data['age']
        ]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0].max()

        # If ground truth is provided, calculate accuracy
        if input_data.failure:
            handle_feedback(prediction, input_data.failure)
        
        # Record metrics
        prediction_time = time.time() - start_time
        PREDICTION_COUNT.inc()
        PREDICTION_LATENCY.observe(prediction_time)
        
        # Background task for logging
        background_tasks.add_task(log_prediction, input_data, prediction, probability, current_user)
        
        return {
            "prediction": str(prediction),
            "probability": float(probability),
            "model_version": model_metadata.get('version', 'unknown'),
            "timestamp": datetime.now().isoformat(),
            "processing_time_ms": round(prediction_time * 1000, 2)
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        PREDICTION_ERRORS.inc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Feedback endpoint
@app.post("/feedback", dependencies=[Depends(check_rate_limit)])
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """Submit feedback (ground truth) for a previous prediction"""
    global model
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare features from feedback data
        features = np.array([[
            feedback.volt,
            feedback.rotate,
            feedback.pressure,
            feedback.vibration,
            feedback.age
        ]])
        
        # Make a prediction to compare with ground truth
        prediction = model.predict(features)[0]
        
        # Handle the feedback
        handle_feedback(prediction, feedback.failure)
        
        return {
            "status": "Feedback received",
            "prediction": str(prediction),
            "ground_truth": feedback.failure,
            "current_accuracy": MODEL_ACCURACY._value.get()
        }
        
    except Exception as e:
        logger.error(f"Feedback processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process feedback")

# Batch prediction endpoint
@app.post("/batch-predict", dependencies=[Depends(check_rate_limit)])
async def batch_predict(
    input_data: BatchPredictionInput,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Make batch predictions with security validation"""
    global model
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(input_data.data) > 1000:
        raise HTTPException(status_code=400, detail="Batch size cannot exceed 1000")
    
    start_time = time.time()
    
    try:
        # Prepare features
        features_list = []
        for item in input_data.data:
            features = [
                item.get('volt', 0),
                item.get('rotate', 0),
                item.get('pressure', 0),
                item.get('vibration', 0),
                item.get('age', 0)
            ]
            features_list.append(features)
        
        features_array = np.array(features_list)
        
        # Make predictions
        predictions = model.predict(features_array)
        probabilities = model.predict_proba(features_array).max(axis=1)
        
        # Record metrics
        prediction_time = time.time() - start_time
        PREDICTION_COUNT.inc(len(features_list))
        PREDICTION_LATENCY.observe(prediction_time)
        
        return {
            "predictions": predictions.tolist(),
            "probabilities": probabilities.tolist(),
            "model_version": model_metadata.get('version', 'unknown'),
            "timestamp": datetime.now().isoformat(),
            "processing_time_ms": round(prediction_time * 1000, 2)
        }
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        PREDICTION_ERRORS.inc()
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

# Model info endpoint
@app.get("/model-info", dependencies=[Depends(check_rate_limit)])
async def model_info(current_user: dict = Depends(get_current_user)):
    """Get model information"""
    return {
        "model_type": type(model).__name__ if model else None,
        "feature_names": model_metadata.get('feature_names', []),
        "performance_metrics": model_metadata.get('metrics', {}),
        "training_date": model_metadata.get('training_date'),
        "version": model_metadata.get('version', 'unknown'),
        "last_updated": datetime.now().isoformat()
    }

# Authentication endpoints
@app.post("/auth/login")
async def login(username: str, password: str):
    """Login endpoint (simplified for demo)"""
    # In production, validate against database
    if username == "admin" and password == "admin123":
        token = Authentication.create_access_token({"sub": username})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh access token"""
    token = Authentication.create_access_token({"sub": current_user["sub"]})
    return {"access_token": token, "token_type": "bearer"}

# Background tasks
async def log_prediction(input_data: PredictionRequest, prediction: str, probability: float, user: dict):
    """Log prediction for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user.get("sub", "unknown"),
        "input": input_data.dict(),
        "prediction": prediction,
        "probability": probability
    }
    logger.info(f"Prediction logged: {log_entry}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=exc.status_code).inc()
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=500).inc()
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and record metrics"""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
    REQUEST_LATENCY.observe(duration)
    
    # Log request
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    
    return response

def handle_feedback(prediction: str, ground_truth: str):
    """Helper function to process feedback and update accuracy"""
    global prediction_history
    
    is_correct = (str(prediction).lower() == str(ground_truth).lower())
    
    # Store result for accuracy calculation
    prediction_history.append(is_correct)
    if len(prediction_history) > MAX_HISTORY_LENGTH:
        prediction_history.pop(0)
    
    # Calculate and update accuracy
    if prediction_history:
        accuracy = sum(prediction_history) / len(prediction_history)
        MODEL_ACCURACY.set(accuracy)
    
    FEEDBACK_COUNT.inc()
    logger.info(f"Feedback received. Prediction: {prediction}, Ground Truth: {ground_truth}. Correct: {is_correct}. New accuracy: {MODEL_ACCURACY._value.get()}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 
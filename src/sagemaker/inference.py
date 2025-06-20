import os
import json
import joblib
import numpy as np
from io import StringIO
import pandas as pd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictiveMaintenancePredictor:
    """SageMaker inference class for predictive maintenance"""
    
    def __init__(self):
        """Initialize the model"""
        self.model = None
        self.feature_columns = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        self._load_model()
    
    def _load_model(self):
        """Load the trained model"""
        try:
            # SageMaker model directory
            model_path = os.path.join(os.environ.get('SM_MODEL_DIR', '/opt/ml/model'), 'model.joblib')
            logger.info(f"Loading model from: {model_path}")
            
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                logger.info("Model loaded successfully")
            else:
                logger.error(f"Model file not found at: {model_path}")
                raise FileNotFoundError(f"Model file not found at: {model_path}")
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def predict(self, input_data):
        """Make predictions on input data"""
        try:
            # Convert input to DataFrame if it's not already
            if isinstance(input_data, dict):
                df = pd.DataFrame([input_data])
            elif isinstance(input_data, list):
                df = pd.DataFrame(input_data)
            else:
                df = input_data
            
            # Extract features
            features = df[self.feature_columns].values
            
            # Make predictions
            predictions = self.model.predict(features)
            probabilities = self.model.predict_proba(features)
            
            # Format results
            results = []
            for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
                result = {
                    'prediction': int(pred),
                    'probability_maintenance': float(prob[1]),
                    'probability_no_maintenance': float(prob[0]),
                    'confidence': self._get_confidence_level(prob[1])
                }
                results.append(result)
            
            return results if len(results) > 1 else results[0]
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
    
    def _get_confidence_level(self, probability):
        """Convert probability to confidence level"""
        if probability >= 0.8:
            return "High"
        elif probability >= 0.6:
            return "Medium"
        else:
            return "Low"

# Global predictor instance
_predictor = None

def model_fn(model_dir):
    """Load the model from disk"""
    try:
        logger.info(f"Loading model from {model_dir}")
        model_path = os.path.join(model_dir, 'model.joblib')
        model = joblib.load(model_path)
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

def input_fn(request_body, request_content_type):
    """Parse input data payload"""
    try:
        if request_content_type == 'application/json':
            data = json.loads(request_body)
            features = ['volt', 'rotate', 'pressure', 'vibration', 'age']
            df = pd.DataFrame([data], columns=features)
            logger.info(f"Input data processed: {df.shape}")
            return df
        else:
            raise ValueError(f"Unsupported content type: {request_content_type}")
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        raise

def predict_fn(input_data, model):
    """Make prediction with the model"""
    try:
        logger.info("Making prediction...")
        prediction = model.predict(input_data)
        prediction_proba = model.predict_proba(input_data)
        
        result = {
            'prediction': prediction.tolist(),
            'probability': prediction_proba.tolist(),
            'prediction_label': ['no_failure' if p == 0 else 'failure' for p in prediction]
        }
        
        logger.info(f"Prediction completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise

def output_fn(prediction, accept):
    """Format prediction output"""
    try:
        if accept == 'application/json':
            return json.dumps(prediction), 'application/json'
        raise ValueError(f"Unsupported accept type: {accept}")
    except Exception as e:
        logger.error(f"Error formatting output: {e}")
        raise 
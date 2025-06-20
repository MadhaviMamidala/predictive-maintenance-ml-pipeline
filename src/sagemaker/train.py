import argparse
import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data():
    """Load training data from SageMaker input"""
    try:
        # Parse input data config
        parser = argparse.ArgumentParser()
        parser.add_argument('--training', type=str, default=os.environ.get('SM_CHANNEL_TRAINING'))
        args = parser.parse_args()

        # Read training data
        logger.info("Reading training data...")
        df = pd.read_csv(os.path.join(args.training, 'processed_data.csv'))
        
        # Prepare features and target
        features = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        X = df[features]
        
        # Convert failure to binary (1 if any failure, 0 if none)
        y = (df['failure'] != 'none').astype(int)
        
        logger.info(f"Data loaded: {X.shape[0]} samples, {X.shape[1]} features")
        logger.info(f"Target distribution: {y.value_counts().to_dict()}")
        return X, y
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def train_model(X, y):
    """Train the Random Forest model"""
    try:
        logger.info("Training Random Forest model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Initialize and train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = {
            'accuracy': model.score(X_test, y_test),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'feature_importance': dict(zip(X.columns, model.feature_importances_))
        }
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        metrics['cv_accuracy_mean'] = cv_scores.mean()
        metrics['cv_accuracy_std'] = cv_scores.std()
        
        logger.info(f"Model training completed. Test accuracy: {metrics['accuracy']:.3f}")
        
        return model, metrics
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise

def save_model(model, metrics):
    """Save the trained model and metrics"""
    try:
        # Parse input data config
        parser = argparse.ArgumentParser()
        parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR', 'models'))
        args = parser.parse_args()

        # Save model
        model_path = os.path.join(args.model_dir, 'model.joblib')
        joblib.dump(model, model_path)
        logger.info(f"Model saved to: {model_path}")
        
        # Save metrics
        metrics_path = os.path.join(args.model_dir, 'metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Metrics saved to: {metrics_path}")
        
        # Save feature names
        feature_names_path = os.path.join(args.model_dir, 'feature_names.json')
        with open(feature_names_path, 'w') as f:
            json.dump(['volt', 'rotate', 'pressure', 'vibration', 'age'], f)
        logger.info(f"Feature names saved to: {feature_names_path}")
        
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        raise

def main():
    """Main training function"""
    try:
        logger.info("Starting SageMaker training job...")
        
        # Load data
        X, y = load_data()
        
        # Train model
        model, metrics = train_model(X, y)
        
        # Save model and metrics
        save_model(model, metrics)
        
        logger.info("Training job completed successfully!")
        
    except Exception as e:
        logger.error(f"Training job failed: {e}")
        raise

if __name__ == "__main__":
    main() 
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
import joblib
import json
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_and_prepare_data():
    """Load and prepare data for training"""
    logger.info("Loading data...")
    
    # Load processed data
    data_path = Path("data/processed/processed_data.csv")
    if not data_path.exists():
        raise FileNotFoundError(f"Processed data not found at {data_path}")
    
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")
    
    # Prepare features and target
    feature_cols = ['volt', 'rotate', 'pressure', 'vibration', 'age']
    X = df[feature_cols].dropna()
    y = df['failure'].dropna()
    
    # Align X and y
    common_index = X.index.intersection(y.index)
    X = X.loc[common_index]
    y = y.loc[common_index]
    
    logger.info(f"Final dataset: {len(X)} samples")
    
    # Encode target variable
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    return X, y_encoded, le

def train_model(X, y, le):
    """Train Random Forest model with hyperparameter tuning"""
    logger.info("Training Random Forest model with GridSearchCV...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Hyperparameter grid for GridSearchCV
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2],
        'bootstrap': [True, False]
    }
    
    # Initialize model
    rf = RandomForestClassifier(random_state=42, n_jobs=-1)
    
    # Initialize GridSearchCV
    grid_search = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=3,  # 3-fold cross-validation for speed
        scoring='accuracy',
        verbose=2,
        n_jobs=-1  # Use all available cores
    )
    
    # Train model
    grid_search.fit(X_train, y_train)
    
    # Best model from grid search
    model = grid_search.best_estimator_
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Decode labels for metrics
    y_test_decoded = le.inverse_transform(y_test)
    y_pred_decoded = le.inverse_transform(y_pred)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    # Feature importance
    feature_importance = dict(zip(X.columns, model.feature_importances_))
    
    # Create metrics dictionary
    metrics = {
        'best_params': grid_search.best_params_,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'feature_importance': feature_importance,
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'total_features': len(X.columns)
    }
    
    logger.info(f"Best parameters found: {grid_search.best_params_}")
    logger.info(f"Model trained successfully!")
    logger.info(f"Accuracy: {accuracy:.3f}")
    
    return model, metrics, X_test, y_test

def save_model_and_metrics(model, metrics, le, output_dir="models"):
    """Save model, metrics, and label encoder"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save model
    model_path = output_path / "best_model.pkl"
    joblib.dump(model, model_path)
    logger.info(f"Model saved to {model_path}")

    # Save label encoder
    le_path = output_path / "label_encoder.pkl"
    joblib.dump(le, le_path)
    logger.info(f"Label encoder saved to {le_path}")
    
    # Save metrics
    metrics_path = output_path / "metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    logger.info(f"Metrics saved to {metrics_path}")
    
    # Save feature names for later use
    feature_names_path = output_path / "feature_names.json"
    with open(feature_names_path, 'w') as f:
        json.dump(list(model.feature_names_in_), f, indent=2)
    logger.info(f"Feature names saved to {feature_names_path}")

def main():
    """Main training function"""
    try:
        logger.info("Starting model training pipeline...")
        
        # Load and prepare data
        X, y, le = load_and_prepare_data()
        
        # Train model
        model, metrics, X_test, y_test = train_model(X, y, le)
        
        # Save model and metrics
        save_model_and_metrics(model, metrics, le)
        
        # Print detailed report
        logger.info("\n" + "="*50)
        logger.info("TRAINING SUMMARY")
        logger.info("="*50)
        logger.info(f"Best Hyperparameters: {metrics['best_params']}")
        logger.info(f"Training samples: {metrics['training_samples']}")
        logger.info(f"Test samples: {metrics['test_samples']}")
        logger.info(f"Features: {metrics['total_features']}")
        logger.info(f"Accuracy: {metrics['accuracy']:.3f}")
        logger.info(f"Precision: {metrics['precision']:.3f}")
        logger.info(f"Recall: {metrics['recall']:.3f}")
        logger.info(f"F1-Score: {metrics['f1_score']:.3f}")
        
        logger.info("\nFeature Importance:")
        for feature, importance in sorted(metrics['feature_importance'].items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {feature}: {importance:.3f}")
        
        logger.info("\nModel training completed successfully!")
        
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
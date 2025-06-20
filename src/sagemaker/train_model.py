import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_data(df):
    """Clean and preprocess the data"""
    logger.info("Cleaning data...")
    
    # Handle missing values
    df['failure'] = df['failure'].fillna('none')
    
    # Convert failure types to binary (none vs failure)
    df['failure'] = df['failure'].apply(lambda x: 'none' if x == 'none' else 'failure')
    
    # Convert numeric columns
    numeric_cols = ['volt', 'rotate', 'pressure', 'vibration', 'age']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df[col].median())
    
    return df

def train_model_locally():
    try:
        logger.info("Starting local model training...")
        
        # Read data
        data_path = Path('data/processed/processed_data.csv')
        df = pd.read_csv(data_path)
        logger.info(f"Read {len(df)} rows of data")
        
        # Clean data
        df = clean_data(df)
        
        # Prepare features and target
        features = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        X = df[features]
        y = df['failure'].map({'none': 0, 'failure': 1})
        
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Target distribution:\n{df['failure'].value_counts()}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        logger.info("Training Random Forest model...")
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate model
        accuracy = model.score(X_test, y_test)
        logger.info(f"Model accuracy: {accuracy:.4f}")
        
        # Save model
        models_dir = Path('models')
        models_dir.mkdir(exist_ok=True)
        
        model_path = models_dir / 'best_model.pkl'
        joblib.dump(model, model_path)
        logger.info(f"Model saved to: {model_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during training: {str(e)}")
        return False

if __name__ == '__main__':
    train_model_locally() 
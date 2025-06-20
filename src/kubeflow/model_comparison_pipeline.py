import kfp
from kfp import dsl
from kfp.components import create_component_from_func
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from pathlib import Path

def load_data():
    """Load and preprocess the data"""
    try:
        data_path = Path('data/processed/processed_data.csv')
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found at {data_path}")
            
        df = pd.read_csv(data_path)
        
        features = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        df['machineID'] = df['machineID'].astype('category').cat.codes
        df['model'] = df['model'].astype('category').cat.codes
        features += ['machineID', 'model']
        
        df['failure_flag'] = df['failure'].apply(lambda x: 0 if x == 'none' else 1)
        
        return df[features], df['failure_flag']
    except Exception as e:
        print(f"Error in load_data: {str(e)}")
        raise

def train_random_forest(X, y):
    """Train Random Forest model"""
    try:
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            bootstrap=True,
            random_state=42
        )
        model.fit(X, y)
        return model
    except Exception as e:
        print(f"Error in train_random_forest: {str(e)}")
        raise

def train_xgboost(X, y):
    """Train XGBoost model"""
    try:
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        model.fit(X, y)
        return model
    except Exception as e:
        print(f"Error in train_xgboost: {str(e)}")
        raise

def train_logistic_regression(X, y):
    """Train Logistic Regression model"""
    try:
        model = LogisticRegression(
            max_iter=1000,
            random_state=42
        )
        model.fit(X, y)
        return model
    except Exception as e:
        print(f"Error in train_logistic_regression: {str(e)}")
        raise

def evaluate_model(model, X, y):
    """Evaluate model performance"""
    try:
        y_pred = model.predict(X)
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred),
            'recall': recall_score(y, y_pred),
            'f1': f1_score(y, y_pred)
        }
        return metrics
    except Exception as e:
        print(f"Error in evaluate_model: {str(e)}")
        raise

# Create components
load_data_op = create_component_from_func(
    load_data,
    base_image='python:3.9',
    packages_to_install=['pandas', 'scikit-learn']
)

train_rf_op = create_component_from_func(
    train_random_forest,
    base_image='python:3.9',
    packages_to_install=['scikit-learn']
)

train_xgb_op = create_component_from_func(
    train_xgboost,
    base_image='python:3.9',
    packages_to_install=['xgboost', 'scikit-learn']
)

train_lr_op = create_component_from_func(
    train_logistic_regression,
    base_image='python:3.9',
    packages_to_install=['scikit-learn']
)

evaluate_op = create_component_from_func(
    evaluate_model,
    base_image='python:3.9',
    packages_to_install=['scikit-learn']
)

@dsl.pipeline(
    name='Model Comparison Pipeline',
    description='Compare different models for predictive maintenance'
)
def model_comparison_pipeline():
    # Load data
    load_data_task = load_data_op()
    
    # Train models
    rf_model = train_rf_op(load_data_task.outputs[0], load_data_task.outputs[1])
    xgb_model = train_xgb_op(load_data_task.outputs[0], load_data_task.outputs[1])
    lr_model = train_lr_op(load_data_task.outputs[0], load_data_task.outputs[1])
    
    # Evaluate models
    rf_metrics = evaluate_op(rf_model.output, load_data_task.outputs[0], load_data_task.outputs[1])
    xgb_metrics = evaluate_op(xgb_model.output, load_data_task.outputs[0], load_data_task.outputs[1])
    lr_metrics = evaluate_op(lr_model.output, load_data_task.outputs[0], load_data_task.outputs[1])

if __name__ == '__main__':
    kfp.compiler.Compiler().compile(model_comparison_pipeline, 'model_comparison_pipeline.yaml') 
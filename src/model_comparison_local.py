import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    confusion_matrix, roc_auc_score, classification_report,
    precision_recall_curve, average_precision_score, brier_score_loss
)
from sklearn.model_selection import cross_val_score, StratifiedKFold, learning_curve
import joblib
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import json
from tabulate import tabulate
import numpy as np
import time
from sklearn.inspection import permutation_importance
from sklearn.calibration import calibration_curve
from scipy.stats import ttest_rel

def load_and_prepare_data():
    """Load and preprocess the data"""
    try:
        data_path = Path('data/processed/processed_data.csv')
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found at {data_path}")
            
        print("Loading data...")
        df = pd.read_csv(data_path)
        
        features = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        df['machineID'] = df['machineID'].astype('category').cat.codes
        df['model'] = df['model'].astype('category').cat.codes
        features += ['machineID', 'model']
        
        df['failure_flag'] = df['failure'].apply(lambda x: 0 if x == 'none' else 1)
        
        print(f"Data loaded successfully. Shape: {df.shape}")
        return df[features], df['failure_flag']
    except Exception as e:
        print(f"Error in load_data: {str(e)}")
        raise

def create_detailed_comparison(results, X, y):
    """Create a detailed side-by-side comparison of models"""
    comparison_data = []
    headers = [
        'Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 
        'ROC AUC', 'Avg Precision', 'Training Time (s)', 
        'Prediction Time (s)', 'CV Accuracy (std)', 'Model Complexity'
    ]
    
    for name, result in results.items():
        model = result['model']
        metrics = result['metrics']
        
        # Calculate ROC AUC and Average Precision
        try:
            y_pred_proba = model.predict_proba(X)[:, 1]
            roc_auc = roc_auc_score(y, y_pred_proba)
            avg_precision = average_precision_score(y, y_pred_proba)
        except:
            roc_auc = 'N/A'
            avg_precision = 'N/A'
        
        # Calculate model complexity
        complexity = calculate_model_complexity(model)
        complexity_str = ', '.join(f"{k}: {v}" for k, v in complexity.items())
        
        # Get cross-validation scores
        cv_scores = perform_cross_validation(model, X, y)
        cv_accuracy = f"{cv_scores['accuracy'].mean():.4f} (±{cv_scores['accuracy'].std():.4f})"
        
        # Add to comparison data
        comparison_data.append([
            name,
            f"{metrics['accuracy']:.4f}",
            f"{metrics['precision']:.4f}",
            f"{metrics['recall']:.4f}",
            f"{metrics['f1']:.4f}",
            f"{roc_auc:.4f}" if isinstance(roc_auc, float) else roc_auc,
            f"{avg_precision:.4f}" if isinstance(avg_precision, float) else avg_precision,
            f"{result['training_time']:.2f}",
            f"{result['prediction_time']:.4f}",
            cv_accuracy,
            complexity_str
        ])
    
    # Create comparison table
    comparison_table = tabulate(comparison_data, headers=headers, tablefmt='grid')
    
    # Save comparison to file
    with open('model_comparison_table.txt', 'w') as f:
        f.write("Detailed Model Comparison\n")
        f.write("=======================\n\n")
        f.write(comparison_table)
        f.write("\n\nFeature Importance Analysis:\n")
        f.write("========================\n")
        
        for name, result in results.items():
            model = result['model']
            if hasattr(model, 'feature_importances_'):
                f.write(f"\n{name} Feature Importance:\n")
                importances = pd.DataFrame({
                    'Feature': X.columns,
                    'Importance': model.feature_importances_
                }).sort_values('Importance', ascending=False)
                f.write(tabulate(importances, headers='keys', tablefmt='grid', showindex=False))
                
                # Calculate permutation importance
                perm_importance = permutation_importance(model, X, y, n_repeats=10, random_state=42)
                perm_importance_df = pd.DataFrame({
                    'Feature': X.columns,
                    'Permutation Importance': perm_importance.importances_mean
                }).sort_values('Permutation Importance', ascending=False)
                f.write(f"\n{name} Permutation Importance:\n")
                f.write(tabulate(perm_importance_df, headers='keys', tablefmt='grid', showindex=False))
    
    print("\nDetailed comparison saved to 'model_comparison_table.txt'")
    return comparison_table

def train_and_evaluate_models(X, y):
    """Train and evaluate multiple models"""
    models = {
        'Random Forest': RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            bootstrap=True,
            random_state=42
        ),
        'XGBoost': xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        ),
        'Logistic Regression': LogisticRegression(
            max_iter=1000,
            random_state=42
        )
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Measure training time
        start_time = time.time()
        model.fit(X, y)
        training_time = time.time() - start_time
        
        # Measure prediction time
        start_time = time.time()
        y_pred = model.predict(X)
        prediction_time = time.time() - start_time
        
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred),
            'recall': recall_score(y, y_pred),
            'f1': f1_score(y, y_pred)
        }
        
        results[name] = {
            'metrics': metrics,
            'model': model,
            'predictions': y_pred,
            'training_time': training_time,
            'prediction_time': prediction_time
        }
        
        print(f"{name} Metrics:")
        for metric_name, value in metrics.items():
            print(f"{metric_name}: {value:.4f}")
        print(f"Training time: {training_time:.2f}s")
        print(f"Prediction time: {prediction_time:.4f}s")
    
    return results

def plot_results(results, y_true):
    """Plot comparison of model metrics"""
    # Create metrics comparison plot
    metrics_df = pd.DataFrame({
        name: results[name]['metrics'] 
        for name in results.keys()
    }).T
    
    plt.figure(figsize=(12, 6))
    metrics_df.plot(kind='bar')
    plt.title('Model Performance Comparison')
    plt.ylabel('Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('model_comparison_metrics.png')
    
    # Create confusion matrices
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for idx, (name, result) in enumerate(results.items()):
        cm = confusion_matrix(y_true, result['predictions'])
        sns.heatmap(cm, annot=True, fmt='d', ax=axes[idx])
        axes[idx].set_title(f'{name} Confusion Matrix')
    plt.tight_layout()
    plt.savefig('model_confusion_matrices.png')

def save_results(results):
    """Save model results and metrics"""
    # Save metrics to JSON
    metrics = {name: results[name]['metrics'] for name in results.keys()}
    with open('model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=4)
    
    # Save best model
    best_model_name = max(
        results.keys(),
        key=lambda x: results[x]['metrics']['f1']
    )
    best_model = results[best_model_name]['model']
    
    # Create models directory if it doesn't exist
    model_dir = Path('models')
    model_dir.mkdir(exist_ok=True)
    
    # Create model filename and path
    model_filename = best_model_name.lower().replace(' ', '_') + '_model.joblib'
    model_path = model_dir / model_filename
    
    # Save the model
    joblib.dump(best_model, model_path)
    
    print(f"\nBest model: {best_model_name}")
    print(f"Model saved to: {model_path}")

def plot_roc_curves(results, X, y):
    """Plot ROC curves for all models"""
    plt.figure(figsize=(10, 6))
    
    for name, result in results.items():
        model = result['model']
        try:
            y_pred_proba = model.predict_proba(X)[:, 1]
            fpr, tpr, _ = roc_curve(y, y_pred_proba)
            roc_auc = roc_auc_score(y, y_pred_proba)
            plt.plot(fpr, tpr, label=f'{name} (AUC = {roc_auc:.3f})')
        except:
            continue
    
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves Comparison')
    plt.legend(loc="lower right")
    plt.savefig('roc_curves.png')
    plt.close()

def plot_precision_recall_curves(results, X, y):
    """Plot Precision-Recall curves for all models"""
    plt.figure(figsize=(10, 6))
    
    for name, result in results.items():
        model = result['model']
        try:
            y_pred_proba = model.predict_proba(X)[:, 1]
            precision, recall, _ = precision_recall_curve(y, y_pred_proba)
            avg_precision = average_precision_score(y, y_pred_proba)
            plt.plot(recall, precision, label=f'{name} (AP = {avg_precision:.3f})')
        except:
            continue
    
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curves')
    plt.legend(loc="lower left")
    plt.savefig('precision_recall_curves.png')
    plt.close()

def calculate_model_complexity(model):
    """Calculate model complexity metrics"""
    complexity = {}
    
    if isinstance(model, RandomForestClassifier):
        complexity['n_trees'] = model.n_estimators
        complexity['avg_depth'] = np.mean([tree.get_depth() for tree in model.estimators_])
        complexity['n_leaves'] = np.mean([tree.get_n_leaves() for tree in model.estimators_])
        complexity['n_parameters'] = sum(tree.tree_.node_count for tree in model.estimators_)
    
    elif isinstance(model, xgb.XGBClassifier):
        complexity['n_trees'] = model.n_estimators
        complexity['max_depth'] = model.max_depth
        complexity['n_parameters'] = model.n_estimators * (2 ** model.max_depth - 1)
    
    elif isinstance(model, LogisticRegression):
        complexity['n_parameters'] = len(model.coef_[0]) + 1  # +1 for intercept
    
    return complexity

def perform_cross_validation(model, X, y, cv=5):
    """Perform cross-validation and return scores"""
    cv_scores = {
        'accuracy': cross_val_score(model, X, y, cv=cv, scoring='accuracy'),
        'precision': cross_val_score(model, X, y, cv=cv, scoring='precision'),
        'recall': cross_val_score(model, X, y, cv=cv, scoring='recall'),
        'f1': cross_val_score(model, X, y, cv=cv, scoring='f1'),
        'roc_auc': cross_val_score(model, X, y, cv=cv, scoring='roc_auc')
    }
    return cv_scores

def plot_feature_importance(results, X):
    """Plot feature importance for all models"""
    plt.figure(figsize=(12, 6))
    
    for idx, (name, result) in enumerate(results.items()):
        model = result['model']
        if hasattr(model, 'feature_importances_'):
            plt.subplot(1, len(results), idx + 1)
            importances = pd.DataFrame({
                'Feature': X.columns,
                'Importance': model.feature_importances_
            }).sort_values('Importance', ascending=True)
            
            plt.barh(range(len(importances)), importances['Importance'])
            plt.yticks(range(len(importances)), importances['Feature'])
            plt.title(f'{name} Feature Importance')
    
    plt.tight_layout()
    plt.savefig('feature_importance.png')
    plt.close()

def plot_calibration_curves(results, X, y):
    plt.figure(figsize=(10, 6))
    for name, result in results.items():
        model = result['model']
        try:
            y_pred_proba = model.predict_proba(X)[:, 1]
            prob_true, prob_pred = calibration_curve(y, y_pred_proba, n_bins=5)
            plt.plot(prob_pred, prob_true, marker='o', label=name)
        except:
            continue
    plt.plot([0, 1], [0, 1], 'k--', label='Perfectly calibrated')
    plt.xlabel('Mean predicted probability')
    plt.ylabel('Fraction of positives')
    plt.title('Calibration Curves')
    plt.legend()
    plt.savefig('calibration_curves.png')
    plt.close()

def plot_learning_curves(results, X, y):
    plt.figure(figsize=(12, 6))
    for name, result in results.items():
        model = result['model']
        try:
            train_sizes, train_scores, test_scores = learning_curve(model, X, y, cv=3, n_jobs=1, train_sizes=np.linspace(0.1, 1.0, 5))
            train_scores_mean = np.mean(train_scores, axis=1)
            test_scores_mean = np.mean(test_scores, axis=1)
            plt.plot(train_sizes, test_scores_mean, label=f'{name} (test)')
            plt.plot(train_sizes, train_scores_mean, '--', label=f'{name} (train)')
        except:
            continue
    plt.xlabel('Training examples')
    plt.ylabel('Score')
    plt.title('Learning Curves')
    plt.legend()
    plt.savefig('learning_curves.png')
    plt.close()

def add_advanced_metrics(results, X, y):
    # Add Brier score
    for name, result in results.items():
        model = result['model']
        try:
            y_pred_proba = model.predict_proba(X)[:, 1]
            brier = brier_score_loss(y, y_pred_proba)
        except:
            brier = 'N/A'
        result['metrics']['brier_score'] = brier

def statistical_significance_test(results, X, y):
    # Paired t-test on cross-val accuracy between best and others
    best_name = max(results.keys(), key=lambda x: results[x]['metrics']['f1'])
    best_model = results[best_name]['model']
    best_scores = cross_val_score(best_model, X, y, cv=3, scoring='accuracy')
    stats = {}
    for name, result in results.items():
        if name == best_name:
            continue
        model = result['model']
        scores = cross_val_score(model, X, y, cv=3, scoring='accuracy')
        try:
            t_stat, p_val = ttest_rel(best_scores, scores)
        except Exception as e:
            t_stat, p_val = None, None
        stats[name] = {'t_stat': t_stat, 'p_val': p_val}
    with open('statistical_significance.json', 'w') as f:
        json.dump(stats, f, indent=4)
    print(f"\nStatistical significance test results saved to 'statistical_significance.json'")

def main():
    print("Starting model comparison...")
    
    # Load and prepare data
    X, y = load_and_prepare_data()
    
    # Train and evaluate models
    results = train_and_evaluate_models(X, y)
    
    # Create detailed comparison
    comparison_table = create_detailed_comparison(results, X, y)
    print("\nModel Comparison Table:")
    print(comparison_table)
    
    # Generate plots
    plot_results(results, y)
    plot_roc_curves(results, X, y)
    plot_precision_recall_curves(results, X, y)
    plot_feature_importance(results, X)
    
    # Add advanced metrics
    add_advanced_metrics(results, X, y)
    # Statistical significance test
    statistical_significance_test(results, X, y)
    # Plot calibration curves
    plot_calibration_curves(results, X, y)
    # Plot learning curves
    plot_learning_curves(results, X, y)
    
    # Save results
    save_results(results)
    
    print("\nModel comparison completed!")
    print("Results saved in:")
    print("- model_comparison_table.txt")
    print("- model_metrics.json")
    print("- model_comparison_metrics.png")
    print("- model_confusion_matrices.png")
    print("- roc_curves.png")
    print("- precision_recall_curves.png")
    print("- feature_importance.png")
    print("- calibration_curves.png")
    print("- learning_curves.png")
    print("- statistical_significance.json")

if __name__ == '__main__':
    main() 
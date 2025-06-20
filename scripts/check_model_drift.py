#!/usr/bin/env python3
"""
Model Drift Detection Script
Detects data drift and model performance degradation
"""

import pandas as pd
import numpy as np
import joblib
import json
import logging
from pathlib import Path
from datetime import datetime
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelDriftDetector:
    """Detect model drift and performance degradation"""
    
    def __init__(self, model_path: str = "models/best_model.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.reference_data = None
        self.drift_threshold = 0.1  # 10% drift threshold
        self.performance_threshold = 0.05  # 5% performance degradation
        
    def load_model(self):
        """Load the trained model"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        self.model = joblib.load(self.model_path)
        logger.info("Model loaded successfully")
        
    def load_reference_data(self, reference_path: str = "data/processed/reference_data.csv"):
        """Load reference data for drift detection"""
        ref_path = Path(reference_path)
        if ref_path.exists():
            self.reference_data = pd.read_csv(ref_path)
            logger.info("Reference data loaded successfully")
        else:
            logger.warning("Reference data not found, using current data as reference")
            self.reference_data = None
    
    def detect_data_drift(self, current_data: pd.DataFrame) -> dict:
        """Detect data drift between reference and current data"""
        if self.reference_data is None:
            return {"drift_detected": False, "message": "No reference data available"}
        
        drift_results = {}
        feature_cols = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        
        for col in feature_cols:
            if col in self.reference_data.columns and col in current_data.columns:
                # Statistical tests for drift
                ref_mean = self.reference_data[col].mean()
                ref_std = self.reference_data[col].std()
                curr_mean = current_data[col].mean()
                curr_std = current_data[col].std()
                
                # Calculate drift metrics
                mean_drift = abs(ref_mean - curr_mean) / ref_std if ref_std > 0 else 0
                std_drift = abs(ref_std - curr_std) / ref_std if ref_std > 0 else 0
                
                # Kolmogorov-Smirnov test
                ks_stat, ks_pvalue = stats.ks_2samp(
                    self.reference_data[col].dropna(),
                    current_data[col].dropna()
                )
                
                drift_results[col] = {
                    "mean_drift": mean_drift,
                    "std_drift": std_drift,
                    "ks_statistic": ks_stat,
                    "ks_pvalue": ks_pvalue,
                    "drift_detected": mean_drift > 2.0 or std_drift > 2.0 or ks_pvalue < 0.05
                }
        
        # Overall drift detection
        total_drift = sum(1 for result in drift_results.values() if result["drift_detected"])
        overall_drift = total_drift / len(drift_results) > self.drift_threshold
        
        return {
            "drift_detected": overall_drift,
            "feature_drift": drift_results,
            "total_features_with_drift": total_drift,
            "drift_percentage": total_drift / len(drift_results) if drift_results else 0
        }
    
    def detect_performance_degradation(self, current_data: pd.DataFrame) -> dict:
        """Detect model performance degradation"""
        if self.model is None:
            return {"degradation_detected": False, "message": "Model not loaded"}
        
        # Load historical performance
        metrics_path = Path("models/metrics.json")
        if not metrics_path.exists():
            return {"degradation_detected": False, "message": "No historical metrics available"}
        
        with open(metrics_path, 'r') as f:
            historical_metrics = json.load(f)
        
        # Prepare current data
        feature_cols = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        X = current_data[feature_cols].dropna()
        y = current_data['failure'].dropna()
        
        if len(X) == 0 or len(y) == 0:
            return {"degradation_detected": False, "message": "Insufficient data for evaluation"}
        
        # Make predictions
        y_pred = self.model.predict(X)
        
        # Calculate current metrics
        current_metrics = {
            "accuracy": accuracy_score(y, y_pred),
            "precision": precision_score(y, y_pred, average='weighted'),
            "recall": recall_score(y, y_pred, average='weighted'),
            "f1_score": f1_score(y, y_pred, average='weighted')
        }
        
        # Compare with historical metrics
        degradation_results = {}
        for metric, current_value in current_metrics.items():
            if metric in historical_metrics:
                historical_value = historical_metrics[metric]
                degradation = historical_value - current_value
                degradation_percentage = degradation / historical_value if historical_value > 0 else 0
                
                degradation_results[metric] = {
                    "historical": historical_value,
                    "current": current_value,
                    "degradation": degradation,
                    "degradation_percentage": degradation_percentage,
                    "degradation_detected": degradation_percentage > self.performance_threshold
                }
        
        # Overall degradation detection
        total_degradation = sum(1 for result in degradation_results.values() if result["degradation_detected"])
        overall_degradation = total_degradation > 0
        
        return {
            "degradation_detected": overall_degradation,
            "metrics_comparison": degradation_results,
            "current_metrics": current_metrics,
            "historical_metrics": historical_metrics
        }
    
    def generate_drift_report(self, current_data_path: str = "data/processed/processed_data.csv") -> dict:
        """Generate comprehensive drift report"""
        logger.info("Starting drift detection analysis...")
        
        # Load current data
        current_data = pd.read_csv(current_data_path)
        
        # Detect data drift
        data_drift = self.detect_data_drift(current_data)
        
        # Detect performance degradation
        performance_degradation = self.detect_performance_degradation(current_data)
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "data_drift": data_drift,
            "performance_degradation": performance_degradation,
            "overall_status": "healthy"
        }
        
        # Determine overall status
        if data_drift["drift_detected"] or performance_degradation["degradation_detected"]:
            report["overall_status"] = "warning"
            if data_drift["drift_detected"] and performance_degradation["degradation_detected"]:
                report["overall_status"] = "critical"
        
        # Save report
        report_path = Path("reports_and_artifacts/drift_report.json")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Drift report saved to {report_path}")
        return report

def main():
    """Main function"""
    detector = ModelDriftDetector()
    
    try:
        # Load model and reference data
        detector.load_model()
        detector.load_reference_data()
        
        # Generate drift report
        report = detector.generate_drift_report()
        
        # Print summary
        print("\n=== Model Drift Detection Report ===")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Overall Status: {report['overall_status'].upper()}")
        
        if report['data_drift']['drift_detected']:
            print("⚠️  DATA DRIFT DETECTED")
            print(f"Features with drift: {report['data_drift']['total_features_with_drift']}")
        
        if report['performance_degradation']['degradation_detected']:
            print("⚠️  PERFORMANCE DEGRADATION DETECTED")
            for metric, result in report['performance_degradation']['metrics_comparison'].items():
                if result['degradation_detected']:
                    print(f"  - {metric}: {result['degradation_percentage']:.2%} degradation")
        
        if report['overall_status'] == 'healthy':
            print("✅ No significant drift or degradation detected")
        
        # Exit with appropriate code
        if report['overall_status'] in ['warning', 'critical']:
            exit(1)
        else:
            exit(0)
            
    except Exception as e:
        logger.error(f"Error in drift detection: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 
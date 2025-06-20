"""
Data Drift Detection Module
Detects statistical drift between reference and current data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

logger = logging.getLogger(__name__)

class DriftDetector:
    """Detects data drift between reference and current datasets"""
    
    def __init__(self, reference_data: pd.DataFrame, output_dir: Path):
        self.reference_data = reference_data
        self.output_dir = output_dir
        self.drift_metrics = {}
        
    def detect_drift(self, current_data: pd.DataFrame) -> Dict:
        """Detect drift between reference and current data"""
        logger.info("Starting drift detection...")
        
        drift_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_drift_detected": False,
            "feature_drift": {},
            "statistical_tests": {},
            "drift_severity": "none"
        }
        
        # Get numeric columns for drift detection
        numeric_cols = current_data.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col in self.reference_data.columns]
        
        drift_detected_count = 0
        
        for col in numeric_cols:
            ref_values = self.reference_data[col].dropna()
            cur_values = current_data[col].dropna()
            
            if len(ref_values) < 10 or len(cur_values) < 10:
                continue
                
            # Kolmogorov-Smirnov test for distribution drift
            ks_stat, ks_pvalue = stats.ks_2samp(ref_values, cur_values)
            
            # Mann-Whitney U test for location drift
            mw_stat, mw_pvalue = stats.mannwhitneyu(ref_values, cur_values, alternative='two-sided')
            
            # Calculate effect size (Cohen's d)
            pooled_std = np.sqrt(((len(ref_values) - 1) * ref_values.var() + 
                                (len(cur_values) - 1) * cur_values.var()) / 
                               (len(ref_values) + len(cur_values) - 2))
            cohens_d = (cur_values.mean() - ref_values.mean()) / pooled_std
            
            # Determine drift severity
            drift_detected = ks_pvalue < 0.05 or mw_pvalue < 0.05
            if drift_detected:
                drift_detected_count += 1
            
            severity = self._classify_drift_severity(ks_pvalue, mw_pvalue, abs(cohens_d))
            
            drift_results["feature_drift"][col] = {
                "drift_detected": drift_detected,
                "severity": severity,
                "ks_statistic": ks_stat,
                "ks_pvalue": ks_pvalue,
                "mw_statistic": mw_stat,
                "mw_pvalue": mw_pvalue,
                "cohens_d": cohens_d,
                "reference_mean": ref_values.mean(),
                "current_mean": cur_values.mean(),
                "reference_std": ref_values.std(),
                "current_std": cur_values.std()
            }
            
            drift_results["statistical_tests"][col] = {
                "ks_test": {"statistic": ks_stat, "pvalue": ks_pvalue},
                "mann_whitney": {"statistic": mw_stat, "pvalue": mw_pvalue}
            }
        
        # Overall drift assessment
        drift_percentage = (drift_detected_count / len(numeric_cols)) * 100 if numeric_cols else 0
        drift_results["overall_drift_detected"] = drift_percentage > 20  # 20% threshold
        drift_results["drift_percentage"] = drift_percentage
        
        # Classify overall severity
        if drift_percentage > 50:
            drift_results["drift_severity"] = "high"
        elif drift_percentage > 20:
            drift_results["drift_severity"] = "medium"
        else:
            drift_results["drift_severity"] = "low"
        
        self.drift_metrics = drift_results
        logger.info(f"Drift detection completed. {drift_percentage:.1f}% of features show drift.")
        
        return drift_results
    
    def _classify_drift_severity(self, ks_pvalue: float, mw_pvalue: float, cohens_d: float) -> str:
        """Classify the severity of drift for a feature"""
        if ks_pvalue < 0.01 or mw_pvalue < 0.01 or cohens_d > 0.8:
            return "high"
        elif ks_pvalue < 0.05 or mw_pvalue < 0.05 or cohens_d > 0.5:
            return "medium"
        else:
            return "low"
    
    def generate_plots(self, current_data: pd.DataFrame) -> None:
        """Generate drift visualization plots"""
        logger.info("Generating drift visualization plots...")
        
        numeric_cols = current_data.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col in self.reference_data.columns]
        
        # Create subplots for each feature
        n_features = len(numeric_cols)
        if n_features == 0:
            return
            
        fig, axes = plt.subplots(2, min(3, n_features), figsize=(15, 10))
        if n_features == 1:
            axes = axes.reshape(-1, 1)
        
        for i, col in enumerate(numeric_cols[:6]):  # Limit to 6 features for readability
            row = i // 3
            col_idx = i % 3
            
            if n_features == 1:
                ax1, ax2 = axes[0], axes[1]
            else:
                ax1, ax2 = axes[row, col_idx], axes[row, col_idx]
            
            # Distribution comparison
            ref_values = self.reference_data[col].dropna()
            cur_values = current_data[col].dropna()
            
            ax1.hist(ref_values, alpha=0.5, label='Reference', bins=30, density=True)
            ax1.hist(cur_values, alpha=0.5, label='Current', bins=30, density=True)
            ax1.set_title(f'{col} - Distribution Comparison')
            ax1.legend()
            ax1.set_xlabel(col)
            ax1.set_ylabel('Density')
            
            # Box plot comparison
            data_to_plot = [ref_values, cur_values]
            ax2.boxplot(data_to_plot, labels=['Reference', 'Current'])
            ax2.set_title(f'{col} - Box Plot Comparison')
            ax2.set_ylabel(col)
        
        plt.tight_layout()
        plot_path = self.output_dir / 'drift_analysis.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Drift plots saved to {plot_path}")
    
    def generate_report(self) -> str:
        """Generate a comprehensive drift report"""
        if not self.drift_metrics:
            return "No drift detection results available."
        
        report = []
        report.append("=" * 60)
        report.append("DATA DRIFT DETECTION REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {self.drift_metrics['timestamp']}")
        report.append(f"Overall Drift Detected: {self.drift_metrics['overall_drift_detected']}")
        report.append(f"Drift Percentage: {self.drift_metrics.get('drift_percentage', 0):.1f}%")
        report.append(f"Overall Severity: {self.drift_metrics['drift_severity'].upper()}")
        report.append("")
        
        # Feature-level drift summary
        report.append("FEATURE-LEVEL DRIFT ANALYSIS")
        report.append("-" * 40)
        
        for feature, metrics in self.drift_metrics.get("feature_drift", {}).items():
            report.append(f"\nFeature: {feature}")
            report.append(f"  Drift Detected: {metrics['drift_detected']}")
            report.append(f"  Severity: {metrics['severity'].upper()}")
            report.append(f"  KS Test p-value: {metrics['ks_pvalue']:.4f}")
            report.append(f"  Mann-Whitney p-value: {metrics['mw_pvalue']:.4f}")
            report.append(f"  Effect Size (Cohen's d): {metrics['cohens_d']:.3f}")
            report.append(f"  Reference Mean: {metrics['reference_mean']:.3f}")
            report.append(f"  Current Mean: {metrics['current_mean']:.3f}")
        
        # Recommendations
        report.append("\n" + "=" * 60)
        report.append("RECOMMENDATIONS")
        report.append("=" * 60)
        
        severity = self.drift_metrics['drift_severity']
        if severity == "high":
            report.append("🚨 HIGH DRIFT DETECTED")
            report.append("- Immediate model retraining recommended")
            report.append("- Investigate data pipeline changes")
            report.append("- Consider feature engineering updates")
            report.append("- Monitor model performance closely")
        elif severity == "medium":
            report.append("⚠️  MEDIUM DRIFT DETECTED")
            report.append("- Schedule model retraining soon")
            report.append("- Monitor drift trends over time")
            report.append("- Consider incremental learning")
        else:
            report.append("✅ LOW DRIFT DETECTED")
            report.append("- Continue monitoring")
            report.append("- No immediate action required")
        
        return "\n".join(report)
    
    def save_metrics(self, filename: str = "drift_metrics.json") -> None:
        """Save drift metrics to file"""
        import json
        metrics_path = self.output_dir / filename
        with open(metrics_path, 'w') as f:
            json.dump(self.drift_metrics, f, indent=2, default=str)
        logger.info(f"Drift metrics saved to {metrics_path}") 
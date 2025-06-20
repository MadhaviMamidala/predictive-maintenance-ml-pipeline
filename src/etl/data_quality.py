import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataQualityChecker:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.quality_metrics = {}
        
    def check_missing_values(self) -> Dict[str, float]:
        """Check percentage of missing values in each column"""
        missing_pct = (self.df.isnull().sum() / len(self.df)) * 100
        self.quality_metrics['missing_values'] = missing_pct.to_dict()
        return missing_pct.to_dict()
    
    def check_numeric_ranges(self) -> Dict[str, Dict[str, float]]:
        """Check if numeric values are within expected ranges"""
        numeric_cols = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        ranges = {}
        
        for col in numeric_cols:
            if col in self.df.columns:
                ranges[col] = {
                    'min': self.df[col].min(),
                    'max': self.df[col].max(),
                    'mean': self.df[col].mean(),
                    'std': self.df[col].std()
                }
        
        self.quality_metrics['numeric_ranges'] = ranges
        return ranges
    
    def check_categorical_values(self) -> Dict[str, List[str]]:
        """Check unique values in categorical columns"""
        categorical_cols = ['errorID', 'failure', 'comp_maint', 'model']
        unique_values = {}
        
        for col in categorical_cols:
            if col in self.df.columns:
                unique_values[col] = self.df[col].unique().tolist()
        
        self.quality_metrics['categorical_values'] = unique_values
        return unique_values
    
    def check_data_consistency(self) -> Dict[str, bool]:
        """Check data consistency rules"""
        consistency_checks = {
            'datetime_ordered': self.df['datetime'].is_monotonic_increasing,
            'no_negative_values': all(self.df[['volt', 'rotate', 'pressure', 'vibration', 'age']].min() >= 0),
            'machine_id_unique': self.df['machineID'].nunique() == len(self.df)
        }
        
        self.quality_metrics['consistency_checks'] = consistency_checks
        return consistency_checks
    
    def run_all_checks(self) -> Dict:
        """Run all data quality checks"""
        logger.info("Running data quality checks...")
        
        self.check_missing_values()
        self.check_numeric_ranges()
        self.check_categorical_values()
        self.check_data_consistency()
        
        logger.info("Data quality checks completed")
        return self.quality_metrics
    
    def generate_report(self) -> str:
        """Generate a human-readable report of data quality metrics"""
        report = []
        report.append("Data Quality Report")
        report.append("=" * 50)
        
        # Missing Values
        report.append("\nMissing Values:")
        for col, pct in self.quality_metrics['missing_values'].items():
            report.append(f"{col}: {pct:.2f}%")
        
        # Numeric Ranges
        report.append("\nNumeric Ranges:")
        for col, stats in self.quality_metrics['numeric_ranges'].items():
            report.append(f"\n{col}:")
            for stat, value in stats.items():
                report.append(f"  {stat}: {value:.2f}")
        
        # Consistency Checks
        report.append("\nConsistency Checks:")
        for check, result in self.quality_metrics['consistency_checks'].items():
            report.append(f"{check}: {'✓' if result else '✗'}")
        
        return "\n".join(report) 
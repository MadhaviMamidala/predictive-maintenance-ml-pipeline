import pandas as pd
from pathlib import Path
import logging
from typing import Optional, Dict
from .schema import PredictiveMaintenanceSchema
from .data_quality import DataQualityChecker
from .drift_detection import DriftDetector
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
input_path = Path('data/predictive_maintenance_full.csv')
output_dir = Path('data/processed')
output_dir.mkdir(exist_ok=True)
output_path = output_dir / 'processed_data.csv'
quality_report_path = output_dir / 'data_quality_report.txt'
quality_metrics_path = output_dir / 'data_quality_metrics.json'
reference_data_path = output_dir / 'reference_data.csv'
drift_report_path = output_dir / 'drift_report.txt'

def validate_schema(df: pd.DataFrame) -> bool:
    """Validate data against schema"""
    try:
        # Convert DataFrame rows to dict and validate
        for _, row in df.iterrows():
            PredictiveMaintenanceSchema(**row.to_dict())
        return True
    except Exception as e:
        logger.error(f"Schema validation failed: {str(e)}")
        return False

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and preprocess the data"""
    logger.info("Starting data cleaning...")
    
    # Convert datetime
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Convert numeric columns
    for col in ['volt', 'rotate', 'pressure', 'vibration', 'age']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Fill missing values
    df['errorID'] = df['errorID'].fillna('none')
    df['failure'] = df['failure'].fillna('none')
    df['comp_maint'] = df['comp_maint'].fillna('none')
    df['model'] = df['model'].fillna('unknown')
    df['age'] = df['age'].fillna(df['age'].median())
    
    # Drop rows with critical missing values
    df = df.dropna(subset=['datetime', 'machineID'])
    
    logger.info("Data cleaning completed")
    return df

def check_drift(df: pd.DataFrame) -> Optional[Dict]:
    """Check for data drift if reference data exists"""
    if reference_data_path.exists():
        logger.info("Checking for data drift...")
        reference_data = pd.read_csv(reference_data_path)
        drift_detector = DriftDetector(reference_data, output_dir)
        drift_metrics = drift_detector.detect_drift(df)
        
        # Save drift report
        drift_report = drift_detector.generate_report()
        with open(drift_report_path, 'w') as f:
            f.write(drift_report)
        
        return drift_metrics
    else:
        logger.info("No reference data found. Saving current data as reference.")
        df.to_csv(reference_data_path, index=False)
        return None

def main():
    try:
        # Read data
        logger.info(f'Reading {input_path}...')
        df = pd.read_csv(input_path)
        
        # Validate schema
        logger.info("Validating data schema...")
        if not validate_schema(df):
            raise ValueError("Data schema validation failed")
        
        # Clean data
        logger.info("Cleaning data...")
        df_clean = clean_data(df)
        
        # Run data quality checks
        logger.info("Running data quality checks...")
        quality_checker = DataQualityChecker(df_clean)
        quality_metrics = quality_checker.run_all_checks()
        
        # Save quality report
        quality_report = quality_checker.generate_report()
        with open(quality_report_path, 'w') as f:
            f.write(quality_report)
        
        # Save quality metrics
        with open(quality_metrics_path, 'w') as f:
            json.dump(quality_metrics, f, indent=2)
        
        # Check for data drift
        drift_metrics = check_drift(df_clean)
        if drift_metrics:
            logger.info("Data drift detected. Check drift_report.txt for details.")
        
        # Save processed data
        logger.info(f'Saving cleaned data to {output_path}...')
        df_clean.to_csv(output_path, index=False)
        
        logger.info("ETL process completed successfully!")
        
    except Exception as e:
        logger.error(f"ETL process failed: {str(e)}")
        raise

if __name__ == '__main__':
    main() 
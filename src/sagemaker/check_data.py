import pandas as pd
import numpy as np
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inspect_data():
    try:
        # Read data
        data_path = Path('data/processed/processed_data.csv')
        df = pd.read_csv(data_path)
        
        logger.info(f"\nDataset Info:")
        logger.info(f"Shape: {df.shape}")
        
        logger.info(f"\nMissing Values:")
        logger.info(df.isnull().sum())
        
        logger.info(f"\nFailure Values:")
        logger.info(df['failure'].value_counts(dropna=False))
        
        logger.info(f"\nSample of Data:")
        logger.info(df.head())
        
        logger.info(f"\nColumns:")
        logger.info(df.columns.tolist())
        
    except Exception as e:
        logger.error(f"❌ Error inspecting data: {str(e)}")

if __name__ == '__main__':
    inspect_data() 
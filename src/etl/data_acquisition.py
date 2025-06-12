import os
import kaggle
import pandas as pd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataAcquisition:
    def __init__(self, dataset_name="predictive-maintenance-dataset", output_dir="../data/raw"):
        """
        Initialize the data acquisition process
        
        Args:
            dataset_name (str): Name of the Kaggle dataset
            output_dir (str): Directory to save the downloaded data
        """
        self.dataset_name = dataset_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def download_dataset(self):
        """Download the dataset from Kaggle"""
        try:
            logger.info(f"Downloading dataset: {self.dataset_name}")
            kaggle.api.dataset_download_files(
                self.dataset_name,
                path=self.output_dir,
                unzip=True
            )
            logger.info("Dataset downloaded successfully")
        except Exception as e:
            logger.error(f"Error downloading dataset: {str(e)}")
            raise
            
    def validate_dataset(self):
        """Validate the downloaded dataset"""
        try:
            # Check if files exist
            files = list(self.output_dir.glob("*.csv"))
            if not files:
                raise FileNotFoundError("No CSV files found in the dataset")
                
            # Read and validate the main dataset
            df = pd.read_csv(files[0])
            
            # Basic validation
            required_columns = ['timestamp', 'sensor_1', 'sensor_2', 'sensor_3', 'failure']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
                
            logger.info(f"Dataset validation successful. Shape: {df.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating dataset: {str(e)}")
            raise
            
    def prepare_data(self):
        """Prepare the data for ETL process"""
        try:
            # Read the dataset
            files = list(self.output_dir.glob("*.csv"))
            df = pd.read_csv(files[0])
            
            # Basic preprocessing
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Save processed data
            processed_dir = self.output_dir.parent / 'processed'
            processed_dir.mkdir(exist_ok=True)
            
            df.to_csv(processed_dir / 'processed_data.csv', index=False)
            logger.info("Data preparation completed successfully")
            
        except Exception as e:
            logger.error(f"Error preparing data: {str(e)}")
            raise

def main():
    """Main function to run the data acquisition process"""
    try:
        # Initialize data acquisition
        data_acq = DataAcquisition()
        
        # Download dataset
        data_acq.download_dataset()
        
        # Validate dataset
        data_acq.validate_dataset()
        
        # Prepare data
        data_acq.prepare_data()
        
        logger.info("Data acquisition process completed successfully")
        
    except Exception as e:
        logger.error(f"Error in data acquisition process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
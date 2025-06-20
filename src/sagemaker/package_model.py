import os
import tarfile
import shutil
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def package_model():
    """Package model and dependencies for SageMaker deployment"""
    try:
        # Create a temporary directory
        tmp_dir = Path('tmp_model')
        tmp_dir.mkdir(exist_ok=True)
        
        # Copy model file
        logger.info("Copying model file...")
        shutil.copy2('models/random_forest_model.joblib', tmp_dir / 'model.joblib')
        
        # Create tar.gz archive
        logger.info("Creating model archive...")
        with tarfile.open('models/model.tar.gz', 'w:gz') as tar:
            tar.add(tmp_dir / 'model.joblib', arcname='model.joblib')
        
        # Clean up
        shutil.rmtree(tmp_dir)
        
        logger.info("Model packaged successfully at models/model.tar.gz")
        
    except Exception as e:
        logger.error(f"Error packaging model: {e}")
        raise

if __name__ == '__main__':
    package_model() 
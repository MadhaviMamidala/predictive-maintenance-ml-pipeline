import boto3
import sagemaker
import tarfile
import joblib
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_and_convert_model():
    try:
        # Initialize SageMaker session
        sagemaker_session = sagemaker.Session()
        account_id = boto3.client('sts').get_caller_identity()['Account']
        region = boto3.session.Session().region_name
        
        # Get the latest training job
        sm_client = boto3.client('sagemaker')
        training_jobs = sm_client.list_training_jobs(
            NameContains='madhu-predictive-maintenance',
            SortBy='CreationTime',
            SortOrder='Descending',
            MaxResults=1
        )
        
        if not training_jobs['TrainingJobSummaries']:
            logger.error("❌ No training jobs found!")
            return False
            
        job_name = training_jobs['TrainingJobSummaries'][0]['TrainingJobName']
        logger.info(f"Found training job: {job_name}")
        
        # Get model artifacts path
        training_details = sm_client.describe_training_job(TrainingJobName=job_name)
        model_artifacts = training_details['ModelArtifacts']['S3ModelArtifacts']
        
        # Create models directory if it doesn't exist
        models_dir = Path('models')
        models_dir.mkdir(exist_ok=True)
        
        # Download model artifacts
        logger.info("Downloading model artifacts...")
        tar_path = models_dir / 'model.tar.gz'
        sagemaker_session.download_data(
            str(models_dir),
            bucket=model_artifacts.split('/')[2],
            key_prefix='/'.join(model_artifacts.split('/')[3:])
        )
        
        # Extract model file
        logger.info("Extracting model file...")
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.extractall(path=models_dir)
        
        # Load and save in correct format
        logger.info("Converting model format...")
        model = joblib.load(models_dir / 'model.joblib')
        joblib.dump(model, models_dir / 'best_model.pkl')
        
        # Cleanup temporary files
        os.remove(tar_path)
        os.remove(models_dir / 'model.joblib')
        
        logger.info("✅ Model downloaded and converted successfully!")
        logger.info(f"Model saved as: models/best_model.pkl")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error downloading model: {str(e)}")
        return False

if __name__ == '__main__':
    download_and_convert_model() 
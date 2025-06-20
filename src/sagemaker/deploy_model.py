import boto3
import sagemaker
from sagemaker.sklearn import SKLearnModel
import logging
from pathlib import Path
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deploy_to_sagemaker():
    """Deploy trained model to SageMaker"""
    try:
        # Initialize SageMaker session
        sagemaker_session = sagemaker.Session()
        region = 'us-west-2'
        bucket_name = 'coredefender.madhu'
        role = 'arn:aws:iam::890992969813:role/SageMakerExecutionRole'
        
        # Upload model to S3
        logger.info("Uploading model to S3...")
        model_data = sagemaker_session.upload_data(
            path='models/model.tar.gz',
            bucket=bucket_name,
            key_prefix='models'
        )
        
        # Create SageMaker model
        logger.info("Creating SageMaker model...")
        model = SKLearnModel(
            model_data=model_data,
            role=role,
            entry_point='inference.py',
            source_dir='src/sagemaker',
            framework_version='0.23-1',
            py_version='py3',
            sagemaker_session=sagemaker_session
        )
        
        # Deploy model to endpoint
        endpoint_name = f'yespredictive-maintenance-{int(time.time())}'
        logger.info(f"Deploying model to endpoint: {endpoint_name}")
        
        predictor = model.deploy(
            initial_instance_count=1,
            instance_type='ml.t2.medium',
            endpoint_name=endpoint_name
        )
        
        logger.info(f"Model deployed successfully to endpoint: {endpoint_name}")
        logger.info(f"Endpoint URL: https://runtime.sagemaker.{region}.amazonaws.com/endpoints/{endpoint_name}")
        
        return endpoint_name
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise

if __name__ == '__main__':
    deploy_to_sagemaker() 
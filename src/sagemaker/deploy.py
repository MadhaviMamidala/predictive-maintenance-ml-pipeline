import boto3
import sagemaker
from sagemaker.sklearn import SKLearn
from sagemaker import get_execution_role
import json
import time
import logging
from pathlib import Path
from src.sagemaker.monitoring import SageMakerMonitor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SageMakerDeployer:
    """SageMaker deployment class for predictive maintenance"""
    
    def __init__(self, region='us-west-2', bucket_name='coredefender.madhu'):
        """Initialize SageMaker session and resources"""
        self.region = region
        self.bucket_name = bucket_name
        self.sagemaker_session = sagemaker.Session()
        
        # Use specific role ARN instead of get_execution_role()
        self.role = 'arn:aws:iam::890992969813:role/SageMakerExecutionRole'
        
        # Initialize AWS clients
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        
        logger.info(f"Initialized SageMaker session in region: {region}")
        logger.info(f"Using S3 bucket: {bucket_name}")
        logger.info(f"Using role: {self.role}")
    
    def upload_data_to_s3(self, local_data_path, s3_key):
        """Upload training data to S3"""
        try:
            logger.info(f"Uploading data from {local_data_path} to s3://{self.bucket_name}/{s3_key}")
            
            self.s3_client.upload_file(
                local_data_path,
                self.bucket_name,
                s3_key
            )
            
            s3_data_path = f"s3://{self.bucket_name}/{s3_key}"
            logger.info(f"Data uploaded successfully to: {s3_data_path}")
            return s3_data_path
            
        except Exception as e:
            logger.error(f"Error uploading data to S3: {e}")
            raise
    
    def create_training_job(self, training_data_s3_path, job_name=None):
        """Create and run SageMaker training job"""
        try:
            if job_name is None:
                job_name = f"predictive-maintenance-{int(time.time())}"
            
            logger.info(f"Creating training job: {job_name}")
            
            # Create SKLearn estimator
            sklearn_estimator = SKLearn(
                entry_point='train.py',
                source_dir='src/sagemaker',
                role=self.role,
                instance_count=1,
                instance_type='ml.m5.large',
                framework_version='1.0-1',
                py_version='py3',
                output_path=f's3://{self.bucket_name}/models/',
                code_location=f's3://{self.bucket_name}/code/',
                hyperparameters={
                    'n_estimators': 100,
                    'max_depth': 10
                }
            )
            
            # Start training
            sklearn_estimator.fit({
                'training': training_data_s3_path
            }, job_name=job_name)
            
            logger.info(f"Training job {job_name} completed successfully")
            return sklearn_estimator
            
        except Exception as e:
            logger.error(f"Error creating training job: {e}")
            raise
    
    def create_model(self, training_job_name, model_name=None):
        """Create SageMaker model from training job"""
        try:
            if model_name is None:
                model_name = f"predictive-maintenance-model-{int(time.time())}"
            
            logger.info(f"Creating model: {model_name}")
            
            # Get model artifacts from training job
            model_artifacts = f"s3://{self.bucket_name}/models/{training_job_name}/output/model.tar.gz"
            
            # Create model
            model = sagemaker.Model(
                image_uri=sklearn_estimator.training_image_uri(),
                model_data=model_artifacts,
                role=self.role,
                name=model_name,
                entry_point='inference.py',
                source_dir='src/sagemaker'
            )
            
            logger.info(f"Model {model_name} created successfully")
            return model
            
        except Exception as e:
            logger.error(f"Error creating model: {e}")
            raise
    
    def deploy_endpoint(self, model, endpoint_name=None, instance_type='ml.t2.medium'):
        """Deploy model to SageMaker endpoint"""
        try:
            if endpoint_name is None:
                endpoint_name = f"predictive-maintenance-endpoint-{int(time.time())}"
            
            logger.info(f"Deploying endpoint: {endpoint_name}")
            
            # Deploy model
            predictor = model.deploy(
                initial_instance_count=1,
                instance_type=instance_type,
                endpoint_name=endpoint_name
            )
            
            logger.info(f"Endpoint {endpoint_name} deployed successfully")
            return predictor, endpoint_name
            
        except Exception as e:
            logger.error(f"Error deploying endpoint: {e}")
            raise
    
    def setup_monitoring(self, endpoint_name, baseline_data_path):
        """Set up monitoring for the endpoint"""
        try:
            logger.info(f"Setting up monitoring for endpoint: {endpoint_name}")
            
            # Initialize monitor
            monitor = SageMakerMonitor(endpoint_name, self.region, self.bucket_name)
            
            # Upload baseline data
            baseline_s3_path = self.upload_data_to_s3(
                baseline_data_path,
                f"baseline/processed_data.csv"
            )
            
            # Enable data capture
            monitor.enable_data_capture()
            
            # Create monitoring schedule
            schedule_name = monitor.create_monitoring_schedule(baseline_s3_path)
            
            # Create CloudWatch dashboard
            dashboard_name = monitor.create_cloudwatch_dashboard()
            
            # Create alarms
            monitor.create_alarms()
            
            logger.info("Monitoring setup completed successfully")
            return schedule_name, dashboard_name
            
        except Exception as e:
            logger.error(f"Error setting up monitoring: {e}")
            raise

def main():
    """Main deployment function"""
    try:
        # Initialize deployer
        deployer = SageMakerDeployer()
        
        # Upload training data
        local_data_path = "data/processed/processed_data.csv"
        s3_data_path = deployer.upload_data_to_s3(local_data_path, "training/processed_data.csv")
        
        # Create training job
        training_job_name = f"predictive-maintenance-{int(time.time())}"
        sklearn_estimator = deployer.create_training_job(s3_data_path, training_job_name)
        
        # Create model
        model_name = f"predictive-maintenance-model-{int(time.time())}"
        model = deployer.create_model(training_job_name, model_name)
        
        # Deploy endpoint
        endpoint_name = f"predictive-maintenance-endpoint-{int(time.time())}"
        predictor, endpoint_name = deployer.deploy_endpoint(model, endpoint_name)
        
        # Set up monitoring
        schedule_name, dashboard_name = deployer.setup_monitoring(
            endpoint_name,
            local_data_path
        )
        
        logger.info("🎉 SageMaker deployment completed successfully!")
        logger.info(f"Endpoint URL: https://runtime.sagemaker.{deployer.region}.amazonaws.com/endpoints/{endpoint_name}")
        logger.info(f"Dashboard URL: https://{deployer.region}.console.aws.amazon.com/cloudwatch/home?region={deployer.region}#dashboards:name={dashboard_name}")
        
        return endpoint_name
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise

if __name__ == '__main__':
    main() 
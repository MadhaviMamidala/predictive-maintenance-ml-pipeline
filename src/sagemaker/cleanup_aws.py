import boto3
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_aws_resources():
    try:
        # Initialize AWS clients
        sagemaker = boto3.client('sagemaker')
        s3 = boto3.client('s3')
        
        logger.info("Starting AWS cleanup process...")
        
        # Stop any running SageMaker endpoints
        try:
            endpoints = sagemaker.list_endpoints()
            for endpoint in endpoints['Endpoints']:
                if 'predictive-maintenance' in endpoint['EndpointName']:
                    logger.info(f"Deleting endpoint: {endpoint['EndpointName']}")
                    sagemaker.delete_endpoint(EndpointName=endpoint['EndpointName'])
        except ClientError as e:
            logger.error(f"Error cleaning up endpoints: {str(e)}")
        
        # Stop any running training jobs
        try:
            training_jobs = sagemaker.list_training_jobs()
            for job in training_jobs['TrainingJobSummaries']:
                if 'predictive-maintenance' in job['TrainingJobName']:
                    if job['TrainingJobStatus'] in ['InProgress', 'Starting']:
                        logger.info(f"Stopping training job: {job['TrainingJobName']}")
                        sagemaker.stop_training_job(TrainingJobName=job['TrainingJobName'])
        except ClientError as e:
            logger.error(f"Error cleaning up training jobs: {str(e)}")
        
        # Clean up S3 buckets (both old and new naming)
        try:
            buckets = s3.list_buckets()['Buckets']
            for bucket in buckets:
                if 'predictive-maintenance' in bucket['Name'].lower():
                    logger.info(f"Emptying and deleting bucket: {bucket['Name']}")
                    # First delete all objects in the bucket
                    paginator = s3.get_paginator('list_objects_v2')
                    for page in paginator.paginate(Bucket=bucket['Name']):
                        if 'Contents' in page:
                            objects = [{'Key': obj['Key']} for obj in page['Contents']]
                            s3.delete_objects(
                                Bucket=bucket['Name'],
                                Delete={'Objects': objects}
                            )
                    # Then delete the bucket
                    s3.delete_bucket(Bucket=bucket['Name'])
        except ClientError as e:
            logger.error(f"Error cleaning up S3 buckets: {str(e)}")
        
        logger.info("✅ AWS cleanup completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {str(e)}")

if __name__ == '__main__':
    cleanup_aws_resources() 
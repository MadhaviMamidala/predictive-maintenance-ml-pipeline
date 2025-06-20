import boto3
import logging
from pathlib import Path
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_sagemaker_project():
    try:
        # Initialize AWS clients
        s3 = boto3.client('s3')
        account_id = boto3.client('sts').get_caller_identity()['Account']
        region = boto3.session.Session().region_name
        
        # Create unique bucket name using account ID and madhu prefix
        bucket_name = f'madhu-predictive-maintenance-{account_id}'
        
        logger.info(f"Setting up project in region: {region}")
        
        # Create S3 bucket
        try:
            if region == 'us-east-1':
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            logger.info(f"✅ Created S3 bucket: {bucket_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                logger.info(f"✅ Using existing bucket: {bucket_name}")
            else:
                raise e
        
        # Create project directories in bucket
        directories = ['data', 'models', 'output']
        for dir_name in directories:
            s3.put_object(Bucket=bucket_name, Key=f'{dir_name}/')
        logger.info("✅ Created project directories in bucket")
        
        # Upload processed data if available
        data_path = Path('data/processed/processed_data.csv')
        if data_path.exists():
            s3.upload_file(
                str(data_path),
                bucket_name,
                'data/processed_data.csv'
            )
            logger.info("✅ Uploaded processed data to S3")
        else:
            logger.warning("⚠️ No processed data found to upload")
        
        # Create local models directory if it doesn't exist
        models_dir = Path('models')
        models_dir.mkdir(exist_ok=True)
        logger.info("✅ Created local models directory")
        
        logger.info(f"\nProject setup complete!")
        logger.info(f"S3 Bucket: {bucket_name}")
        logger.info(f"Region: {region}")
        
        return bucket_name
        
    except Exception as e:
        logger.error(f"❌ Error during project setup: {str(e)}")
        raise

if __name__ == '__main__':
    setup_sagemaker_project() 
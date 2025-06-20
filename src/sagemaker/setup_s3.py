import boto3
import logging
from pathlib import Path
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_s3():
    try:
        s3 = boto3.client('s3')
        bucket_name = 'predictive-maintenance-sagemaker'
        region = boto3.session.Session().region_name
        
        # Create bucket if it doesn't exist
        try:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
            logger.info(f"✅ Created S3 bucket: {bucket_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                logger.info(f"✅ Using existing S3 bucket: {bucket_name}")
            else:
                raise e
        
        # Upload processed data
        data_path = Path('data/processed/processed_data.csv')
        if data_path.exists():
            s3.upload_file(
                str(data_path),
                bucket_name,
                'data/processed_data.csv'
            )
            logger.info("✅ Uploaded processed data to S3")
        else:
            logger.error("❌ Processed data file not found")
            return False
        
        # Upload training code
        training_code = Path('src/sagemaker/train.py')
        if training_code.exists():
            s3.upload_file(
                str(training_code),
                bucket_name,
                'code/train.py'
            )
            logger.info("✅ Uploaded training code to S3")
        else:
            logger.error("❌ Training code file not found")
            return False
        
        logger.info(f"S3 setup complete. Bucket: {bucket_name}")
        return bucket_name
        
    except Exception as e:
        logger.error(f"❌ Error setting up S3: {str(e)}")
        return False

if __name__ == '__main__':
    setup_s3() 
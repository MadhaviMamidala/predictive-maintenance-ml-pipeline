import boto3
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_aws_connection():
    try:
        # Test AWS credentials by listing S3 buckets
        s3 = boto3.client('s3')
        s3.list_buckets()
        logger.info("✅ AWS credentials are valid and working")
        
        # Test SageMaker access
        sagemaker = boto3.client('sagemaker')
        sagemaker.list_training_jobs(MaxResults=1)
        logger.info("✅ SageMaker access confirmed")
        
        # Get the SageMaker execution role
        iam = boto3.client('iam')
        role = iam.get_role(RoleName='SageMakerExecutionRole')
        logger.info(f"✅ SageMaker execution role found: {role['Role']['Arn']}")
        
        return True
        
    except ClientError as e:
        if "AccessDenied" in str(e):
            logger.error("❌ AWS credentials are invalid or have insufficient permissions")
        elif "NoSuchEntity" in str(e):
            logger.error("❌ SageMaker execution role not found")
        else:
            logger.error(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_aws_connection() 
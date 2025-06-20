import boto3
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_aws_setup():
    try:
        # Check current AWS identity
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        logger.info("=== Current AWS Configuration ===")
        logger.info(f"Account ID: {identity['Account']}")
        logger.info(f"User ID: {identity['UserId']}")
        
        # Get current region
        session = boto3.session.Session()
        region = session.region_name
        logger.info(f"Current Region: {region}")
        
        # Check SageMaker access
        logger.info("\nChecking SageMaker permissions...")
        sagemaker = boto3.client('sagemaker')
        sagemaker.list_training_jobs(MaxResults=1)
        logger.info("✅ SageMaker access confirmed")
        
        # Check S3 access
        logger.info("\nChecking S3 permissions...")
        s3 = boto3.client('s3')
        s3.list_buckets()
        logger.info("✅ S3 access confirmed")
        
        # Check IAM access
        logger.info("\nChecking IAM permissions...")
        iam = boto3.client('iam')
        iam.get_user()
        logger.info("✅ IAM access confirmed")
        
        logger.info("\n✅ All required permissions are configured correctly!")
        return True
        
    except ClientError as e:
        if "AccessDenied" in str(e):
            logger.error(f"\n❌ Permission error: {str(e)}")
        else:
            logger.error(f"\n❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    verify_aws_setup() 
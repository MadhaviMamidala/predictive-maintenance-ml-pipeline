#!/usr/bin/env python3
"""
Script to set up SageMaker execution role with required permissions
"""

import boto3
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sagemaker_role():
    """Create SageMaker execution role with required permissions"""
    try:
        iam_client = boto3.client('iam')
        
        # Role name
        role_name = 'SageMakerExecutionRole'
        
        # Check if role already exists
        try:
            iam_client.get_role(RoleName=role_name)
            logger.info(f"Role {role_name} already exists")
            return f"arn:aws:iam::{boto3.client('sts').get_caller_identity()['Account']}:role/{role_name}"
        except iam_client.exceptions.NoSuchEntityException:
            pass
        
        # Trust policy for SageMaker
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "sagemaker.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        # Create role
        logger.info(f"Creating role: {role_name}")
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='SageMaker execution role for predictive maintenance project'
        )
        
        role_arn = response['Role']['Arn']
        logger.info(f"Role created: {role_arn}")
        
        # Attach required policies
        policies = [
            'AmazonSageMakerFullAccess',
            'AmazonS3FullAccess',
            'CloudWatchLogsFullAccess'
        ]
        
        for policy in policies:
            try:
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=f'arn:aws:iam::aws:policy/{policy}'
                )
                logger.info(f"Attached policy: {policy}")
            except Exception as e:
                logger.warning(f"Could not attach {policy}: {e}")
        
        # Create custom policy for specific permissions
        custom_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "sagemaker:*",
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListBucket",
                        "ecr:GetAuthorizationToken",
                        "ecr:BatchCheckLayerAvailability",
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:BatchGetImage",
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        # Create and attach custom policy
        custom_policy_name = 'SageMakerCustomPolicy'
        try:
            iam_client.create_policy(
                PolicyName=custom_policy_name,
                PolicyDocument=json.dumps(custom_policy),
                Description='Custom policy for SageMaker predictive maintenance'
            )
            
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=f'arn:aws:iam::{boto3.client("sts").get_caller_identity()["Account"]}:policy/{custom_policy_name}'
            )
            logger.info(f"Attached custom policy: {custom_policy_name}")
        except Exception as e:
            logger.warning(f"Could not create custom policy: {e}")
        
        return role_arn
        
    except Exception as e:
        logger.error(f"Error creating SageMaker role: {e}")
        raise

def update_aws_config(role_arn):
    """Update AWS config to use the SageMaker role"""
    try:
        # Get current user info
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        
        logger.info("AWS Configuration Instructions:")
        logger.info("=" * 50)
        logger.info(f"1. Your current AWS account: {identity['Account']}")
        logger.info(f"2. SageMaker role ARN: {role_arn}")
        logger.info("3. To use this role, you have two options:")
        logger.info("")
        logger.info("Option A: Update your AWS credentials file")
        logger.info("   Add this to ~/.aws/credentials:")
        logger.info(f"   [sagemaker]")
        logger.info(f"   role_arn = {role_arn}")
        logger.info(f"   source_profile = default")
        logger.info("")
        logger.info("Option B: Use the role in your SageMaker code")
        logger.info("   Update src/sagemaker/deploy.py to use:")
        logger.info(f"   role = '{role_arn}'")
        logger.info("")
        logger.info("4. Test the setup:")
        logger.info("   python test_sagemaker_setup.py")
        
    except Exception as e:
        logger.error(f"Error updating AWS config: {e}")

def main():
    """Main function"""
    print("🔧 SageMaker Role Setup")
    print("=" * 50)
    
    try:
        # Create SageMaker role
        role_arn = create_sagemaker_role()
        
        # Provide configuration instructions
        update_aws_config(role_arn)
        
        print("\n✅ SageMaker role setup completed!")
        print("Please follow the configuration instructions above.")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\nManual setup instructions:")
        print("1. Go to AWS IAM Console")
        print("2. Create a new role with SageMaker execution permissions")
        print("3. Attach the following policies:")
        print("   - AmazonSageMakerFullAccess")
        print("   - AmazonS3FullAccess")
        print("   - CloudWatchLogsFullAccess")
        print("4. Use the role ARN in your SageMaker code")

if __name__ == "__main__":
    main() 
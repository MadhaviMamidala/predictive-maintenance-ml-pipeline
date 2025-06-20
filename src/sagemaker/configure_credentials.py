import os
import sys
import boto3
import logging
from pathlib import Path
from configparser import ConfigParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def configure_aws_credentials():
    print("\n=== AWS Credentials Configuration ===")
    print("Please enter your AWS credentials:")
    
    access_key = input("AWS Access Key ID: ").strip()
    secret_key = input("AWS Secret Access Key: ").strip()
    region = input("AWS Region (e.g., us-east-1): ").strip()
    
    if not all([access_key, secret_key, region]):
        logger.error("❌ All fields are required!")
        return False
    
    try:
        # Create .aws directory if it doesn't exist
        aws_dir = Path.home() / '.aws'
        aws_dir.mkdir(exist_ok=True)
        
        # Create or update credentials file
        config = ConfigParser()
        credentials_file = aws_dir / 'credentials'
        
        if credentials_file.exists():
            config.read(credentials_file)
        
        if 'default' not in config:
            config.add_section('default')
        
        config['default']['aws_access_key_id'] = access_key
        config['default']['aws_secret_access_key'] = secret_key
        
        with open(credentials_file, 'w') as f:
            config.write(f)
        
        # Create or update config file
        config = ConfigParser()
        config_file = aws_dir / 'config'
        
        if config_file.exists():
            config.read(config_file)
        
        if 'default' not in config:
            config.add_section('default')
        
        config['default']['region'] = region
        
        with open(config_file, 'w') as f:
            config.write(f)
        
        # Test the credentials
        try:
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            
            logger.info("✅ AWS credentials configured successfully!")
            logger.info(f"Account ID: {identity['Account']}")
            logger.info(f"User ID: {identity['UserId']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to validate credentials: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error configuring credentials: {str(e)}")
        return False

if __name__ == '__main__':
    configure_aws_credentials() 
import boto3
from pathlib import Path

# Configuration
bucket_name = 'coredefender.madhu'
region = 'us-west-2'
model_path = Path('models/random_forest_model.joblib')
s3_key = 'models/random_forest_model.joblib'

# Upload model to S3
def upload_model():
    s3 = boto3.client('s3', region_name=region)
    print(f'Uploading {model_path} to s3://{bucket_name}/{s3_key} ...')
    s3.upload_file(str(model_path), bucket_name, s3_key)
    print('Upload complete.')

if __name__ == '__main__':
    upload_model() 
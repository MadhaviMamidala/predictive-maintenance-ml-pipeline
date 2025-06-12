import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# AWS Configuration
AWS_REGION = "us-east-1"
S3_BUCKET = "predictive-maintenance-ml"
S3_RAW_DATA_PATH = "raw_data"
S3_PROCESSED_DATA_PATH = "processed_data"
S3_MODEL_PATH = "models"

# SageMaker Configuration
SAGEMAKER_ROLE = "arn:aws:iam::<YOUR_ACCOUNT_ID>:role/SageMakerExecutionRole"
SAGEMAKER_INSTANCE_TYPE = "ml.m5.xlarge"
SAGEMAKER_INSTANCE_COUNT = 1

# Airflow Configuration
AIRFLOW_HOME = PROJECT_ROOT / "airflow"
AIRFLOW_DAGS_FOLDER = AIRFLOW_HOME / "dags"
AIRFLOW_LOGS_FOLDER = AIRFLOW_HOME / "logs"

# Monitoring Configuration
PROMETHEUS_PORT = 9090
GRAFANA_PORT = 3000

# Model Configuration
MODEL_NAME = "predictive-maintenance-model"
MODEL_VERSION = "1.0"
TRAINING_INSTANCE_TYPE = "ml.m5.xlarge"
ENDPOINT_INSTANCE_TYPE = "ml.m5.large"

# Security Configuration
ENCRYPTION_KEY_ID = "<YOUR_KMS_KEY_ID>"
VPC_ID = "<YOUR_VPC_ID>"
SUBNET_IDS = ["<YOUR_SUBNET_ID_1>", "<YOUR_SUBNET_ID_2>"]

# Create necessary directories
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, AIRFLOW_HOME, AIRFLOW_DAGS_FOLDER, AIRFLOW_LOGS_FOLDER]:
    directory.mkdir(parents=True, exist_ok=True)

# Environment variables
os.environ["AWS_DEFAULT_REGION"] = AWS_REGION
os.environ["AIRFLOW_HOME"] = str(AIRFLOW_HOME) 
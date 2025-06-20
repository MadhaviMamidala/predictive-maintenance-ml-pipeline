# Predictive Maintenance ML Pipeline

## Project Overview
This project implements an end-to-end machine learning pipeline for predictive maintenance of industrial equipment using AWS services. The goal is to predict equipment failures before they occur, enabling proactive maintenance and reducing downtime and costs.

## Architecture
![Architecture Diagram](docs/architecture.png)

**Explanation:**
- The architecture is modular and scalable, leveraging AWS managed services (S3, Glue, SageMaker, Airflow, Prometheus, Grafana, etc.).
- Each stage (ETL, validation, modeling, deployment, monitoring) is decoupled for flexibility and maintainability.
- Security and monitoring are integrated from the start.

## Use Case and Motivation
- **Use Case:** Predictive maintenance for industrial equipment.
- **Why:** Unplanned equipment failures are costly and disruptive. Predicting failures enables proactive maintenance, saving costs and improving safety.
- **Example:** Predicting when a factory motor will fail based on sensor data (vibration, voltage, etc.).

## Dataset
- **File:** `data/predictive_maintenance_full.csv`
- **Description:** Merged dataset containing telemetry, failures, errors, maintenance, and machine info.
- **Columns:**
  - `datetime`, `machineID`, `volt`, `rotate`, `pressure`, `vibration`, `errorID`, `failure`, `comp_maint`, `age`, `model`
- **Why merged:** Simplifies the pipeline, reduces join/merge errors, and ensures all features are available for each record.

## Current Project Status ✅

### Completed Components:
1. ✅ **Data Generation**: 200-row synthetic dataset with realistic patterns
2. ✅ **ETL Pipeline**: Advanced data processing with schema validation, quality checks, and drift detection
3. ✅ **Model Training & Comparison**: Random Forest, XGBoost, Logistic Regression with comprehensive evaluation
4. ✅ **Advanced Analytics**: Feature importance, learning curves, calibration curves, statistical significance tests
5. ✅ **Model API**: FastAPI-based REST API for real-time predictions
6. ✅ **Containerization**: Docker support for deployment
7. ✅ **AWS SageMaker Deployment**: Complete deployment pipeline with training, model creation, and endpoint deployment

### Model Performance:
- **Best Model**: Random Forest
- **Accuracy**: ~85%
- **Key Features**: vibration, age, pressure, volt, rotate
- **Statistical Significance**: All models show significant performance differences

## Step-by-Step Instructions

### 1. Data Preparation
- Clean and preprocess the dataset using `src/etl/etl_cleaning.py`.
- Output: `data/processed/processed_data.csv`

### 2. Data Validation
- Validate the processed data using Great Expectations (`src/validation/validate_data.py`).
- Ensures schema, types, missing values, and value ranges are correct.

### 3. Model Training
- Train and compare models using `src/model_comparison_local.py`.
- Features: `volt`, `rotate`, `pressure`, `vibration`, `age`, `machineID`, `model`
- Target: Binary flag for failure
- Output: `models/best_model.pkl` and comprehensive evaluation metrics

### 4. Model API Deployment 🚀

#### Option A: Local Development
```bash
# Start the API
python start_api.py

# Test the API
python src/api/test_api.py
```

#### Option B: Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -f docker/Dockerfile.api -t predictive-maintenance-api .
docker run -p 8000:8000 predictive-maintenance-api
```

#### API Endpoints:
- **Health Check**: `GET /health`
- **Single Prediction**: `POST /predict`
- **Batch Prediction**: `POST /batch-predict`
- **Model Info**: `GET /model-info`
- **API Documentation**: `http://localhost:8000/docs`

### 5. AWS SageMaker Deployment ☁️

#### Prerequisites:
1. **AWS Account Setup**: Configure AWS CLI and credentials
2. **SageMaker Execution Role**: Create IAM role with required permissions
3. **S3 Bucket**: Ensure `coredefender.madhu` bucket exists

#### Deployment Steps:
```bash
# 1. Test SageMaker setup
python test_sagemaker_setup.py

# 2. Install SageMaker dependencies
pip install -r requirements-sagemaker.txt

# 3. Deploy to SageMaker
python src/sagemaker/deploy.py
```

#### What the deployment does:
- ✅ Uploads training data to S3
- ✅ Creates and runs SageMaker training job
- ✅ Creates SageMaker model from training artifacts
- ✅ Deploys real-time inference endpoint
- ✅ Tests the endpoint with sample data

#### SageMaker Resources Created:
- **Training Job**: ml.m5.large instance (~$0.115/hour)
- **Model**: Stored in S3 with custom inference code
- **Endpoint**: ml.t2.medium instance (~$0.046/hour) with auto-scaling

### 6. Model Artifact Upload
- Upload the trained model to S3 using `src/deployment/upload_to_s3.py`.
- S3 bucket: `coredefender.madhu` (region: `us-west-2`)

### 7. Monitoring & Security
- Integrate Prometheus, Grafana, and CloudWatch for monitoring.
- Use IAM, KMS, Security Groups, and VPC for security.

## Technology Choices and Rationale
- **AWS Services:** Chosen for scalability, managed infrastructure, and integration. Alternatives like Azure and GCP are also strong, but AWS is most widely adopted in industry.
- **Great Expectations:** Open-source, Python integration, rich validation features. Alternatives: Pandera, Deequ.
- **Random Forest:** Robust, interpretable baseline for tabular data. Alternatives: XGBoost, neural networks, logistic regression.
- **FastAPI:** Modern, fast, automatic documentation. Alternatives: Flask, Django REST.
- **Docker:** Containerization for consistent deployment. Alternatives: Kubernetes, serverless.
- **AWS SageMaker:** Managed ML platform with built-in training and deployment. Alternatives: Azure ML, Google AI Platform.
- **Single merged dataset:** Simplifies pipeline, reduces errors, and supports all ML tasks. Alternatives: separate files for modular pipelines.
- **Security and monitoring:** Built-in from the start for production readiness. AWS-native tools are best for AWS-based pipelines.

## How to Run Each Step
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Clean and preprocess data:**
   ```bash
   python src/etl/etl_cleaning.py
   ```
3. **Validate data:**
   ```bash
   python src/validation/validate_data.py
   ```
4. **Train and compare models:**
   ```bash
   python src/model_comparison_local.py
   ```
5. **Start the API:**
   ```bash
   python start_api.py
   ```
6. **Test the API:**
   ```bash
   python src/api/test_api.py
   ```
7. **Deploy to SageMaker:**
   ```bash
   python test_sagemaker_setup.py  # Verify setup
   python src/sagemaker/deploy.py   # Deploy
   ```
8. **Upload model to S3:**
   ```bash
   python src/deployment/upload_to_s3.py
   ```

## Next Steps 🎯
1. **Production Monitoring**: Set up CloudWatch dashboards and alarms
2. **CI/CD Pipeline**: GitHub Actions for automated testing and deployment
3. **Advanced Features**: A/B testing, model versioning, automated retraining
4. **Security Hardening**: API authentication, rate limiting, input sanitization
5. **Cost Optimization**: Spot instances, auto-scaling, resource monitoring

## Contribution Guidelines
- Fork the repository and create a feature branch for your changes.
- Write clear, descriptive commit messages.
- Open a pull request for review.
- Follow PEP8 and Python best practices.

## License
This project is licensed under the MIT License. 
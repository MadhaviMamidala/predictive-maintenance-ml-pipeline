# Standup Report: Predictive Maintenance ML Pipeline

## 1. Project Planning & Architecture
- **Use Case:** Predictive maintenance for industrial equipment to reduce downtime and optimize maintenance schedules.
  - **Definition:** Predictive maintenance uses data and ML to predict when equipment will fail, allowing for proactive repairs.
  - **Example:** Predicting when a factory motor will fail based on vibration and temperature sensors.
- **Why:** Unplanned equipment failures are costly; predicting failures enables proactive maintenance, saving costs and improving safety.
- **Architecture:**
  - **Alternatives:** On-premise solutions, other cloud providers (Azure, GCP), monolithic scripts.
  - **Chosen:** Modular, scalable AWS-based pipeline (S3, Glue, SageMaker, Airflow, Prometheus, Grafana, etc.).
  - **Why:** AWS offers managed, scalable, and integrated services, reducing operational overhead and increasing reliability.
  - **Definition:**
    - **Modular:** Each component (ETL, validation, modeling, deployment) is independent and replaceable.
    - **Scalable:** Can handle increasing data and compute needs without major redesign.
    - **Security and Monitoring:** Built-in from the start for production readiness.

## 2. Dataset Preparation
- **Dataset:** Merged, realistic predictive maintenance dataset (`predictive_maintenance_full.csv`).
  - **Alternatives:** Use separate files for telemetry, failures, errors, maintenance, and machine info.
  - **Why merged:** Simplifies pipeline, reduces join/merge errors, and ensures all features are available for each record.
  - **Definition:**
    - **Telemetry:** Time-series sensor data (volt, rotate, pressure, vibration).
    - **Failures:** Records of component failures.
    - **Errors:** Machine error events.
    - **Maintenance:** Preventive maintenance actions.
    - **Machine metadata:** Age and model of each machine.
  - **Example:**
    - `datetime,machineID,volt,rotate,pressure,vibration,errorID,failure,comp_maint,age,model`
- **Selection Reason:**
  - Covers all relevant signals for predictive maintenance.
  - Structure supports both supervised and unsupervised ML.

## 3. ETL (Extract, Transform, Load)
- **Script:** `src/etl/etl_cleaning.py`
- **Alternatives:** Manual cleaning in Excel, SQL-based ETL, other ETL tools (Talend, Informatica).
- **Why Python script:**
  - Automates repeatable data prep, integrates with ML pipeline, and is easy to maintain and version.
- **Definition:**
  - **ETL:** Process of extracting data from source, transforming it (cleaning, type conversion), and loading it for analysis.
- **Example:**
  - Convert `volt` column to numeric, fill missing `model` with 'unknown', drop rows with missing `machineID`.

## 4. Data Validation
- **Tool:** Great Expectations
  - **Alternatives:** Custom Python validation, Pandera, Deequ (for Spark), manual checks.
  - **Why Great Expectations:**
    - Open-source, widely adopted, integrates with Python and data pipelines, provides rich validation and reporting.
  - **Definition:**
    - **Data validation:** Ensuring data meets quality standards (schema, types, ranges, missing values).
  - **Example:**
    - Check that `volt` is always between 100 and 300, and `datetime` is never null.

## 5. Model Training
- **Model:** Random Forest Classifier (scikit-learn)
  - **Alternatives:**
    - **XGBoost:** Often better for tabular data, but more complex and sensitive to hyperparameters.
    - **Neural Networks:** Powerful, but require more data and tuning, less interpretable.
    - **Logistic Regression:** Simple, interpretable, but may underfit complex patterns.
  - **Why Random Forest:**
    - Handles tabular, mixed-type data well
    - Robust to outliers and missing values
    - Provides feature importance for interpretability
    - Less prone to overfitting than single trees
    - Good baseline for industrial ML
  - **Definition:**
    - **Random Forest:** An ensemble of decision trees, each trained on a random subset of data and features, and outputs the majority vote (classification) or average (regression).
  - **Example:**
    - Predicting machine failure using sensor readings and machine metadata.
- **Features Used:** `volt`, `rotate`, `pressure`, `vibration`, `age`, `machineID`, `model`
- **Target:** Binary flag for failure (1 if failure, else 0)
- **Why Random Forest:**
  - Handles tabular, mixed-type data well
  - Robust to outliers and missing values
  - Provides feature importance for interpretability
  - Less prone to overfitting than single trees
- **Hyperparameters:**
  - **n_estimators:** Number of trees in the forest. More trees = more stable, but slower.
  - **max_depth:** Maximum depth of each tree. Controls overfitting.
  - **min_samples_split:** Minimum samples required to split a node. Higher = less overfitting.
  - **min_samples_leaf:** Minimum samples at a leaf node. Higher = less overfitting.
  - **max_features:** Number of features to consider at each split. 'sqrt' is standard for classification.
  - **bootstrap:** Whether to use bootstrap samples. True = standard bagging.
  - **random_state:** Seed for reproducibility.
  - **Example:**
    ```python
    RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_split=5, min_samples_leaf=2, max_features='sqrt', bootstrap=True, random_state=42)
    ```

## 6. Model Artifact Upload
- **Script:** `src/deployment/upload_to_s3.py`
- **Alternatives:** Manual upload via AWS Console, AWS CLI, or other SDKs.
- **Why boto3 script:**
  - Automates the process, integrates with pipeline, and is repeatable.
- **Definition:**
  - **S3:** Amazon Simple Storage Service, used for storing and retrieving any amount of data.
- **Example:**
  - Uploading `random_forest_model.joblib` to `s3://coredefender.madhu/models/random_forest_model.joblib`.

## 7. Next Steps
- **SageMaker Deployment:**
  - **Alternatives:** Deploy locally (Flask API), use other cloud ML services (Azure ML, GCP AI Platform).
  - **Why SageMaker:**
    - Managed, scalable, integrates with S3 and other AWS services, supports real-time endpoints.
  - **Definition:**
    - **SageMaker:** AWS service for building, training, and deploying ML models at scale.
  - **Example:**
    - Deploying the trained Random Forest as a real-time endpoint for API-based predictions.
- **Monitoring & Security:**
  - **Prometheus & Grafana:** Open-source tools for metrics and dashboards.
  - **CloudWatch:** AWS-native logging and alerting.
  - **IAM/KMS/Security Groups/VPC:** AWS security best practices for access control, encryption, and network isolation.
- **Documentation:**
  - All steps, scripts, and design decisions are documented in README and this standup report.

---

## **Reasoning for Technology and Design Choices**
- **AWS Services:** Chosen for scalability, managed infrastructure, and integration. Alternatives like Azure and GCP are also strong, but AWS is most widely adopted in industry.
- **Great Expectations:** Chosen for its open-source community, Python integration, and rich validation features. Alternatives like Pandera or Deequ are good for specific use cases (e.g., Spark).
- **Random Forest:** Chosen as a robust, interpretable baseline. XGBoost or neural networks can be used for further improvement if needed.
- **Single merged dataset:** Simplifies pipeline, reduces errors, and supports all ML tasks. Separate files can be used for more complex, modular pipelines.
- **Security and monitoring:** Built-in from the start for production readiness. Alternatives exist, but AWS-native tools are best for AWS-based pipelines.

---

**This report can be shared in standups or reviews to communicate project progress, design rationale, and next steps.** 
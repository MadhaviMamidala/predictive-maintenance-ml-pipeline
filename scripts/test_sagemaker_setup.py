#!/usr/bin/env python3
"""
Test script to verify SageMaker setup and dependencies
"""

import sys
import importlib
import boto3
import json
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'boto3',
        'sagemaker',
        'sklearn',
        'pandas',
        'numpy',
        'joblib'
    ]
    
    failed_imports = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {failed_imports}")
        print("Please install missing packages: pip install -r requirements-sagemaker.txt")
        return False
    
    print("✅ All packages imported successfully")
    return True

def test_aws_credentials():
    """Test AWS credentials and permissions"""
    print("\n🔍 Testing AWS credentials...")
    
    try:
        # Test basic AWS access
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials valid")
        print(f"   Account: {identity['Account']}")
        print(f"   User: {identity['Arn']}")
        
        # Test SageMaker access
        sagemaker = boto3.client('sagemaker')
        sagemaker.list_training_jobs(MaxResults=1)
        print("✅ SageMaker access confirmed")
        
        # Test S3 access
        s3 = boto3.client('s3')
        s3.list_buckets()
        print("✅ S3 access confirmed")
        
        return True
        
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        print("Please configure AWS credentials: aws configure")
        return False

def test_sagemaker_session():
    """Test SageMaker session creation"""
    print("\n🔍 Testing SageMaker session...")
    
    try:
        import sagemaker
        from sagemaker import get_execution_role
        
        session = sagemaker.Session()
        role = get_execution_role()
        
        print(f"✅ SageMaker session created")
        print(f"   Region: {session.boto_region_name}")
        print(f"   Role: {role}")
        
        return True
        
    except Exception as e:
        print(f"❌ SageMaker session error: {e}")
        print("Please ensure you have a SageMaker execution role")
        return False

def test_data_files():
    """Test if required data files exist"""
    print("\n🔍 Testing data files...")
    
    required_files = [
        "data/processed/processed_data.csv",
        "models/random_forest_model.joblib",
        "model_metrics.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        print("Please run the ETL and model training pipelines first")
        return False
    
    print("✅ All required files found")
    return True

def test_sagemaker_scripts():
    """Test if SageMaker scripts exist"""
    print("\n🔍 Testing SageMaker scripts...")
    
    required_scripts = [
        "src/sagemaker/train.py",
        "src/sagemaker/inference.py",
        "src/sagemaker/deploy.py"
    ]
    
    missing_scripts = []
    for script_path in required_scripts:
        if Path(script_path).exists():
            print(f"✅ {script_path}")
        else:
            print(f"❌ {script_path}")
            missing_scripts.append(script_path)
    
    if missing_scripts:
        print(f"\n❌ Missing scripts: {missing_scripts}")
        return False
    
    print("✅ All SageMaker scripts found")
    return True

def test_data_format():
    """Test if processed data has the correct format"""
    print("\n🔍 Testing data format...")
    
    try:
        import pandas as pd
        
        df = pd.read_csv("data/processed/processed_data.csv")
        
        # Check required columns
        required_columns = ['volt', 'rotate', 'pressure', 'vibration', 'age', 'failure']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        
        print(f"✅ Data format correct")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        # Check for missing values in key columns
        key_columns = ['volt', 'rotate', 'pressure', 'vibration', 'age']
        missing_counts = df[key_columns].isnull().sum()
        
        if missing_counts.sum() > 0:
            print(f"⚠️  Missing values in key columns: {missing_counts.to_dict()}")
        else:
            print("✅ No missing values in key columns")
        
        return True
        
    except Exception as e:
        print(f"❌ Data format error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SageMaker Setup Verification")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_aws_credentials,
        test_sagemaker_session,
        test_data_files,
        test_sagemaker_scripts,
        test_data_format
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for SageMaker deployment.")
        print("\nNext steps:")
        print("1. Run: python src/sagemaker/deploy.py")
        print("2. Monitor deployment in AWS SageMaker console")
        print("3. Test the deployed endpoint")
    else:
        print("⚠️  Some tests failed. Please fix the issues before deployment.")
        print("\nCommon fixes:")
        print("1. Install dependencies: pip install -r requirements-sagemaker.txt")
        print("2. Configure AWS: aws configure")
        print("3. Run ETL pipeline: python src/etl/etl_cleaning.py")
        print("4. Train models: python src/model_comparison_local.py")

if __name__ == "__main__":
    main() 
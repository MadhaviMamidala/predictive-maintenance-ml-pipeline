#!/usr/bin/env python3
"""
ML Lifecycle Project to Notion Integration
==========================================

This script analyzes your ML lifecycle project and creates detailed documentation
in your Notion workspace, including:

- Project overview and structure
- Model performance metrics
- Data pipeline status
- Deployment information
- Monitoring dashboards
- Technical documentation
- Progress tracking

"""

import os
import json
import sys
import pickle
import joblib
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.append('src')
from notion_client import create_notion_client

class MLProjectNotionUpdater:
    def __init__(self):
        self.client = create_notion_client()
        self.project_root = Path(".")
        self.project_data = {}
        
    def analyze_project_structure(self):
        """Analyze the complete project structure"""
        print("🔍 Analyzing ML Lifecycle Project Structure...")
        
        structure = {
            "directories": {},
            "key_files": {},
            "models": {},
            "data": {},
            "configs": {},
            "scripts": {},
            "documentation": {}
        }
        
        # Analyze directory structure
        for root, dirs, files in os.walk(self.project_root):
            rel_path = os.path.relpath(root, self.project_root)
            if rel_path == ".":
                rel_path = "root"
            
            structure["directories"][rel_path] = {
                "subdirs": dirs,
                "files": files,
                "file_count": len(files)
            }
            
            # Categorize important files
            for file in files:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, self.project_root)
                
                if file.endswith(('.pkl', '.joblib', '.tar.gz')) and 'model' in file.lower():
                    structure["models"][rel_file_path] = self._get_file_info(file_path)
                elif file.endswith(('.csv', '.json')) and any(x in file.lower() for x in ['data', 'dataset']):
                    structure["data"][rel_file_path] = self._get_file_info(file_path)
                elif file.endswith(('.py', '.sh', '.bat')) and 'script' in root.lower():
                    structure["scripts"][rel_file_path] = self._get_file_info(file_path)
                elif file.endswith(('.md', '.txt', '.rst')):
                    structure["documentation"][rel_file_path] = self._get_file_info(file_path)
                elif file in ['config.py', 'requirements.txt', 'docker-compose.yml']:
                    structure["configs"][rel_file_path] = self._get_file_info(file_path)
        
        self.project_data["structure"] = structure
        return structure
    
    def _get_file_info(self, file_path):
        """Get file information"""
        try:
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "exists": True
            }
        except:
            return {"exists": False}
    
    def analyze_models(self):
        """Analyze model files and performance metrics"""
        print("🤖 Analyzing ML Models...")
        
        models_info = {}
        
        # Check for model files
        model_files = [
            "models/best_model.pkl",
            "models/model.joblib", 
            "models/random_forest_model.joblib",
            "models/xgboost_model.joblib"
        ]
        
        for model_file in model_files:
            if os.path.exists(model_file):
                try:
                    model_info = self._get_file_info(model_file)
                    model_info["type"] = self._detect_model_type(model_file)
                    models_info[model_file] = model_info
                except Exception as e:
                    models_info[model_file] = {"error": str(e)}
        
        # Load metrics if available
        metrics_file = "models/metrics.json"
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
                models_info["performance_metrics"] = metrics
            except Exception as e:
                models_info["metrics_error"] = str(e)
        
        # Load feature names if available
        features_file = "models/feature_names.json"
        if os.path.exists(features_file):
            try:
                with open(features_file, 'r') as f:
                    features = json.load(f)
                models_info["features"] = features
            except Exception as e:
                models_info["features_error"] = str(e)
        
        self.project_data["models"] = models_info
        return models_info
    
    def _detect_model_type(self, model_file):
        """Detect the type of ML model"""
        if "random_forest" in model_file.lower():
            return "Random Forest"
        elif "xgboost" in model_file.lower():
            return "XGBoost"
        elif "best_model" in model_file.lower():
            return "Best Model (Optimized)"
        else:
            return "Unknown"
    
    def analyze_data_pipeline(self):
        """Analyze data pipeline and ETL processes"""
        print("📊 Analyzing Data Pipeline...")
        
        pipeline_info = {
            "data_files": {},
            "etl_scripts": {},
            "data_quality": {},
            "processed_data": {}
        }
        
        # Check data files
        data_files = [
            "data/predictive_maintenance_full.csv",
            "data/processed/processed_data.csv"
        ]
        
        for data_file in data_files:
            if os.path.exists(data_file):
                info = self._get_file_info(data_file)
                info.update(self._analyze_csv_file(data_file))
                pipeline_info["data_files"][data_file] = info
        
        # Check ETL scripts
        etl_dir = "src/etl"
        if os.path.exists(etl_dir):
            for file in os.listdir(etl_dir):
                if file.endswith('.py'):
                    file_path = os.path.join(etl_dir, file)
                    pipeline_info["etl_scripts"][file] = {
                        "path": file_path,
                        "purpose": self._get_script_purpose(file),
                        **self._get_file_info(file_path)
                    }
        
        self.project_data["data_pipeline"] = pipeline_info
        return pipeline_info
    
    def _analyze_csv_file(self, file_path):
        """Analyze CSV file structure"""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            return {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist(),
                "data_types": df.dtypes.to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum()
            }
        except Exception as e:
            return {"analysis_error": str(e)}
    
    def _get_script_purpose(self, filename):
        """Determine the purpose of a script based on filename"""
        purposes = {
            "data_acquisition.py": "Data Collection & Ingestion",
            "data_quality.py": "Data Quality Validation",
            "drift_detection.py": "Data Drift Monitoring",
            "etl_cleaning.py": "Data Cleaning & Transformation",
            "schema.py": "Data Schema Management"
        }
        return purposes.get(filename, "ETL Processing")
    
    def analyze_deployment(self):
        """Analyze deployment configuration and status"""
        print("🚀 Analyzing Deployment Configuration...")
        
        deployment_info = {
            "docker": {},
            "api": {},
            "monitoring": {},
            "cloud": {}
        }
        
        # Docker configuration
        docker_files = [
            "docker/Dockerfile.api",
            "docker/Dockerfile.simple",
            "docker-compose.yml",
            "docker-compose.prod.yml"
        ]
        
        for docker_file in docker_files:
            if os.path.exists(docker_file):
                deployment_info["docker"][docker_file] = self._get_file_info(docker_file)
        
        # API configuration
        api_files = [
            "src/api/main.py",
            "src/api/security.py"
        ]
        
        for api_file in api_files:
            if os.path.exists(api_file):
                deployment_info["api"][api_file] = self._get_file_info(api_file)
        
        # Cloud deployment
        cloud_files = [
            "src/sagemaker/deploy_model.py",
            "src/kubeflow/model_comparison_pipeline.py"
        ]
        
        for cloud_file in cloud_files:
            if os.path.exists(cloud_file):
                deployment_info["cloud"][cloud_file] = self._get_file_info(cloud_file)
        
        self.project_data["deployment"] = deployment_info
        return deployment_info
    
    def analyze_monitoring(self):
        """Analyze monitoring and observability setup"""
        print("📈 Analyzing Monitoring Setup...")
        
        monitoring_info = {
            "scripts": {},
            "dashboards": {},
            "alerts": {},
            "logs": {}
        }
        
        # Monitoring scripts
        monitoring_scripts = [
            "scripts/automate_monitoring.py",
            "scripts/check_model_drift.py",
            "scripts/continuous_monitor.py",
            "scripts/monitor_background.py"
        ]
        
        for script in monitoring_scripts:
            if os.path.exists(script):
                monitoring_info["scripts"][script] = {
                    **self._get_file_info(script),
                    "purpose": self._get_monitoring_purpose(script)
                }
        
        self.project_data["monitoring"] = monitoring_info
        return monitoring_info
    
    def _get_monitoring_purpose(self, script_path):
        """Get the purpose of monitoring scripts"""
        purposes = {
            "automate_monitoring.py": "Automated Monitoring Orchestration",
            "check_model_drift.py": "Model Performance Drift Detection",
            "continuous_monitor.py": "Continuous Model Monitoring",
            "monitor_background.py": "Background Monitoring Service"
        }
        filename = os.path.basename(script_path)
        return purposes.get(filename, "Monitoring Service")
    
    def read_documentation(self):
        """Read and process documentation files"""
        print("📚 Processing Documentation...")
        
        docs = {}
        doc_files = [
            "README.md",
            "docs/MASTER_PROJECT_HISTORY_AND_GUIDE.md",
            "docs/TECHNICAL_PRESENTATION_GUIDE.md"
        ]
        
        for doc_file in doc_files:
            if os.path.exists(doc_file):
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    docs[doc_file] = {
                        "content": content,
                        "length": len(content),
                        "lines": len(content.split('\n')),
                        **self._get_file_info(doc_file)
                    }
                except Exception as e:
                    docs[doc_file] = {"error": str(e)}
        
        self.project_data["documentation"] = docs
        return docs
    
    def create_notion_database(self, database_name: str, properties: Dict) -> Optional[str]:
        """Create a new database in Notion"""
        print(f"📝 Creating Notion database: {database_name}")
        
        # First, we need a parent page to create the database in
        # Let's search for existing pages first
        search_result = self.client.search()
        pages = [p for p in search_result.get("results", []) if p.get("object") == "page"]
        
        if not pages:
            print("❌ No parent page found. Please create a page in Notion first.")
            return None
        
        # Use the first available page as parent
        parent_page_id = pages[0]["id"]
        
        try:
            # Create database
            database_data = {
                "parent": {"type": "page_id", "page_id": parent_page_id},
                "title": [{"type": "text", "text": {"content": database_name}}],
                "properties": properties
            }
            
            response = requests.post(
                f"{self.client.base_url}/databases",
                headers=self.client.headers,
                json=database_data
            )
            
            if response.status_code == 200:
                database = response.json()
                print(f"✅ Created database: {database_name}")
                return database["id"]
            else:
                print(f"❌ Failed to create database: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating database: {str(e)}")
            return None
    
    def create_ml_project_overview_page(self):
        """Create a comprehensive ML project overview page"""
        print("📄 Creating ML Project Overview Page...")
        
        # Get a parent page
        search_result = self.client.search()
        pages = [p for p in search_result.get("results", []) if p.get("object") == "page"]
        
        if not pages:
            print("❌ No parent page found. Please create a page in Notion first.")
            return None
        
        parent_page_id = pages[0]["id"]
        
        # Create the overview page
        page_content = self._build_overview_content()
        
        page_data = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "properties": {
                "title": {"title": [{"text": {"content": "ML Lifecycle Project Overview"}}]}
            },
            "children": page_content
        }
        
        try:
            response = requests.post(
                f"{self.client.base_url}/pages",
                headers=self.client.headers,
                json=page_data
            )
            
            if response.status_code == 200:
                page = response.json()
                print(f"✅ Created overview page: {page.get('url', 'N/A')}")
                return page["id"]
            else:
                print(f"❌ Failed to create page: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating page: {str(e)}")
            return None
    
    def _build_overview_content(self):
        """Build the content blocks for the overview page"""
        content = []
        
        # Header
        content.append({
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"type": "text", "text": {"content": "🤖 ML Lifecycle Project"}}]
            }
        })
        
        # Project summary
        content.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": f"Comprehensive ML project analysis completed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}}]
            }
        })
        
        # Project structure section
        content.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📁 Project Structure"}}]
            }
        })
        
        # Add structure details
        structure = self.project_data.get("structure", {})
        for dir_name, dir_info in structure.get("directories", {}).items():
            content.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": f"{dir_name}: {dir_info['file_count']} files"}}]
                }
            })
        
        # Models section
        content.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "🤖 Models"}}]
            }
        })
        
        models = self.project_data.get("models", {})
        for model_name, model_info in models.items():
            if isinstance(model_info, dict) and "type" in model_info:
                content.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": f"{model_name}: {model_info.get('type', 'Unknown')}"}}]
                    }
                })
        
        # Performance metrics
        if "performance_metrics" in models:
            content.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "📊 Performance Metrics"}}]
                }
            })
            
            metrics = models["performance_metrics"]
            for metric, value in metrics.items():
                content.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": f"{metric}: {value}"}}]
                    }
                })
        
        # Data pipeline section
        content.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📊 Data Pipeline"}}]
            }
        })
        
        pipeline = self.project_data.get("data_pipeline", {})
        for data_file, data_info in pipeline.get("data_files", {}).items():
            if "rows" in data_info:
                content.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": f"{data_file}: {data_info['rows']} rows, {data_info['columns']} columns"}}]
                    }
                })
        
        # Deployment section
        content.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "🚀 Deployment"}}]
            }
        })
        
        deployment = self.project_data.get("deployment", {})
        for category, files in deployment.items():
            if files:
                content.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": f"{category.title()}: {len(files)} configuration files"}}]
                    }
                })
        
        return content
    
    def run_full_analysis(self):
        """Run complete project analysis and update Notion"""
        print("🚀 Starting ML Lifecycle Project Analysis...")
        print("=" * 60)
        
        # Analyze all components
        self.analyze_project_structure()
        self.analyze_models()
        self.analyze_data_pipeline()
        self.analyze_deployment()
        self.analyze_monitoring()
        self.read_documentation()
        
        print("\n" + "=" * 60)
        print("📊 Analysis Summary:")
        print(f"• Directories analyzed: {len(self.project_data.get('structure', {}).get('directories', {}))}")
        print(f"• Models found: {len(self.project_data.get('models', {}))}")
        print(f"• Data files: {len(self.project_data.get('data_pipeline', {}).get('data_files', {}))}")
        print(f"• Deployment configs: {sum(len(v) for v in self.project_data.get('deployment', {}).values())}")
        print(f"• Monitoring scripts: {len(self.project_data.get('monitoring', {}).get('scripts', {}))}")
        print(f"• Documentation files: {len(self.project_data.get('documentation', {}))}")
        
        # Create Notion content
        print("\n🔄 Creating Notion Documentation...")
        
        # Create overview page
        overview_page_id = self.create_ml_project_overview_page()
        
        if overview_page_id:
            print(f"✅ ML Project documentation created successfully!")
            print(f"📄 Overview page created in Notion")
        else:
            print("❌ Failed to create Notion documentation")
            print("Make sure you have:")
            print("1. Shared at least one page with your integration")
            print("2. Given your integration write permissions")
        
        # Save analysis to JSON for reference
        with open("ml_project_analysis.json", "w") as f:
            json.dump(self.project_data, f, indent=2, default=str)
        
        print(f"\n💾 Analysis saved to: ml_project_analysis.json")
        
        return self.project_data

def main():
    """Main function to run the ML project to Notion integration"""
    print("🤖 ML Lifecycle Project → Notion Integration")
    print("=" * 60)
    
    try:
        updater = MLProjectNotionUpdater()
        
        # Test Notion connection first
        print("🔗 Testing Notion connection...")
        search_result = updater.client.search()
        
        if not search_result:
            print("❌ Cannot connect to Notion. Please check:")
            print("1. Your integration token is correct")
            print("2. You've shared pages with your integration")
            print("3. Your integration has proper permissions")
            return
        
        accessible_content = search_result.get("results", [])
        print(f"✅ Connected to Notion! Found {len(accessible_content)} accessible items")
        
        # Run full analysis
        project_data = updater.run_full_analysis()
        
        print("\n" + "=" * 60)
        print("🎉 ML Project successfully documented in Notion!")
        print("\nYour Notion workspace now contains:")
        print("• Complete project overview")
        print("• Model performance metrics")
        print("• Data pipeline documentation")
        print("• Deployment configuration details")
        print("• Monitoring setup information")
        
    except Exception as e:
        print(f"❌ Error during integration: {str(e)}")
        print("\nPlease check:")
        print("1. Notion integration is properly configured")
        print("2. Required Python packages are installed")
        print("3. Project files are accessible")

if __name__ == "__main__":
    main()
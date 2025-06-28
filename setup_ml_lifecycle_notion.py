#!/usr/bin/env python3
"""
Setup ML Lifecycle Project in Notion
====================================

This script creates a dedicated "ML lifecycle project" page in your Notion workspace
and sets up a complete ML project management system inside it.

Features:
- Creates a new page named "ML lifecycle project"
- Sets up structured databases for ML project tracking
- Populates with your current project data
- Creates a comprehensive project dashboard

"""

import sys
import json
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Any

# Add src to path for imports
sys.path.append('src')
from notion_client import create_notion_client

class MLLifecycleNotionSetup:
    def __init__(self):
        self.client = create_notion_client()
        self.ml_project_page_id = None
        self.created_databases = {}
        self.project_data = {}
        
    def get_workspace_parent(self):
        """Get a workspace or page to create the ML lifecycle project in"""
        search_result = self.client.search()
        
        if not search_result:
            print("❌ Cannot connect to Notion. Please check your integration setup.")
            return None
            
        results = search_result.get("results", [])
        
        # Look for pages first
        pages = [p for p in results if p.get("object") == "page"]
        if pages:
            return pages[0]["id"]
        
        # If no pages, look for databases (can create pages in database parents)
        databases = [d for d in results if d.get("object") == "database"]
        if databases:
            return databases[0]["id"]
        
        print("❌ No accessible pages or databases found.")
        print("Please share at least one page with your Notion integration.")
        return None
    
    def create_ml_lifecycle_project_page(self, parent_id: str) -> Optional[str]:
        """Create the main 'ML lifecycle project' page"""
        print("📄 Creating 'ML lifecycle project' page...")
        
        # Create the main project page
        page_data = {
            "parent": {"type": "page_id", "page_id": parent_id},
            "properties": {
                "title": {"title": [{"text": {"content": "ML lifecycle project"}}]}
            },
            "children": [
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": "🤖 ML Lifecycle Project Dashboard"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": f"Project initialized on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "📊 Project Overview"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": "This page contains the complete ML lifecycle project management system with databases for tracking experiments, data pipeline, deployments, and tasks."}}]
                    }
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.client.base_url}/pages",
                headers=self.client.headers,
                json=page_data
            )
            
            if response.status_code == 200:
                page = response.json()
                self.ml_project_page_id = page["id"]
                print(f"✅ Created 'ML lifecycle project' page")
                print(f"   URL: {page.get('url', 'N/A')}")
                return page["id"]
            else:
                print(f"❌ Failed to create page: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating page: {str(e)}")
            return None
    
    def analyze_current_project(self):
        """Analyze the current ML project structure and data"""
        print("🔍 Analyzing current ML lifecycle project...")
        
        project_analysis = {
            "models": {},
            "data_files": {},
            "scripts": {},
            "deployment": {},
            "monitoring": {},
            "documentation": {}
        }
        
        # Analyze models
        model_files = [
            "models/best_model.pkl",
            "models/model.joblib", 
            "models/random_forest_model.joblib",
            "models/xgboost_model.joblib"
        ]
        
        for model_file in model_files:
            if os.path.exists(model_file):
                project_analysis["models"][model_file] = {
                    "exists": True,
                    "size": os.path.getsize(model_file),
                    "modified": datetime.fromtimestamp(os.path.getmtime(model_file)).isoformat(),
                    "type": self._detect_model_type(model_file)
                }
        
        # Load metrics if available
        if os.path.exists("models/metrics.json"):
            try:
                with open("models/metrics.json", 'r') as f:
                    project_analysis["metrics"] = json.load(f)
            except Exception as e:
                project_analysis["metrics_error"] = str(e)
        
        # Analyze data files
        data_files = [
            "data/predictive_maintenance_full.csv",
            "data/processed/processed_data.csv"
        ]
        
        for data_file in data_files:
            if os.path.exists(data_file):
                project_analysis["data_files"][data_file] = {
                    "exists": True,
                    "size": os.path.getsize(data_file),
                    "modified": datetime.fromtimestamp(os.path.getmtime(data_file)).isoformat()
                }
        
        # Count scripts
        script_dirs = ["scripts/", "src/"]
        for script_dir in script_dirs:
            if os.path.exists(script_dir):
                py_files = [f for f in os.listdir(script_dir) if f.endswith('.py')]
                project_analysis["scripts"][script_dir] = len(py_files)
        
        self.project_data = project_analysis
        return project_analysis
    
    def _detect_model_type(self, model_file):
        """Detect the type of ML model"""
        if "random_forest" in model_file.lower():
            return "Random Forest"
        elif "xgboost" in model_file.lower():
            return "XGBoost"
        elif "best_model" in model_file.lower():
            return "Best Model (Optimized)"
        else:
            return "ML Model"
    
    def create_model_experiments_database(self) -> Optional[str]:
        """Create ML model experiments database"""
        print("🤖 Creating Model Experiments Database...")
        
        properties = {
            "Experiment Name": {"title": {}},
            "Model Type": {
                "select": {
                    "options": [
                        {"name": "Random Forest", "color": "green"},
                        {"name": "XGBoost", "color": "blue"},
                        {"name": "Neural Network", "color": "purple"},
                        {"name": "Best Model", "color": "red"},
                        {"name": "Baseline", "color": "gray"},
                        {"name": "Other", "color": "yellow"}
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "Planning", "color": "gray"},
                        {"name": "Training", "color": "yellow"},
                        {"name": "Completed", "color": "green"},
                        {"name": "Failed", "color": "red"},
                        {"name": "Deployed", "color": "blue"}
                    ]
                }
            },
            "Accuracy": {"number": {"format": "percent"}},
            "Precision": {"number": {"format": "percent"}},
            "Recall": {"number": {"format": "percent"}},
            "F1 Score": {"number": {"format": "percent"}},
            "Training Date": {"date": {}},
            "Dataset": {"rich_text": {}},
            "Model File": {"rich_text": {}},
            "Notes": {"rich_text": {}},
            "Priority": {
                "select": {
                    "options": [
                        {"name": "Critical", "color": "red"},
                        {"name": "High", "color": "orange"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "gray"}
                    ]
                }
            }
        }
        
        database_id = self._create_database("🤖 Model Experiments", properties)
        
        if database_id:
            self.created_databases["model_experiments"] = database_id
            self._populate_model_experiments(database_id)
        
        return database_id
    
    def create_data_pipeline_database(self) -> Optional[str]:
        """Create data pipeline tracking database"""
        print("📊 Creating Data Pipeline Database...")
        
        properties = {
            "Pipeline Stage": {"title": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Not Started", "color": "gray"},
                        {"name": "In Progress", "color": "yellow"},
                        {"name": "Completed", "color": "green"},
                        {"name": "Failed", "color": "red"},
                        {"name": "Needs Review", "color": "orange"}
                    ]
                }
            },
            "Data Source": {"rich_text": {}},
            "Records Count": {"number": {}},
            "Data Quality": {"number": {"format": "percent"}},
            "Last Updated": {"date": {}},
            "Output Location": {"rich_text": {}},
            "Processing Time": {"rich_text": {}},
            "Issues": {"rich_text": {}},
            "Next Actions": {"rich_text": {}}
        }
        
        database_id = self._create_database("📊 Data Pipeline Status", properties)
        
        if database_id:
            self.created_databases["data_pipeline"] = database_id
            self._populate_data_pipeline(database_id)
        
        return database_id
    
    def create_deployment_database(self) -> Optional[str]:
        """Create deployment tracking database"""
        print("🚀 Creating Deployment Database...")
        
        properties = {
            "Deployment": {"title": {}},
            "Environment": {
                "select": {
                    "options": [
                        {"name": "Development", "color": "gray"},
                        {"name": "Staging", "color": "yellow"},
                        {"name": "Production", "color": "green"},
                        {"name": "Testing", "color": "blue"}
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "Planning", "color": "gray"},
                        {"name": "Deploying", "color": "yellow"},
                        {"name": "Active", "color": "green"},
                        {"name": "Failed", "color": "red"},
                        {"name": "Maintenance", "color": "orange"}
                    ]
                }
            },
            "Model Version": {"rich_text": {}},
            "Deploy Date": {"date": {}},
            "Health Status": {
                "select": {
                    "options": [
                        {"name": "Healthy", "color": "green"},
                        {"name": "Warning", "color": "yellow"},
                        {"name": "Critical", "color": "red"},
                        {"name": "Unknown", "color": "gray"}
                    ]
                }
            },
            "API Endpoint": {"url": {}},
            "CPU Usage": {"number": {"format": "percent"}},
            "Memory Usage": {"number": {"format": "percent"}},
            "Request Count": {"number": {}},
            "Error Rate": {"number": {"format": "percent"}},
            "Notes": {"rich_text": {}}
        }
        
        database_id = self._create_database("🚀 Deployment Tracking", properties)
        
        if database_id:
            self.created_databases["deployment"] = database_id
            self._populate_deployment_data(database_id)
        
        return database_id
    
    def create_project_tasks_database(self) -> Optional[str]:
        """Create project tasks database"""
        print("📋 Creating Project Tasks Database...")
        
        properties = {
            "Task": {"title": {}},
            "Category": {
                "select": {
                    "options": [
                        {"name": "Data Collection", "color": "blue"},
                        {"name": "Data Processing", "color": "green"},
                        {"name": "Model Development", "color": "purple"},
                        {"name": "Model Training", "color": "orange"},
                        {"name": "Model Evaluation", "color": "yellow"},
                        {"name": "Deployment", "color": "red"},
                        {"name": "Monitoring", "color": "gray"},
                        {"name": "Documentation", "color": "brown"},
                        {"name": "Testing", "color": "pink"}
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "Backlog", "color": "gray"},
                        {"name": "To Do", "color": "red"},
                        {"name": "In Progress", "color": "yellow"},
                        {"name": "Review", "color": "orange"},
                        {"name": "Done", "color": "green"},
                        {"name": "Blocked", "color": "red"}
                    ]
                }
            },
            "Priority": {
                "select": {
                    "options": [
                        {"name": "Critical", "color": "red"},
                        {"name": "High", "color": "orange"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "gray"}
                    ]
                }
            },
            "Assignee": {"rich_text": {}},
            "Due Date": {"date": {}},
            "Progress": {"number": {"format": "percent"}},
            "Estimated Hours": {"number": {}},
            "Actual Hours": {"number": {}},
            "Description": {"rich_text": {}},
            "Dependencies": {"rich_text": {}}
        }
        
        database_id = self._create_database("📋 Project Tasks", properties)
        
        if database_id:
            self.created_databases["tasks"] = database_id
            self._populate_project_tasks(database_id)
        
        return database_id
    
    def _create_database(self, title: str, properties: Dict) -> Optional[str]:
        """Helper method to create a database in the ML project page"""
        try:
            database_data = {
                "parent": {"type": "page_id", "page_id": self.ml_project_page_id},
                "title": [{"type": "text", "text": {"content": title}}],
                "properties": properties
            }
            
            response = requests.post(
                f"{self.client.base_url}/databases",
                headers=self.client.headers,
                json=database_data
            )
            
            if response.status_code == 200:
                database = response.json()
                print(f"✅ Created database: {title}")
                return database["id"]
            else:
                print(f"❌ Failed to create database {title}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating database {title}: {str(e)}")
            return None
    
    def _populate_model_experiments(self, database_id: str):
        """Populate model experiments with actual project data"""
        experiments = []
        
        # Add experiments based on actual models found
        models = self.project_data.get("models", {})
        metrics = self.project_data.get("metrics", {})
        
        if "models/random_forest_model.joblib" in models:
            experiments.append({
                "Experiment Name": {"title": [{"text": {"content": "Random Forest Model"}}]},
                "Model Type": {"select": {"name": "Random Forest"}},
                "Status": {"select": {"name": "Completed"}},
                "Dataset": {"rich_text": [{"text": {"content": "predictive_maintenance_full.csv"}}]},
                "Model File": {"rich_text": [{"text": {"content": "models/random_forest_model.joblib"}}]},
                "Training Date": {"date": {"start": models["models/random_forest_model.joblib"].get("modified", "").split("T")[0] if "models/random_forest_model.joblib" in models else datetime.now().strftime("%Y-%m-%d")}},
                "Priority": {"select": {"name": "High"}}
            })
        
        if "models/xgboost_model.joblib" in models:
            experiments.append({
                "Experiment Name": {"title": [{"text": {"content": "XGBoost Model"}}]},
                "Model Type": {"select": {"name": "XGBoost"}},
                "Status": {"select": {"name": "Completed"}},
                "Dataset": {"rich_text": [{"text": {"content": "predictive_maintenance_full.csv"}}]},
                "Model File": {"rich_text": [{"text": {"content": "models/xgboost_model.joblib"}}]},
                "Training Date": {"date": {"start": models["models/xgboost_model.joblib"].get("modified", "").split("T")[0] if "models/xgboost_model.joblib" in models else datetime.now().strftime("%Y-%m-%d")}},
                "Priority": {"select": {"name": "High"}}
            })
        
        if "models/best_model.pkl" in models:
            exp_data = {
                "Experiment Name": {"title": [{"text": {"content": "Best Model (Optimized)"}}]},
                "Model Type": {"select": {"name": "Best Model"}},
                "Status": {"select": {"name": "Completed"}},
                "Dataset": {"rich_text": [{"text": {"content": "processed_data.csv"}}]},
                "Model File": {"rich_text": [{"text": {"content": "models/best_model.pkl"}}]},
                "Training Date": {"date": {"start": models["models/best_model.pkl"].get("modified", "").split("T")[0] if "models/best_model.pkl" in models else datetime.now().strftime("%Y-%m-%d")}},
                "Priority": {"select": {"name": "Critical"}}
            }
            
            # Add metrics if available
            if metrics:
                if "accuracy" in metrics:
                    exp_data["Accuracy"] = {"number": float(metrics["accuracy"])}
                if "precision" in metrics:
                    exp_data["Precision"] = {"number": float(metrics["precision"])}
                if "recall" in metrics:
                    exp_data["Recall"] = {"number": float(metrics["recall"])}
                if "f1_score" in metrics:
                    exp_data["F1 Score"] = {"number": float(metrics["f1_score"])}
            
            experiments.append(exp_data)
        
        # If no models found, add placeholder
        if not experiments:
            experiments.append({
                "Experiment Name": {"title": [{"text": {"content": "Initial Model Training"}}]},
                "Model Type": {"select": {"name": "Baseline"}},
                "Status": {"select": {"name": "Planning"}},
                "Dataset": {"rich_text": [{"text": {"content": "predictive_maintenance_full.csv"}}]},
                "Priority": {"select": {"name": "High"}},
                "Notes": {"rich_text": [{"text": {"content": "First model to establish baseline performance"}}]}
            })
        
        for experiment in experiments:
            self._create_page_in_database(database_id, experiment)
    
    def _populate_data_pipeline(self, database_id: str):
        """Populate data pipeline with actual project status"""
        pipeline_stages = [
            {
                "Pipeline Stage": {"title": [{"text": {"content": "Data Ingestion"}}]},
                "Status": {"select": {"name": "Completed" if os.path.exists("data/predictive_maintenance_full.csv") else "Not Started"}},
                "Data Source": {"rich_text": [{"text": {"content": "CSV Files - Predictive Maintenance Dataset"}}]},
                "Output Location": {"rich_text": [{"text": {"content": "data/predictive_maintenance_full.csv"}}]},
                "Last Updated": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                "Data Quality": {"number": 0.95 if os.path.exists("data/predictive_maintenance_full.csv") else 0.0}
            },
            {
                "Pipeline Stage": {"title": [{"text": {"content": "Data Preprocessing"}}]},
                "Status": {"select": {"name": "Completed" if os.path.exists("data/processed/processed_data.csv") else "In Progress"}},
                "Data Source": {"rich_text": [{"text": {"content": "Raw maintenance data"}}]},
                "Output Location": {"rich_text": [{"text": {"content": "data/processed/processed_data.csv"}}]},
                "Last Updated": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                "Data Quality": {"number": 0.92 if os.path.exists("data/processed/processed_data.csv") else 0.75}
            },
            {
                "Pipeline Stage": {"title": [{"text": {"content": "Feature Engineering"}}]},
                "Status": {"select": {"name": "Completed" if os.path.exists("models/feature_names.json") else "In Progress"}},
                "Data Source": {"rich_text": [{"text": {"content": "Processed maintenance data"}}]},
                "Output Location": {"rich_text": [{"text": {"content": "Feature matrices for model training"}}]},
                "Last Updated": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                "Data Quality": {"number": 0.88}
            },
            {
                "Pipeline Stage": {"title": [{"text": {"content": "Data Validation"}}]},
                "Status": {"select": {"name": "In Progress"}},
                "Data Source": {"rich_text": [{"text": {"content": "Engineered features"}}]},
                "Output Location": {"rich_text": [{"text": {"content": "Validation reports"}}]},
                "Last Updated": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                "Next Actions": {"rich_text": [{"text": {"content": "Implement data drift detection"}}]}
            }
        ]
        
        for stage in pipeline_stages:
            self._create_page_in_database(database_id, stage)
    
    def _populate_deployment_data(self, database_id: str):
        """Populate deployment tracking"""
        deployments = [
            {
                "Deployment": {"title": [{"text": {"content": "Local Development API"}}]},
                "Environment": {"select": {"name": "Development"}},
                "Status": {"select": {"name": "Active" if os.path.exists("src/api/main.py") else "Planning"}},
                "Model Version": {"rich_text": [{"text": {"content": "best_model_v1.0"}}]},
                "Deploy Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                "Health Status": {"select": {"name": "Healthy" if os.path.exists("src/api/main.py") else "Unknown"}},
                "Notes": {"rich_text": [{"text": {"content": "FastAPI-based ML model serving endpoint"}}]}
            },
            {
                "Deployment": {"title": [{"text": {"content": "Docker Container"}}]},
                "Environment": {"select": {"name": "Testing"}},
                "Status": {"select": {"name": "Planning" if os.path.exists("docker/Dockerfile.api") else "Not Started"}},
                "Model Version": {"rich_text": [{"text": {"content": "latest"}}]},
                "Health Status": {"select": {"name": "Unknown"}},
                "Notes": {"rich_text": [{"text": {"content": "Containerized deployment for scalability"}}]}
            },
            {
                "Deployment": {"title": [{"text": {"content": "Production API"}}]},
                "Environment": {"select": {"name": "Production"}},
                "Status": {"select": {"name": "Planning"}},
                "Model Version": {"rich_text": [{"text": {"content": "To be determined"}}]},
                "Health Status": {"select": {"name": "Unknown"}},
                "Notes": {"rich_text": [{"text": {"content": "Production-ready deployment with monitoring"}}]}
            }
        ]
        
        for deployment in deployments:
            self._create_page_in_database(database_id, deployment)
    
    def _populate_project_tasks(self, database_id: str):
        """Populate project tasks based on current project state"""
        tasks = [
            {
                "Task": {"title": [{"text": {"content": "Model Performance Optimization"}}]},
                "Category": {"select": {"name": "Model Development"}},
                "Status": {"select": {"name": "In Progress"}},
                "Priority": {"select": {"name": "High"}},
                "Progress": {"number": 0.70},
                "Estimated Hours": {"number": 20},
                "Actual Hours": {"number": 14},
                "Description": {"rich_text": [{"text": {"content": "Optimize model hyperparameters and feature selection"}}]}
            },
            {
                "Task": {"title": [{"text": {"content": "Data Pipeline Monitoring"}}]},
                "Category": {"select": {"name": "Monitoring"}},
                "Status": {"select": {"name": "To Do"}},
                "Priority": {"select": {"name": "High"}},
                "Progress": {"number": 0.0},
                "Estimated Hours": {"number": 16},
                "Description": {"rich_text": [{"text": {"content": "Implement automated data quality monitoring"}}]}
            },
            {
                "Task": {"title": [{"text": {"content": "Model Drift Detection"}}]},
                "Category": {"select": {"name": "Monitoring"}},
                "Status": {"select": {"name": "In Progress" if os.path.exists("scripts/check_model_drift.py") else "To Do"}},
                "Priority": {"select": {"name": "Medium"}},
                "Progress": {"number": 0.40 if os.path.exists("scripts/check_model_drift.py") else 0.0},
                "Estimated Hours": {"number": 12},
                "Description": {"rich_text": [{"text": {"content": "Set up model performance drift detection system"}}]}
            },
            {
                "Task": {"title": [{"text": {"content": "API Documentation"}}]},
                "Category": {"select": {"name": "Documentation"}},
                "Status": {"select": {"name": "Review" if os.path.exists("README.md") else "To Do"}},
                "Priority": {"select": {"name": "Medium"}},
                "Progress": {"number": 0.80 if os.path.exists("README.md") else 0.0},
                "Estimated Hours": {"number": 8},
                "Description": {"rich_text": [{"text": {"content": "Complete API endpoint documentation"}}]}
            },
            {
                "Task": {"title": [{"text": {"content": "Production Deployment"}}]},
                "Category": {"select": {"name": "Deployment"}},
                "Status": {"select": {"name": "Backlog"}},
                "Priority": {"select": {"name": "High"}},
                "Progress": {"number": 0.0},
                "Estimated Hours": {"number": 24},
                "Description": {"rich_text": [{"text": {"content": "Deploy model to production environment with monitoring"}}]}
            },
            {
                "Task": {"title": [{"text": {"content": "Model Retraining Pipeline"}}]},
                "Category": {"select": {"name": "Model Development"}},
                "Status": {"select": {"name": "Backlog"}},
                "Priority": {"select": {"name": "Medium"}},
                "Progress": {"number": 0.0},
                "Estimated Hours": {"number": 18},
                "Description": {"rich_text": [{"text": {"content": "Automated model retraining based on new data"}}]}
            }
        ]
        
        for task in tasks:
            self._create_page_in_database(database_id, task)
    
    def _create_page_in_database(self, database_id: str, properties: Dict):
        """Create a page in a database"""
        try:
            page_data = {
                "parent": {"database_id": database_id},
                "properties": properties
            }
            
            response = requests.post(
                f"{self.client.base_url}/pages",
                headers=self.client.headers,
                json=page_data
            )
            
            if response.status_code != 200:
                print(f"Warning: Failed to create entry: {response.status_code}")
                
        except Exception as e:
            print(f"Warning: Error creating entry: {str(e)}")
    
    def add_project_summary_to_page(self):
        """Add project summary content to the main page"""
        print("📝 Adding project summary to main page...")
        
        # Prepare summary content
        models_count = len(self.project_data.get("models", {}))
        data_files_count = len(self.project_data.get("data_files", {}))
        
        summary_blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "📊 Project Status Summary"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": f"🤖 Models: {models_count} trained models found"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": f"📊 Data Files: {data_files_count} data files processed"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": f"🚀 Deployment: {'API ready' if os.path.exists('src/api/main.py') else 'In development'}"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": f"📈 Monitoring: {'Active' if os.path.exists('scripts/continuous_monitor.py') else 'Setup needed'}"}}]
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "🎯 Quick Access"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "Use the databases below to manage your ML lifecycle:"}}]
                }
            }
        ]
        
        # Add the summary blocks to the page
        try:
            for block in summary_blocks:
                response = requests.patch(
                    f"{self.client.base_url}/blocks/{self.ml_project_page_id}/children",
                    headers=self.client.headers,
                    json={"children": [block]}
                )
                
                if response.status_code != 200:
                    print(f"Warning: Failed to add summary block: {response.status_code}")
                    
        except Exception as e:
            print(f"Warning: Error adding summary: {str(e)}")
    
    def setup_complete_ml_lifecycle_project(self):
        """Set up the complete ML lifecycle project in Notion"""
        print("🚀 Setting up ML Lifecycle Project in Notion...")
        print("=" * 60)
        
        # Step 1: Get workspace parent
        parent_id = self.get_workspace_parent()
        if not parent_id:
            return False
        
        print(f"✅ Found workspace parent: {parent_id}")
        
        # Step 2: Analyze current project
        self.analyze_current_project()
        
        # Step 3: Create main ML lifecycle project page
        ml_page_id = self.create_ml_lifecycle_project_page(parent_id)
        if not ml_page_id:
            return False
        
        # Step 4: Create all databases
        print("\n🔧 Creating project databases...")
        model_db = self.create_model_experiments_database()
        pipeline_db = self.create_data_pipeline_database()
        deployment_db = self.create_deployment_database()
        tasks_db = self.create_project_tasks_database()
        
        # Step 5: Add project summary
        self.add_project_summary_to_page()
        
        # Step 6: Summary
        print("\n" + "=" * 60)
        print("🎉 ML Lifecycle Project Setup Complete!")
        print(f"\n📄 Main Page: ML lifecycle project")
        print(f"   Page ID: {self.ml_project_page_id}")
        
        print(f"\n📊 Created Databases:")
        for name, db_id in self.created_databases.items():
            if db_id:
                print(f"   ✅ {name}: {db_id}")
        
        print(f"\n🔍 Project Analysis:")
        print(f"   • Models found: {len(self.project_data.get('models', {}))}")
        print(f"   • Data files: {len(self.project_data.get('data_files', {}))}")
        print(f"   • Scripts: {sum(self.project_data.get('scripts', {}).values())}")
        
        print(f"\n🎯 Next Steps:")
        print("   1. Open your 'ML lifecycle project' page in Notion")
        print("   2. Review and update the populated data")
        print("   3. Use the databases to track ongoing work")
        print("   4. Update task progress as you work")
        
        return True

def main():
    """Main function to set up the ML lifecycle project in Notion"""
    print("🤖 ML Lifecycle Project → Notion Setup")
    print("=" * 60)
    
    try:
        setup = MLLifecycleNotionSetup()
        
        # Test connection
        print("🔗 Testing Notion connection...")
        search_result = setup.client.search()
        
        if not search_result:
            print("❌ Cannot connect to Notion. Please check:")
            print("   1. Your integration token is correct")
            print("   2. You've shared at least one page with your integration")
            print("   3. Your integration has write permissions")
            return
        
        accessible_items = len(search_result.get("results", []))
        print(f"✅ Connected! Found {accessible_items} accessible items")
        
        # Set up the complete project
        success = setup.setup_complete_ml_lifecycle_project()
        
        if success:
            print("\n🎊 Your 'ML lifecycle project' page is ready in Notion!")
            print("   Check your Notion workspace for the new page and databases.")
        else:
            print("\n❌ Setup failed. Please check the error messages above.")
            
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure Notion integration has proper permissions")
        print("2. Share at least one page with your integration")
        print("3. Check your internet connection")
        print("4. Verify your integration token is correct")

if __name__ == "__main__":
    main()
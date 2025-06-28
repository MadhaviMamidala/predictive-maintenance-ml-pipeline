#!/usr/bin/env python3
"""
Create ML Lifecycle Notion Workspace
====================================

This script creates a structured Notion workspace for ML project management:
- Model Experiments Database
- Data Pipeline Tracking
- Deployment Status
- Performance Metrics Dashboard
- Project Tasks & Progress

"""

import sys
import json
import requests
from datetime import datetime
from typing import Dict, Optional

# Add src to path for imports
sys.path.append('src')
from notion_client import create_notion_client

class NotionMLWorkspaceCreator:
    def __init__(self):
        self.client = create_notion_client()
        self.created_databases = {}
        
    def get_parent_page(self):
        """Get or create a parent page for the ML workspace"""
        search_result = self.client.search()
        pages = [p for p in search_result.get("results", []) if p.get("object") == "page"]
        
        if pages:
            return pages[0]["id"]
        else:
            print("❌ No parent page found. Please create a page in Notion and share it with your integration.")
            return None
    
    def create_model_experiments_database(self, parent_page_id: str) -> Optional[str]:
        """Create a database for tracking ML model experiments"""
        print("🤖 Creating Model Experiments Database...")
        
        properties = {
            "Experiment Name": {"title": {}},
            "Model Type": {
                "select": {
                    "options": [
                        {"name": "Random Forest", "color": "green"},
                        {"name": "XGBoost", "color": "blue"},
                        {"name": "Neural Network", "color": "purple"},
                        {"name": "SVM", "color": "orange"},
                        {"name": "Linear Regression", "color": "yellow"},
                        {"name": "Other", "color": "gray"}
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
            "Hyperparameters": {"rich_text": {}},
            "Notes": {"rich_text": {}},
            "Model File": {"rich_text": {}},
            "Priority": {
                "select": {
                    "options": [
                        {"name": "High", "color": "red"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "gray"}
                    ]
                }
            }
        }
        
        database_id = self._create_database(
            parent_page_id, 
            "🤖 ML Model Experiments", 
            properties
        )
        
        if database_id:
            self.created_databases["model_experiments"] = database_id
            # Add sample data
            self._add_sample_model_experiments(database_id)
        
        return database_id
    
    def create_data_pipeline_database(self, parent_page_id: str) -> Optional[str]:
        """Create a database for tracking data pipeline status"""
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
            "Records Processed": {"number": {}},
            "Data Quality Score": {"number": {"format": "percent"}},
            "Last Updated": {"date": {}},
            "Processing Time": {"rich_text": {}},
            "Output Location": {"rich_text": {}},
            "Responsible Person": {"rich_text": {}},
            "Issues": {"rich_text": {}},
            "Next Steps": {"rich_text": {}}
        }
        
        database_id = self._create_database(
            parent_page_id,
            "📊 Data Pipeline Status",
            properties
        )
        
        if database_id:
            self.created_databases["data_pipeline"] = database_id
            self._add_sample_pipeline_data(database_id)
        
        return database_id
    
    def create_deployment_tracking_database(self, parent_page_id: str) -> Optional[str]:
        """Create a database for tracking model deployments"""
        print("🚀 Creating Deployment Tracking Database...")
        
        properties = {
            "Deployment Name": {"title": {}},
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
                        {"name": "Retired", "color": "red"}
                    ]
                }
            },
            "Model Version": {"rich_text": {}},
            "Deployment Date": {"date": {}},
            "URL/Endpoint": {"url": {}},
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
            "CPU Usage": {"number": {"format": "percent"}},
            "Memory Usage": {"number": {"format": "percent"}},
            "Request Count": {"number": {}},
            "Error Rate": {"number": {"format": "percent"}},
            "Response Time": {"rich_text": {}},
            "Notes": {"rich_text": {}}
        }
        
        database_id = self._create_database(
            parent_page_id,
            "🚀 Deployment Tracking",
            properties
        )
        
        if database_id:
            self.created_databases["deployment"] = database_id
            self._add_sample_deployment_data(database_id)
        
        return database_id
    
    def create_tasks_database(self, parent_page_id: str) -> Optional[str]:
        """Create a database for project tasks and progress"""
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
                        {"name": "Evaluation", "color": "yellow"},
                        {"name": "Deployment", "color": "red"},
                        {"name": "Monitoring", "color": "gray"},
                        {"name": "Documentation", "color": "brown"}
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
                        {"name": "Done", "color": "green"}
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
            "Estimated Hours": {"number": {}},
            "Actual Hours": {"number": {}},
            "Progress": {"number": {"format": "percent"}},
            "Dependencies": {"rich_text": {}},
            "Notes": {"rich_text": {}}
        }
        
        database_id = self._create_database(
            parent_page_id,
            "📋 ML Project Tasks",
            properties
        )
        
        if database_id:
            self.created_databases["tasks"] = database_id
            self._add_sample_tasks(database_id)
        
        return database_id
    
    def _create_database(self, parent_page_id: str, title: str, properties: Dict) -> Optional[str]:
        """Helper method to create a database"""
        try:
            database_data = {
                "parent": {"type": "page_id", "page_id": parent_page_id},
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
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating database {title}: {str(e)}")
            return None
    
    def _add_sample_model_experiments(self, database_id: str):
        """Add sample model experiment data"""
        sample_experiments = [
            {
                "Experiment Name": {"title": [{"text": {"content": "Random Forest Baseline"}}]},
                "Model Type": {"select": {"name": "Random Forest"}},
                "Status": {"select": {"name": "Completed"}},
                "Accuracy": {"number": 0.85},
                "Precision": {"number": 0.82},
                "Recall": {"number": 0.88},
                "F1 Score": {"number": 0.85},
                "Training Date": {"date": {"start": "2024-01-15"}},
                "Dataset": {"rich_text": [{"text": {"content": "predictive_maintenance_full.csv"}}]},
                "Priority": {"select": {"name": "High"}}
            },
            {
                "Experiment Name": {"title": [{"text": {"content": "XGBoost Optimization"}}]},
                "Model Type": {"select": {"name": "XGBoost"}},
                "Status": {"select": {"name": "Training"}},
                "Training Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                "Dataset": {"rich_text": [{"text": {"content": "processed_data.csv"}}]},
                "Priority": {"select": {"name": "High"}}
            }
        ]
        
        for experiment in sample_experiments:
            self._create_page_in_database(database_id, experiment)
    
    def _add_sample_pipeline_data(self, database_id: str):
        """Add sample data pipeline entries"""
        sample_pipelines = [
            {
                "Pipeline Stage": {"title": [{"text": {"content": "Data Ingestion"}}]},
                "Status": {"select": {"name": "Completed"}},
                "Data Source": {"rich_text": [{"text": {"content": "CSV Files"}}]},
                "Records Processed": {"number": 50000},
                "Data Quality Score": {"number": 0.95},
                "Last Updated": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
            },
            {
                "Pipeline Stage": {"title": [{"text": {"content": "Data Cleaning"}}]},
                "Status": {"select": {"name": "In Progress"}},
                "Data Source": {"rich_text": [{"text": {"content": "Raw maintenance data"}}]},
                "Records Processed": {"number": 45000},
                "Data Quality Score": {"number": 0.88},
                "Last Updated": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
            }
        ]
        
        for pipeline in sample_pipelines:
            self._create_page_in_database(database_id, pipeline)
    
    def _add_sample_deployment_data(self, database_id: str):
        """Add sample deployment entries"""
        sample_deployments = [
            {
                "Deployment Name": {"title": [{"text": {"content": "Production API v1.0"}}]},
                "Environment": {"select": {"name": "Production"}},
                "Status": {"select": {"name": "Active"}},
                "Model Version": {"rich_text": [{"text": {"content": "best_model_v1.0"}}]},
                "Deployment Date": {"date": {"start": "2024-01-20"}},
                "Health Status": {"select": {"name": "Healthy"}},
                "CPU Usage": {"number": 0.45},
                "Memory Usage": {"number": 0.60},
                "Request Count": {"number": 1250},
                "Error Rate": {"number": 0.02}
            }
        ]
        
        for deployment in sample_deployments:
            self._create_page_in_database(database_id, deployment)
    
    def _add_sample_tasks(self, database_id: str):
        """Add sample project tasks"""
        sample_tasks = [
            {
                "Task": {"title": [{"text": {"content": "Implement model drift detection"}}]},
                "Category": {"select": {"name": "Monitoring"}},
                "Status": {"select": {"name": "In Progress"}},
                "Priority": {"select": {"name": "High"}},
                "Progress": {"number": 0.60},
                "Estimated Hours": {"number": 16},
                "Actual Hours": {"number": 10}
            },
            {
                "Task": {"title": [{"text": {"content": "Set up production monitoring dashboard"}}]},
                "Category": {"select": {"name": "Monitoring"}},
                "Status": {"select": {"name": "To Do"}},
                "Priority": {"select": {"name": "Medium"}},
                "Progress": {"number": 0.0},
                "Estimated Hours": {"number": 8}
            },
            {
                "Task": {"title": [{"text": {"content": "Document API endpoints"}}]},
                "Category": {"select": {"name": "Documentation"}},
                "Status": {"select": {"name": "Review"}},
                "Priority": {"select": {"name": "Medium"}},
                "Progress": {"number": 0.90},
                "Estimated Hours": {"number": 4},
                "Actual Hours": {"number": 3}
            }
        ]
        
        for task in sample_tasks:
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
                print(f"Warning: Failed to create sample entry: {response.status_code}")
                
        except Exception as e:
            print(f"Warning: Error creating sample entry: {str(e)}")
    
    def create_workspace_overview_page(self, parent_page_id: str):
        """Create an overview page with links to all databases"""
        print("📄 Creating ML Workspace Overview Page...")
        
        content = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "🤖 ML Lifecycle Project Workspace"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"Created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "📊 Project Databases"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "🤖 ML Model Experiments - Track all model training experiments"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "📊 Data Pipeline Status - Monitor ETL processes"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "🚀 Deployment Tracking - Monitor production deployments"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "📋 ML Project Tasks - Track project progress and tasks"}}]
                }
            }
        ]
        
        page_data = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "properties": {
                "title": {"title": [{"text": {"content": "ML Lifecycle Workspace Overview"}}]}
            },
            "children": content
        }
        
        try:
            response = requests.post(
                f"{self.client.base_url}/pages",
                headers=self.client.headers,
                json=page_data
            )
            
            if response.status_code == 200:
                page = response.json()
                print(f"✅ Created workspace overview page")
                return page["id"]
            else:
                print(f"❌ Failed to create overview page: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating overview page: {str(e)}")
            return None
    
    def setup_complete_workspace(self):
        """Set up the complete ML workspace in Notion"""
        print("🚀 Setting up ML Lifecycle Notion Workspace...")
        print("=" * 60)
        
        # Get parent page
        parent_page_id = self.get_parent_page()
        if not parent_page_id:
            return False
        
        print(f"✅ Using parent page ID: {parent_page_id}")
        
        # Create all databases
        model_db = self.create_model_experiments_database(parent_page_id)
        pipeline_db = self.create_data_pipeline_database(parent_page_id)
        deployment_db = self.create_deployment_tracking_database(parent_page_id)
        tasks_db = self.create_tasks_database(parent_page_id)
        
        # Create overview page
        overview_page = self.create_workspace_overview_page(parent_page_id)
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 ML Lifecycle Notion Workspace Created Successfully!")
        print("\nCreated Databases:")
        for name, db_id in self.created_databases.items():
            if db_id:
                print(f"✅ {name}: {db_id}")
        
        print(f"\n📄 Overview Page: {overview_page if overview_page else 'Failed to create'}")
        
        print("\n🔧 Next Steps:")
        print("1. Start logging your model experiments")
        print("2. Track data pipeline status")
        print("3. Monitor deployments")
        print("4. Manage project tasks")
        print("5. Use the overview page as your ML project dashboard")
        
        return True

def main():
    """Main function to create the ML Notion workspace"""
    print("🤖 ML Lifecycle → Notion Workspace Creator")
    print("=" * 60)
    
    try:
        creator = NotionMLWorkspaceCreator()
        
        # Test connection
        print("🔗 Testing Notion connection...")
        search_result = creator.client.search()
        
        if not search_result:
            print("❌ Cannot connect to Notion. Please check:")
            print("1. Your integration token is correct")
            print("2. You've shared at least one page with your integration")
            print("3. Your integration has write permissions")
            return
        
        accessible_content = search_result.get("results", [])
        print(f"✅ Connected! Found {len(accessible_content)} accessible items")
        
        # Create workspace
        success = creator.setup_complete_workspace()
        
        if success:
            print("\n🎊 Your ML Lifecycle Notion workspace is ready!")
        else:
            print("\n❌ Failed to create complete workspace")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure your Notion integration has proper permissions")
        print("2. Share at least one page with your integration")
        print("3. Check your internet connection")

if __name__ == "__main__":
    main()
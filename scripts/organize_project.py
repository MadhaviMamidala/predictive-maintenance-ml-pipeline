#!/usr/bin/env python3
"""
ML Lifecycle Project Organizer
Automatically organizes the project into an optimal, industry-standard structure
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('project_organization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProjectOrganizer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).resolve()
        self.backup_dir = self.project_root / f"backup_before_organization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.moves_log = []
        
        # Define the optimal structure
        self.structure = {
            "data": {
                "raw": [],
                "processed": [],
                "backups": []
            },
            "models": [],
            "src": {
                "api": [],
                "etl": [],
                "training": [],
                "validation": [],
                "deployment": [],
                "sagemaker": [],
                "kubeflow": []
            },
            "monitoring": {
                "grafana": {
                    "dashboards": [],
                    "provisioning": {
                        "dashboards": [],
                        "datasources": []
                    }
                },
                "prometheus": []
            },
            "docker": [],
            "nginx": {
                "ssl": [],
                "logs": []
            },
            "scripts": [],
            "notebooks": [],
            "docs": []
        }
        
        # File mapping rules
        self.file_mapping = {
            # Data files
            "data/processed/processed_data.csv": "data/processed/",
            "data/generate_synthetic_data.py": "data/",
            
            # Model files
            "models/best_model.pkl": "models/",
            
            # Source code files
            "src/api/main.py": "src/api/",
            "src/api/test_api.py": "src/api/",
            "src/etl/": "src/etl/",
            "src/training/train_random_forest.py": "src/training/",
            "src/validation/validate_data.py": "src/validation/",
            "src/deployment/upload_to_s3.py": "src/deployment/",
            "src/sagemaker/": "src/sagemaker/",
            "src/kubeflow/model_comparison_pipeline.py": "src/kubeflow/",
            "src/config.py": "src/",
            "src/model_comparison_local.py": "src/",
            "src/test_monitoring.py": "src/",
            "src/test_system.py": "src/",
            
            # Monitoring files
            "monitoring/grafana/dashboards/": "monitoring/grafana/dashboards/",
            "monitoring/grafana/provisioning/": "monitoring/grafana/provisioning/",
            "monitoring/prometheus/prometheus.yml": "monitoring/prometheus/",
            
            # Docker files
            "docker/Dockerfile.api": "docker/",
            "docker/Dockerfile.simple": "docker/",
            
            # Nginx files
            "nginx/nginx.conf": "nginx/",
            "nginx/nginx.production.conf": "nginx/",
            "nginx/ssl/": "nginx/ssl/",
            "nginx/logs/": "nginx/logs/",
            
            # Scripts
            "scripts/deploy_production.sh": "scripts/",
            "scripts/deploy_production.bat": "scripts/",
            "scripts/generate_ssl.py": "scripts/",
            "scripts/init-db.sql": "scripts/",
            
            # Documentation
            "docs/": "docs/",
            
            # Root level files (keep in place)
            "README.md": ".",
            "requirements.txt": ".",
            "requirements-sagemaker.txt": ".",
            "requirements-kubeflow.txt": ".",
            ".gitignore": ".",
            
            # Entry points and automation
            "start_api.py": ".",
            "start_monitoring.py": ".",
            "start_monitoring.sh": ".",
            "start_monitoring.bat": ".",
            "automate_monitoring.py": ".",
            "monitor_background.py": ".",
            "continuous_monitor.py": ".",
            
            # Docker compose files
            "docker-compose.yml": ".",
            "docker-compose.simple.yml": ".",
            "docker-compose.prod.yml": ".",
            "docker-compose.production.yml": ".",
            
            # Guides and documentation
            "AUTOMATION_GUIDE.md": ".",
            "MONITORING_GUIDE.md": ".",
            "DASHBOARD_SETUP_GUIDE.md": ".",
            "VISUAL_MONITORING_SETUP.md": ".",
            "PRODUCTION_DEPLOYMENT_GUIDE.md": ".",
            
            # Model artifacts and metrics
            "model_metrics.json": ".",
            "model_comparison_metrics.png": ".",
            "model_comparison_table.txt": ".",
            "model_confusion_matrices.png": ".",
            "learning_curves.png": ".",
            "calibration_curves.png": ".",
            "feature_importance.png": ".",
            "precision_recall_curves.png": ".",
            "roc_curves.png": ".",
            "statistical_significance.json": ".",
            
            # Logs
            "monitoring.log": ".",
            "background_monitor.log": ".",
            "deployment_info.txt": "."
        }

    def create_backup(self):
        """Create a backup of the current project structure"""
        logger.info(f"Creating backup at: {self.backup_dir}")
        
        try:
            # Create backup directory
            self.backup_dir.mkdir(exist_ok=True)
            
            # Copy all files except the backup directory itself
            for item in self.project_root.iterdir():
                if item.name != self.backup_dir.name and not item.name.startswith('.'):
                    if item.is_file():
                        shutil.copy2(item, self.backup_dir / item.name)
                    elif item.is_dir():
                        shutil.copytree(item, self.backup_dir / item.name)
            
            logger.info("✓ Backup created successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create backup: {e}")
            return False

    def create_directory_structure(self):
        """Create the optimal directory structure"""
        logger.info("Creating directory structure...")
        
        try:
            # Create main directories
            for main_dir in self.structure.keys():
                main_path = self.project_root / main_dir
                main_path.mkdir(exist_ok=True)
                
                # Create subdirectories
                if isinstance(self.structure[main_dir], dict):
                    for sub_dir in self.structure[main_dir].keys():
                        sub_path = main_path / sub_dir
                        sub_path.mkdir(exist_ok=True)
                        
                        # Create nested subdirectories
                        if isinstance(self.structure[main_dir][sub_dir], dict):
                            for nested_dir in self.structure[main_dir][sub_dir].keys():
                                nested_path = sub_path / nested_dir
                                nested_path.mkdir(exist_ok=True)
            
            logger.info("✓ Directory structure created successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create directory structure: {e}")
            return False

    def move_files(self):
        """Move files to their optimal locations"""
        logger.info("Moving files to optimal locations...")
        
        moved_count = 0
        skipped_count = 0
        
        for source_pattern, target_dir in self.file_mapping.items():
            source_path = self.project_root / source_pattern
            
            if source_path.exists():
                target_path = self.project_root / target_dir
                target_path.mkdir(parents=True, exist_ok=True)
                
                if source_path.is_file():
                    # Move single file
                    target_file = target_path / source_path.name
                    if target_file.exists():
                        logger.warning(f"Target file already exists, skipping: {target_file}")
                        skipped_count += 1
                        continue
                    
                    try:
                        shutil.move(str(source_path), str(target_file))
                        self.moves_log.append({
                            "type": "file",
                            "from": str(source_path),
                            "to": str(target_file),
                            "status": "moved"
                        })
                        logger.info(f"✓ Moved: {source_path.name} -> {target_dir}")
                        moved_count += 1
                    except Exception as e:
                        logger.error(f"✗ Failed to move {source_path}: {e}")
                        self.moves_log.append({
                            "type": "file",
                            "from": str(source_path),
                            "to": str(target_file),
                            "status": "failed",
                            "error": str(e)
                        })
                
                elif source_path.is_dir():
                    # Move directory contents
                    for item in source_path.iterdir():
                        target_item = target_path / item.name
                        if target_item.exists():
                            logger.warning(f"Target already exists, skipping: {target_item}")
                            skipped_count += 1
                            continue
                        
                        try:
                            if item.is_file():
                                shutil.move(str(item), str(target_item))
                            else:
                                shutil.move(str(item), str(target_item))
                            
                            self.moves_log.append({
                                "type": "item",
                                "from": str(item),
                                "to": str(target_item),
                                "status": "moved"
                            })
                            logger.info(f"✓ Moved: {item.name} -> {target_dir}")
                            moved_count += 1
                        except Exception as e:
                            logger.error(f"✗ Failed to move {item}: {e}")
                            self.moves_log.append({
                                "type": "item",
                                "from": str(item),
                                "to": str(target_item),
                                "status": "failed",
                                "error": str(e)
                            })
        
        logger.info(f"✓ File organization completed: {moved_count} moved, {skipped_count} skipped")
        return moved_count, skipped_count

    def cleanup_empty_directories(self):
        """Remove empty directories after moving files"""
        logger.info("Cleaning up empty directories...")
        
        removed_count = 0
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        logger.info(f"✓ Removed empty directory: {dir_path}")
                        removed_count += 1
                except Exception as e:
                    logger.warning(f"Could not remove directory {dir_path}: {e}")
        
        logger.info(f"✓ Cleanup completed: {removed_count} empty directories removed")

    def create_organization_report(self):
        """Create a detailed report of the organization process"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "backup_location": str(self.backup_dir),
            "moves": self.moves_log,
            "summary": {
                "total_moves": len([m for m in self.moves_log if m["status"] == "moved"]),
                "total_failures": len([m for m in self.moves_log if m["status"] == "failed"]),
                "backup_created": self.backup_dir.exists()
            }
        }
        
        report_path = self.project_root / "organization_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✓ Organization report saved to: {report_path}")
        return report

    def organize(self, create_backup=True):
        """Main organization method"""
        logger.info("🚀 Starting ML Lifecycle Project Organization")
        logger.info("=" * 60)
        
        try:
            # Step 1: Create backup
            if create_backup:
                if not self.create_backup():
                    logger.error("Backup creation failed. Aborting organization.")
                    return False
            
            # Step 2: Create directory structure
            if not self.create_directory_structure():
                logger.error("Directory structure creation failed. Aborting organization.")
                return False
            
            # Step 3: Move files
            moved_count, skipped_count = self.move_files()
            
            # Step 4: Cleanup empty directories
            self.cleanup_empty_directories()
            
            # Step 5: Create report
            report = self.create_organization_report()
            
            # Final summary
            logger.info("=" * 60)
            logger.info("🎉 Project Organization Completed Successfully!")
            logger.info(f"📊 Summary:")
            logger.info(f"   • Files moved: {report['summary']['total_moves']}")
            logger.info(f"   • Files failed: {report['summary']['total_failures']}")
            logger.info(f"   • Backup created: {report['summary']['backup_created']}")
            logger.info(f"   • Backup location: {self.backup_dir}")
            logger.info(f"   • Report saved: organization_report.json")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Organization failed: {e}")
            return False

def main():
    """Main function"""
    print("🔧 ML Lifecycle Project Organizer")
    print("=" * 50)
    print("This script will organize your project into an optimal structure.")
    print("A backup will be created before making any changes.")
    print()
    
    # Check if running in the correct directory
    current_dir = Path.cwd()
    if not (current_dir / "src").exists() and not (current_dir / "models").exists():
        print("⚠️  Warning: This doesn't appear to be an ML lifecycle project directory.")
        print("   Make sure you're running this script from the project root.")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Organization cancelled.")
            return
    
    # Create organizer and run
    organizer = ProjectOrganizer()
    
    print("Starting organization process...")
    print()
    
    success = organizer.organize(create_backup=True)
    
    if success:
        print()
        print("✅ Organization completed successfully!")
        print("📁 Your project is now organized according to industry best practices.")
        print("📋 Check 'organization_report.json' for detailed information.")
        print("💾 A backup of your original structure has been created.")
    else:
        print()
        print("❌ Organization failed. Check the logs for details.")

if __name__ == "__main__":
    main() 
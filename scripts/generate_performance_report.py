#!/usr/bin/env python3
"""
Performance Report Generator
Generates comprehensive performance reports for the MLOps system
"""

import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any
import requests
import psutil
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceReporter:
    """Generate comprehensive performance reports"""
    
    def __init__(self):
        self.report_data = {}
        self.report_dir = Path("reports_and_artifacts")
        self.report_dir.mkdir(exist_ok=True)
        
    def collect_model_performance(self) -> Dict[str, Any]:
        """Collect model performance metrics"""
        logger.info("Collecting model performance metrics...")
        
        # Load model metrics
        metrics_path = Path("models/metrics.json")
        if not metrics_path.exists():
            return {"error": "Model metrics not found"}
        
        with open(metrics_path, 'r') as f:
            model_metrics = json.load(f)
        
        # Load model metadata
        feature_names_path = Path("models/feature_names.json")
        feature_names = []
        if feature_names_path.exists():
            with open(feature_names_path, 'r') as f:
                feature_names = json.load(f)
        
        return {
            "model_metrics": model_metrics,
            "feature_names": feature_names,
            "model_file_size": Path("models/best_model.pkl").stat().st_size if Path("models/best_model.pkl").exists() else 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def collect_api_performance(self) -> Dict[str, Any]:
        """Collect API performance metrics"""
        logger.info("Collecting API performance metrics...")
        
        api_metrics = {}
        
        try:
            # Test API health
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                api_metrics["health"] = health_data
                api_metrics["api_status"] = "healthy"
            else:
                api_metrics["api_status"] = "unhealthy"
        except Exception as e:
            api_metrics["api_status"] = "unreachable"
            api_metrics["error"] = str(e)
        
        try:
            # Test prediction endpoint
            test_data = {
                "volt": 220,
                "rotate": 1500,
                "pressure": 95,
                "vibration": 0.5,
                "age": 12
            }
            
            start_time = datetime.now()
            response = requests.post("http://localhost:8000/predict", json=test_data, timeout=10)
            end_time = datetime.now()
            
            if response.status_code == 200:
                prediction_data = response.json()
                api_metrics["prediction_test"] = {
                    "status": "success",
                    "response_time_ms": (end_time - start_time).total_seconds() * 1000,
                    "prediction": prediction_data.get("prediction"),
                    "probability": prediction_data.get("probability")
                }
            else:
                api_metrics["prediction_test"] = {
                    "status": "failed",
                    "status_code": response.status_code
                }
        except Exception as e:
            api_metrics["prediction_test"] = {
                "status": "error",
                "error": str(e)
            }
        
        return api_metrics
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        logger.info("Collecting system metrics...")
        
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_io": dict(psutil.net_io_counters()._asdict()),
            "timestamp": datetime.now().isoformat()
        }
    
    def collect_monitoring_metrics(self) -> Dict[str, Any]:
        """Collect monitoring system metrics"""
        logger.info("Collecting monitoring metrics...")
        
        monitoring_metrics = {}
        
        # Check Prometheus
        try:
            response = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
            if response.status_code == 200:
                targets_data = response.json()
                monitoring_metrics["prometheus"] = {
                    "status": "healthy",
                    "targets": len(targets_data.get("data", {}).get("activeTargets", []))
                }
            else:
                monitoring_metrics["prometheus"] = {"status": "unhealthy"}
        except Exception as e:
            monitoring_metrics["prometheus"] = {"status": "unreachable", "error": str(e)}
        
        # Check Grafana
        try:
            response = requests.get("http://localhost:3000/api/health", timeout=5)
            if response.status_code == 200:
                monitoring_metrics["grafana"] = {"status": "healthy"}
            else:
                monitoring_metrics["grafana"] = {"status": "unhealthy"}
        except Exception as e:
            monitoring_metrics["grafana"] = {"status": "unreachable", "error": str(e)}
        
        return monitoring_metrics
    
    def generate_performance_charts(self):
        """Generate performance visualization charts"""
        logger.info("Generating performance charts...")
        
        # Model performance chart
        if "model_metrics" in self.report_data:
            metrics = self.report_data["model_metrics"]
            if isinstance(metrics, dict) and "metrics" in metrics:
                model_metrics = metrics["metrics"]
                
                fig, axes = plt.subplots(2, 2, figsize=(12, 10))
                fig.suptitle('Model Performance Metrics', fontsize=16)
                
                # Accuracy
                axes[0, 0].bar(['Accuracy'], [model_metrics.get('accuracy', 0)])
                axes[0, 0].set_ylim(0, 1)
                axes[0, 0].set_title('Accuracy')
                
                # Precision
                axes[0, 1].bar(['Precision'], [model_metrics.get('precision', 0)])
                axes[0, 1].set_ylim(0, 1)
                axes[0, 1].set_title('Precision')
                
                # Recall
                axes[1, 0].bar(['Recall'], [model_metrics.get('recall', 0)])
                axes[1, 0].set_ylim(0, 1)
                axes[1, 0].set_title('Recall')
                
                # F1 Score
                axes[1, 1].bar(['F1 Score'], [model_metrics.get('f1_score', 0)])
                axes[1, 1].set_ylim(0, 1)
                axes[1, 1].set_title('F1 Score')
                
                plt.tight_layout()
                plt.savefig(self.report_dir / "performance_metrics.png", dpi=300, bbox_inches='tight')
                plt.close()
        
        # System metrics chart
        if "system_metrics" in self.report_data:
            system_metrics = self.report_data["system_metrics"]
            
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle('System Performance Metrics', fontsize=16)
            
            # CPU Usage
            axes[0, 0].pie([system_metrics.get('cpu_percent', 0), 100 - system_metrics.get('cpu_percent', 0)], 
                          labels=['Used', 'Free'], autopct='%1.1f%%')
            axes[0, 0].set_title('CPU Usage')
            
            # Memory Usage
            axes[0, 1].pie([system_metrics.get('memory_percent', 0), 100 - system_metrics.get('memory_percent', 0)], 
                          labels=['Used', 'Free'], autopct='%1.1f%%')
            axes[0, 1].set_title('Memory Usage')
            
            # Disk Usage
            axes[1, 0].pie([system_metrics.get('disk_percent', 0), 100 - system_metrics.get('disk_percent', 0)], 
                          labels=['Used', 'Free'], autopct='%1.1f%%')
            axes[1, 0].set_title('Disk Usage')
            
            # Network I/O
            network_io = system_metrics.get('network_io', {})
            if network_io:
                axes[1, 1].bar(['Bytes Sent', 'Bytes Recv'], 
                              [network_io.get('bytes_sent', 0) / 1024 / 1024, 
                               network_io.get('bytes_recv', 0) / 1024 / 1024])
                axes[1, 1].set_title('Network I/O (MB)')
                axes[1, 1].set_ylabel('MB')
            
            plt.tight_layout()
            plt.savefig(self.report_dir / "system_metrics.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def generate_summary_report(self) -> str:
        """Generate a human-readable summary report"""
        logger.info("Generating summary report...")
        
        summary = []
        summary.append("=" * 60)
        summary.append("CORE DEFENDER MLOPS PERFORMANCE REPORT")
        summary.append("=" * 60)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        # Model Performance Summary
        summary.append("MODEL PERFORMANCE:")
        summary.append("-" * 20)
        if "model_metrics" in self.report_data and "model_metrics" in self.report_data["model_metrics"]:
            metrics = self.report_data["model_metrics"]["model_metrics"]
            if "metrics" in metrics:
                model_metrics = metrics["metrics"]
                summary.append(f"Accuracy:    {model_metrics.get('accuracy', 'N/A'):.3f}")
                summary.append(f"Precision:   {model_metrics.get('precision', 'N/A'):.3f}")
                summary.append(f"Recall:      {model_metrics.get('recall', 'N/A'):.3f}")
                summary.append(f"F1 Score:    {model_metrics.get('f1_score', 'N/A'):.3f}")
        else:
            summary.append("Model metrics not available")
        summary.append("")
        
        # API Performance Summary
        summary.append("API PERFORMANCE:")
        summary.append("-" * 20)
        if "api_metrics" in self.report_data:
            api_metrics = self.report_data["api_metrics"]
            summary.append(f"API Status:  {api_metrics.get('api_status', 'Unknown')}")
            
            if "prediction_test" in api_metrics:
                pred_test = api_metrics["prediction_test"]
                summary.append(f"Prediction:  {pred_test.get('status', 'Unknown')}")
                if pred_test.get('status') == 'success':
                    summary.append(f"Response Time: {pred_test.get('response_time_ms', 0):.2f} ms")
        else:
            summary.append("API metrics not available")
        summary.append("")
        
        # System Performance Summary
        summary.append("SYSTEM PERFORMANCE:")
        summary.append("-" * 20)
        if "system_metrics" in self.report_data:
            sys_metrics = self.report_data["system_metrics"]
            summary.append(f"CPU Usage:   {sys_metrics.get('cpu_percent', 0):.1f}%")
            summary.append(f"Memory Usage: {sys_metrics.get('memory_percent', 0):.1f}%")
            summary.append(f"Disk Usage:   {sys_metrics.get('disk_percent', 0):.1f}%")
        else:
            summary.append("System metrics not available")
        summary.append("")
        
        # Monitoring Summary
        summary.append("MONITORING STATUS:")
        summary.append("-" * 20)
        if "monitoring_metrics" in self.report_data:
            mon_metrics = self.report_data["monitoring_metrics"]
            summary.append(f"Prometheus:  {mon_metrics.get('prometheus', {}).get('status', 'Unknown')}")
            summary.append(f"Grafana:     {mon_metrics.get('grafana', {}).get('status', 'Unknown')}")
        else:
            summary.append("Monitoring metrics not available")
        summary.append("")
        
        # Overall Health Assessment
        summary.append("OVERALL HEALTH ASSESSMENT:")
        summary.append("-" * 25)
        
        health_score = 0
        total_checks = 0
        
        # Check model performance
        if "model_metrics" in self.report_data:
            total_checks += 1
            if "model_metrics" in self.report_data["model_metrics"]:
                metrics = self.report_data["model_metrics"]["model_metrics"]
                if "metrics" in metrics and metrics["metrics"].get('accuracy', 0) > 0.8:
                    health_score += 1
        
        # Check API status
        if "api_metrics" in self.report_data:
            total_checks += 1
            if self.report_data["api_metrics"].get('api_status') == 'healthy':
                health_score += 1
        
        # Check system resources
        if "system_metrics" in self.report_data:
            total_checks += 1
            sys_metrics = self.report_data["system_metrics"]
            if (sys_metrics.get('cpu_percent', 100) < 80 and 
                sys_metrics.get('memory_percent', 100) < 80 and 
                sys_metrics.get('disk_percent', 100) < 90):
                health_score += 1
        
        # Check monitoring
        if "monitoring_metrics" in self.report_data:
            total_checks += 1
            mon_metrics = self.report_data["monitoring_metrics"]
            if (mon_metrics.get('prometheus', {}).get('status') == 'healthy' and
                mon_metrics.get('grafana', {}).get('status') == 'healthy'):
                health_score += 1
        
        health_percentage = (health_score / total_checks * 100) if total_checks > 0 else 0
        
        if health_percentage >= 80:
            status = "EXCELLENT"
        elif health_percentage >= 60:
            status = "GOOD"
        elif health_percentage >= 40:
            status = "FAIR"
        else:
            status = "POOR"
        
        summary.append(f"Health Score: {health_percentage:.1f}% ({status})")
        summary.append(f"Passed Checks: {health_score}/{total_checks}")
        summary.append("")
        summary.append("=" * 60)
        
        return "\n".join(summary)
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        logger.info("Starting performance report generation...")
        
        # Collect all metrics
        self.report_data["model_metrics"] = self.collect_model_performance()
        self.report_data["api_metrics"] = self.collect_api_performance()
        self.report_data["system_metrics"] = self.collect_system_metrics()
        self.report_data["monitoring_metrics"] = self.collect_monitoring_metrics()
        
        # Generate charts
        self.generate_performance_charts()
        
        # Generate summary
        summary = self.generate_summary_report()
        
        # Save detailed report
        report_path = self.report_dir / "performance_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        # Save summary report
        summary_path = self.report_dir / "performance_summary.txt"
        with open(summary_path, 'w') as f:
            f.write(summary)
        
        # Print summary
        print(summary)
        
        logger.info(f"Performance report saved to {report_path}")
        logger.info(f"Performance summary saved to {summary_path}")
        
        return self.report_data

def main():
    """Main function"""
    reporter = PerformanceReporter()
    
    try:
        report = reporter.generate_report()
        print("\n✅ Performance report generated successfully!")
        exit(0)
    except Exception as e:
        logger.error(f"Error generating performance report: {str(e)}")
        print(f"\n❌ Error generating performance report: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 
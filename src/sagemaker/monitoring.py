import boto3
import sagemaker
from sagemaker.model_monitor import DataCaptureConfig, ModelMonitor
from sagemaker.model_monitor.dataset_format import DatasetFormat
import json
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SageMakerMonitor:
    def __init__(self, endpoint_name, region='us-west-2', bucket_name='coredefender.madhu'):
        """Initialize SageMaker monitoring"""
        self.endpoint_name = endpoint_name
        self.region = region
        self.bucket_name = bucket_name
        
        # Initialize AWS clients
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        
        # Initialize SageMaker session
        self.sagemaker_session = sagemaker.Session()
        
        logger.info(f"Initialized monitoring for endpoint: {endpoint_name}")
    
    def enable_data_capture(self):
        """Enable data capture for the endpoint"""
        try:
            data_capture_config = DataCaptureConfig(
                enable_capture=True,
                sampling_percentage=100,
                destination_s3_uri=f's3://{self.bucket_name}/datacapture',
                capture_options=['REQUEST', 'RESPONSE'],
                csv_content_types=['text/csv'],
                json_content_types=['application/json']
            )
            
            # Update endpoint configuration
            self.sagemaker_client.update_endpoint(
                EndpointName=self.endpoint_name,
                DataCaptureConfig=data_capture_config.to_dict()
            )
            
            logger.info("Data capture enabled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling data capture: {e}")
            raise
    
    def create_monitoring_schedule(self, baseline_dataset_uri):
        """Create model monitoring schedule"""
        try:
            monitor = ModelMonitor(
                role=self.sagemaker_session.get_execution_role(),
                instance_count=1,
                instance_type='ml.m5.xlarge',
                volume_size_in_gb=20,
                max_runtime_in_seconds=3600,
                base_job_name='predictive-maintenance-monitor'
            )
            
            # Create baseline
            monitor.suggest_baseline(
                baseline_dataset=baseline_dataset_uri,
                dataset_format=DatasetFormat.csv,
                output_s3_uri=f's3://{self.bucket_name}/monitoring/baseline'
            )
            
            # Create monitoring schedule
            monitoring_schedule_name = f"{self.endpoint_name}-monitor-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            monitor.create_monitoring_schedule(
                endpoint_input=self.endpoint_name,
                schedule_cron_expression='cron(0 * ? * * *)',  # Hourly monitoring
                output_s3_uri=f's3://{self.bucket_name}/monitoring/reports',
                statistics=monitor.baseline_statistics(),
                constraints=monitor.suggested_constraints(),
                schedule_name=monitoring_schedule_name,
                enable_cloudwatch_metrics=True
            )
            
            logger.info(f"Created monitoring schedule: {monitoring_schedule_name}")
            return monitoring_schedule_name
            
        except Exception as e:
            logger.error(f"Error creating monitoring schedule: {e}")
            raise
    
    def create_cloudwatch_dashboard(self):
        """Create CloudWatch dashboard for model monitoring"""
        try:
            dashboard_name = f"predictive-maintenance-{self.endpoint_name}"
            
            dashboard_body = {
                "widgets": [
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["AWS/SageMaker/Endpoints", "Invocations", "EndpointName", self.endpoint_name],
                                [".", "ModelLatency", ".", "."],
                                [".", "OverheadLatency", ".", "."]
                            ],
                            "period": 300,
                            "stat": "Average",
                            "region": self.region,
                            "title": "Endpoint Performance"
                        }
                    },
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["AWS/SageMaker/Endpoints", "CPUUtilization", "EndpointName", self.endpoint_name],
                                [".", "MemoryUtilization", ".", "."],
                                [".", "DiskUtilization", ".", "."]
                            ],
                            "period": 300,
                            "stat": "Average",
                            "region": self.region,
                            "title": "Resource Utilization"
                        }
                    },
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["AWS/SageMaker/ModelMonitoring", "DatasetObjectCount", "MonitoringScheduleName", "${monitoring_schedule_name}"],
                                [".", "DroppedDatasetObjectCount", ".", "."]
                            ],
                            "period": 3600,
                            "stat": "Sum",
                            "region": self.region,
                            "title": "Data Quality Metrics"
                        }
                    }
                ]
            }
            
            # Create dashboard
            self.cloudwatch.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body)
            )
            
            logger.info(f"Created CloudWatch dashboard: {dashboard_name}")
            return dashboard_name
            
        except Exception as e:
            logger.error(f"Error creating CloudWatch dashboard: {e}")
            raise
    
    def create_alarms(self):
        """Create CloudWatch alarms for monitoring"""
        try:
            alarms = [
                {
                    "name": f"{self.endpoint_name}-model-latency",
                    "metric_name": "ModelLatency",
                    "threshold": 1000,  # 1 second
                    "comparison": "GreaterThanThreshold",
                    "period": 300,  # 5 minutes
                    "evaluation_periods": 3
                },
                {
                    "name": f"{self.endpoint_name}-error-rate",
                    "metric_name": "Invocation4XXErrors",
                    "threshold": 5,
                    "comparison": "GreaterThanThreshold",
                    "period": 300,
                    "evaluation_periods": 2
                },
                {
                    "name": f"{self.endpoint_name}-cpu-utilization",
                    "metric_name": "CPUUtilization",
                    "threshold": 85,
                    "comparison": "GreaterThanThreshold",
                    "period": 300,
                    "evaluation_periods": 3
                }
            ]
            
            for alarm in alarms:
                self.cloudwatch.put_metric_alarm(
                    AlarmName=alarm["name"],
                    MetricName=alarm["metric_name"],
                    Namespace="AWS/SageMaker/Endpoints",
                    Statistic="Average",
                    Dimensions=[{"Name": "EndpointName", "Value": self.endpoint_name}],
                    Period=alarm["period"],
                    EvaluationPeriods=alarm["evaluation_periods"],
                    Threshold=alarm["threshold"],
                    ComparisonOperator=alarm["comparison"],
                    ActionsEnabled=True
                )
            
            logger.info("Created CloudWatch alarms")
            return True
            
        except Exception as e:
            logger.error(f"Error creating alarms: {e}")
            raise

def main():
    """Main function to set up monitoring"""
    try:
        # Get endpoint name from environment or config
        endpoint_name = "predictive-maintenance-endpoint"  # Replace with your endpoint name
        
        # Initialize monitor
        monitor = SageMakerMonitor(endpoint_name)
        
        # Enable data capture
        monitor.enable_data_capture()
        
        # Create monitoring schedule
        baseline_uri = f's3://{monitor.bucket_name}/baseline/processed_data.csv'
        schedule_name = monitor.create_monitoring_schedule(baseline_uri)
        
        # Create CloudWatch dashboard
        dashboard_name = monitor.create_cloudwatch_dashboard()
        
        # Create alarms
        monitor.create_alarms()
        
        logger.info("🎉 Monitoring setup completed successfully!")
        logger.info(f"Dashboard URL: https://{monitor.region}.console.aws.amazon.com/cloudwatch/home?region={monitor.region}#dashboards:name={dashboard_name}")
        
    except Exception as e:
        logger.error(f"Monitoring setup failed: {e}")
        raise

if __name__ == '__main__':
    main() 
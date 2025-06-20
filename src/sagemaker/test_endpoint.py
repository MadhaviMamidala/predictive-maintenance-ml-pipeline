import boto3
import json
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EndpointTester:
    def __init__(self, endpoint_name, region='us-west-2'):
        """Initialize endpoint tester"""
        self.endpoint_name = endpoint_name
        self.region = region
        self.runtime_client = boto3.client('sagemaker-runtime', region_name=region)
        
    def test_prediction(self, test_data):
        """Test prediction with sample data"""
        try:
            response = self.runtime_client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(test_data)
            )
            
            result = json.loads(response['Body'].read().decode())
            logger.info(f"Prediction result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
    
    def run_comprehensive_test(self):
        """Run comprehensive endpoint testing"""
        logger.info("Starting comprehensive endpoint testing...")
        
        # Test cases
        test_cases = [
            {
                "name": "Normal Operation",
                "data": {
                    "volt": 170.0,
                    "rotate": 1388.0,
                    "pressure": 113.0,
                    "vibration": 40.0,
                    "age": 15.0
                }
            },
            {
                "name": "High Pressure Warning",
                "data": {
                    "volt": 175.0,
                    "rotate": 1400.0,
                    "pressure": 150.0,  # High pressure
                    "vibration": 45.0,
                    "age": 20.0
                }
            },
            {
                "name": "High Vibration Alert",
                "data": {
                    "volt": 165.0,
                    "rotate": 1350.0,
                    "pressure": 110.0,
                    "vibration": 60.0,  # High vibration
                    "age": 25.0
                }
            },
            {
                "name": "Aged Equipment",
                "data": {
                    "volt": 160.0,
                    "rotate": 1300.0,
                    "pressure": 105.0,
                    "vibration": 35.0,
                    "age": 50.0  # Old equipment
                }
            }
        ]
        
        results = []
        for test_case in test_cases:
            logger.info(f"Testing: {test_case['name']}")
            try:
                result = self.test_prediction(test_case['data'])
                results.append({
                    "test_case": test_case['name'],
                    "input": test_case['data'],
                    "output": result,
                    "status": "SUCCESS"
                })
            except Exception as e:
                results.append({
                    "test_case": test_case['name'],
                    "input": test_case['data'],
                    "error": str(e),
                    "status": "FAILED"
                })
            
            time.sleep(1)  # Rate limiting
        
        # Generate test report
        self.generate_test_report(results)
        return results
    
    def generate_test_report(self, results):
        """Generate comprehensive test report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "endpoint_name": self.endpoint_name,
            "total_tests": len(results),
            "successful_tests": len([r for r in results if r['status'] == 'SUCCESS']),
            "failed_tests": len([r for r in results if r['status'] == 'FAILED']),
            "test_results": results
        }
        
        # Save report
        with open(f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test report generated: {report['successful_tests']}/{report['total_tests']} tests passed")
        return report

def main():
    """Main testing function"""
    endpoint_name = "predictive-maintenance-1750363630"  # Update with actual endpoint name
    
    try:
        tester = EndpointTester(endpoint_name)
        results = tester.run_comprehensive_test()
        
        logger.info("Endpoint testing completed successfully!")
        
    except Exception as e:
        logger.error(f"Endpoint testing failed: {e}")
        raise

if __name__ == '__main__':
    main() 
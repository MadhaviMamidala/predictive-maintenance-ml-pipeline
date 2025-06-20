import webbrowser
import time
import requests

def check_service(url, name):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def open_monitoring_dashboards():
    """Open monitoring dashboards in browser"""
    print("🔍 Checking monitoring services...")
    
    # Check services
    prometheus_ok = check_service("http://localhost:9090", "Prometheus")
    grafana_ok = check_service("http://localhost:3000", "Grafana")
    api_ok = check_service("http://localhost:8000/health", "API")
    
    print(f"📊 Prometheus: {'✅ Running' if prometheus_ok else '❌ Not accessible'}")
    print(f"📈 Grafana: {'✅ Running' if grafana_ok else '❌ Not accessible'}")
    print(f"🤖 API: {'✅ Running' if api_ok else '❌ Not accessible'}")
    
    if prometheus_ok:
        print("\n🌐 Opening Prometheus dashboard...")
        webbrowser.open("http://localhost:9090")
        
        # Wait a moment
        time.sleep(2)
        
        # Show how to view metrics
        print("\n📋 In Prometheus, you can:")
        print("  1. Go to 'Graph' tab")
        print("  2. Try these queries:")
        print("     - http_requests_total")
        print("     - model_predictions_total")
        print("     - http_request_duration_seconds")
        print("     - prediction_errors_total")
    
    if grafana_ok:
        print("\n🌐 Opening Grafana dashboard...")
        webbrowser.open("http://localhost:3000")
        
        print("\n📋 In Grafana:")
        print("  1. Login with admin/admin")
        print("  2. Add Prometheus as data source:")
        print("     - URL: http://prometheus:9090")
        print("  3. Create dashboard with metrics")
    
    if api_ok:
        print("\n🌐 Opening API documentation...")
        webbrowser.open("http://localhost:8000/docs")
    
    print("\n🎯 Quick Access URLs:")
    print("  📊 Prometheus: http://localhost:9090")
    print("  📈 Grafana: http://localhost:3000")
    print("  🤖 API Docs: http://localhost:8000/docs")
    print("  📋 API Metrics: http://localhost:8000/metrics")

if __name__ == "__main__":
    open_monitoring_dashboards() 
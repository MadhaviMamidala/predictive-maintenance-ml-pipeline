#!/usr/bin/env python3
"""
Ready Dashboard Setup Script
Sets up Grafana with auto-loading dashboards
"""

import webbrowser
import time
import requests
import subprocess
import json

def check_service(url, name):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def setup_prometheus_datasource():
    """Set up Prometheus data source via API"""
    try:
        # Grafana API endpoint for data sources
        url = "http://localhost:3000/api/datasources"
        
        # Data source configuration
        datasource_config = {
            "name": "Prometheus",
            "type": "prometheus",
            "access": "proxy",
            "url": "http://prometheus:9090",
            "isDefault": True,
            "editable": True
        }
        
        # Add data source
        response = requests.post(
            url,
            json=datasource_config,
            auth=('admin', 'admin'),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 409]:  # 409 means already exists
            print("✅ Prometheus data source configured")
            return True
        else:
            print(f"⚠️  Data source setup returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not auto-configure data source: {e}")
        return False

def main():
    print("🎨 Ready Dashboard Setup")
    print("=" * 50)
    
    # Check services
    print("🔍 Checking services...")
    prometheus_ok = check_service("http://localhost:9090", "Prometheus")
    grafana_ok = check_service("http://localhost:3000", "Grafana")
    api_ok = check_service("http://localhost:8000/health", "API")
    
    print(f"📊 Prometheus: {'✅ Running' if prometheus_ok else '❌ Not running'}")
    print(f"📈 Grafana: {'✅ Running' if grafana_ok else '❌ Not running'}")
    print(f"🤖 API: {'✅ Running' if api_ok else '❌ Not running'}")
    
    if not all([prometheus_ok, grafana_ok, api_ok]):
        print("\n⚠️  Starting monitoring stack...")
        try:
            subprocess.run(["docker-compose", "up", "-d", "prometheus", "grafana"], check=True)
            print("⏳ Waiting for services to start...")
            time.sleep(15)
        except Exception as e:
            print(f"❌ Failed to start services: {e}")
            return
    
    # Wait for Grafana to be fully ready
    print("\n⏳ Waiting for Grafana to be ready...")
    time.sleep(10)
    
    # Try to auto-configure data source
    print("\n🔧 Setting up Prometheus data source...")
    datasource_ok = setup_prometheus_datasource()
    
    print("\n🌐 Opening Grafana...")
    webbrowser.open("http://localhost:3000")
    
    print("\n🔑 Login Credentials:")
    print("   Username: admin")
    print("   Password: admin")
    
    print("\n📋 What You'll See After Login:")
    print("   1. Go to Dashboards → Browse")
    print("   2. Look for these dashboards:")
    print("      - 'ML Predictive Maintenance - Simple Dashboard'")
    print("      - 'ML Predictive Maintenance - Auto Dashboard'")
    print("      - 'ML Predictive Maintenance Dashboard'")
    
    if not datasource_ok:
        print("\n⚠️  Manual Data Source Setup Required:")
        print("   1. Login to Grafana")
        print("   2. Go to Configuration → Data Sources")
        print("   3. Add Prometheus")
        print("   4. URL: http://prometheus:9090")
        print("   5. Save & Test")
    
    print("\n🎯 Dashboard Features:")
    print("   🚀 Real-time API request graphs")
    print("   📊 Total predictions counter")
    print("   ⚡ Response time monitoring")
    print("   🟢 API health status")
    print("   🎯 ML model success rates")
    print("   ❌ Error tracking")
    print("   📈 Status distribution charts")
    
    print("\n🧪 Generate Live Data:")
    print("   Run: python src/test_monitoring.py")
    
    print("\n🔗 Quick Access:")
    print("   📈 Grafana: http://localhost:3000")
    print("   📊 Prometheus: http://localhost:9090")
    print("   🤖 API Docs: http://localhost:8000/docs")
    
    print("\n💡 Tips:")
    print("   - Dashboards auto-refresh every 5 seconds")
    print("   - Use time range selector for historical data")
    print("   - Click panels for detailed metrics")
    print("   - Generate more data to see live updates")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Visual Monitoring Dashboard Opener
Opens Grafana and Prometheus dashboards for ML monitoring
"""

import webbrowser
import time
import requests
import subprocess
import sys
from pathlib import Path

def check_service(url, name):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🎨 ML Visual Monitoring Dashboard Opener")
    print("=" * 50)
    
    # Check services
    print("🔍 Checking monitoring services...")
    
    prometheus_ok = check_service("http://localhost:9090", "Prometheus")
    grafana_ok = check_service("http://localhost:3000", "Grafana")
    api_ok = check_service("http://localhost:8000/health", "API")
    
    print(f"📊 Prometheus: {'✅ Running' if prometheus_ok else '❌ Not running'}")
    print(f"📈 Grafana: {'✅ Running' if grafana_ok else '❌ Not running'}")
    print(f"🤖 API: {'✅ Running' if api_ok else '❌ Not running'}")
    
    if not all([prometheus_ok, grafana_ok, api_ok]):
        print("\n⚠️  Some services are not running. Starting monitoring stack...")
        try:
            subprocess.run(["docker-compose", "up", "-d", "prometheus", "grafana"], check=True)
            print("⏳ Waiting for services to start...")
            time.sleep(10)
        except Exception as e:
            print(f"❌ Failed to start services: {e}")
            return
    
    print("\n🌐 Opening Visual Monitoring Dashboards...")
    print()
    
    # Open Grafana
    print("📈 Opening Grafana Dashboard...")
    print("   Login: admin / admin")
    print("   Look for: 'ML Predictive Maintenance - Visual Dashboard'")
    webbrowser.open("http://localhost:3000")
    
    time.sleep(2)
    
    # Open Prometheus
    print("\n📊 Opening Prometheus Dashboard...")
    print("   Try these visual queries:")
    print("   - rate(http_requests_total[5m])")
    print("   - model_predictions_total")
    print("   - http_request_duration_seconds")
    webbrowser.open("http://localhost:9090")
    
    time.sleep(2)
    
    # Open API docs
    print("\n🤖 Opening API Documentation...")
    print("   Test predictions directly in the browser")
    webbrowser.open("http://localhost:8000/docs")
    
    print("\n🎯 Visual Dashboard Features:")
    print("   🚀 Real-time API request rate graphs")
    print("   🎯 Prediction success rate with color coding")
    print("   ⚡ Response time trends")
    print("   ❌ Error rate monitoring")
    print("   📊 Total predictions counter")
    print("   🟢 API health status")
    print("   📊 Request status distribution (pie chart)")
    print("   🔥 Prediction confidence distribution")
    print("   📊 Model performance metrics table")
    
    print("\n🔗 Quick Access URLs:")
    print("   📈 Grafana: http://localhost:3000")
    print("   📊 Prometheus: http://localhost:9090")
    print("   🤖 API Docs: http://localhost:8000/docs")
    print("   📋 Raw Metrics: http://localhost:8000/metrics")
    
    print("\n💡 Tips:")
    print("   - Refresh dashboards every 5 seconds")
    print("   - Use time range selector for historical data")
    print("   - Click on panels to see detailed metrics")
    print("   - Generate more data with: python src/test_monitoring.py")

if __name__ == "__main__":
    main() 
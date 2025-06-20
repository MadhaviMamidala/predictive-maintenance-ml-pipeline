#!/usr/bin/env python3
"""
Grafana Login Helper
Helps you access Grafana with the correct credentials
"""

import webbrowser
import time
import requests

def main():
    print("🔐 Grafana Login Helper")
    print("=" * 40)
    
    # Check if Grafana is running
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Grafana is running and accessible!")
        else:
            print("❌ Grafana is not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Grafana: {e}")
        return
    
    print("\n🌐 Opening Grafana login page...")
    webbrowser.open("http://localhost:3000")
    
    print("\n🔑 Login Credentials:")
    print("   Username: admin")
    print("   Password: admin")
    
    print("\n📋 Step-by-step instructions:")
    print("1. Wait for the login page to load")
    print("2. Enter username: admin")
    print("3. Enter password: admin")
    print("4. Click 'Log In'")
    
    print("\n🎯 After login, you can:")
    print("   - Add Prometheus as data source")
    print("   - Create beautiful dashboards")
    print("   - View real-time ML metrics")
    
    print("\n🔗 Quick Access:")
    print("   Grafana: http://localhost:3000")
    print("   Prometheus: http://localhost:9090")
    print("   API Docs: http://localhost:8000/docs")
    
    print("\n💡 If login still fails:")
    print("   - Try refreshing the page")
    print("   - Clear browser cache")
    print("   - Check if Docker containers are running")

if __name__ == "__main__":
    main() 
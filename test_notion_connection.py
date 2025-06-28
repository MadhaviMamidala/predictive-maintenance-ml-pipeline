#!/usr/bin/env python3
"""
Simple Notion Connection Test
============================
Tests if we can connect to Notion using the REST API
"""

import requests
import json

# Your Notion integration token
NOTION_TOKEN = "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"

def test_notion_connection():
    """Test basic connection to Notion API"""
    print("🔗 Testing Notion API Connection...")
    print("=" * 50)
    
    # Notion API configuration
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # Test with a simple search request
        url = f"{base_url}/search"
        payload = {}
        
        print(f"Making request to: {url}")
        print(f"Using token: {NOTION_TOKEN[:20]}...")
        
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            print("✅ Connection successful!")
            print(f"Found {len(results)} accessible items in your workspace")
            
            if results:
                print("\n📄 Accessible content:")
                for i, item in enumerate(results[:5], 1):
                    item_type = item.get("object", "unknown")
                    
                    # Get title
                    title = "Untitled"
                    if item.get("properties"):
                        # For pages
                        for prop_name, prop_value in item["properties"].items():
                            if prop_value.get("type") == "title" and prop_value.get("title"):
                                if len(prop_value["title"]) > 0:
                                    title = prop_value["title"][0].get("text", {}).get("content", "Untitled")
                                break
                    elif item.get("title"):
                        # For databases
                        if len(item["title"]) > 0:
                            title = item["title"][0].get("text", {}).get("content", "Untitled")
                    
                    print(f"   {i}. {title} ({item_type})")
                    print(f"      ID: {item['id']}")
                
                if len(results) > 5:
                    print(f"   ... and {len(results) - 5} more items")
                
                print(f"\n🎯 Ready to create 'ML lifecycle project' page!")
                return True
            else:
                print("\n⚠️  No accessible content found.")
                print("To fix this:")
                print("1. Go to your Notion workspace")
                print("2. Create or open a page")
                print("3. Click 'Share' → 'Invite'")
                print("4. Add your integration with Read & Write permissions")
                return False
                
        elif response.status_code == 401:
            print("❌ Authentication failed!")
            print("Your integration token might be invalid or expired.")
            print("Please check your token and try again.")
            return False
            
        elif response.status_code == 403:
            print("❌ Access forbidden!")
            print("Your integration doesn't have permission to access this workspace.")
            print("Please share at least one page with your integration.")
            return False
            
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        print("Please check your internet connection.")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def create_ml_lifecycle_page_direct():
    """Create the ML lifecycle project page directly using API"""
    print("\n🚀 Creating 'ML lifecycle project' page...")
    
    # First, get a parent page
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # Search for pages to use as parent
        search_response = requests.post(f"{base_url}/search", headers=headers, json={})
        
        if search_response.status_code != 200:
            print("❌ Cannot find parent page")
            return False
        
        results = search_response.json().get("results", [])
        pages = [r for r in results if r.get("object") == "page"]
        
        if not pages:
            print("❌ No pages found to use as parent")
            print("Please create a page in Notion and share it with your integration")
            return False
        
        parent_page_id = pages[0]["id"]
        print(f"✅ Using parent page: {parent_page_id}")
        
        # Create the ML lifecycle project page
        page_data = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
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
                        "rich_text": [{"type": "text", "text": {"content": "Welcome to your ML project management system! This page will contain databases for tracking experiments, data pipeline, deployments, and tasks."}}]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "📊 Project Status"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": "🤖 Models: Ready for tracking experiments"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": "📊 Data Pipeline: Ready for monitoring"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": "🚀 Deployment: Ready for tracking"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": "📋 Tasks: Ready for project management"}}]
                    }
                }
            ]
        }
        
        response = requests.post(f"{base_url}/pages", headers=headers, json=page_data)
        
        if response.status_code == 200:
            page = response.json()
            print(f"✅ Created 'ML lifecycle project' page successfully!")
            print(f"   Page ID: {page['id']}")
            print(f"   URL: {page.get('url', 'N/A')}")
            return page["id"]
        else:
            print(f"❌ Failed to create page: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating page: {str(e)}")
        return False

if __name__ == "__main__":
    print("🤖 Notion Connection Test & Page Creation")
    print("=" * 60)
    
    # Test connection
    connection_ok = test_notion_connection()
    
    if connection_ok:
        # Try to create the ML lifecycle project page
        page_id = create_ml_lifecycle_page_direct()
        
        if page_id:
            print("\n🎉 Success!")
            print("Your 'ML lifecycle project' page has been created in Notion!")
            print("\nNext steps:")
            print("1. Go to your Notion workspace")
            print("2. Find the 'ML lifecycle project' page")
            print("3. You can now manually add databases or run the full setup script")
        else:
            print("\n❌ Page creation failed")
    else:
        print("\n❌ Connection test failed")
        print("Please fix the connection issues before proceeding") 
"""
Notion API Integration Example
=============================

This script demonstrates how to connect to your Notion workspace using the API.
Your integration token is already configured.

To use this script:
1. Make sure you have 'requests' installed: pip install requests
2. Share your Notion pages/databases with your integration
3. Run this script to see what's accessible

Your Integration Token: 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
"""

import requests
import json
from datetime import datetime

# Configuration
NOTION_TOKEN = "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"
BASE_URL = "https://api.notion.com/v1"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def make_notion_request(method, endpoint, data=None):
    """Make a request to the Notion API with error handling"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"API Request: {method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            return response.json(), None
        else:
            error_msg = f"API Error {response.status_code}: {response.text}"
            print(error_msg)
            return None, error_msg
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network Error: {str(e)}"
        print(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Unexpected Error: {str(e)}"
        print(error_msg)
        return None, error_msg

def search_workspace():
    """Search for all accessible content in the workspace"""
    print("🔍 Searching Notion workspace...")
    print("=" * 50)
    
    # Search for databases
    print("\n📊 Searching for databases...")
    db_data, db_error = make_notion_request("POST", "/search", {
        "filter": {"property": "object", "value": "database"}
    })
    
    databases = []
    if db_data:
        databases = db_data.get("results", [])
        print(f"Found {len(databases)} databases")
        
        for i, db in enumerate(databases, 1):
            title = get_title_from_object(db)
            print(f"  {i}. {title}")
            print(f"     ID: {db['id']}")
            print(f"     URL: {db.get('url', 'N/A')}")
    
    # Search for pages
    print("\n📄 Searching for pages...")
    page_data, page_error = make_notion_request("POST", "/search", {
        "filter": {"property": "object", "value": "page"}
    })
    
    pages = []
    if page_data:
        pages = page_data.get("results", [])
        print(f"Found {len(pages)} pages")
        
        for i, page in enumerate(pages[:5], 1):  # Show first 5
            title = get_title_from_object(page)
            print(f"  {i}. {title}")
            print(f"     ID: {page['id']}")
            print(f"     URL: {page.get('url', 'N/A')}")
        
        if len(pages) > 5:
            print(f"     ... and {len(pages) - 5} more pages")
    
    return databases, pages

def get_title_from_object(obj):
    """Extract title from a Notion object (database or page)"""
    # For databases
    if obj.get("title") and len(obj["title"]) > 0:
        return obj["title"][0].get("text", {}).get("content", "Untitled")
    
    # For pages
    if obj.get("properties"):
        for prop_name, prop_value in obj["properties"].items():
            if prop_value.get("type") == "title" and prop_value.get("title"):
                if len(prop_value["title"]) > 0:
                    return prop_value["title"][0].get("text", {}).get("content", "Untitled")
    
    return "Untitled"

def explore_database(database_id):
    """Explore a specific database structure and content"""
    print(f"\n🔍 Exploring database: {database_id}")
    print("-" * 50)
    
    # Get database structure
    db_info, error = make_notion_request("GET", f"/databases/{database_id}")
    
    if not db_info:
        print("❌ Could not access database")
        return
    
    title = get_title_from_object(db_info)
    print(f"Database: {title}")
    
    # Show properties
    properties = db_info.get("properties", {})
    print(f"\nProperties ({len(properties)}):")
    for prop_name, prop_info in properties.items():
        prop_type = prop_info.get("type", "unknown")
        print(f"  • {prop_name} ({prop_type})")
    
    # Query database content
    print(f"\nQuerying database content...")
    content, error = make_notion_request("POST", f"/databases/{database_id}/query", {})
    
    if content:
        results = content.get("results", [])
        print(f"Found {len(results)} entries")
        
        if results:
            print("\nFirst few entries:")
            for i, entry in enumerate(results[:3], 1):
                entry_title = get_title_from_object(entry)
                print(f"  {i}. {entry_title}")
                print(f"     ID: {entry['id']}")
    
    return db_info

def create_sample_page(database_id, title="Test Page"):
    """Create a sample page in a database"""
    print(f"\n✏️ Creating sample page: {title}")
    
    # First, get database structure to understand required properties
    db_info, error = make_notion_request("GET", f"/databases/{database_id}")
    
    if not db_info:
        print("❌ Could not access database structure")
        return None
    
    # Build properties for the new page
    properties = {}
    db_properties = db_info.get("properties", {})
    
    for prop_name, prop_info in db_properties.items():
        prop_type = prop_info.get("type")
        
        if prop_type == "title":
            properties[prop_name] = {
                "title": [{"text": {"content": title}}]
            }
        elif prop_type == "rich_text":
            properties[prop_name] = {
                "rich_text": [{"text": {"content": "Created via API"}}]
            }
        elif prop_type == "number":
            properties[prop_name] = {"number": 42}
        elif prop_type == "select":
            # You'd need to use valid options from the database
            pass
        elif prop_type == "date":
            properties[prop_name] = {"date": {"start": datetime.now().isoformat()}}
    
    # Create the page
    page_data = {
        "parent": {"database_id": database_id},
        "properties": properties
    }
    
    result, error = make_notion_request("POST", "/pages", page_data)
    
    if result:
        print(f"✅ Page created successfully!")
        print(f"   ID: {result['id']}")
        print(f"   URL: {result.get('url', 'N/A')}")
        return result
    else:
        print(f"❌ Failed to create page: {error}")
        return None

def main():
    """Main function to demonstrate Notion API usage"""
    print("🚀 Notion API Integration Test")
    print("=" * 50)
    print(f"Token: {NOTION_TOKEN[:20]}...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Search workspace
    databases, pages = search_workspace()
    
    if not databases and not pages:
        print("\n⚠️  No content found!")
        print("\nTo fix this:")
        print("1. Go to your Notion workspace")
        print("2. Open the page/database you want to access")
        print("3. Click 'Share' in the top right")
        print("4. Click 'Invite' and search for your integration")
        print("5. Add your integration with appropriate permissions")
        return
    
    print(f"\n✅ Found {len(databases)} databases and {len(pages)} pages")
    
    # If we have databases, explore the first one
    if databases:
        first_db = databases[0]
        db_id = first_db['id']
        
        print(f"\n🔍 Exploring first database...")
        explore_database(db_id)
        
        # Optionally create a sample page (uncomment to test)
        # create_sample_page(db_id, "API Test Page")
    
    print("\n" + "=" * 50)
    print("🎉 Notion API integration is working!")
    print("\nYou can now:")
    print("• Read data from databases and pages")
    print("• Create new pages and entries")
    print("• Update existing content")
    print("• Export data to JSON")

if __name__ == "__main__":
    main() 
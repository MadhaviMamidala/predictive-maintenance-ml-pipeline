import requests
import json

# Your Notion integration token
NOTION_TOKEN = "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"

# Notion API base URL
BASE_URL = "https://api.notion.com/v1"

# Headers for API requests
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def test_notion_connection():
    """Test basic connection to Notion API"""
    print("🚀 Testing Notion API Connection...")
    print("=" * 50)
    
    try:
        # Test with a simple search request
        url = f"{BASE_URL}/search"
        payload = {"filter": {"property": "object", "value": "database"}}
        
        print("Making API request...")
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            databases = data.get("results", [])
            
            print("✅ Connection successful!")
            print(f"Found {len(databases)} databases accessible to your integration")
            
            if databases:
                print("\n📊 Your databases:")
                for i, db in enumerate(databases, 1):
                    title = "Untitled"
                    if db.get("title") and len(db["title"]) > 0:
                        title = db["title"][0].get("text", {}).get("content", "Untitled")
                    
                    print(f"{i}. {title}")
                    print(f"   ID: {db['id']}")
                    print(f"   URL: {db.get('url', 'N/A')}")
                    print()
                
                return databases
            else:
                print("\n⚠️  No databases found.")
                print("This could mean:")
                print("1. Your integration hasn't been added to any databases")
                print("2. You need to share databases with your integration")
                print("3. The integration doesn't have the right permissions")
                
        elif response.status_code == 401:
            print("❌ Authentication failed!")
            print("Your integration token might be invalid or expired.")
            
        elif response.status_code == 403:
            print("❌ Access forbidden!")
            print("Your integration doesn't have permission to access this workspace.")
            
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        print("Check your internet connection.")
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    return []

def test_pages():
    """Test searching for pages"""
    print("\n🔍 Searching for pages...")
    
    try:
        url = f"{BASE_URL}/search"
        payload = {"filter": {"property": "object", "value": "page"}}
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get("results", [])
            
            print(f"Found {len(pages)} pages accessible to your integration")
            
            if pages:
                print("\n📄 Your pages:")
                for i, page in enumerate(pages[:5], 1):  # Show first 5 pages
                    title = "Untitled"
                    if page.get("properties"):
                        for prop_name, prop_value in page["properties"].items():
                            if prop_value.get("type") == "title" and prop_value.get("title"):
                                if len(prop_value["title"]) > 0:
                                    title = prop_value["title"][0].get("text", {}).get("content", "Untitled")
                                break
                    
                    print(f"{i}. {title}")
                    print(f"   ID: {page['id']}")
                    print(f"   URL: {page.get('url', 'N/A')}")
                    print()
                
                if len(pages) > 5:
                    print(f"... and {len(pages) - 5} more pages")
                    
            return pages
        else:
            print(f"Failed to search pages: {response.status_code}")
            
    except Exception as e:
        print(f"Error searching pages: {str(e)}")
    
    return []

if __name__ == "__main__":
    # Test connection
    databases = test_notion_connection()
    
    # Test pages
    pages = test_pages()
    
    print("\n" + "=" * 50)
    if databases or pages:
        print("🎉 Your Notion integration is working!")
        print("\nNext steps:")
        print("1. Choose a database ID to work with")
        print("2. Use the NotionClient class for more advanced operations")
        print("3. Create, read, update, or delete content")
    else:
        print("⚠️  Integration setup needed:")
        print("1. Go to your Notion workspace")
        print("2. Find the pages/databases you want to access")
        print("3. Share them with your integration")
        print("4. Make sure the integration has the right permissions") 
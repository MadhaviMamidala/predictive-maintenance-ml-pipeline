import requests
import json
from typing import Dict, List, Optional, Any
import os
from datetime import datetime

class NotionClient:
    def __init__(self, token: str):
        """
        Initialize Notion client with integration token
        
        Args:
            token: Notion integration token
        """
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def search(self, query: str = "", filter_type: str = None) -> Dict:
        """
        Search for pages and databases in Notion workspace
        
        Args:
            query: Search query string
            filter_type: Filter by 'page' or 'database'
        
        Returns:
            Dictionary containing search results
        """
        url = f"{self.base_url}/search"
        
        payload = {}
        if query:
            payload["query"] = query
        
        if filter_type:
            payload["filter"] = {"property": "object", "value": filter_type}
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error searching: {response.status_code} - {response.text}")
            return {}
    
    def get_database(self, database_id: str) -> Dict:
        """
        Get database information
        
        Args:
            database_id: The ID of the database
        
        Returns:
            Dictionary containing database information
        """
        url = f"{self.base_url}/databases/{database_id}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting database: {response.status_code} - {response.text}")
            return {}
    
    def query_database(self, database_id: str, filter_conditions: Dict = None, sorts: List = None) -> Dict:
        """
        Query a database for pages
        
        Args:
            database_id: The ID of the database
            filter_conditions: Filter conditions for the query
            sorts: Sort conditions for the query
        
        Returns:
            Dictionary containing query results
        """
        url = f"{self.base_url}/databases/{database_id}/query"
        
        payload = {}
        if filter_conditions:
            payload["filter"] = filter_conditions
        if sorts:
            payload["sorts"] = sorts
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error querying database: {response.status_code} - {response.text}")
            return {}
    
    def get_page(self, page_id: str) -> Dict:
        """
        Get page information
        
        Args:
            page_id: The ID of the page
        
        Returns:
            Dictionary containing page information
        """
        url = f"{self.base_url}/pages/{page_id}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting page: {response.status_code} - {response.text}")
            return {}
    
    def create_page(self, parent_id: str, properties: Dict, children: List = None) -> Dict:
        """
        Create a new page
        
        Args:
            parent_id: ID of the parent database or page
            properties: Properties for the new page
            children: Content blocks for the page
        
        Returns:
            Dictionary containing created page information
        """
        url = f"{self.base_url}/pages"
        
        payload = {
            "parent": {"database_id": parent_id},
            "properties": properties
        }
        
        if children:
            payload["children"] = children
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error creating page: {response.status_code} - {response.text}")
            return {}
    
    def update_page(self, page_id: str, properties: Dict) -> Dict:
        """
        Update page properties
        
        Args:
            page_id: The ID of the page to update
            properties: Properties to update
        
        Returns:
            Dictionary containing updated page information
        """
        url = f"{self.base_url}/pages/{page_id}"
        
        payload = {"properties": properties}
        
        response = requests.patch(url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error updating page: {response.status_code} - {response.text}")
            return {}
    
    def list_databases(self) -> List[Dict]:
        """
        List all databases accessible to the integration
        
        Returns:
            List of database dictionaries
        """
        search_result = self.search(filter_type="database")
        return search_result.get("results", [])
    
    def list_pages(self) -> List[Dict]:
        """
        List all pages accessible to the integration
        
        Returns:
            List of page dictionaries
        """
        search_result = self.search(filter_type="page")
        return search_result.get("results", [])
    
    def print_database_structure(self, database_id: str):
        """
        Print the structure of a database (properties and their types)
        
        Args:
            database_id: The ID of the database
        """
        db_info = self.get_database(database_id)
        
        if not db_info:
            print("Could not retrieve database information")
            return
        
        print(f"\nDatabase: {db_info.get('title', [{}])[0].get('text', {}).get('content', 'Untitled')}")
        print(f"ID: {database_id}")
        print("\nProperties:")
        
        properties = db_info.get("properties", {})
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get("type", "unknown")
            print(f"  - {prop_name}: {prop_type}")
    
    def export_database_to_json(self, database_id: str, filename: str = None):
        """
        Export database content to JSON file
        
        Args:
            database_id: The ID of the database
            filename: Output filename (optional)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"notion_export_{timestamp}.json"
        
        # Get database structure
        db_info = self.get_database(database_id)
        
        # Query all pages in the database
        pages = self.query_database(database_id)
        
        export_data = {
            "database_info": db_info,
            "pages": pages.get("results", []),
            "exported_at": datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Database exported to {filename}")
        return filename


# Initialize the client with your token
def create_notion_client():
    """Create and return a Notion client instance"""
    token = "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"
    return NotionClient(token)


# Example usage functions
def explore_notion_workspace():
    """Explore your Notion workspace - list databases and pages"""
    client = create_notion_client()
    
    print("=== EXPLORING NOTION WORKSPACE ===")
    
    # List all databases
    print("\n📊 DATABASES:")
    databases = client.list_databases()
    
    if databases:
        for i, db in enumerate(databases, 1):
            title = "Untitled"
            if db.get("title") and len(db["title"]) > 0:
                title = db["title"][0].get("text", {}).get("content", "Untitled")
            
            print(f"{i}. {title}")
            print(f"   ID: {db['id']}")
            print(f"   URL: {db.get('url', 'N/A')}")
            print()
    else:
        print("No databases found or accessible to this integration.")
    
    # List all pages
    print("\n📄 PAGES:")
    pages = client.list_pages()
    
    if pages:
        for i, page in enumerate(pages, 1):
            title = "Untitled"
            if page.get("properties"):
                # Try to get title from properties
                for prop_name, prop_value in page["properties"].items():
                    if prop_value.get("type") == "title" and prop_value.get("title"):
                        if len(prop_value["title"]) > 0:
                            title = prop_value["title"][0].get("text", {}).get("content", "Untitled")
                        break
            
            print(f"{i}. {title}")
            print(f"   ID: {page['id']}")
            print(f"   URL: {page.get('url', 'N/A')}")
            print()
    else:
        print("No pages found or accessible to this integration.")
    
    return databases, pages


if __name__ == "__main__":
    # Run the exploration
    explore_notion_workspace()
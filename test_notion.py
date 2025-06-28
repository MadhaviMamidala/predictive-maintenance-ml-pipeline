#!/usr/bin/env python3
"""
Test script to explore your Notion workspace
"""

import sys
import os

# Add src directory to path
sys.path.append('src')

from notion_client import create_notion_client, explore_notion_workspace

def main():
    """Main function to test Notion connection and explore workspace"""
    print("🚀 Testing Notion API Connection...")
    print("=" * 50)
    
    try:
        # Create client
        client = create_notion_client()
        
        # Test basic connection by exploring workspace
        databases, pages = explore_notion_workspace()
        
        print("\n" + "=" * 50)
        print("✅ Connection successful!")
        print(f"Found {len(databases)} databases and {len(pages)} pages")
        
        # If we found databases, let's explore the first one
        if databases:
            print("\n🔍 Exploring first database in detail...")
            first_db = databases[0]
            db_id = first_db['id']
            
            print(f"\nDatabase ID: {db_id}")
            client.print_database_structure(db_id)
            
            # Query some data from the database
            print("\n📊 Querying database content...")
            results = client.query_database(db_id)
            
            if results.get('results'):
                print(f"Found {len(results['results'])} entries in the database")
                
                # Show first entry as example
                if len(results['results']) > 0:
                    first_entry = results['results'][0]
                    print("\n📝 First entry properties:")
                    for prop_name, prop_value in first_entry.get('properties', {}).items():
                        prop_type = prop_value.get('type', 'unknown')
                        print(f"  - {prop_name} ({prop_type})")
            else:
                print("Database appears to be empty")
        
        print("\n" + "=" * 50)
        print("🎉 Notion API integration is working!")
        print("You can now use the NotionClient to:")
        print("  • Read data from databases")
        print("  • Create new pages/entries") 
        print("  • Update existing content")
        print("  • Export data to JSON")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nPossible issues:")
        print("1. Integration token might be invalid")
        print("2. Integration might not have access to any content")
        print("3. Network connection issues")
        print("\nMake sure your Notion integration has been:")
        print("- Added to the pages/databases you want to access")
        print("- Given appropriate permissions")

if __name__ == "__main__":
    main() 
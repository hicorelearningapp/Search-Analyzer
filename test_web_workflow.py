# test_web_workflow.py
from sources.web_search import WebSearchManager
import time

def test_web_search(query: str = "latest AI advancements", max_results: int = 3):
    """Test the web search functionality with better error reporting."""
    print(f"🔍 Testing web search for: '{query}'")
    
    try:
        # Initialize the web search manager
        search_manager = WebSearchManager(max_results=max_results)
        
        # Perform the search with timing
        start_time = time.time()
        results = search_manager.run(query)
        end_time = time.time()
        
        print(f"⏱️ Search completed in {end_time - start_time:.2f} seconds")
        
        # Check if there was an error
        if "Error:" in results:
            print(f"❌ Search failed with error: {results}")
            return None
        
        # Print the results
        print("\n📝 Search Results:")
        print("=" * 50)
        print(results)
        print("=" * 50)
        
        # Basic validation
        if "Top search results:" in results and "http" in results:
            print("✅ Search completed successfully!")
            return results
        else:
            print("⚠️ Unexpected result format")
            return results
            
    except Exception as e:
        print(f"❌ Exception during web search: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test with a default query or take user input
    test_query = input("Enter search query (or press Enter to use default): ").strip()
    if not test_query:
        test_query = "latest AI advancements"
        print(f"Using default query: '{test_query}'")
    
    result = test_web_search(test_query)
    
    if result is None:
        print("\n💡 Troubleshooting tips:")
        print("1. Check internet connection")
        print("2. Run: pip uninstall duckduckgo-search")
        print("3. Run: pip install ddgs")
        print("4. Try a different search query")
import os
import shutil
import sys
from pathlib import Path

def copy_directory(src, dst):
    """Copy directory from src to dst, overwriting existing files"""
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

def copy_file(src, dst):
    """Copy file from src to dst, creating parent directories if needed"""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)

def setup_search_analyzer():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    search_analyzer_dir = os.path.join(base_dir, "..", "Search-Analyzer")
    
    # Verify Search-Analyzer directory exists
    if not os.path.exists(search_analyzer_dir):
        print(f"Error: Search-Analyzer directory not found at {search_analyzer_dir}")
        return False
    
    # Create required directories
    target_dirs = [
        os.path.join(base_dir, "services", "search_analyzer"),
        os.path.join(base_dir, "summarizer"),
        os.path.join(base_dir, "reports")
    ]
    
    for dir_path in target_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # Copy required files and directories
    try:
        # Copy document system
        copy_file(
            os.path.join(search_analyzer_dir, "document_system.py"),
            os.path.join(base_dir, "services", "search_analyzer", "document_system.py")
        )
        
        # Copy services
        copy_directory(
            os.path.join(search_analyzer_dir, "services"),
            os.path.join(base_dir, "services", "search_analyzer", "services")
        )
        
        # Copy summarizer if it exists
        if os.path.exists(os.path.join(search_analyzer_dir, "summarizer")):
            copy_directory(
                os.path.join(search_analyzer_dir, "summarizer"),
                os.path.join(base_dir, "summarizer")
            )
        
        # Copy config file
        copy_file(
            os.path.join(search_analyzer_dir, "config.py"),
            os.path.join(base_dir, "services", "search_analyzer", "config.py")
        )
        
        # Create __init__.py files to make packages
        for root, dirs, _ in os.walk(os.path.join(base_dir, "services", "search_analyzer")):
            for d in dirs:
                init_file = os.path.join(root, d, "__init__.py")
                if not os.path.exists(init_file):
                    with open(init_file, 'w') as f:
                        f.write("")
        
        print("Search-Analyzer setup completed successfully!")
        print("\nNext steps:")
        print("1. Install required dependencies from Search-Analyzer/requirements.txt")
        print("2. Copy your .env file from Search-Analyzer to the root directory")
        print("3. Start the server with: uvicorn main:app --reload")
        
        return True
        
    except Exception as e:
        print(f"Error during setup: {str(e)}")
        return False

if __name__ == "__main__":
    setup_search_analyzer()

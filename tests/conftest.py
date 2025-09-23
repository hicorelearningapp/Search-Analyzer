import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test configurations
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_REPORTS_DIR = TEST_DATA_DIR / "reports"

# Create test directories if they don't exist
TEST_DATA_DIR.mkdir(exist_ok=True)
TEST_REPORTS_DIR.mkdir(exist_ok=True)

# Mock environment variables for testing
os.environ["OPENAI_API_KEY"] = "test_api_key"

@pytest.fixture(autouse=True)
def mock_settings():
    """Mock the settings for testing."""
    with patch('config.Config.REPORTS_DIR', str(TEST_REPORTS_DIR)):
        yield

@pytest.fixture
def temp_pdf():
    """Create a temporary PDF file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        yield tmp.name
    # Cleanup
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)

@pytest.fixture
def temp_txt():
    """Create a temporary text file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w+') as tmp:
        tmp.write("This is a test document content.")
        tmp.flush()
        yield tmp.name
    # Cleanup
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)

@pytest.fixture
def test_app():
    """Create a test FastAPI app instance."""
    from main import create_app
    app = create_app()
    return app

@pytest.fixture
async def async_client(test_app):
    """Create a test client for the FastAPI app."""
    from fastapi.testclient import TestClient
    async with TestClient(test_app) as client:
        yield client

# Common test data
TEST_DOC_TYPES = [
    "Research Paper Summary",
    "Blog Post",
    "Business Report",
    "Technical Whitepaper",
    "Presentation Outline",
    "News Brief",
    "Educational Lesson Plan"
]

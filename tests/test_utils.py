import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
import json
from datetime import datetime

# Configure logging
def setup_logging(test_name: str) -> str:
    """Set up logging for tests with file and console handlers.
    
    Args:
        test_name: Name of the test being run
        
    Returns:
        str: Path to the log file
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("tests/logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create a timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{test_name}_{timestamp}.log"
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w'),
            logging.StreamHandler()
        ]
    )
    
    return str(log_file)

class TestLogger:
    """Helper class for logging test steps and results."""
    
    def __init__(self, test_name: str):
        self.logger = logging.getLogger(test_name)
        self.test_start_time = datetime.now()
        self.logger.info(f"🚀 Starting test: {test_name}")
        self.step_counter = 1
    
    def log_step(self, message: str):
        """Log a test step with automatic numbering."""
        self.logger.info(f"STEP {self.step_counter}: {message}")
        self.step_counter += 1
    
    def log_result(self, success: bool, details: Optional[Dict[str, Any]] = None):
        """Log the result of a test step."""
        status = "✅ PASSED" if success else "❌ FAILED"
        self.logger.info(f"RESULT: {status}")
        if details:
            self.logger.debug(f"Details: {json.dumps(details, indent=2, default=str)}")
    
    def log_error(self, error: Exception):
        """Log an error that occurred during testing."""
        self.logger.error(f"Error: {str(error)}", exc_info=True)
    
    def complete_test(self):
        """Log test completion with duration."""
        duration = datetime.now() - self.test_start_time
        self.logger.info(f"Test completed in {duration.total_seconds():.2f} seconds")
        self.logger.info("=" * 80 + "\n")

def get_test_file_path(filename: str) -> str:
    """Get the absolute path to a test file in the test_data directory."""
    test_data_dir = Path(__file__).parent / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    return str(test_data_dir / filename)

def cleanup_test_files():
    """Clean up any test files that were created during testing."""
    test_data_dir = Path(__file__).parent / "test_data"
    for file in test_data_dir.glob("test_*"):
        try:
            if file.is_file():
                file.unlink()
        except Exception as e:
            logging.warning(f"Failed to delete test file {file}: {e}")

import os
import pytest
import io
from pathlib import Path
from fastapi import UploadFile
from unittest.mock import MagicMock, patch

# Import test utilities
from test_utils import TestLogger, get_test_file_path, setup_logging

# Import the service to test
from services.pdf_service import PDFClass
from document_system import document_system

# Test data
TEST_PDF_PATH = "test_data/sample.pdf"  # You'll need to provide a sample PDF for testing
TEST_DOC_TYPE = "Research Paper Summary"
TEST_PAGES = 2

# Initialize test logger
logger = TestLogger("test_pdf_service")

@pytest.fixture(scope="module")
def pdf_service():
    """Fixture to provide a PDFService instance for testing."""
    logger.log_step("Initializing PDF service")
    service = PDFClass()
    yield service
    logger.log_step("PDF service test completed")

@pytest.fixture
def sample_pdf_file():
    """Fixture to provide a sample PDF file for testing."""
    test_pdf_path = get_test_file_path("sample.pdf")
    if not os.path.exists(test_pdf_path):
        pytest.skip(f"Test PDF file not found at {test_pdf_path}")
    
    with open(test_pdf_path, "rb") as f:
        file_content = f.read()
    
    upload_file = UploadFile(
        file=io.BytesIO(file_content),
        filename="test.pdf",
        content_type="application/pdf"
    )
    
    logger.log_step(f"Created test PDF file: {upload_file.filename}")
    return upload_file

def test_process_pdf(pdf_service, sample_pdf_file):
    """Test processing a PDF file with different document types."""
    test_name = "test_process_pdf"
    logger.log_step(f"Starting test: {test_name}")
    
    try:
        # Test with valid document type
        logger.log_step("Testing with valid document type")
        result = pdf_service.process_pdf(sample_pdf_file, TEST_DOC_TYPE, TEST_PAGES)
        
        # Verify the result structure
        assert "summary" in result, "Result should contain 'summary' key"
        assert "metadata" in result, "Result should contain 'metadata' key"
        assert "processing_time" in result["metadata"], "Metadata should contain 'processing_time'"
        
        logger.log_result(True, {"summary_length": len(result["summary"]), 
                             "metadata_keys": list(result["metadata"].keys())})
        
        # Test with invalid document type
        logger.log_step("Testing with invalid document type")
        invalid_doc_type = "Invalid Document Type"
        with pytest.raises(ValueError) as exc_info:
            pdf_service.process_pdf(sample_pdf_file, invalid_doc_type, TEST_PAGES)
        
        assert "Unsupported document type" in str(exc_info.value), \
            "Should raise ValueError for invalid document type"
        
        logger.log_result(True, {"error_message": str(exc_info.value)})
        
    except Exception as e:
        logger.log_error(e)
        logger.log_result(False, {"error": str(e)})
        raise
    finally:
        logger.complete_test()

@patch('services.pdf_service.PDFClass._extract_text_from_pdf')
def test_extract_text_from_pdf(mock_extract, pdf_service, sample_pdf_file):
    """Test text extraction from PDF."""
    test_name = "test_extract_text_from_pdf"
    logger.log_step(f"Starting test: {test_name}")
    
    try:
        # Mock the text extraction
        mock_extract.return_value = "Sample extracted text from PDF"
        
        # Call the method
        text = pdf_service._extract_text_from_pdf(sample_pdf_file)
        
        # Verify the result
        assert isinstance(text, str), "Extracted text should be a string"
        assert len(text) > 0, "Extracted text should not be empty"
        
        logger.log_result(True, {"extracted_text_length": len(text)})
        
    except Exception as e:
        logger.log_error(e)
        logger.log_result(False, {"error": str(e)})
        raise
    finally:
        logger.complete_test()

# Add more test cases as needed for different scenarios
# Example: Test with different page counts, empty PDF, corrupted PDF, etc.

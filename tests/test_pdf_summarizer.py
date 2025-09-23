"""
Tests for the PDF summarization functionality.
"""
import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import status, UploadFile, HTTPException
from fastapi.testclient import TestClient
from io import BytesIO

# Test data
TEST_FILENAME = "test_document.pdf"
TEST_CONTENT = b"%PDF-1.4\n%\xd3\xeb\xe9\xe1\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 24 Tf 100 700 Td (Hello, World!) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000015 00000 n \n0000000060 00000 n \n0000000111 00000 n \n0000000202 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n307\n%%EOF"
TEST_DOC_TYPE = "Research Paper Summary"
TEST_PAGES = 2
TEST_SUMMARY = "This is a test summary of the PDF document."

class TestPDFSummarizer:
    """Test cases for PDF summarization."""

    @pytest.fixture
    def test_pdf_file(self):
        """Create a test PDF file in memory."""
        return (BytesIO(TEST_CONTENT), TEST_FILENAME)

    @pytest.mark.asyncio
    async def test_summarize_pdf_success(self, async_client, test_pdf_file):
        """Test successful PDF summarization."""
        # Create a test PDF file
        file, filename = test_pdf_file
        
        # Mock the PDF processing and summarization
        with patch('api.PDFManager') as mock_pdf_manager, \
             patch('api.VectorRetriever') as mock_retriever, \
             patch('api.LLMSummarizer') as mock_summarizer:
            
            # Setup mocks
            mock_pdf_manager.return_value.extract_text.return_value = "Test PDF content"
            mock_retriever.return_value.process_text.return_value = None
            mock_summarizer.return_value.summarize_with_structure.return_value = TEST_SUMMARY
            
            # Make the request
            files = {'file': (filename, file, 'application/pdf')}
            data = {
                'doc_type': TEST_DOC_TYPE,
                'pages': str(TEST_PAGES)
            }
            
            response = await async_client.post(
                "/summarize/pdf",
                files=files,
                data=data
            )
            
            # Assertions
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "summary" in data
            assert data["download_link"].endswith(".docx")
    
    @pytest.mark.asyncio
    async def test_summarize_pdf_invalid_file_type(self, async_client):
        """Test PDF summarization with invalid file type."""
        # Create a test text file instead of PDF
        files = {'file': ("test.txt", b"This is not a PDF", 'text/plain')}
        data = {
            'doc_type': TEST_DOC_TYPE,
            'pages': str(TEST_PAGES)
        }
        
        response = await async_client.post(
            "/summarize/pdf",
            files=files,
            data=data
        )
        
        # Should return 400 for invalid file type
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    async def test_summarize_pdf_missing_file(self, async_client):
        """Test PDF summarization with no file provided."""
        response = await async_client.post(
            "/summarize/pdf",
            data={
                'doc_type': TEST_DOC_TYPE,
                'pages': str(TEST_PAGES)
            }
        )
        
        # Should return 422 for missing file
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_summarize_pdf_error_handling(self, async_client, test_pdf_file):
        """Test error handling in PDF summarization."""
        file, filename = test_pdf_file
        
        with patch('api.PDFManager') as mock_pdf_manager:
            mock_pdf_manager.return_value.extract_text.side_effect = Exception("Test error")
            
            files = {'file': (filename, file, 'application/pdf')}
            data = {
                'doc_type': TEST_DOC_TYPE,
                'pages': str(TEST_PAGES)
            }
            
            response = await async_client.post(
                "/summarize/pdf",
                files=files,
                data=data
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "error" in response.json()

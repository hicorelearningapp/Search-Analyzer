"""
Tests for the web summarization functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from services.types import DocumentTypeEnum

# Test data
TEST_QUERY = "test query"
TEST_DOC_TYPE = "Research Paper Summary"
TEST_PAGES = 2
TEST_SUMMARY = "This is a test summary."

class TestWebSummarizer:
    """Test cases for web summarization."""

    @pytest.mark.asyncio
    async def test_summarize_web_success(self, async_client, temp_txt):
        """Test successful web summarization."""
        # Mock the web search and summarization
        with patch('services.web_service.WebSearchManager') as mock_web_manager, \
             patch('api.VectorRetriever') as mock_retriever, \
             patch('api.LLMSummarizer') as mock_summarizer:
            
            # Setup mocks
            mock_web_manager.return_value.run.return_value = "Test web content"
            mock_retriever.return_value.process_text.return_value = None
            mock_summarizer.return_value.summarize_with_structure.return_value = TEST_SUMMARY
            
            # Make the request
            response = await async_client.post(
                "/summarize/web",
                data={
                    "query": TEST_QUERY,
                    "doc_type": TEST_DOC_TYPE,
                    "pages": TEST_PAGES
                }
            )
            
            # Assertions
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "summary" in data
            assert data["query"] == TEST_QUERY
            assert data["download_link"].endswith(".docx")
    
    @pytest.mark.asyncio
    async def test_summarize_web_invalid_doc_type(self, async_client):
        """Test web summarization with invalid document type."""
        response = await async_client.post(
            "/summarize/web",
            data={
                "query": TEST_QUERY,
                "doc_type": "Invalid Type",
                "pages": TEST_PAGES
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_summarize_web_missing_query(self, async_client):
        """Test web summarization with missing query."""
        response = await async_client.post(
            "/summarize/web",
            data={
                "doc_type": TEST_DOC_TYPE,
                "pages": TEST_PAGES
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_summarize_web_error_handling(self, async_client):
        """Test error handling in web summarization."""
        with patch('services.web_service.WebSearchManager') as mock_web_manager:
            mock_web_manager.return_value.run.side_effect = Exception("Test error")
            
            response = await async_client.post(
                "/summarize/web",
                data={
                    "query": TEST_QUERY,
                    "doc_type": TEST_DOC_TYPE,
                    "pages": TEST_PAGES
                }
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "error" in response.json()

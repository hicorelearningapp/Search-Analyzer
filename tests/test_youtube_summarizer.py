"""
Tests for the YouTube summarization functionality.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import status

# Test data
TEST_YT_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
TEST_DOC_TYPE = "Educational Lesson Plan"
TEST_PAGES = 1
TEST_TRANSCRIPT = "This is a test transcript from a YouTube video."
TEST_SUMMARY = "This is a test summary of the YouTube video."

class TestYouTubeSummarizer:
    """Test cases for YouTube video summarization."""

    @pytest.mark.asyncio
    async def test_summarize_youtube_success(self, async_client):
        """Test successful YouTube video summarization."""
        # Mock the YouTube transcript fetching and summarization
        with patch('sources.video_transcript.TranscriptFetcher') as mock_fetcher, \
             patch('api.VectorRetriever') as mock_retriever, \
             patch('api.LLMSummarizer') as mock_summarizer:
            
            # Setup mocks
            mock_fetcher.return_value.fetch.return_value = TEST_TRANSCRIPT
            mock_retriever.return_value.process_text.return_value = None
            mock_summarizer.return_value.summarize_with_structure.return_value = TEST_SUMMARY
            
            # Make the request
            response = await async_client.post(
                "/summarize/youtube",
                data={
                    "url": TEST_YT_URL,
                    "doc_type": TEST_DOC_TYPE,
                    "pages": TEST_PAGES
                }
            )
            
            # Assertions
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "summary" in data
            assert data["download_link"].endswith(".docx")
    
    @pytest.mark.asyncio
    async def test_summarize_youtube_invalid_url(self, async_client):
        """Test YouTube summarization with invalid URL."""
        response = await async_client.post(
            "/summarize/youtube",
            data={
                "url": "not-a-valid-url",
                "doc_type": TEST_DOC_TYPE,
                "pages": TEST_PAGES
            }
        )
        
        # Should return 422 for invalid URL format
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_summarize_youtube_missing_url(self, async_client):
        """Test YouTube summarization with missing URL."""
        response = await async_client.post(
            "/summarize/youtube",
            data={
                "doc_type": TEST_DOC_TYPE,
                "pages": TEST_PAGES
            }
        )
        
        # Should return 422 for missing required field
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_summarize_youtube_transcript_error(self, async_client):
        """Test error handling when transcript cannot be fetched."""
        with patch('sources.video_transcript.TranscriptFetcher') as mock_fetcher:
            mock_fetcher.return_value.fetch.side_effect = Exception("Failed to fetch transcript")
            
            response = await async_client.post(
                "/summarize/youtube",
                data={
                    "url": TEST_YT_URL,
                    "doc_type": TEST_DOC_TYPE,
                    "pages": TEST_PAGES
                }
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "error" in response.json()
    
    @pytest.mark.parametrize("url", [
        "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ"
    ])
    @pytest.mark.asyncio
    async def test_summarize_youtube_url_variations(self, async_client, url):
        """Test YouTube summarization with different URL formats."""
        with patch('sources.video_transcript.TranscriptFetcher') as mock_fetcher, \
             patch('api.VectorRetriever') as mock_retriever, \
             patch('api.LLMSummarizer') as mock_summarizer:
            
            mock_fetcher.return_value.fetch.return_value = TEST_TRANSCRIPT
            mock_retriever.return_value.process_text.return_value = None
            mock_summarizer.return_value.summarize_with_structure.return_value = TEST_SUMMARY
            
            response = await async_client.post(
                "/summarize/youtube",
                data={
                    "url": url,
                    "doc_type": TEST_DOC_TYPE,
                    "pages": TEST_PAGES
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "summary" in data
            assert data["download_link"].endswith(".docx")

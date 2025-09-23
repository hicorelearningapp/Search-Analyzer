import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Import the service to test
from services.youtube_service import YouTubeClass
from sources.video_transcript import YouTubeTranscriptFetcher, YouTubeSearch, YouTubeTranscriptManager
from services.types import DocumentTypeEnum

# Test data
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
TEST_VIDEO_ID = "dQw4w9WgXcQ"
TEST_DOC_TYPE = DocumentTypeEnum.Blog_Post
TEST_PAGES = 2
TEST_TRANSCRIPT = "This is a test transcript with multiple lines of text"

# Mock search results
MOCK_SEARCH_RESULTS = [
    {
        "rank": 1,
        "title": "Test Video 1",
        "href": "https://www.youtube.com/watch?v=test123"
    },
    {
        "rank": 2,
        "title": "Test Video 2",
        "href": "https://www.youtube.com/watch?v=test456"
    }
]

@pytest.fixture
def youtube_service():
    """Fixture to provide a YouTubeClass instance for testing."""
    return YouTubeClass()

@pytest.fixture
def mock_transcript_fetcher():
    with patch('sources.video_transcript.YouTubeTranscriptFetcher') as mock:
        yield mock

@pytest.fixture
def mock_retriever():
    with patch('sources.retriever.VectorRetriever') as mock:
        yield mock

@pytest.fixture
def mock_summarizer():
    with patch('summarizer.llm_summarizer.LLMSummarizer') as mock:
        yield mock

def test_extract_video_id():
    """Test extraction of video ID from YouTube URL."""
    # Test various URL formats
    assert YouTubeTranscriptFetcher.get_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert YouTubeTranscriptFetcher.get_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert YouTubeTranscriptFetcher.get_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    
    # Test with additional parameters
    assert YouTubeTranscriptFetcher.get_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s") == "dQw4w9WgXcQ"
    
    # Test invalid URLs
    with pytest.raises(ValueError):
        YouTubeTranscriptFetcher.get_video_id("invalid_url")
    with pytest.raises(ValueError):
        YouTubeTranscriptFetcher.get_video_id("https://www.youtube.com/watch")

def test_get_transcript_direct():
    """Test fetching transcript for a YouTube video."""
    # Create a mock for the transcript data
    mock_transcript_data = [
        {'text': 'This is a test transcript', 'start': 0, 'duration': 5},
        {'text': 'with multiple lines of text', 'start': 5, 'duration': 5}
    ]
    
    # Mock the YouTubeTranscriptApi.fetch method
    with patch('sources.video_transcript.YouTubeTranscriptApi') as mock_api:
        # Setup the mock to return our test data
        mock_api.return_value.fetch.return_value = mock_transcript_data
        
        # Call the method
        transcript = YouTubeTranscriptFetcher.get_transcript_direct(TEST_VIDEO_URL)
        
        # Verify the result
        assert "test transcript" in transcript
        assert "multiple lines" in transcript
        
        # Verify the API was called with the correct video ID
        mock_api.return_value.fetch.assert_called_once_with(TEST_VIDEO_ID)

def test_youtube_search():
    """Test searching for YouTube videos."""
    # Create a mock for the search results
    mock_search_results = [
        {"title": "Test Video", "href": "https://www.youtube.com/watch?v=test123"},
        {"title": "Another Test Video", "href": "https://www.youtube.com/watch?v=test456"}
    ]
    
    # Mock the DDGS class and its text method
    with patch('sources.video_transcript.DDGS') as mock_ddgs:
        # Setup the mock to return our test data
        mock_ddgs.return_value.__enter__.return_value.text.return_value = mock_search_results
        
        # Create an instance of YouTubeSearch
        searcher = YouTubeSearch(max_results=2)
        
        # Call the search method
        results = searcher.search("test query")
        
        # Verify the results
        assert len(results) == 2
        assert "title" in results[0]
        assert "href" in results[0]
        assert "youtube.com/watch" in results[0]["href"]
        
        # Verify the DDGS was called with the correct parameters
        mock_ddgs.return_value.__enter__.return_value.text.assert_called_once_with(
            "site:youtube.com test query", 
            max_results=2
        )

@pytest.mark.asyncio
async def test_process_youtube_success(youtube_service):
    """Test the complete YouTube processing flow."""
    # Setup test data
    test_transcript = "This is a test transcript"
    test_summary = "Test summary"
    test_filename = "test_doc.docx"
    
    # Mock the YouTubeTranscriptFetcher
    with patch('sources.video_transcript.YouTubeTranscriptFetcher') as mock_fetcher:
        # Setup the fetcher mock
        mock_fetcher.return_value.get_transcript_direct.return_value = test_transcript
        
        # Mock the retriever and summarizer
        youtube_service.retriever.process_text = MagicMock()
        youtube_service.summarizer.summarize_with_structure = MagicMock(return_value=test_summary)
        
        # Mock the save_docx method
        with patch.object(youtube_service, 'save_docx', return_value=test_filename) as mock_save_docx:
            # Call the method
            result = await youtube_service.process_youtube(
                url=TEST_VIDEO_URL,
                doc_type=TEST_DOC_TYPE,
                pages=TEST_PAGES
            )
            
            # Verify the results
            assert result["raw_text"] == test_transcript
            assert result["summary"] == test_summary
            assert result["download_link"] == f"/download/{test_filename}"
            
            # Verify the mocks were called correctly
            mock_fetcher.return_value.get_transcript_direct.assert_called_once_with(TEST_VIDEO_URL)
            youtube_service.retriever.process_text.assert_called_once()
            youtube_service.summarizer.summarize_with_structure.assert_called_once()
            mock_save_docx.assert_called_once()

@pytest.mark.asyncio
async def test_process_youtube_error(youtube_service, mock_transcript_fetcher):
    """Test error handling in process_youtube."""
    # Setup mock to raise an exception
    mock_transcript_fetcher.return_value.get_transcript_direct.side_effect = Exception("Test error")
    
    # Call the method and check the error response
    result = await youtube_service.process_youtube(
        url=TEST_VIDEO_URL,
        doc_type=TEST_DOC_TYPE,
        pages=TEST_PAGES
    )
    
    # Should return a JSONResponse with error
    assert isinstance(result, JSONResponse)
    assert result.status_code == 500
    assert "error" in result.body.decode()

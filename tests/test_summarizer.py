"""
Tests for the paper summarizer module.
"""
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from research_pal.core.summarizer import PaperSummarizer


@pytest.mark.asyncio
async def test_summarize_paper(mock_summarizer):
    """Test the main paper summarization pipeline."""
    # Set up the mock PDF processor to return expected data
    mock_extract_data = {
        "metadata": {"title": "Test Paper", "author": "Test Author"},
        "chunks": ["Chunk 1", "Chunk 2"],
        "highlighted_text": [],
        "figures_tables": [],
        "chunk_count": 2
    }
    mock_summarizer.pdf_processor.extract_and_chunk.return_value = mock_extract_data
    
    # Patch the determine_paper_domain method
    with patch.object(mock_summarizer, "determine_paper_domain", new_callable=AsyncMock) as mock_determine_domain:
        mock_determine_domain.return_value = "Computer Science"
        
        # Call the method
        result = await mock_summarizer.summarize_paper(
            filepath="test.pdf",
            generate_code=True,
            generate_blog=True
        )
        
        # Verify the result
        assert result["paper_id"] is not None
        assert result["title"] == "Test Paper"
        assert result["domain"] == "Computer Science"
        assert "summary" in result
        assert "takeaways" in result
        assert "code_implementation" in result
        assert "blog_post" in result
        
        # Verify method calls
        mock_summarizer.pdf_processor.extract_and_chunk.assert_called_once_with("test.pdf")
        mock_summarizer.llm_interface.summarize_paper_chunk.assert_called()
        mock_summarizer.llm_interface.merge_chunk_summaries.assert_called_once()
        mock_summarizer.llm_interface.generate_comprehensive_analysis.assert_called_once()
        mock_summarizer.llm_interface.generate_similar_papers.assert_called_once()
        mock_summarizer.llm_interface.generate_code_implementation.assert_called_once()
        mock_summarizer.llm_interface.generate_blog_post.assert_called_once()
        
        # Verify database storage
        mock_summarizer._store_paper_summary.assert_called_once()


@pytest.mark.asyncio
async def test_determine_paper_domain(mock_summarizer):
    """Test domain determination logic."""
    # Set up the mock LLM interface
    mock_summarizer.llm_interface.query_model.return_value = "Computer Vision"
    
    # Call the method
    domain = await mock_summarizer.determine_paper_domain(
        title="Test Paper on Object Detection",
        summary="This paper introduces a new object detection algorithm."
    )
    
    # Verify the result
    assert domain == "Computer Vision"
    
    # Verify method calls
    mock_summarizer.llm_interface.query_model.assert_called_once()
    assert "domain" in mock_summarizer.llm_interface.query_model.call_args[1]["prompt"].lower()


def test_generate_paper_id(mock_summarizer):
    """Test paper ID generation."""
    paper_id1 = mock_summarizer._generate_paper_id(
        filepath="test.pdf",
        title="Test Paper"
    )
    
    paper_id2 = mock_summarizer._generate_paper_id(
        filepath="test.pdf",
        title="Test Paper"
    )
    
    paper_id3 = mock_summarizer._generate_paper_id(
        filepath="different.pdf",
        title="Different Paper"
    )
    
    # Verify that the same input produces the same ID
    assert paper_id1 == paper_id2
    
    # Verify that different inputs produce different IDs
    assert paper_id1 != paper_id3


def test_store_paper_summary(mock_summarizer):
    """Test storing paper summary in database."""
    # Prepare test data
    test_data = {
        "paper_id": "test123",
        "title": "Test Paper",
        "filepath": "test.pdf",
        "summary": "This is a test summary.",
        "takeaways": ["Takeaway 1", "Takeaway 2"],
        "architecture": "Test architecture",
        "domain": "Computer Science"
    }
    
    # Call the method
    mock_summarizer._store_paper_summary(test_data)
    
    # Verify database call
    mock_summarizer.db_manager.add_paper.assert_called_once()
    args, kwargs = mock_summarizer.db_manager.add_paper.call_args
    assert kwargs["paper_id"] == "test123"
    assert kwargs["title"] == "Test Paper"
    assert kwargs["summary"] == "This is a test summary."
    assert "Takeaway 1" in kwargs["takeaways"]


def test_get_paper_summary(mock_summarizer):
    """Test retrieving paper summary from database."""
    # Set up the mock DB manager
    expected_summary = {
        "paper_id": "test123",
        "title": "Test Paper",
        "summary": "This is a test summary.",
        "takeaways": ["Takeaway 1", "Takeaway 2"],
        "domain": "Computer Science"
    }
    mock_summarizer.db_manager.get_paper.return_value = expected_summary
    
    # Call the method
    result = mock_summarizer.get_paper_summary("test123")
    
    # Verify the result
    assert result == expected_summary
    
    # Verify database call
    mock_summarizer.db_manager.get_paper.assert_called_once_with("test123")


def test_search_papers(mock_summarizer):
    """Test paper search functionality."""
    # Set up the mock DB manager
    expected_results = [
        {"paper_id": "test123", "title": "Test Paper", "domain": "Computer Science"},
        {"paper_id": "test456", "title": "Another Test", "domain": "Machine Learning"}
    ]
    mock_summarizer.db_manager.search_papers.return_value = expected_results
    mock_summarizer.db_manager.search_by_domain.return_value = [expected_results[0]]
    
    # Test general search
    result_general = mock_summarizer.search_papers("test query", n_results=2)
    assert result_general == expected_results
    mock_summarizer.db_manager.search_papers.assert_called_once_with("test query", n_results=2)
    
    # Reset mock
    mock_summarizer.db_manager.search_papers.reset_mock()
    
    # Test domain search
    result_domain = mock_summarizer.search_papers("domain:Computer Science", n_results=2)
    assert result_domain == [expected_results[0]]
    mock_summarizer.db_manager.search_by_domain.assert_called_once_with("Computer Science", n_results=2)


def test_update_paper_field(mock_summarizer):
    """Test updating a paper field in the database."""
    # Call the method
    result = mock_summarizer.update_paper_field(
        paper_id="test123",
        field="takeaways",
        value=["New takeaway"]
    )
    
    # Verify the result
    assert result is True
    
    # Verify database call
    mock_summarizer.db_manager.update_paper_field.assert_called_once_with(
        "test123", "takeaways", ["New takeaway"]
    )
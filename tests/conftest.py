"""
Pytest configuration and fixtures for ResearchPal tests.
"""
import os
import pytest
from unittest.mock import MagicMock, AsyncMock

from research_pal.core.llm_interface import LLMInterface
from research_pal.core.summarizer import PaperSummarizer
from research_pal.db.chroma_manager import ChromaManager


@pytest.fixture
def sample_pdf_path():
    """Path to a sample PDF for testing."""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(tests_dir, "data", "sample_paper.pdf")


@pytest.fixture
def mock_llm_interface():
    """Mock LLM interface for testing."""
    mock_llm = MagicMock(spec=LLMInterface)
    
    # Add AsyncMock for async methods
    mock_llm.query_model = AsyncMock()
    mock_llm.query_model.return_value = "Mock response"
    
    mock_llm.summarize_paper_chunk = AsyncMock()
    mock_llm.summarize_paper_chunk.return_value = {
        "SECTION_IDENTIFICATION": "Introduction",
        "SUMMARY": "This is a mock summary",
        "KEY_FINDINGS": ["Finding 1", "Finding 2"],
        "TECHNICAL_DETAILS": "Technical details here",
        "MATH_FORMULATIONS": "E = mc^2",
        "ARCHITECTURE_DETAILS": "Architecture details here",
        "RESULTS": "Results here"
    }
    
    mock_llm.merge_chunk_summaries = AsyncMock()
    mock_llm.merge_chunk_summaries.return_value = {
        "OVERVIEW": "This is a mock overview",
        "PROBLEM_STATEMENT": "This is a mock problem statement",
        "METHODOLOGY": "This is a mock methodology",
        "ARCHITECTURE": "This is a mock architecture",
        "KEY_RESULTS": "These are mock key results",
        "IMPLICATIONS": "These are mock implications",
        "TAKEAWAYS": ["Takeaway 1", "Takeaway 2"],
        "FUTURE_DIRECTIONS": ["Direction 1", "Direction 2"],
        "BACKGROUND": "This is a mock background",
        "MATH_FORMULATIONS": "E = mc^2"
    }
    
    mock_llm.generate_comprehensive_analysis = AsyncMock()
    mock_llm.generate_comprehensive_analysis.return_value = {
        "TAKEAWAYS": ["Takeaway 1", "Takeaway 2"],
        "IMPORTANT_IDEAS": ["Idea 1", "Idea 2"],
        "FUTURE_IDEAS": ["Future 1", "Future 2"],
        "NOVELTY": "This is a mock novelty",
        "LIMITATIONS": ["Limitation 1", "Limitation 2"],
        "PRACTICAL_APPLICATIONS": ["Application 1", "Application 2"],
        "RELATED_WORK": "This is mock related work"
    }
    
    mock_llm.generate_similar_papers = AsyncMock()
    mock_llm.generate_similar_papers.return_value = [
        {
            "title": "Similar Paper 1",
            "authors": "Author 1, Author 2",
            "year": "2023",
            "relevance": "This is relevant because..."
        },
        {
            "title": "Similar Paper 2",
            "authors": "Author 3, Author 4",
            "year": "2022",
            "relevance": "This is also relevant because..."
        }
    ]
    
    mock_llm.generate_code_implementation = AsyncMock()
    mock_llm.generate_code_implementation.return_value = "def mock_function():\n    return 'Hello, world!'"
    
    mock_llm.generate_blog_post = AsyncMock()
    mock_llm.generate_blog_post.return_value = "# Mock Blog Post\n\nThis is a mock blog post."
    
    return mock_llm


@pytest.fixture
def mock_db_manager():
    """Mock DB manager for testing."""
    mock_db = MagicMock(spec=ChromaManager)
    
    mock_db.add_paper.return_value = None
    
    mock_db.get_paper.return_value = {
        "paper_id": "mock123",
        "title": "Mock Paper Title",
        "summary": "This is a mock paper summary",
        "takeaways": ["Takeaway 1", "Takeaway 2"],
        "domain": "Computer Science"
    }
    
    mock_db.search_papers.return_value = [
        {
            "paper_id": "mock123",
            "title": "Mock Paper Title",
            "summary": "This is a mock paper summary",
            "takeaways": ["Takeaway 1", "Takeaway 2"],
            "domain": "Computer Science"
        },
        {
            "paper_id": "mock456",
            "title": "Another Mock Paper",
            "summary": "This is another mock paper summary",
            "takeaways": ["Takeaway A", "Takeaway B"],
            "domain": "Machine Learning"
        }
    ]
    
    mock_db.search_by_domain.return_value = [
        {
            "paper_id": "mock123",
            "title": "Mock Paper Title",
            "summary": "This is a mock paper summary",
            "takeaways": ["Takeaway 1", "Takeaway 2"],
            "domain": "Computer Science"
        }
    ]
    
    return mock_db


@pytest.fixture
def mock_summarizer(mock_llm_interface, mock_db_manager):
    """Mock paper summarizer for testing."""
    summarizer = PaperSummarizer(
        llm_interface=mock_llm_interface,
        db_manager=mock_db_manager
    )
    
    # Replace the pdf_processor with a mock
    mock_pdf_processor = MagicMock()
    mock_pdf_processor.extract_and_chunk.return_value = {
        "metadata": {"title": "Mock Paper Title", "author": "Mock Author"},
        "chunks": ["Chunk 1", "Chunk 2"],
        "highlighted_text": ["Highlighted text 1"],
        "figures_tables": [{"type": "figure", "page": 1}],
        "chunk_count": 2
    }
    
    summarizer.pdf_processor = mock_pdf_processor
    
    # Add spy for _store_paper_summary method
    summarizer._store_paper_summary = MagicMock()
    summarizer._generate_paper_id = MagicMock(return_value="mock123")
    
    return summarizer
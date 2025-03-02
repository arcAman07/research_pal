"""
Tests for the PDF processor module.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

from research_pal.core.pdf_processor import PDFProcessor


@pytest.fixture
def pdf_processor():
    """Create a PDF processor for testing."""
    return PDFProcessor(chunk_size=1000, chunk_overlap=100)


def test_init(pdf_processor):
    """Test PDF processor initialization."""
    assert pdf_processor.chunk_size == 1000
    assert pdf_processor.chunk_overlap == 100


def test_chunk_text(pdf_processor):
    """Test chunking of text."""
    # Create sample text with paragraph breaks
    sample_text = "This is paragraph one.\n\nThis is paragraph two.\n\nThis is paragraph three with more text to ensure that it exceeds the chunk size. " + "Extra text " * 100
    
    chunks = pdf_processor._chunk_text(sample_text)
    
    # Verify chunks
    assert len(chunks) > 1  # Should create multiple chunks
    assert chunks[0].startswith("This is paragraph one.")
    assert chunks[0].endswith("paragraph two.")  # First chunk should include first and second paragraphs
    
    # Check overlap
    assert "paragraph three" in chunks[1]  # Second chunk should include third paragraph


@patch("pdfminer.high_level.extract_text")
def test_extract_metadata(mock_extract_text, pdf_processor):
    """Test metadata extraction from PDF."""
    # Mock extract_text function
    mock_extract_text.return_value = """
    Title: Test Research Paper
    Authors: John Doe, Jane Smith
    
    Abstract
    This is a test abstract for a research paper about testing.
    
    Introduction
    This paper introduces testing methodology.
    """
    
    metadata = pdf_processor._extract_metadata(
        filepath="test.pdf",
        text=mock_extract_text.return_value
    )
    
    # Verify metadata extraction
    assert metadata["title"] == "Title: Test Research Paper"  # Should extract title
    assert "John Doe" in metadata["author"]  # Should extract authors
    assert metadata["filepath"] == "test.pdf"  # Should include filepath
    assert "abstract" in metadata  # Should extract abstract


@patch("research_pal.core.pdf_processor.extract_text")
@patch("research_pal.core.pdf_processor.extract_pages")
def test_extract_and_chunk(mock_extract_pages, mock_extract_text, pdf_processor):
    """Test PDF extraction and chunking."""
    # Mock extract_text function
    mock_extract_text.return_value = """
    Title: Test Research Paper
    Authors: John Doe, Jane Smith
    
    Abstract
    This is a test abstract for a research paper about testing.
    
    Introduction
    This paper introduces testing methodology.
    """
    
    # Mock extract_pages function
    mock_page_layout = MagicMock()
    mock_extract_pages.return_value = [mock_page_layout]
    
    # Call the method
    result = pdf_processor.extract_and_chunk("test.pdf")
    
    # Verify result
    assert "metadata" in result
    assert "chunks" in result
    assert "chunk_count" in result
    assert "highlighted_text" in result
    assert "figures_tables" in result
    
    # Verify metadata extraction
    assert result["metadata"]["title"] == "Title: Test Research Paper"
    
    # Verify text chunking
    assert len(result["chunks"]) > 0
    assert result["chunk_count"] == len(result["chunks"])


def test_extract_and_chunk_nonexistent_file(pdf_processor):
    """Test handling of nonexistent files."""
    with pytest.raises(FileNotFoundError):
        pdf_processor.extract_and_chunk("nonexistent.pdf")
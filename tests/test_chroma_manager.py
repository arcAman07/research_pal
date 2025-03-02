"""
Tests for the ChromaDB manager module.
"""
import os
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from research_pal.db.chroma_manager import ChromaManager


@pytest.fixture
def temp_db_path():
    """Create a temporary directory for the test database."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def chroma_manager(temp_db_path):
    """Create a ChromaManager with a temporary database path."""
    with patch("chromadb.PersistentClient") as mock_client:
        # Mock the collection
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        # Create the manager
        manager = ChromaManager(persist_directory=temp_db_path)
        
        # Assign the mock collection
        manager.papers_collection = mock_collection
        
        yield manager


def test_init(chroma_manager, temp_db_path):
    """Test ChromaManager initialization."""
    assert chroma_manager.persist_directory == temp_db_path
    assert chroma_manager.client is not None
    assert chroma_manager.papers_collection is not None


def test_add_paper(chroma_manager):
    """Test adding a paper to the database."""
    # Call the method
    chroma_manager.add_paper(
        paper_id="test123",
        title="Test Paper",
        filepath="/path/to/test.pdf",
        summary="This is a test summary.",
        takeaways=["Takeaway 1", "Takeaway 2"],
        architecture="Test architecture",
        domain="Computer Science"
    )
    
    # Verify the collection call
    chroma_manager.papers_collection.upsert.assert_called_once()
    args, kwargs = chroma_manager.papers_collection.upsert.call_args
    
    # Check that the ID is correct
    assert kwargs["ids"] == ["test123"]
    
    # Check that metadata contains expected fields
    metadata = kwargs["metadatas"][0]
    assert metadata["title"] == "Test Paper"
    assert metadata["filepath"] == "/path/to/test.pdf"
    assert metadata["domain"] == "Computer Science"
    assert metadata["has_architecture"] is True
    
    # Check that document text contains expected content
    document_text = kwargs["documents"][0]
    assert "This is a test summary" in document_text
    assert "Takeaway 1 | Takeaway 2" in document_text
    assert "Test architecture" in document_text


def test_get_paper(chroma_manager):
    """Test retrieving a paper from the database."""
    # Mock the collection response
    chroma_manager.papers_collection.get.return_value = {
        "ids": ["test123"],
        "documents": ["summary: This is a test summary\ntakeaways: Takeaway 1 | Takeaway 2\ndomain: Computer Science"],
        "metadatas": [{"title": "Test Paper", "filepath": "/path/to/test.pdf", "domain": "Computer Science"}]
    }
    
    # Call the method
    result = chroma_manager.get_paper("test123")
    
    # Verify the collection call
    chroma_manager.papers_collection.get.assert_called_once_with(ids=["test123"])
    
    # Check the result
    assert result is not None
    assert "title" in result
    assert result["title"] == "Test Paper"
    assert "domain" in result
    assert result["domain"] == "Computer Science"
    assert "takeaways" in result
    assert len(result["takeaways"]) == 2
    assert "Takeaway 1" in result["takeaways"]


def test_get_paper_not_found(chroma_manager):
    """Test retrieving a non-existent paper."""
    # Mock the collection response for empty result
    chroma_manager.papers_collection.get.return_value = {
        "ids": [],
        "documents": [],
        "metadatas": []
    }
    
    # Call the method
    result = chroma_manager.get_paper("nonexistent")
    
    # Verify the collection call
    chroma_manager.papers_collection.get.assert_called_once_with(ids=["nonexistent"])
    
    # Check the result
    assert result is None


def test_search_papers(chroma_manager):
    """Test searching for papers."""
    # Mock the collection response
    chroma_manager.papers_collection.query.return_value = {
        "ids": [["test123", "test456"]],
        "distances": [[0.1, 0.2]]
    }
    
    # Mock the get_paper method
    with patch.object(chroma_manager, "get_paper") as mock_get_paper:
        mock_get_paper.side_effect = [
            {"paper_id": "test123", "title": "Test Paper"},
            {"paper_id": "test456", "title": "Another Test"}
        ]
        
        # Call the method
        results = chroma_manager.search_papers("test query", n_results=2)
        
        # Verify the collection call
        chroma_manager.papers_collection.query.assert_called_once_with(
            query_texts=["test query"],
            n_results=2
        )
        
        # Verify get_paper calls
        assert mock_get_paper.call_count == 2
        mock_get_paper.assert_any_call("test123")
        mock_get_paper.assert_any_call("test456")
        
        # Check the results
        assert len(results) == 2
        assert results[0]["paper_id"] == "test123"
        assert results[1]["paper_id"] == "test456"


def test_search_by_domain(chroma_manager):
    """Test searching papers by domain."""
    # Mock the collection response
    chroma_manager.papers_collection.get.return_value = {
        "ids": ["test123", "test789"],
        "documents": ["doc1", "doc2"],
        "metadatas": [{"domain": "Computer Science"}, {"domain": "Computer Science"}]
    }
    
    # Mock the get_paper method
    with patch.object(chroma_manager, "get_paper") as mock_get_paper:
        mock_get_paper.side_effect = [
            {"paper_id": "test123", "title": "Test CS Paper", "domain": "Computer Science"},
            {"paper_id": "test789", "title": "Another CS Paper", "domain": "Computer Science"}
        ]
        
        # Call the method
        results = chroma_manager.search_by_domain("Computer Science", n_results=2)
        
        # Verify the collection call
        chroma_manager.papers_collection.get.assert_called_once_with(
            where={"domain": {"$eq": "Computer Science"}}
        )
        
        # Verify get_paper calls
        assert mock_get_paper.call_count == 2
        mock_get_paper.assert_any_call("test123")
        mock_get_paper.assert_any_call("test789")
        
        # Check the results
        assert len(results) == 2
        assert results[0]["paper_id"] == "test123"
        assert results[1]["paper_id"] == "test789"
        assert results[0]["domain"] == "Computer Science"


def test_update_paper_field(chroma_manager):
    """Test updating a field in a paper."""
    # Mock the get_paper method
    with patch.object(chroma_manager, "get_paper") as mock_get_paper, \
         patch.object(chroma_manager, "add_paper") as mock_add_paper:
        
        mock_get_paper.return_value = {
            "paper_id": "test123",
            "title": "Test Paper",
            "filepath": "/path/to/test.pdf",
            "summary": "This is a test summary.",
            "takeaways": ["Original takeaway"],
            "domain": "Computer Science"
        }
        
        # Call the method
        chroma_manager.update_paper_field(
            paper_id="test123",
            field="takeaways",
            value=["Updated takeaway"]
        )
        
        # Verify get_paper call
        mock_get_paper.assert_called_once_with("test123")
        
        # Verify add_paper call to update the paper
        mock_add_paper.assert_called_once()
        kwargs = mock_add_paper.call_args[1]
        assert kwargs["paper_id"] == "test123"
        assert kwargs["takeaways"] == ["Updated takeaway"]  # Field should be updated
        assert kwargs["title"] == "Test Paper"  # Other fields should be preserved
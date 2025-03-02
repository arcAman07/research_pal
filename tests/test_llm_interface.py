"""
Tests for the LLM interface module.
"""
import os
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock

from research_pal.core.llm_interface import LLMInterface


@pytest.fixture
def llm_interface():
    """Create an LLM interface for testing."""
    # Set mock API keys for testing
    os.environ["OPENAI_API_KEY"] = "test_openai_key"
    os.environ["GOOGLE_API_KEY"] = "test_google_key"
    
    return LLMInterface(default_model="gpt-4o-mini")


def test_init(llm_interface):
    """Test LLM interface initialization."""
    assert llm_interface.default_model == "gpt-4o-mini"
    assert llm_interface.openai_api_key == "test_openai_key"
    assert llm_interface.google_api_key == "test_google_key"
    assert "gpt-4o-mini" in llm_interface.model_configs
    assert "gemini-1.5-flash" in llm_interface.model_configs


def test_get_model_info(llm_interface):
    """Test getting model information."""
    model_info = llm_interface.get_model_info("gpt-4o-mini")
    assert model_info["provider"] == "openai"
    assert model_info["max_tokens"] > 0
    assert "capabilities" in model_info
    
    # Test default model
    default_model_info = llm_interface.get_model_info()
    assert default_model_info == model_info


def test_select_provider(llm_interface):
    """Test provider selection based on model."""
    assert llm_interface._select_provider("gpt-4o-mini") == "openai"
    assert llm_interface._select_provider("gemini-1.5-flash") == "google"
    
    # Test default provider
    assert llm_interface._select_provider() == "openai"  # Based on default_model


def test_get_actual_model_name(llm_interface):
    """Test getting actual model name for API requests."""
    assert llm_interface._get_actual_model_name("gpt-4o-mini") == "gpt-4o-mini"
    
    # For Google models, should return the mapping from model_name
    assert llm_interface._get_actual_model_name("gemini-1.5-flash") == "gemini-1.5-flash-latest"


@pytest.mark.asyncio
async def test_query_openai(llm_interface):
    """Test OpenAI API query."""
    with patch("httpx.AsyncClient.post") as mock_post:
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response
        
        # Call the method
        response = await llm_interface.query_openai(
            prompt="Test prompt",
            system_message="Test system message"
        )
        
        # Verify response
        assert response == "Test response"
        
        # Verify API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["messages"][0]["role"] == "system"
        assert kwargs["json"]["messages"][0]["content"] == "Test system message"
        assert kwargs["json"]["messages"][1]["role"] == "user"
        assert kwargs["json"]["messages"][1]["content"] == "Test prompt"


@pytest.mark.asyncio
async def test_query_google(llm_interface):
    """Test Google API query."""
    with patch("httpx.AsyncClient.post") as mock_post:
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "Test response"}]
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Call the method
        response = await llm_interface.query_google(
            prompt="Test prompt",
            system_message="Test system message",
            model="gemini-1.5-flash"
        )
        
        # Verify response
        assert response == "Test response"
        
        # Verify API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "generativelanguage.googleapis.com" in args[0]
        assert "gemini-1.5-flash-latest" in args[0]
        assert kwargs["json"]["contents"][0]["parts"][0]["text"].startswith("<system>")
        assert kwargs["json"]["contents"][1]["parts"][0]["text"] == "Test prompt"


@pytest.mark.asyncio
async def test_query_model(llm_interface):
    """Test generic model query routing."""
    with patch.object(llm_interface, "query_openai", new_callable=AsyncMock) as mock_openai, \
         patch.object(llm_interface, "query_google", new_callable=AsyncMock) as mock_google:
        
        # Mock responses
        mock_openai.return_value = "OpenAI response"
        mock_google.return_value = "Google response"
        
        # Test OpenAI routing
        response_openai = await llm_interface.query_model(
            prompt="Test prompt",
            model="gpt-4o-mini"
        )
        assert response_openai == "OpenAI response"
        mock_openai.assert_called_once()
        mock_google.assert_not_called()
        
        # Reset mocks
        mock_openai.reset_mock()
        mock_google.reset_mock()
        
        # Test Google routing
        response_google = await llm_interface.query_model(
            prompt="Test prompt",
            model="gemini-1.5-flash"
        )
        assert response_google == "Google response"
        mock_google.assert_called_once()
        mock_openai.assert_not_called()
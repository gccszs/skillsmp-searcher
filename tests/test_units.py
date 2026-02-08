"""
Unit tests for SkillsMP Searcher scripts
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
import requests

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'skills', 'skillsmp-searcher', 'scripts'))

import search_skills
import ai_search


class TestAPIKeyLoading:
    """Test API key loading from various sources"""

    def test_load_from_env_var(self, mock_env_api_key):
        """Test loading API key from environment variable"""
        key = search_skills.load_api_key()
        assert key == 'test_key_123'

    def test_load_from_file(self, temp_api_key_file):
        """Test loading API key from file"""
        # Mock the API_KEY_REAL_FILE path
        with patch.object(search_skills, 'API_KEY_REAL_FILE', str(temp_api_key_file)):
            with patch.object(search_skills, 'API_KEY_FILE', str(temp_api_key_file)):
                with patch.dict(os.environ, {}, clear=True):
                    key = search_skills.load_api_key()
                    assert key == 'sk_test_key_456'

    def test_load_no_api_key(self, tmp_path):
        """Test error when no API key is found"""
        # Create empty temp directory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        with patch.object(search_skills, 'API_KEY_REAL_FILE', str(empty_dir / "nonexistent.txt")):
            with patch.object(search_skills, 'API_KEY_FILE', str(empty_dir / "nonexistent.txt")):
                with patch.dict(os.environ, {}, clear=True):
                    with pytest.raises(SystemExit):
                        search_skills.load_api_key()


class TestSearchFunctions:
    """Test search functionality"""

    @patch('search_skills.requests.get')
    def test_search_skills_success(self, mock_get, mock_api_response):
        """Test successful API call for keyword search"""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = search_skills.search_skills("test", api_key="test_key")

        assert result["success"] == True
        assert len(result["data"]["skills"]) == 2
        mock_get.assert_called_once()

    @patch('search_skills.requests.get')
    def test_search_skills_parameters(self, mock_get, mock_api_response):
        """Test that search parameters are correctly passed"""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        search_skills.search_skills(
            query="SEO",
            page=2,
            limit=10,
            sort_by="recent",
            api_key="test_key"
        )

        call_args = mock_get.call_args
        assert "params" in call_args[1]
        params = call_args[1]["params"]
        assert params["q"] == "SEO"
        assert params["page"] == 2
        assert params["limit"] == 10
        assert params["sortBy"] == "recent"

    @patch('search_skills.requests.get')
    def test_search_skills_error_401(self, mock_get):
        """Test API authentication error handling"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "success": False,
            "error": {
                "code": "INVALID_API_KEY",
                "message": "Invalid key"
            }
        }
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(SystemExit):
            search_skills.search_skills("test", api_key="invalid_key")

    @patch('ai_search.requests.get')
    def test_ai_search_success(self, mock_get, mock_api_response):
        """Test successful AI semantic search"""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = ai_search.ai_search("How to create a scraper", api_key="test_key")

        assert result["success"] == True
        assert len(result["data"]["skills"]) == 2


class TestResultFormatting:
    """Test result formatting functions"""

    def test_format_results_success(self, mock_api_response, capsys):
        """Test successful result formatting"""
        search_skills.format_results(mock_api_response)
        captured = capsys.readouterr()

        assert "Test Skill" in captured.out
        assert "Test Author" in captured.out
        assert "42" in captured.out  # stars

    def test_format_results_error(self, mock_api_error_response, capsys):
        """Test error result formatting"""
        search_skills.format_results(mock_api_error_response)
        captured = capsys.readouterr()

        assert "Error" in captured.out
        assert "INVALID_API_KEY" in captured.out

    def test_ai_format_results_success(self, mock_api_response, capsys):
        """Test AI search result formatting"""
        ai_search.format_results(mock_api_response)
        captured = capsys.readouterr()

        assert "AI Search Results" in captured.out
        assert "Test Skill" in captured.out
        assert "0.95" in captured.out  # relevance score

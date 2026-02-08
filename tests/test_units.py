"""
Unit tests for SkillsMP Searcher scripts
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest
import requests

# Add scripts directory to path
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "skills", "skillsmp-searcher", "scripts"
    ),
)

import ai_search
import search_skills
import utils
from utils import APIKeyError, APIRequestError, SkillsMPError


class TestAPIKeyLoading:
    """Test API key loading from various sources"""

    def test_load_from_env_var(self, monkeypatch):
        """Test loading API key from environment variable"""
        monkeypatch.setenv("SKILLSMP_API_KEY", "test_key_123")
        key = utils.load_api_key()
        assert key == "test_key_123"

    def test_load_from_real_file(self, tmp_path, monkeypatch):
        """Test loading API key from api_key_real.txt"""
        api_key_file = tmp_path / "api_key_real.txt"
        api_key_file.write_text("sk_test_key_456")

        with patch.object(utils, "API_KEY_REAL_FILE", str(api_key_file)):
            monkeypatch.delenv("SKILLSMP_API_KEY", raising=False)
            key = utils.load_api_key()
            assert key == "sk_test_key_456"

    def test_load_from_template_file(self, tmp_path, monkeypatch):
        """Test loading API key from api_key.txt template"""
        api_key_file = tmp_path / "api_key.txt"
        api_key_file.write_text("sk_live_real_key_789")

        with patch.object(utils, "API_KEY_FILE", str(api_key_file)):
            with patch.object(
                utils, "API_KEY_REAL_FILE", str(tmp_path / "nonexistent.txt")
            ):
                monkeypatch.delenv("SKILLSMP_API_KEY", raising=False)
                key = utils.load_api_key()
                assert key == "sk_live_real_key_789"

    def test_load_template_file_skips_placeholder(self, tmp_path, monkeypatch):
        """Test that placeholder text in template file is skipped"""
        api_key_file = tmp_path / "api_key.txt"
        api_key_file.write_text("sk_live_your_api_key_here")

        with patch.object(utils, "API_KEY_FILE", str(api_key_file)):
            with patch.object(
                utils, "API_KEY_REAL_FILE", str(tmp_path / "nonexistent.txt")
            ):
                monkeypatch.delenv("SKILLSMP_API_KEY", raising=False)
                with pytest.raises(APIKeyError):
                    utils.load_api_key()

    def test_load_no_api_key_raises_exception(self, tmp_path, monkeypatch):
        """Test APIKeyError is raised when no API key is found"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        with patch.object(
            utils, "API_KEY_REAL_FILE", str(empty_dir / "nonexistent.txt")
        ):
            with patch.object(
                utils, "API_KEY_FILE", str(empty_dir / "nonexistent.txt")
            ):
                monkeypatch.delenv("SKILLSMP_API_KEY", raising=False)
                with pytest.raises(APIKeyError, match="No valid API key found"):
                    utils.load_api_key()


class TestProxyLoading:
    """Test proxy configuration loading"""

    def test_load_http_proxy(self, monkeypatch):
        """Test loading HTTP proxy"""
        monkeypatch.setenv("HTTP_PROXY", "http://proxy.example.com:8080")
        proxies = utils.load_proxies()
        assert proxies is not None
        assert proxies["http"] == "http://proxy.example.com:8080"

    def test_load_https_proxy(self, monkeypatch):
        """Test loading HTTPS proxy"""
        monkeypatch.setenv("HTTPS_PROXY", "https://proxy.example.com:8443")
        proxies = utils.load_proxies()
        assert proxies is not None
        assert proxies["https"] == "https://proxy.example.com:8443"

    def test_load_both_proxies(self, monkeypatch):
        """Test loading both HTTP and HTTPS proxies"""
        monkeypatch.setenv("HTTP_PROXY", "http://proxy.example.com:8080")
        monkeypatch.setenv("HTTPS_PROXY", "https://proxy.example.com:8443")
        proxies = utils.load_proxies()
        assert proxies is not None
        assert proxies["http"] == "http://proxy.example.com:8080"
        assert proxies["https"] == "https://proxy.example.com:8443"

    def test_no_proxy_returns_none(self, monkeypatch):
        """Test that None is returned when no proxy is configured"""
        monkeypatch.delenv("HTTP_PROXY", raising=False)
        monkeypatch.delenv("HTTPS_PROXY", raising=False)
        monkeypatch.delenv("http_proxy", raising=False)
        monkeypatch.delenv("https_proxy", raising=False)
        proxies = utils.load_proxies()
        assert proxies is None


class TestSearchFunctions:
    """Test search functionality"""

    @patch("utils.requests.get")
    def test_search_skills_success(self, mock_get, mock_api_response):
        """Test successful API call for keyword search"""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = search_skills.search_skills("test", api_key="test_key")

        assert result["success"] is True
        assert len(result["data"]["skills"]) == 2
        mock_get.assert_called_once()

    @patch("utils.requests.get")
    def test_search_skills_with_timeout(self, mock_get, mock_api_response):
        """Test that timeout is passed to requests"""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        search_skills.search_skills("test", api_key="test_key")

        # Check that timeout was passed
        call_kwargs = mock_get.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] == 10

    @patch("utils.requests.get")
    def test_search_skills_with_custom_timeout(self, mock_get, mock_api_response):
        """Test custom timeout parameter"""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        utils.make_api_request(
            "/skills/search", {"q": "test"}, api_key="test_key", timeout=5
        )

        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["timeout"] == 5

    @patch("utils.requests.get")
    def test_search_skills_error_401(self, mock_get):
        """Test API authentication error handling"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "success": False,
            "error": {"code": "INVALID_API_KEY", "message": "Invalid key"},
        }
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(APIRequestError, match="authentication failed"):
            search_skills.search_skills("test", api_key="invalid_key")

    @patch("utils.requests.get")
    def test_search_skills_timeout(self, mock_get):
        """Test request timeout handling"""
        mock_get.side_effect = requests.exceptions.Timeout()

        with pytest.raises(APIRequestError, match="timed out"):
            search_skills.search_skills("test", api_key="test_key")

    @patch("utils.requests.get")
    def test_ai_search_success(self, mock_get, mock_api_response):
        """Test successful AI semantic search"""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = ai_search.ai_search("How to create a scraper", api_key="test_key")

        assert result["success"] is True
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

    def test_ai_format_results_empty(self, capsys):
        """Test AI search with no results"""
        empty_response = {"success": True, "data": {"skills": []}}
        ai_search.format_results(empty_response)
        captured = capsys.readouterr()

        assert "No skills found" in captured.out


class TestIntegration:
    """Integration tests with utils module"""

    @patch("utils.requests.get")
    def test_search_without_api_key_uses_utils_loader(
        self, mock_get, mock_api_response, monkeypatch
    ):
        """Test that search uses utils.load_api_key when no key provided"""
        # Set up API key in environment
        monkeypatch.setenv("SKILLSMP_API_KEY", "env_key_123")

        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Call without api_key parameter
        result = search_skills.search_skills("test")

        # Verify the request was made
        assert result["success"] is True
        # Check that the Authorization header was set
        call_args = mock_get.call_args
        headers = call_args[1]["headers"]
        assert "Bearer env_key_123" in headers["Authorization"]

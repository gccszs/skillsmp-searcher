"""
Pytest configuration and shared fixtures for SkillsMP Searcher tests
"""

import pytest
import os
from unittest.mock import patch


@pytest.fixture
def mock_api_response():
    """Mock successful API response fixture"""
    return {
        "success": True,
        "data": {
            "skills": [
                {
                    "id": "test-skill-1",
                    "name": "Test Skill",
                    "description": "A test skill for unit testing",
                    "author": "Test Author",
                    "stars": 42,
                    "relevance_score": 0.95
                },
                {
                    "id": "test-skill-2",
                    "name": "Another Test Skill",
                    "description": "Another test skill",
                    "author": "Another Author",
                    "stars": 10,
                    "relevance_score": 0.87
                }
            ],
            "total": 2,
            "page": 1,
            "limit": 20
        }
    }


@pytest.fixture
def mock_api_error_response():
    """Mock API error response fixture"""
    return {
        "success": False,
        "error": {
            "code": "INVALID_API_KEY",
            "message": "The provided API key is invalid"
        }
    }


@pytest.fixture
def mock_env_api_key():
    """Mock environment variable API key"""
    with patch.dict(os.environ, {'SKILLSMP_API_KEY': 'test_key_123'}):
        yield


@pytest.fixture
def temp_api_key_file(tmp_path):
    """Create a temporary API key file"""
    api_key_file = tmp_path / "api_key_real.txt"
    api_key_file.write_text("sk_test_key_456")
    return api_key_file

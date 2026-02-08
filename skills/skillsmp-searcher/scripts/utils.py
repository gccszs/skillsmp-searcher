#!/usr/bin/env python3
"""
Shared utilities for SkillsMP search scripts
"""

import os
from typing import Dict, Optional

import requests


class SkillsMPError(Exception):
    """Base exception for SkillsMP errors"""

    pass


class APIKeyError(SkillsMPError):
    """Exception raised when API key is not found or invalid"""

    pass


class APIRequestError(SkillsMPError):
    """Exception raised when API request fails"""

    pass


# API Configuration
BASE_URL = os.getenv("SKILLSMP_API_BASE_URL", "https://skillsmp.com/api/v1")
API_KEY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "references", "api_key.txt"
)
API_KEY_REAL_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "references", "api_key_real.txt"
)


def load_api_key() -> str:
    """
    Load API key from multiple sources (priority order):
    1. Environment variable SKILLSMP_API_KEY
    2. File references/api_key_real.txt (for development, gitignored)
    3. File references/api_key.txt (template file)

    Returns:
        str: API key

    Raises:
        APIKeyError: If no valid API key is found
    """
    # Try environment variable first (most secure)
    env_key = os.getenv("SKILLSMP_API_KEY")
    if env_key:
        return env_key

    # Try api_key_real.txt (for development)
    try:
        with open(API_KEY_REAL_FILE, "r") as f:
            api_key = f.read().strip()
            if api_key and not api_key.startswith("#"):
                return api_key
    except FileNotFoundError:
        pass

    # Try api_key.txt (template file)
    try:
        with open(API_KEY_FILE, "r") as f:
            api_key = f.read().strip()
            if (
                api_key
                and not api_key.startswith("#")
                and "your_api_key_here" not in api_key
            ):
                return api_key
    except FileNotFoundError:
        pass

    # No valid API key found
    raise APIKeyError(
        "No valid API key found.\n\n"
        "Please configure your API key using one of these methods:\n"
        "1. Set environment variable SKILLSMP_API_KEY (recommended)\n"
        "2. Create file: references/api_key_real.txt\n"
        "3. Edit file: references/api_key.txt\n\n"
        "See README.md for detailed instructions."
    )


def load_proxies() -> Optional[Dict[str, str]]:
    """
    Load proxy settings from environment variables.

    Returns:
        Dict with 'http' and 'https' proxy URLs, or None if no proxies configured
    """
    http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

    if http_proxy or https_proxy:
        proxies = {}
        if http_proxy:
            proxies["http"] = http_proxy
        if https_proxy:
            proxies["https"] = https_proxy
        return proxies
    return None


def make_api_request(
    endpoint: str,
    params: Dict,
    api_key: Optional[str] = None,
    timeout: int = 10,
) -> Dict:
    """
    Make an API request to SkillsMP with error handling and proxy support.

    Args:
        endpoint: API endpoint (e.g., '/skills/search')
        params: Query parameters
        api_key: SkillsMP API key (if None, will load from config)
        timeout: Request timeout in seconds (default: 10)

    Returns:
        dict: API response data

    Raises:
        APIKeyError: If API key is not found
        APIRequestError: If the request fails
    """
    if api_key is None:
        api_key = load_api_key()

    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    proxies = load_proxies()

    try:
        response = requests.get(
            url, headers=headers, params=params, proxies=proxies, timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            error_data = response.json()
            raise APIRequestError(
                f"API authentication failed: {error_data.get('error', {}).get('message', 'Invalid API key')}"
            ) from e
        raise APIRequestError(f"HTTP error {response.status_code}: {e}") from e
    except requests.exceptions.Timeout:
        raise APIRequestError(f"Request timed out after {timeout} seconds") from None
    except requests.exceptions.RequestException as e:
        raise APIRequestError(f"Request failed: {e}") from e

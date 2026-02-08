#!/usr/bin/env python3
"""
Shared utilities for SkillsMP search scripts
"""

import os
import subprocess
import sys
import zipfile
from pathlib import Path
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


def get_claude_skills_dir() -> Path:
    """
    Get the Claude Code skills directory.

    Returns:
        Path: Path to Claude skills directory

    Raises:
        SkillsMPError: If Claude skills directory cannot be found
    """
    # Try common Claude Code skills directories
    possible_paths = [
        Path.home() / ".claude" / "skills",
        Path.home() / "AppData" / "Roaming" / "claude" / "skills",  # Windows
        Path.home() / ".config" / "claude" / "skills",  # Linux/macOS
    ]

    for path in possible_paths:
        if path.exists():
            return path

    # If none exist, create the default one
    default_path = Path.home() / ".claude" / "skills"
    try:
        default_path.mkdir(parents=True, exist_ok=True)
        return default_path
    except OSError as e:
        raise SkillsMPError(f"Cannot create Claude skills directory: {e}") from e


def download_skill(skill_url: str, download_dir: Path) -> Path:
    """
    Download a skill file from URL.

    Args:
        skill_url: URL to download the skill from
        download_dir: Directory to save the downloaded file

    Returns:
        Path: Path to downloaded skill file

    Raises:
        APIRequestError: If download fails
    """
    proxies = load_proxies()

    try:
        response = requests.get(skill_url, proxies=proxies, timeout=30, stream=True)
        response.raise_for_status()

        # Extract filename from URL or use default
        filename = skill_url.split("/")[-1] or "downloaded_skill.skill"
        skill_path = download_dir / filename

        with open(skill_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return skill_path
    except requests.exceptions.RequestException as e:
        raise APIRequestError(f"Failed to download skill: {e}") from e


def install_skill(skill_path: Path, skills_dir: Optional[Path] = None) -> Path:
    """
    Install a skill from a .skill file to Claude Code skills directory.

    Args:
        skill_path: Path to the .skill file
        skills_dir: Custom skills directory (if None, uses default Claude location)

    Returns:
        Path: Path to installed skill directory

    Raises:
        SkillsMPError: If installation fails
    """
    if skills_dir is None:
        skills_dir = get_claude_skills_dir()

    if not skill_path.exists():
        raise SkillsMPError(f"Skill file not found: {skill_path}")

    # Extract the skill file
    try:
        with zipfile.ZipFile(skill_path, "r") as zip_ref:
            # Get the root directory name in the zip
            namelist = zip_ref.namelist()
            if not namelist:
                raise SkillsMPError("Skill file is empty")

            # Extract all contents
            zip_ref.extractall(skills_dir)

            # Find the extracted skill directory
            # Typically the first entry is the skill directory
            first_item = namelist[0]
            skill_dir_name = first_item.split("/")[0]
            installed_path = skills_dir / skill_dir_name

            print(f"✅ Skill installed to: {installed_path}")
            return installed_path

    except zipfile.BadZipFile:
        raise SkillsMPError(f"Invalid skill file: {skill_path}") from None
    except Exception as e:
        raise SkillsMPError(f"Failed to install skill: {e}") from e


def install_skill_from_url(skill_url: str, skills_dir: Optional[Path] = None) -> Path:
    """
    Download and install a skill from URL.

    Args:
        skill_url: URL to download the skill from
        skills_dir: Custom skills directory (if None, uses default Claude location)

    Returns:
        Path: Path to installed skill directory

    Raises:
        APIRequestError: If download fails
        SkillsMPError: If installation fails
    """
    # Download to temp directory
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        skill_file = download_skill(skill_url, temp_path)
        return install_skill(skill_file, skills_dir)


def list_installed_skills(skills_dir: Optional[Path] = None) -> list[str]:
    """
    List all installed skills in Claude Code skills directory.

    Args:
        skills_dir: Custom skills directory (if None, uses default Claude location)

    Returns:
        list[str]: List of installed skill names
    """
    if skills_dir is None:
        skills_dir = get_claude_skills_dir()

    if not skills_dir.exists():
        return []

    skills = []
    for item in skills_dir.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            skills.append(item.name)

    return sorted(skills)

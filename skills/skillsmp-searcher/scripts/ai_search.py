#!/usr/bin/env python3
"""
SkillsMP AI Semantic Search Script
Search for skills using AI-powered semantic search on SkillsMP marketplace.
"""

import requests
import argparse
import json
import sys
import os

# API Configuration
BASE_URL = os.getenv("SKILLSMP_API_BASE_URL", "https://skillsmp.com/api/v1")
API_KEY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "references", "api_key.txt")
API_KEY_REAL_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "references", "api_key_real.txt")


def load_api_key():
    """
    Load API key from multiple sources (priority order):
    1. Environment variable SKILLSMP_API_KEY
    2. File references/api_key_real.txt (for development, gitignored)
    3. File references/api_key.txt (template file)
    """
    # Try environment variable first (most secure)
    env_key = os.getenv("SKILLSMP_API_KEY")
    if env_key:
        return env_key

    # Try api_key_real.txt (for development)
    try:
        with open(API_KEY_REAL_FILE, 'r') as f:
            api_key = f.read().strip()
            if api_key and not api_key.startswith("#"):
                return api_key
    except FileNotFoundError:
        pass

    # Try api_key.txt (template file)
    try:
        with open(API_KEY_FILE, 'r') as f:
            api_key = f.read().strip()
            if api_key and not api_key.startswith("#") and "your_api_key_here" not in api_key:
                return api_key
    except FileNotFoundError:
        pass

    # No valid API key found
    print("Error: No valid API key found.")
    print("\nPlease configure your API key using one of these methods:")
    print("1. Set environment variable SKILLSMP_API_KEY (recommended)")
    print("2. Create file: references/api_key_real.txt")
    print("3. Edit file: references/api_key.txt")
    print("\nSee API_KEY_GUIDE.md for detailed instructions.")
    sys.exit(1)


def ai_search(query, api_key=None):
    """
    Search skills using AI semantic search.

    Args:
        query: Natural language search query
        api_key: SkillsMP API key

    Returns:
        dict: Search results
    """
    if api_key is None:
        api_key = load_api_key()

    url = f"{BASE_URL}/skills/ai-search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "q": query
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if response.status_code == 401:
            error_data = response.json()
            print(f"API Error: {error_data.get('error', {}).get('message', 'Authentication failed')}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        sys.exit(1)


def format_results(results):
    """Format search results for display"""
    if not results.get("success", True):
        error = results.get("error", {})
        print(f"Error: {error.get('code', 'UNKNOWN')} - {error.get('message', 'Unknown error')}")
        return

    data = results.get("data", {})
    skills = data.get("skills", [])

    print(f"\n=== AI Search Results ===\n")

    if not skills:
        print("No skills found matching your query.")
        return

    for i, skill in enumerate(skills, 1):
        name = skill.get("name", "Unknown")
        description = skill.get("description", "No description")
        relevance = skill.get("relevance_score", 0)
        stars = skill.get("stars", 0)
        author = skill.get("author", "Unknown")

        print(f"{i}. {name}")
        print(f"   Author: {author} | Stars: {stars} | Relevance: {relevance:.2f}")
        print(f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}")
        print()


def main():
    parser = argparse.ArgumentParser(description="AI-powered semantic search on SkillsMP marketplace")
    parser.add_argument("query", help="Natural language search query")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--api-key", help="API key (overrides file)")

    args = parser.parse_args()

    results = ai_search(
        query=args.query,
        api_key=args.api_key
    )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        format_results(results)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SkillsMP Keyword Search Script
Search for skills using keywords on SkillsMP marketplace.
"""

import requests
import argparse
import json
import sys
import os

# API Configuration
BASE_URL = "https://skillsmp.com/api/v1"
API_KEY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "references", "api_key.txt")


def load_api_key():
    """Load API key from references/api_key.txt"""
    try:
        with open(API_KEY_FILE, 'r') as f:
            api_key = f.read().strip()
            if not api_key:
                raise ValueError("API key file is empty")
            return api_key
    except FileNotFoundError:
        print(f"Error: API key file not found at {API_KEY_FILE}")
        print("Please create the file and add your SkillsMP API key.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading API key: {e}")
        sys.exit(1)


def search_skills(query, page=1, limit=20, sort_by="stars", api_key=None):
    """
    Search skills using keyword search.

    Args:
        query: Search keyword
        page: Page number (default: 1)
        limit: Items per page (default: 20, max: 100)
        sort_by: Sort by 'stars' or 'recent' (default: 'stars')
        api_key: SkillsMP API key

    Returns:
        dict: Search results
    """
    if api_key is None:
        api_key = load_api_key()

    url = f"{BASE_URL}/skills/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "q": query,
        "page": page,
        "limit": min(limit, 100),
        "sortBy": sort_by
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
    total = data.get("total", 0)

    print(f"\n=== Search Results ===")
    print(f"Total: {total} skills found\n")

    for i, skill in enumerate(skills, 1):
        name = skill.get("name", "Unknown")
        description = skill.get("description", "No description")
        stars = skill.get("stars", 0)
        author = skill.get("author", "Unknown")

        print(f"{i}. {name}")
        print(f"   Author: {author} | Stars: {stars}")
        print(f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Search SkillsMP marketplace for skills")
    parser.add_argument("query", help="Search keyword")
    parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    parser.add_argument("--limit", type=int, default=20, help="Items per page (default: 20, max: 100)")
    parser.add_argument("--sort", choices=["stars", "recent"], default="stars",
                       help="Sort by: 'stars' (default) or 'recent'")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--api-key", help="API key (overrides file)")

    args = parser.parse_args()

    results = search_skills(
        query=args.query,
        page=args.page,
        limit=args.limit,
        sort_by=args.sort,
        api_key=args.api_key
    )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        format_results(results)


if __name__ == "__main__":
    main()

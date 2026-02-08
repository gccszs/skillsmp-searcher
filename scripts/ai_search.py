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

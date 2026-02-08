#!/usr/bin/env python3
"""
SkillsMP AI Semantic Search Script
Search for skills using AI-powered semantic search on SkillsMP marketplace.
"""

import argparse
import json
import sys

from utils import APIRequestError, SkillsMPError, make_api_request


def ai_search(query, api_key=None):
    """
    Search skills using AI semantic search.

    Args:
        query: Natural language search query
        api_key: SkillsMP API key

    Returns:
        dict: Search results

    Raises:
        SkillsMPError: If the search fails
    """
    params = {"q": query}
    return make_api_request("/skills/ai-search", params, api_key=api_key)


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
    parser = argparse.ArgumentParser(
        description="AI-powered semantic search on SkillsMP marketplace"
    )
    parser.add_argument("query", help="Natural language search query")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--api-key", help="API key (overrides file)")

    args = parser.parse_args()

    try:
        results = ai_search(query=args.query, api_key=args.api_key)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            format_results(results)

    except SkillsMPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

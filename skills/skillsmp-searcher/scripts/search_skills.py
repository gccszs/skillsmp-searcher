#!/usr/bin/env python3
"""
SkillsMP Keyword Search Script
Search for skills using keywords on SkillsMP marketplace.
"""

import argparse
import json
import sys
from typing import Optional

from utils import APIRequestError, SkillsMPError, make_api_request


def search_skills(
    query: str,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "stars",
    api_key: Optional[str] = None,
) -> dict:
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

    Raises:
        SkillsMPError: If the search fails
    """
    params = {"q": query, "page": page, "limit": min(limit, 100), "sortBy": sort_by}
    return make_api_request("/skills/search", params, api_key=api_key)


def format_results(results):
    """Format search results for display"""
    if not results.get("success", True):
        error = results.get("error", {})
        print(f"Error: {error.get('code', 'UNKNOWN')} - {error.get('message', 'Unknown error')}")
        return

    data = results.get("data", {})
    skills = data.get("skills", [])

    # Use total from API, fallback to actual count
    total = data.get("total", len(skills))
    if total == 0 and len(skills) > 0:
        total = len(skills)

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
    parser.add_argument(
        "--limit", type=int, default=20, help="Items per page (default: 20, max: 100)"
    )
    parser.add_argument(
        "--sort",
        choices=["stars", "recent"],
        default="stars",
        help="Sort by: 'stars' (default) or 'recent'",
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--api-key", help="API key (overrides file)")

    args = parser.parse_args()

    try:
        results = search_skills(
            query=args.query,
            page=args.page,
            limit=args.limit,
            sort_by=args.sort,
            api_key=args.api_key,
        )

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            format_results(results)

    except SkillsMPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

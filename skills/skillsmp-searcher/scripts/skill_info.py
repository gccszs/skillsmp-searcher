#!/usr/bin/env python3
"""
SkillsMP Skill Details Viewer
View detailed information about a specific skill.
"""

import argparse
import json
import sys

# Fix UTF-8 encoding for Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from utils import (APIRequestError, SkillsMPError, load_api_key,
                   make_api_request)


def get_skill_details(skill_id: str, api_key: str = None) -> dict:
    """
    Get detailed information about a specific skill.

    Args:
        skill_id: The ID of the skill
        api_key: SkillsMP API key

    Returns:
        dict: Skill details

    Raises:
        SkillsMPError: If the request fails
    """
    params = {"id": skill_id}
    # Note: This endpoint may need adjustment based on actual API
    return make_api_request("/skills/details", params, api_key=api_key)


def format_skill_details(skill: dict):
    """Format skill details for display"""
    print("\n" + "=" * 60)
    print(f"📦 {skill.get('name', 'Unknown')}")
    print("=" * 60)

    # Basic info
    print(f"\n👤 Author: {skill.get('author', 'Unknown')}")
    print(f"⭐ Stars: {skill.get('stars', 0)}")
    print(f"📅 Version: {skill.get('version', 'N/A')}")

    # Description
    description = skill.get("description", "No description")
    print(f"\n📝 Description:")
    print(f"   {description}")

    # Categories/Tags
    tags = skill.get("tags", [])
    if tags:
        print(f"\n🏷️  Tags: {', '.join(tags)}")

    # Installation command
    repo_url = skill.get("repository_url", "")
    if repo_url:
        print(f"\n🔗 Repository: {repo_url}")
        print(f"📦 Install: npx skills add {repo_url.split('github.com/')[-1]}")

    # Requirements
    requirements = skill.get("requirements", [])
    if requirements:
        print(f"\n📋 Requirements:")
        for req in requirements:
            print(f"   - {req}")

    # Examples
    examples = skill.get("examples", [])
    if examples:
        print(f"\n💡 Usage Examples:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")

    print("\n" + "=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="View detailed information about a SkillsMP skill"
    )
    parser.add_argument("skill_id", help="Skill ID or name")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--api-key", help="API key (overrides file)")

    args = parser.parse_args()

    try:
        details = get_skill_details(args.skill_id, api_key=args.api_key)

        if args.json:
            print(json.dumps(details, indent=2))
        else:
            format_skill_details(details)

    except SkillsMPError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SkillsMP Skill Diff Viewer
Compare local skill with remote SkillsMP version.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

from utils import APIRequestError, SkillsMPError, make_api_request


def extract_frontmatter(skill_md_path: Path) -> Dict[str, str]:
    """
    Extract YAML frontmatter from SKILL.md.

    Args:
        skill_md_path: Path to SKILL.md file

    Returns:
        Dict with frontmatter fields
    """
    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()

            frontmatter = {}
            in_frontmatter = False

            for line in content.split("\n")[:30]:  # Check first 30 lines
                if line.strip() == "---":
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        break
                    continue

                if in_frontmatter:
                    match = re.match(r"^(\w+):\s*(.+)$", line)
                    if match:
                        key, value = match.groups()
                        frontmatter[key] = value.strip()

            return frontmatter
    except Exception:
        return {}


def get_skill_details_from_skillsmp(
    skill_name: str, api_key: Optional[str] = None
) -> Optional[Dict]:
    """
    Get detailed skill information from SkillsMP.

    Args:
        skill_name: Name of the skill
        api_key: SkillsMP API key

    Returns:
        Skill data or None if not found
    """
    try:
        params = {"q": skill_name, "limit": 5, "sortBy": "stars"}
        result = make_api_request("/skills/search", params, api_key=api_key)

        if not result.get("success"):
            return None

        skills_list = result.get("data", {}).get("skills", [])
        if not skills_list:
            return None

        # Find exact match
        for skill in skills_list:
            if skill.get("name", "").lower() == skill_name.lower():
                return skill

        # Return best match
        return skills_list[0]

    except (APIRequestError, SkillsMPError):
        return None


def compare_versions(local: Dict, remote: Dict) -> Dict[str, any]:
    """
    Compare local and remote skill versions.

    Args:
        local: Local frontmatter data
        remote: Remote API data

    Returns:
        Dict with comparison results
    """
    differences = {
        "name_changed": False,
        "description_changed": False,
        "author_changed": False,
        "stars_changed": False,
        "fields": [],
    }

    # Compare name
    local_name = local.get("name", "")
    remote_name = remote.get("name", "")
    if local_name and remote_name and local_name != remote_name:
        differences["name_changed"] = True
        differences["fields"].append({"field": "name", "local": local_name, "remote": remote_name})

    # Compare description
    local_desc = local.get("description", "")
    remote_desc = remote.get("description", "")
    if local_desc and remote_desc and local_desc != remote_desc:
        differences["description_changed"] = True
        differences["fields"].append(
            {"field": "description", "local": local_desc[:100], "remote": remote_desc[:100]}
        )

    # Compare author
    local_author = local.get("author", "")
    remote_author = remote.get("author", "")
    if local_author and remote_author and local_author != remote_author:
        differences["author_changed"] = True
        differences["fields"].append(
            {"field": "author", "local": local_author, "remote": remote_author}
        )

    # Compare stars (always check, not in frontmatter)
    remote_stars = remote.get("stars", 0)
    differences["stars_changed"] = True
    differences["fields"].append({"field": "stars", "remote": remote_stars})

    return differences


def format_diff_output(skill_name: str, local_path: Path, remote_data: Dict, differences: Dict):
    """Format and display diff comparison."""
    print("\n" + "=" * 60)
    print(f"📦 {skill_name} - Version Comparison")
    print("=" * 60)

    # Basic info
    print(f"\n📍 Local Path: {local_path}")
    print(f"🔗 GitHub: {remote_data.get('githubUrl', 'N/A')}")
    print(f"🌐 SkillsMP: {remote_data.get('skillUrl', 'N/A')}")
    print(f"⭐ Stars: {remote_data.get('stars', 0)}")
    print(f"📅 Last Updated: {remote_data.get('updatedAt', 'N/A')} " f"(Unix timestamp)")

    # Differences
    if differences["fields"]:
        print("\n📋 Changes Detected:\n")

        for field_data in differences["fields"]:
            field = field_data["field"]
            if field == "name":
                print(f"  Name:")
                print(f"    - Local:  {field_data['local']}")
                print(f"    + Remote: {field_data['remote']}")
            elif field == "description":
                print(f"  Description:")
                print(f"    - Local:  {field_data['local']}...")
                print(f"    + Remote: {field_data['remote']}...")
            elif field == "author":
                print(f"  Author:")
                print(f"    - Local:  {field_data['local']}")
                print(f"    + Remote: {field_data['remote']}")
            elif field == "stars":
                print(f"  Stars: {field_data['remote']}")
    else:
        print("\n✅ No differences detected in frontmatter")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Compare local skill with SkillsMP remote version")
    parser.add_argument("skill_name", help="Name of the skill to compare")
    parser.add_argument(
        "--skill-dir",
        type=Path,
        help="Custom skills directory (default: ~/.claude/skills)",
    )
    parser.add_argument("--api-key", help="API key (overrides file)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    try:
        # Determine skill directory
        skill_dir = args.skill_dir
        if not skill_dir:
            from utils import get_claude_skills_dir

            skill_dir = get_claude_skills_dir()

        # Find local skill directory
        local_skill_path = None
        for item in skill_dir.iterdir():
            if item.is_dir():
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    # Extract name from frontmatter
                    frontmatter = extract_frontmatter(skill_md)
                    if frontmatter.get("name", "").lower() == args.skill_name.lower():
                        local_skill_path = item
                        break

        if not local_skill_path:
            print(f"❌ Skill '{args.skill_name}' not found locally")
            sys.exit(1)

        # Get remote data
        remote_data = get_skill_details_from_skillsmp(args.skill_name, api_key=args.api_key)

        if not remote_data:
            print(f"❌ Skill '{args.skill_name}' not found on SkillsMP")
            sys.exit(1)

        # Extract local frontmatter
        skill_md = local_skill_path / "SKILL.md"
        local_frontmatter = extract_frontmatter(skill_md)

        # Compare
        differences = compare_versions(local_frontmatter, remote_data)

        if args.json:
            # Output JSON
            json_output = {
                "skill_name": args.skill_name,
                "local_path": str(local_skill_path),
                "remote_data": remote_data,
                "differences": differences,
            }
            print(json.dumps(json_output, indent=2))
        else:
            # Format output
            format_diff_output(args.skill_name, local_skill_path, remote_data, differences)

    except SkillsMPError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

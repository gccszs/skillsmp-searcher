#!/usr/bin/env python3
"""
SkillsMP Skill Installer
Install skills from SkillsMP marketplace with one command.
"""

import argparse
import json
import sys

# Fix UTF-8 encoding for Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import search_skills
from utils import install_skill, install_skill_from_url, list_installed_skills


def install_from_search_results(skill_index: int, search_query: str, **search_kwargs):
    """
    Search for a skill and install it by index.

    Args:
        skill_index: Index of the skill in search results (1-based)
        search_query: Search query to find the skill
        **search_kwargs: Additional arguments for search_skills
    """
    print(f"🔍 Searching for skills: {search_query}\n")

    # Search for skills
    results = search_skills.search_skills(search_query, **search_kwargs)

    if not results.get("success", True):
        error = results.get("error", {})
        print(f"❌ Search failed: {error.get('message', 'Unknown error')}")
        sys.exit(1)

    data = results.get("data", {})
    skills = data.get("skills", [])

    if not skills:
        print("❌ No skills found matching your query.")
        sys.exit(1)

    # Display search results
    print(f"Found {data.get('total', 0)} skills:\n")
    for i, skill in enumerate(skills, 1):
        name = skill.get("name", "Unknown")
        author = skill.get("author", "Unknown")
        stars = skill.get("stars", 0)
        print(f"{i}. {name} by {author} (⭐ {stars})")

    print()

    # Validate index
    if skill_index < 1 or skill_index > len(skills):
        print(f"❌ Invalid skill index. Please choose between 1 and {len(skills)}")
        sys.exit(1)

    selected_skill = skills[skill_index - 1]
    skill_name = selected_skill.get("name", "Unknown")
    skill_url = selected_skill.get("download_url", "")
    skill_id = selected_skill.get("id", "")

    # If no direct download URL, construct from repository
    if not skill_url and skill_id:
        # Assuming SkillsMP provides repository_url or similar
        repo_url = selected_skill.get("repository_url", "")
        if repo_url:
            # Try to get the latest release asset
            skill_url = f"{repo_url}/releases/latest/download/skill_name.skill"
        else:
            print(f"❌ Skill '{skill_name}' does not provide a download URL.")
            print("   Please visit SkillsMP marketplace to download manually.")
            sys.exit(1)

    print(f"📦 Installing: {skill_name}\n")

    try:
        if skill_url.startswith("http"):
            installed_path = install_skill_from_url(skill_url)
        else:
            # Assume it's a local path
            from pathlib import Path

            installed_path = install_skill(Path(skill_url))

        print(f"\n✅ Successfully installed: {skill_name}")
        print(f"   Location: {installed_path}")
        print("\n💡 You can now use this skill in Claude Code!")

    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Install skills from SkillsMP marketplace"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install a skill")
    install_parser.add_argument(
        "query", help="Search query to find the skill (or direct URL/path)"
    )
    install_parser.add_argument(
        "--index",
        type=int,
        default=1,
        help="Index of skill to install from search results (default: 1)",
    )
    install_parser.add_argument(
        "--page", type=int, default=1, help="Search page number (default: 1)"
    )
    install_parser.add_argument(
        "--sort",
        choices=["stars", "recent"],
        default="stars",
        help="Sort search results (default: stars)",
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List installed skills")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "install":
            # Check if query is a URL or local path
            if (
                args.query.startswith("http://")
                or args.query.startswith("https://")
                or args.query.endswith(".skill")
            ):
                # Direct installation from URL or file
                print(f"📦 Installing from: {args.query}\n")
                from pathlib import Path

                if args.query.startswith("http"):
                    installed_path = install_skill_from_url(args.query)
                else:
                    installed_path = install_skill(Path(args.query))

                print(f"\n✅ Successfully installed!")
                print(f"   Location: {installed_path}")
            else:
                # Search and install by index
                install_from_search_results(
                    skill_index=args.index,
                    search_query=args.query,
                    page=args.page,
                    sort_by=args.sort,
                )

        elif args.command == "list":
            skills = list_installed_skills()
            if skills:
                print("📚 Installed skills:\n")
                for skill in skills:
                    print(f"  • {skill}")
                print(f"\nTotal: {len(skills)} skills")
            else:
                print("❌ No skills installed.")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

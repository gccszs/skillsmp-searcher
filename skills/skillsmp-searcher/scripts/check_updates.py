#!/usr/bin/env python3
"""
SkillsMP Skill Update Checker
Check for updates to installed skills by comparing local file times with SkillsMP API.
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils import (
    APIRequestError,
    SkillsMPError,
    get_claude_skills_dir,
    load_api_key,
    make_api_request,
)


def get_skill_name_from_md(skill_md_path: Path) -> Optional[str]:
    """
    Extract skill name from SKILL.md frontmatter.

    Args:
        skill_md_path: Path to SKILL.md file

    Returns:
        Skill name or None if not found
    """
    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()

            # Extract name from YAML frontmatter
            match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
            if match:
                return match.group(1).strip()
    except Exception:
        pass
    return None


def get_installed_skills_with_metadata(skills_dir: Path) -> List[Dict]:
    """
    Scan local skills directory and extract metadata.

    Args:
        skills_dir: Path to Claude skills directory

    Returns:
        List of dicts with skill metadata: name, path, local_modified
    """
    skills: List[Dict[str, Any]] = []

    if not skills_dir.exists():
        return skills

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        skill_name = get_skill_name_from_md(skill_md)
        if not skill_name:
            continue

        # Get directory modification time as Unix timestamp
        local_mtime = skill_dir.stat().st_mtime

        skills.append(
            {
                "name": skill_name,
                "path": skill_dir,
                "local_modified": local_mtime,
                "local_modified_date": datetime.fromtimestamp(local_mtime).strftime("%Y-%m-%d"),
            }
        )

    return skills


def search_skill_on_skillsmp(skill_name: str, api_key: Optional[str] = None) -> Optional[Dict]:
    """
    Search for a skill on SkillsMP marketplace.

    Args:
        skill_name: Name of the skill to search for
        api_key: SkillsMP API key

    Returns:
        Skill data from API or None if not found
    """
    try:
        params = {"q": skill_name, "limit": 5, "sortBy": "stars"}
        result = make_api_request("/skills/search", params, api_key=api_key)

        if not result.get("success"):
            return None

        skills_list = result.get("data", {}).get("skills", [])
        if not skills_list:
            return None

        # Find exact match by name
        for skill in skills_list:
            if skill.get("name", "").lower() == skill_name.lower():
                return skill

        # If no exact match, return first result (best match)
        return skills_list[0]

    except (APIRequestError, SkillsMPError):
        return None


def format_timestamp(unix_timestamp: int) -> str:
    """Convert Unix timestamp to readable date."""
    return datetime.fromtimestamp(unix_timestamp).strftime("%Y-%m-%d")


def check_skill_updates(skills_dir: Optional[Path] = None, api_key: Optional[str] = None) -> Dict:
    """
    Check all installed skills for available updates.

    Args:
        skills_dir: Custom skills directory
        api_key: API key for SkillsMP API

    Returns:
        Dict with 'updates', 'up_to_date', 'not_found', 'errors' lists
    """
    if skills_dir is None:
        skills_dir = get_claude_skills_dir()

    installed_skills = get_installed_skills_with_metadata(skills_dir)

    result: Dict[str, List[Any]] = {
        "updates": [],  # Skills with remote updates
        "up_to_date": [],  # Skills that are current
        "not_found": [],  # Skills not found on SkillsMP
        "errors": [],  # Skills that had errors
    }

    if not installed_skills:
        return result

    print(f"🔍 Checking {len(installed_skills)} installed skills for updates...\n")

    for i, skill in enumerate(installed_skills, 1):
        skill_name = skill["name"]
        local_mtime = skill["local_modified"]

        # Show progress
        print(f"[{i}/{len(installed_skills)}] Checking {skill_name}...", end=" ")

        # Search on SkillsMP
        remote_skill = search_skill_on_skillsmp(skill_name, api_key=api_key)

        if not remote_skill:
            print("❓ Not found on SkillsMP")
            result["not_found"].append(skill)
            # Add small delay to avoid rate limiting
            time.sleep(0.3)
            continue

        # Extract remote data
        remote_updated = remote_skill.get("updatedAt", 0)
        remote_updated_date = format_timestamp(remote_updated)
        github_url = remote_skill.get("githubUrl", "")
        skill_url = remote_skill.get("skillUrl", "")
        stars = remote_skill.get("stars", 0)

        # Compare timestamps (allow 1 second tolerance for file system precision)
        if remote_updated > local_mtime + 1:
            print(f"⚠️ Update available!")
            print(f"   Local: {skill['local_modified_date']} | Remote: {remote_updated_date}")
            result["updates"].append(
                {
                    "name": skill_name,
                    "local_date": skill["local_modified_date"],
                    "remote_date": remote_updated_date,
                    "local_timestamp": local_mtime,
                    "remote_timestamp": remote_updated,
                    "github_url": github_url,
                    "skill_url": skill_url,
                    "stars": stars,
                }
            )
        else:
            print("✅ Up to date")
            result["up_to_date"].append(skill)

        # Add small delay to avoid rate limiting
        time.sleep(0.3)

    return result


def format_update_summary(result: Dict):
    """Format and display update check results."""
    updates = result["updates"]
    up_to_date = result["up_to_date"]
    not_found = result["not_found"]
    errors = result["errors"]

    print("\n" + "=" * 60)
    print("📊 UPDATE CHECK SUMMARY")
    print("=" * 60)

    # Show updates
    if updates:
        print(f"\n⚠️ {len(updates)} skill(s) with potential updates:\n")
        for i, update in enumerate(updates, 1):
            print(f"{i}. {update['name']}")
            print(f"   Local: {update['local_date']} | SkillsMP: {update['remote_date']}")
            print(f"   Stars: {update['stars']}")
            print(f"   GitHub: {update['github_url']}")
            print()
    else:
        print("\n✨ No updates found - all checked skills are up to date!\n")

    # Show not found
    if not_found:
        print(f"❓ {len(not_found)} skill(s) not found on SkillsMP:")
        for skill in not_found:
            print(f"   - {skill['name']}")
        print()

    # Show errors
    if errors:
        print(f"❌ {len(errors)} skill(s) had errors:")
        for error in errors:
            print(f"   - {error['name']}: {error['error']}")
        print()

    # Show summary
    total_checked = len(updates) + len(up_to_date)
    print(f"Total checked: {total_checked}")
    print(f"Up to date: {len(up_to_date)}")
    print(f"Updates available: {len(updates)}")
    print(f"Not found: {len(not_found)}")
    print(f"Errors: {len(errors)}")


def interactive_details_loop(result: Dict, api_key: Optional[str] = None):
    """
    Interactive loop for viewing skill details and updating.

    Args:
        result: Update check result from check_skill_updates()
        api_key: API key for API requests
    """
    updates = result["updates"]

    if not updates:
        return

    while True:
        print("\n" + "=" * 60)
        print(
            "View details? Enter skill number (1-{}) or 'q' to quit:".format(len(updates)), end=" "
        )

        try:
            user_input = input().strip()

            if user_input.lower() == "q":
                print("👋 Exiting update checker.")
                break

            skill_index = int(user_input)
            if skill_index < 1 or skill_index > len(updates):
                print(f"❌ Invalid number. Please enter 1-{len(updates)} or 'q'")
                continue

            # Get selected update
            selected = updates[skill_index - 1]
            skill_name = selected["name"]
            github_url = selected["github_url"]

            # Import skill_diff to show details
            import subprocess

            print(f"\n🔍 Fetching details for {skill_name}...")
            subprocess.run(
                ["python", "skill_diff.py", skill_name],
                cwd=Path(__file__).parent,
                capture_output=False,
            )

            # Ask if user wants to update
            print("\n" + "=" * 60)
            print("Update this skill? [Y/n]:", end=" ")

            update_choice = input().strip().lower()

            if update_choice == "n":
                print("⏭️  Skipped")
                continue

            if update_choice in ("", "y", "yes"):
                # Import and run skill_downloader
                print(f"\n📦 Updating {skill_name}...")

                update_result = subprocess.run(
                    ["python", "skill_downloader.py", skill_name, "--github-url", github_url],
                    cwd=Path(__file__).parent,
                    capture_output=False,
                )

                if update_result.returncode == 0:
                    print(f"\n✅ {skill_name} updated successfully!")
                else:
                    print(f"\n❌ {skill_name} update failed")
            else:
                print("⏭️  Skipped (invalid input)")

        except ValueError:
            print("❌ Invalid input. Please enter a number or 'q'")
        except KeyboardInterrupt:
            print("\n👋 Exiting update checker.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Check SkillsMP skills for available updates")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--api-key", help="API key (overrides file)")
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Disable interactive mode (exit after showing summary)",
    )

    args = parser.parse_args()

    try:
        result = check_skill_updates(api_key=args.api_key)

        if args.json:
            # Convert to JSON-serializable format
            json_result = {
                "updates": result["updates"],
                "up_to_date": [
                    {"name": s["name"], "local_date": s["local_modified_date"]}
                    for s in result["up_to_date"]
                ],
                "not_found": [s["name"] for s in result["not_found"]],
                "errors": result["errors"],
            }
            print(json.dumps(json_result, indent=2))
        else:
            format_update_summary(result)

            # Interactive mode (only if updates found, not disabled, and in TTY)
            if result["updates"] and not args.no_interactive and sys.stdin.isatty():
                interactive_details_loop(result, api_key=args.api_key)

    except SkillsMPError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

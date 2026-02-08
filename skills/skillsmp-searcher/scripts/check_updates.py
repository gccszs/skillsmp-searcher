#!/usr/bin/env python3
"""
SkillsMP Skill Update Checker
Check for updates to installed skills.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Fix UTF-8 encoding for Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from utils import (
    APIRequestError,
    SkillsMPError,
    get_claude_skills_dir,
    list_installed_skills,
    load_api_key,
    make_api_request,
)

# Cache file to store update check timestamps
CACHE_FILE = Path.home() / ".skillsmp" / "update_cache.json"
CACHE_TTL = timedelta(hours=1)  # Check for updates at most once per hour


def read_cache() -> dict:
    """Read update check cache."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def write_cache(data: dict):
    """Write update check cache."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)


def should_check_updates(skill_name: str) -> bool:
    """Check if we should verify updates for this skill (respects TTL)."""
    cache = read_cache()
    last_check = cache.get(skill_name)

    if not last_check:
        return True

    last_check_time = datetime.fromisoformat(last_check)
    return datetime.now() - last_check_time > CACHE_TTL


def mark_as_checked(skill_name: str):
    """Mark a skill as having been checked for updates."""
    cache = read_cache()
    cache[skill_name] = datetime.now().isoformat()
    write_cache(cache)


def check_skill_updates(
    skills_dir: Path = None, force: bool = False, api_key: str = None
) -> list[dict]:
    """
    Check all installed skills for available updates.

    Args:
        skills_dir: Custom skills directory
        force: Force check even if within TTL
        api_key: API key for SkillsMP API

    Returns:
        List of skills with available updates
    """
    if skills_dir is None:
        skills_dir = get_claude_skills_dir()

    skills = list_installed_skills(skills_dir)
    updates_available = []

    print(f"🔍 Checking {len(skills)} installed skills for updates...\n")

    for skill_name in skills:
        # Check TTL unless forced
        if not force and not should_check_updates(skill_name):
            print(f"⏭️  Skipping {skill_name} (checked recently)")
            continue

        try:
            # Get skill metadata
            skill_dir = skills_dir / skill_name
            skill_md = skill_dir / "SKILL.md"

            if not skill_md.exists():
                continue

            # Read current version from SKILL.md
            with open(skill_md, "r", encoding="utf-8") as f:
                content = f.read()
                # Try to extract version from frontmatter
                current_version = "unknown"
                for line in content.split("\n")[:20]:  # Check first 20 lines
                    if "version:" in line.lower():
                        current_version = line.split(":")[1].strip()
                        break

            # Query SkillsMP API for latest version
            # Note: This assumes the API provides a skills/check-updates endpoint
            # You may need to adjust based on actual API
            params = {"skill": skill_name}
            result = make_api_request("/skills/check-updates", params, api_key=api_key)

            if result.get("success"):
                skill_data = result.get("data", {})
                latest_version = skill_data.get("version", "unknown")
                latest_stars = skill_data.get("stars", 0)

                if latest_version != current_version and latest_version != "unknown":
                    updates_available.append(
                        {
                            "name": skill_name,
                            "current_version": current_version,
                            "latest_version": latest_version,
                            "stars": latest_stars,
                            "repository": skill_data.get("repository_url", ""),
                        }
                    )
                    print(f"✨ {skill_name}: Update available!")
                    print(f"   {current_version} → {latest_version}")
                else:
                    print(f"✅ {skill_name}: Up to date ({current_version})")

                # Mark as checked
                mark_as_checked(skill_name)

        except (APIRequestError, SkillsMPError) as e:
            print(f"⚠️  {skill_name}: Could not check updates ({e})")
        except Exception as e:
            print(f"❌ {skill_name}: Error ({e})")

    return updates_available


def format_updates(updates: list[dict]):
    """Format available updates for display."""
    if not updates:
        print("\n✨ All skills are up to date!")
        return

    print(f"\n📦 {len(updates)} update(s) available:\n")

    for i, update in enumerate(updates, 1):
        print(f"{i}. {update['name']}")
        print(f"   Current: {update['current_version']}")
        print(f"   Latest: {update['latest_version']}")
        print(f"   Stars: {update['stars']}")

        if update["repository"]:
            repo = update["repository"].split("github.com/")[-1]
            print(f"   Update: npx skills add {repo}")

        print()


def main():
    parser = argparse.ArgumentParser(
        description="Check SkillsMP skills for available updates"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force check even if recently checked",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    parser.add_argument("--api-key", help="API key (overrides file)")

    args = parser.parse_args()

    try:
        updates = check_skill_updates(force=args.force, api_key=args.api_key)

        if args.json:
            print(json.dumps(updates, indent=2))
        else:
            format_updates(updates)

    except SkillsMPError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

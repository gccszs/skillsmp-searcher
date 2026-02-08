#!/usr/bin/env python3
"""
SkillsMP Skill Downloader
Download and install skill updates from GitHub or SkillsMP.
"""

import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

import requests
from utils import (
    APIRequestError,
    SkillsMPError,
    get_claude_skills_dir,
    install_skill,
    load_api_key,
    make_api_request,
)


def infer_download_url(github_url: str, skill_name: str) -> Optional[str]:
    """
    Infer download URL from GitHub URL.

    Attempts to construct GitHub Releases download URL.

    Args:
        github_url: GitHub repository URL
        skill_name: Name of the skill

    Returns:
        Download URL or None if cannot be inferred
    """
    # Extract owner/repo from GitHub URL
    # Format: https://github.com/owner/repo/tree/branch/skills/skill-name
    match = re.search(r"github\.com/([^/]+)/([^/]+)", github_url)
    if not match:
        return None

    owner, repo = match.groups()

    # Try GitHub Releases latest download
    # Common patterns: skill-name.skill, repo-name.skill, etc.
    possible_filenames = [
        f"{skill_name}.skill",
        f"{repo}.skill",
        f"{owner}-{repo}.skill",
    ]

    for filename in possible_filenames:
        download_url = f"https://github.com/{owner}/{repo}/releases/latest/download/{filename}"
        return download_url

    return None


def download_skill_file(download_url: str, dest_path: Path) -> bool:
    """
    Download skill file from URL.

    Args:
        download_url: URL to download from
        dest_path: Destination file path

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"📥 Downloading from: {download_url}")
        response = requests.get(download_url, stream=True, timeout=30)

        if response.status_code == 404:
            print("❌ Download failed: File not found (404)")
            return False

        response.raise_for_status()

        # Download to file
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"✅ Downloaded to: {dest_path}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        return False


def backup_skill_directory(skill_dir: Path) -> Optional[Path]:
    """
    Create backup of existing skill directory.

    Args:
        skill_dir: Path to skill directory

    Returns:
        Backup directory path or None if failed
    """
    try:
        parent = skill_dir.parent
        backup_name = f"{skill_dir.name}.backup"
        backup_path = parent / backup_name

        # Remove existing backup if present
        if backup_path.exists():
            shutil.rmtree(backup_path)

        # Create backup
        shutil.copytree(skill_dir, backup_path)
        print(f"📦 Backup created: {backup_path}")
        return backup_path

    except Exception as e:
        print(f"⚠️  Warning: Could not create backup: {e}")
        return None


def install_skill_update(
    skill_name: str,
    download_url: Optional[str] = None,
    github_url: Optional[str] = None,
    skills_dir: Optional[Path] = None,
    api_key: Optional[str] = None,
    backup: bool = True,
) -> bool:
    """
    Download and install skill update.

    Args:
        skill_name: Name of the skill to update
        download_url: Direct download URL (optional)
        github_url: GitHub repository URL (for inferring download URL)
        skills_dir: Skills directory
        api_key: API key
        backup: Whether to backup existing installation

    Returns:
        True if successful, False otherwise
    """
    if skills_dir is None:
        skills_dir = get_claude_skills_dir()

    # Find existing skill directory
    skill_dir = None
    for item in skills_dir.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            # Extract name from frontmatter
            import skill_diff

            frontmatter = skill_diff.extract_frontmatter(item / "SKILL.md")
            if frontmatter.get("name", "").lower() == skill_name.lower():
                skill_dir = item
                break

    if not skill_dir:
        print(f"❌ Skill '{skill_name}' not found locally")
        return False

    # Determine download URL
    if not download_url and github_url:
        download_url = infer_download_url(github_url, skill_name)

    if not download_url:
        print("❌ No download URL available")
        print("   Please provide --download-url or --github-url")
        return False

    # Create backup
    backup_path = None
    if backup:
        backup_path = backup_skill_directory(skill_dir)

    # Download to temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "downloaded.skill"
        if not download_skill_file(download_url, temp_path):
            return False

        # Verify it's a valid zip file (skill package)
        try:
            with zipfile.ZipFile(temp_path, "r") as zip_ref:
                namelist = zip_ref.namelist()
                if not namelist:
                    print("❌ Invalid skill file: empty archive")
                    return False
        except zipfile.BadZipFile:
            print("❌ Invalid skill file: not a valid zip archive")
            return False

        # Remove existing installation
        try:
            shutil.rmtree(skill_dir)
        except Exception as e:
            print(f"⚠️  Warning: Could not remove old installation: {e}")
            # Try to remove backup and restore
            if backup_path and backup_path.exists():
                shutil.rmtree(backup_path)
            return False

        # Install new version
        try:
            installed_path = install_skill(temp_path, skills_dir=skills_dir)
            print(f"✅ Successfully updated: {skill_name}")
            print(f"   Location: {installed_path}")

            # Remove backup on success
            if backup_path and backup_path.exists():
                shutil.rmtree(backup_path)
                print("🗑️  Backup removed (update successful)")

            return True

        except Exception as e:
            print(f"❌ Installation failed: {e}")

            # Restore from backup
            if backup_path and backup_path.exists():
                print(f"🔄 Restoring from backup...")
                try:
                    shutil.copytree(backup_path, skill_dir)
                    print("✅ Successfully restored from backup")
                except Exception as restore_error:
                    print(f"❌ Could not restore backup: {restore_error}")

            return False


def main():
    parser = argparse.ArgumentParser(description="Download and install skill updates from SkillsMP")
    parser.add_argument("skill_name", help="Name of the skill to update")

    download_group = parser.add_mutually_exclusive_group()
    download_group.add_argument("--download-url", help="Direct download URL")
    download_group.add_argument(
        "--github-url",
        help="GitHub repository URL (will infer download URL)",
    )

    parser.add_argument(
        "--skill-dir",
        type=Path,
        help="Custom skills directory (default: ~/.claude/skills)",
    )
    parser.add_argument("--api-key", help="API key (overrides file)")
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup before installing",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually installing",
    )

    args = parser.parse_args()

    try:
        if args.dry_run:
            print("🔍 Dry run mode - showing planned actions:\n")
            print(f"Skill to update: {args.skill_name}")

            if args.download_url:
                print(f"Download URL: {args.download_url}")
            elif args.github_url:
                inferred = infer_download_url(args.github_url, args.skill_name)
                print(f"GitHub URL: {args.github_url}")
                print(f"Inferred download URL: {inferred}")
            else:
                print("❌ No download source specified")
                sys.exit(1)

            backup_msg = "Backup: " + ("No (disabled)" if args.no_backup else "Yes")
            print(backup_msg)
            print("\n✅ Dry run complete - no changes made")
            return

        # Perform actual installation
        success = install_skill_update(
            skill_name=args.skill_name,
            download_url=args.download_url,
            github_url=args.github_url,
            skills_dir=args.skill_dir,
            api_key=args.api_key,
            backup=not args.no_backup,
        )

        sys.exit(0 if success else 1)

    except SkillsMPError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

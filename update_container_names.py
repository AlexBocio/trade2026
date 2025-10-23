#!/usr/bin/env python3
"""
Automated script to prefix all container names with 'trade2026-'
Updates all docker-compose.yml files in the infrastructure/docker directory
"""

import os
import re
from pathlib import Path

# Docker compose files to update
COMPOSE_FILES = [
    "infrastructure/docker/docker-compose.core.yml",
    "infrastructure/docker/docker-compose.apps.yml",
    "infrastructure/docker/docker-compose.backend-services.yml",
    "infrastructure/docker/docker-compose.frontend.yml",
    "infrastructure/docker/docker-compose.library.yml",
    "infrastructure/docker/docker-compose.library-db.yml",
    "infrastructure/docker/docker-compose.data-ingestion.yml",
    "infrastructure/docker/docker-compose.api-gateway.yml",
]

def update_container_names(file_path):
    """Update container_name and hostname fields in a docker-compose file"""

    if not os.path.exists(file_path):
        print(f"[WARN] Skipping {file_path} (not found)")
        return 0

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes = 0

    # Pattern 1: container_name: <name> (not already prefixed)
    def replace_container_name(match):
        nonlocal changes
        indent = match.group(1)
        name = match.group(2)
        if not name.startswith('trade2026-'):
            changes += 1
            return f'{indent}container_name: trade2026-{name}'
        return match.group(0)

    content = re.sub(
        r'^(\s*)container_name:\s+([a-z0-9_-]+)',
        replace_container_name,
        content,
        flags=re.MULTILINE
    )

    # Pattern 2: hostname: <name> (not already prefixed)
    def replace_hostname(match):
        nonlocal changes
        indent = match.group(1)
        name = match.group(2)
        if not name.startswith('trade2026-'):
            changes += 1
            return f'{indent}hostname: trade2026-{name}'
        return match.group(0)

    content = re.sub(
        r'^(\s*)hostname:\s+([a-z0-9_-]+)',
        replace_hostname,
        content,
        flags=re.MULTILINE
    )

    # Only write if changes were made
    if content != original_content:
        # Create backup
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"[BACKUP] Backed up to: {backup_path}")

        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Updated {file_path}: {changes} changes")
    else:
        print(f"[SKIP] No changes needed in {file_path}")

    return changes

def main():
    """Main execution"""
    print("=" * 70)
    print("Trade2026 Container Name Prefix Update Script")
    print("=" * 70)
    print()

    total_changes = 0

    for compose_file in COMPOSE_FILES:
        changes = update_container_names(compose_file)
        total_changes += changes
        print()

    print("=" * 70)
    print(f"Total changes: {total_changes}")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review changes in each file")
    print("2. Stop all containers: docker-compose down")
    print("3. Start with new names: docker-compose up -d")
    print("4. Check health: docker ps")
    print()

if __name__ == "__main__":
    main()

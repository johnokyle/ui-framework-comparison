#!/usr/bin/env python3
"""Generate a reproducible target-specific Cargo license inventory."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

NOTICE_PREFIXES = ("LICENSE", "LICENCE", "COPYING", "NOTICE")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-path", required=True, type=Path)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def source_revision(repository: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def notice_files(package: dict[str, Any]) -> list[str]:
    root = Path(package["manifest_path"]).parent
    files = {
        path.name
        for path in root.iterdir()
        if path.is_file() and path.name.upper().startswith(NOTICE_PREFIXES)
    }
    declared = package.get("license_file")
    if declared:
        path = Path(declared)
        if not path.is_absolute():
            path = root / path
        if path.is_file():
            files.add(path.name)
    return sorted(files)


def cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render(
    metadata: dict[str, Any], manifest_path: Path, target: str, revision: str
) -> str:
    workspace = set(metadata["workspace_members"])
    packages = sorted(
        (package for package in metadata["packages"] if package["id"] not in workspace),
        key=lambda package: (package["name"], package["version"], package["id"]),
    )
    root = metadata["resolve"].get("root")
    root_name = "workspace"
    if root:
        root_package = next(package for package in metadata["packages"] if package["id"] == root)
        root_name = f"{root_package['name']} {root_package['version']}"

    rows = []
    missing = 0
    for package in packages:
        notices = notice_files(package)
        missing += not notices
        rows.append(
            "| {name} | {version} | {license} | {notices} |".format(
                name=cell(package["name"]),
                version=cell(package["version"]),
                license=cell(package.get("license") or "NOT DECLARED"),
                notices=cell(", ".join(notices)) if notices else "**None found**",
            )
        )

    relative_manifest = manifest_path.name
    return "\n".join(
        [
            "# Cargo target-resolution license inventory",
            "",
            f"Package: `{root_name}`",
            f"Source revision: `{revision}`",
            f"Target: `{target}`",
            "",
            "Generated with:",
            "",
            "```bash",
            f"cargo metadata --locked --format-version 1 --filter-platform {target} --manifest-path {relative_manifest}",
            "```",
            "",
            f"The inventory contains {len(packages)} non-workspace packages. "
            f"{missing} packages have no license/notice file at their package root.",
            "",
            "This is a Cargo resolution inventory, not proof of the exact code linked into a binary "
            "and not a complete legal notice bundle. Verify the actual release features and artifacts, "
            "retain the applicable license texts and copyright notices, and resolve every missing-file "
            "entry from the corresponding upstream package before distribution.",
            "",
            "| Package | Version | Declared license | Package-root license/notice files |",
            "|---|---|---|---|",
            *rows,
            "",
        ]
    )


def main() -> None:
    args = parse_args()
    manifest_path = args.manifest_path.resolve()
    result = subprocess.run(
        [
            "cargo",
            "metadata",
            "--locked",
            "--format-version",
            "1",
            "--filter-platform",
            args.target,
            "--manifest-path",
            str(manifest_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    metadata = json.loads(result.stdout)
    output = render(
        metadata,
        manifest_path,
        args.target,
        source_revision(manifest_path.parent),
    )
    args.output.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Copy the Beakr skill and slash commands from beakr-cli, or check the copies.

beakr-cli is the source of truth: it bundles the same skill into its wheel and
`beakr setup` installs it. This repository ships a copy so plugins install
without the CLI's help. The copy must not drift, so CI runs ``--check``.

What is synced, from a beakr-cli tree at the ref pinned in ``tools/beakr-cli.ref``:

- ``.claude/skills/beakr/**``   -> ``skills/beakr/**``  (byte-for-byte)
- ``.claude/commands/kb-*.md``  -> ``commands/kb-*.md`` (with the YAML frontmatter
  from ``tools/command-frontmatter.json`` prepended; plugin validators require it
  and beakr-cli's copies have none)

Usage:
    tools/sync_from_beakr_cli.py --check            # CI: fail on any drift
    tools/sync_from_beakr_cli.py                    # rewrite the copies
    tools/sync_from_beakr_cli.py --source ../beakr-cli   # use a local checkout
                                                    # (its working tree, not the pin)

To move to a newer beakr-cli, put the new commit SHA in tools/beakr-cli.ref,
run this without --check, review the diff, and commit both together.
"""

from __future__ import annotations

import argparse
import io
import json
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REF_FILE = REPO_ROOT / "tools" / "beakr-cli.ref"
FRONTMATTER_FILE = REPO_ROOT / "tools" / "command-frontmatter.json"
UPSTREAM_REPO = "BeakrHub/beakr-cli"

SKILL_SRC = Path(".claude/skills/beakr")
SKILL_DST = Path("skills/beakr")
COMMANDS_SRC = Path(".claude/commands")
COMMANDS_DST = Path("commands")
COMMAND_GLOB = "kb-*.md"


def pinned_ref() -> str:
    ref = REF_FILE.read_text().strip()
    if len(ref) != 40 or any(c not in "0123456789abcdef" for c in ref):
        sys.exit(f"{REF_FILE} must hold a full 40-character commit SHA, got {ref!r}")
    return ref


def fetch_upstream(ref: str, into: Path) -> Path:
    """Download beakr-cli at ``ref`` (the repository is public) and return its root."""
    url = f"https://codeload.github.com/{UPSTREAM_REPO}/tar.gz/{ref}"
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = [
            m
            for m in archive.getmembers()
            if "/.claude/skills/beakr/" in m.name or "/.claude/commands/" in m.name
        ]
        archive.extractall(into, members=members, filter="data")
    roots = list(into.iterdir())
    if len(roots) != 1:
        sys.exit(f"unexpected archive layout from {url}")
    return roots[0]


def render_command(name: str, body: str, frontmatter: dict[str, dict[str, str]]) -> str:
    fields = frontmatter.get(name)
    if fields is None:
        sys.exit(
            f"commands/{name} has no entry in {FRONTMATTER_FILE.name}; "
            "add its description and argument-hint there"
        )
    lines = ["---"] + [f"{key}: {json.dumps(value)}" for key, value in fields.items()] + ["---"]
    return "\n".join(lines) + "\n\n" + body


def expected_files(upstream: Path) -> dict[Path, bytes]:
    """Every synced file this repository should contain, by repo-relative path."""
    files: dict[Path, bytes] = {}
    skill_root = upstream / SKILL_SRC
    if not skill_root.is_dir():
        sys.exit(f"{skill_root} not found in beakr-cli")
    for path in sorted(skill_root.rglob("*")):
        if path.is_file():
            files[SKILL_DST / path.relative_to(skill_root)] = path.read_bytes()

    frontmatter = json.loads(FRONTMATTER_FILE.read_text())
    for path in sorted((upstream / COMMANDS_SRC).glob(COMMAND_GLOB)):
        rendered = render_command(path.name, path.read_text(), frontmatter)
        files[COMMANDS_DST / path.name] = rendered.encode()
    return files


def current_files() -> dict[Path, bytes]:
    files: dict[Path, bytes] = {}
    for path in sorted((REPO_ROOT / SKILL_DST).rglob("*")):
        if path.is_file():
            files[path.relative_to(REPO_ROOT)] = path.read_bytes()
    for path in sorted((REPO_ROOT / COMMANDS_DST).glob(COMMAND_GLOB)):
        files[path.relative_to(REPO_ROOT)] = path.read_bytes()
    return files


def drift(expected: dict[Path, bytes], actual: dict[Path, bytes]) -> list[str]:
    problems = []
    for path in sorted(expected.keys() | actual.keys()):
        if path not in actual:
            problems.append(f"missing: {path}")
        elif path not in expected:
            problems.append(f"not in beakr-cli: {path}")
        elif expected[path] != actual[path]:
            problems.append(f"differs: {path}")
    return problems


def write(expected: dict[Path, bytes]) -> None:
    shutil.rmtree(REPO_ROOT / SKILL_DST, ignore_errors=True)
    for path in (REPO_ROOT / COMMANDS_DST).glob(COMMAND_GLOB):
        path.unlink()
    for rel, content in expected.items():
        target = REPO_ROOT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="fail if the copies drift")
    parser.add_argument(
        "--source",
        type=Path,
        help="a local beakr-cli checkout to read instead of the pinned ref",
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        if args.source:
            upstream = args.source.resolve()
            origin = f"{upstream} (working tree)"
        else:
            ref = pinned_ref()
            upstream = fetch_upstream(ref, Path(tmp))
            origin = f"{UPSTREAM_REPO}@{ref}"
        expected = expected_files(upstream)

    if args.check:
        problems = drift(expected, current_files())
        if problems:
            print(f"Skill/commands out of sync with {origin}:", file=sys.stderr)
            for line in problems:
                print(f"  {line}", file=sys.stderr)
            print("Run tools/sync_from_beakr_cli.py and commit the result.", file=sys.stderr)
            return 1
        print(f"In sync with {origin}: {len(expected)} files.")
        return 0

    write(expected)
    print(f"Synced {len(expected)} files from {origin}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

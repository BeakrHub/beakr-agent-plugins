#!/usr/bin/env python3
"""Validate every manifest and config in this repository.

Checks, in order:

1. Every JSON file parses.
2. Manifests validate against their published JSON schemas, vendored in
   ``schemas/`` (see ``schemas/README.md`` for where each comes from):
   Agent Plugins 1.0 for ``plugin.json`` and ``mcp.json``, SchemaStore's Claude
   Code schemas for ``.claude-plugin/plugin.json`` and ``marketplace.json``.
3. Formats without a published schema (the Codex and Cursor marketplaces, the
   Gemini extension, hooks, the example configs) get structural checks taken
   from each client's documentation.
4. Cross-file consistency: one plugin name and version everywhere, every path a
   manifest points at exists, launchers are executable, the skill's frontmatter
   matches its directory.

Run with ``uv run --with jsonschema tools/validate.py``. Exits 1 on any problem.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

from jsonschema import validators

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = REPO_ROOT / "schemas"
PLUGIN_NAME = "beakr"

SCHEMA_FOR = {
    "plugin.json": "agent-plugins-1.0.0-plugin.schema.json",
    "mcp.json": "agent-plugins-1.0.0-mcp.schema.json",
    ".claude-plugin/plugin.json": "claude-code-plugin-manifest.json",
    ".claude-plugin/marketplace.json": "claude-code-marketplace.json",
}

CODEX_INSTALLATION = {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"}
CODEX_AUTHENTICATION = {"ON_INSTALL", "ON_FIRST_USE"}
CLAUDE_HOOK_EVENTS = {
    "SessionStart",
    "SessionEnd",
    "Stop",
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "PreCompact",
    "Notification",
    "SubagentStop",
}

problems: list[str] = []


def fail(message: str) -> None:
    problems.append(message)


def load(rel: str) -> Any:
    return json.loads((REPO_ROOT / rel).read_text())


def tracked_files() -> list[str]:
    """Files git knows about (tracked or new), so stray local files are ignored."""
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if (REPO_ROOT / line).is_file()]


def inside_repo(rel: str) -> Path | None:
    path = (REPO_ROOT / rel).resolve()
    if path != REPO_ROOT and REPO_ROOT not in path.parents:
        return None
    return path


# ---------------------------------------------------------------------------


def check_json_parses(files: list[str]) -> None:
    for rel in files:
        if rel.endswith(".json"):
            try:
                load(rel)
            except ValueError as exc:
                fail(f"{rel}: invalid JSON ({exc})")


def check_schemas() -> None:
    for rel, schema_file in SCHEMA_FOR.items():
        schema = json.loads((SCHEMAS / schema_file).read_text())
        validator_class = validators.validator_for(schema)
        validator_class.check_schema(schema)
        for error in sorted(validator_class(schema).iter_errors(load(rel)), key=str):
            where = "/".join(str(p) for p in error.absolute_path) or "(root)"
            fail(f"{rel}: {where}: {error.message} [schema {schema_file}]")


def check_codex_marketplace() -> None:
    rel = ".agents/plugins/marketplace.json"
    data = load(rel)
    if data.get("name") != PLUGIN_NAME:
        fail(f"{rel}: name must be {PLUGIN_NAME!r}")
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        fail(f"{rel}: plugins must be a non-empty list")
        return
    for entry in plugins:
        source = entry.get("source")
        if isinstance(source, str):
            path = source
        elif isinstance(source, dict) and source.get("source") == "local":
            path = source.get("path")
        else:
            fail(f"{rel}: plugin {entry.get('name')!r} must use a local source")
            continue
        if not isinstance(path, str) or inside_repo(path) is None:
            fail(f"{rel}: plugin {entry.get('name')!r} source path must stay inside the repository")
        policy = entry.get("policy", {})
        if policy.get("installation") not in CODEX_INSTALLATION:
            fail(f"{rel}: policy.installation must be one of {sorted(CODEX_INSTALLATION)}")
        if policy.get("authentication") not in CODEX_AUTHENTICATION:
            fail(f"{rel}: policy.authentication must be one of {sorted(CODEX_AUTHENTICATION)}")


def check_cursor_marketplace() -> None:
    rel = ".cursor-plugin/marketplace.json"
    data = load(rel)
    if data.get("name") != PLUGIN_NAME or not isinstance(data.get("owner"), dict):
        fail(f"{rel}: needs name {PLUGIN_NAME!r} and an owner object")
    for entry in data.get("plugins") or []:
        if not isinstance(entry.get("source"), str) or inside_repo(entry["source"]) is None:
            fail(f"{rel}: plugin {entry.get('name')!r} source must be a path inside the repository")


def check_gemini_extension() -> None:
    rel = "gemini-extension.json"
    data = load(rel)
    for key in ("name", "version"):
        if not isinstance(data.get(key), str) or not data[key]:
            fail(f"{rel}: {key} is required")
    if not re.fullmatch(r"[a-z0-9-]+", data.get("name", "")):
        fail(f"{rel}: name must be lowercase letters, digits and dashes")
    context = data.get("contextFileName")
    if context and not (REPO_ROOT / context).is_file():
        fail(f"{rel}: contextFileName {context!r} does not exist")
    for name, server in (data.get("mcpServers") or {}).items():
        kinds = [key for key in ("command", "url", "httpUrl") if key in server]
        if len(kinds) != 1:
            fail(f"{rel}: server {name!r} needs exactly one of command, url, httpUrl")
        for arg in server.get("args", []):
            local = arg.replace("${extensionPath}", ".").replace("${/}", "/")
            if local.startswith("./") and not (REPO_ROOT / local).is_file():
                fail(f"{rel}: server {name!r} arg {arg!r} points at a missing file")


def check_claude_plugin_paths() -> None:
    rel = ".claude-plugin/plugin.json"
    manifest = load(rel)
    for key in ("mcpServers", "hooks"):
        value = manifest.get(key)
        if isinstance(value, str):
            if not value.startswith("./"):
                fail(f"{rel}: {key} path must start with ./")
            elif not (REPO_ROOT / value).is_file():
                fail(f"{rel}: {key} points at missing {value}")

    hooks_rel = manifest.get("hooks")
    if isinstance(hooks_rel, str) and (REPO_ROOT / hooks_rel).is_file():
        hooks = load(hooks_rel).get("hooks")
        if not isinstance(hooks, dict):
            fail(f"{hooks_rel}: events must sit under a top-level 'hooks' object")
            hooks = {}
        for event, groups in hooks.items():
            if event not in CLAUDE_HOOK_EVENTS:
                fail(f"{hooks_rel}: unknown event {event!r}")
            for group in groups:
                for hook in group.get("hooks", []):
                    command = hook.get("command", "")
                    script = re.search(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"' ]+)", command)
                    if hook.get("type") != "command" or not script:
                        fail(f"{hooks_rel}: {event} hook must run a script under ${{CLAUDE_PLUGIN_ROOT}}")
                        continue
                    check_executable(script.group(1), hooks_rel)

    servers = load(".mcp.json").get("mcpServers", {})
    for name, server in servers.items():
        command = server.get("command", "")
        if command.startswith("${CLAUDE_PLUGIN_ROOT}/"):
            check_executable(command.removeprefix("${CLAUDE_PLUGIN_ROOT}/"), ".mcp.json")
        elif "url" not in server:
            fail(f".mcp.json: server {name!r} must run a bundled script or use a url")


def check_agent_plugins_mcp() -> None:
    for name, server in load("mcp.json")["mcpServers"].items():
        command = server.get("command")
        if command and command.startswith("./"):
            check_executable(command, "mcp.json")
        elif command:
            fail(f"mcp.json: server {name!r} should run the bundled ./scripts launcher")


def check_executable(rel: str, referenced_from: str) -> None:
    path = inside_repo(rel)
    if path is None or not path.is_file():
        fail(f"{referenced_from}: {rel} does not exist")
    elif not os.access(path, os.X_OK):
        fail(f"{referenced_from}: {rel} is not executable (chmod +x, and commit the mode)")


def check_versions() -> None:
    versions = {
        "plugin.json": load("plugin.json").get("version"),
        ".claude-plugin/plugin.json": load(".claude-plugin/plugin.json").get("version"),
        "gemini-extension.json": load("gemini-extension.json").get("version"),
    }
    for rel in (".claude-plugin/marketplace.json", ".cursor-plugin/marketplace.json"):
        for entry in load(rel).get("plugins", []):
            if entry.get("name") == PLUGIN_NAME and "version" in entry:
                versions[f"{rel} plugins[{PLUGIN_NAME}]"] = entry["version"]
    if len(set(versions.values())) != 1:
        listing = ", ".join(f"{where}={version}" for where, version in versions.items())
        fail(f"plugin versions disagree: {listing}")

    names = {
        "plugin.json": load("plugin.json").get("name"),
        ".claude-plugin/plugin.json": load(".claude-plugin/plugin.json").get("name"),
        "gemini-extension.json": load("gemini-extension.json").get("name"),
    }
    if set(names.values()) != {PLUGIN_NAME}:
        fail(f"plugin names must all be {PLUGIN_NAME!r}: {names}")


def check_skills() -> None:
    for skill_md in sorted((REPO_ROOT / "skills").glob("*/SKILL.md")):
        text = skill_md.read_text()
        match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        rel = skill_md.relative_to(REPO_ROOT)
        if not match:
            fail(f"{rel}: missing YAML frontmatter")
            continue
        fields = dict(
            line.split(":", 1) for line in match.group(1).splitlines() if ":" in line
        )
        name = fields.get("name", "").strip().strip("\"'")
        if name != skill_md.parent.name:
            fail(f"{rel}: frontmatter name {name!r} must match its directory")
        if not fields.get("description", "").strip():
            fail(f"{rel}: frontmatter description is required")


def check_examples() -> None:
    for rel in ("examples/cursor/mcp.json", "examples/cursor/mcp.remote.json"):
        if not isinstance(load(rel).get("mcpServers"), dict):
            fail(f"{rel}: Cursor configs use a top-level mcpServers object")
    for rel in ("examples/vscode/mcp.json", "examples/vscode/mcp.remote.json"):
        for name, server in (load(rel).get("servers") or {}).items():
            if server.get("type") not in ("stdio", "http", "sse"):
                fail(f"{rel}: server {name!r} needs type stdio, http or sse")
    for rel in ("examples/codex/config.toml", "examples/codex/config.remote.toml"):
        try:
            servers = tomllib.loads((REPO_ROOT / rel).read_text()).get("mcp_servers", {})
        except tomllib.TOMLDecodeError as exc:
            fail(f"{rel}: invalid TOML ({exc})")
            continue
        for name, server in servers.items():
            if ("command" in server) == ("url" in server):
                fail(f"{rel}: [mcp_servers.{name}] needs exactly one of command or url")


def main() -> int:
    files = tracked_files()
    check_json_parses(files)
    if problems:
        # Nothing further is meaningful on unparseable files.
        print("\n".join(problems), file=sys.stderr)
        return 1
    check_schemas()
    check_codex_marketplace()
    check_cursor_marketplace()
    check_gemini_extension()
    check_claude_plugin_paths()
    check_agent_plugins_mcp()
    check_versions()
    check_skills()
    check_examples()
    if problems:
        print(f"{len(problems)} problem(s):", file=sys.stderr)
        for line in problems:
            print(f"  {line}", file=sys.stderr)
        return 1
    print("All manifests and configs are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

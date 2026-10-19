#!/usr/bin/env python3
"""Generate every MCP config and install link in this repository from one switch.

``mcp-variant.json`` at the repository root decides which Beakr MCP server the
plugins ship:

- ``"local"`` (the default): ``beakr mcp`` over stdio, through
  ``scripts/beakr-mcp``. Needs the beakr CLI installed and signed in.
- ``"remote"``: the hosted server at ``remote_url`` (streamable HTTP, OAuth).
  Refused while ``remote_live`` is false, so a placeholder URL can never ship.

Generated files (do not edit them by hand; edit this script or the switch):

- ``.mcp.json``                 Claude Code plugin MCP config
- ``mcp.json``                  Agent Plugins 1.0 MCP config (Codex, Cursor, VS Code)
- ``gemini-extension.json``     Gemini CLI extension manifest
- ``examples/<client>/...``     hand-install configs for both variants
- the install-links block in ``README.md``

Usage:
    tools/render_configs.py           # rewrite the generated files
    tools/render_configs.py --check   # CI: fail if any generated file is stale
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SWITCH = REPO_ROOT / "mcp-variant.json"
AGENT_PLUGIN_MANIFEST = REPO_ROOT / "plugin.json"
README = REPO_ROOT / "README.md"

SERVER_NAME = "beakr"
LOCAL_COMMAND = "beakr"
LOCAL_ARGS = ["mcp"]
AGENT_PLUGINS_MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
LINKS_START = "<!-- generated:install-links:start -->"
LINKS_END = "<!-- generated:install-links:end -->"


def load_switch() -> dict:
    switch = json.loads(SWITCH.read_text())
    variant = switch.get("variant")
    if variant not in ("local", "remote"):
        sys.exit(f"{SWITCH.name}: variant must be 'local' or 'remote', got {variant!r}")
    if variant == "remote" and not switch.get("remote_live"):
        sys.exit(
            f"{SWITCH.name}: variant 'remote' needs remote_live: true. Set it only once "
            f"{switch.get('remote_url')} serves Beakr's hosted MCP in production."
        )
    return switch


def dump(data: object) -> str:
    return json.dumps(data, indent=2) + "\n"


# ---------------------------------------------------------------------------
# Plugin configs: these follow the switch
# ---------------------------------------------------------------------------


def claude_plugin_mcp(switch: dict) -> dict:
    if switch["variant"] == "remote":
        server = {"type": "http", "url": switch["remote_url"]}
    else:
        server = {
            "type": "stdio",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/beakr-mcp",
            "args": [],
        }
    return {"mcpServers": {SERVER_NAME: server}}


def agent_plugins_mcp(switch: dict) -> dict:
    if switch["variant"] == "remote":
        server = {"type": "streamable-http", "url": switch["remote_url"]}
    else:
        # Agent Plugins resolves a "./" command against the plugin root.
        server = {"type": "stdio", "command": "./scripts/beakr-mcp", "args": []}
    return {"$schema": AGENT_PLUGINS_MCP_SCHEMA, "mcpServers": {SERVER_NAME: server}}


def gemini_extension(switch: dict) -> dict:
    manifest = json.loads(AGENT_PLUGIN_MANIFEST.read_text())
    if switch["variant"] == "remote":
        server = {"httpUrl": switch["remote_url"]}
    else:
        # Run through `sh` so the launcher works even if the archive Gemini
        # unpacked lost the executable bit.
        server = {"command": "sh", "args": ["${extensionPath}${/}scripts${/}beakr-mcp"]}
    return {
        "name": manifest["name"],
        "version": manifest["version"],
        "description": manifest["description"],
        "mcpServers": {SERVER_NAME: server},
        "contextFileName": "GEMINI.md",
    }


# ---------------------------------------------------------------------------
# Hand-install examples: both variants, always
# ---------------------------------------------------------------------------


def local_server() -> dict:
    return {"command": LOCAL_COMMAND, "args": LOCAL_ARGS}


def cursor_config(remote_url: str | None) -> dict:
    server = {"url": remote_url} if remote_url else {"type": "stdio", **local_server()}
    return {"mcpServers": {SERVER_NAME: server}}


def vscode_config(remote_url: str | None) -> dict:
    server = {"type": "http", "url": remote_url} if remote_url else {"type": "stdio", **local_server()}
    return {"servers": {SERVER_NAME: server}}


def codex_config(remote_url: str | None) -> str:
    if remote_url:
        return (
            "# Beakr's hosted MCP server. After adding this, sign in with:\n"
            f"#   codex mcp login {SERVER_NAME}\n"
            f"[mcp_servers.{SERVER_NAME}]\n"
            f'url = "{remote_url}"\n'
        )
    return (
        "# Beakr's local MCP server: needs the beakr CLI installed and signed in\n"
        "# (`beakr auth login`, or BEAKR_API_KEY passed through env_vars below).\n"
        "# If Codex cannot find `beakr`, replace it with the output of `which beakr`.\n"
        "# Writes are attributed to Codex automatically; BEAKR_AGENT overrides that\n"
        "# label, and BEAKR_MCP_TOOLS=eager lists fewer tools (see the README).\n"
        f"[mcp_servers.{SERVER_NAME}]\n"
        f'command = "{LOCAL_COMMAND}"\n'
        f"args = {json.dumps(LOCAL_ARGS)}\n"
        'env_vars = ["BEAKR_API_KEY", "BEAKR_API_URL", "BEAKR_AGENT", "BEAKR_MCP_TOOLS"]\n'
    )


# ---------------------------------------------------------------------------
# Install links
# ---------------------------------------------------------------------------


def cursor_deeplink(server: dict) -> str:
    config = base64.b64encode(json.dumps(server, separators=(",", ":")).encode()).decode()
    return (
        "cursor://anysphere.cursor-deeplink/mcp/install?"
        + urllib.parse.urlencode({"name": SERVER_NAME, "config": config})
    )


def cursor_web_link(server: dict) -> str:
    config = base64.b64encode(json.dumps(server, separators=(",", ":")).encode()).decode()
    return "https://cursor.com/en/install-mcp?" + urllib.parse.urlencode(
        {"name": SERVER_NAME, "config": config}
    )


def vscode_link(server: dict) -> str:
    payload = json.dumps({"name": SERVER_NAME, **server}, separators=(",", ":"))
    return "vscode:mcp/install?" + urllib.parse.quote(payload, safe="")


def vscode_cli(server: dict) -> str:
    payload = json.dumps({"name": SERVER_NAME, **server}, separators=(",", ":"))
    return f"code --add-mcp '{payload}'"


def links_block(switch: dict) -> str:
    local = local_server()
    remote_url = switch["remote_url"]
    remote_state = (
        "live" if switch.get("remote_live") else "**not live yet**: these will work once it ships"
    )
    lines = [
        LINKS_START,
        "<!-- Generated by tools/render_configs.py; edit that script, not this block. -->",
        "",
        "**Local server** (`beakr mcp`; needs the beakr CLI installed and signed in):",
        "",
        f"- Cursor: [Add Beakr to Cursor]({cursor_web_link(local)})",
        f"  (desktop deeplink: `{cursor_deeplink(local)}`)",
        f"- VS Code: `{vscode_link({'type': 'stdio', **local})}`",
        f"  or from a terminal: `{vscode_cli({'type': 'stdio', **local})}`",
        f"- Codex: `codex mcp add {SERVER_NAME} -- {LOCAL_COMMAND} {' '.join(LOCAL_ARGS)}`",
        f"- Claude Code: `claude mcp add {SERVER_NAME} -- {LOCAL_COMMAND} {' '.join(LOCAL_ARGS)}`",
        "",
        f"**Hosted server** (`{remote_url}`, OAuth sign-in; {remote_state}):",
        "",
        f"- Cursor: [Add hosted Beakr to Cursor]({cursor_web_link({'url': remote_url})})",
        f"- VS Code: `{vscode_cli({'type': 'http', 'url': remote_url})}`",
        f"- Codex: `codex mcp add {SERVER_NAME} --url {remote_url}` then `codex mcp login {SERVER_NAME}`",
        f"- Claude Code: `claude mcp add --transport http {SERVER_NAME} {remote_url}`, then `/mcp` to sign in",
        f"- Gemini CLI: `gemini mcp add --transport http {SERVER_NAME} {remote_url}`",
        "",
        LINKS_END,
    ]
    return "\n".join(lines)


def render_readme(switch: dict) -> str:
    text = README.read_text()
    start, end = text.find(LINKS_START), text.find(LINKS_END)
    if start == -1 or end == -1:
        sys.exit(f"README.md must contain {LINKS_START} ... {LINKS_END}")
    return text[:start] + links_block(switch) + text[end + len(LINKS_END) :]


# ---------------------------------------------------------------------------


def generated(switch: dict) -> dict[str, str]:
    remote_url = switch["remote_url"]
    return {
        ".mcp.json": dump(claude_plugin_mcp(switch)),
        "mcp.json": dump(agent_plugins_mcp(switch)),
        "gemini-extension.json": dump(gemini_extension(switch)),
        "examples/cursor/mcp.json": dump(cursor_config(None)),
        "examples/cursor/mcp.remote.json": dump(cursor_config(remote_url)),
        "examples/vscode/mcp.json": dump(vscode_config(None)),
        "examples/vscode/mcp.remote.json": dump(vscode_config(remote_url)),
        "examples/codex/config.toml": codex_config(None),
        "examples/codex/config.remote.toml": codex_config(remote_url),
        "README.md": render_readme(switch),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="fail if a generated file is stale")
    args = parser.parse_args()

    switch = load_switch()
    files = generated(switch)
    stale = []
    for rel, content in files.items():
        path = REPO_ROOT / rel
        current = path.read_text() if path.exists() else None
        if current == content:
            continue
        if args.check:
            stale.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            print(f"wrote {rel}")
    if stale:
        print("Generated files are stale (run tools/render_configs.py):", file=sys.stderr)
        for rel in stale:
            print(f"  {rel}", file=sys.stderr)
        return 1
    if args.check:
        print(f"Generated configs are current (variant: {switch['variant']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

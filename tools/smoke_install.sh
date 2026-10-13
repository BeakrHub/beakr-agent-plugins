#!/bin/sh
# Each client runs in a subshell with its own HOME; that is the point.
# shellcheck disable=SC2030,SC2031

# Install this checkout into Claude Code and Codex under a throwaway HOME and
# show what each client loaded. Your real ~/.claude and ~/.codex are never read
# or written.
#
# Usage: tools/smoke_install.sh [claude|codex|all]
#
# The MCP health check needs a working `beakr` CLI; point BEAKR_BIN at one
# (with credentials it can reach from the throwaway HOME, e.g. BEAKR_API_KEY)
# to see "Connected". Without it the server reports the install hint and fails,
# which is the expected no-CLI behaviour.

set -eu

target=${1:-all}
repo=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
scratch=$(mktemp -d "${TMPDIR:-/tmp}/beakr-plugin-smoke.XXXXXX")
echo "Throwaway HOME: $scratch"

smoke_claude() {
    command -v claude >/dev/null || { echo "claude CLI not found; skipping Claude Code"; return; }
    echo "== Claude Code"
    (
        export HOME="$scratch/claude"
        unset CLAUDE_CONFIG_DIR
        mkdir -p "$HOME"
        cd "$HOME"
        claude plugin validate "$repo" --strict
        claude plugin validate "$repo/.claude-plugin/plugin.json" --strict
        claude plugin marketplace add "$repo"
        claude plugin install beakr@beakr
        claude plugin details beakr
        claude mcp list
    )
}

smoke_codex() {
    command -v codex >/dev/null || { echo "codex CLI not found; skipping Codex"; return; }
    echo "== Codex"
    (
        export HOME="$scratch/codex"
        export CODEX_HOME="$HOME/.codex"
        mkdir -p "$CODEX_HOME"
        cd "$HOME"
        codex plugin marketplace add "$repo"
        codex plugin add beakr@beakr
        codex plugin list
        codex mcp list
        echo "Installed skills:"
        find "$CODEX_HOME/plugins/cache/beakr/beakr" -name SKILL.md
    )
}

case "$target" in
    claude) smoke_claude ;;
    codex) smoke_codex ;;
    all) smoke_claude; smoke_codex ;;
    *) echo "usage: $0 [claude|codex|all]" >&2; exit 2 ;;
esac

# Beakr agent plugins

Install Beakr into your coding agent in one step. Beakr is your team's organizational memory: decisions, processes, ownership and dated events. With this plugin your agent can research it with citations, read and write the knowledge base, and start each session knowing what your team knows.

| Client | What you get | Install |
|---|---|---|
| Claude Code | skill, MCP server, slash commands, session hooks | [plugin](#claude-code) |
| Codex | skill, MCP server | [plugin](#codex) |
| Cursor | skill, MCP server | [plugin or one-click MCP](#cursor) |
| VS Code (Copilot) | skill, MCP server | [plugin or MCP config](#vs-code) |
| Gemini CLI | skill, MCP server, context file | [extension](#gemini-cli) |
| Claude.ai, Claude Desktop, ChatGPT | MCP server | [hosted connector](#claudeai-claude-desktop-and-chatgpt) (not live yet) |

## Before you install

Every plugin talks to Beakr through the `beakr` CLI's local MCP server (`beakr mcp`). Install the CLI and sign in once:

```sh
curl -fsSL https://raw.githubusercontent.com/BeakrHub/beakr-cli/main/install.sh | sh
beakr auth login
```

The installer puts `beakr` in `~/.local/bin` via `uv tool install beakr-cli`; `pipx install beakr-cli` works too. Instead of `beakr auth login` you can set `BEAKR_API_KEY` (and `BEAKR_API_URL` for a non-production instance) in the environment your agent starts from. Session hooks need beakr-cli 0.4.0 or later (`beakr update`).

Without the CLI the plugins still install, but the Beakr tools stay unavailable: the MCP server exits with install instructions and the hooks do nothing.

> This repository is private for now. Installing from `BeakrHub/beakr-agent-plugins` needs GitHub access to it (your git credentials or `gh auth login`); see [Publishing](#publishing).

## Claude Code

```text
/plugin marketplace add BeakrHub/beakr-agent-plugins
/plugin install beakr@beakr
```

From a terminal: `claude plugin marketplace add BeakrHub/beakr-agent-plugins && claude plugin install beakr@beakr`. Restart the session, then run `/beakr:setup` to check that everything is connected.

What it installs:

- **The `beakr` skill**: how to search, research, write and audit the knowledge base, and when to propose capturing something durable.
- **The `beakr` MCP server** (`beakr mcp`): `research`, `knowledge_base`, `knowledge_base_write`, `list_projects` and the rest of Beakr's tools, all listed from the start (see [MCP server settings](#mcp-server-settings)).
- **Slash commands**: `/beakr:kb-search`, `/beakr:kb-research`, `/beakr:kb-write`, `/beakr:kb-audit`, and `/beakr:setup`.
- **Session hooks**, the same ones `beakr hooks install` writes into `settings.json`:
  - `SessionStart` runs `beakr context --format claude_md --project auto --hook`, which adds your Beakr context (profile, recent activity, relevant memories and skills) to the session.
  - `Stop` and `SessionEnd` run `beakr compound --hook --client claude-code --background`, which captures the session into Beakr. **Capture only happens in a repository that opted in** with `beakr init --capture` or `beakr hooks capture on`; everywhere else these hooks upload nothing.

  If you already ran `beakr hooks install`, the plugin's hooks stand down so nothing runs twice. To stop capture in a repository, run `beakr hooks capture off` there; to drop the hooks entirely, disable the plugin with `/plugin`.

## Codex

```sh
codex plugin marketplace add BeakrHub/beakr-agent-plugins
codex plugin add beakr@beakr
```

This installs the `beakr` skill and the `beakr` MCP server. Codex plugins get no session hooks here. For Beakr context and capture in Codex, start it through the CLI with `beakr codex` (refreshes a Beakr block in `~/.codex/AGENTS.md` before each session and captures the session afterwards, if the repository allows it).

Without the plugin, register the server by hand: `codex mcp add beakr -- beakr mcp`, or paste [`examples/codex/config.toml`](examples/codex/config.toml) into `~/.codex/config.toml`. Then add [`examples/codex/AGENTS.md`](examples/codex/AGENTS.md) to `~/.codex/AGENTS.md` so Codex knows when to use Beakr.

## Cursor

Plugin (skill and MCP server): in Cursor's **Customize** panel, add a plugin **From GitHub Repository** and enter `BeakrHub/beakr-agent-plugins`.

MCP server only: use the one-click link below, or copy [`examples/cursor/mcp.json`](examples/cursor/mcp.json) into `~/.cursor/mcp.json` (all projects) or `.cursor/mcp.json` (one project).

## VS Code

Plugin (skill and MCP server): add the repository as a plugin marketplace in your user settings, then install `beakr` from the Chat view's plugins list.

```json
"chat.plugins.marketplaces": ["BeakrHub/beakr-agent-plugins"]
```

MCP server only: use the install link or `code --add-mcp` command below, or copy [`examples/vscode/mcp.json`](examples/vscode/mcp.json) into `.vscode/mcp.json`.

## Gemini CLI

```sh
gemini extensions install https://github.com/BeakrHub/beakr-agent-plugins
```

This installs the `beakr` skill, the `beakr` MCP server and a short `GEMINI.md` context file. Gemini CLI does not pass your shell's environment variables to extensions, so sign in with `beakr auth login` rather than relying on `BEAKR_API_KEY`.

## Claude.ai, Claude Desktop and ChatGPT

Claude.ai custom connectors and ChatGPT connectors can only reach a remote MCP server over HTTPS with OAuth; they cannot run `beakr mcp` on your machine. They will work once Beakr's hosted MCP server is live, by adding its URL as a custom connector. Until then, Claude Desktop can use the local server: add the `beakr` entry from [`examples/cursor/mcp.json`](examples/cursor/mcp.json) to `claude_desktop_config.json`, with the full path from `which beakr` as the command.

## One-click links and commands

<!-- generated:install-links:start -->
<!-- Generated by tools/render_configs.py; edit that script, not this block. -->

**Local server** (`beakr mcp`; needs the beakr CLI installed and signed in):

- Cursor: [Add Beakr to Cursor](https://cursor.com/en/install-mcp?name=beakr&config=eyJjb21tYW5kIjoiYmVha3IiLCJhcmdzIjpbIm1jcCJdfQ%3D%3D)
  (desktop deeplink: `cursor://anysphere.cursor-deeplink/mcp/install?name=beakr&config=eyJjb21tYW5kIjoiYmVha3IiLCJhcmdzIjpbIm1jcCJdfQ%3D%3D`)
- VS Code: `vscode:mcp/install?%7B%22name%22%3A%22beakr%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22beakr%22%2C%22args%22%3A%5B%22mcp%22%5D%7D`
  or from a terminal: `code --add-mcp '{"name":"beakr","type":"stdio","command":"beakr","args":["mcp"]}'`
- Codex: `codex mcp add beakr -- beakr mcp`
- Claude Code: `claude mcp add beakr -- beakr mcp`

**Hosted server** (`https://api.thebeakr.com/mcp`, OAuth sign-in; **not live yet**: these will work once it ships):

- Cursor: [Add hosted Beakr to Cursor](https://cursor.com/en/install-mcp?name=beakr&config=eyJ1cmwiOiJodHRwczovL2FwaS50aGViZWFrci5jb20vbWNwIn0%3D)
- VS Code: `code --add-mcp '{"name":"beakr","type":"http","url":"https://api.thebeakr.com/mcp"}'`
- Codex: `codex mcp add beakr --url https://api.thebeakr.com/mcp` then `codex mcp login beakr`
- Claude Code: `claude mcp add --transport http beakr https://api.thebeakr.com/mcp`, then `/mcp` to sign in
- Gemini CLI: `gemini mcp add --transport http beakr https://api.thebeakr.com/mcp`

<!-- generated:install-links:end -->

## MCP server settings

Needs beakr-cli 0.4.0 or later (`beakr update`). Set these in the environment your agent starts from, or in the `env` of the `beakr` MCP entry:

- **Tool listing.** The server lists every Beakr tool, because Claude Code calls only the tools a server lists. `BEAKR_MCP_TOOLS=eager` lists a smaller set plus `discover_tools`, which adds the tools it finds to the listing.
- **Write attribution.** Every Knowledge write the server makes records the agent that made it: the client's own name and version (`claude-code/2.1.283`, `codex-mcp-client/0.40.0`), shown on proposals as "filed by Dana Reyes via claude-code/2.1". When several agents share one API key, give each MCP entry its own `BEAKR_AGENT` label (`"env": {"BEAKR_AGENT": "reviewer"}`); it overrides the client's name.
- **Self-hosted Beakr.** On an installation that leaves out hosted features (integrations, skills, organization administration), the server does not list their tools (`skills` and `org_audit_log`, for example), and `beakr doctor` names the missing areas. When the CLI came with the installation, `beakr_version` says so and `update_beakr` does not run: the installation upgrades it.
- **Update checks.** `BEAKR_NO_UPDATE_CHECK=1` stops the CLI asking PyPI for a newer release; `beakr_version` and `update_beakr` then say update checks are off.

## Local or hosted MCP server

The plugins ship the **local** server (`beakr mcp` over stdio). Beakr's hosted MCP server (streamable HTTP with OAuth, so no CLI needed) is not live in production yet. One switch moves every plugin over when it is:

1. In [`mcp-variant.json`](mcp-variant.json), set `"remote_live": true` (only once `remote_url` serves Beakr in production) and `"variant": "remote"`.
2. Run `tools/render_configs.py`. It rewrites `.mcp.json` (Claude Code), `mcp.json` (Codex, Cursor, VS Code) and `gemini-extension.json`; the examples for both servers are always generated.
3. Bump the version (see [Releasing](#releasing)) and commit.

The hooks keep needing the CLI either way; with the hosted server and no CLI they do nothing.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Beakr tools missing; the MCP server shows as failed (`/mcp` in Claude Code, `codex mcp list`) | The CLI is not installed or not on the agent's PATH. Install it (above). If it lives somewhere unusual, set `BEAKR_BIN` to its full path in the environment your agent starts from. |
| The server connects but tool calls fail with an auth error | Run `beakr auth login`, or check `BEAKR_API_KEY`. `beakr doctor` shows what the CLI can reach. |
| Cursor, VS Code or Claude Desktop launched from the Dock cannot find `beakr` | GUI apps may not inherit your shell's PATH. The plugins' launcher also checks `~/.local/bin`, `/opt/homebrew/bin` and `/usr/local/bin`; for hand-written configs, use the full path from `which beakr` as the command. |
| No Beakr context at session start | Check `beakr doctor`. The context comes from the project bound to the repository (`beakr init`), or your default project. On beakr-cli older than 0.4.0, the session starts with a note asking you to run `beakr update`. |
| Sessions are not captured | Capture is opt-in per repository: `beakr hooks capture status`, then `beakr hooks capture on`. Headless runs (`claude -p`) are captured but never teach personal learning. |
| A captured session is still compounding and should stop | `beakr conversations ls`, then `beakr conversations compound cancel ID`. Proposals it already filed stay; `beakr compound ID` resumes it. |
| `accept_proposal` is refused with `person_review_required` | The organization or project requires a person to accept what agents write. The user accepts it in Beakr; `beakr kb agent-review show -P <project>` says which policy is in force and where it comes from. |
| A `scope` or `project` is refused with `scope_not_found` or `scope_ambiguous` | No single project you can read has that name; the refusal names the closest. Pass the name or id `list_projects` prints. |
| Some files never reach Knowledge | `beakr projects status -P <project>` names the files that failed and `beakr projects retry -P <project>` resends them. `beakr projects refusals <project>` shows, by file, where models refused or fell back. |
| Only a few Beakr tools are listed | `BEAKR_MCP_TOOLS=eager` is set; unset it, or call `discover_tools`. On a self-hosted installation, `beakr doctor` lists the areas it does not provide. |
| `beakr doctor` says MCP "not registered" and hooks "not installed" | Expected: it checks only what `beakr setup` and `beakr hooks install` registered, not what a plugin provides. |
| Context appears twice | You installed the hooks with `beakr hooks install` as well. The plugin stands down when it sees them in `~/.claude/settings.json`; if you keep your settings elsewhere, run `beakr hooks uninstall`. |
| Windows | The launcher and hooks are POSIX shell scripts. On Windows, register the server by hand (`claude mcp add beakr -- beakr mcp`, `codex mcp add beakr -- beakr mcp`) and use `beakr hooks install` for hooks. |

## Repository layout

```text
.claude-plugin/plugin.json        Claude Code plugin manifest
.claude-plugin/marketplace.json   Claude Code marketplace (also read by Codex and VS Code)
.agents/plugins/marketplace.json  Codex marketplace
.cursor-plugin/marketplace.json   Cursor marketplace
plugin.json                       Agent Plugins 1.0 manifest (Codex, Cursor, VS Code)
mcp.json, .mcp.json               MCP server config: Agent Plugins / Claude Code (generated)
gemini-extension.json, GEMINI.md  Gemini CLI extension (manifest generated)
skills/beakr/                     the Beakr skill, copied from beakr-cli (synced, do not edit)
commands/                         Claude Code slash commands (kb-* synced from beakr-cli)
hooks/claude-hooks.json           Claude Code session hooks
scripts/                          MCP launcher, hook runner, CLI finder
examples/                         hand-install configs for Codex, Cursor and VS Code
mcp-variant.json                  local or hosted MCP server switch
tools/                            sync, render, validate and smoke-test scripts
schemas/                          vendored JSON schemas used by CI
```

The repository root is the plugin root, because Gemini CLI installs only whole repositories.

## Maintaining

The skill and the `kb-*` commands come from [beakr-cli](https://github.com/BeakrHub/beakr-cli), which bundles the same skill into the CLI. Never edit them here.

```sh
tools/sync_from_beakr_cli.py --check       # are the copies identical to the pinned beakr-cli commit?
tools/sync_from_beakr_cli.py               # re-copy after changing tools/beakr-cli.ref
tools/render_configs.py --check            # are the generated MCP configs and links current?
uv run --with jsonschema tools/validate.py # manifests against their schemas, plus consistency checks
claude plugin validate . --strict          # Claude Code's own validator
tools/smoke_install.sh                     # install into Claude Code and Codex under a throwaway HOME
```

To take a newer skill: put the beakr-cli commit SHA in `tools/beakr-cli.ref`, run `tools/sync_from_beakr_cli.py`, review the diff and commit both together. CI runs all of the checks above except the smoke install.

### Releasing

The version lives in `plugin.json`, `.claude-plugin/plugin.json`, the three marketplace files and (generated) `gemini-extension.json`; `tools/validate.py` fails if they disagree. Claude Code and Codex only offer users an update when the version changes, so bump it in every place for each release, run `tools/render_configs.py`, and tag the commit `vX.Y.Z`.

### Publishing

Nothing is submitted to any marketplace. To let people install it:

1. Make this repository public (or grant access to the people who should install it). Every install command above reads it from GitHub.
2. Optionally submit to the public directories: the Claude Code plugin directory, OpenAI's Codex plugin directory, Cursor's marketplace and the Gemini CLI extensions gallery. Each has its own review.

## License

Apache-2.0, like beakr-cli.

---
description: "Check that Beakr is ready in this agent: the beakr CLI, sign-in, API and project binding"
---

Check whether the Beakr plugin can work here, then tell the user exactly what, if anything, they still need to do.

1. Find the CLI by running `"${CLAUDE_PLUGIN_ROOT}/scripts/find-beakr"`. It prints the path of the `beakr` binary, or exits 1 when there is none.
   - If there is none, stop and give the user these steps. Do not run them yourself: they install software and open a browser sign-in.
     ```
     curl -fsSL https://raw.githubusercontent.com/BeakrHub/beakr-cli/main/install.sh | sh -s -- --no-auth --no-mcp --no-skills --no-hooks
     beakr auth login
     ```
     Then they restart this session so the Beakr MCP server starts.

2. Run `<that path> doctor --json` and read its checks.
   - `version`, `api` and `auth` must be `ok`. If `version` reports a CLI older than 0.4.0 (often a PyPI install), the user reinstalls it with the install command above; `beakr update` alone does not move a PyPI install to 0.4.0.
   - If `auth` fails, the user runs `beakr auth login`, or sets `BEAKR_API_KEY` in the environment the agent starts from.
   - `project` with `warn` means this directory is not bound to a Beakr project. Say what binding gives them: session context and capture scoped to that project. They bind with `beakr init`.
   - Ignore `mcp` and `hooks` warnings that say "not registered" or "not installed". This plugin provides both, and `beakr doctor` only looks at its own `beakr setup` and `beakr hooks install` registrations.
   - On a self-hosted installation, `beakr doctor` lists the areas it does not provide (for example integrations, skills or organization administration). Their tools, such as `skills` and `org_audit_log`, are not listed; that is expected, not a fault.

3. Check whether the Beakr MCP tools (`research`, `knowledge_base`, `knowledge_base_write`, `show_proposal`, `list_projects`) are available in this session. The server lists every tool, so if only a few appear with `discover_tools`, `BEAKR_MCP_TOOLS=eager` is set in the environment; that is the user's choice. If the CLI is fine but the tools are missing, the session started before the CLI was installed or signed in; the user restarts the session or runs `/mcp` to reconnect `beakr`.

Report in a few lines: what works, and the single next step if something does not.

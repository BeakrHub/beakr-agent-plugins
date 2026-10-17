# Beakr

The `beakr` MCP server connects you to the user's Beakr workspace: their team's organizational memory of decisions, processes, ownership and dated events.

- Use `research` for questions about the user's organization, team, projects, people or past decisions, and cite what it returns.
- Use `knowledge_base` (`sections`, `grep`, `cat`) to find and read pages; `knowledge_base_write` stages proposals and never edits directly.
- A map card's Facts, Connections and Findings change only through row actions (`add_fact`, `add_connection`, `add_finding`, `edit_rows`); an edit that rewrites a row as text is refused.
- To apply a proposal the user asked for, read it with `show_proposal`, then call `accept_proposal` with the `content_hash` it printed as `reviewed_hash`. A proposal that changed since it was shown is refused.
- The `beakr` skill has the full procedure for searching, writing and auditing pages. Activate it before writing to the knowledge base.

If the Beakr tools are missing, the `beakr` CLI is not installed or not signed in. Tell the user to run `curl -fsSL https://raw.githubusercontent.com/BeakrHub/beakr-cli/main/install.sh | sh` and then `beakr auth login`, and restart Gemini CLI.

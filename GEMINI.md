# Beakr

The `beakr` MCP server connects you to the user's Beakr workspace: their team's organizational memory of decisions, processes, ownership and dated events.

- Use `research` for questions about the user's organization, team, projects, people or past decisions, and cite what it returns.
- Use `knowledge_base` (`sections`, `grep`, `cat`) to find and read pages; `knowledge_base_write` stages proposals; only `sort_table` and a project or org `page_type` the verifier accepts apply at once, and a global `page_type` is refused.
- Read four ways, combined as the task needs: the file system (`ls`, `cat`, `grep`), the graph (`links`, `hover`, `timeline`), the database (`rows`: every map card's Facts, Connections and Findings as one table, for every, how many, latest, largest and as-of questions; `match` sets how a field name is found: `exact`, `similar` or `meaning`) and meaning (`sections`). An empty `rows` result is not proof a fact is absent.
- A map card's Facts, Connections and Findings change only through row actions (`add_fact`, `add_connection`, `add_finding`, `edit_rows`); an edit that rewrites a row as text is refused, and `find_replace` skips the rows and says which it left. Give a row's `evidence` as the readable reference a read printed (`memo.pdf › p. 7`).
- A write to one section or row prints its proposal id and `content_hash`. To apply a proposal the user asked for, show it with `show_proposal` (it names who filed it), then call `accept_proposal` with that `content_hash` as `reviewed_hash`. A proposal that changed since it was shown is refused. One that needs a person to accept is refused to agents (`person_review_required`): ask the user to accept it in Beakr.
- Pass `scope` on `knowledge_base` and `knowledge_base_write` as a project name or id from `list_projects` to work in one project. One that names no project you can read is refused with the closest names (`scope_not_found`), never widened to everything. `research`, `read_file`, `documents`, `wiki_stats` and `wiki_graph` take `project`: pass the project id to work on every Beakr server (the local `beakr mcp` server also accepts a name).
- Every Beakr tool is listed from the start; call the one you need directly.
- The `beakr` skill has the full procedure for searching, writing and auditing pages. Activate it before writing to the knowledge base.

If the Beakr tools are missing, the `beakr` CLI is not installed or not signed in. Tell the user to run `curl -fsSL https://raw.githubusercontent.com/BeakrHub/beakr-cli/main/install.sh | sh` and then `beakr auth login`, and restart Gemini CLI.

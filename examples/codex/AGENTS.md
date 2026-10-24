<!-- Beakr: paste into ~/.codex/AGENTS.md (all projects) or a repository's AGENTS.md.
     Only needed when you register the MCP server by hand instead of installing the
     Codex plugin, which ships the full Beakr skill. -->
## Beakr

The `beakr` MCP server is this team's organizational memory: decisions, processes, ownership and dated events.

- Before non-trivial work, and whenever the user asks about the organization, its people, projects or past decisions, call `research` or `knowledge_base` (`sections`, then `cat`) and cite what you use.
- When the session produces something durable (a decision and its rationale, a process, an owner, a dated event), check it is not already captured with `knowledge_base` `sections`, then offer to propose it with `knowledge_base_write`. Writes are proposals (only a table sort, or a project or org page type the verifier accepts, applies at once; a global page type is refused); never claim a page changed until the proposal is accepted. A map card's Facts, Connections and Findings change only through row actions (`add_fact`, `add_connection`, `add_finding`, `edit_rows`). Cite a source Beakr already has by the readable reference a read printed (`memo.pdf › p. 7`), not a raw `{{...}}` key.
- Accept a proposal only when the user asks: show it with `show_proposal`, then pass the `content_hash` the write or `show_proposal` printed to `accept_proposal` as `reviewed_hash`. A proposal that changed since it was shown is refused, and one that needs a person (`person_review_required`) is the user's to accept in Beakr.
- Skip transient state, debugging traces and anything already in the code or git history.

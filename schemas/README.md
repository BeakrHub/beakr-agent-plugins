# Vendored JSON schemas

`tools/validate.py` validates the manifests against these copies, so CI does not depend on the network and a schema change upstream cannot silently change what passes. Refresh a copy by downloading it again from its source and committing the diff.

| File | Source | Validates |
|---|---|---|
| `agent-plugins-1.0.0-plugin.schema.json` | https://agent-plugins.org/schemas/1.0.0/plugin.schema.json | `plugin.json` |
| `agent-plugins-1.0.0-mcp.schema.json` | https://agent-plugins.org/schemas/1.0.0/mcp.schema.json | `mcp.json` |
| `claude-code-plugin-manifest.json` | https://www.schemastore.org/claude-code-plugin-manifest.json (community-maintained) | `.claude-plugin/plugin.json` |
| `claude-code-marketplace.json` | https://www.schemastore.org/claude-code-marketplace.json (community-maintained) | `.claude-plugin/marketplace.json` |

Downloaded 2026-10-12. Codex's marketplace, Cursor's marketplace and Gemini CLI's extension manifest have no published schema; `tools/validate.py` checks their structure directly. Claude Code's own validator (`claude plugin validate --strict`) runs in CI as well.

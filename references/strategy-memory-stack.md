# Memory stack map (ai-memory + mnemosyne)

Facts verified via repo docs and local inspection. Paths may move — re-check with `ls` before citing.

## Local checkouts

| Item | Path | Facts |
|---|---|---|
| ai-memory | `/Users/kereru/Development/ai-memory` | akitaonrails/ai-memory checkout, Cargo workspace 2.4.x, MIT. Rust single binary: server (default `127.0.0.1:49374`) + thin CLI + MCP (17 tools) + lifecycle hooks. macOS menu bar app exists; Docker/AUR/native builds documented. |
| mnemosyne | `/Users/kereru/development/mnemosyne` | tipsy-kereru/mnemosyne (user's OWN project), Python pkg `mnemosyne-kg` v0.11.x. SQLite knowledge graph (sqlite3+NetworkX) + Markdown wiki + MCP server (15+ tools) + PostToolUse hooks (git/claude/codex/gemini/copilot). Binary at `~/.local/bin/mnemosyne`. NOT the mnemosyne-oss memory layer. Team comparison doc: `docs/AI_MEMORY_COMPARISON.ko.md`. |

## ai-memory wiring (per agent)

```bash
# server first; per-agent registration is two commands each
ai-memory install-mcp   --client <client> --apply
ai-memory install-hooks --agent <agent> --apply
```

- Existing project adoption: run `ai-memory bootstrap` once; then `ai-memory install-instructions` (writes routing snippet + managed Agent Skills into AGENTS.md/CLAUDE.md — gives agents tool-routing knowledge).
- **Codex and Antigravity (`agy`) have no true session-end hook:** run `ai-memory finalize-session` (optionally `--agent antigravity-cli`) after the final turn or no handoff is created.
- **OMP (oh-my-pi)** is fully supported (MCP + generated TS plugin; SessionStart handoff injection works); also `ai-memory run omp`.
- **Orca-ide is NOT in the support matrix.** Orca drives agents as terminals, so wire the inner agent binaries instead — they read user-level hook/MCP config. Orca tab command wrapper for managed workstreams: `orca terminal create ... --command "ai-memory run codex --yolo"` (auto-installs hooks/MCP first run).
- Grok CLI / Zero discard SessionStart stdout — agents must call `memory_handoff_accept` to receive handoffs.
- Concurrent same-user sessions: server `[auto_scope] mode = "per_session"` + `install-mcp --session-aware` (Claude Code only has the bridge).
- Secrets: per-repo `[capture]` rules exclude paths or invert to allowlist; DATA_HANDLING.md documents the data flow.
- Orca + ai-memory hook coexistence: ai-memory's installer preserves third-party hook entries; still verify both after install.

## mnemosyne wiring (per agent)

```bash
mnemosyne add . --domain coding        # seed graph+wiki from codebase
mnemosyne config hook install codex    # PostToolUse auto-sync of edits
mnemosyne config skill install --target agents   # ~/.agents/skills/
mnemosyne mcp serve                    # MCP server (also `mcp install --client hermes`)
mnemosyne query --stats / wiki doctor  # health
```

- Codex gets hook-only sync; querying from Codex goes through the `mnemosyne` CLI or MCP.
- Slack ingest is deliberately isolated (`slack_*` tables, `mnemosyne-slack` CLI only) — never expose it through the general graph or MCP.

## Role boundary (from the team comparison doc — do not re-derive)

- ai-memory: wiki page / observation / session / handoff. Session continuity, cross-agent handoff, claim-once CAS. Wiki markdown is source of truth for PAGES only — sessions/handoffs/users need DB backup, not just wiki git.
- mnemosyne: entity / relation / scope / entity-history. Coding/daily/legal domains, Tree-sitter deterministic extraction (zero-LLM), LLM extraction via `add` (needs provider or CLI fallback), generated wiki from graph.
- Port direction if integrating products: bring ai-memory's sanitizer contract, typed handoff CAS, no-LLM session summary, bounded startup brief, retrieval eval into mnemosyne. Do NOT port managed-workstreams launcher or full Rust rewrite (explicitly deferred in the team doc).

# Changes in v0.9.x (from v0.8.10)

## Major Changes

### Package Name

The npm package is now `@agentmemory/agentmemory` (scoped under `@agentmemory`). The standalone MCP server is `@agentmemory/mcp`.

### iii-engine Rebrand

The runtime engine was rebranded from its previous name to [iii-engine](https://iii.dev). Installation and documentation references updated accordingly.

### Tool Count Increase

MCP tools increased from 43 to 51. New tools include facet tagging, verification, and enhanced diagnostic capabilities.

## v0.9.4 (2026-04-29) — Bug-fix patch

- **Fixed:** `mem::graph-extract` now auto-fires at session end when `GRAPH_EXTRACTION_ENABLED=true`. Previously the function was registered but never internally invoked — graph stayed empty unless manually called via REST.
- **Added:** `agentmemory doctor` detects Claude Code plugin-hook load state by scanning `~/.claude/debug/latest`.

## v0.9.3 (2026-04-24) — Developer-experience patch

- **Added:** `agentmemory doctor` command — runs 10 diagnostic checks (server reachability, health, viewer port, LLM/embedding providers, feature flags, graph data).
- **Added:** `/agentmemory/config/flags` REST endpoint for introspecting feature flag states.
- **Added:** Viewer feature-flag banner system with collapsible summary and per-flag cards.
- **Added:** Viewer first-run hero card pointing at `demo` command.
- **Added:** Viewer footer with preset GitHub issue report link (pre-filled with version, provider, flags).
- **Added:** Richer empty states on Actions, Memories, Lessons, Crystals tabs.
- **Added:** `status` command shows flag state.
- **Added:** `AGENTMEMORY_URL` environment variable honored by CLI.
- **Changed:** REST feature-not-enabled errors return structured bodies with fix guidance.

## v0.9.2 (2026-04-22) — Safety + import-pipeline patch

- **Security:** Fixed Stop-hook recursion loop that could drain Claude Pro subscriptions on unkeyed installs. Five-layer defense-in-depth fix.
- **Security:** `detectProvider()` default is now `noop` (no LLM calls). Claude subscription fallback requires explicit `AGENTMEMORY_ALLOW_AGENT_SDK=true`.
- **Added:** `OPENAI_BASE_URL`, `OPENAI_EMBEDDING_MODEL`, `OPENAI_EMBEDDING_DIMENSIONS` for OpenAI-compatible embedding providers.
- **Added:** Auto-derived lessons and crystals on `import-jsonl`.
- **Added:** Session preview on sessions list (firstPrompt field).
- **Changed:** `import-jsonl` runs synthetic compression + BM25 indexing (was writing raw to KV only).
- **Fixed:** Viewer WebSocket connect timeout (5s force-close).
- **Fixed:** Various viewer rendering bugs (strength gauge, audit response shape, replay path).

## v0.9.1 (2026-04-21) — Trust-the-CLI patch

- Fixed dashboard viewer showing zeros for half its cards
- Fixed `import-jsonl` command issues
- Various CLI reliability improvements

## v0.9.0 (2026-04-18) — Major release

- Landing site at [agent-memory.dev](https://agent-memory.dev)
- Filesystem connector (`@agentmemory/fs-watcher`)
- Standalone MCP now proxies to running server
- Audit policy codified across every delete path
- Health stops flagging `memory_critical` on tiny Node processes
- Session replay with timeline scrubbing
- Claude Code plugin with 12 hooks + 4 skills

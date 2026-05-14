# Memory Pipeline & Architecture

## The Capture Phase

agentmemory captures agent activity through 12 hooks that fire on specific lifecycle events. Each hook reads JSON from stdin, makes HTTP calls to the REST API, and exits. All use `try/catch` with `AbortSignal.timeout()` for best-effort delivery.

**Hook types and what they capture:**

- **SessionStart** — Project path, session ID
- **UserPromptSubmit** — User prompts (privacy-filtered)
- **PreToolUse** — File access patterns + enriched context
- **PostToolUse** — Tool name, input, output
- **PostToolUseFailure** — Error context
- **PreCompact** — Re-injects memory before compaction
- **SubagentStart/Stop** — Sub-agent lifecycle
- **Stop** — End-of-session summary
- **SessionEnd** — Session complete marker
- **Notification** — Agent notifications
- **TaskCompleted** — Completed task results

### Deduplication

Every observation passes through SHA-256 deduplication with a 5-minute window. The `DedupMap` class tracks content fingerprints so identical tool uses within the window are collapsed into a single observation.

### Privacy Filtering

Before any observation is stored, the privacy filter strips sensitive data using regex patterns covering:

- API keys (various formats)
- Bearer tokens
- OpenAI project keys (`sk-proj-*`)
- GitHub fine-grained service tokens (`ghs_`, `ghu_`)
- Content marked with `<private>` tags

## The Compression Phase

Since v0.8.8, compression is opt-in via `AGENTMEMORY_AUTO_COMPRESS`. Two modes exist:

### Synthetic Compression (default, zero-token)

The `buildSyntheticCompression()` helper derives structured data from raw tool I/O without any LLM call:

- Maps tool names to `ObservationType` via camelCase-aware substring matching (`Read` → `file_read`, `Write` → `file_write`, `Bash` → `command_run`, etc.)
- Extracts file paths from `tool_input.file_path`, `pattern`, and similar fields
- Truncates narratives to 400 characters to prevent single large outputs from bloating the BM25 index
- Sets `post_tool_failure` hook type to `"error"` observation type

### LLM-Powered Compression (opt-in)

When `AGENTMEMORY_AUTO_COMPRESS=true`, every PostToolUse observation is sent to the configured LLM provider for compression. This produces richer summaries with extracted facts, concepts, and narrative — but consumes API tokens proportional to session tool-use frequency (50-200 tool calls/hour on active sessions).

## The Indexing Phase

Three independent indexes are maintained:

### BM25 Keyword Index

Stemmed keyword matching with synonym expansion. Always active regardless of embedding configuration. Provides the baseline search capability when no embedding provider is configured.

### Vector Index

Dense embeddings stored in-memory via iii-engine's StateModule. Supports cosine similarity search. Available providers (see [Configuration & Providers](reference/04-configuration.md) for details):

- **Local** — `all-MiniLM-L6-v2` via `@xenova/transformers` (free, offline)
- **Gemini** — `text-embedding-004` (free tier, 1500 RPM)
- **OpenAI** — `text-embedding-3-small` ($0.02/1M tokens)
- **Voyage AI** — `voyage-code-3` (paid, optimized for code)
- **Cohere** — `embed-english-v3.0` (free trial)
- **OpenRouter** — Any model (multi-model proxy)

Local embeddings add ~8 percentage points recall over BM25-only mode.

### Knowledge Graph

Entity extraction + BFS traversal. Enabled via `GRAPH_EXTRACTION_ENABLED=true`. Extracts entities from observations and builds a relationship graph for semantic connections between concepts, files, and decisions.

## The Retrieval Phase

Triple-stream retrieval combining three signals with Reciprocal Rank Fusion (RRF, k=60):

1. **BM25** — Stemmed keyword matching (always on)
2. **Vector** — Cosine similarity over dense embeddings (when embedding provider configured)
3. **Graph** — Knowledge graph traversal via entity matching (when entities detected in query)

Results are session-diversified (max 3 results per session) and constrained by token budget (default: 2000 tokens).

## System Architecture

Built on iii-engine's three primitives — no Express, no Postgres, no Redis:

| Traditional stack | agentmemory uses |
|---|---|
| Express.js / Fastify | iii HTTP Triggers |
| SQLite / Postgres + pgvector | iii KV State + in-memory vector index |
| SSE / Socket.io | iii Streams (WebSocket) |
| pm2 / systemd | iii-engine worker management |
| Prometheus / Grafana | iii OTEL + health monitor |

### Key Components

- **Engine**: iii-sdk connects via WebSocket to iii-engine on port 49134
- **State**: File-based SQLite via iii-engine's StateModule (`./data/state_store.db`)
- **Build**: TypeScript → ESM via tsdown, output to `dist/`
- **Test**: vitest (715 tests as of v0.8.9)

### iii-engine Workers

The engine runs multiple workers:

- **HTTP** — REST API endpoints
- **Queue** — Background job processing
- **Cron** — Scheduled tasks (consolidation, eviction)
- **Stream** — WebSocket real-time updates
- **State** — KV state persistence
- **PubSub** — Event broadcasting
- **Exec** — External command execution
- **Bridge** — Cross-worker communication
- **Worker Manager** — Worker lifecycle management

## Data Directory

All data stored in `~/.agentmemory/`:

- State database: `./data/state_store.db`
- Environment config: `./.env`
- Standalone MCP data: `./standalone.json`
- Export root (Obsidian, etc.): configurable via `AGENTMEMORY_EXPORT_ROOT`

# Configuration and Providers

## LLM Providers

agentmemory auto-detects the LLM provider from environment variables. Detection order:

1. **MiniMax** — `MINIMAX_API_KEY` (Anthropic-compatible API, model: `MiniMax-M2.7`)
2. **Anthropic** — `ANTHROPIC_API_KEY` (model: `claude-sonnet-4-20250514`)
3. **Gemini** — `GEMINI_API_KEY` (model: `gemini-2.0-flash`, routed through OpenAI-compatible endpoint)
4. **OpenRouter** — `OPENROUTER_API_KEY` (model: `anthropic/claude-sonnet-4-20250514`)
5. **Claude Agent SDK** (default) — uses Claude subscription, no API key needed

Provider-specific model overrides:

```env
ANTHROPIC_MODEL=claude-sonnet-4-20250514
GEMINI_MODEL=gemini-2.0-flash
OPENROUTER_MODEL=anthropic/claude-sonnet-4-20250514
MINIMAX_MODEL=MiniMax-M2.7
ANTHROPIC_BASE_URL=https://custom.endpoint.com  # proxy support
MAX_TOKENS=4096
```

### Fallback Chain

Configure multiple providers for resilience:

```env
FALLBACK_PROVIDERS=anthropic,gemini,openrouter
```

Providers are tried in order. Circuit breaker with half-open state prevents cascading failures.

## Embedding Providers

Auto-detected from environment variables (first match wins):

| Env Var | Provider | Model | Dimensions |
|---------|----------|-------|------------|
| `EMBEDDING_PROVIDER=local` | Local (@xenova/transformers) | all-MiniLM-L6-v2 | 384 |
| `GEMINI_API_KEY` | Gemini | text-embedding-004 | 768 |
| `OPENAI_API_KEY` | OpenAI | text-embedding-3-small | 1536 |
| `VOYAGE_API_KEY` | Voyage AI | voyage-code-3 | varies |
| `COHERE_API_KEY` | Cohere | embed-english-v3.0 | 1024 |
| `OPENROUTER_API_KEY` | OpenRouter | any model | varies |

## Environment Variables

Configuration file: `~/.agentmemory/.env`

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `III_ENGINE_URL` | `ws://localhost:49134` | iii-engine WebSocket URL |
| `III_REST_PORT` | `3111` | REST API port |
| `III_STREAMS_PORT` | `3112` | WebSocket streams port |
| `TOKEN_BUDGET` | `2000` | Max tokens for context injection |
| `MAX_OBS_PER_SESSION` | `500` | Maximum observations per session |

### Search Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `BM25_WEIGHT` | `0.4` | BM25 weight in RRF fusion |
| `VECTOR_WEIGHT` | `0.6` | Vector weight in RRF fusion |

### Feature Flags

All OFF by default in v0.8.10:

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENTMEMORY_AUTO_COMPRESS` | `false` | LLM compression per observation (opt-in, token-costly) |
| `AGENTMEMORY_INJECT_CONTEXT` | `false` | Context injection into conversation (opt-in, token-costly) |
| `GRAPH_EXTRACTION_ENABLED` | `false` | Knowledge graph entity extraction |
| `CONSOLIDATION_ENABLED` | `true` | 4-tier consolidation pipeline |
| `LESSON_DECAY_ENABLED` | — | Ebbinghaus decay for lessons |
| `CLAUDE_MEMORY_BRIDGE` | `false` | Bi-directional sync with Claude Code MEMORY.md |
| `SNAPSHOT_ENABLED` | `false` | Git-versioned memory snapshots |
| `OBSIDIAN_AUTO_EXPORT` | `false` | Auto-export to Obsidian vault |

### Consolidation

| Variable | Default | Description |
|----------|---------|-------------|
| `CONSOLIDATION_DECAY_DAYS` | `30` | Days before strength decay applies |
| `GRAPH_EXTRACTION_BATCH_SIZE` | `10` | Observations per graph extraction batch |

### Team Memory

| Variable | Required | Description |
|----------|----------|-------------|
| `TEAM_ID` | Yes | Team namespace identifier |
| `USER_ID` | Yes | User identifier within team |
| `TEAM_MODE` | `private` | `shared` or `private` |

### Snapshots

| Variable | Default | Description |
|----------|---------|-------------|
| `SNAPSHOT_INTERVAL` | `3600` | Snapshot interval in seconds |
| `SNAPSHOT_DIR` | `~/.agentmemory/snapshots` | Snapshot storage directory |

### Claude Bridge

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAUDE_PROJECT_PATH` | — | Project path for MEMORY.md sync |
| `CLAUDE_MEMORY_LINE_BUDGET` | `200` | Max lines in synced MEMORY.md |

### Standalone MCP

| Variable | Default | Description |
|----------|---------|-------------|
| `STANDALONE_MCP` | `false` | Enable standalone MCP mode |
| `STANDALONE_PERSIST_PATH` | `~/.agentmemory/standalone.json` | Persistence file for standalone mode |

### Tool Visibility

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENTMEMORY_TOOLS` | `core` | `core` (7 tools) or `all` (43 tools) |

## Data Directory

All persistent data stored under `~/.agentmemory/`:
- `.env` — environment configuration
- `standalone.json` — standalone MCP persistence
- `snapshots/` — git-versioned snapshots (when enabled)

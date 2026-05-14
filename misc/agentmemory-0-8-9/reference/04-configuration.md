# Configuration & Providers

## LLM Providers

agentmemory auto-detects the LLM provider from your environment. No API key is needed if you have a Claude subscription (uses `@anthropic-ai/claude-agent-sdk`).

**Supported providers:**

- **Claude subscription** (default) — Uses `@anthropic-ai/claude-agent-sdk`, no config needed
- **Anthropic API** — Set `ANTHROPIC_API_KEY`, per-token billing
- **MiniMax** — Set `MINIMAX_API_KEY`, Anthropic-compatible endpoint
- **Gemini** — Set `GEMINI_API_KEY`, also enables Gemini embeddings
- **OpenRouter** — Set `OPENROUTER_API_KEY`, supports any model

Provider configuration is loaded via `loadConfig()` which reads from environment variables and iii-engine config. The `ProviderType` union includes: `"agent-sdk" | "anthropic" | "gemini" | "openrouter" | "minimax"`.

## Embedding Providers

Embeddings power the vector search stream. agentmemory auto-detects your provider based on available API keys, with local fallback.

**Supported embedding providers:**

- **Local (recommended)** — `all-MiniLM-L6-v2` via `@xenova/transformers`. Free, offline, no API key. Adds ~8 percentage points recall over BM25-only. Install: `npm install @xenova/transformers`
- **Gemini** — `text-embedding-004`. Free tier, 1500 RPM limit
- **OpenAI** — `text-embedding-3-small`. $0.02 per 1M tokens, highest quality
- **Voyage AI** — `voyage-code-3`. Paid, optimized for code embeddings
- **Cohere** — `embed-english-v3.0`. Free trial available
- **OpenRouter** — Any embedding model. Multi-model proxy

Override auto-detection with `EMBEDDING_PROVIDER=local` (or the provider name).

## Environment Variables

Configuration file: `~/.agentmemory/.env`

### LLM & Embedding

```env
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
OPENROUTER_API_KEY=...
MINIMAX_API_KEY=...
EMBEDDING_PROVIDER=local
VOYAGE_API_KEY=...
```

### Search Tuning

```env
BM25_WEIGHT=0.4          # BM25 signal weight in RRF fusion
VECTOR_WEIGHT=0.6        # Vector similarity weight
TOKEN_BUDGET=2000        # Max tokens for context injection per session
```

### Security

```env
AGENTMEMORY_SECRET=your-secret   # Bearer token for protected endpoints
```

When set, all endpoints except `/health` require `Authorization: Bearer <secret>`. Mesh sync requires the secret on both peers.

### Ports

```env
III_REST_PORT=3111       # REST API port (default)
```

Viewer always runs on port 3113. Streams on port 3112.

### Feature Flags

```env
AGENTMEMORY_AUTO_COMPRESS=false   # OFF by default since v0.8.8 (#138)
GRAPH_EXTRACTION_ENABLED=false    # Knowledge graph entity extraction
CONSOLIDATION_ENABLED=true        # 4-tier memory consolidation
LESSON_DECAY_ENABLED=true         # Ebbinghaus forgetting curve decay
OBSIDIAN_AUTO_EXPORT=false        # Auto-export to Obsidian vault
SNAPSHOT_ENABLED=false            # Git-versioned memory snapshots
CLAUDE_MEMORY_BRIDGE=false        # Bi-directional sync with MEMORY.md
```

### Export Configuration

```env
AGENTMEMORY_EXPORT_ROOT=~/.agentmemory   # Root directory for exports
```

Since v0.8.2, exports are confined to this root via `path.resolve` + `startsWith` containment check (path traversal fix).

### Team Memory

```env
TEAM_ID=your-team-id
USER_ID=your-user-id
TEAM_MODE=private    # or "shared"
```

### Tool Visibility

```env
AGENTMEMORY_TOOLS=core   # "core" = 7 tools, "all" = 43 tools
```

## iii-engine Configuration

agentmemory ships two config files:

- **iii-config.yaml** — Local development, binds to `127.0.0.1`
- **iii-config.docker.yaml** — Docker deployment, host port mapping restricted to `127.0.0.1:port`

The engine URL defaults to WebSocket on port 49134. Configuration is loaded via `loadConfig()` in `src/config.ts`.

## Fallback Provider Chain

When a primary provider fails, agentmemory uses circuit breaker pattern with fallback chain. The `createFallbackProvider()` function chains multiple providers so that if one fails, the next is tried automatically. Health monitoring (`registerHealthMonitor`) tracks connection state and triggers alerts.

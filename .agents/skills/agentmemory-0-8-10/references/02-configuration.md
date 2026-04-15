# agentmemory Configuration Guide

## Environment Variables

Configuration is stored in `~/.agentmemory/.env` or passed as environment variables at runtime.

### Core Settings

```bash
# iii-engine connection
III_ENGINE_URL=ws://localhost:49134
III_REST_PORT=3111
III_STREAMS_PORT=3112

# Data directory (default: ~/.agentmemory)
# AGENTMEMORY_DATA_DIR=/custom/path

# Security
AGENTMEMORY_SECRET=your-secret-key-here
```

### LLM Provider Configuration

agentmemory supports multiple LLM backends for compression and summarization.

**Anthropic (Claude):**
```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_BASE_URL=https://api.anthropic.com  # Optional override
```

**Google Gemini:**
```bash
GEMINI_API_KEY=ai-...
GEMINI_MODEL=gemini-2.0-flash
```

**OpenRouter (multiple providers via one API):**
```bash
OPENROUTER_API_KEY=or-...
OPENROUTER_MODEL=anthropic/claude-sonnet-4-20250514
```

**MiniMax (Anthropic-compatible API):**
```bash
MINIMAX_API_KEY=...
MINIMAX_MODEL=MiniMax-M2.7
```

**Agent SDK (default, for Claude Code integration):**
```bash
# No env vars needed - uses Claude Code's built-in SDK
# Model configured via Claude Code settings
```

**Model selection priority:**
1. `MINIMAX_API_KEY` → MiniMax
2. `ANTHROPIC_API_KEY` → Anthropic
3. `GEMINI_API_KEY` → Gemini
4. `OPENROUTER_API_KEY` → OpenRouter
5. Default → Agent SDK

### Embedding Provider Configuration

Embeddings enable semantic search. If not configured, falls back to BM25-only mode.

**Local (no API key):**
```bash
EMBEDDING_PROVIDER=local
# Uses @xenova/transformers with all-MiniLM-L6-v2
# Requires: npm install @xenova/transformers
```

**OpenAI:**
```bash
OPENAI_API_KEY=sk-...
EMBEDDING_PROVIDER=openai
# Model: text-embedding-3-small (default)
```

**Gemini:**
```bash
GEMINI_API_KEY=ai-...
EMBEDDING_PROVIDER=gemini
# Model: gemini-embedding-exp-03-07
```

**Voyage AI:**
```bash
VOYAGE_API_KEY=voy-...
EMBEDDING_PROVIDER=voyage
# Model: voyage-3
```

**Cohere:**
```bash
COHERE_API_KEY=co-...
EMBEDDING_PROVIDER=cohere
# Model: embed-english-v3.0
```

**OpenRouter:**
```bash
OPENROUTER_API_KEY=or-...
EMBEDDING_PROVIDER=openrouter
# Model: mixedbread-ai/mxbai-embed-large-v1
```

**Detection priority:** If `EMBEDDING_PROVIDER` not set, auto-detects from available API keys in order: Gemini → OpenAI → Voyage → Cohere → OpenRouter.

### Search Weights

Tune hybrid search scoring:

```bash
# BM25 (keyword) weight: 0.0-1.0, default 0.4
BM25_WEIGHT=0.4

# Vector (semantic) weight: 0.0-1.0, default 0.6
VECTOR_WEIGHT=0.6

# Graph weight is derived: 1.0 - BM25_WEIGHT - VECTOR_WEIGHT
# Example: BM25=0.4, Vector=0.35 → Graph=0.25
```

**Recommended configurations:**

| Use Case | BM25 | Vector | Graph | Rationale |
|----------|------|--------|-------|-----------|
| Code search | 0.5 | 0.3 | 0.2 | Exact matches important |
| Conceptual search | 0.3 | 0.5 | 0.2 | Semantic similarity key |
| Graph-heavy | 0.3 | 0.25 | 0.45 | Relations matter most |
| BM25-only fallback | 1.0 | 0.0 | 0.0 | No embedding provider |

### Token Budget

Control context injection size:

```bash
# Maximum tokens for context injection (default: 2000)
TOKEN_BUDGET=2000

# Maximum observations per session (default: 500)
MAX_OBS_PER_SESSION=500

# Maximum tokens for LLM compression (default: 4096)
MAX_TOKENS=4096
```

### Claude Code Bridge

Sync with Claude Code's native MEMORY.md:

```bash
# Enable Claude memory bridge
CLAUDE_MEMORY_BRIDGE=true

# Claude project path (required for bridge)
CLAUDE_PROJECT_PATH=/home/user/my-project

# Line budget for MEMORY.md injection (default: 200)
CLAUDE_MEMORY_LINE_BUDGET=200
```

**Bridge behavior:**
- `direction=read`: Import from Claude's MEMORY.md into agentmemory
- `direction=write`: Export agentmemory summaries to MEMORY.md
- Auto-sync at session start/end when enabled

### MCP Tool Visibility

Control which tools are visible to MCP clients:

```bash
# Show only core tools (default)
AGENTMEMORY_TOOLS=core
# Visible: memory_recall, memory_save, memory_file_history, memory_patterns, memory_sessions, memory_smart_search, memory_timeline, memory_profile, memory_export, memory_relations

# Show all 43 tools
AGENTMEMORY_TOOLS=all
```

**Core tools (always visible):**
- `memory_recall` — Search past observations
- `memory_save` — Save explicit memories
- `memory_file_history` — File-specific history
- `memory_patterns` — Pattern detection
- `memory_sessions` — Session listing
- `memory_smart_search` — Hybrid search
- `memory_timeline` — Chronological view
- `memory_profile` — Project profiling
- `memory_export` — Data export
- `memory_relations` — Graph query

### Team Collaboration

```bash
# Team ID for shared memories
TEAM_ID=my-team

# User ID within team
USER_ID=alice

# Enable team features
TEAM_ENABLED=true
```

### Advanced Settings

```bash
# Compression model (defaults to provider model)
COMPRESSION_MODEL=claude-sonnet-4-20250514

# Auto-compression enabled (default: true)
AUTO_COMPRESS=true

# Auto-consolidation enabled (default: true)
AUTO_CONSOLIDATE=true

# Context injection enabled (default: true)
CONTEXT_INJECTION=true

# Graph extraction enabled (default: true)
GRAPH_EXTRACTION=true

# Knowledge graph confidence threshold (default: 0.5)
GRAPH_CONFIDENCE_THRESHOLD=0.5

# Retention score decay rate (default: 0.95 per day)
RETENTION_DECAY_RATE=0.95

# Minimum retention score before auto-forget (default: 0.1)
MIN_RETENTION_SCORE=0.1
```

## Configuration Files

### iii-config.yaml

Engine configuration (copied to `dist/` during build):

```yaml
engine:
  wsPort: 49134
  restPort: 3111
  streamsPort: 3112

worker:
  name: agentmemory
  reconnectDelayMs: 1000
  maxReconnectAttempts: 10

state:
  adapter: sqlite
  path: ~/.agentmemory/state_store.db

telemetry:
  enabled: true
  serviceName: agentmemory
  serviceVersion: 0.8.10
  metricsExportIntervalMs: 10000
```

### iii-config.docker.yaml

Docker-specific configuration:

```yaml
engine:
  wsPort: 49134
  restPort: 3111
  streamsPort: 3112

worker:
  name: agentmemory
  reconnectDelayMs: 1000

state:
  adapter: sqlite
  path: /data/state_store.db

# Docker networking
network:
  host: 0.0.0.0
```

### docker-compose.yml

Multi-service deployment:

```yaml
version: '3.8'

services:
  iii-engine:
    image: rohitg00/iii-engine:latest
    ports:
      - "49134:49134"
      - "3111:3111"
      - "3112:3112"
    volumes:
      - iii-data:/data

  agentmemory:
    image: rohitg00/agentmemory:0.8.10
    depends_on:
      - iii-engine
    environment:
      - III_ENGINE_URL=ws://iii-engine:49134
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - AGENTMEMORY_SECRET=${AGENTMEMORY_SECRET}
    volumes:
      - agentmemory-data:/root/.agentmemory
    ports:
      - "3111:3111"
      - "3112:3112"

volumes:
  iii-data:
  agentmemory-data:
```

## Runtime Configuration

### Check Current Config

```bash
# Via REST API
curl http://localhost:3111/agentmemory/config

# Returns all loaded configuration
{
  "engineUrl": "ws://localhost:49134",
  "restPort": 3111,
  "streamsPort": 3112,
  "provider": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514"
  },
  "tokenBudget": 2000,
  "embeddingProvider": "openai",
  "bm25Weight": 0.4,
  "vectorWeight": 0.6,
  // ...
}
```

### Update Config at Runtime

Most settings require restart, but some can be updated via API:

```bash
# Update token budget
curl -X POST http://localhost:3111/agentmemory/config-update \
  -H "Authorization: Bearer $AGENTMEMORY_SECRET" \
  -d '{"tokenBudget": 4000}'

# Update search weights
curl -X POST http://localhost:3111/agentmemory/config-update \
  -d '{"bm25Weight": 0.5, "vectorWeight": 0.35}'
```

### Provider Fallback Chain

Configure fallback providers for resilience:

```bash
# Primary provider
ANTHROPIC_API_KEY=sk-ant-...

# Fallback providers (JSON array in .env)
FALLBACK_PROVIDERS='[
  {"provider": "gemini", "model": "gemini-2.0-flash", "apiKeyEnv": "GEMINI_API_KEY"},
  {"provider": "openrouter", "model": "anthropic/claude-sonnet-4-20250514", "apiKeyEnv": "OPENROUTER_API_KEY"}
]'
```

**Fallback behavior:** If primary provider fails (rate limit, timeout, error), automatically retries with next fallback provider.

## Security Considerations

### Secret Management

```bash
# Always set a secret in production
AGENTMEMORY_SECRET=$(openssl rand -hex 32)

# Never commit .env files to git
echo "~/.agentmemory/.env" >> .gitignore

# Use secrets management in production:
# - Docker secrets
# - Kubernetes secrets
# - AWS Secrets Manager
# - HashiCorp Vault
```

### Authentication

All REST endpoints require Bearer token authentication when `AGENTMEMORY_SECRET` is set:

```bash
curl -H "Authorization: Bearer $AGENTMEMORY_SECRET" \
  http://localhost:3111/agentmemory/search
```

MCP tools inherit authentication from server configuration.

### Localhost-Only by Default

REST API binds to `localhost` only. To expose externally:

```bash
# WARNING: Only do this behind a reverse proxy with auth
III_REST_HOST=0.0.0.0
```

**Recommended setup:**
```
Internet → Nginx/Apache (TLS + Auth) → localhost:3111 → agentmemory
```

## Troubleshooting Configuration

### Verify Provider Detection

```bash
# Check which provider was detected
agentmemory start 2>&1 | grep "Provider:"
# Output: [agentmemory] Provider: anthropic (claude-sonnet-4-20250514)
```

### Test Embedding Provider

```bash
# Test embedding generation
curl -X POST http://localhost:3111/agentmemory/test-embedding \
  -d '{"text": "test query", "provider": "openai"}'
```

### Validate Config

```bash
# Check config parsing
python3 -c "
import yaml
with open('~/.agentmemory/iii-config.yaml') as f:
  config = yaml.safe_load(f)
print('✓ Valid' if 'engine' in config else '✗ Invalid')
"
```

### Common Issues

**Issue:** Provider not detected
```bash
# Solution: Check API key env var names
env | grep -E "(ANTHROPIC|GEMINI|OPENAI|VOYAGE|COHERE)"
```

**Issue:** Embeddings failing
```bash
# Solution: Verify embedding provider has API key
# Local provider requires @xenova/transformers installed
npm list @xenova/transformers
```

**Issue:** Token budget too low
```bash
# Symptom: Context injection truncated
# Solution: Increase TOKEN_BUDGET or reduce MAX_OBS_PER_SESSION
TOKEN_BUDGET=4000
```

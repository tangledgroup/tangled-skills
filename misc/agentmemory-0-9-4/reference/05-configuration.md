# Configuration and Providers

## LLM Providers

agentmemory auto-detects from environment. No API key needed for basic BM25-only operation (noop provider).

| Provider | Config | Notes |
|----------|--------|-------|
| **No-op (default)** | No config needed | LLM-backed compress/summarize DISABLED. Synthetic BM25 compression + recall still work. |
| Anthropic API | `ANTHROPIC_API_KEY` | Per-token billing |
| MiniMax | `MINIMAX_API_KEY` | Anthropic-compatible |
| Gemini | `GEMINI_API_KEY` | Also enables embeddings |
| OpenRouter | `OPENROUTER_API_KEY` | Any model |
| Claude subscription | `AGENTMEMORY_ALLOW_AGENT_SDK=true` | Opt-in only. Spawns `@anthropic-ai/claude-agent-sdk` sessions. |

The Claude subscription fallback is opt-in only in v0.9.x (was implicit default before). It required explicit `AGENTMEMORY_ALLOW_AGENT_SDK=true` due to Stop-hook recursion risks.

## Embedding Providers

| Provider | Config | Notes |
|----------|--------|-------|
| **Local** | `EMBEDDING_PROVIDER=local` | Free, offline. Install: `npm install @xenova/transformers` |
| Gemini | `GEMINI_API_KEY` | Auto-detected |
| OpenAI | `OPENAI_API_KEY` | `text-embedding-3-small` default |
| OpenAI-compatible | `OPENAI_BASE_URL` + `OPENAI_API_KEY` | Azure, vLLM, LM Studio |
| Voyage AI | `VOYAGE_API_KEY` | Code-optimized |
| Cohere | `COHERE_API_KEY` | General purpose |
| OpenRouter | `OPENROUTER_API_KEY` | Multi-model proxy |

OpenAI-compatible providers support `OPENAI_BASE_URL`, `OPENAI_EMBEDDING_MODEL`, and `OPENAI_EMBEDDING_DIMENSIONS` for custom/self-hosted models.

## Environment Variables

Create `~/.agentmemory/.env`:

```env
# LLM provider
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_BASE_URL=...              # Optional: Anthropic-compatible proxy / Azure
GEMINI_API_KEY=...
OPENROUTER_API_KEY=...
MINIMAX_API_KEY=...
AGENTMEMORY_ALLOW_AGENT_SDK=true    # Opt-in Claude subscription fallback

# Embedding provider
EMBEDDING_PROVIDER=local
VOYAGE_API_KEY=...
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536

# Search tuning
BM25_WEIGHT=0.4
VECTOR_WEIGHT=0.6
TOKEN_BUDGET=2000

# Auth
AGENTMEMORY_SECRET=your-secret

# Ports (defaults: 3111 API, 3113 viewer)
III_REST_PORT=3111

# Feature flags (all OFF by default)
AGENTMEMORY_AUTO_COMPRESS=false     # LLM compression per observation
AGENTMEMORY_SLOTS=false             # Editable pinned memory slots
AGENTMEMORY_REFLECT=false           # Auto-reflect into slots at session end
AGENTMEMORY_INJECT_CONTEXT=false    # Context injection into conversation
GRAPH_EXTRACTION_ENABLED=false      # Knowledge graph extraction
CONSOLIDATION_ENABLED=true          # 4-tier consolidation pipeline
LESSON_DECAY_ENABLED=true           # Lesson auto-decay
OBSIDIAN_AUTO_EXPORT=false          # Auto-export to Obsidian format
CLAUDE_MEMORY_BRIDGE=false          # Bi-directional sync with MEMORY.md
SNAPSHOT_ENABLED=false              # Git-versioned snapshots

# Team
TEAM_ID=
USER_ID=
TEAM_MODE=private

# Tool visibility: "core" (8 tools) or "all" (51 tools)
AGENTMEMORY_TOOLS=core

# Server URL override (v0.9.3+)
AGENTMEMORY_URL=http://host:port    # Honored by CLI status/doctor
```

## Feature Flags

v0.9.3 introduced a feature flag system with visibility across the viewer, CLI, and REST API:

- **`/agentmemory/config/flags`** endpoint returns full flag state
- Viewer shows collapsible banner with per-flag cards
- CLI `status` and `doctor` commands show flag states
- Disabled flags produce structured error responses with enable instructions

## iii Console

For trace-level engine inspection, use the official [iii console](https://iii.dev/docs/console):

```bash
curl -fsSL https://install.iii.dev/console/main/install.sh | sh
iii-console --port 3114 --engine-port 3111 --ws-port 3112
```

Provides OpenTelemetry traces, KV state store browser, stream monitor, and direct function invoker.

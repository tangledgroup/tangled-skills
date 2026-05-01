# Memory Pipeline and Hooks

## Observation Lifecycle

The memory pipeline processes agent activity through a multi-stage pipeline:

```
PostToolUse hook fires
  -> SHA-256 dedup (5min window)
  -> Privacy filter (strip secrets, API keys)
  -> Store raw observation
  -> LLM compress -> structured facts + concepts + narrative
  -> Vector embedding (6 providers + local)
  -> Index in BM25 + vector

Stop / SessionEnd hook fires
  -> Summarize session
  -> Knowledge graph extraction (if GRAPH_EXTRACTION_ENABLED=true)
  -> Slot reflection (if SLOT_REFLECT_ENABLED=true)

SessionStart hook fires
  -> Load project profile (top concepts, files, patterns)
  -> Hybrid search (BM25 + vector + graph)
  -> Token budget (default: 2000 tokens)
  -> Inject into conversation
```

## Lifecycle Hooks

agentmemory registers 12 lifecycle hooks for Claude Code (via the official plugin). Other agents use MCP tools or REST API instead.

| Hook | Captures |
|------|----------|
| `SessionStart` | Project path, session ID |
| `UserPromptSubmit` | User prompts (privacy-filtered) |
| `PreToolUse` | File access patterns + enriched context |
| `PostToolUse` | Tool name, input, output |
| `PostToolUseFailure` | Error context |
| `PreCompact` | Re-injects memory before compaction |
| `SubagentStart` | Sub-agent lifecycle entry |
| `SubagentStop` | Sub-agent lifecycle exit |
| `Stop` | End-of-session summary, graph extraction |
| `SessionEnd` | Session complete marker |

## 4-Tier Memory Consolidation

| Tier | What | Analogy |
|------|------|---------|
| **Working** | Raw observations from tool use | Short-term memory |
| **Episodic** | Compressed session summaries | "What happened" |
| **Semantic** | Extracted facts and patterns | "What I know" |
| **Procedural** | Workflows and decision patterns | "How to do it" |

Memories decay over time (Ebbinghaus curve). Frequently accessed memories strengthen. Stale memories auto-evict. Contradictions are detected and resolved.

## Compression Modes

- **Synthetic BM25 compression** — always available, no LLM required. Produces keyword-rich summaries optimized for BM25 retrieval.
- **LLM-powered compression** — requires an LLM provider (Anthropic, Gemini, OpenRouter, MiniMax). Produces richer structured facts, concepts, and narratives. Controlled by `AGENTMEMORY_AUTO_COMPRESS` flag (OFF by default due to token cost on active sessions).

## Privacy Filtering

Before storage, observations pass through a privacy filter that strips:
- API keys and secrets
- `<private>` tagged content
- Sensitive file paths
- Authentication tokens

## Knowledge Graph Extraction

When `GRAPH_EXTRACTION_ENABLED=true`, the `mem::graph-extract` function fires at session end (Stop/SessionEnd hooks). It extracts entities and relationships from session observations and merges them into the knowledge graph using idempotent node/edge merge keys. This runs fire-and-forget and does not block session teardown.

In v0.9.4, a bug fix ensures `mem::graph-extract` actually auto-fires at session end — previously it was registered but never internally invoked unless manually called via REST `/agentmemory/graph/extract`.

## Session Replay

Every recorded session is replayable through the viewer's **Replay** tab. Scrub through the timeline with play/pause, speed control (0.5x–4x), and keyboard shortcuts (space to toggle, arrows to step). Prompts, tool calls, tool results, and responses render as discrete events.

Import older Claude Code JSONL transcripts:

```bash
# Import everything under default ~/.claude/projects
npx @agentmemory/agentmemory import-jsonl

# Or a single file
npx @agentmemory/agentmemory import-jsonl ~/.claude/projects/-my-project/abc123.jsonl
```

Imported sessions go through synthetic compression + BM25 indexing, produce auto-derived lessons and crystals, and appear in the Replay picker alongside native sessions.

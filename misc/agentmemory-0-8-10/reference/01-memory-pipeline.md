# Memory Pipeline and Hooks

## Observation Lifecycle

The memory pipeline captures agent activity through 12 lifecycle hooks, processes observations through deduplication and privacy filtering, then indexes them for retrieval.

```
PostToolUse hook fires
  -> SHA-256 dedup (5min window)
  -> Privacy filter (strip secrets, API keys)
  -> Store raw observation
  -> Synthetic compression (default) or LLM compression (opt-in)
     -> structured facts + concepts + narrative
  -> Vector embedding (if provider configured)
  -> Index in BM25 + vector + knowledge graph

SessionStart hook fires
  -> Load project profile (top concepts, files, patterns)
  -> Hybrid search (BM25 + vector + graph)
  -> Token budget (default: 2000 tokens)
  -> Inject into conversation (only if AGENTMEMORY_INJECT_CONTEXT=true)
```

## Lifecycle Hooks

| Hook | Captures |
|------|----------|
| `SessionStart` | Project path, session ID |
| `UserPromptSubmit` | User prompts (privacy-filtered) |
| `PreToolUse` | File access patterns + enriched context |
| `PostToolUse` | Tool name, input, output |
| `PostToolUseFailure` | Error context |
| `PreCompact` | Re-injects memory before compaction |
| `SubagentStart/Stop` | Sub-agent lifecycle |
| `Stop` | End-of-session summary |
| `SessionEnd` | Session complete marker |
| `Notification` | Agent notifications |
| `TaskCompleted` | Task completion data |

## Data Types

### Raw Observation

Captured directly from hook payloads before compression:

```typescript
interface RawObservation {
  id: string;
  sessionId: string;
  timestamp: string;
  hookType: HookType;
  toolName?: string;
  toolInput?: unknown;
  toolOutput?: unknown;
  userPrompt?: string;
  assistantResponse?: string;
  raw: unknown;
}
```

### Compressed Observation

After synthetic or LLM compression:

```typescript
interface CompressedObservation {
  id: string;
  sessionId: string;
  timestamp: string;
  type: ObservationType;       // file_read, file_write, command_run, error, decision, etc.
  title: string;
  subtitle?: string;
  facts: string[];
  narrative: string;
  concepts: string[];
  files: string[];
  importance: number;
  confidence?: number;
}
```

### Memory

Long-term stored knowledge:

```typescript
interface Memory {
  id: string;
  createdAt: string;
  updatedAt: string;
  type: "pattern" | "preference" | "architecture" | "bug" | "workflow" | "fact";
  title: string;
  content: string;
  concepts: string[];
  files: string[];
  sessionIds: string[];
  strength: number;            // 1-10
  version: number;
  parentId?: string;
  supersedes?: string[];       // Jaccard-based supersession
  relatedIds?: string[];
  sourceObservationIds?: string[];
  isLatest: boolean;
  forgetAfter?: string;        // TTL expiry
}
```

## Compression Modes

### Synthetic Compression (default, 0.8.8+)

Zero-LLM compression that derives `type`, `title`, `narrative`, and `files` directly from raw tool name, tool input, and tool output. Narratives are truncated to 400 characters. BM25 indexing works on synthetic data. This is the default since 0.8.8 to prevent silent token burn.

Tool-name-to-type mapping uses camelCase-aware substring matching: `Read` → `file_read`, `Write` → `file_write`, `Edit` → `file_edit`, `Bash` → `command_run`, `Grep` → `search`, `WebFetch` → `web_fetch`, etc.

### LLM Compression (opt-in)

Set `AGENTMEMORY_AUTO_COMPRESS=true` to enable per-observation LLM compression. Each PostToolUse hook triggers a call to your configured LLM provider to produce richer summaries with structured XML output:

```xml
<memory>
  <type>pattern|preference|architecture|bug|workflow|fact</type>
  <title>Concise memory title (max 80 chars)</title>
  <content>2-4 sentence description of the learned insight</content>
  <concepts>
    <concept>key term</concept>
  </concepts>
  <files>
    <file>relevant/file/path</file>
  </files>
  <strength>1-10 how confident/important this memory is</strength>
</memory>
```

**Warning:** Active coding sessions (50-200 tool calls/hour) can consume hundreds of thousands of tokens with LLM compression enabled.

## Privacy Filtering

Before any observation is stored, the privacy filter strips:
- `<private>...</private>` tagged content
- API keys matching patterns: `sk-proj-*`, `sk-ant-*`, `sk-*`, `pk-*`
- Bearer tokens
- GitHub tokens (`ghp_*`, `ghs_*`, `ghu_*`, `github_pat_*`)
- Slack tokens (`xoxb-*`)
- AWS access keys (`AKIA*`)
- Google API keys (`AIza*`)
- JWT tokens (`eyJ*`)
- npm tokens (`npm_*`)
- GitLab tokens (`glpat-*`)
- Datadog tokens (`dop_v1_*`)

## Deduplication

SHA-256 hash of observation content with a 5-minute window. Duplicate observations within the window are discarded, preventing redundant captures from rapid tool use sequences.

## KV Storage Namespaces

All state is stored via iii-engine's KV StateModule:

- `mem:sessions` — session metadata
- `mem:obs:<sessionId>` — observations per session
- `mem:memories` — long-term memories
- `mem:summaries` — session summaries
- `mem:index:bm25` — BM25 inverted index
- `mem:emb:<obsId>` — vector embeddings
- `mem:graph:nodes` / `mem:graph:edges` — knowledge graph
- `mem:semantic` — semantic facts (consolidation tier 3)
- `mem:procedural` — procedural workflows (consolidation tier 4)
- `mem:relations` — memory relationships
- `mem:access` — access log for retention scoring
- `mem:audit` — audit trail of all mutations
- `mem:actions`, `mem:leases`, `mem:routines`, `mem:signals` — multi-agent coordination
- `mem:team:<teamId>:shared` — team memory

## Auto-Forgetting

Three mechanisms remove stale or low-value data:

1. **TTL expiry** — memories with `forgetAfter` timestamp past current time are deleted
2. **Contradiction detection** — Jaccard similarity above 0.9 threshold triggers review of contradictory memories
3. **Low-value eviction** — retention scoring based on access frequency and recency (Ebbinghaus decay curve). Semantic memories that fall below threshold are evicted, with audit records emitted per sweep

Retention scores track real agent-side reads from search, context, timeline, and file-context endpoints. A bounded ring buffer stores the last 20 access timestamps per memory for time-frequency decay computation.

## 4-Tier Consolidation

Requires `CONSOLIDATION_ENABLED=true`:

| Tier | What | Analogy |
|------|------|---------|
| **Working** | Raw observations from tool use | Short-term memory |
| **Episodic** | Compressed session summaries | "What happened" |
| **Semantic** | Extracted facts and patterns | "What I know" |
| **Procedural** | Workflows and decision patterns | "How to do it" |

The consolidation pipeline:
1. Gathers session summaries (requires >= 5 summaries for semantic tier)
2. Sends to LLM provider with semantic merge prompt
3. Extracts facts from XML response with confidence scores
4. Merges with existing semantic memories (strength boost on access)
5. Runs reflect tier for pattern clustering
6. Applies Ebbinghaus decay based on `CONSOLIDATION_DECAY_DAYS` (default: 30 days)

Decay formula: `strength * 0.9^decayPeriods` where `decayPeriods = floor(daysSinceLastAccess / decayDays)`. Minimum strength floor is 0.1.

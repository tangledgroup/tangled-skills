# agentmemory Architecture Details

## iii-Engine Integration

agentmemory is built on [iii-engine](https://github.com/rohitg00/iii-engine), which provides three core primitives:

### 1. Worker
Long-running process that registers functions and triggers. agentmemory runs as a single worker connected via WebSocket.

```typescript
import { init } from "iii-sdk";

const sdk = init("ws://localhost:49134", {
  workerName: "agentmemory",
  otel: {
    serviceName: "agentmemory",
    serviceVersion: "0.8.10",
    metricsExportIntervalMs: 10000,
  },
});
```

### 2. Function
Stateless operations registered with the SDK. All memory operations are functions.

```typescript
sdk.registerFunction(
  { id: "mem::remember" },
  async (data: { content: string; type: string; concepts: string[] }) => {
    // Validate inputs
    // Create memory object
    // Store via kv.set()
    // Record audit log
    return { success: true, memoryId: "mem_abc123" };
  },
);
```

### 3. Trigger
Event handlers that invoke functions. Types include HTTP, WebSocket, and scheduled triggers.

```typescript
// HTTP trigger for REST API
sdk.registerTrigger({
  type: "http",
  function_id: "api::search",
  config: { api_path: "/agentmemory/search", http_method: "POST" },
});

// WebSocket trigger for hook events
sdk.registerTrigger({
  type: "ws",
  function_id: "hook::observer",
  config: { path: "/hooks" },
});
```

## State Management

### StateKV Wrapper

File-based SQLite access via iii-engine's StateModule. All persistent data goes through `StateKV`.

```typescript
import { StateKV } from "./state/kv.js";

const kv = new StateKV(sdk);

// Store session
await kv.set(KV.sessions, sessionId, sessionData);

// List all memories
const memories = await kv.list(KV.memories);

// Get specific observation
const obs = await kv.get(KV.observations(sessionId), obsId);
```

### KV Scopes

All data organized into named scopes in `src/state/schema.ts`:

```typescript
export const KV = {
  // Core entities
  sessions: "mem:sessions",
  observations: (sessionId: string) => `mem:obs:${sessionId}`,
  memories: "mem:memories",
  summaries: "mem:summaries",
  
  // Search indexes
  embeddings: (obsId: string) => `mem:emb:${obsId}`,
  bm25Index: "mem:index:bm25",
  
  // Knowledge graph
  relations: "mem:relations",
  graphNodes: "mem:graph:nodes",
  graphEdges: "mem:graph:edges",
  
  // Advanced features
  profiles: "mem:profiles",
  teamShared: (teamId: string) => `mem:team:${teamId}:shared`,
  audit: "mem:audit",
  // ... 30+ total scopes
} as const;
```

### Data Flow

```
Hook Event → RawObservation → LLM Compression → CompressedObservation
                                                     ↓
                                              Memory Storage
                               ↓              ↓              ↓
                          BM25 Index    Vector Embed    Graph Edge
                               ↓              ↓              ↓
                         Hybrid Search ←───────────────────────┘
```

## Observation Processing Pipeline

### 1. Capture (Hook Observer)

```typescript
registerObserveFunction(sdk, kv, dedupMap, maxObservationsPerSession);

// Hooks into agent lifecycle events
interface HookPayload {
  hookType: HookType;      // session_start, pre_tool_use, etc.
  sessionId: string;
  project: string;
  cwd: string;
  timestamp: string;
  data: unknown;           // Tool input/output, prompt/response
}
```

### 2. Deduplication

Content-addressable dedup using SHA-256 fingerprinting:

```typescript
function fingerprintId(prefix: string, content: string): string {
  const hash = createHash("sha256").update(content).digest("hex");
  return `${prefix}_${hash.slice(0, 16)}`;
}

// Check before storing
const existing = dedupMap.get(fingerprintId("obs", rawData));
if (existing) return existing; // Skip duplicate
```

### 3. Compression (LLM-Powered)

Compresses raw observations into structured format:

```typescript
registerCompressFunction(sdk, kv, provider, metricsStore);

// System prompt guides compression
const systemPrompt = `Extract key facts from agent tool usage.
Format: title, subtitle, facts[], narrative, concepts[], files[]`;

const compressed = await provider.compress(
  systemPrompt,
  JSON.stringify(rawObservation),
);
```

**Compression output:**
```typescript
interface CompressedObservation {
  id: string;
  sessionId: string;
  timestamp: string;
  type: ObservationType;      // file_read, command_run, decision, etc.
  title: string;              // "Added JWT middleware"
  subtitle?: string;          // "Using jose library for Edge compatibility"
  facts: string[];            // ["JWT uses HS256", "Token expiry: 24h"]
  narrative: string;          // "Implemented authentication..."
  concepts: string[];         // ["jwt", "auth", "edge-functions"]
  files: string[];            // ["src/middleware/auth.ts"]
  importance: number;         // 0-1 score from LLM
  confidence?: number;        // LLM confidence in compression quality
}
```

### 4. Indexing

**BM25 Index (always active):**
```typescript
const bm25Index = new BM25Index();
bm25Index.add(obsId, {
  title: obs.title,
  narrative: obs.narrative,
  concepts: obs.concepts.join(" "),
  files: obs.files.join(" "),
});
```

**Vector Embeddings (optional):**
```typescript
if (embeddingProvider) {
  const embedding = await embeddingProvider.embed(
    `${obs.title} ${obs.narrative} ${obs.concepts.join(" ")}`
  );
  await kv.set(KV.embeddings(obsId), obsId, embedding);
}
```

**Graph Extraction:**
```typescript
registerGraphFunction(sdk, kv);

// Extract entities and relationships
const entities = extractEntities(obs.narrative); // ["JWT", "jose", "auth middleware"]
const relations = inferRelations(obs, existingMemories); // [{ source: "mem_abc", target: "mem_def", type: "extends" }]
```

## Hybrid Search Implementation

### Scoring Algorithm

```typescript
interface HybridSearchResult {
  observation: CompressedObservation;
  bm25Score: number;        // Normalized 0-1
  vectorScore: number;      // Cosine similarity 0-1
  graphScore: number;       // Relation-based score 0-1
  combinedScore: number;    // Weighted sum
  sessionId: string;
  graphContext?: string;    // Related memories for context
}

// Combined score calculation
const combinedScore =
  (bm25Score * BM25_WEIGHT) +
  (vectorScore * VECTOR_WEIGHT) +
  (graphScore * GRAPH_WEIGHT);

// Default weights: BM25=0.4, Vector=0.35, Graph=0.25
```

### Progressive Disclosure

Two-phase search for efficiency:

```typescript
// Phase 1: Compact results (metadata only)
const compactResults = await smartSearch(query, { limit: 10 });
// Returns: [{ obsId, title, type, score, timestamp }]

// Phase 2: Expand specific results
const expanded = await expandObservations(
  compactResults.filter(r => r.score > 0.7).map(r => r.obsId)
);
// Returns: Full observation details for high-confidence matches
```

## Multi-Agent Coordination

### Shared State Architecture

```
┌─────────────────────────────────────────────────────┐
│              iii-engine (WebSocket Server)          │
│                 Port 49134                          │
└─────────────────────────────────────────────────────┘
                         ↓
            ┌──────────────────────────┐
            │   agentmemory Worker     │
            │   (Single Instance)      │
            └──────────────────────────┘
                         ↓
            ┌──────────────────────────┐
            │  StateKV (SQLite File)   │
            │  ~/.agentmemory/         │
            │  state_store.db          │
            └──────────────────────────┘
                         ↓
    ┌─────────────────┬────────────┬─────────────────┐
    ↓                 ↓            ↓                 ↓
Claude Code      Cursor        Gemini CLI      OpenCode
(Hooks + MCP)    (MCP)         (MCP)           (MCP)
```

**Key insight:** All agents share the same memory server. Memories captured by Claude Code are immediately available to Cursor, and vice versa.

### Session Isolation

Each agent session gets a unique ID:

```typescript
const sessionId = generateId("session");
// Example: "session_1i2a3b4c5d6_e7f8g9h0"

// Observations tagged with sessionId for traceability
interface RawObservation {
  id: string;
  sessionId: string;    // Links to specific agent session
  timestamp: string;
  hookType: HookType;
  // ...
}
```

### Cross-Session Context Injection

At session start, inject relevant context:

```typescript
registerContextFunction(sdk, kv, tokenBudget);

// Called at session_start hook
const context = await buildContext({
  project: cwd,
  tokenBudget: 2000,      // Configurable via TOKEN_BUDGET
  include: ["summaries", "memories", "recent-observations"],
});

// Returns ContextBlock array sorted by relevance
interface ContextBlock {
  type: "summary" | "observation" | "memory";
  content: string;        // Markdown-formatted context
  tokens: number;         // Token count for budget tracking
  recency: number;        // 0-1 score based on timestamp
  sourceIds?: string[];   // Source observation/memory IDs
}
```

## Health Monitoring

### Circuit Breaker Pattern

Prevents cascading failures:

```typescript
interface CircuitBreakerState {
  state: "closed" | "open" | "half-open";
  failures: number;
  lastFailureAt: number | null;
  openedAt: number | null;
}

// Auto-recovery after cooldown
if (state === "open" && Date.now() - openedAt > COOLDOWN_MS) {
  state = "half-open"; // Allow one test request
}
```

### Health Checks

```typescript
registerHealthMonitor(sdk, kv);

// Exposed via REST API
curl http://localhost:3111/agentmemory/health

// Returns health snapshot
interface HealthSnapshot {
  connectionState: string;
  workers: Array<{ id: string; name: string; status: string }>;
  memory: { heapUsed: number; heapTotal: number; rss: number };
  cpu: { percent: number };
  eventLoopLagMs: number;
  uptimeSeconds: number;
  kvConnectivity?: { status: string; latencyMs?: number };
  status: "healthy" | "degraded" | "critical";
  alerts: string[];
}
```

## Telemetry and Metrics

### OpenTelemetry Integration

```typescript
import { initMetrics, OTEL_CONFIG } from "./telemetry/setup.js";

initMetrics(sdk.getMeter.bind(sdk));

// Track function performance
const metricsStore = new MetricsStore(kv);

// Record latency and quality scores
metricsStore.record({
  functionId: "mem::compress",
  latencyMs: 1234,
  qualityScore: 0.92,
  success: true,
});
```

### Function Metrics

```typescript
interface FunctionMetrics {
  functionId: string;
  totalCalls: number;
  successCount: number;
  failureCount: number;
  avgLatencyMs: number;
  avgQualityScore: number;
}

// Access via REST API
curl http://localhost:3111/agentmemory/metrics
```

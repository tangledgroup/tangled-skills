# Session Management and Compaction

This document covers session persistence, branching, compaction strategies, and conversation history management in Pi Coding Agent.

## Session Architecture

### Session File Structure

Sessions are stored as JSONL (JSON Lines) files:

```
~/.pi/sessions/
├── 2024-01-15-refactor-auth/
│   └── session.jsonl
├── 2024-01-16-add-tests/
│   └── session.jsonl
└── 2024-01-17-fix-bugs/
    └── session.jsonl
```

Each session file contains:

```json
// Line 1: Session header
{
  "type": "header",
  "version": 1,
  "createdAt": "2024-01-15T10:30:00.000Z",
  "model": { "id": "gpt-4o", "provider": "openai" },
  "thinkingLevel": "high",
  "cwd": "/home/user/project",
  "labels": ["refactor", "auth"]
}

// Line 2+: Session entries (messages, tool calls, etc.)
{"type": "user", "content": "Refactor the auth module", "timestamp": 1705315800000}
{"type": "assistant", "content": [...], "usage": {...}, "stopReason": "toolUse"}
{"type": "toolResult", "toolCallId": "1", "toolName": "read", "content": [...], "isError": false}
{"type": "compaction", "summary": "...", "tokensSaved": 5000}
```

### Session Entry Types

Different entry types track conversation state:

```typescript
type SessionEntry = 
  | HeaderEntry        // Session metadata
  | UserMessageEntry   // User messages
  | AssistantMessageEntry // Assistant responses
  | ToolResultEntry    // Tool execution results
  | CompactionEntry    // Summary after compaction
  | ModelChangeEntry   // Model switch events
  | ThinkingLevelChangeEntry // Thinking level changes
  | CustomEntry        // Extension-defined entries
  | BashExecutionEntry // Bash command history
  | BranchSummaryEntry // Branch summary data
```

## Session Manager

### Creating Sessions

```typescript
const sessionManager = new SessionManager({
  sessionsDir: "~/.pi/sessions",
});

// Create new session
const session = await sessionManager.createSession({
  name: "refactor-auth",
  model: getModel("openai", "gpt-4o"),
  thinkingLevel: "high",
  cwd: process.cwd(),
  labels: ["refactor"]
});

// Or create with default name (timestamp-based)
const autoSession = await sessionManager.createSession();
// Name: "2024-01-15T10-30-00"
```

### Loading Sessions

```typescript
// List available sessions
const sessions = await sessionManager.listSessions();
[
  { id: "refactor-auth", path: "...", lastModified: ... },
  { id: "add-tests", path: "...", lastModified: ... }
]

// Load specific session
const session = await sessionManager.loadSession("refactor-auth");

// Load most recent session
const recent = await sessionManager.loadMostRecentSession();
```

### Session Context

Access session metadata:

```typescript
interface SessionContext {
  id: string;
  path: string;
  createdAt: Date;
  lastModified: Date;
  model: Model<any>;
  thinkingLevel: ThinkingLevel;
  cwd: string;
  labels: string[];
  entries: SessionEntry[];
  stats: {
    turnCount: number;
    toolCallCount: number;
    tokenCount: number;
    compactionCount: number;
  };
}

const context = sessionManager.getContext();
console.log(`Session ${context.id}: ${context.stats.turnCount} turns`);
```

## Compaction System

### Why Compact?

LLM context windows are limited. Compaction preserves conversation history while reducing token count:

- **Context Overflow Prevention**: Stay within model limits
- **Cost Reduction**: Fewer tokens = lower costs
- **Performance**: Smaller context = faster responses
- **Focus**: Keep recent/relevant information prominent

### Compaction Triggers

Compaction occurs automatically when:

```typescript
function shouldCompact(
  entries: SessionEntry[],
  settings: CompactionSettings
): { shouldCompact: boolean; reason: "threshold" | "overflow" | null } {
  const usage = calculateContextTokens(entries);
  const limit = settings.maxTokens || 100000;
  const threshold = settings.threshold || 0.8; // 80%
  
  // Overflow: already exceeded limit
  if (usage.totalTokens > limit) {
    return { shouldCompact: true, reason: "overflow" };
  }
  
  // Threshold: approaching limit
  if (usage.totalTokens / limit > threshold) {
    return { shouldCompact: true, reason: "threshold" };
  }
  
  return { shouldCompact: false, reason: null };
}
```

### Compaction Process

Four-phase compaction workflow:

```typescript
async function compact(
  entries: SessionEntry[],
  model: Model<any>,
  settings: CompactionSettings
): Promise<CompactionResult> {
  // Phase 1: Find cut point
  const cutPoint = await findCutPoint(entries, settings);
  
  // Phase 2: Prepare branch summary
  const branchSummary = await prepareBranchEntries(
    entries.slice(0, cutPoint.index)
  );
  
  // Phase 3: Generate summary via LLM
  const summary = await generateSummary(
    branchSummary,
    model,
    settings
  );
  
  // Phase 4: Replace old entries with summary
  const newEntries = [
    ...entries.slice(cutPoint.index),
    {
      type: "compaction",
      summary: summary.text,
      tokensSaved: cutPoint.tokenCount,
      timestamp: Date.now()
    }
  ];
  
  return {
    originalCount: entries.length,
    newCount: newEntries.length,
    tokensSaved: cutPoint.tokenCount,
    summaryLength: summary.text.length
  };
}
```

### Cut Point Selection

Intelligent cut point finding preserves important context:

```typescript
async function findCutPoint(
  entries: SessionEntry[],
  settings: CompactionSettings
): Promise<CutPointResult> {
  // Find turn start indices (user message after assistant + tool results)
  const turnStarts = findTurnStartIndices(entries);
  
  // Calculate cumulative token usage from end
  let cumulativeTokens = 0;
  const targetTokens = settings.maxTokens * (1 - settings.preserveRatio);
  
  for (let i = entries.length - 1; i >= 0; i--) {
    const entry = entries[i];
    const tokens = estimateTokens(entry);
    cumulativeTokens += tokens;
    
    // Found turn start that keeps us under limit
    if (turnStarts.includes(i) && cumulativeTokens > targetTokens) {
      return {
        index: i,
        tokenCount: calculateTokensBefore(entries, i),
        turnNumber: getTurnNumberAtEntry(entries, i)
      };
    }
  }
  
  // Fallback: compact everything except last turn
  return {
    index: turnStarts[turnStarts.length - 2] || 0,
    tokenCount: calculateTokensBefore(entries, 0),
    turnNumber: 1
  };
}
```

### Summary Generation

LLM generates concise summary of old conversation:

```typescript
async function generateSummary(
  entries: SessionEntry[],
  model: Model<any>,
  settings: CompactionSettings
): Promise<BranchSummaryResult> {
  // Build context from entries
  const context = buildSessionContext(entries);
  
  // Prompt for summary
  const prompt = `
Summarize this conversation for future reference. Include:
- Key decisions made
- Files modified and why
- Important technical details
- Outstanding tasks or questions

Conversation:
${context}
  `;
  
  // Call LLM with reduced tokens
  const response = await streamSimple(model, {
    systemPrompt: "You are a conversation summarizer.",
    messages: [{ role: "user", content: prompt, timestamp: Date.now() }],
    tools: []
  }, {
    maxTokens: settings.summaryMaxTokens || 1000
  });
  
  const summary = await response.result();
  
  return {
    text: summary.content.map(b => b.text).join("\n"),
    usage: summary.usage
  };
}
```

## Session Branching

### Creating Branches

Fork sessions to explore alternatives:

```typescript
// Create branch from current session
const branch = await sessionManager.createBranch({
  fromSession: "refactor-auth",
  name: "refactor-auth-alternative",
  forkPoint: -1 // From end, or specify entry index
});

// Or branch from specific point
const midSessionBranch = await sessionManager.createBranch({
  fromSession: "refactor-auth", 
  name: "try-different-approach",
  forkPoint: 15 // Fork from entry 15
});
```

### Branch Summary

Compare branches with summaries:

```typescript
const summary = await generateBranchSummary(
  sessionManager,
  "refactor-auth",
  "refactor-auth-alternative"
);

console.log(`
Branch Comparison:
- Original: ${summary.original.turnCount} turns, ${summary.original.tokenCount} tokens
- Branch: ${summary.branch.turnCount} turns, ${summary.branch.tokenCount} tokens
- Divergence point: Entry ${summary.divergencePoint}
`);
```

## Session Switching

### Switching Sessions

Change active session:

```typescript
// List and select session
const sessions = await sessionManager.listSessions();
const selected = await selectSession(sessions); // UI selection

// Switch to selected session
await sessionManager.switchSession(selected.id);

// Agent continues with new session context
await agent.continue();
```

### Session Tree Navigation

Navigate session history:

```typescript
// Get session tree (parent-child relationships)
const tree = await sessionManager.getSessionTree();
/*
{
  id: "refactor-auth",
  children: [
    { id: "refactor-auth-alternative", forkPoint: 15 },
    { id: "refactor-auth-v2", forkPoint: -1 }
  ]
}
*/

// Navigate to parent
await sessionManager.navigateToParent();

// Navigate to child
await sessionManager.navigateToChild("refactor-auth-alternative");
```

## Context Token Estimation

### Token Counting

Estimate tokens for different entry types:

```typescript
function estimateTokens(entry: SessionEntry): number {
  switch (entry.type) {
    case "user":
      return Math.ceil(entry.content.length / 4);
    
    case "assistant":
      const contentTokens = entry.content.reduce(
        (sum, block) => sum + Math.ceil(block.text.length / 4), 
        0
      );
      return contentTokens + entry.usage.totalTokens;
    
    case "toolResult":
      return Math.ceil(
        entry.content.map(b => b.text).join("\n").length / 4
      );
    
    case "compaction":
      // Summaries are compressed, count at 50% rate
      return Math.ceil(entry.summary.length / 8);
    
    default:
      return Math.ceil(JSON.stringify(entry).length / 4);
  }
}

// Total context usage
function calculateContextTokens(entries: SessionEntry[]): ContextUsage {
  let total = 0;
  const byType: Record<string, number> = {};
  
  for (const entry of entries) {
    const tokens = estimateTokens(entry);
    total += tokens;
    byType[entry.type] = (byType[entry.type] || 0) + tokens;
  }
  
  return { totalTokens: total, byType };
}
```

## Manual Compaction

### User-Initiated Compaction

Force compaction via command:

```typescript
context.registerCommand({
  name: "compact",
  description: "Manually compact session history",
  handler: async (ctx) => {
    const result = await session.compact({
      reason: "manual",
      preserveRatio: 0.3 // Keep last 30% of tokens
    });
    
    ctx.output(`
Compaction complete:
- Tokens saved: ${result.tokensSaved}
- Entries removed: ${result.originalCount - result.newCount}
- Summary length: ${result.summaryLength} chars
    `);
  }
});

// Usage: /compact
```

### Compaction Settings

Configure compaction behavior:

```typescript
const settings = {
  compaction: {
    enabled: true,
    maxTokens: 100000,        // Compact when exceeding this
    threshold: 0.8,           // Or when reaching 80% of maxTokens
    preserveRatio: 0.2,       // Keep last 20% of conversation
    summaryMaxTokens: 1000,   // Max tokens for summary generation
    minEntriesToCompact: 10   // Don't compact if fewer than 10 entries
  }
};
```

## Session Persistence

### Auto-Save

Sessions auto-save after each turn:

```typescript
context.subscribe(async (event) => {
  if (event.type === "turn_end") {
    await sessionManager.saveSession();
  }
});
```

### Save Entry

Add entries to session:

```typescript
await sessionManager.saveEntry({
  type: "custom",
  source: "my-extension",
  data: { action: "deploy", environment: "production" },
  timestamp: Date.now()
});
```

### Migration Support

Session format versioning:

```typescript
const CURRENT_SESSION_VERSION = 1;

function migrateSessionEntries(
  entries: SessionEntry[],
  fromVersion: number
): SessionEntry[] {
  if (fromVersion < 1) {
    // Migrate from v0 to v1
    return entries.map(entry => ({
      ...entry,
      version: 1
    }));
  }
  
  return entries;
}
```

## Best Practices

1. **Label sessions** - Use descriptive names and labels for organization
2. **Branch before experiments** - Fork session before trying risky changes
3. **Compact regularly** - Don't wait for overflow to compact
4. **Review summaries** - Check compaction summaries preserve key info
5. **Archive old sessions** - Move completed sessions to archive folder
6. **Use labels** - Tag sessions for easy filtering (e.g., "bugfix", "feature")
7. **Monitor token usage** - Watch context growth with /stats command
8. **Test branches** - Verify branch works before merging changes

## Session Statistics

### Track Usage

Monitor session metrics:

```typescript
const stats = sessionManager.getStats();

console.log(`
Session Statistics:
- Total turns: ${stats.turnCount}
- Tool calls: ${stats.toolCallCount}
- Token usage: ${stats.tokenCount.toLocaleString()}
  - Input: ${stats.inputTokens.toLocaleString()}
  - Output: ${stats.outputTokens.toLocaleString()}
- Compactions: ${stats.compactionCount}
- Tokens saved: ${stats.tokensSaved.toLocaleString()}
- Duration: ${formatDuration(stats.duration)}
`);
```

### Cost Tracking

Calculate session costs:

```typescript
function calculateSessionCost(
  entries: SessionEntry[],
  model: Model<any>
): { total: number; breakdown: Record<string, number> } {
  const usage = { input: 0, output: 0 };
  
  for (const entry of entries) {
    if (entry.type === "assistant" && entry.usage) {
      usage.input += entry.usage.input;
      usage.output += entry.usage.output;
    }
  }
  
  const cost = {
    input: (model.cost.input / 1000000) * usage.input,
    output: (model.cost.output / 1000000) * usage.output
  };
  
  return {
    total: cost.input + cost.output,
    breakdown: cost
  };
}

const cost = calculateSessionCost(entries, model);
console.log(`Session cost: $${cost.total.toFixed4}`);
```

# Session Management

Sessions are JSONL files with tree structure (`id`/`parentId`), enabling in-place branching without creating new files. Stored in `~/.pi/agent/sessions/--<path>--/<timestamp>_<uuid>.jsonl`.

## File Format

Each line is a JSON object. First line is the session header:

```json
{"type":"session","version":3,"id":"uuid","timestamp":"2024-12-03T14:00:00.000Z","cwd":"/path/to/project"}
```

Sessions have version tracking (v1 legacy → v2 tree → v3 renamed hookMessage to custom). Auto-migrated on load.

## Entry Types

All entries extend `SessionEntryBase`:

```typescript
interface SessionEntryBase {
  type: string;
  id: string;           // 8-char hex ID
  parentId: string | null;
  timestamp: string;    // ISO timestamp
}
```

### Message Entry

```json
{"type":"message","id":"a1b2c3d4","parentId":"prev1234","timestamp":"...","message":{"role":"user","content":"Hello"}}
```

### Model/Thinking Change Entries

```json
{"type":"model_change","id":"d4e5f6g7","parentId":"prev","timestamp":"...","provider":"openai","modelId":"gpt-4o"}
{"type":"thinking_level_change","id":"e5f6g7h8","parentId":"prev","timestamp":"...","thinkingLevel":"high"}
```

### Compaction Entry

```json
{"type":"compaction","id":"f6g7h8i9","parentId":"prev","timestamp":"...","summary":"User discussed X,Y,Z...","firstKeptEntryId":"c3d4e5f6","tokensBefore":50000}
```

Optional: `details` (file tracking), `fromHook` (true if extension-generated).

### Branch Summary Entry

```json
{"type":"branch_summary","id":"g7h8i9j0","parentId":"a1b2c3d4","timestamp":"...","fromId":"f6g7h8i9","summary":"Branch explored approach A..."}
```

### Custom Entry (Extension State, NOT in LLM context)

```json
{"type":"custom","id":"h8i9j0k1","parentId":"prev","timestamp":"...","customType":"my-extension","data":{"count":42}}
```

### Custom Message Entry (Extension, IN LLM context)

```json
{"type":"custom_message","id":"i9j0k1l2","parentId":"prev","timestamp":"...","customType":"my-extension","content":"Injected context...","display":true}
```

### Label Entry

```json
{"type":"label","id":"j0k1l2m3","parentId":"prev","timestamp":"...","targetId":"a1b2c3d4","label":"checkpoint-1"}
```

### Session Info Entry

```json
{"type":"session_info","id":"k1l2m3n4","parentId":"prev","timestamp":"...","name":"Refactor auth module"}
```

## Message Types

### Content Blocks

```typescript
interface TextContent { type: "text"; text: string; }
interface ImageContent { type: "image"; data: string; mimeType: string; }
interface ThinkingContent { type: "thinking"; thinking: string; }
interface ToolCall { type: "toolCall"; id: string; name: string; arguments: Record<string, any>; }
```

### AgentMessage Union

```typescript
type AgentMessage =
  | UserMessage              // role: "user"
  | AssistantMessage         // role: "assistant", includes usage, stopReason
  | ToolResultMessage        // role: "toolResult", isError flag
  | BashExecutionMessage     // role: "bashExecution", command/output/exitCode
  | CustomMessage            // role: "custom", customType for extensions
  | BranchSummaryMessage     // role: "branchSummary"
  | CompactionSummaryMessage // role: "compactionSummary"
```

## Tree Structure

Entries form a tree via `id`/`parentId`:

```
[user msg] ─── [assistant] ─── [user msg] ─── [assistant] ─┬─ [user msg] ← current leaf
                                                             │
                                                             └─ [branch_summary] ─── [user msg] ← alternate branch
```

The "leaf" pointer tracks the current position. Navigation changes the leaf without creating new files.

## CLI Session Management

```bash
pi -c                           # Continue most recent session
pi -r                           # Browse and select from past sessions
pi --no-session                 # Ephemeral mode (don't save)
pi --session <path|id>          # Use specific session file or partial UUID
pi --fork <path|id>             # Fork into new session
pi --session-dir <dir>          # Custom session storage directory
```

Session dir precedence: `--session-dir` > `PI_CODING_AGENT_SESSION_DIR` env (new in 0.71.0) > `sessionDir` in settings.json.

## Interactive Commands

- `/tree` — Navigate session tree in-place. Search, fold/unfold branches, filter modes
- `/fork` — Create new session file from previous user message
- `/clone` — Duplicate current active branch into new session
- `/compact [prompt]` — Manually compact context
- `/resume` — Pick from previous sessions
- `/new` — Start new session
- `/name <name>` — Set session display name

## Compaction

Auto-compaction triggers when: `contextTokens > contextWindow - reserveTokens` (default reserve: 16384).

### How It Works

1. Walk backwards from newest message until `keepRecentTokens` (default 20000) reached
2. Extract messages from previous boundary to cut point
3. Generate structured summary via LLM
4. Append `CompactionEntry` with summary and `firstKeptEntryId`
5. Session reloads with summary + kept messages

### Summary Format

```markdown
## Goal
[What the user is trying to accomplish]

## Progress
### Done
- [x] Completed tasks

### In Progress
- [ ] Current work

## Key Decisions
- **[Decision]**: Rationale

## Next Steps
1. What should happen next

<read-files>path/to/file.ts</read-files>
<modified-files>path/to/changed.ts</modified-files>
```

### Split Turns

When a single turn exceeds `keepRecentTokens`, compaction cuts mid-turn and generates two summaries (history + turn prefix) that are merged.

Valid cut points: user messages, assistant messages, bashExecution, custom messages. Never at tool results.

## Branch Summarization

When using `/tree` to switch branches, pi offers to summarize the abandoned path:

1. Find common ancestor between old and new positions
2. Collect entries from old leaf back to common ancestor
3. Generate summary with structured format
4. Store as `BranchSummaryEntry` at navigation point

File tracking is cumulative across compactions and branch summaries.

## SessionManager API

```typescript
// Creation
SessionManager.create(cwd, sessionDir?)           // New session
SessionManager.open(path, sessionDir?)            // Open existing
SessionManager.continueRecent(cwd, sessionDir?)   // Continue most recent
SessionManager.inMemory(cwd?)                     // No persistence
SessionManager.forkFrom(sourcePath, targetCwd)    // Fork from another project

// Listing
SessionManager.list(cwd, sessionDir?)             // Sessions for directory
SessionManager.listAll(onProgress?)               // All sessions

// Tree Navigation
sm.getLeafId()              // Current position
sm.getBranch(fromId?)       // Walk from entry to root
sm.getEntries()             // All entries (excludes header)
sm.getPath()                // Path from root to current leaf
sm.getLeafEntry()           // Current leaf entry
sm.getEntry(id)             // Get entry by ID
sm.getTree()                // Full tree structure
sm.getChildren(parentId)    // Direct children
sm.branch(entryId)          // Move leaf to earlier entry
sm.branchWithSummary(id, summary)  // Branch with context summary
sm.createBranchedSession(leafId)   // Extract path to new file

// Labels (new in 0.71.0)
sm.getLabel(id)             // Get label for entry
sm.appendLabelChange(id, "checkpoint")  // Set label

// Appending (all return entry ID)
sm.appendMessage(message)
sm.appendCustomEntry(customType, data?)
sm.appendCompaction(summary, firstKeptEntryId, tokensBefore)
sm.appendLabelChange(targetId, label)

// Context
sm.buildSessionContext()    // Messages, thinkingLevel, model for LLM
```

## Parsing Sessions

```typescript
import { readFileSync } from "fs";

const lines = readFileSync("session.jsonl", "utf8").trim().split("\n");
for (const line of lines) {
  const entry = JSON.parse(line);
  switch (entry.type) {
    case "session": console.log(`Session v${entry.version}: ${entry.id}`); break;
    case "message": console.log(`[${entry.id}] ${entry.message.role}`); break;
    case "compaction": console.log(`Compaction: ${entry.tokensBefore} tokens`); break;
  }
}
```

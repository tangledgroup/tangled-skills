# Session Management - Deep Dive

This reference document explains how pi-coding-agent implements persistent session storage, branching, and context compaction.

## Session Architecture

A session is the fundamental unit of persistence in pi. It represents a conversation with:
- A linear (or branched) history of messages and events
- Metadata (working directory, creation time, model used)
- Automatic persistence to disk after each change

Sessions enable resuming work days later, exploring alternatives via branching, and managing context size through compaction.

## Session Structure

### File Format

Each session is stored as a JSON file with:
```json
{
  "header": {
    "version": 1,
    "cwd": "/path/to/project",
    "createdAt": 1234567890,
    "updatedAt": 1234567890,
    "name": "My Session"
  },
  "entries": [
    // Ordered list of session entries
  ]
}
```

### Entry Types

Sessions contain ordered entries of different types:

**SessionInfoEntry**: Header information (cwd, model, thinking level)

**SessionMessageEntry**: User, assistant, or tool result messages with full content

**FileEntry**: File operations (read, write, edit) with paths and details

**CompactionEntry**: Summary of compacted content with token savings

**BranchSummaryEntry**: Summary when branching from a non-terminal point

**ModelChangeEntry**: Record of model switches during session

**ThinkingLevelChangeEntry**: Record of thinking level adjustments

**CustomEntry**: Extension-defined entry types for custom data

### Entry Metadata

Each entry includes:
- `type`: Entry type identifier
- `timestamp`: When the entry was created
- Type-specific data (message content, file paths, summaries, etc.)

Timestamps enable:
- Proper ordering when multiple agents modify session concurrently
- Finding branch points by time
- Compaction decisions based on age

## Session Manager

The SessionManager class handles all session operations:

### Creating Sessions

```typescript
const sessionId = await sessionManager.createSession({
    cwd: process.cwd(),
    name: "My Task",
    initialEntries: [...] // Optional starting entries
});
```

**What happens**:
1. Generate unique session ID (timestamp + random)
2. Create session directory under `~/.pi/agent/sessions/<id>/`
3. Write initial session file with header and entries
4. Return session ID for future operations

### Loading Sessions

```typescript
const session = await sessionManager.loadSession(sessionId);
```

**What happens**:
1. Read session file from disk
2. Parse JSON into header and entries
3. Run migrations if version is outdated
4. Return session object with methods for modification

### Appending Entries

```typescript
await sessionManager.appendEntries(sessionId, [
    { type: "message", role: "user", content: "Hello", timestamp: Date.now() }
]);
```

**What happens**:
1. Load current session
2. Add new entries to end of array
3. Update header.updatedAt timestamp
4. Write back to disk atomically (write to temp file, then rename)

**Atomic writes** prevent corruption if pi crashes during write.

### Session Switching

```typescript
await sessionManager.switchSession(newSessionId);
```

**What happens**:
1. Save current session state (if any unsaved changes)
2. Load new session from disk
3. Update agent context with new session's messages
4. Return previous session ID (for potential return)

## Branching

Branching creates a new session from a point in an existing session's history.

### Why Branching?

**Explore alternatives**: "What if I tried a different approach?"

**Safe experimentation**: Try risky changes without affecting main session.

**Parallel workstreams**: Work on multiple features simultaneously.

**Recovery point**: Return to a known-good state if things go wrong.

### Branch Creation Process

```typescript
const branchId = await sessionManager.createBranch({
    sourceSessionId: "abc123",
    branchPoint: 45, // Entry index to branch from
    branchName: "Try alternative approach"
});
```

**What happens**:

1. **Load source session**: Read the original session's entries

2. **Copy entries up to branch point**: 
   - Entries 0 through branchPoint are copied to new session
   - These become the new session's history

3. **Generate future summary** (if branching from non-terminal):
   - If branchPoint < last entry, there's "future" content
   - Send future entries to LLM with: "Summarize what happened after this point"
   - Add BranchSummaryEntry with the summary
   - This gives context about what was "left behind"

4. **Create new session**:
   - Generate new session ID
   - Write copied entries + summary to new session file
   - Set header.cwd from source (usually want same working directory)

5. **Return branch ID**: Ready to switch to and continue work

### Branch Summary Example

If branching from entry 45 of 100:
- Entries 0-45: Copied to branch (history up to branch point)
- Entries 46-100: Summarized as "After this point, you implemented feature X, fixed bug Y, and refactored module Z"
- Branch starts with 46 entries (45 original + 1 summary)

The summary helps the agent understand what happened in the "original timeline" after the branch point.

### Switching Between Branches

```typescript
// Save current work, switch to branch
await sessionManager.switchSession(branchId);

// Later, return to original
await sessionManager.switchSession(originalId);
```

Each switch loads the target session's entries into the agent's context. Work continues from that point independently.

## Compaction

Compaction reduces session size by summarizing old content, freeing up tokens in the LLM's context window.

### Why Compaction?

LLMs have limited context windows (e.g., 128K tokens). Long sessions eventually exceed this limit. Compaction:
- Preserves important information (decisions, changes, outcomes)
- Discards details no longer needed (step-by-step reasoning, intermediate attempts)
- Enables indefinitely long conversations

### When to Compact

**Automatic compaction** triggers when:
- Current context tokens > 90% of model's context window
- Safety buffer prevents hitting the hard limit

**Manual compaction** via `/compact` command:
- User explicitly requests compaction
- Optional custom instructions: `/compact "focus on architectural decisions"`

**Overflow recovery**: If LLM rejects due to context overflow:
- Compact immediately
- Retry the same request
- Repeat if necessary (with more aggressive compaction)

### Compaction Process

```typescript
const result = await compact(session.entries, {
    model: currentModel,
    maxTokens: targetTokenCount,
    instructions: "Summarize key decisions and changes"
});
```

**Phase 1: Find cut point**
- Analyze entries from oldest to newest
- Estimate tokens for each entry
- Find where to cut so remaining + summary fits in target
- Prefer cutting at natural boundaries (after compaction, between topics)

**Phase 2: Collect entries for summary**
- Entries before cut point: To be summarized
- Entries after cut point: To be kept as-is

**Phase 3: Generate summary**
- Send entries-to-summarize to LLM with instructions
- Prompt includes: "Summarize this conversation for future reference. Include: key decisions, implemented features, bugs fixed, important context"
- LLM returns condensed summary

**Phase 4: Create compaction entry**
```json
{
    "type": "compaction",
    "timestamp": Date.now(),
    "summary": "LLM-generated summary...",
    "entriesRemoved": 45,
    "tokensSaved": 12000,
    "cutPoint": 45
}
```

**Phase 5: Replace entries**
- New session entries = [compactionEntry, ...entriesAfterCutPoint]
- Old entries are discarded (garbage collected)

**Phase 6: Update session**
- Write new entries to session file
- Update stats (total tokens saved, compaction count)

### Compaction Instructions

Default instructions focus on preserving:
- **Decisions**: What was decided and why
- **Changes**: Files modified, features added, bugs fixed  
- **Context**: Important background information
- **Outcomes**: What worked, what didn't

Custom instructions allow focusing on specific aspects:
- `/compact "focus on API design decisions"`
- `/compact "summarize testing approach and results"`
- `/compact "keep implementation details for auth system"`

### Multiple Compactions

Sessions can be compacted multiple times. Each compaction:
- Creates a new CompactionEntry
- Preserves previous summaries (they're part of kept entries)
- Further reduces token count

Over time, a session might have:
- 1st compaction: Summarizes entries 0-100 into 500 tokens
- 2nd compaction: Summarizes entries 0-150 (including 1st summary) into 800 tokens
- 3rd compaction: Summarizes entries 0-200 (including 2 summaries) into 1200 tokens

Each summary builds on previous ones, preserving long-term history.

### Compaction Quality

Summary quality depends on:
- **Model capability**: Smarter models produce better summaries
- **Instructions**: Clearer instructions = more relevant summaries
- **Entry selection**: Including relevant entries in the summary input

Pi uses the same model for compaction as for the agent (usually). Users can configure a different, potentially cheaper/faster model for compactions.

## Session Statistics

Sessions track usage statistics:

**Token counts**:
- Total input tokens across all messages
- Total output tokens across all responses
- Cache read/write tokens (for providers that support caching)

**Cost tracking**:
- Cost per message based on model pricing
- Total session cost
- Cost broken down by input/output/cache

**Message counts**:
- User messages
- Assistant messages
- Tool calls
- Tool results

**Compaction stats**:
- Number of compactions performed
- Total tokens saved through compaction
- Entries removed vs kept

These stats display in the footer and help users understand session size and cost.

## Session Metadata

### Working Directory

Each session records its working directory (cwd). This is important because:
- File paths are relative to cwd
- Bash commands execute in cwd
- Switching sessions might change cwd

Pi changes to the session's cwd when switching to it.

### Model History

Sessions track which models were used:
- Default model at session start
- Any model changes during the session (via ModelChangeEntry)

This enables:
- Resuming with the same model
- Understanding which model produced which responses
- Cost attribution per model

### Thinking Level History

Similarly, sessions track thinking level changes:
- Default thinking level
- Any adjustments (via ThinkingLevelChangeEntry)

## Session Recovery

### Crash Recovery

If pi crashes mid-operation:
- Session file might be incomplete or corrupted
- On restart, pi validates session files
- Corrupted sessions are recovered from backup or marked as damaged

**Atomic writes** (write to temp, then rename) minimize corruption risk.

### Manual Recovery

Users can manually edit session files (they're JSON):
- Remove problematic entries
- Fix malformed data
- Merge sessions

Pi provides `/export` to export sessions as HTML for external editing/backup.

## Session Listing and Selection

Pi maintains a list of recent sessions:
- Sorted by last updated time
- Shows name, cwd, message count, token usage
- Selectable via `/session` or `/resume` commands

**Session naming**:
- Auto-generated names based on first user message
- User-set names via `/name "My Task"`
- Names appear in session lists for easy identification

## Migration System

Session files have version numbers. When pi updates:
1. Load session file
2. Check version number
3. If outdated, run migration functions
4. Save with new version number

**Migration examples**:
- Add new fields to entries
- Rename entry types
- Transform data formats
- Fix bugs in old data

Migrations ensure old sessions work with new pi versions.

## Concurrent Access

Pi doesn't support multiple agents modifying the same session simultaneously:
- Session files are locked during writes
- Concurrent writes would corrupt data

**Workaround**: Use branching for parallel workstreams, each in its own session.

## Cleanup and Retention

Sessions accumulate over time. Pi provides:
- `/session` command to list all sessions with stats
- Manual deletion via file system
- Future: Automatic retention policies (delete sessions older than X days)

Session directories can grow large with many long-running sessions. Periodic cleanup is recommended.

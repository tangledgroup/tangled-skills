# Session Management: Persistence, Memory, and Resumption

This document covers session persistence, memory distillation, transcript management, resumption workflows, and interactive commands for managing agent sessions.

## Session Storage Structure

Sessions are stored in the workspace root under a hidden directory:

```
your-project/
├── .mini-coding-agent/
│   └── sessions/
│       ├── 20260413-143022-a1b2c3.json
│       ├── 20260413-150045-d4e5f6.json
│       └── 20260414-091233-g7h8i9.json
├── src/
├── tests/
└── README.md
```

Each session file is named with a timestamp and random suffix: `YYYYMMDD-HHMMSS-xxxxxx.json`

## Session JSON Structure

Complete session object saved to disk:

```json
{
  "id": "20260413-143022-a1b2c3",
  "created_at": "2026-04-13T14:30:22+00:00",
  "workspace_root": "/home/user/projects/my-project",
  "history": [
    {
      "role": "user",
      "content": "Create a binary_search.py file with iterative implementation",
      "created_at": "2026-04-13T14:30:25+00:00"
    },
    {
      "role": "tool",
      "name": "write_file",
      "args": {
        "path": "binary_search.py"
      },
      "content": "wrote binary_search.py (847 chars)",
      "created_at": "2026-04-13T14:30:28+00:00"
    },
    {
      "role": "user",
      "content": "Add unit tests for the binary search function",
      "created_at": "2026-04-13T14:32:15+00:00"
    },
    {
      "role": "tool",
      "name": "write_file",
      "args": {
        "path": "test_binary_search.py"
      },
      "content": "wrote test_binary_search.py (1243 chars)",
      "created_at": "2026-04-13T14:32:20+00:00"
    },
    {
      "role": "assistant",
      "content": "I've created both files. The implementation uses an iterative approach...",
      "created_at": "2026-04-13T14:32:22+00:00"
    }
  ],
  "memory": {
    "task": "Create a binary_search.py file with iterative implementation",
    "files": [
      "binary_search.py",
      "test_binary_search.py"
    ],
    "notes": [
      "write_file: wrote binary_search.py (847 chars)",
      "write_file: wrote test_binary_search.py (1243 chars)",
      "read_file: binary_search.py lines 1-25",
      "run_shell: exit_code: 0, 5 passed in 0.12s"
    ]
  }
}
```

## Session Lifecycle

### Session Creation

When starting a new session:

```python
session = {
    "id": datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6],
    "created_at": now(),  # ISO format UTC timestamp
    "workspace_root": workspace.repo_root,
    "history": [],
    "memory": {
        "task": "",
        "files": [],
        "notes": []
    }
}
```

The session ID combines:
- **Timestamp**: `20260413-143022` (YYYYMMDD-HHMMSS) — for chronological ordering and identification
- **Random suffix**: `a1b2c3` (6 hex characters from UUID) — for uniqueness when multiple sessions start at the same second

### Session Persistence

Sessions are saved after **every turn** (user message, tool call, or final answer):

```python
def record(self, item):
    self.session["history"].append(item)
    self.session_path = self.session_store.save(self.session)
```

This ensures:
- No data loss if agent crashes mid-task
- Session can be resumed from any point in the conversation
- Transcript is always up-to-date on disk for inspection

### Session Loading

To resume a session:

```python
@classmethod
def from_session(cls, model_client, workspace, session_store, session_id, **kwargs):
    session = session_store.load(session_id)
    return cls(
        model_client=model_client,
        workspace=workspace,
        session_store=session_store,
        session=session,
        **kwargs
    )
```

The loaded session includes:
- Full history transcript with timestamps
- Distilled memory (task summary, tracked files, operation notes)
- Original workspace root path

## Memory Distillation

Memory is a compact, distilled representation of the session state that stays bounded in size. It survives across turns even as the full history grows and gets compressed.

### Memory Structure

```python
memory = {
    "task": str,      # First user message (truncated to 300 chars)
    "files": [str],   # LRU list of tracked files (max 8)
    "notes": [str]    # LRU list of operation notes (max 5)
}
```

### Task Extraction

The first user message becomes the session task:

```python
if not memory["task"]:
    memory["task"] = clip(user_message.strip(), 300)
```

This provides a persistent summary of what the session is about, even after dozens of turns. The task remains visible in `/memory` output throughout the session.

### File Tracking (LRU List)

Files are automatically tracked when read, written, or patched:

```python
def note_tool(self, name, args, result):
    if name in {"read_file", "write_file", "patch_file"} and "path" in args:
        self.remember(memory["files"], str(args["path"]), limit=8)
```

The `remember()` function implements **LRU (Least Recently Used)** behavior:

```python
@staticmethod
def remember(bucket, item, limit):
    if not item:
        return
    # Move to end if already exists (most recent)
    if item in bucket:
        bucket.remove(item)
    # Append new item
    bucket.append(item)
    # Trim to limit (drop oldest from front)
    del bucket[:-limit]
```

**Example progression:**
```python
# After reading file A
files = ["src/main.py"]

# After reading file B  
files = ["src/main.py", "src/utils.py"]

# After reading file A again (moved to end, most recent)
files = ["src/utils.py", "src/main.py"]

# After 8 files, oldest is dropped when new one added
```

### Note Generation

Each tool operation generates a compact note:

```python
note = f"{name}: {clip(str(result).replace('\n', ' '), 220)}"
self.remember(memory["notes"], note, limit=5)
```

Notes are truncated to 220 characters and newlines are replaced with spaces for compactness. The LRU list keeps only the 5 most recent notes.

**Examples:**
```
write_file: wrote binary_search.py (847 chars)
read_file: # src/main.py     1: def main():     2:     pass
run_shell: exit_code: 0 stdout: 5 passed in 0.12s stderr: (empty)
patch_file: patched config.json
search: src/main.py:12:def binary_search(...)
```

### Final Answer Notes

Final answers also generate notes, capturing the agent's conclusion in memory:

```python
final = (payload or raw).strip()
self.remember(memory["notes"], clip(final, 220), 5)
```

## Transcript Management

The history transcript contains the full conversation but is compressed for prompt efficiency. The `history_text()` method handles all compression logic.

### History Compression Strategy

```python
def history_text(self):
    history = self.session["history"]
    if not history:
        return "- empty"

    lines = []
    seen_reads = set()
    recent_start = max(0, len(history) - 6)  # Last 6 turns are "recent"
    
    for index, item in enumerate(history):
        recent = index >= recent_start
        
        # Skip duplicate reads in older history
        if item["role"] == "tool" and item["name"] == "read_file" and not recent:
            path = str(item["args"].get("path", ""))
            if path in seen_reads:
                continue
            seen_reads.add(path)
        
        # Apply different compression limits based on recency
        if item["role"] == "tool":
            limit = 900 if recent else 180
            lines.append(f"[tool:{item['name']}] {json.dumps(item['args'], sort_keys=True)}")
            lines.append(clip(item["content"], limit))
        else:
            limit = 900 if recent else 220
            lines.append(f"[{item['role']}] {clip(item['content'], limit)}")
    
    # Final cap on entire history text
    return clip("\n".join(lines), MAX_HISTORY)  # MAX_HISTORY = 12000
```

### Compression Levels

| Turn Age | Tool Output Limit | Message Limit | Dedup Reads |
|----------|------------------|---------------|-------------|
| Recent (last 6) | 900 chars | 900 chars | No |
| Older | 180 chars | 220 chars | Yes (skip duplicates) |
| **Total history** | — | **12,000 chars** | — |

### Read Deduplication

Repeated reads of the same file are suppressed in older history to prevent transcript bloat:

```python
# Write/patch operations clear the "seen" status for that file
if item["role"] == "tool" and item["name"] in ("write_file", "patch_file"):
    path = str(item["args"].get("path", ""))
    seen_reads.discard(path)
```

**Example with deduplication:**
```
Turn 3: read_file src/main.py (included)
Turn 5: read_file src/main.py (included, first repeat)
Turn 7: read_file src/main.py (skipped, duplicate in older history)
Turn 8: patch_file src/main.py (clears "seen" for this file)
Turn 9: read_file src/main.py (included again, file was modified)
```

### History Format in Prompts

Compressed history appears as:

```
Transcript:
[user] Create a binary_search.py file with...
[tool:write_file] {"path": "binary_search.py"}
wrote binary_search.py (847 chars)
[user] Add validation for unsorted input
[tool:patch_file] {"new_text": "...", "old_text": "...", "path": "binary_search.py"}
patched binary_search.py
[assistant] I've updated the implementation to...
```

## Resumption Workflows

### Resume Latest Session

```bash
python mini_coding_agent.py --resume latest
```

Finds the most recently modified session file (by `st_mtime`) and loads it.

### Resume Specific Session

```bash
python mini_coding_agent.py --resume 20260413-143022-a1b2c3
```

Loads a specific session by ID from the filename.

### List Available Sessions

```bash
ls -lt .mini-coding-agent/sessions/
```

Shows all sessions sorted by modification time:
```
-rw-r--r-- 1 user user 12345 Apr 13 15:00 20260413-143022-a1b2c3.json
-rw-r--r-- 1 user user  8765 Apr 13 10:22 20260413-102211-d4e5f6.json
```

### Resumption Behavior

When resuming a session:
1. Session history and memory are loaded from disk
2. **Workspace context is rebuilt** (git status, recent commits, project docs may have changed)
3. Agent continues with full conversation history preserved
4. New turns append to existing history

**Important:** Workspace context is always fresh even in resumed sessions — git state and project docs are re-collected at the start of each new session (including resumed ones).

## Interactive Commands

Slash commands are handled directly by the agent REPL and **not sent to the model**:

### /help

Show available commands:
```
mini-coding-agent> /help

Commands:
/help    Show this help message.
/memory  Show the agent's distilled working memory.
/session Show the path to the saved session file.
/reset   Clear the current session history and memory.
/exit    Exit the agent.
```

### /memory

Display current distilled memory:
```
mini-coding-agent> /memory

Memory:
- task: Create a binary search implementation with tests
- files: binary_search.py, test_binary_search.py
- notes:
  - write_file: wrote binary_search.py (847 chars)
  - write_file: wrote test_binary_search.py (1243 chars)
  - run_shell: exit_code: 0 stdout: 5 passed in 0.12s
```

### /session

Show path to current session file:
```
mini-coding-agent> /session

/home/user/projects/my-project/.mini-coding-agent/sessions/20260413-143022-a1b2c3.json
```

Useful for:
- Manually inspecting session JSON
- Backing up sessions
- Debugging session state

### /reset

Clear current session history and memory:
```
mini-coding-agent> /reset

session reset
```

This:
- Clears `history` array (full transcript)
- Resets `memory` to empty defaults (task, files, notes)
- Keeps the same session ID
- Saves cleared state to disk
- User stays in the REPL for new interactions

Useful for starting fresh without exiting the agent.

### /exit and /quit

Exit the interactive session:
```
mini-coding-agent> /exit
# or:
mini-coding-agent> /quit
```

Both `/exit` and `/quit` are aliases that cleanly terminate the agent. The session is saved to disk before exit so it can be resumed later.

## Session Management Best Practices

### When to Resume

| Scenario | Action |
|----------|--------|
| Agent crashed or terminal closed | `--resume latest` |
| Multi-day project, pick up where left off | `--resume latest` |
| Specific session needed | `--resume <session_id>` |
| Iterative development building on previous work | `--resume latest` |

### When to Start Fresh

| Scenario | Action |
|----------|--------|
| Different task (unrelated feature) | New session (no `--resume`) |
| Context pollution (too much irrelevant history) | `/reset` or new session |
| Clean slate needed (previous attempts went wrong) | `/reset` or new session |

### Manual Session Backup

Before major changes, back up the current session:
```bash
cp .mini-coding-agent/sessions/20260413-143022-a1b2c3.json \
   ~/backups/session-before-refactor.json
```

### Session Cleanup

Old sessions accumulate over time. Clean up periodically:
```bash
# Keep only last 10 sessions
cd .mini-coding-agent/sessions/
ls -t *.json | tail -n +11 | xargs rm -f
```

## Debugging Session Issues

### Corrupted Session

If a session file is corrupted:
```bash
# Check JSON validity
python -m json.tool .mini-coding-agent/sessions/20260413-143022-a1b2c3.json

# If invalid, remove and start fresh
rm .mini-coding-agent/sessions/20260413-143022-a1b2c3.json
```

### Memory Not Updating

If memory isn't tracking files:
- Check that tool calls are succeeding (not failing validation)
- Verify session is being saved (`/session` path should update mtime after each turn)
- Inspect raw session JSON for correct memory structure

### History Too Long

If prompts are getting truncated due to long history:
- Use `/reset` to clear history and start fresh
- Start a new session with focused scope
- Consider breaking large tasks into multiple separate sessions

## Programmatic Session Access

For advanced use cases, sessions can be accessed programmatically:

```python
from pathlib import Path
import json

# Load session
session_path = Path(".mini-coding-agent/sessions/20260413-143022-a1b2c3.json")
session = json.loads(session_path.read_text())

# Inspect history
for turn in session["history"]:
    role = turn.get("role", "?")
    tool_name = turn.get("name", "")
    content_preview = turn.get("content", "")[:100]
    print(f"{role}:{tool_name} - {content_preview}...")

# Check memory
print("Task:", session["memory"]["task"])
print("Files:", session["memory"]["files"])
```

This enables custom tooling for session analysis, backup automation, or migration between projects.

## Test Coverage

The project includes pytest tests in `tests/test_mini_coding_agent.py` that verify:
- Tool execution and final answer generation
- Retry behavior after malformed model output
- Session persistence and loading
- Workspace context building
- File path validation and security checks

Run tests with:
```bash
cd mini-coding-agent
uv run pytest
# or without uv:
python -m pytest tests/
```

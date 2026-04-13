# Core Concepts: Six Architecture Components

This document explains the six practical building blocks that organize the mini-coding-agent architecture. Each component addresses a specific challenge in building reliable coding agents.

## Component 1: Live Repo Context (WorkspaceContext)

The agent collects stable workspace facts upfront to provide consistent context for all model interactions.

### What It Collects

```python
class WorkspaceContext:
    cwd              # Current working directory
    repo_root        # Git repository root (or cwd if not a git repo)
    branch           # Current git branch name
    default_branch   # Default branch (e.g., "main" or "origin/main")
    status           # Git status output (staged/unstaged changes)
    recent_commits   # Last 5 commit messages with hashes
    project_docs     # Snippets from key documentation files
```

### Documentation Files Indexed

The agent automatically reads and indexes these files (up to 1200 chars each):
- `AGENTS.md` - Agent-specific instructions
- `README.md` - Project documentation
- `pyproject.toml` - Python project configuration
- `package.json` - Node.js project configuration

### Implementation Details

```python
# Build workspace context from a directory
workspace = WorkspaceContext.build(cwd="/path/to/project")

# Convert to text for prompt inclusion
context_text = workspace.text()
```

The `text()` method formats all collected data into a structured string that becomes part of every model prompt, ensuring the agent always knows:
- Where it is in the filesystem
- What branch it's working on
- What recent changes were made
- Key project documentation

### Git Fallback Behavior

If git commands fail (not a repository or git unavailable):
- `repo_root` defaults to `cwd`
- `branch` shows "-" 
- `status` shows "clean"
- `recent_commits` shows "- none"

## Component 2: Prompt Shape and Cache Reuse

The prompt is structured to enable efficient caching while maintaining context across turns.

### Prompt Structure

```
[prefix - static for entire session]
  ├── System instructions and rules
  ├── Tool definitions with schemas
  ├── Valid response examples
  └── Workspace context ( Component 1 )

[memory_text - changes occasionally]
  ├── Current task summary
  ├── Tracked files list
  └── Recent notes (up to 5)

[history_text - grows each turn]
  └── Compressed transcript of recent turns

[current user request - changes each turn]
  └── User's latest message
```

### Why This Structure Matters

1. **Static prefix can be cached**: The tool definitions, rules, and workspace context rarely change, so they can be cached across multiple model calls
2. **Separate memory from history**: Memory is distilled and compact (task, files, notes), while history contains full turn details
3. **Bounded growth**: History is compressed and truncated to prevent context overflow

### The Prefix Content

The prefix includes:
- Agent identity: "You are Mini-Coding-Agent, a small local coding agent running through Ollama"
- Response format rules (use `<tool>` or `<final>` tags)
- Tool definitions with schemas and risk flags
- Example tool calls in both JSON and XML formats
- Workspace context from Component 1

### Memory Text Format

```
Memory:
- task: Create a binary_search.py file
- files: binary_search.py, test_binary_search.py
- notes:
  - read_file: function implemented with while loop
  - write_file: wrote test_binary_search.py (847 chars)
  - ...
```

Memory is automatically updated when tools are used and stays compact (limited to 8 files, 5 notes).

## Component 3: Structured Tools, Validation, and Permissions

The agent works through named tools with checked inputs instead of free-form arbitrary actions.

### Tool Schema Format

Each tool has a schema that defines expected arguments:

```python
{
    "name": "read_file",
    "schema": {
        "path": "str",        # Required string argument
        "start": "int=1",     # Optional int, default 1
        "end": "int=200"      # Optional int, default 200
    },
    "risky": False,           # No approval needed
    "description": "Read a UTF-8 file by line range."
}
```

### Risk Classification

Tools are classified as risky or safe:

**Safe tools (no approval needed):**
- `list_files` - List directory contents
- `read_file` - Read file contents
- `search` - Search for patterns in files

**Risky tools (require approval):**
- `run_shell` - Execute shell commands
- `write_file` - Create or modify files
- `patch_file` - Replace text in existing files

### Validation Rules

Each tool validates its arguments before execution:

```python
# read_file validation
- path must exist and be a file
- start >= 1
- end >= start

# write_file validation  
- path must not be a directory
- content argument must be present
- path must be within workspace root

# patch_file validation
- path must exist and be a file
- old_text must not be empty
- new_text must be present
- old_text must occur exactly once in file
```

### Path Security

All file paths are validated to prevent escaping the workspace:

```python
def path(self, raw_path):
    # Convert relative to absolute path within repo_root
    path = Path(raw_path) if Path(raw_path).is_absolute() else self.root / raw_path
    resolved = path.resolve()
    
    # Verify path is within workspace root
    if not self.path_is_within_root(resolved):
        raise ValueError(f"path escapes workspace: {raw_path}")
    return resolved
```

This prevents the agent from reading or writing files outside the designated workspace.

## Component 4: Context Reduction and Output Management

Long outputs are clipped, repeated reads are deduplicated, and older transcript entries are compressed to keep prompt size under control.

### Output Truncation

Tool outputs are limited to prevent context overflow:

```python
MAX_TOOL_OUTPUT = 4000  # characters

def clip(text, limit=MAX_TOOL_OUTPUT):
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...[truncated {len(text) - limit} chars]"
```

### History Compression

The transcript is compressed differently for recent vs. older turns:

```python
def history_text(self):
    # Recent turns (last 6): full detail
    # Older turns: compressed
    
    for item in history:
        if item["role"] == "tool":
            limit = 900 if recent else 180  # Compress old tool outputs
        else:
            limit = 900 if recent else 220  # Compress old messages
    
    # Final limit on entire history
    return clip(full_history_text, MAX_HISTORY)  # MAX_HISTORY = 12000
```

### Read Deduplication

Repeated reads of the same file are suppressed in older history:

```python
seen_reads = set()
for item in history:
    if item["role"] == "tool" and item["name"] == "read_file" and not recent:
        path = item["args"]["path"]
        if path in seen_reads:
            continue  # Skip duplicate reads
        seen_reads.add(path)
    
    # Write/patch operations clear the "seen" status for that file
    if item["name"] in ("write_file", "patch_file"):
        seen_reads.discard(item["args"]["path"])
```

This prevents the transcript from filling up with repeated reads of unchanged files.

### Repeated Tool Call Prevention

The agent detects and blocks identical consecutive tool calls:

```python
def repeated_tool_call(self, name, args):
    recent_tools = history[-2:]  # Last 2 tool calls
    return all(t["name"] == name and t["args"] == args for t in recent_tools)
```

If detected, the agent returns an error prompting the model to try a different approach.

## Component 5: Transcripts, Memory, and Resumption

The runtime keeps both a full durable transcript and a smaller working memory so sessions can be resumed while preserving important state.

### Session Structure

```python
session = {
    "id": "20260413-143022-a1b2c3",  # timestamp + random suffix
    "created_at": "2026-04-13T14:30:22+00:00",
    "workspace_root": "/path/to/project",
    "history": [  # Full transcript
        {
            "role": "user",
            "content": "Create a binary search function",
            "created_at": "2026-04-13T14:30:25+00:00"
        },
        {
            "role": "tool",
            "name": "write_file",
            "args": {"path": "binary_search.py"},
            "content": "wrote binary_search.py (342 chars)",
            "created_at": "2026-04-13T14:30:28+00:00"
        },
        # ... more turns
    ],
    "memory": {  # Distilled working memory
        "task": "Create a binary search function",
        "files": ["binary_search.py"],
        "notes": [
            "write_file: wrote binary_search.py (342 chars)",
            # ... up to 5 notes
        ]
    }
}
```

### Session Persistence

Sessions are saved to JSON files after each turn:

```
.mini-coding-agent/sessions/
├── 20260413-143022-a1b2c3.json
├── 20260413-150045-d4e5f6.json
└── 20260414-091233-g7h8i9.json
```

### Memory Distillation

Memory is automatically updated when tools are used:

```python
def note_tool(self, name, args, result):
    # Track files that were read/written/patched
    if name in {"read_file", "write_file", "patch_file"} and "path" in args:
        self.remember(memory["files"], str(args["path"]), limit=8)
    
    # Add compact note about the operation
    note = f"{name}: {clip(str(result), 220)}"
    self.remember(memory["notes"], note, limit=5)
```

The `remember()` function maintains LRU-style lists:
- If item already exists, move it to end (most recent)
- Append new items
- Trim to limit (8 files, 5 notes)

### Task Extraction

The first user message becomes the session task (truncated to 300 chars):

```python
if not memory["task"]:
    memory["task"] = clip(user_message.strip(), 300)
```

This provides a persistent summary of what the session is about.

## Component 6: Delegation and Bounded Subagents

Scoped subtasks can be delegated to helper agents that inherit enough context to help but operate within limits.

### When Delegation Is Available

The `delegate` tool is only available if the current agent hasn't reached max depth:

```python
if self.depth < self.max_depth:
    tools["delegate"] = {
        "schema": {"task": "str", "max_steps": "int=3"},
        "risky": False,
        "description": "Ask a bounded read-only child agent to investigate.",
        "run": self.tool_delegate
    }
```

Default configuration: `max_depth=1`, so the root agent can create one level of subagents.

### Subagent Creation

When delegation is invoked:

```python
def tool_delegate(self, args):
    child = MiniAgent(
        model_client=self.model_client,      # Same model
        workspace=self.workspace,            # Same workspace context
        session_store=self.session_store,    # Separate session
        approval_policy="never",             # No risky operations
        max_steps=int(args.get("max_steps", 3)),  # Limited steps
        max_new_tokens=self.max_new_tokens,
        depth=self.depth + 1,                # Incremented depth
        max_depth=self.max_depth,            # Same limit
        read_only=True                       # Cannot modify files
    )
    
    # Inherit context from parent
    child.session["memory"]["task"] = task
    child.session["memory"]["notes"] = [clip(self.history_text(), 300)]
    
    return "delegate_result:\n" + child.ask(task)
```

### Subagent Restrictions

Subagents are bounded by:
1. **Read-only mode**: Cannot use `write_file`, `patch_file`, or `run_shell` (approval always denied)
2. **Limited steps**: Default 3 steps (configurable via `max_steps` argument)
3. **No further delegation**: `depth + 1 >= max_depth` prevents nested subagents
4. **Inherited context**: Gets compressed parent history as notes for context

### Use Cases for Delegation

- Investigate a specific file or directory without modifying anything
- Research code patterns before making changes in the parent agent
- Parallel exploration of different approaches (manually invoked)
- Scoped fact-finding missions with limited context inheritance

## How Components Work Together

### Typical Request Flow

1. **User sends request** → `ask(user_message)`
2. **Component 5**: Record user message in history, extract task if new
3. **Component 2**: Build prompt (prefix + memory + history + request)
4. **Model generates response** → `<tool>...</tool>` or `<final>...</final>`
5. **Parse response** → Extract tool name and arguments
6. **Component 3**: Validate tool arguments, check for repeats
7. **Component 3**: Request approval if risky (unless auto mode)
8. **Execute tool** → Get result
9. **Component 4**: Clip result if too long
10. **Component 5**: Record tool call and result in history
11. **Component 5**: Update memory (track files, add notes)
12. **Component 5**: Save session to disk
13. **Loop** → If not `<final>`, go back to step 3 with tool result

### Session Resumption Flow

1. **User requests resume** → `--resume latest` or `--resume <session_id>`
2. **Component 5**: Load session JSON from `.mini-coding-agent/sessions/`
3. **Component 1**: Rebuild workspace context (may have changed)
4. **Component 2**: Rebuild prefix with updated workspace context
5. **Continue** → Agent continues with preserved history and memory

This architecture enables reliable, safe, and resumable coding agent operations while keeping context manageable and maintaining human oversight through approval gates.

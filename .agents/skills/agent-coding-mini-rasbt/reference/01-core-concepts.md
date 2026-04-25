# Core Concepts: Six Architecture Components

This document explains the six practical building blocks that organize the mini-coding-agent architecture. These components demonstrate how a **coding harness** — the software scaffold around an LLM — dramatically improves coding capabilities beyond plain chat interfaces.

## The Agent Loop: Observe → Inspect → Choose → Act

Every coding agent, from this minimal framework to Claude Code or Codex CLI, follows the same fundamental loop:

```
observe → inspect → choose → act → (loop back)
   ↑                                    │
   └─────────────────────────────────────┘
```

| Phase | What Happens | Harness Responsibility |
|-------|-------------|----------------------|
| **Observe** | Collect information from the environment | File reads, git status, test output capture |
| **Inspect** | Analyze that information to understand state | Context reduction, memory distillation |
| **Choose** | Select next action based on goal and state | Tool selection, prompt assembly |
| **Act** | Execute a tool call | Validation, approval gates, execution |

The harness provides the plumbing that makes this loop efficient: stable prompt caching, context management, bounded tools, and session persistence.

---

## Component 1: Live Repo Context (WorkspaceContext)

This is arguably the most important component. When a user says "fix the tests" or "implement xyz," the model needs to know whether it's inside a Git repo, what branch it's on, which project documents might contain instructions, and so on. These details often change and directly affect what the correct action is.

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

| File | Purpose |
|------|---------|
| `AGENTS.md` | Agent-specific instructions for the project |
| `README.md` | Project documentation and setup instructions |
| `pyproject.toml` | Python project configuration, dependencies |
| `package.json` | Node.js project configuration, dependencies |

### Why This Matters

"Fix the tests" is not a self-contained instruction. If the agent sees `AGENTS.md`, it may learn which test command to run (`uv run pytest` vs `python -m pytest`). If it knows the repo root and layout, it can look in the right places instead of guessing. The git branch, status, and recent commits also provide context about what changes are currently in progress.

### Implementation Details

```python
# Build workspace context from a directory
workspace = WorkspaceContext.build(cwd="/path/to/project")

# Convert to text for prompt inclusion
context_text = workspace.text()
```

The `text()` method formats all collected data into a structured string:

```
Workspace:
- cwd: /home/user/my-project
- repo_root: /home/user/my-project
- branch: feature/auth
- default_branch: main
- status:
 M src/auth.py
?? tests/test_auth.py
- recent_commits:
- a1b2c3d Add login endpoint
- e4f5g6h Fix token refresh
...
- project_docs:
- README.md
  # My Project
  ...
```

### Git Fallback Behavior

If git commands fail (not a repository or git unavailable):
- `repo_root` defaults to `cwd`
- `branch` shows "-"
- `status` shows "clean"
- `recent_commits` shows "- none"

---

## Component 2: Prompt Shape and Cache Reuse

Coding sessions are repetitive — the agent rules stay the same, tool descriptions stay the same, and even the workspace summary usually stays mostly the same. The main things that change each turn are: the latest user request, the recent transcript, and the short-term memory.

### Why Caching Matters

A "smart" runtime doesn't rebuild everything as one giant undifferentiated prompt on every turn. Instead, it separates the prompt into stable and changing parts:

```
Stable prefix (cached across turns):
├── System instructions and rules
├── Tool definitions with schemas
├── Valid response examples
└── Workspace context

Changing session state (updated each turn):
├── Short-term memory (distilled task, files, notes)
├── Recent transcript (compressed history)
└── Newest user request
```

### Prompt Structure

The final prompt assembled each turn:

```python
def prompt(self, user_message):
    return "\n\n".join([
        self.prefix,              # Static: rules + tools + workspace
        self.memory_text(),       # Changes occasionally (task/files/notes)
        "Transcript:\n" + self.history_text(),  # Grows each turn
        "Current user request:\n" + user_message,
    ])
```

### The Prefix Content

The prefix includes:
- **Agent identity**: "You are Mini-Coding-Agent, a small local coding agent running through Ollama"
- **Response format rules**: Use `<tool>` or `<final>` tags, return exactly one per response
- **Tool definitions**: All available tools with schemas and risk flags
- **Example tool calls**: Both JSON and XML format examples
- **Workspace context**: From Component 1 (repo root, branch, status, docs)

### Memory Text Format

```
Memory:
- task: Create a binary_search.py file
- files: binary_search.py, test_binary_search.py
- notes:
  - read_file: function implemented with while loop
  - write_file: wrote test_binary_search.py (847 chars)
```

Memory is automatically updated when tools are used and stays compact (limited to 8 files, 5 notes). This distilled memory persists across turns even as the full history grows.

---

## Component 3: Structured Tools, Validation, and Permissions

Tool access is where it starts to feel less like chat and more like an agent. A plain model can suggest commands in prose, but an LLM in a coding harness should do something narrower and more useful — actually execute the command and retrieve results.

### The Tool-Use Flow

```
Model emits structured action
        ↓
Harness validates it (known tool? valid args? in workspace?)
        ↓
Optionally asks for user approval (if risky)
        ↓
Executes the tool
        ↓
Feeds bounded result back into the loop
```

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

| Category | Tools | Approval Required |
|----------|-------|-------------------|
| **Safe** | `list_files`, `read_file`, `search` | No |
| **Risky** | `run_shell`, `write_file`, `patch_file` | Yes (unless `--approval auto`) |

### Validation Rules

Each tool validates its arguments before execution. The harness runs programmatic checks:
- Is this a known tool?
- Are the arguments valid and properly typed?
- Does this need user approval?
- Is the requested path even inside the workspace?

Only after all checks pass does anything actually run. This improves reliability because the model doesn't execute arbitrary commands — only pre-defined tools with checked inputs.

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

---

## Component 4: Context Reduction and Output Management

Long outputs must be clipped, repeated reads deduplicated, and older transcript entries compressed to keep prompt size under control. Without these mechanisms, sessions would quickly exhaust context windows.

### Output Truncation

Tool outputs are limited to prevent context overflow:

```python
MAX_TOOL_OUTPUT = 4000  # characters per tool output

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
    # Older turns: heavily compressed
    
    for item in history:
        if item["role"] == "tool":
            limit = 900 if recent else 180  # Compress old tool outputs
        else:
            limit = 900 if recent else 220  # Compress old messages
    
    # Final limit on entire history
    return clip(full_history_text, MAX_HISTORY)  # MAX_HISTORY = 12000
```

| Turn Age | Tool Output Limit | Message Limit |
|----------|------------------|---------------|
| Recent (last 6) | 900 chars | 900 chars |
| Older | 180 chars | 220 chars |
| Total history | — | 12,000 chars |

### Read Deduplication

Repeated reads of the same file are suppressed in older history:

```python
seen_reads = set()
for item in history:
    if item["role"] == "tool" and item["name"] == "read_file" and not recent:
        path = item["args"]["path"]
        if path in seen_reads:
            continue  # Skip duplicate read
        seen_reads.add(path)
    
    # Write/patch operations clear the "seen" status for that file
    if item["name"] in ("write_file", "patch_file"):
        seen_reads.discard(item["args"]["path"])
```

**Example:**
```
Turn 3: read_file src/main.py (included)
Turn 5: read_file src/main.py (included, first repeat)
Turn 7: read_file src/main.py (skipped, duplicate in older history)
Turn 8: patch_file src/main.py (clears "seen" for this file)
Turn 9: read_file src/main.py (included again, file changed)
```

### Repeated Tool Call Prevention

The agent detects and blocks identical consecutive tool calls:

```python
def repeated_tool_call(self, name, args):
    recent_tools = history[-2:]  # Last 2 tool calls
    return all(t["name"] == name and t["args"] == args for t in recent_tools)
```

If detected, the agent returns an error prompting the model to try a different approach.

---

## Component 5: Transcripts, Memory, and Resumption

The runtime keeps both a full durable transcript and a smaller working memory so sessions can be resumed while preserving important state.

### Session Structure

```python
session = {
    "id": "20260413-143022-a1b2c3",  # timestamp + random suffix
    "created_at": "2026-04-13T14:30:22+00:00",
    "workspace_root": "/path/to/project",
    "history": [  # Full transcript of all turns
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
    ],
    "memory": {  # Distilled working memory (compact)
        "task": "Create a binary search function",
        "files": ["binary_search.py"],
        "notes": [
            "write_file: wrote binary_search.py (342 chars)",
        ]
    }
}
```

### Session Persistence

Sessions are saved to JSON files after **every turn**:

```
your-project/
├── .mini-coding-agent/
│   └── sessions/
│       ├── 20260413-143022-a1b2c3.json
│       ├── 20260413-150045-d4e5f6.json
│       └── 20260414-091233-g7h8i9.json
```

This ensures no data loss if the agent crashes and sessions can be resumed from any point.

### Memory Distillation

Memory is automatically updated when tools are used:

```python
def note_tool(self, name, args, result):
    # Track files that were read/written/patched (LRU, max 8)
    if name in {"read_file", "write_file", "patch_file"} and "path" in args:
        self.remember(memory["files"], str(args["path"]), limit=8)
    
    # Add compact note about the operation (LRU, max 5)
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

---

## Component 6: Delegation and Bounded Subagents

Once an agent has tools and state, delegation allows parallelizing work into subtasks via subagents. The main agent can split off side tasks (which file defines a symbol, what a config says) into bounded subtasks instead of carrying every thread at once.

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
        model_client=self.model_client,      # Same model backend
        workspace=self.workspace,            # Same workspace context
        session_store=self.session_store,    # Separate session storage
        approval_policy="never",             # No risky operations allowed
        max_steps=int(args.get("max_steps", 3)),  # Limited steps
        max_new_tokens=self.max_new_tokens,
        depth=self.depth + 1,                # Incremented depth
        max_depth=self.max_depth,            # Same limit
        read_only=True                       # Cannot modify files
    )
    
    # Inherit context from parent (compressed history)
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

### Comparison with Claude Code and Codex

| Feature | Mini-Coding-Agent | Claude Code | Codex CLI |
|---------|------------------|-------------|-----------|
| Subagent mode | Read-only only | Configurable | Inherits sandbox/approval |
| Depth limit | 1 level | Multi-level | Multi-level |
| Context inheritance | Compressed history | Full context | Full context |

The mini-agent's approach is simpler but safer — subagents can investigate without modifying files. More sophisticated harnesses like Codex allow subagents to inherit the main agent's sandbox, with boundaries around task scoping and context rather than strict read-only mode.

---

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

### Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                   Coding Harness                     │
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐ │
│  │ Component │   │Component │   │  Component       │ │
│  │    1      │   │    2     │   │     3            │ │
│  │Live Repo  │   │Prompt    │   │Structured Tools, │ │
│  │ Context   │   │Shape &   │   │Validation &      │ │
│  │           │   │Cache Reuse│  │Permissions       │ │
│  └─────┬─────┘   └────┬─────┘   └────────┬─────────┘ │
│        │              │                   │           │
│        ▼              ▼                   ▼           │
│  ┌──────────────────────────────────────────────────┐│
│  │              Stable Prompt Prefix                ││
│  │  (rules + tools + workspace context)             ││
│  └──────────────────────────────────────────────────┘│
│                          ▲                           │
│  ┌──────────┐   ┌────────┴───────┐   ┌──────────┐  │
│  │Component │   │   Component    │   │Component │  │
│  │    6     │   │       4        │   │    5     │  │
│  │Delegation│   │Context Reduction│  │Session   │  │
│  │& Subagents│  │& Output Mgmt   │  │Memory &  │  │
│  │          │   │                │  │Resumption│  │
│  └──────────┘   └────────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
```

This architecture enables reliable, safe, and resumable coding agent operations while keeping context manageable and maintaining human oversight through approval gates.

# Six Components Deep Dive

## Component 1: Live Repo Context

The `WorkspaceContext` class collects stable workspace facts at agent startup. These facts are injected into every prompt so the model always knows what it is working with.

### What It Collects

- **cwd** — the current working directory (absolute path)
- **repo_root** — the git repository root, discovered via `git rev-parse --show-toplevel`
- **branch** — current branch name from `git branch --show-current`
- **default_branch** — default branch from `git symbolic-ref --short refs/remotes/origin/HEAD`
- **status** — short git status from `git status --short` (clipped to 1500 chars)
- **recent_commits** — last 5 commits from `git log --oneline -5`
- **project_docs** — content of key documentation files, clipped to 1200 chars each

### Document Files Scanned

The agent reads these files if they exist, checking both the repo root and the cwd:

- `AGENTS.md`
- `README.md`
- `pyproject.toml`
- `package.json`

If a file exists at both locations, only the first found is included. Documents are stored keyed by their path relative to the repo root.

### Implementation Pattern

```python
class WorkspaceContext:
    def __init__(self, cwd, repo_root, branch, default_branch, status, recent_commits, project_docs):
        self.cwd = cwd
        self.repo_root = repo_root
        # ... store all fields

    @classmethod
    def build(cls, cwd):
        # Run git commands, read docs, return instance
        pass

    def text(self):
        # Format all fields into a prompt-ready string
        pass
```

The `text()` method formats everything into a structured block with labels, making it easy for the model to parse workspace information.

## Component 2: Prompt Shape and Cache Reuse

The prompt is constructed as a concatenation of four sections, with the prefix being static across turns:

```
<prefix>
  <rules>
  <tools>
  <examples>
  <workspace_context>
<memory>
<transcript>
<current_user_request>
```

### Prefix (Static)

The prefix contains:

1. **Identity** — "You are Mini-Coding-Agent, a small local coding agent running through Ollama."
2. **Rules** — behavioral constraints (use tools, return one tool or final, never invent results, etc.)
3. **Tools** — list of available tools with schemas and risk labels
4. **Examples** — valid response format examples for both JSON and XML tool styles
5. **Workspace Context** — output of `workspace.text()`

Because the prefix is stable, Ollama's prompt caching can reuse it efficiently across turns. Only the memory, transcript, and user request change.

### Memory (Dynamic, Small)

Working memory is formatted as:

```
Memory:
- task: <current task description>
- files: <comma-separated tracked files>
- notes:
  - <note 1>
  - <note 2>
```

### Transcript (Dynamic, Growing)

The transcript is the history text, built from the session history with context reduction applied (see Component 4).

### Current User Request (Dynamic)

The latest user message, appended at the end.

## Component 3: Structured Tools, Validation, and Permissions

Every tool has:

- **Schema** — typed argument definitions with defaults
- **Risky flag** — whether the tool requires approval
- **Description** — one-line explanation for the model
- **Run function** — the actual implementation

### Validation Flow

When `run_tool(name, args)` is called:

1. Check tool exists
2. Validate arguments via `validate_tool()`
3. Check for repeated identical calls (reject if same name + args as last two tool events)
4. Check approval gate for risky tools
5. Execute the tool, clipping output to MAX_TOOL_OUTPUT (4000 chars)
6. Return result or error message with example

### Path Safety

The `path()` method resolves all paths and validates they stay within the workspace root:

- Resolves symlinks
- Walks up to find an existing parent
- Checks if any candidate matches the workspace root via `samefile()`
- Raises `ValueError` if path escapes the workspace

This prevents directory traversal attacks even through symlinks.

### Approval Gate

```python
def approve(self, name, args):
    if self.read_only:
        return False          # child agents never get risky tools
    if self.approval_policy == "auto":
        return True           # auto-approve everything
    if self.approval_policy == "never":
        return False          # deny everything
    # Interactive prompt
    answer = input(f"approve {name} {json.dumps(args)}? [y/N] ")
    return answer.strip().lower() in {"y", "yes"}
```

Invalid tool arguments are rejected before the approval gate — the user is never asked to approve a malformed call.

## Component 4: Context Reduction and Output Management

### Output Clipping

Tool outputs are clipped to `MAX_TOOL_OUTPUT` (4000 chars) via the `clip()` helper:

```python
def clip(text, limit=MAX_TOOL_OUTPUT):
    text = str(text)
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...[truncated {len(text) - limit} chars]"
```

### Transcript Compression

The `history_text()` method builds the transcript with progressive compression:

- **Recent entries** (last 6) — tool output clipped to 900 chars, other content to 220 chars
- **Older entries** — tool output clipped to 180 chars, other content to 220 chars
- **Total transcript** — clipped to `MAX_HISTORY` (12000 chars)

### Read Deduplication

For `read_file` tool calls in the non-recent window:

- If the same file was already read, subsequent reads are skipped (only the first is shown)
- **Write operations clear the dedup set** — after `write_file` or `patch_file`, the next `read_file` on the same path is included, ensuring the model sees updated content

This prevents the transcript from filling with repeated file contents while still showing changes after writes.

## Component 5: Transcripts, Memory, and Resumption

### Session Storage

Sessions are saved as JSON files in `.mini-coding-agent/sessions/<id>.json`:

```json
{
  "id": "20260401-144025-2dd0aa",
  "created_at": "2026-04-01T14:40:25+00:00",
  "workspace_root": "/path/to/repo",
  "history": [...],
  "memory": {
    "task": "",
    "files": [],
    "notes": []
  }
}
```

The session is saved after every history entry is recorded, providing durable persistence.

### Working Memory Distillation

Memory is a small, curated state maintained alongside the full transcript:

- **task** — set from the first user message, clipped to 300 chars
- **files** — last 8 files touched by read/write/patch tools (LRU order)
- **notes** — last 5 notes from tool results and final answers, clipped to 220 chars each

The `remember()` helper maintains LRU ordering: if an item is already in the bucket, it is moved to the end; if the bucket exceeds the limit, oldest items are dropped.

### Session Resumption

```bash
uv run mini-coding-agent --resume latest
uv run mini-coding-agent --resume 20260401-144025-2dd0aa
```

The `SessionStore.latest()` method finds the most recently modified JSON file. The agent reconstructs its full state from the saved session, including history and memory.

## Component 6: Delegation and Bounded Subagents

### How Delegation Works

The `delegate` tool spawns a child `MiniAgent` instance:

```python
def tool_delegate(self, args):
    child = MiniAgent(
        model_client=self.model_client,
        workspace=self.workspace,
        session_store=self.session_store,
        approval_policy="never",     # child cannot do risky actions
        max_steps=int(args.get("max_steps", 3)),
        max_new_tokens=self.max_new_tokens,
        depth=self.depth + 1,
        max_depth=self.max_depth,
        read_only=True,              # approval gate always returns False
    )
    child.session["memory"]["task"] = task
    child.session["memory"]["notes"] = [clip(self.history_text(), 300)]
    return "delegate_result:\n" + child.ask(task)
```

### Delegation Constraints

- **Depth limit** — default `max_depth=1`, so only one level of delegation (parent → child, but not child → grandchild)
- **Read-only** — child agents have `read_only=True`, which causes the approval gate to always deny risky tools
- **No delegate tool** — when `depth >= max_depth`, the `delegate` tool is excluded from the child's tool set
- **Context inheritance** — the child receives the parent's compressed history as a note, giving it enough context to understand the task
- **Independent session** — the child has its own session and transcript, separate from the parent

### Use Cases

Delegation is useful for:

- Investigating a specific file or pattern without consuming the parent's step budget
- Running parallel investigations (conceptually, though execution is sequential)
- Scoping complex tasks into smaller, focused subtasks

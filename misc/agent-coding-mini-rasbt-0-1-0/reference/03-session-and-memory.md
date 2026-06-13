# Session and Memory System

## Session Structure

Each session is a JSON object persisted to `.mini-coding-agent/sessions/<id>.json`:

```json
{
  "id": "20260401-144025-2dd0aa",
  "created_at": "2026-04-01T14:40:25+00:00",
  "workspace_root": "/absolute/path/to/repo",
  "history": [
    {
      "role": "user",
      "content": "Create a binary_search.py file",
      "created_at": "2026-04-01T14:40:30+00:00"
    },
    {
      "role": "tool",
      "name": "write_file",
      "args": {"path": "binary_search.py", "content": "..."},
      "content": "wrote binary_search.py (123 chars)",
      "created_at": "2026-04-01T14:40:31+00:00"
    },
    {
      "role": "assistant",
      "content": "Created binary_search.py with iterative implementation.",
      "created_at": "2026-04-01T14:40:32+00:00"
    }
  ],
  "memory": {
    "task": "Create a binary_search.py file",
    "files": ["binary_search.py"],
    "notes": [
      "write_file: wrote binary_search.py (123 chars)",
      "Created binary_search.py with iterative implementation."
    ]
  }
}
```

### Session ID Format

`<YYYYMMDD>-<HHMMSS>-<6-hex-chars>` — combines a human-readable timestamp with a short random suffix for uniqueness.

### Save Strategy

The session is saved to disk after every history entry is appended. This provides crash resilience — if the agent terminates unexpectedly, the last complete state is preserved.

## Working Memory

Working memory is a small, curated state distilled from the full transcript. It serves as a compact summary that travels in every prompt.

### Task Field

Set from the first user message of the session, clipped to 300 characters. Once set, it persists for the session lifetime unless the session is reset.

### Files Field

Tracks the last 8 files touched by `read_file`, `write_file`, or `patch_file` tools. Uses LRU ordering — when a file is accessed again, it moves to the end of the list. If the list exceeds 8 entries, the oldest is dropped.

```python
@staticmethod
def remember(bucket, item, limit):
    if not item:
        return
    if item in bucket:
        bucket.remove(item)   # move to end (LRU)
    bucket.append(item)
    del bucket[:-limit]        # trim to limit
```

### Notes Field

Tracks the last 5 notes, each clipped to 220 characters. Notes come from:

- Tool execution results (formatted as `<tool_name>: <clipped result>`)
- Final answers from the model

Like files, notes use LRU ordering — repeated notes are moved to the end.

### Memory in Prompts

Memory is formatted into the prompt as:

```
Memory:
- task: Create a binary_search.py file
- files: binary_search.py
- notes:
  - write_file: wrote binary_search.py (123 chars)
  - Created binary_search.py with iterative implementation.
```

## Session Resumption

### Resuming Latest Session

```bash
uv run mini-coding-agent --resume latest
```

The `SessionStore.latest()` method sorts all `.json` files by modification time and returns the stem of the most recent one.

### Resuming Specific Session

```bash
uv run mini-coding-agent --resume 20260401-144025-2dd0aa
```

The full session ID is used to load the exact JSON file.

### From Code

```python
agent = MiniAgent.from_session(
    model_client=model_client,
    workspace=workspace,
    session_store=session_store,
    session_id="20260401-144025-2dd0aa",
    approval_policy="auto",
)
```

The `from_session` classmethod loads the saved JSON and reconstructs the agent with full history and memory intact.

## Reset

The `/reset` command clears the session history and memory:

```python
def reset(self):
    self.session["history"] = []
    self.session["memory"] = {"task": "", "files": [], "notes": []}
    self.session_store.save(self.session)
```

This starts a fresh conversation while keeping the same session ID and workspace context.

## Testing with FakeModelClient

The codebase includes a `FakeModelClient` for testing without Ollama:

```python
class FakeModelClient:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.prompts = []

    def complete(self, prompt, max_new_tokens):
        self.prompts.append(prompt)
        if not self.outputs:
            raise RuntimeError("fake model ran out of outputs")
        return self.outputs.pop(0)
```

It records all prompts sent to it and returns pre-programmed outputs in order. This enables deterministic testing of the agent loop, tool execution, retry logic, and session persistence.

### Test Pattern

```python
def build_agent(tmp_path, outputs, **kwargs):
    workspace = WorkspaceContext.build(tmp_path)
    store = SessionStore(tmp_path / ".mini-coding-agent" / "sessions")
    return MiniAgent(
        model_client=FakeModelClient(outputs),
        workspace=workspace,
        session_store=store,
        approval_policy="auto",
        **kwargs,
    )

agent = build_agent(tmp_path, [
    '<tool>{"name":"read_file","args":{"path":"hello.txt","start":1,"end":2}}</tool>',
    "<final>Read the file successfully.</final>",
])
answer = agent.ask("Inspect hello.txt")
assert answer == "Read the file successfully."
```

## OllamaModelClient

The production client sends requests to Ollama's `/api/generate` endpoint:

```python
payload = {
    "model": model_name,
    "prompt": prompt_text,
    "stream": False,
    "raw": False,
    "think": False,
    "options": {
        "num_predict": max_new_tokens,
        "temperature": temperature,
        "top_p": top_p,
    },
}
```

Key settings:

- `stream: False` — non-streaming response (full completion returned at once)
- `raw: False` — uses Ollama's built-in prompt formatting
- `think: False` — disables Ollama's thinking/reasoning mode
- `num_predict` — caps the maximum output tokens per step
- Uses only Python stdlib (`urllib.request`) — no external HTTP library needed

Error handling covers:

- HTTP errors (returns status code and body)
- Connection errors (friendly message about checking `ollama serve`)
- Ollama-level errors (forwards the error field from response JSON)

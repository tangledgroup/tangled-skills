# Tool Reference

## Tool Call Formats

The agent accepts two tool call formats. The model should emit exactly one `<tool>` or one `<final>` per response.

### JSON Style

Used for simple tools with scalar arguments:

```xml
<tool>{"name":"list_files","args":{"path":"."}}</tool>
<tool>{"name":"read_file","args":{"path":"README.md","start":1,"end":80}}</tool>
<tool>{"name":"run_shell","args":{"command":"python -m pytest -q","timeout":20}}</tool>
```

### XML Style

Used for tools with multi-line content (write_file, patch_file):

```xml
<tool name="write_file" path="file.py"><content>def hello():\n    print("hi")\n</content></tool>
<tool name="patch_file" path="file.py"><old_text>return -1</old_text><new_text>return mid</new_text></tool>
```

The XML parser extracts named inner tags (`<content>`, `<old_text>`, `<new_text>`, `<command>`, `<task>`, `<pattern>`) and attribute values.

### Final Answer

```xml
<final>Task completed. Created binary_search.py with iterative implementation.</final>
```

If the model returns plain text without tags, it is treated as a final answer.

## Built-in Tools

### list_files

List files in the workspace directory.

- **Risky**: No
- **Schema**: `path: str='.'`
- **Description**: List files in the workspace
- **Output**: Lines of `[D] path/to/dir` or `[F] path/to/file`, sorted with directories first, limited to 200 entries
- **Hidden paths**: `.git`, `.mini-coding-agent`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.venv`, `venv` are always excluded
- **Example**: `<tool>{"name":"list_files","args":{"path":"."}}</tool>`

### read_file

Read a UTF-8 file by line range.

- **Risky**: No
- **Schema**: `path: str`, `start: int=1`, `end: int=200`
- **Description**: Read a UTF-8 file by line range
- **Validation**: path must be an existing file; start >= 1; end >= start
- **Output**: Numbered lines with format `   N: <content>`, prefixed with `# <relative-path>`
- **Example**: `<tool>{"name":"read_file","args":{"path":"src/main.py","start":1,"end":50}}</tool>`

### search

Search the workspace for a text pattern.

- **Risky**: No
- **Schema**: `pattern: str`, `path: str='.'`
- **Description**: Search the workspace with rg or a simple fallback
- **Implementation**: Uses `rg -n --smart-case --max-count 200` if available, otherwise falls back to recursive file scanning with case-insensitive matching
- **Output**: Lines of `<relative-path>:<line_number>:<matching_line>`, up to 200 matches
- **Example**: `<tool>{"name":"search","args":{"pattern":"binary_search","path":"."}}</tool>`

### run_shell

Run a shell command in the repo root.

- **Risky**: Yes (requires approval)
- **Schema**: `command: str`, `timeout: int=20`
- **Description**: Run a shell command in the repo root
- **Validation**: command must not be empty; timeout must be in [1, 120]
- **Output**: Structured output with exit code, stdout, and stderr sections:
  ```
  exit_code: 0
  stdout:
  <output>
  stderr:
  (empty)
  ```
- **Example**: `<tool>{"name":"run_shell","args":{"command":"python -m pytest -q","timeout":20}}</tool>`

### write_file

Write a text file (creates parent directories as needed).

- **Risky**: Yes (requires approval)
- **Schema**: `path: str`, `content: str`
- **Description**: Write a text file
- **Validation**: path must not be an existing directory; content must be present
- **Output**: `wrote <relative-path> (<N> chars)`
- **Example (XML)**: `<tool name="write_file" path="hello.py"><content>print("hi")\n</content></tool>`

### patch_file

Replace one exact text block in a file.

- **Risky**: Yes (requires approval)
- **Schema**: `path: str`, `old_text: str`, `new_text: str`
- **Description**: Replace one exact text block in a file
- **Validation**: path must be an existing file; old_text must not be empty; new_text must be present; old_text must occur exactly once in the file
- **Output**: `patched <relative-path>`
- **Example (XML)**: `<tool name="patch_file" path="main.py"><old_text>return -1</old_text><new_text>return mid</new_text></tool>`

### delegate

Ask a bounded read-only child agent to investigate.

- **Risky**: No
- **Schema**: `task: str`, `max_steps: int=3`
- **Description**: Ask a bounded read-only child agent to investigate
- **Constraints**: Only available when `depth < max_depth` (default max_depth is 1, so only the top-level agent has this tool)
- **Child restrictions**: read-only mode (no risky tools), no further delegation, inherits parent's compressed history as context
- **Output**: `delegate_result:\n<child's final answer>`
- **Example**: `<tool>{"name":"delegate","args":{"task":"inspect README.md","max_steps":3}}</tool>`

## Error Handling

### Tool Validation Errors

When arguments fail validation, the error message includes a usage example:

```
error: invalid arguments for write_file: 'path'
example: <tool name="write_file" path="binary_search.py"><content>...</content></tool>
```

Validation runs before approval — malformed calls are never presented to the user for approval.

### Repeated Call Detection

If the last two tool events in history have the same name and args, the call is rejected:

```
error: repeated identical tool call for list_files; choose a different tool or return a final answer
```

### Unknown Tools

```
error: unknown tool 'nonexistent_tool'
```

### Runtime Errors

Tool execution errors are caught and reported:

```
error: tool run_shell failed: [Errno 2] No such file or directory
```

## Retry Mechanism

When the model returns malformed output, the agent sends a retry notice back to the model:

```
Runtime notice: model returned malformed tool JSON. Reply with a valid <tool> call or a non-empty <final> answer. For multi-line files, prefer <tool name="write_file" path="file.py"><content>...</content></tool>.
```

Retries do not count against the step budget — only successful tool calls consume steps. The overall attempt limit is `max(max_steps * 3, max_steps + 4)` to prevent infinite retry loops.

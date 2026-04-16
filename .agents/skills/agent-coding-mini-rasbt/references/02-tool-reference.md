# Tool Reference: Complete API Documentation

This document provides complete reference information for all agent tools, including schemas, validation rules, examples, and output formats. The mini-coding-agent implements **7 tools** organized into safe tools (no approval), risky tools (require approval), and conditional tools (delegation).

## Tool Response Formats

The model must emit tool calls in one of two XML-enclosed formats:

### JSON Format (within `<tool>` tags)

Used for simple tool calls with short arguments:

```xml
<tool>{"name":"list_files","args":{"path":"."}}</tool>
<tool>{"name":"read_file","args":{"path":"README.md","start":1,"end":80}}</tool>
<tool>{"name":"run_shell","args":{"command":"uv run --with pytest python -m pytest -q","timeout":20}}</tool>
```

### XML Format (for multi-line content)

Used for `write_file`, `patch_file`, and other tools with large text bodies:

```xml
<tool name="write_file" path="binary_search.py">
<content>def binary_search(nums, target):
    """Iterative binary search implementation."""
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1</content>
</tool>
```

### XML Format for Patch Operations

```xml
<tool name="patch_file" path="binary_search.py">
<old_text>return -1</old_text>
<new_text>raise ValueError("Target not found in sorted list")</new_text>
</tool>
```

---

## Safe Tools (No Approval Required)

### list_files

List files and directories in the workspace.

**Schema:** `{"path": "str='.'"}`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `path` | string | `"."` | Directory path to list (relative to workspace root) |

**Validation:**
- Path must exist and be a directory
- Path must be within workspace root

**Examples:**

```xml
<tool>{"name":"list_files","args":{"path":"."}}</tool>
<tool>{"name":"list_files","args":{"path":"src"}}}</tool>
```

**Output Format:**
```
[D] src/
[D] tests/
[F] README.md
[F] pyproject.toml
[F] main.py
```

Directories shown with `[D]`, files with `[F]`. Sorted with directories first, then files alphabetically. Limited to 200 entries.

**Ignored Directories:** `.git`, `.mini-coding-agent`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.venv`, `venv`

---

### read_file

Read a UTF-8 file by line range.

**Schema:** `{"path": "str", "start": "int=1", "end": "int=200"}`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `path` | string | **required** | File path to read (relative to workspace root) |
| `start` | integer | `1` | Starting line number (1-indexed) |
| `end` | integer | `200` | Ending line number (inclusive) |

**Validation:**
- Path must exist and be a file
- Path must be within workspace root
- `start >= 1`
- `end >= start`

**Examples:**

```xml
<tool>{"name":"read_file","args":{"path":"README.md","start":1,"end":50}}</tool>
<tool>{"name":"read_file","args":{"path":"src/main.py","start":25,"end":75}}</tool>
<tool>{"name":"read_file","args":{"path":"config.json"}}</tool>
```

**Output Format:**
```
# README.md
   1: # Project Title
   2: 
   3: This is a sample project.
   4: 
   5: ## Installation
   6: ```bash
   7: pip install -r requirements.txt
   8: ```
```

Lines are numbered and right-aligned. File path shown as header.

---

### search

Search the workspace for a pattern using ripgrep (`rg`) or fallback to Python-based search.

**Schema:** `{"pattern": "str", "path": "str='.'"}`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `pattern` | string | **required** | Search pattern (regex supported with rg) |
| `path` | string | `"."` | Directory or file to search in |

**Validation:**
- `pattern` must not be empty or whitespace-only
- `path` must exist and be within workspace root

**Examples:**

```xml
<tool>{"name":"search","args":{"pattern":"def binary_search","path":"."}}</tool>
<tool>{"name":"search","args":{"pattern":"TODO","path":"src"}}</tool>
<tool>{"name":"search","args":{"pattern":"class.*Agent","path":"."}}</tool>
```

**Output Format:**
```
src/main.py:12:def binary_search(nums, target):
src/utils.py:45:def binary_search_recursive(arr, left, right, target):
tests/test_search.py:8:    def test_binary_search(self):
```

Format: `filepath:line_number:matching_line`

Limited to 200 matches. Returns "(no matches)" if nothing found.

**Note:** If `rg` (ripgrep) is installed, it's used with `--smart-case` flag. Otherwise, a case-insensitive Python fallback is used.

---

## Risky Tools (Require Approval)

### run_shell

Execute a shell command in the repository root directory.

**Schema:** `{"command": "str", "timeout": "int=20"}`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `command` | string | **required** | Shell command to execute |
| `timeout` | integer | `20` | Timeout in seconds (1–120) |

**Validation:**
- `command` must not be empty or whitespace-only
- `timeout` must be between 1 and 120 seconds
- Requires approval unless `--approval auto` is set

**Examples:**

```xml
<tool>{"name":"run_shell","args":{"command":"uv run --with pytest python -m pytest -q","timeout":60}}</tool>
<tool>{"name":"run_shell","args":{"command":"python --version","timeout":10}}</tool>
<tool>{"name":"run_shell","args":{"command":"ruff check .","timeout":30}}</tool>
```

**Output Format:**
```
exit_code: 0
stdout:
====================== test session starts ======================
collected 5 items

tests/test_binary.py .....

========================= 5 passed in 0.12s =========================

stderr:
(empty)
```

Always includes exit code, stdout, and stderr sections. Empty sections show "(empty)".

**Security Notes:**
- Commands run in workspace root directory (`cwd=self.root`)
- Shell injection is possible — use approval gates!
- Timeout prevents hanging commands (max 120 seconds)
- Requires explicit approval in interactive mode (`--approval ask`)

---

### write_file

Create or overwrite a text file.

**Schema:** `{"path": "str", "content": "str"}`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `path` | string | **required** | File path to create/overwrite (relative to workspace root) |
| `content` | string | **required** | File contents |

**Validation:**
- Path must not be an existing directory
- Path must be within workspace root
- `content` must be present
- Requires approval unless `--approval auto` is set

**Examples (JSON format for small files):**

```xml
<tool>{"name":"write_file","args":{"path":".gitignore","content":"__pycache__/\n*.pyc\n.venv/"}}</tool>
```

**Examples (XML format for multi-line content):**

```xml
<tool name="write_file" path="binary_search.py">
<content>def binary_search(nums, target):
    """Iterative binary search implementation."""
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1


if __name__ == "__main__":
    test_nums = [1, 3, 5, 7, 9, 11, 13]
    print(binary_search(test_nums, 7))  # Output: 3
</content>
</tool>
```

**Output Format:**
```
wrote binary_search.py (847 chars)
```

Shows relative path and character count. Creates parent directories if they don't exist. UTF-8 encoding used. Prefer XML format for multi-line content to avoid JSON escaping issues.

---

### patch_file

Replace one exact text block in an existing file.

**Schema:** `{"path": "str", "old_text": "str", "new_text": "str"}`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `path` | string | **required** | File path to modify (relative to workspace root) |
| `old_text` | string | **required** | Exact text to find and replace |
| `new_text` | string | **required** | Replacement text |

**Validation:**
- Path must exist and be a file
- Path must be within workspace root
- `old_text` must not be empty
- `new_text` must be present
- `old_text` must occur **exactly once** in the file
- Requires approval unless `--approval auto` is set

**Examples:**

Simple text replacement:
```xml
<tool name="patch_file" path="binary_search.py">
<old_text>return -1</old_text>
<new_text>raise ValueError("Target not found in sorted list")</new_text>
</tool>
```

Add validation:
```xml
<tool name="patch_file" path="binary_search.py">
<old_text>def binary_search(nums, target):
    """Iterative binary search implementation."""
    left, right = 0, len(nums) - 1</old_text>
<new_text>def binary_search(nums, target):
    """Iterative binary search implementation.
    
    Args:
        nums: Sorted list of integers
        target: Integer to search for
        
    Raises:
        ValueError: If nums is not sorted in ascending order
    """
    if any(nums[i] > nums[i+1] for i in range(len(nums)-1)):
        raise ValueError("Input list must be sorted in ascending order")
    
    left, right = 0, len(nums) - 1</new_text>
</tool>
```

**Output Format:**
```
patched binary_search.py
```

**Error Cases:**

If `old_text` not found or found multiple times:
```
error: invalid arguments for patch_file: old_text must occur exactly once, found 0
error: invalid arguments for patch_file: old_text must occur exactly once, found 3
```

**Notes:**
- Use exact whitespace matching (including indentation)
- Prefer XML format for multi-line text
- Read file first to get exact text to replace
- Use `write_file` instead if making extensive changes

---

## Delegation Tool (Conditional)

### delegate

Ask a bounded read-only child agent to investigate a subtask.

**Availability:** Only available if current `depth < max_depth` (default: depth 0, max_depth 1)

**Schema:** `{"task": "str", "max_steps": "int=3"}`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `task` | string | **required** | Task description for the subagent |
| `max_steps` | integer | `3` | Maximum tool/model iterations for subagent |

**Validation:**
- `task` must not be empty or whitespace-only
- Current depth must be less than max_depth
- Subagent runs in read-only mode (no file modifications)

**Examples:**

```xml
<tool>{"name":"delegate","args":{"task":"Read and summarize the architecture in src/main.py","max_steps":3}}</tool>
<tool>{"name":"delegate","args":{"task":"Search for all uses of WorkspaceContext and report findings","max_steps":5}}</tool>
```

**Output Format:**
```
delegate_result:
Based on my analysis of the test files, this project uses pytest as the testing framework. I found:

- tests/test_binary.py contains pytest-style test functions
- pyproject.toml lists pytest>=9.0.2 as a dependency
- Test files use parametrized tests and fixtures

The project appears to follow standard pytest conventions with test_*.py naming pattern.
```

**Subagent Restrictions:**
- Cannot use `write_file`, `patch_file`, or `run_shell` (approval always denied)
- Limited to `max_steps` iterations (default 3)
- Cannot create further subagents (depth limit reached)
- Gets compressed parent history as context notes

---

## Final Answer Format

When the agent has completed its task, it should emit a final answer:

```xml
<final>I've created binary_search.py with an iterative implementation that:</final>
```

Or for simple answers:
```xml
<final>Done. The binary search implementation is complete.</final>
```

**Rules:**
- Only one `<final>` tag per response
- Final answers should be concise but informative
- Include relevant details (file sizes, line counts, key changes)
- Don't emit both `<tool>` and `<final>` in the same response

---

## Tool Call Parsing

The agent parses tool calls using multiple strategies to accommodate different model output styles:

### Strategy 1: JSON within `<tool>` tags
```xml
<tool>{"name":"read_file","args":{"path":"file.py"}}</tool>
```

### Strategy 2: XML-style with attributes
```xml
<tool name="write_file" path="file.py">
<content>...</content>
</tool>
```

### Strategy 3: XML body as content
For `write_file` and `delegate`, if no `<content>` or `<task>` tag exists, the raw body text is used:
```xml
<tool name="write_file" path="file.py">
def hello():
    print("world")
</tool>
# Body becomes content argument
```

### Error Recovery

If tool parsing fails, the agent returns a retry notice:
```
Runtime notice: model returned malformed tool JSON. Reply with a valid <tool> call or a non-empty <final> answer. For multi-line files, prefer <tool name="write_file" path="file.py"><content>...</content></tool>.
```

The model should then retry with properly formatted output. The agent counts these as attempts but not as tool steps — the step limit only applies to successful tool executions.

---

## Tool Summary Table

| Tool | Risky | Approval | Description | Key Validation |
|------|-------|----------|-------------|----------------|
| `list_files` | No | None | List directory contents | Path is a directory, in workspace |
| `read_file` | No | None | Read file by line range | File exists, valid line range |
| `search` | No | None | Search for pattern in files | Pattern not empty |
| `run_shell` | Yes | ask/auto/never | Execute shell command | Command not empty, timeout 1-120s |
| `write_file` | Yes | ask/auto/never | Create/overwrite file | Content present, path not a directory |
| `patch_file` | Yes | ask/auto/never | Replace exact text block | old_text occurs exactly once |
| `delegate` | No | N/A (conditional) | Spawn bounded subagent | depth < max_depth, task not empty |

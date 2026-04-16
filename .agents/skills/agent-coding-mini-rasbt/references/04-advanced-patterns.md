# Advanced Patterns: Configuration, Approval Modes, and Customization

This document covers advanced usage patterns including approval modes, bounded delegation strategies, model configuration, CLI options, troubleshooting techniques, and extension patterns for modifying the agent.

## Approval Modes

Risky tools (`run_shell`, `write_file`, `patch_file`) are gated by approval policies. This is a critical safety feature — without it, the model has arbitrary command execution capability.

### Mode: ask (Default)

Prompts before each risky operation:

```bash
python mini_coding_agent.py --approval ask
```

**Behavior:**
```
approve write_file {"path": "binary_search.py", "content": "..."}? [y/N] 
```

| Input | Result |
|-------|--------|
| `y` or `yes` | Approve the operation |
| `n`, `no`, or Enter (empty) | Deny the operation |
| EOF (non-interactive mode) | Defaults to deny |

**Use cases:**
- Interactive development sessions
- Human-in-the-loop safety for production environments
- Learning what the agent wants to do before committing changes
- Auditing agent behavior in real-time

### Mode: auto

Automatically approve all risky operations:

```bash
python mini_coding_agent.py --approval auto
```

**Behavior:**
- No prompts for risky tools — agent acts freely
- Agent can execute commands and modify files without oversight
- **WARNING**: Model has arbitrary command execution capability

**Use cases:**
- Automated CI/CD pipelines (trusted repos only)
- Quick prototyping in isolated environments
- Testing agent capabilities without manual intervention
- Trusted prompts and repositories only

**Security considerations:**
- Only use with trusted codebases you understand
- Model could execute destructive commands (`rm -rf`, `> /dev/sda`, etc.)
- Model could overwrite important configuration files
- Consider sandboxing (containers, VMs) for untrusted work
- Never use `--approval auto` on production systems

### Mode: never

Deny all risky operations — read-only mode:

```bash
python mini_coding_agent.py --approval never
```

**Behavior:**
- `write_file`, `patch_file`, `run_shell` always fail with "approval denied"
- Agent can only read files and search the workspace
- Useful for investigation-only sessions

**Use cases:**
- Codebase exploration without modification risk
- Read-only analysis and documentation tasks
- Safe mode for untrusted or sensitive environments
- Subagents (automatically set to `never` internally)

## Bounded Delegation Strategies

The `delegate` tool creates read-only subagents with limited scope. This is where the agent harness starts to resemble more sophisticated systems like Claude Code's subagent feature.

### Default Delegation

```xml
<tool>{"name":"delegate","args":{"task":"Summarize the architecture in src/main.py","max_steps":3}}</tool>
```

Creates a subagent with:
- `read_only=True` — cannot modify any files
- `approval_policy="never"` — risky tools always denied
- `max_steps=3` — limited iterations (configurable)
- `depth=1` — cannot create further subagents (max_depth default is 1)
- Inherits compressed parent history as context notes

### Delegation Use Cases

#### Investigate Before Modifying

Delegate fact-finding before making changes:

```xml
<tool>{"name":"delegate","args":{"task":"Read all files in tests/ and summarize the testing patterns used","max_steps":5}}</tool>
```

Parent agent gets investigation results without using its own step budget for reading files.

#### Research Code Patterns

```xml
<tool>{"name":"delegate","args":{"task":"Search for all uses of WorkspaceContext and report how it's instantiated","max_steps":4}}</tool>
```

Subagent explores the codebase, parent receives findings to inform decisions.

#### Parallel Investigation (Manual)

The main agent can delegate multiple subtasks sequentially:

```
Parent: Investigate the authentication module thoroughly
  → Delegate 1: "Read auth/login.py and summarize the flow"
  → Delegate 2: "Search for session management patterns in auth/"
  → Delegate 3: "Check what dependencies are used for auth in pyproject.toml"
```

Then synthesize findings in the parent agent's next step.

### Delegation Limitations

| Constraint | Default | Description |
|-----------|---------|-------------|
| Depth limit | `max_depth=1` | Root can create subagents; subagents cannot create further ones |
| Read-only | Always | Subagents cannot modify files or run shell commands |
| Context inheritance | Compressed history (300 chars) | Subagent gets parent's recent transcript as notes |
| Step limit | `max_steps=3` | Configurable per delegation call |

### Comparison: Mini-Agent vs Claude Code vs Codex

| Feature | Mini-Coding-Agent | Claude Code | Codex CLI |
|---------|------------------|-------------|-----------|
| Subagent mode | Read-only only | Configurable | Inherits sandbox/approval |
| Depth limit | 1 level | Multi-level | Multi-level |
| Context inheritance | Compressed history (300 chars) | Full context | Full context |
| Tool access | Limited set | Full tool set | Full tool set |

The mini-agent's approach is simpler but safer — subagents investigate without modifying files. More sophisticated harnesses allow subagents to inherit the main agent's sandbox, with boundaries around task scoping and context rather than strict read-only mode.

## Model Configuration

### Ollama Model Selection

Different models have different capabilities for tool use and instruction following:

| Model | RAM Needed | Quality | Best For |
|-------|-----------|---------|----------|
| `qwen3.5:4b` | ~3 GB | Baseline | Limited RAM, fast iteration |
| `qwen3.5:9b` | ~6 GB | Better | Good instruction following |
| `qwen3.5:14b` | ~10 GB | Strong | Complex tasks |
| `qwen3.5:32b` | ~20 GB | Excellent | Very complex reasoning |
| `llama3.1:8b` | ~5 GB | Good alternative | When Qwen not available |

```bash
# Default (works with limited RAM)
python mini_coding_agent.py --model qwen3.5:4b

# Better instruction following (if memory allows)
python mini_coding_agent.py --model qwen3.5:9b

# Alternative models
python mini_coding_agent.py --model llama3.1:8b
```

**Model recommendations:**
- **Qwen 3.5 family**: Best instruction following for structured tool use
- **Larger models**: Better at complex reasoning and format adherence
- **Smaller models**: Faster, lower memory, may need simpler tasks

### Ollama Server Configuration

#### Custom Host

If Ollama is running on a different host:

```bash
python mini_coding_agent.py --host http://localhost:11434
python mini_coding_agent.py --host http://192.168.1.100:11434
```

#### Connection Timeout

Increase timeout for slow models or networks (default: 300 seconds):

```bash
python mini_coding_agent.py --ollama-timeout 600  # 10 minutes
```

### Generation Parameters

#### Temperature

Control randomness in generation. Lower values are more deterministic:

```bash
# More deterministic (default, recommended for coding)
python mini_coding_agent.py --temperature 0.2

# Very deterministic
python mini_coding_agent.py --temperature 0.0

# More creative/varied (not recommended for coding tasks)
python mini_coding_agent.py --temperature 0.7
```

**Recommendations:**
| Temperature | Use Case |
|-------------|----------|
| `0.0–0.3` | Coding tasks, tool use (deterministic) |
| `0.3–0.5` | General tasks with some variation |
| `0.5+` | Creative tasks (not recommended for coding agents) |

#### Top-p (Nucleus Sampling)

Control vocabulary diversity:

```bash
# Default (focus on likely tokens)
python mini_coding_agent.py --top-p 0.9

# More restrictive
python mini_coding_agent.py --top-p 0.7

# More diverse
python mini_coding_agent.py --top-p 0.95
```

**How it works:** Samples from the smallest set of tokens whose cumulative probability >= top_p. Lower values restrict to more probable tokens.

#### Max Tokens

Limit output length per step:

```bash
# Default (good for tool calls)
python mini_coding_agent.py --max-new-tokens 512

# Longer responses for complex explanations
python mini_coding_agent.py --max-new-tokens 1024

# Short, concise responses
python mini_coding_agent.py --max-new-tokens 256
```

**Considerations:**
- Tool calls should fit within the limit
- Final answers may need more tokens for explanations
- Larger models may need more tokens for complex reasoning

## Step Limits and Control

### Max Steps Per Request

Limit iterations per user request:

```bash
# Default (6 tool/model turns)
python mini_coding_agent.py --max-steps 6

# More iterations for complex tasks
python mini_coding_agent.py --max-steps 12

# Fewer iterations for simple tasks
python mini_coding_agent.py --max-steps 3
```

**What counts as a step:**
- Each successful tool call = 1 step
- Final answer (`<final>`) = terminates the loop (not a step)
- Retry notices (malformed responses) = not a step (no step penalty)

**Stopping conditions:**
| Condition | Message |
|-----------|---------|
| Agent emits `<final>` before max_steps | Task complete |
| Max steps reached without final answer | "Stopped after reaching the step limit without a final answer." |
| Too many malformed responses | "Stopped after too many malformed model responses without a valid tool call or final answer." |

**Max attempts calculation:** `max(max_steps * 3, max_steps + 4)` — allows extra attempts for malformed responses without consuming steps.

### Step Budget Management

For complex tasks, manage step budget efficiently:

```
Task: Implement feature with tests and run them (~6 steps optimal)

Step 1: read_file (existing code)
Step 2: write_file (implementation)
Step 3: write_file (tests)
Step 4: run_shell (pytest)
Step 5: patch_file (fix issues if needed)
Step 6: final answer

If step 4 fails, may need more steps for fixes
```

**Strategies:**
- Break large tasks into multiple user requests
- Use delegation for investigation (doesn't consume parent steps)
- Set higher `--max-steps` for complex multi-file changes
- Use `/reset` to start fresh when context gets polluted

## CLI Reference

Complete command-line interface documentation. Run `python mini_coding_agent.py --help` or `uv run mini-coding-agent --help` for the latest.

### Positional Arguments

| Argument | Description |
|----------|-------------|
| `prompt` (optional, variable) | One-shot prompt to execute and exit (non-interactive mode) |

```bash
python mini_coding_agent.py "Create a hello_world.py file"
```

### Workspace Options

| Flag | Default | Description |
|------|---------|-------------|
| `--cwd` | `.` | Workspace directory the agent should inspect and modify |

```bash
python mini_coding_agent.py --cwd /path/to/project
python mini_coding_agent.py --cwd ./src/module
```

### Model Connection Options

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `qwen3.5:4b` | Ollama model name |
| `--host` | `http://127.0.0.1:11434` | Ollama server URL |
| `--ollama-timeout` | `300` | Ollama request timeout in seconds |

```bash
python mini_coding_agent.py --model qwen3.5:9b \
  --host http://localhost:11434 \
  --ollama-timeout 600
```

### Session Options

| Flag | Default | Description |
|------|---------|-------------|
| `--resume` | None | Resume a saved session by ID or use "latest" |

```bash
python mini_coding_agent.py --resume latest
python mini_coding_agent.py --resume 20260413-143022-a1b2c3
```

### Approval Options

| Flag | Default | Description |
|------|---------|-------------|
| `--approval` | `ask` | Approval policy: `ask`, `auto`, or `never` |

```bash
python mini_coding_agent.py --approval ask    # Interactive prompts (default)
python mini_coding_agent.py --approval auto   # No prompts (trusted env only)
python mini_coding_agent.py --approval never  # Read-only mode
```

### Generation Limits

| Flag | Default | Description |
|------|---------|-------------|
| `--max-steps` | `6` | Maximum tool/model iterations per user request |
| `--max-new-tokens` | `512` | Maximum model output tokens per step |

```bash
python mini_coding_agent.py --max-steps 12 --max-new-tokens 1024
```

### Sampling Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--temperature` | `0.2` | Sampling temperature for generation |
| `--top-p` | `0.9` | Top-p nucleus sampling value |

```bash
python mini_coding_agent.py --temperature 0.0 --top-p 0.7
```

## Complete Example Workflows

### Workflow 1: New Feature Implementation (Interactive)

```bash
# Start fresh session in project directory
cd my-project
python mini_coding_agent.py --approval ask
```

```
mini-coding-agent> Implement a user authentication module with login, logout, and session management. Create auth.py with classes for UserSession and AuthManager.
```

Agent responds with implementation plan and starts creating files.

```
mini-coding-agent> Now add unit tests for the auth module covering successful login, failed login, session expiration, and concurrent sessions.
```

Agent creates test file and runs tests.

```
mini-coding-agent> Run the tests and fix any failures.
```

Agent executes pytest and patches issues.

```
mini-coding-agent> /memory    # Review what was accomplished
mini-coding-agent> /exit      # Save session and exit
```

### Workflow 2: Codebase Investigation (Read-Only)

```bash
# Read-only investigation mode — no modifications possible
python mini_coding_agent.py --approval never
```

```
mini-coding-agent> Investigate this codebase and summarize the architecture. What design patterns are used? How is the project organized?
```

Agent uses `search`, `read_file`, and `delegate` to explore without risk of changes.

### Workflow 3: Automated Pipeline (Trusted Environment Only)

```bash
# CI/CD pipeline with auto approval — DANGER: model has arbitrary command execution
python mini_coding_agent.py --approval auto --max-steps 10 \
  "Fix all failing tests in the repository"
```

Agent autonomously:
1. Runs tests to identify failures
2. Reads failing test files and related source
3. Patches bugs
4. Re-runs tests
5. Repeats until all pass or max_steps reached

### Workflow 4: Resume Interrupted Work

```bash
# Next day, resume where you left off
python mini_coding_agent.py --resume latest
```

```
mini-coding-agent> Continue from where we stopped. We were working on the payment processing module.
```

Agent has full context from previous session — history and memory are preserved.

## Troubleshooting

### Model Not Following Format

**Symptom:** Agent repeatedly outputs malformed tool calls or plain text instead of `<tool>`/`<final>` tags.

| Solution | Command |
|----------|---------|
| Try a larger model | `--model qwen3.5:9b` |
| Lower temperature for deterministic output | `--temperature 0.0` |
| Use models with better instruction following | Qwen 3.5 family recommended |
| Simplify the task | Break into smaller steps |

### Ollama Connection Errors

**Symptom:** "Could not reach Ollama" or connection timeout errors.

```bash
# Check if Ollama is running
ollama --help

# Test API endpoint
curl http://127.0.0.1:11434/api/tags

# Check model is loaded
ollama list
```

**Solutions:**
```bash
# Start Ollama server (separate terminal)
ollama serve

# Pull the model if not already pulled
ollama pull qwen3.5:4b

# Increase timeout for slow models
python mini_coding_agent.py --ollama-timeout 600

# Check host configuration
python mini_coding_agent.py --host http://localhost:11434
```

### Tool Validation Errors

**Symptom:** "invalid arguments for <tool>" errors.

| Common Cause | Solution |
|-------------|----------|
| Path doesn't exist or is wrong type | List directory first to verify paths |
| Missing required arguments | Check argument schemas in tool reference |
| `old_text` in patch_file occurs 0 or >1 times | Read file first, get exact text to replace |
| Command empty in run_shell | Ensure command string is not whitespace-only |

### Repeated Tool Call Errors

**Symptom:** "repeated identical tool call" error.

**Cause:** Agent called same tool with same arguments twice in a row.

**Solutions:**
- Provide more specific follow-up instructions
- Reset session: `/reset`
- Break task into smaller, sequential steps

### Session Issues

**Symptom:** Memory not updating, files not tracked.

```bash
# Check session is being saved
python mini_coding_agent.py
/session    # Note the path
ls -lt <session_path>  # Should update mtime after each turn
```

**Solutions:**
- Verify tool calls are succeeding (failed tools don't update memory)
- Check disk space — session saves may fail silently
- Manual reset: `/reset` to clear corrupted state

### Performance Issues

**Symptom:** Slow responses, high memory usage.

| Optimization | Command |
|-------------|---------|
| Use smaller model | `--model qwen3.5:4b` |
| Reduce max tokens | `--max-new-tokens 256` |
| Limit steps | `--max-steps 4` |
| Close other applications | Free up RAM for Ollama |

## Customization and Extension

The single-file architecture makes it easy to modify the agent. Here's how to extend each component.

### Adding a Custom Tool

To add a new tool, you need to modify four places in `mini_coding_agent.py`:

```python
# 1. Add to build_tools() method
def build_tools(self):
    tools = {
        # ... existing tools ...
        "my_custom_tool": {
            "schema": {"arg1": "str", "arg2": "int=10"},
            "risky": False,  # or True for approval
            "description": "Description of my custom tool.",
            "run": self.tool_my_custom_tool,
        },
    }
    if self.depth < self.max_depth:
        tools["delegate"] = { ... }
    return tools

# 2. Implement the tool method
def tool_my_custom_tool(self, args):
    arg1 = str(args.get("arg1", ""))
    arg2 = int(args.get("arg2", 10))
    # ... your logic here ...
    return f"Result: {result}"

# 3. Add validation in validate_tool() method
def validate_tool(self, name, args):
    # ... existing validations ...
    if name == "my_custom_tool":
        arg1 = str(args.get("arg1", "")).strip()
        if not arg1:
            raise ValueError("arg1 must not be empty")
        return

# 4. Add example in tool_example() dictionary
def tool_example(self, name):
    examples = {
        # ... existing examples ...
        "my_custom_tool": '<tool>{"name":"my_custom_tool","args":{"arg1":"value"}}}</tool>',
    }
    return examples.get(name, "")
```

### Custom Workspace Context

Modify `WorkspaceContext.build()` to collect additional context:

```python
@classmethod
def build(cls, cwd):
    # ... existing code ...
    
    # Add custom context collection
    custom_data = subprocess.run(
        ["custom-command", "--flag"],
        capture_output=True, text=True
    ).stdout.strip()
    
    return cls(
        # ... existing fields ...
        custom_field=custom_data,
    )

def text(self):
    # ... existing output ...
    return "\n".join([existing_text, f"- custom: {self.custom_field}"])
```

### Custom Approval Logic

Override `approve()` method for custom approval workflows:

```python
def approve(self, name, args):
    # Custom logic before default behavior
    if name == "run_shell":
        command = str(args.get("command", ""))
        dangerous_patterns = ["rm -rf /", "mkfs", "> /dev/sda"]
        for pattern in dangerous_patterns:
            if pattern in command:
                return False  # Always deny dangerous commands
    
    # Default approval flow
    if self.read_only:
        return False
    if self.approval_policy == "auto":
        return True
    if self.approval_policy == "never":
        return False
    try:
        answer = input(f"approve {name} {json.dumps(args, ensure_ascii=True)}? [y/N] ")
    except EOFError:
        return False
    return answer.strip().lower() in {"y", "yes"}
```

### Custom Prompt Rules

Modify the `build_prefix()` method to add or change rules:

```python
def build_prefix(self):
    # ... existing code ...
    
    # Add custom rules
    extra_rules = "\n".join([
        "- Always check if a file exists before writing to it.",
        "- When creating tests, use pytest-style functions (not unittest).",
        "- Prefer f-strings over .format() or % formatting.",
    ])
    
    # Insert into rules section
    rules = "\n".join([existing_rules, extra_rules])
```

## Best Practices

### Task Scoping

| Practice | Reason |
|----------|--------|
| One file per request for complex edits | Easier to track changes and fix issues |
| Read before write | Understand context before modifying |
| Test incrementally | Catch errors early, smaller diffs |
| Use delegation for investigation | Doesn't consume parent step budget |

### Session Management

| Practice | Reason |
|----------|--------|
| Resume for continuity on multi-day projects | Preserves conversation history and memory |
| Reset for fresh start when context polluted | Removes irrelevant history |
| Backup important sessions before major changes | Prevents data loss |
| Clean up old sessions periodically | Frees disk space |

### Safety

| Practice | Reason |
|----------|--------|
| Use `--approval ask` in production environments | Human oversight for all changes |
| Review tool calls before approving destructive operations | Prevents accidental data loss |
| Test with `--approval auto` only in isolated environments | Model has arbitrary command execution |
| Monitor subagent actions even though read-only | Ensures correct investigation |

### Model Selection

| Practice | Reason |
|----------|--------|
| Start with `qwen3.5:4b` for baseline performance | Works with limited RAM (~3 GB) |
| Upgrade to larger models if format issues occur | Better instruction following |
| Consider RAM constraints when selecting model size | Larger models need more memory |
| Test multiple models for your specific use case | Different models excel at different tasks |

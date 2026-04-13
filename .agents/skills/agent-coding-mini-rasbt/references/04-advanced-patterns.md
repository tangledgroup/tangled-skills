# Advanced Patterns: Configuration, Approval Modes, and Customization

This document covers advanced usage patterns including approval modes, bounded delegation strategies, model configuration, prompt customization, CLI options, and troubleshooting techniques.

## Approval Modes

Risky tools (`run_shell`, `write_file`, `patch_file`) are gated by approval policies.

### Mode: ask (Default)

Prompts before each risky operation:

```bash
python mini_coding_agent.py --approval ask
```

**Behavior:**
```
approve write_file {"path": "binary_search.py", "content": "..."}? [y/N] 
```

- Type `y` or `yes` to approve
- Type `n`, `no`, or press Enter to deny
- EOF (non-interactive) defaults to deny

**Use cases:**
- Interactive development sessions
- Human-in-the-loop safety
- Learning what the agent wants to do
- Production environments requiring oversight

### Mode: auto

Automatically approve all risky operations:

```bash
python mini_coding_agent.py --approval auto
```

**Behavior:**
- No prompts for risky tools
- Agent can execute commands and modify files freely
- **WARNING**: Model has arbitrary command execution capability

**Use cases:**
- Automated CI/CD pipelines (trusted repos only)
- Quick prototyping in isolated environments
- Testing agent capabilities
- Trusted prompts and repositories only

**Security considerations:**
- Only use with trusted codebases
- Model could execute destructive commands (`rm -rf`, etc.)
- Model could overwrite important files
- Consider sandboxing (containers, VMs) for untrusted work

### Mode: never

Deny all risky operations:

```bash
python mini_coding_agent.py --approval never
```

**Behavior:**
- `write_file`, `patch_file`, `run_shell` always fail
- Agent can only read files and search
- Useful for investigation-only sessions

**Use cases:**
- Codebase exploration without modification risk
- Read-only analysis tasks
- Safe mode for untrusted environments
- Subagents (automatically set to never)

## Bounded Delegation Strategies

The `delegate` tool creates read-only subagents with limited scope.

### Default Delegation

```xml
<tool>{"name":"delegate","args":{"task":"Summarize the architecture in src/main.py","max_steps":3}}</tool>
```

Creates a subagent with:
- `read_only=True` (cannot modify files)
- `approval_policy="never"` (risky tools denied)
- `max_steps=3` (limited iterations)
- `depth=1` (cannot create further subagents)
- Inherited context from parent history

### Delegation Use Cases

#### Investigate Before Modifying

```xml
<tool>{"name":"delegate","args":{"task":"Read all files in tests/ and summarize the testing patterns used","max_steps":5}}</tool>
```

Parent agent gets investigation results without using its own step budget.

#### Research Code Patterns

```xml
<tool>{"name":"delegate","args":{"task":"Search for all uses of WorkspaceContext and report how it's instantiated","max_steps":4}}</tool>
```

Subagent explores codebase, parent receives findings.

#### Parallel Investigation (Manual)

Ask multiple delegations for different aspects:

```
Parent: Investigate the authentication module
Delegate 1: "Read auth/login.py and summarize the flow"
Delegate 2: "Search for session management patterns"
Delegate 3: "Check what dependencies are used for auth"
```

Then synthesize findings in parent agent.

### Delegation Limitations

**Depth limit:** Default `max_depth=1` means:
- Root agent (depth 0) can create subagents (depth 1)
- Subagents (depth 1) cannot create further subagents

**Read-only:** Subagents cannot:
- Write or modify files
- Execute shell commands
- Make any workspace changes

**Context inheritance:** Subagents get:
- Same workspace context (files, git state)
- Compressed parent history as notes (300 chars)
- Their own separate session

## Model Configuration

### Ollama Model Selection

Different models have different capabilities:

```bash
# Default (works with limited RAM)
python mini_coding_agent.py --model qwen3.5:4b

# Better instruction following (if memory allows)
python mini_coding_agent.py --model qwen3.5:9b

# Other Qwen 3.5 variants
python mini_coding_agent.py --model qwen3.5:14b
python mini_coding_agent.py --model qwen3.5:32b

# Alternative models
python mini_coding_agent.py --model llama3.1:8b
python mini_coding_agent.py --model mistral:7b
```

**Model recommendations:**
- **Qwen 3.5 family**: Best instruction following for tool use
- **Larger models**: Better at complex reasoning and format adherence
- **Smaller models**: Faster, lower memory, may need simpler prompts

### Ollama Server Configuration

#### Custom Host

If Ollama is running on a different host:

```bash
python mini_coding_agent.py --host http://localhost:11434
python mini_coding_agent.py --host http://192.168.1.100:11434
```

#### Connection Timeout

Increase timeout for slow models or networks:

```bash
python mini_coding_agent.py --ollama-timeout 600  # 10 minutes
```

Default is 300 seconds (5 minutes).

### Generation Parameters

#### Temperature

Control randomness in generation:

```bash
# More deterministic (default)
python mini_coding_agent.py --temperature 0.2

# More creative/varied
python mini_coding_agent.py --temperature 0.7

# Very deterministic
python mini_coding_agent.py --temperature 0.0
```

**Recommendations:**
- `0.0-0.3`: Coding tasks, tool use (deterministic)
- `0.3-0.5`: General tasks with some variation
- `0.5+`: Creative tasks (not recommended for coding agents)

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

**How it works:** Samples from smallest set of tokens with cumulative probability >= top_p

#### Max Tokens

Limit output length per step:

```bash
# Default (good for tool calls)
python mini_coding_agent.py --max-new-tokens 512

# Longer responses
python mini_coding_agent.py --max-new-tokens 1024

# Short, concise responses
python mini_coding_agent.py --max-new-tokens 256
```

**Considerations:**
- Tool calls should fit within limit
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
- Each tool call = 1 step
- Final answer = not a step (terminates loop)
- Retry notices = not a step (malformed responses)

**Stopping conditions:**
- Agent emits `<final>` before max_steps
- Max steps reached without final answer
- Too many malformed responses (max_attempts = max(3*max_steps, max_steps+4))

### Step Budget Management

For complex tasks, manage step budget:

```
Task: Implement feature with tests and run them

Optimal flow (~6 steps):
1. read_file existing code
2. write_file implementation
3. write_file tests
4. run_shell pytest
5. patch_file fix issues (if needed)
6. final answer

If step 4 fails, may need more steps for fixes
```

**Strategies:**
- Break large tasks into multiple user requests
- Use delegation for investigation (doesn't use parent steps)
- Set higher max_steps for complex multi-file changes

## CLI Reference

Complete command-line interface documentation:

```bash
python mini_coding_agent.py --help
```

### Positional Arguments

**prompt** (optional, variable):
One-shot prompt to execute and exit (non-interactive mode).

```bash
python mini_coding_agent.py "Create a hello_world.py file"
```

### Workspace Options

**--cwd** (default: "."):
Workspace directory the agent should inspect and modify.

```bash
python mini_coding_agent.py --cwd /path/to/project
python mini_coding_agent.py --cwd ./src/module
```

### Model Connection Options

**--model** (default: "qwen3.5:4b"):
Ollama model name to use.

```bash
python mini_coding_agent.py --model qwen3.5:9b
python mini_coding_agent.py --model llama3.1:8b
```

**--host** (default: "http://127.0.0.1:11434"):
Ollama server URL.

```bash
python mini_coding_agent.py --host http://localhost:11434
python mini_coding_agent.py --host http://192.168.1.100:11434
```

**--ollama-timeout** (default: 300):
Ollama request timeout in seconds.

```bash
python mini_coding_agent.py --ollama-timeout 600
```

### Session Options

**--resume** (default: None):
Resume a saved session by ID or use "latest".

```bash
python mini_coding_agent.py --resume latest
python mini_coding_agent.py --resume 20260413-143022-a1b2c3
```

### Approval Options

**--approval** (default: "ask", choices: "ask", "auto", "never"):
Approval policy for risky tools.

```bash
python mini_coding_agent.py --approval ask    # Interactive prompts
python mini_coding_agent.py --approval auto   # No prompts (trusted env only)
python mini_coding_agent.py --approval never  # Read-only mode
```

### Generation Limits

**--max-steps** (default: 6):
Maximum tool/model iterations per user request.

```bash
python mini_coding_agent.py --max-steps 12
```

**--max-new-tokens** (default: 512):
Maximum model output tokens per step.

```bash
python mini_coding_agent.py --max-new-tokens 1024
```

### Sampling Parameters

**--temperature** (default: 0.2):
Sampling temperature for generation.

```bash
python mini_coding_agent.py --temperature 0.0  # Deterministic
python mini_coding_agent.py --temperature 0.5  # More varied
```

**--top-p** (default: 0.9):
Top-p nucleus sampling value.

```bash
python mini_coding_agent.py --top-p 0.7  # More focused
python mini_coding_agent.py --top-p 0.95 # More diverse
```

## Complete Example Workflows

### Workflow 1: New Feature Implementation

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
mini-coding-agent> /memory
```

Review what was accomplished.

```
mini-coding-agent> /exit
```

### Workflow 2: Codebase Investigation

```bash
# Read-only investigation mode
python mini_coding_agent.py --approval never
```

```
mini-coding-agent> Investigate this codebase and summarize the architecture. What design patterns are used? How is the project organized?
```

Agent uses search, read_file, and delegate to explore.

```
mini-coding-agent> Create a README.md documenting the project structure and key components based on your investigation.
```

Denied (approval never), but agent can provide documentation text.

### Workflow 3: Automated Pipeline (Trusted Env Only)

```bash
# CI/CD pipeline with auto approval
python mini_coding_agent.py --approval auto --max-steps 10 \
  "Fix all failing tests in the repository"
```

Agent autonomously:
1. Runs tests to see failures
2. Reads failing test files
3. Reads related source files
4. Patches bugs
5. Re-runs tests
6. Repeats until all pass or max_steps reached

### Workflow 4: Resume Interrupted Work

```bash
# Next day, resume where you left off
python mini_coding_agent.py --resume latest
```

```
mini-coding-agent> Continue from where we stopped. We were working on the payment processing module.
```

Agent has full context from previous session.

## Troubleshooting

### Model Not Following Format

**Symptom:** Agent repeatedly outputs malformed tool calls or plain text instead of `<tool>`/`<final>` tags.

**Solutions:**
1. **Try a larger model:**
   ```bash
   python mini_coding_agent.py --model qwen3.5:9b
   ```

2. **Lower temperature for more deterministic output:**
   ```bash
   python mini_coding_agent.py --temperature 0.0
   ```

3. **Check model supports tool use:** Some models need specific training for structured output.

4. **Simplify the task:** Complex prompts may confuse smaller models.

### Ollama Connection Errors

**Symptom:** "Could not reach Ollama" or connection timeout errors.

**Diagnosis:**
```bash
# Check if Ollama is running
ollama --help

# Test API endpoint
curl http://127.0.0.1:11434/api/tags

# Check model is loaded
ollama list
```

**Solutions:**
1. **Start Ollama server:**
   ```bash
   ollama serve
   ```

2. **Pull the model:**
   ```bash
   ollama pull qwen3.5:4b
   ```

3. **Increase timeout for slow models:**
   ```bash
   python mini_coding_agent.py --ollama-timeout 600
   ```

4. **Check host configuration:**
   ```bash
   python mini_coding_agent.py --host http://localhost:11434
   ```

### Tool Validation Errors

**Symptom:** "invalid arguments for <tool>" errors.

**Common causes:**
- Path doesn't exist or is wrong type (file vs directory)
- Missing required arguments
- `old_text` in patch_file occurs 0 or >1 times
- Command empty in run_shell

**Solutions:**
1. **Read file first** before patching to get exact text
2. **List directory** before reading to verify paths
3. **Check argument schemas** in tool reference
4. **Use XML format** for multi-line content to avoid escaping issues

### Repeated Tool Call Errors

**Symptom:** "repeated identical tool call" error.

**Cause:** Agent called same tool with same arguments twice in a row.

**Solutions:**
1. **Provide more specific follow-up:** Guide agent to next step
2. **Reset session:** `/reset` to clear history
3. **Break task into smaller steps:** One file at a time

### Session Issues

**Symptom:** Memory not updating, files not tracked.

**Diagnosis:**
```bash
# Check session is being saved
python mini_coding_agent.py
/session  # Note the path
ls -lt <session_path>  # Should update after each turn
```

**Solutions:**
1. **Verify tool calls succeed:** Failed tools don't update memory
2. **Check disk space:** Session saves may fail silently
3. **Manual reset:** `/reset` to clear corrupted state

### Performance Issues

**Symptom:** Slow responses, high memory usage.

**Optimizations:**
1. **Use smaller model:** `qwen3.5:4b` instead of larger variants
2. **Reduce max_tokens:** `--max-new-tokens 256` for faster responses
3. **Limit steps:** `--max-steps 4` for quicker iterations
4. **Close other applications:** Free up RAM for Ollama

## Customization and Extension

### Modifying Tool Definitions

Tools are defined in `build_tools()` method:

```python
def build_tools(self):
    tools = {
        "list_files": {
            "schema": {"path": "str='.'"},
            "risky": False,
            "description": "List files in the workspace.",
            "run": self.tool_list_files,
        },
        # Add custom tools here
    }
```

To add a custom tool:
1. Define schema and metadata
2. Implement `tool_custom_name(self, args)` method
3. Add validation in `validate_tool()` method
4. Add example in `tool_example()` dictionary

### Custom Workspace Context

Modify `WorkspaceContext.build()` to collect additional context:

```python
# Add custom fields
class WorkspaceContext:
    def __init__(self, ..., custom_field):
        # ... existing fields ...
        self.custom_field = custom_field
    
    @classmethod
    def build(cls, cwd):
        # ... existing code ...
        custom_data = subprocess.run(
            ["custom-command"], capture_output=True, text=True
        ).stdout
        return cls(..., custom_field=custom_data)
    
    def text(self):
        # ... existing output ...
        return "\n".join([existing_text, f"- custom: {self.custom_field}"])
```

### Custom Approval Logic

Override `approve()` method for custom approval workflows:

```python
def approve(self, name, args):
    # Custom logic before default behavior
    if name == "run_shell" and "rm -rf" in args.get("command", ""):
        return False  # Always deny dangerous commands
    
    # Default approval flow
    return super().approve(name, args)
```

## Best Practices

### Task Scoping

- **One file per request** for complex edits
- **Read before write** to understand context
- **Test incrementally** after each change
- **Use delegation** for investigation tasks

### Session Management

- **Resume for continuity** on multi-day projects
- **Reset for fresh start** when context polluted
- **Backup important sessions** before major changes
- **Clean up old sessions** periodically

### Safety

- **Use `--approval ask`** in production environments
- **Review tool calls** before approving destructive operations
- **Test in isolated environments** with `--approval auto`
- **Monitor subagent actions** even though read-only

### Model Selection

- **Start with qwen3.5:4b** for baseline performance
- **Upgrade to larger models** if format issues occur
- **Consider RAM constraints** when selecting model size
- **Test multiple models** for your specific use case

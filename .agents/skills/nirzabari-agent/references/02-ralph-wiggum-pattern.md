# Ralph Wiggum Pattern

The simplest working agentic coding system and what it teaches us about harness engineering.

## The Pattern

Geoffrey Huntley created this technique and ran it to build entire programming languages:

```bash
while :; do cat PROMPT.md | claude-code --dangerously-skip-permissions; done
```

That's it. At a Y Combinator hackathon, a team used it to ship 6 repos overnight. No orchestrator, no tool registry, no safety layer - just a model in a loop, reading a prompt file, writing code, and looping back.

**Key insight**: The feedback loop is everything. Program in ways where the agent can evaluate itself - add logging, compile the application and inspect output.

## How It Works

1. Agent reads PROMPT.md with instructions
2. Executes tasks, writes code
3. Loops back, reads prompt again
4. Continues until human intervenes

When something went wrong, Huntley tuned the prompt, "like tuning a guitar." When the agent drifted too far, he'd `git reset --hard` and start again.

## Why It Works

### Strong Feedback Loops

The agent can see its own output and errors immediately. If code doesn't compile, the error message becomes part of the next iteration's context. This creates a tight feedback loop similar to how humans debug.

### No Over-Engineering

No complex orchestration layer, no state management, no tool registry. Just prompt + model + loop. The simplicity means fewer failure modes and easier debugging.

### Git as Recovery Mechanism

When things go wrong, `git reset --hard` provides clean recovery. Version control becomes the persistence and rollback layer.

## Limitations

### No Context Management

The model eventually drowns in its own output. There's no compaction, summarization, or selective context loading. Long-running sessions degrade as context window fills.

### No Safety Boundary

The `--dangerously-skip-permissions` flag is right there in the name. Agent can execute any command, modify any file. No approvals, no sandboxing, no allowlists.

### No Persistence

Kill the process and state is gone. No event logs, no replay capability, no way to resume from interruption.

### No Recovery Mechanisms

When the agent loops on the same bug for an hour, nobody notices. No circuit breakers, no timeout detection, no automatic intervention.

### Placeholder Implementation Bias

Huntley found that agents have inherent bias toward minimal and placeholder implementations. His solution was blunt:

> "DO NOT IMPLEMENT PLACEHOLDER OR SIMPLE IMPLEMENTATIONS. WE WANT FULL IMPLEMENTATIONS. DO IT OR I WILL YELL AT YOU."

This works but requires explicit anti-placeholder instructions in the prompt.

## When to Use This Pattern

### Good For

- Quick prototypes and experiments
- Learning how agents behave
- Simple, well-scoped tasks
- Environments where you trust the agent completely
- Situations where git reset is acceptable recovery

### Not Good For

- Production systems
- Multi-user environments
- Tasks requiring long context windows
- Safety-critical operations
- Projects needing audit trails or replay

## The Gap to Production

The gap between this one-liner and what Codex, Cursor, or Claude Code actually ship is **the entire subject of harness engineering**. That gap is product engineering.

Production agents add:

1. **Context management** - Compaction, selective loading, summary
2. **Safety boundaries** - Approvals, policies, sandboxes
3. **Persistence** - Event logs, state storage, replay
4. **Recovery mechanisms** - Circuit breakers, timeout detection, human intervention points
5. **Multi-client support** - TUI, web, IDE interfaces
6. **Tool orchestration** - Typed tool calls, approval workflows
7. **Extensibility** - Plugins, MCP, custom tools

## Lessons for Harness Design

### 1. Feedback Loops Are Critical

The Ralph Wiggum pattern works because of tight feedback. Production harnesses must preserve this while adding safety and management. Agents need to see their own output and errors quickly.

### 2. Simplicity Has Value

Complex orchestration layers add failure modes. The simplest thing that works is often better than the most sophisticated system. Many improvements in agent systems came from **removing** complexity, not adding it.

### 3. Prompt Quality Matters More Than Architecture

Huntley's success came from prompt tuning, not system design. Extensive prompt experimentation often matters more than architectural choices. The "perfect prompt" doesn't exist, but good prompts matter enormously.

### 4. Git Is a Great Recovery Mechanism

Version control provides natural rollback and state management. Production agents should integrate with git workflows, not replace them.

### 5. Anti-Placeholder Instructions Are Essential

Agents naturally drift toward minimal implementations. Explicit instructions about completeness and quality are necessary, especially for production code.

## Comparison: Ralph Wiggum vs Production Agents

| Aspect | Ralph Wiggum | Production Agent |
|--------|-------------|------------------|
| **Context Management** | None - eventually drowns | Compaction, selective loading, summary |
| **Safety** | None - `--dangerously-skip-permissions` | Approvals, policies, sandboxes |
| **Persistence** | None - kill process = lose state | Event logs, state storage, replay |
| **Recovery** | Git reset | Circuit breakers, timeouts, intervention points |
| **Tool Calls** | Whatever model generates | Typed schemas, approval workflows |
| **Multi-Client** | Single terminal | TUI, web, IDE interfaces |
| **Extensibility** | Prompt only | Plugins, MCP, custom tools |
| **Complexity** | Minimal | Moderate to high |
| **Safety** | None | Defense-in-depth |
| **Debuggability** | Git history | Event logs, replay, state inspection |

## Practical Implementation

If you want to experiment with this pattern:

```bash
# Create your prompt file
cat > PROMPT.md << 'EOF'
You are an expert software engineer. Your task is to [describe task].

IMPORTANT GUIDELINES:
- DO NOT implement placeholder or simple implementations
- Write complete, production-ready code
- Add logging so you can see what your code does
- Compile/test after making changes to verify they work
- If you encounter errors, fix them in the next iteration
- Be thorough and complete in your implementations

Current progress: [agent fills this in]
Next steps: [agent fills this in]
EOF

# Run the loop
while :; do 
    cat PROMPT.md | claude-code --dangerously-skip-permissions
done
```

**Warning**: Use `--dangerously-skip-permissions` only in trusted environments. Production systems should never skip safety checks.

## References

- **Original Article**: https://ghuntley.com/ralph/
- **Venture Beat Coverage**: "How Ralph Wiggum went from The Simpsons to the biggest name in AI"
- **Y Combinator Case Study**: https://github.com/repomirrorhq/repomirror/blob/main/repomirror.md
- **The Register**: "Like tuning a guitar" - https://www.theregister.com/2026/01/27/ralph_wiggum_claude_loops/

## Key Takeaways

1. **Simple loops work surprisingly well** - Don't over-engineer prematurely
2. **Feedback loops are everything** - Agents need to see their own output and errors
3. **Prompt tuning > architecture** - Good prompts matter more than complex systems
4. **Git provides natural recovery** - Version control is a great rollback mechanism
5. **Safety matters for production** - The pattern lacks all safety boundaries
6. **Context management limits scale** - No compaction means eventual degradation
7. **Placeholder bias is real** - Explicit anti-placeholder instructions are essential

The Ralph Wiggum pattern proves that agentic coding works with minimal infrastructure. Production harnesses add safety, management, and scalability on top of this simple foundation.

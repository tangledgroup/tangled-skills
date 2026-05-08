# Execution Model

## Contents
- Sequential Evaluation
- Context Propagation
- Output Formats Between Stages
- Timing and Concurrency

## Sequential Evaluation

Pipes execute strictly left-to-right. Stage N+1 does not begin until Stage N completes. There is no parallel execution within a single pipe expression.

```
/pipe stage-A | stage-B | stage-C
        ↓           ↓           ↓
     runs first  runs second  runs third
```

Each stage receives the full accumulated context from all preceding stages, not just the immediately previous one. This means Stage C has access to the outputs of both Stage A and Stage B.

### Accumulated Context

The context grows monotonically through the pipe:

- **Stage 1**: Receives the original user request + any prior conversation context
- **Stage 2**: Receives everything from Stage 1 plus Stage 1's output
- **Stage N**: Receives everything from Stage N-1 plus Stage N-1's output

The agent should manage context size intelligently — if accumulated context becomes excessive, prioritize the most recent and relevant outputs.

## Context Propagation

Context propagation follows these rules:

1. **Tool/script output** (e.g., `bash`, file reads): The raw stdout/stderr or file content is added to context
2. **Skill invocation**: The skill's execution result (typically a summary or structured output) is added to context
3. **Free-text reasoning**: The agent's generated text response is added to context
4. **MCP calls**: The MCP tool's return value is added to context

The next stage implicitly sees all propagated context without needing explicit references. For example:

```
/pipe read src/main.py | find function definitions
```

The second stage (`find function definitions`) automatically has access to the content of `src/main.py` from the first stage — it doesn't need to re-read the file.

## Output Formats Between Stages

There are no enforced output format contracts between stages. Each stage produces whatever output is natural for its operation, and the next stage interprets that context as needed.

However, for reliability, prefer structured outputs when the next stage depends on specific data:

- **Lists/tables**: When the next stage needs to iterate over items
- **JSON/YAML blocks**: When the next stage needs named fields
- **Markdown headings**: When the next stage needs to locate sections

Example of intentional output formatting:

```
/pipe read config.yaml | extract database settings as JSON | validate connection string
```

Here, the second stage explicitly outputs JSON so the third stage can parse structured fields.

## Timing and Concurrency

- **No parallelism**: All stages execute sequentially within a single pipe
- **No timeouts per stage**: Each stage runs to completion (or failure) before the next begins
- **No reordering**: Stages always execute in the order written, left-to-right
- **Cross-pipe concurrency**: Multiple independent pipes can execute concurrently if the agent chooses to split work

If parallelism is needed, use separate pipe expressions rather than a single pipe with implicit parallel stages.

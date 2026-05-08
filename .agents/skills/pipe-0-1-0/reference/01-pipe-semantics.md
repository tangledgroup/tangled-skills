# Pipe Semantics

## Contents
- Grammar Specification
- Stage Resolution Algorithm
- Output Capture and Injection
- Pipe Buffer Rules

## Grammar Specification

### Pipe Expression

```
pipe := "|" stage ( "|" stage )*
```

A pipe expression starts with `|` followed by at least one stage. Each additional stage is preceded by `|`. Whitespace around `|` is optional but recommended for readability.

### Stage

```
stage := <free-text-instruction>
```

A stage is free text — no formal subgrammar. The agent resolves it semantically (see Stage Resolution Algorithm below).

### Examples of Valid Pipes

```
| search for "rust programming" | summarize top 3 results
| read src/main.py | find all function definitions | list them with line numbers
| bash ls -la | filter hidden files | count them
```

### Examples of Invalid Pipes

```
search for "rust" | summarize          # Missing leading |
| search for "rust"                    # Single stage is valid but pointless (no piping)
|                                        # Empty pipe, no stages
```

A single-stage pipe (`| stage1`) is syntactically valid but functionally equivalent to just executing the stage directly. Use pipes only when chaining 2+ stages.

## Stage Resolution Algorithm

When the agent encounters a stage, it resolves it using this priority order:

### Step 1: Check for Tool Prefix

If the stage starts with a known tool name followed by a space or argument:

- `bash <command>` → Execute via bash tool
- `read <path>` → Execute via read tool
- `write <path>` → Execute via write tool
- `edit <path>` → Execute via edit tool

The remaining text after the tool name is treated as arguments.

### Step 2: Check for Skill Match

Search available skills by keyword matching against skill names and descriptions. If a stage contains words that match a skill's name or key terms in its description, resolve to that skill.

**Matching strategy**: Prefer exact name matches over partial matches. If multiple skills match, choose the most specific one (longest name overlap or best description match).

**Example**: `scrapling get https://example.com` → matches skill `scrapling-0-4-7` by name keyword "scrapling". The instruction "get https://example.com" is passed to the skill's execution context.

### Step 3: Check for MCP Tool Match

If the stage name or pattern matches an available MCP tool, resolve to that MCP tool with remaining text as arguments.

### Step 4: Default — Raw Instruction

If no tool, skill, or MCP tool matches, treat the entire stage as a raw agent instruction. The agent executes it directly using its general capabilities, with the pipe buffer as additional context.

**Example**: `summarize in three bullets` → No specific skill/tool match. Agent summarizes the pipe buffer content into three bullet points.

## Output Capture and Injection

### Capture

After a stage completes, capture its output:

| Stage Type | Output Source |
|------------|---------------|
| Tool invocation | Tool's return text / stdout |
| Skill execution | The skill's produced output (text, file content, structured data) |
| MCP tool | Tool result text |
| Raw instruction | The agent's response text for that stage |

### Injection

The captured output is injected into the next stage as **pipe buffer context**. The agent should treat it as:

> "Here is the output from the previous stage. Use it as input/context for executing this stage."

The injection is implicit — the agent doesn't need explicit markers. It simply has the previous output in its working context when executing the next stage.

### Multi-Stage Context Chain

In a 3-stage pipe, Stage 3 only receives Stage 2's output (not Stage 1's raw output). If Stage 3 needs information from Stage 1, Stage 2 must have preserved it in its output. This mirrors Unix pipes where each command only sees the previous command's stdout.

If you need earlier context to persist, explicitly carry it forward:

```
| search for "rust" | extract URLs and keep search query | scrape first URL and note what we searched for
```

## Pipe Buffer Rules

### Size Limits

- **Hard limit**: 50KB or 2000 lines (whichever is hit first)
- If output exceeds limits, truncate to the limit and append: `[output truncated: N of M lines]`
- Truncation preserves the beginning of output (head-first), as earlier content is typically more relevant

### Summarization Trigger

Before injecting the pipe buffer into the next stage, check if the next stage's instruction implies a reduction operation. If so, summarize the buffer first rather than injecting raw content.

**Triggers**: "summarize", "extract", "list", "count", "find", "filter", "parse", "format"

**Non-triggers**: "read", "search", "scrape", "get", "fetch" (these produce output, they don't reduce)

**Example**: If Stage 1 produces 50KB of scraped HTML and Stage 2 is `summarize the content`, summarize the 50KB before injecting — don't dump raw megatext into context.

### Empty Buffer

If a stage produces no meaningful output (empty result, zero matches, error with no data):

- The pipe buffer is empty for the next stage
- Default behavior: fail-fast (stop the pipe, report the failure)
- If explicitly instructed otherwise (e.g., "continue even if empty"), proceed with empty context

### Buffer Reset

The pipe buffer is overwritten (not appended) at each stage. Only the most recent stage's output is available. There is no accumulated history — this mirrors Unix pipes where `cmd1 | cmd2 | cmd3` means cmd3 only sees cmd2's output.

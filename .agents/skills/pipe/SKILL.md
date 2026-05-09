---
name: pipe
description: Unix-style pipe expression syntax for chaining multiple agent operations sequentially. Each stage's output becomes the next stage's implicit context, enabling multi-step workflows in a single expression. Use when chaining 2+ operations where intermediate results feed into subsequent steps — e.g., search then summarize, read then analyze, transform then report.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.1"
tags:
  - pipe
  - meta
  - meta-skill
  - chaining
  - workflow
  - orchestration
category: meta
---

# Pipe — Unix-Style Chaining for LLM Agents

## Overview

Pipe provides a unix-pipe-like expression syntax for chaining multiple agent operations sequentially. Just as `grep | sort | uniq` passes data through a pipeline of shell commands, `/pipe stage1 | stage2 | stage3` passes context through a sequence of agent stages.

Each stage is evaluated left-to-right. The output (or result context) of one stage implicitly becomes the input context for the next stage. Stages can invoke skills, call tools, invoke MCP servers, or execute free-text instructions — the agent resolves each stage independently based on available capabilities.

## When to Use

- Chaining 2+ operations where intermediate results feed into subsequent steps
- Composing multi-step workflows in a single expression (search → summarize, read → analyze → report)
- Breaking complex requests into explicit sequential stages for clearer execution
- Combining different capability types in one flow (tool call → skill invocation → free-text reasoning)

Do not use pipes for single operations — a single-stage pipe is functionally equivalent to executing the stage directly.

## Syntax & Grammar

```
pipe := stage ( "|" stage )*
stage := <free-text-instruction>
```

A pipe expression starts with at least one stage. Each additional stage is preceded by `|`. Whitespace around `|` is optional but recommended for readability.

**Never start or end a line with `|`** — this is treated as a markdown table delimiter and will confuse the user, agent, and LLM.

### Valid Pipes

Example 1:
```
/pipe search for "rust programming" | summarize top 3 results | read src/main.py | find all function definitions | list them with line numbers | bash ls -la | filter hidden files | count them
```

Example 2:
```
/pipe search for "rust programming" | summarize top 3 results |
read src/main.py | find all function definitions | list them with line numbers |
bash ls -la | filter hidden files | count them
```


A single-stage pipe is syntactically valid but pointless — use pipes only when chaining 2+ stages.

### Escaping `|` Inside a Stage

When a stage's free-text instruction contains a literal `|`, quote it with backticks or parentheses:

```
/pipe read config.yaml | extract field "type | category"
```

Here `"type | category"` inside quotes is treated as literal text within the second stage, not as a pipe delimiter. The agent should parse `|` delimiters at the top level only — ignoring `|` characters that appear inside quoted strings, backticks, or parentheses.

## Execution Model

Pipes execute **sequentially, left-to-right**. Each stage:

1. Receives the accumulated context from all previous stages
2. Resolves to a capability (skill, tool, MCP call, or free-text instruction)
3. Executes and produces output
4. Passes its output as implicit context to the next stage

If any stage fails, the pipe stops by default (fail-fast). The agent may report partial results from stages that completed before the failure.

## Stage Resolution

Each stage is a free-text instruction. The agent resolves it by checking available capabilities in this priority order:

1. **Skill match** — Does an available skill's description match this stage's intent?
2. **Tool call** — Is there a built-in tool that performs this operation?
3. **MCP call** — Is there an MCP server with a relevant tool/resource?
4. **Free-text interpretation** — Treat as a direct instruction to the agent

The agent should resolve each stage independently — different stages in the same pipe can invoke different capability types.

## Advanced Topics

**Execution Model**: Sequential evaluation rules, context propagation, output passing → [Execution Model](reference/01-execution-model.md)

**Stage Resolution**: How the agent resolves free-text to skills, tools, and MCP calls → [Stage Resolution](reference/02-stage-resolution.md)

**Error Handling**: Failure modes, error propagation strategies, recovery patterns → [Error Handling](reference/03-error-handling.md)

**Advanced Patterns**: Multi-line pipes, composition with other meta-skills, reusable templates → [Advanced Patterns](reference/04-advanced-patterns.md)

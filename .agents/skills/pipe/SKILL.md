---
name: pipe
description: Unix-style pipe expression syntax for chaining multiple agent operations sequentially. Each stage's output becomes the next stage's implicit context, enabling multi-step workflows in a single expression. Use when chaining 2+ operations where intermediate results feed into subsequent steps — e.g., search then summarize, read then analyze, transform then report.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.3"
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

Each stage is evaluated left-to-right. The output (or result context) of one stage implicitly becomes the input context for the next stage. Stages can invoke skills, call tools, invoke MCP servers, or execute free-text instructions — the agent analyzes each stage independently to determine its intent.

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

A pipe expression starts with at least one stage. Each additional stage is preceded by ` | `. Whitespace around `|` is recommended for readability.

**Always keep pipes on a single line.** Starting a line with `|` triggers markdown table rendering and will corrupt the pipe expression. For long pipes, enclose the entire expression in a code block.

### Valid Pipes

Example 1 — Research workflow:
```
/pipe search for "rust async runtime comparison" | summarize top 3 results | generate comparison table
```

Example 2 — Code analysis workflow:
```
/pipe read src/main.py | find all function definitions | list them with line numbers | count total functions
```

Example 3 — Long pipe in a code block:
```
/pipe search for "distributed consensus algorithms" | summarize top 5 results | extract key terms from summaries | generate comparison table
```

A single-stage pipe is syntactically valid but pointless — use pipes only when chaining 2+ stages.

### Escaping `|` Inside a Stage

When a stage's free-text instruction contains a literal `|`, wrap it in backticks, double quotes, or parentheses. The agent parses `|` delimiters at the top level only — ignoring `|` characters inside quoted strings, backticks, or parentheses.

```
/pipe read config.yaml | extract field `type | category`
```

Here `` `type | category` `` inside backticks is treated as literal text within the second stage, not as a pipe delimiter.

## Execution Model

Pipes execute **sequentially, left-to-right**. Each stage:

1. Receives the accumulated context from all previous stages
2. Is analyzed by the agent to determine its intent (skill, tool, MCP, or free-text)
3. Executes and produces output
4. Passes its output as implicit context to the next stage

If any stage fails, the pipe stops by default (fail-fast). The agent may report partial results from stages that completed before the failure.

## Stage Resolution

Each stage is a free-text instruction. Stages are heterogeneous — they may invoke skills, call built-in tools, invoke MCP servers, or be free-text instructions to the agent's reasoning. The agent must analyze each stage to determine its intent.

### Skill-First Guardrail

**Before resolving any stage as a shell command or free-text instruction, check if a skill can handle it.**

When a stage mentions a project name, tool name, domain keyword, or operation that could match an available skill, the agent **must** run `list-skills.sh` with relevant filters before falling back to bash or free-text:

```bash
bash scripts/list-skills.sh --filter <keyword>
```

Extract keywords from the stage text (project names, tool names, domain terms) and use them as filters. If the filter returns matching skills, load the most specific one and let it handle the stage. **Only if no skills match** should the agent fall through to built-in tools, MCP calls, or free-text interpretation.

This prevents the agent from guessing shell commands (e.g., `curl`, `grep`, `bash`) when a dedicated skill exists for the operation.

### Resolution Priority

1. **Skill invocation** — Run `list-skills.sh --filter <keyword>` to check for matching skills. If found, use the skill and let it handle its own logic.
2. **Tool call** — Is there a built-in tool (read, bash, edit, write) that performs this operation?
3. **MCP call** — Is there an MCP server with a relevant tool/resource?
4. **Free-text interpretation** — Treat as a direct instruction to the agent's reasoning.

The agent should resolve each stage independently — different stages in the same pipe can invoke different capability types.

### Stage Analysis Principles

- **Stages carry diverse intent**: A stage might be a skill invocation, a free-text instruction, a tool call, or a reasoning prompt. Analyze the stage content before deciding.
- **Never reinterpret skill logic**: Once a skill is selected for a stage, let the skill make its own decisions. The pipe orchestrates the chain but does not control how individual skills operate.
- **Prefer specificity**: When multiple skills could match, choose the narrowest scope that satisfies the stage.
- **Never guess shell commands over skills**: If a stage's keywords match any skill, use the skill. Do not invent bash commands to replicate what a skill already provides.
- **Fallback gracefully**: Only interpret as free-text or bash if no skill matches and no tool/MCP applies.

## Advanced Topics

**Execution Model**: Sequential evaluation rules, context propagation, output passing → [Execution Model](reference/01-execution-model.md)

**Stage Resolution**: Script-assisted resolution, stage analysis, capability mapping → [Stage Resolution](reference/02-stage-resolution.md)

**Error Handling**: Failure modes, error propagation strategies, recovery patterns → [Error Handling](reference/03-error-handling.md)

**Advanced Patterns**: Multi-line pipes, composition with meta-skills, reusable templates → [Advanced Patterns](reference/04-advanced-patterns.md)

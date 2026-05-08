---
name: pipe-0-1-0
description: Unix pipe-inspired function composition for LLM agents. Chains multiple operations (skills, tools, MCP tools, user instructions) into sequential pipelines where output of one stage feeds into the next. Use when multi-step workflows need to be expressed as a single composable expression, chaining search→scrape→summarize, extract→transform→load, or any pipeline of agent capabilities.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - pipe
  - composition
  - chaining
  - workflow
  - meta-skill
category: meta
---

# Pipe 0.1.0

## Overview

Pipe is a Unix pipe-inspired function composition pattern for LLM agents. It lets you chain multiple operations — skills, tools, MCP tools, and raw instructions — into a single sequential pipeline where the output of one stage becomes the input context for the next.

The `|` character separates stages. Each stage executes to completion, its output is captured, and that output is injected as context into the following stage. This mirrors Unix pipes (`cmd1 | cmd2 | cmd3`) but operates at the agent instruction level rather than process I/O.

```
| duckduckgo search for "Tangled Group" | scrapling get first result URL | summarize in three bullets
```

This pipe: searches the web → scrapes the top result → summarizes it. Three stages, one expression.

## When to Use

- Chaining multiple skills or tools into a sequential workflow
- Expressing multi-step data transformations as a single pipeline (search→scrape→summarize, read→parse→transform)
- Combining different capabilities (web search, file reading, code analysis) in one composable expression
- Reducing back-and-forth by expressing the full workflow upfront rather than step-by-step

**Do not use pipes for:**
- Single-step operations (just invoke the skill/tool directly)
- Tasks requiring parallel execution (pipes are strictly sequential)
- Workflows with conditional branching (use explicit if/else logic instead)
- Chains longer than 5 stages (token budget degrades; split into multiple pipes)

## Core Concepts

### Pipe Syntax

A pipe expression uses `|` as the stage separator:

```
| stage1 | stage2 | stage3
```

Each stage is a free-text instruction that the agent resolves and executes. The leading `|` marks the start of a pipe expression.

### Stage Types

Each stage resolves to one of these types:

| Type | Example | Resolution |
|------|---------|------------|
| **Skill reference** | `scrapling get https://example.com` | Match against available skills by keyword, load skill context, execute with instruction |
| **Tool invocation** | `bash grep -r "TODO" src/` | Recognize tool name prefix, invoke with remaining text as arguments |
| **MCP tool** | `mem0_search "recent decisions"` | Match against available MCP tools, invoke with piped input as context |
| **Raw instruction** | `summarize in three bullets` | Execute as a direct agent instruction with no special resolution |

### Output Flow

1. Stage N executes and produces output (text, JSON, file content, tool result)
2. Output is captured into the **pipe buffer**
3. Pipe buffer contents are injected as context into Stage N+1
4. The agent uses the buffered output to inform its next action

### Pipe Buffer

The pipe buffer holds the output of the most recently executed stage. Rules:

- **Full pass-through**: By default, all output passes to the next stage
- **Truncation**: If output exceeds ~2000 lines or 50KB, truncate to the first 2000 lines and note the truncation
- **Summarization trigger**: If the next stage's instruction implies summarization (e.g., "summarize", "extract key points"), summarize the buffer before injecting — do not dump raw megatext into context
- **Empty buffer**: If a stage produces no output, the next stage receives an empty pipe buffer and should proceed with its own context

### Execution Model

Pipes execute strictly sequentially. Each stage must complete (success or failure) before the next begins. The agent processes stages left-to-right, capturing and injecting output at each step.

**Fail-fast**: If any stage fails, stop the pipe immediately and report which stage failed, what was attempted, and the error. Do not continue to subsequent stages.

## Usage Examples

### Search → Scrape → Summarize

```
| duckduckgo search for "Tangled Group" | scrapling get first result URL | summarize in three bullets
```

1. Searches DuckDuckGo, captures JSON results
2. Extracts the first result URL, scrapes it with Scrapling, captures Markdown
3. Summarizes the scraped content into three bullet points

### Read → Parse → Transform

```
| read config.yaml | extract all database settings | format as a markdown table
```

1. Reads a YAML config file
2. Extracts only the database-related settings from the YAML
3. Formats those settings as a clean Markdown table

### Tool Chain with Raw Instructions

```
| bash find . -name "*.py" -type f | filter files modified in last 7 days | count them and list by directory
```

1. Finds all Python files recursively
2. Filters to only recently modified files
3. Counts and groups them by directory

### Error Case (Fail-Fast)

```
| duckduckgo search for "nonexistent-topic-xyz-12345" | scrapling get first result URL | summarize
```

If the search returns zero results, Stage 2 fails (no URL to scrape). The pipe stops immediately and reports:

> **Pipe failed at Stage 2** (`scrapling get first result URL`): No URLs found in search results. Stage 1 produced 0 results for query "nonexistent-topic-xyz-12345".

## Advanced Topics

**Pipe Semantics**: Detailed grammar, stage resolution algorithm, buffer mechanics → [Pipe Semantics](reference/01-pipe-semantics.md)

**Stage Patterns**: Common composition patterns, anti-patterns, token budgeting → [Stage Patterns](reference/02-stage-patterns.md)

**Error Handling**: Fail-fast semantics, recovery patterns, debugging → [Error Handling](reference/03-error-handling.md)

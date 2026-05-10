---
name: agent-coding-mini-rasbt-0-1-0
description: Minimal standalone coding agent framework by Sebastian Raschka backed by Ollama, providing workspace context collection, tool execution with approval gates, session persistence, and subagent delegation. Use when building lightweight local coding agents for file manipulation, shell commands, code editing, or automated workflows without external API dependencies.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - coding-agent
  - ollama
  - local-ai
  - autonomous-agent
  - python
  - tool-use
  - memory
category: ai-agents
external_references:
  - https://github.com/rasbt/mini-coding-agent
  - https://magazine.sebastianraschka.com/p/components-of-a-coding-agent
---

# Mini-Coding-Agent

## Overview

Mini-Coding-Agent is a minimal standalone coding agent framework by Sebastian Raschka. It runs entirely locally through Ollama with zero Python runtime dependencies beyond the standard library. The agent operates in an interactive REPL loop, accepting natural language tasks and executing them through structured tools — file reads, writes, patches, shell commands, and search — with approval gates for risky operations.

The entire codebase is a single `mini_coding_agent.py` file (~600 lines) organized around six core architectural components: live repo context, prompt shape with cache reuse, structured tools with validation and permissions, context reduction and output management, transcripts with memory and resumption, and bounded subagent delegation.

## When to Use

- Building or studying a minimal coding agent architecture from scratch
- Operating a local AI coding assistant backed by Ollama (no cloud API keys needed)
- Understanding how coding agents manage workspace context, tool use, memory, and session persistence
- Creating test-driven development workflows with autonomous code generation
- Learning the patterns behind agent harnesses: prompt construction, tool parsing, approval gates, and context management
- Extending or adapting the six-component agent architecture for custom use cases

## Core Concepts

### Six Component Architecture

The agent is organized around six practical building blocks:

1. **Live Repo Context** — The agent collects stable workspace facts upfront: repo layout, git state, branch info, recent commits, and key documentation files. This context is injected into every prompt so the model always knows what it is working with.

2. **Prompt Shape and Cache Reuse** — A stable prompt prefix (rules, tools, workspace context) is separated from the changing transcript and user request. This allows Ollama's prompt caching to reuse static parts efficiently across turns.

3. **Structured Tools, Validation, and Permissions** — The model works through named tools with checked inputs, workspace path validation, and approval gates. No free-form arbitrary actions — every tool call is validated before execution.

4. **Context Reduction and Output Management** — Long outputs are clipped, repeated reads are deduplicated, and older transcript entries are compressed to keep prompt size under control. Write operations clear read deduplication so the model sees updated content.

5. **Transcripts, Memory, and Resumption** — The runtime keeps both a full durable transcript (saved as JSON) and a smaller working memory (task, tracked files, notes). Sessions can be resumed while preserving important state.

6. **Delegation and Bounded Subagents** — Scoped subtasks can be delegated to read-only child agents that inherit enough context to help but operate within strict limits (max depth, read-only mode, no risky tools).

### Tool Protocol

The agent expects the model to emit one of two response types:

- **Tool call** — `<tool>{"name":"tool_name","args":{...}}</tool>` for JSON-style, or XML-style `<tool name="write_file" path="file.py"><content>...</content></tool>` for multi-line content
- **Final answer** — `<final>your answer</final>`

The parser handles both formats and provides retry notices when the model returns malformed output.

### Approval Policy

Risky tools (`run_shell`, `write_file`, `patch_file`) are gated by approval:

- `ask` — prompts the user before risky actions (default, recommended)
- `auto` — allows risky actions automatically (use only with trusted prompts and repos)
- `never` — denies all risky actions

### Session Persistence

Sessions are saved as JSON files under `.mini-coding-agent/sessions/` in the workspace root. Each session contains:

- `id` — timestamped unique identifier
- `created_at` — ISO timestamp
- `workspace_root` — absolute path to the repo root
- `history` — full transcript of user messages, tool calls, and model responses
- `memory` — distilled working memory with task, tracked files, and notes

## Installation / Setup

### Prerequisites

- Python 3.10+
- Ollama installed and running (`ollama serve`)
- An Ollama model pulled locally (default: `qwen3.5:4b`)

### Quick Start

```bash
git clone https://github.com/rasbt/mini-coding-agent.git
cd mini-coding-agent
python mini_coding_agent.py
```

Or with `uv` for the CLI entry point:

```bash
uv run mini-coding-agent
```

### Key CLI Flags

- `--cwd <path>` — workspace directory (default: `.`)
- `--model <name>` — Ollama model name (default: `qwen3.5:4b`)
- `--host <url>` — Ollama server URL (default: `http://127.0.0.1:11434`)
- `--approval <mode>` — approval policy: `ask`, `auto`, or `never` (default: `ask`)
- `--max-steps <n>` — max tool/model iterations per request (default: `6`)
- `--max-new-tokens <n>` — max model output tokens per step (default: `512`)
- `--temperature <f>` — sampling temperature (default: `0.2`)
- `--resume <id|latest>` — resume a saved session

### Interactive Commands

Inside the REPL:

- `/help` — list available slash commands
- `/memory` — print distilled working memory
- `/session` — print path to current session JSON
- `/reset` — clear session history and memory
- `/exit` or `/quit` — exit the agent

## Usage Examples

### One-shot prompt

```bash
python mini_coding_agent.py --cwd ./my-project "Create a hello.py that prints hello world"
```

### Interactive session with auto-approval

```bash
uv run mini-coding-agent --cwd ./my-project --approval auto
```

### Resume the latest session

```bash
uv run mini-coding-agent --resume latest
```

### Point at a custom Ollama host and model

```bash
python mini_coding_agent.py \
  --host http://remote-server:11434 \
  --model "qwen3.5:9b" \
  --max-steps 10
```

## Advanced Topics

**Six Components Deep Dive**: Architecture breakdown of workspace context, prompt shape, tools, context reduction, memory, and delegation → [Six Components](reference/01-six-components.md)

**Tool Reference**: Complete reference for all seven built-in tools with schemas, validation rules, and examples → [Tool Reference](reference/02-tool-reference.md)

**Session and Memory System**: Transcript persistence, working memory distillation, session resumption, and the FakeModelClient testing pattern → [Session and Memory](reference/03-session-and-memory.md)

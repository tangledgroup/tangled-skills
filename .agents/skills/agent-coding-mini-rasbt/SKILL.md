---
name: agent-coding-mini-rasbt
description: A minimal standalone coding agent framework by Sebastian Raschka backed by Ollama that provides workspace context collection, structured tool execution with approval gates, session persistence, memory distillation, and bounded subagent delegation. Use when building or operating lightweight local coding agents for file manipulation, shell command execution, code editing, test-driven development, and automated workflows without external API dependencies.
version: "0.3.0"
author: Sebastian Raschka <https://github.com/rasbt>
license: MIT
tags:
  - coding-agent
  - ollama
  - local-llm
  - python
  - agent-harness
  - development-tools
  - workspace-management
category: development
external_references:
  - https://github.com/rasbt/mini-coding-agent
  - https://magazine.sebastianraschka.com/p/components-of-a-coding-agent
---

# Mini-Coding-Agent

A minimal standalone coding agent harness by Sebastian Raschka that runs entirely locally using Ollama as the model backend. The framework demonstrates how a **coding harness** — the software scaffold around an LLM — can dramatically improve coding capabilities beyond what plain chat interfaces achieve.

## Conceptual Foundation

### LLM vs Reasoning Model vs Agent

Understanding the architecture requires distinguishing three layers:

| Layer | Role | Analogy |
|-------|------|---------|
| **LLM** | Raw next-token prediction model | The engine |
| **Reasoning model** | LLM optimized for intermediate reasoning and self-verification | A beefed-up engine |
| **Agent harness** | Control loop that decides what to inspect, which tools to call, how to update state, and when to stop | The driver + navigation system |

A coding harness is a special-purpose agent harness for software engineering. It manages code context, tool use, execution, permissions, caching, memory, and iterative feedback. **The harness often matters more than the model choice** — a good harness can make even modest models feel significantly more capable.

### The Agent Loop

At its core, every coding agent follows an observe-inspect-choose-act loop:

```
observe → inspect → choose → act → (loop back)
   ↑                                    │
   └─────────────────────────────────────┘
```

1. **Observe**: Collect information from the environment (file contents, git state, test output)
2. **Inspect**: Analyze that information to understand current state
3. **Choose**: Select the next action based on the goal and current state
4. **Act**: Execute a tool call (read file, write code, run command)

The harness provides the plumbing that makes this loop efficient: stable prompt caching, context reduction, memory distillation, and bounded delegation.

## When to Use

- Building a lightweight coding agent that runs entirely locally without external API dependencies
- Automating file manipulation, code editing, and shell command execution in Python projects
- Creating development workflows with human-in-the-loop approval for risky operations
- Implementing session persistence to resume interrupted coding tasks
- Delegating scoped investigation tasks to bounded read-only subagents
- Learning about coding agent architecture patterns and implementation details
- Understanding how tools like Claude Code or Codex CLI wrap LLMs in a coding harness

## Setup

### Prerequisites

1. **Python 3.10+** installed on your system
2. **Ollama** installed and running:
   ```bash
   # Install Ollama from https://ollama.com/download
   ollama serve  # Run in background or separate terminal
   ```
3. **Pull a model** (recommended: Qwen 3.5 family for instruction following):
   ```bash
   ollama pull qwen3.5:4b    # Default, works with limited RAM
   ollama pull qwen3.5:9b    # Better performance if memory allows
   ```

### Installation

Clone the repository:
```bash
git clone https://github.com/rasbt/mini-coding-agent.git
cd mini-coding-agent
```

Optional: Use `uv` for environment management and CLI entry point:
```bash
uv sync
```

### Verification

Verify Ollama is running:
```bash
ollama --help
curl http://127.0.0.1:11434/api/tags  # Should list available models
```

## Quick Start

### Basic Usage (Interactive REPL)

Start the agent in the current directory:
```bash
cd mini-coding-agent
python mini_coding_agent.py
# or with uv:
uv run mini-coding-agent
```

### Target a Specific Workspace

Point the agent at a different project directory:
```bash
python mini_coding_agent.py --cwd /path/to/your/project
```

### One-Shot Prompt (Non-Interactive)

Execute a single task and exit:
```bash
python mini_coding_agent.py "Create a binary_search.py file with iterative implementation"
```

### Resume an Interrupted Session

Resume the most recent session:
```bash
python mini_coding_agent.py --resume latest
```

Resume a specific session by ID:
```bash
python mini_coding_agent.py --resume 20260413-143022-a1b2c3
```

## Interactive Commands

While the agent is running, slash commands are handled directly by the REPL (not sent to the model):

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/memory` | Print distilled working memory (task, tracked files, notes) |
| `/session` | Show path to current session JSON file |
| `/reset` | Clear history and memory but stay in REPL |
| `/exit` or `/quit` | Exit the agent |

## Complete CLI Reference

```bash
python mini_coding_agent.py --help
```

| Flag | Default | Description |
|------|---------|-------------|
| `prompt` (positional) | — | One-shot prompt to execute and exit |
| `--cwd` | `.` | Workspace directory to inspect/modify |
| `--model` | `qwen3.5:4b` | Ollama model name |
| `--host` | `http://127.0.0.1:11434` | Ollama server URL |
| `--ollama-timeout` | `300` | Ollama request timeout in seconds |
| `--resume` | — | Session ID to resume or `latest` |
| `--approval` | `ask` | Approval policy: `ask`, `auto`, or `never` |
| `--max-steps` | `6` | Maximum tool/model iterations per request |
| `--max-new-tokens` | `512` | Maximum model output tokens per step |
| `--temperature` | `0.2` | Sampling temperature (lower = more deterministic) |
| `--top-p` | `0.9` | Top-p nucleus sampling value |

## Example Workflow

See [EXAMPLE.md](https://github.com/rasbt/mini-coding-agent/blob/main/EXAMPLE.md) in the repository for a complete hands-on workflow that demonstrates:

1. Creating a fresh repo
2. Launching the agent with `--cwd`
3. Implementing `binary_search.py` from a natural language prompt
4. Editing the implementation with follow-up instructions
5. Adding pytest unit tests
6. Running tests and fixing failures
7. Inspecting the final repo state

## Six Architecture Components

The framework is organized around six practical building blocks:

1. **Live Repo Context** — Workspace snapshot collected upfront (git state, docs, layout)
2. **Prompt Shape & Cache Reuse** — Stable prefix separated from changing session state
3. **Structured Tools, Validation & Permissions** — Named tools with checked inputs and approval gates
4. **Context Reduction & Output Management** — Truncation, deduplication, and transcript compression
5. **Transcripts, Memory & Resumption** — Full durable transcript + compact working memory
6. **Delegation & Bounded Subagents** — Scoped read-only helper agents for investigation

## File Structure

```
mini-coding-agent/
├── mini_coding_agent.py          # Single-file implementation (~1000 lines)
├── pyproject.toml                # Project config with CLI entry point
├── LICENSE                       # MIT License
├── README.md                     # Repository documentation
├── EXAMPLE.md                    # Complete hands-on workflow example
└── tests/
    └── test_mini_coding_agent.py # Pytest unit tests
```

The entire agent is implemented in a **single Python file** with zero external dependencies beyond the standard library. This makes it easy to read, understand, and modify.

## Reference Files

- [`references/01-core-concepts.md`](references/01-core-concepts.md) — Six architecture components: workspace context, prompt shape, structured tools, context reduction, session memory, and subagent delegation
- [`references/02-tool-reference.md`](references/02-tool-reference.md) — Complete tool API reference with schema, examples, and validation rules for all 7 tools
- [`references/03-session-management.md`](references/03-session-management.md) — Session persistence, memory distillation, transcript management, resumption workflows, and interactive commands
- [`references/04-advanced-patterns.md`](references/04-advanced-patterns.md) — Approval modes, bounded delegation, model configuration, CLI options, troubleshooting, and extension patterns

## Troubleshooting

### Ollama Connection Errors

If you see "Could not reach Ollama" errors:
```bash
# Verify Ollama is running
ollama serve

# Check the default port
curl http://127.0.0.1:11434/api/tags

# Specify custom host if needed
python mini_coding_agent.py --host http://localhost:11434
```

### Model Not Following Format

If the model doesn't emit `<tool>...</tool>` or `<final>...</final>` tags:
- Try a larger model (qwen3.5:9b instead of qwen3.5:4b)
- Lower temperature for more deterministic output: `--temperature 0.0`
- Use models with better instruction-following capabilities
- Check for "malformed tool output" retry notices in the transcript

### Approval Prompts Not Showing

If running in non-interactive mode:
```bash
# Use auto approval for trusted environments only
python mini_coding_agent.py --approval auto

# Or use never to deny all risky operations
python mini_coding_agent.py --approval never
```

### Repeated Tool Call Errors

If the agent gets stuck calling the same tool with the same arguments:
- Provide more specific follow-up instructions
- Reset session: `/reset`
- Break task into smaller steps

See [Advanced Patterns](references/04-advanced-patterns.md) for detailed configuration and troubleshooting.

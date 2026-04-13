---
name: rasbt-mini-coding-agent
description: A minimal standalone coding agent framework backed by Ollama that provides workspace context collection, structured tool execution with approval gates, session persistence, and bounded subagent delegation for local development tasks. Use when building or operating lightweight coding agents for file manipulation, shell command execution, code editing, and automated development workflows without external API dependencies.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - coding-agent
  - ollama
  - local-llm
  - python
  - automation
  - development-tools
  - workspace-management
category: development
required_environment_variables:
  - name: OLLAMA_HOST
    prompt: "Ollama server URL (default: http://127.0.0.1:11434)"
    help: "The URL where Ollama server is running. Start with 'ollama serve' command."
    required_for: "model inference"
  - name: OLLAMA_MODEL
    prompt: "Ollama model name (default: qwen3.5:4b)"
    help: "Name of the pulled Ollama model, e.g., qwen3.5:4b, qwen3.5:9b, llama3.1:8b"
    required_for: "model inference"
---

# Mini-Coding-Agent

A minimal standalone coding agent framework that runs entirely locally using Ollama as the model backend. The agent provides six core components for workspace context collection, structured tool execution with approval gates, session persistence and memory management, output truncation and deduplication, and bounded subagent delegation for complex tasks.

## When to Use

- Building a lightweight coding agent that runs entirely locally without external API dependencies
- Automating file manipulation, code editing, and shell command execution in Python projects
- Creating development workflows with human-in-the-loop approval for risky operations
- Implementing session persistence to resume interrupted coding tasks
- Delegating scoped investigation tasks to bounded read-only subagents
- Learning about coding agent architecture patterns and implementation details

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

Optional: Use `uv` for environment management:
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

### Basic Usage

Start the agent in the current directory:
```bash
cd mini-coding-agent
python mini_coding_agent.py
```

Or with `uv`:
```bash
uv run mini-coding-agent
```

### Target a Specific Workspace

Point the agent at a different project directory:
```bash
python mini_coding_agent.py --cwd /path/to/your/project
```

### One-Shot Prompt

Execute a single task and exit:
```bash
python mini_coding_agent.py "Create a binary_search.py file with iterative implementation"
```

### Common Workflows

See [Core Concepts](references/01-core-concepts.md) for detailed explanations of the six architecture components.

See [Tool Reference](references/02-tool-reference.md) for complete tool syntax and examples.

See [Session Management](references/03-session-management.md) for persistence, memory, and resumption patterns.

See [Advanced Patterns](references/04-advanced-patterns.md) for delegation, approval modes, and customization.

## Reference Files

- [`references/01-core-concepts.md`](references/01-core-concepts.md) - Six architecture components: workspace context, prompt shape, structured tools, context reduction, session memory, and subagent delegation
- [`references/02-tool-reference.md`](references/02-tool-reference.md) - Complete tool API reference with schema, examples, and validation rules for list_files, read_file, search, run_shell, write_file, patch_file, and delegate
- [`references/03-session-management.md`](references/03-session-management.md) - Session persistence, memory distillation, transcript management, resumption workflows, and interactive commands
- [`references/04-advanced-patterns.md`](references/04-advanced-patterns.md) - Approval modes, bounded delegation, model configuration, prompt customization, and troubleshooting

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/mini-coding-agent/`). All paths are relative to this directory.

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

See [Advanced Patterns](references/04-advanced-patterns.md) for detailed configuration options.

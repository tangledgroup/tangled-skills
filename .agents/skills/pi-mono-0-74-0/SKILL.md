---
name: pi-mono-0-74-0
description: >-
  Complete toolkit for the pi coding agent monorepo v0.74.0 covering five packages:
  pi-coding-agent (interactive CLI), pi-ai (unified LLM API), pi-agent-core (agent runtime),
  pi-tui (terminal UI framework), and pi-web-ui (web chat components). Provides provider setup,
  extension authoring, SDK embedding, session management, and customization guidance.
  Use when building, extending, or integrating with the pi coding agent ecosystem — writing extensions,
  configuring providers, embedding via SDK, or troubleshooting pi's interactive mode.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - pi
  - pi-mono
  - coding-agent
  - ai-agent
  - terminal-ai
  - extensions
  - llm-api
category: tooling
external_references:
  - https://github.com/earendil-works/pi/tree/v0.74.0
  - https://github.com/earendil-works/website
---

# Pi Monorepo v0.74.0

## Overview

Pi is a minimal terminal coding harness. The monorepo contains five packages that form a complete stack for building AI agent applications:

| Package | Description |
|---------|-------------|
| `@earendil-works/pi-coding-agent` | Interactive coding agent CLI with extensions, skills, and themes |
| `@earendil-works/pi-ai` | Unified multi-provider LLM API (20+ providers, streaming, tool calls) |
| `@earendil-works/pi-agent-core` | Agent runtime with tool execution, event streaming, and state management |
| `@earendil-works/pi-tui` | Terminal UI framework with differential rendering and flicker-free output |
| `@earendil-works/pi-web-ui` | Web components for AI chat interfaces built on mini-lit web components |

Pi's philosophy: **aggressively extensible, minimal core**. Features other tools bake in (sub-agents, plan mode, permission popups) are built via extensions or installed as pi packages. The core provides four default tools (`read`, `write`, `edit`, `bash`) and everything else is optional.

## When to Use

- Installing or configuring pi for coding agent workflows
- Writing pi extensions (custom tools, commands, event handlers, UI components)
- Configuring LLM providers, OAuth authentication, or custom models
- Embedding pi programmatically via the SDK in your own applications
- Building web chat interfaces with pi-web-ui components
- Understanding session management, branching, and compaction
- Debugging tool execution, streaming events, or provider integration
- Creating pi packages to share extensions, skills, prompts, or themes

## Core Concepts

### Extension-First Architecture

Pi ships with minimal built-in features. Extend it via:
- **Extensions** — TypeScript modules that register tools, commands, event handlers, and UI components
- **Skills** — On-demand capability packages (Agent Skills standard)
- **Prompt Templates** — Reusable prompts with variable substitution
- **Themes** — Visual customization with hot-reload
- **Pi Packages** — Bundled extensions/skills/prompts/themes shared via npm or git

### Four Run Modes

| Mode | Flag | Use Case |
|------|------|----------|
| Interactive | (default) | Full TUI with editor, commands, and streaming |
| Print | `-p` | Single-shot: send prompt, get response, exit |
| JSON | `--mode json` | Structured event output for parsing |
| RPC | `--mode rpc` | JSON-RPC over stdin/stdout for subprocess integration |

### Session Tree Model

Sessions use a tree structure (JSONL files with `id`/`parentId`). Navigate with `/tree`, fork branches with `/fork`, clone with `/clone`. All history preserved in one file.

### Progressive Context Loading

Only skill descriptions are always in context. Full skill content loads on-demand via `read`. This applies to skills, prompt templates, and extensions — the system prompt stays lean.

## Installation

```bash
npm install -g @earendil-works/pi-coding-agent
```

Or via curl installer:

```bash
curl -fsSL https://pi.dev/install.sh | sh
```

Authenticate with an API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pi
```

Or use subscription login (Anthropic Pro/Max, ChatGPT Plus/Pro, GitHub Copilot):

```
/login   # Interactive provider selection
```

### Package Dependencies

For development, install all packages from the monorepo root:

```bash
cd pi-mono
npm install
npm run build
npm run check
./test.sh
```

## Usage Examples

### Basic interactive use

```bash
pi "List all TypeScript files in src/"
```

### Non-interactive with piped input

```bash
cat README.md | pi -p "Summarize this text"
```

### Switch models mid-session

```
/model          # Open model selector
Ctrl+L          # Same as /model
Ctrl+P          # Cycle scoped models forward
Shift+Ctrl+P    # Cycle scoped models backward
```

### Session management

```bash
pi -c                          # Continue most recent session
pi -r                          # Browse and select from past sessions
pi --session <file-or-uuid>    # Use specific session
pi --fork <file-or-uuid>       # Fork existing session
pi --no-session                # Ephemeral mode (don't save)
```

### Read-only mode for code review

```bash
pi --tools read,grep,find,ls -p "Review the codebase architecture"
```

### High thinking level for complex problems

```bash
pi --thinking high "Solve this complex problem"
# Or with model shorthand:
pi --model sonnet:high "Analyze this deeply"
```

### Extension: custom tool with permission gate

Create `~/.pi/agent/extensions/safe-bash.ts`:

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName === "bash" && event.input.command?.includes("rm -rf")) {
      const ok = await ctx.ui.confirm("Dangerous!", "Allow rm -rf?");
      if (!ok) return { block: true, reason: "Blocked by user" };
    }
  });
}
```

### SDK: embed pi in your app

```typescript
import { AuthStorage, createAgentSession, ModelRegistry, SessionManager } from "@earendil-works/pi-coding-agent";

const authStorage = AuthStorage.create();
const modelRegistry = ModelRegistry.create(authStorage);
const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),
  authStorage,
  modelRegistry,
});

session.subscribe((event) => {
  if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
});

await session.prompt("What files are in the current directory?");
```

## Advanced Topics

**Coding Agent CLI**: Interactive mode, commands, sessions, branching, compaction, keybindings → [Coding Agent](reference/01-coding-agent.md)

**Providers & Models**: 20+ providers, OAuth login, custom models, environment variables, settings → [Providers and Models](reference/02-providers-and-models.md)

**Extensions API**: Event system, lifecycle, custom tools, UI components, commands, flags → [Extensions](reference/03-extensions.md)

**SDK & Integration**: Programmatic embedding, RPC mode, print mode, web-ui components → [SDK and Integration](reference/04-sdks-and-integration.md)

**pi-ai Package**: Unified LLM API, streaming events, tool calls, thinking, cross-provider handoffs → [pi-ai Package](reference/05-pi-ai-package.md)

**Agent Core & TUI**: Agent runtime, event flow, parallel tool execution, terminal UI components → [Agent Core and TUI](reference/06-agent-core-and-tui.md)

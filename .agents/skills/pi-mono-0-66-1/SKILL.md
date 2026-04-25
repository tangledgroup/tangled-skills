---
name: pi-mono-0-66-1
description: Complete implementation guide for pi-mono monorepo architecture covering provider abstraction, agent runtime, terminal UI rendering, extension system, session management, and tool implementation patterns.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - TypeScript
  - AI agents
  - LLM
  - terminal UI
  - coding agents
  - architecture
category: development
external_references:
  - https://www.npmjs.com/package/@mariozechner/pi-coding-agent
  - https://pi.dev/
  - https://github.com/badlogic/pi-skills
  - https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples/extensions/
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/tui.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/tree.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/themes.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/settings.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/session.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/providers.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/prompt-templates.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/packages.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/models.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/keybindings.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/json.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/development.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/custom-provider.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/compaction.md
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md
  - https://github.com/badlogic/pi-mono
  - https://github.com/anthropics/skills
  - https://discord.com/invite/3cU7Bz4UPx
required_environment_variables: []
---

# Pi Mono v0.66.1

## Overview

Pi Mono is a minimal, terminal-based coding agent framework designed to be adapted to your workflows rather than forcing you to adapt to it. Pi ships with powerful defaults but skips features like sub-agents and plan mode - instead, you ask pi to build what you want or install third-party packages that match your workflow.

The project consists of four core packages that work together:
- **@mariozechner/pi-ai**: Unified LLM API supporting 15+ providers (Anthropic, OpenAI, Google, Azure, Bedrock, Mistral, Groq, Cerebras, xAI, Hugging Face, Kimi For Coding, MiniMax, OpenRouter, Vercel AI Gateway, Ollama, and more)
- **@mariozechner/pi-agent**: Stateful agent runtime with tool execution, event streaming, and queue management for steering/follow-ups
- **@mariozechner/pi-tui**: Terminal UI framework with flicker-free differential rendering and component system
- **@mariozechner/pi-coding-agent**: The main CLI application combining all three packages

Pi runs in four modes:
1. **Interactive (TUI)**: Full terminal interface with editor, message history, and keyboard shortcuts
2. **Print/JSON**: Output responses as text or structured JSON lines
3. **RPC**: Process integration via stdin/stdout JSONL protocol
4. **SDK**: Embed pi in your own Node.js applications programmatically

All modes share the same core logic but use different input/output layers.

## When to Use

Use this skill when:

- **Building custom coding agents**: You need a minimal foundation to extend rather than fighting against built-in features you don't want
- **Understanding agent architecture**: You want to learn how production coding agents are structured internally
- **Creating terminal-based AI tools**: You're building CLI applications that interact with LLMs
- **Extending existing workflows**: You need to add custom tools, UI components, or authentication flows to pi
- **Studying extensibility patterns**: You want examples of plugin architectures, event-driven design, and layered abstractions

**Don't use this skill** if you just want to run pi as a user - see the official README for usage instructions. This skill focuses on implementation details for developers who want to understand or extend pi's architecture.

## Core Concepts

### Design Philosophy

Pi is built on **minimalism and extensibility**. Unlike feature-heavy agents with built-in sub-agents, plan modes, MCP support, and permission gates, pi provides powerful defaults that you extend yourself. The philosophy: "Adapt pi to your workflows, not the other way around."

**Key design decisions:**

1. **No MCP**: MCP servers dump 7-9% of context window on startup with tools you'll never use. Instead, build CLI tools with README files - progressive disclosure means you only pay token costs when needed.

2. **No sub-agents**: Black-box sub-agents have zero observability and poor context transfer. If you need parallel work, spawn pi via bash (optionally in tmux for full visibility). Better yet: gather context in a separate session first, create an artifact, then use it in a fresh session.

3. **No plan mode**: Ephemeral planning confuses models. Write plans to files (`PLAN.md`) - they're versioned with code, shareable across sessions, and editable collaboratively.

4. **No built-in to-dos**: To-do lists add state that models struggle to track. Use a `TODO.md` file with checkboxes instead - simple, visible, under your control.

5. **No background bash**: Background process management adds complexity with poor observability. Use tmux instead - full visibility, direct interaction, CLI to list sessions, and you can co-debug with the agent.

6. **No permission popups**: Security theater. If an agent can write code and run commands, it's game over anyway. Run in a container if you need isolation, or build your own confirmation flow via extensions.

7. **YOLO by default**: Unrestricted filesystem access, no safety rails, no command pre-checking. Everybody runs in YOLO mode to get work done - why pretend otherwise?

8. **Minimal system prompt**: ~1000 tokens total (system prompt + tool definitions). Models are RL-trained to understand coding agents - they don't need 10,000 tokens of instructions.

9. **Minimal toolset**: Four tools (`read`, `bash`, `edit`, `write`) are all you need. Optional read-only tools (`grep`, `find`, `ls`) for exploration mode. Models know how to use these - they've been trained on similar schemas.

10. **Context engineering**: Pi's minimal system prompt and extensibility let you do actual context engineering. Control what goes into the context window via AGENTS.md, SYSTEM.md, skills, and extensions.

### Layered Architecture

Pi is built in four distinct layers, each with a single responsibility:

**Layer 1: pi-ai (LLM Abstraction)**
This layer provides a unified interface to 15+ LLM providers with 2000+ models. Instead of writing separate code for OpenAI, Anthropic, Google, etc., you work with one API that handles all the differences.

**Key innovations:**
- **Lazy loading**: Providers are only loaded when used, keeping bundle size small and enabling browser compatibility
- **Unified streaming events**: Every provider has different streaming format; pi-ai normalizes them into single event types (`text_delta`, `thinking_delta`, `toolcall_delta`, `done`, `error`)
- **Abort support**: Full abort controller integration throughout pipeline (unlike most unified APIs that ignore this)
- **Partial results**: When aborted, you get partial content instead of nothing
- **Structured tool results**: Tools return both `content` (for LLM) and `details` (for UI display) - no need to parse textual outputs for restructuring
- **TypeBox validation**: Tool arguments automatically validated with AJV, detailed error messages on failure
- **Cost tracking**: Per-message token usage by type (input, output, cache read/write) with cost calculation
- **Model registry**: Built-in catalog of 2000+ models with metadata (capabilities, pricing, context window)
- **Custom models**: Define self-hosted endpoints (Ollama, vLLM, Mistral) via simple model objects
- **Provider SDKs**: Uses official provider SDKs under the hood (OpenAI SDK, Anthropic SDK, etc.) for full feature support

**Layer 2: pi-agent-core (Agent Runtime)**
This layer wraps pi-ai into an agent loop via the `Agent` class. You define tools, the agent calls the LLM, executes tools, feeds results back, and repeats until done.

**Key features:**
- **Event-driven**: Emits events at every step (`agent_start`, `turn_start`, `message_update`, `tool_execution_start/end`, `agent_end`)
- **Steering**: Interrupt agent mid-turn - message delivered after current tool finishes, remaining pending tools skipped
- **Follow-ups**: Queue messages for after agent finishes naturally without interrupting current work
- **State management**: Change model, thinking level, system prompt, or tools at any time (picked up on next turn)
- **Parallel tool execution**: Independent tools execute in parallel for speed
- **Tool validation**: TypeBox schemas validated with AJV before execution, errors returned to LLM for retry
- **Streaming tool results**: `onUpdate` callback in tools allows streaming partial results during long-running execution
- **Transport abstraction**: Run agent directly or through proxy for RPC/SDK modes

**Layer 3: pi-tui (Terminal UI)**
This layer provides a retained-mode component framework for terminals using differential rendering.

**Two TUI approaches:**
1. **Full-screen TUIs** (Amp, opencode): Take ownership of viewport, treat it like pixel buffer. Lose scrollback buffer, must implement custom search and scrolling.
2. **Native terminal TUIs** (Claude Code, Codex, Droid, pi): Write to terminal like CLI programs, append to scrollback buffer, occasionally move cursor up to redraw editors/spinners. Get natural scrolling, built-in search, mouse scrolling works properly.

Pi uses approach #2 - coding agents are chat interfaces with linear flow (prompt → replies → tool calls → results), perfect for native terminal emulator.

**Differential rendering algorithm:**
1. **First render**: Output all lines without clearing scrollback
2. **Width changed**: Clear screen, fully re-render (soft wrapping changes)
3. **Normal update**: Find first changed line, move cursor there, clear to end, render only changed lines
4. **Synchronized output**: Wrap in `CSI ?2026h/l` escape sequences for atomic display (no flicker in modern terminals like Ghostty, iTerm2)

**Retained mode components:**
- Components cache rendered output - unchanged components return cached lines
- Containers collect lines from children
- TUI class compares to previously rendered backbuffer, redraws only differences
- Components have `render(width)` returning string array with ANSI codes, optional `handleInput(data)` for keyboard

**Trade-offs:** Stores entire scrollback buffer worth of lines (few hundred KB for large sessions), compares many lines on each update. Worth it for dead-simple programming model and fast iteration.

**Layer 4: pi-coding-agent (Application)**
This layer combines all lower layers into a production-ready agent with built-in tools, session persistence, and extensibility.

**Built-in tool presets:**
- `codingTools`: `[read, bash, edit, write]` - default active tools
- `readOnlyTools`: `[read, grep, find, ls]` - exploration without modification
- Individual tools accessible via `allBuiltInTools.*`

**Key features:**
- **Session management**: JSONL persistence with tree structure, branching, forking
- **Context files**: AGENTS.md loaded hierarchically (global → parent dirs → project), SYSTEM.md to replace prompt, APPEND_SYSTEM.md to augment
- **Extension system**: TypeScript modules that register tools, commands, UI components, event handlers
- **Skills**: Agent Skills standard compliance with `/skill:name` commands
- **Prompt templates**: Markdown files with argument support via `/templatename`
- **Themes**: Hot-reloading color schemes
- **Package management**: Install extensions/skills/prompts/themes from npm or git
- **Four run modes**: Interactive (TUI), Print/JSON, RPC (stdin/stdout JSONL), SDK (programmatic embedding)

### Session-Based Design

Everything in pi revolves around sessions. A session is:
- A JSONL file stored in `~/.pi/agent/sessions/--<path>--/<timestamp>_<uuid>.jsonl`
- A tree structure via `id`/`parentId` fields enabling in-place branching without creating new files
- Automatically compacted when approaching context limits (proactive) or on overflow (recovery)
- Fully replayable from any point using `/tree` navigation

**Key session features:**
- **Branching**: Use `/tree` to navigate to any previous point and continue from there; all branches live in a single file
- **Forking**: `/fork` creates a new session file from the current branch, copying history up to the selected point
- **Compaction**: Summarizes older messages while keeping recent ones; fully customizable via extensions
- **Export/Share**: `/export` converts sessions to HTML; `/share` uploads as private GitHub gists with shareable URLs
- **Labels**: Mark entries as bookmarks with Shift+L in tree view for quick navigation

Sessions enable workflows like "try this risky refactoring in a branch, if it works keep it, if not discard the branch" without duplicating files.

### Event-Driven Architecture

Pi uses events for all state changes. When the agent receives a message, executes a tool, or completes a turn, it emits events that listeners can react to. This design:
- Decouples the agent logic from UI updates
- Allows streaming responses (show text as it arrives)
- Enables extensions to hook into any point in the workflow
- Makes testing easier (record and replay event sequences)

### Extension System

Pi's core is intentionally minimal - it ships with four built-in tools (`read`, `bash`, `edit`, `write`) plus optional `grep`, `find`, `ls`. Everything else is added through TypeScript extensions:

**What extensions can do:**
- **Custom tools**: Register tools callable by the LLM via `pi.registerTool()`
- **Event interception**: Block or modify tool calls, inject context, customize compaction behavior
- **User interaction**: Prompt users via `ctx.ui` (select, confirm, input, notify)
- **Custom UI components**: Full TUI components with keyboard input via `ctx.ui.custom()` for complex interactions
- **Custom commands**: Register slash commands like `/deploy` via `pi.registerCommand()`
- **Session persistence**: Store state that survives restarts via `pi.appendEntry()`
- **Custom rendering**: Control how tool calls/results and messages appear in TUI
- **Keyboard shortcuts**: Add custom keybindings
- **Status lines, headers, footers**: Augment the interface
- **Git checkpointing**: Auto-stash/commit at each turn
- **Permission gates**: Confirm before dangerous operations (`rm -rf`, `sudo`)
- **Path protection**: Block writes to sensitive files (`.env`, `node_modules/`)
- **Custom compaction**: Implement topic-based summaries or code-aware summarization
- **External integrations**: File watchers, webhooks, CI triggers
- **Games while waiting**: Yes, Doom runs in pi

**Extension locations:**
- Global: `~/.pi/agent/extensions/*.ts` or `~/.pi/agent/extensions/*/index.ts`
- Project-local: `.pi/extensions/*.ts` or `.pi/extensions/*/index.ts`
- Packages: Via `pi install npm:@foo/bar` or `pi install git:github.com/user/repo`

Extensions are loaded via jiti, so TypeScript works without compilation. Use `/reload` to hot-reload extensions in auto-discovered locations.

### Skills as Documentation

Skills are self-contained capability packages following the [Agent Skills standard](https://agentskills.io). Unlike prompt templates (which insert text) or extensions (which add code), skills provide specialized workflows, setup instructions, helper scripts, and reference documentation for specific tasks.

**How skills work:**
1. At startup, pi scans skill locations and extracts names/descriptions
2. The system prompt includes available skills in XML format per the specification
3. When a task matches, the agent uses `read` to load the full SKILL.md (models don't always do this; use `/skill:name` to force it)
4. The agent follows instructions, using relative paths from the skill directory

**Skill locations:**
- Global: `~/.pi/agent/skills/`, `~/.agents/skills/`
- Project: `.pi/skills/`, `.agents/skills/` in cwd and ancestor directories (up to git repo root)
- Packages: `skills/` directories or `pi.skills` entries in `package.json`
- CLI: `--skill <path>` (repeatable)

**Skill structure:**
```
my-skill/
├── SKILL.md              # Required: frontmatter + instructions
├── scripts/              # Helper scripts
├── references/           # Detailed docs loaded on-demand
└── assets/               # Templates, configs, etc.
```

**Skill commands:** Skills register as `/skill:name` commands. Arguments after the command are appended to skill content as `User: <args>`.

A skill can have:
- A main SKILL.md file with required frontmatter (name, description)
- Optional reference files for modular loading
- Scripts and assets referenced via relative paths

## Installation / Setup

### Installing Pi

```bash
npm install -g @mariozechner/pi-coding-agent
```

### Authentication

Pi supports two authentication methods:

**Subscriptions (OAuth):** Use `/login` in interactive mode, then select a provider:
- Claude Pro/Max
- ChatGPT Plus/Pro (Codex)
- GitHub Copilot
- Google Gemini CLI
- Google Antigravity

Use `/logout` to clear credentials. Tokens are stored in `~/.pi/agent/auth.json` and auto-refresh when expired.

**API Keys:** Set via environment variable or auth file:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=...
```

Or store in `~/.pi/agent/auth.json`:
```json
{
  "anthropic": { "type": "api_key", "key": "sk-ant-..." },
  "openai": { "type": "api_key", "key": "sk-..." }
}
```

**Key resolution order:** CLI `--api-key` flag → `auth.json` entry → environment variable → custom provider keys from `models.json`.

**Auth file key formats:**
- **Shell command**: `"!command"` executes and uses stdout (cached for process lifetime)
- **Environment variable**: Uses the value of the named variable
- **Literal value**: Used directly

**Cloud providers:** Azure OpenAI, Amazon Bedrock, and Google Vertex AI support additional configuration via environment variables (resource names, AWS credentials, GCP project/location).

### Configuration

Pi reads configuration from two locations:

**Global (`~/.pi/agent/`):**
- `settings.json`: Thinking level, theme, message delivery, transport preferences
- `keybindings.json`: Custom keyboard shortcuts
- `models.json`: Custom provider/model definitions
- `auth.json`: API keys and OAuth tokens (0600 permissions)
- `extensions/`: Directory for extension packages
- `skills/`: Directory for skill markdown files
- `prompts/`: Directory for prompt templates
- `themes/`: Directory for custom color themes
- `sessions/--<path>--/`: Session JSONL files organized by working directory

**Project-local (`.pi/`):**
- `settings.json`: Project-specific settings (override global)
- `extensions/`, `skills/`, `prompts/`, `themes/`: Project-local resources
- `SYSTEM.md`: Replace default system prompt
- `APPEND_SYSTEM.md`: Append to system prompt without replacing

**Context files:** Pi loads `AGENTS.md` (or `CLAUDE.md`) from:
- `~/.pi/agent/AGENTS.md` (global)
- Parent directories (walking up from cwd)
- Current directory

All matching AGENTS.md files are concatenated for project instructions, conventions, and common commands.

## Usage Examples

### Installation and Quick Start

```bash
# Install globally
npm install -g @mariozechner/pi-coding-agent

# Run with API key
export ANTHROPIC_API_KEY=sk-ant-...
pi

# Or use OAuth login
pi
/login  # Select provider, authenticate in browser
```

### Interactive Mode Commands

Type `/` in the editor to trigger commands:

| Command | Description |
|---------|-------------|
| `/login`, `/logout` | OAuth authentication |
| `/model` | Switch models (or Ctrl+L) |
| `/scoped-models` | Enable/disable models for Ctrl+P cycling |
| `/settings` | Thinking level, theme, message delivery, transport |
| `/resume` | Pick from previous sessions |
| `/new` | Start a new session |
| `/name <name>` | Set session display name |
| `/session` | Show session info (path, tokens, cost) |
| `/tree` | Jump to any point in the session and continue from there |
| `/fork` | Create a new session from the current branch |
| `/compact [prompt]` | Manually compact context, optional custom instructions |
| `/copy` | Copy last assistant message to clipboard |
| `/export [file]` | Export session to HTML file |
| `/share` | Upload as private GitHub gist with shareable HTML link |
| `/reload` | Reload keybindings, extensions, skills, prompts, and context files (themes hot-reload automatically) |
| `/hotkeys` | Show all keyboard shortcuts |
| `/changelog` | Display version history |
| `/quit` | Quit pi |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+C | Clear editor (twice to quit) |
| Escape | Cancel/abort (twice to open `/tree`) |
| Ctrl+L | Open model selector |
| Ctrl+P / Shift+Ctrl+P | Cycle scoped models forward/backward |
| Shift+Tab | Cycle thinking level |
| Ctrl+O | Collapse/expand tool output |
| Ctrl+T | Collapse/expand thinking blocks |
| @ | Fuzzy-search project files |
| Tab | Complete paths |
| Shift+Enter | Multi-line input (or Ctrl+Enter on Windows Terminal) |
| Ctrl+V | Paste images (Alt+V on Windows), or drag onto terminal |
| `!command` | Run bash and send output to LLM |
| `!!command` | Run bash without sending to LLM |

### Message Queue

Submit messages while the agent is working:
- **Enter**: Queues a *steering* message, delivered after current assistant turn finishes executing tool calls
- **Alt+Enter**: Queues a *follow-up* message, delivered only after agent finishes all work
- **Escape**: Aborts and restores queued messages to editor
- **Alt+Up**: Retrieves queued messages back to editor

Configure delivery in settings: `steeringMode` and `followUpMode` can be `"one-at-a-time"` (default) or `"all"`. `transport` selects provider preference (`"sse"`, `"websocket"`, or `"auto"`).

### Provider and Model Selection

Pi supports 15+ providers with hundreds of models. Switch mid-session with `/model` or Ctrl+L.

**Model selection patterns:**
```bash
# By provider and model
pi --provider anthropic --model claude-sonnet-4

# With provider prefix (no --provider needed)
pi --model openai/gpt-4o "Help me refactor"

# With thinking level shorthand
pi --model sonnet:high "Solve this complex problem"

# Limit model cycling to specific patterns
pi --models "claude-*,gpt-4o"
```

**Thinking levels:** `off`, `minimal`, `low`, `medium`, `high`, `xhigh` (set via `/settings` or Shift+Tab)

### Package Management

Install, remove, and update pi packages (extensions, skills, prompts, themes):

```bash
# Install from npm
pi install npm:@foo/pi-tools
pi install npm:@foo/pi-tools@1.2.3      # pinned version

# Install from git
pi install git:github.com/user/repo
pi install git:github.com/user/repo@v1  # tag or commit
pi install https://github.com/user/repo@v1

# Project-local install (-l flag)
pi install -l npm:@foo/pi-tools

# Manage packages
pi list          # List installed packages
pi update        # Update (skips pinned)
pi remove npm:@foo/pi-tools
pi config        # Enable/disable extensions, skills, prompts, themes
```

**Security:** Pi packages run with full system access. Review source code before installing third-party packages.

### CLI Reference

```bash
pi [options] [@files...] [messages...]
```

**Modes:**
- Default: Interactive mode
- `-p`, `--print`: Print response and exit
- `--mode json`: Output all events as JSON lines
- `--mode rpc`: RPC mode for process integration
- `--export <in> [out]`: Export session to HTML

**Session options:**
- `-c`, `--continue`: Continue most recent session
- `-r`, `--resume`: Browse and select session
- `--session <path>`: Use specific session file or partial UUID
- `--fork <path>`: Fork specific session file or partial UUID into new session
- `--no-session`: Ephemeral mode (don't save)

**Tool options:**
- `--tools <list>`: Enable specific built-in tools (default: `read,bash,edit,write`)
- `--no-tools`: Disable all built-in tools (extension tools still work)

**Resource options:**
- `-e`, `--extension <source>`: Load extension from path, npm, or git (repeatable)
- `--no-extensions`: Disable extension discovery
- `--skill <path>`: Load skill (repeatable)
- `--no-skills`: Disable skill discovery
- `--prompt-template <path>`: Load prompt template (repeatable)
- `--theme <path>`: Load theme (repeatable)

**File arguments:** Prefix files with `@` to include in the message:
```bash
pi @prompt.md "Answer this"
pi -p @screenshot.png "What's in this image?"
pi @code.ts @test.ts "Review these files"
```

### Piped Input

In print mode, pi reads piped stdin and merges it into the initial prompt:
```bash
cat README.md | pi -p "Summarize this text"
```

### Why Minimalism Works

**Benchmark results**: pi with Claude Opus 4.5 on Terminal-Bench 2.0 competed against Codex, Cursor, Windsurf, and other harnesses with native models. Results: https://github.com/laude-institute/terminal-bench (see leaderboard placement).

**Key insight**: Terminus 2 (Terminal-Bench team's own minimal agent) just gives the model a tmux session - no fancy tools, no file operations, raw terminal interaction. It holds its own against agents with sophisticated tooling. Evidence that minimal approach works.

**Why it works:**
1. **Models are RL-trained**: Frontier models inherently understand what coding agents are - they don't need 10,000 tokens of system prompt
2. **Training data**: Models trained on read/write/edit tools with similar schemas, know how to use bash
3. **Context efficiency**: ~1000 tokens for system prompt + tool definitions vs 7-9% context window waste from MCP servers
4. **Progressive disclosure**: CLI tools with READMEs only cost tokens when agent reads them (on-demand)
5. **Observability**: Full visibility into what agent does vs black-box sub-agents
6. **Workflow matters**: Context gathering in separate session → artifact → fresh session beats mid-session sub-agents

**Real-world validation**: Pi used exclusively for day-to-day work, hundreds of exchanges in single session without compaction issues. Terminal-Bench results prove contrarian design decisions work in practice.

### Understanding Provider Abstraction

When you call an LLM in pi, you don't directly invoke OpenAI or Anthropic APIs. Instead:

1. You select a model using `getModel("anthropic", "claude-sonnet-4")`
2. The model object contains metadata (API type, capabilities, pricing)
3. When you stream a response, pi looks up which provider implementation handles that API type
4. The provider is loaded lazily (only when first used)
5. The provider translates your request to its native format, calls the API, and converts responses back to pi's unified event format

This means you can switch models mid-conversation without changing your code. The agent can even hand off work between different providers - Claude's thinking output becomes tagged text that GPT-5 can read.

### Understanding the Agent Loop

The agent runs a continuous loop:

1. **Turn starts**: Collect all messages (user prompts, assistant responses, tool results)
2. **Send to LLM**: Convert messages to provider format, stream response
3. **Receive response**: Emit events for each chunk of text, thinking, or tool call
4. **Execute tools**: If the response includes tool calls, execute them (in parallel if independent)
5. **Add results**: Tool results become new messages in the conversation
6. **Check queues**: Process any steering (interrupt) or follow-up (queued) messages
7. **Repeat or end**: If tools were called or there are queued messages, go to step 1; otherwise finish

At every step, events are emitted so the UI can update and extensions can react. The loop handles errors gracefully - if a tool fails, the error becomes a tool result message that the LLM can see and recover from.

### Understanding Differential Rendering

Terminal UIs traditionally flicker because they clear the screen and redraw everything on each update. Pi uses three rendering strategies:

**First Render**: Just output all lines without clearing scrollback history.

**Width Changed**: When terminal resizes, clear screen and fully re-render (layouts need recalculation).

**Normal Update**: Find the first line that changed, move cursor there, clear to end of screen, render only changed lines.

All updates are wrapped in "synchronized output" mode (CSI 2026), which tells the terminal to batch all changes and display them atomically. This prevents users from seeing intermediate states during rendering.

### Understanding Session Branching

Sessions are trees, not linear histories. When you branch:

1. Pi copies all entries up to the branch point into a new session
2. If branching from an old point (not the latest), it generates a summary of what happened after that point
3. The new session is independent - changes don't affect the original
4. You can switch between branches anytime, or create branches from branches

This enables workflows like "try this risky refactoring in a branch, if it works merge it back, if not discard the branch."

### Understanding Compaction

LLMs have limited context windows. When a session grows too large:

1. Pi detects approaching the limit (with a safety buffer)
2. It finds a cut point - where to start summarizing from
3. It sends old messages to an LLM with instructions to summarize key decisions, changes, and context
4. The summary replaces the old messages, freeing up tokens
5. A compaction entry records what was removed and how many tokens were saved

Compaction preserves important information while discarding details no longer needed. You can also manually trigger compaction with custom instructions via `/compact "summarize focusing on X"`.

## Advanced Topics

### Creating Custom Tools

Tools are functions the agent can call. Each tool has:
- A name and description (for the LLM to understand when to use it)
- Parameters defined with TypeBox schemas (for type safety and validation)
- An execute function that returns results or throws errors

The agent automatically validates parameters before execution. If validation fails, the error is returned to the LLM so it can retry with correct arguments.

### Building Extensions

Extensions are TypeScript modules that register for lifecycle events. Common patterns:

**Add a custom tool**: Implement `getTools()` to return tool definitions. The agent will include them in its available tools list.

**Add a command**: Implement `getCommands()` to return slash commands. Users can invoke them with `/commandname`.

**Modify UI**: Implement `getUI()` to return components that replace or augment the interface.

**Hook into events**: Implement event handlers like `onToolExecutionStart` to intercept and potentially block tool calls, or `onMessageEnd` to log messages.

Extensions receive a context object with access to the session state, agent instance, and registration functions. They can also define custom message types via TypeScript declaration merging.

### Custom Providers

Adding a new LLM provider requires:
1. Implementing the stream function that calls the provider's API
2. Converting between pi's unified message format and the provider's format
3. Emitting standardized events (text, thinking, tool calls) as responses arrive
4. Registering the provider in the API registry
5. Adding model metadata (capabilities, pricing, context window)

The provider is loaded lazily via dynamic import, so it only affects bundle size when actually used. Browser-compatible providers avoid Node.js-specific APIs.

### OAuth Authentication

Some providers (ChatGPT Plus, Claude Pro, GitHub Copilot) require OAuth instead of API keys. Pi provides:
- Login functions that open browser flows and capture authorization codes
- Token refresh logic to handle expiration
- Secure credential storage in `auth.json`
- Automatic token refresh before making API calls

The OAuth system is provider-specific but follows a common pattern: login → store credentials → refresh as needed → use access token for API calls.

### Context Overflow Handling

When context exceeds the model's limit, pi has multiple strategies:
1. **Prevention**: Estimate tokens before sending, compact proactively
2. **Recovery**: If the provider rejects due to overflow, compact and retry
3. **Truncation**: As last resort, remove oldest messages until it fits

The system tracks token usage per message type (input, output, cache reads/writes) and cost, displaying totals in the footer.


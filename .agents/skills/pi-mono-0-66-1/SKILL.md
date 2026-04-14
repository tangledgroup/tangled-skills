---
name: pi-mono-0-66-1
description: Complete implementation guide for pi-mono monorepo architecture covering provider abstraction, agent runtime, terminal UI rendering, extension system, session management, and tool implementation patterns.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - TypeScript
  - AI agents
  - LLM
  - terminal UI
  - coding agents
  - architecture
category: development
required_environment_variables: []
---

# Pi Mono v0.66.1

## Overview

Pi Mono is a minimal, terminal-based coding agent framework designed to be adapted to your workflows rather than forcing you to adapt to it. Unlike feature-heavy agents with built-in sub-agents and plan modes, pi provides powerful defaults that you extend through TypeScript extensions, skills, prompt templates, and themes.

The project consists of four core packages that work together:
- **pi-ai**: Unified API for multiple LLM providers (OpenAI, Anthropic, Google, etc.)
- **pi-agent-core**: Stateful agent runtime with tool execution and event streaming
- **pi-tui**: Terminal UI framework with flicker-free differential rendering
- **pi-coding-agent**: The main CLI application combining all three

Pi runs in four modes: interactive (TUI), print (JSON output), RPC (process integration), and SDK (programmatic embedding). All modes share the same core logic but use different input/output layers.

## When to Use

Use this skill when:

- **Building custom coding agents**: You need a minimal foundation to extend rather than fighting against built-in features you don't want
- **Understanding agent architecture**: You want to learn how production coding agents are structured internally
- **Creating terminal-based AI tools**: You're building CLI applications that interact with LLMs
- **Extending existing workflows**: You need to add custom tools, UI components, or authentication flows to pi
- **Studying extensibility patterns**: You want examples of plugin architectures, event-driven design, and layered abstractions

**Don't use this skill** if you just want to run pi as a user - see the official README for usage instructions. This skill focuses on implementation details for developers who want to understand or extend pi's architecture.

## Core Concepts

### Layered Architecture

Pi is built in four distinct layers, each with a single responsibility:

**Layer 1: pi-ai (LLM Abstraction)**
This layer provides a unified interface to dozens of LLM providers. Instead of writing separate code for OpenAI, Anthropic, Google, etc., you work with one API that handles all the differences. The key innovation is lazy loading - providers are only loaded when you actually use them, keeping the application small and allowing browser compatibility.

**Layer 2: pi-agent-core (Agent Runtime)**
This layer implements the agent's message loop: send prompt to LLM, receive response, execute any requested tools, repeat until done. It handles parallel tool execution, steering (interrupting the agent), follow-up (queuing work for later), and emits events at every step so UIs can stay synchronized.

**Layer 3: pi-tui (Terminal UI)**
This layer provides a component-based UI framework for terminals. It uses differential rendering to only update changed screen regions, preventing flicker. Components like Editor, Input, SelectList, and Markdown are composable building blocks. The focus system supports IME (Input Method Editors) for CJK languages.

**Layer 4: pi-coding-agent (Application)**
This layer combines the three lower layers into a working application. It manages sessions (persistent conversation history), implements branching (create alternative timelines), compaction (summarize old messages to fit context windows), and provides four different run modes for different use cases.

### Session-Based Design

Everything in pi revolves around sessions. A session is:
- A persistent conversation stored on disk
- A tree structure allowing branching at any point
- Automatically compacted when it grows too large
- Fully replayable from any point in history

Sessions enable features like "what if I tried a different approach?" (branching), automatic context management (compaction), and resuming work days later exactly where you left off.

### Event-Driven Architecture

Pi uses events for all state changes. When the agent receives a message, executes a tool, or completes a turn, it emits events that listeners can react to. This design:
- Decouples the agent logic from UI updates
- Allows streaming responses (show text as it arrives)
- Enables extensions to hook into any point in the workflow
- Makes testing easier (record and replay event sequences)

### Extension System

Pi's core is intentionally minimal - it ships with only four tools (read, write, edit, bash). Everything else is added through extensions:
- **Custom tools**: Add new capabilities like database queries or API calls
- **UI components**: Replace or augment the interface with custom widgets
- **Commands**: Add new slash commands like `/deploy` or `/test`
- **Authentication**: Support new providers or OAuth flows
- **Themes**: Change colors and styling

Extensions are TypeScript modules that register hooks for lifecycle events. They receive a context object giving them access to the session, agent, and registration functions for tools and commands.

### Skills as Documentation

Skills are markdown files that teach the agent about specific topics. Unlike prompt templates (which insert text) or extensions (which add code), skills provide reference documentation the agent can consult. They're loaded from directories, parsed for metadata (name, description, when to use), and formatted into the system prompt.

A skill can have:
- A main SKILL.md file with overview and examples
- Optional reference files in a `refs/` subdirectory for modular loading
- Frontmatter metadata describing when to invoke it

## Installation / Setup

### Installing Pi

```bash
npm install -g @mariozechner/pi-coding-agent
```

### Authentication

Pi supports multiple authentication methods:

**API Keys (Simplest)**
Set environment variables for your provider:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=...
```

**OAuth Subscriptions (For ChatGPT Plus, Claude Pro, etc.)**
Run the login command:
```bash
pi
/login  # Interactive provider selection
```
Credentials are saved to `~/.pi/agent/auth.json`.

### Configuration

Pi reads configuration from `~/.pi/agent/`:
- `settings.json`: Thinking level, theme, message delivery preferences
- `keybindings.json`: Custom keyboard shortcuts
- `models.json`: Custom model definitions
- `extensions/`: Directory for extension packages
- `skills/`: Directory for skill markdown files
- `prompts/`: Directory for prompt templates
- `themes/`: Directory for custom color themes

## Usage Examples

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

## References

- **Official Repository**: https://github.com/badlogic/pi-mono/tree/v0.66.1
- **Pi Documentation**: https://github.com/badlogic/pi-mono/blob/v0.66.1/packages/coding-agent/README.md
- **pi-ai Package**: https://github.com/badlogic/pi-mono/blob/v0.66.1/packages/ai/README.md
- **pi-agent-core Package**: https://github.com/badlogic/pi-mono/blob/v0.66.1/packages/agent/README.md
- **pi-tui Package**: https://github.com/badlogic/pi-mono/blob/v0.66.1/packages/tui/README.md

### Reference Files

See the `references/` directory for deep dives into specific topics:
- [`references/01-provider-architecture.md`](references/01-provider-architecture.md) - Detailed provider implementation patterns
- [`references/02-agent-runtime.md`](references/02-agent-runtime.md) - Message loop and tool execution internals
- [`references/03-tui-rendering.md`](references/03-tui-rendering.md) - Differential rendering and component lifecycle
- [`references/04-extension-system.md`](references/04-extension-system.md) - Extension API and hook patterns
- [`references/05-session-management.md`](references/05-session-management.md) - Branching, compaction, and persistence
- [`references/06-tool-implementation.md`](references/06-tool-implementation.md) - Creating custom tools with validation

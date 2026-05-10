---
name: acp-0-12-2
description: Protocol standardizing communication between code editors and AI coding agents using JSON-RPC 2.0 over stdio. Decouples agents from editors for cross-compatibility. Use when building AI coding agents needing editor interoperability, implementing persistent sessions with tool calls, connecting agents via MCP delegation, or working with the official SDKs.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - agent-protocol
  - json-rpc
  - coding-agents
  - editor-integration
  - ai-agents
  - stdio-transport
category: protocols
external_references:
  - https://agentclientprotocol.com
  - https://github.com/agentclientprotocol/agent-client-protocol
---

# Agent Client Protocol (ACP) 0.12.2

## Overview

The Agent Client Protocol (ACP) standardizes communication between code editors (interactive programs for viewing and editing source code) and coding agents (programs that use generative AI to autonomously modify code). It is suitable for both local and remote scenarios.

Before ACP, every agent-editor combination required custom integration work. ACP solves this by providing a standardized protocol — similar to how the Language Server Protocol (LSP) standardized language server integration. Agents that implement ACP work with any compatible editor. Editors that support ACP gain access to the entire ecosystem of ACP-compatible agents.

ACP uses JSON-RPC 2.0 over stdio as its primary transport. The protocol re-uses JSON representations from MCP where possible, but includes custom types for agentic coding UX elements like displaying diffs. The default format for user-readable text is Markdown.

## When to Use

- Building an AI coding agent that needs to work across multiple editors (VS Code, Cursor, Zed, JetBrains, etc.)
- Implementing a code editor or IDE that wants to support any ACP-compatible agent
- Working with persistent agent sessions, tool calls, and permission flows
- Integrating agents via MCP server delegation
- Using official SDKs (TypeScript, Python, Rust, Java, Kotlin) for ACP client or agent development
- Understanding the session lifecycle: initialize → authenticate → session/new → prompt turns

## Core Concepts

**Client** — The code editor or IDE. Manages the environment, handles user interactions, controls access to resources, and provides filesystem/terminal capabilities to agents.

**Agent** — An AI coding agent that runs as a subprocess of the client (local) or remotely. Processes prompts, generates tool calls, executes actions, and reports progress through structured notifications.

**Session** — A specific conversation thread between client and agent. Each session maintains its own context, conversation history, and state. Multiple independent sessions can run with the same agent.

**Prompt Turn** — The core interaction cycle: user sends a message → agent processes with LLM → agent reports output via `session/update` notifications (plan entries, text chunks, tool calls) → turn completes with a stop reason.

**Tool Calls** — Actions the LLM requests the agent to perform (read files, run commands, edit code). Agents report tool calls through `session/update` notifications with real-time status progression: pending → in_progress → completed/failed/cancelled.

**Permission Requests** — Agents may request user authorization before executing tool calls via `session/request_permission`. Clients display approval/denial UI and respond to the agent.

## Architecture

ACP follows a three-phase lifecycle:

1. **Initialization** — Client and agent negotiate protocol version, exchange capabilities (filesystem, terminal, MCP, session features), and optionally authenticate
2. **Session Setup** — Create a new session (`session/new`) with working directory and MCP servers, or load/resume an existing one (`session/load`, `session/resume`)
3. **Prompt Turns** — Send user messages via `session/prompt`, receive real-time progress via `session/update` notifications, handle tool calls and permissions

### Message Types

- **Methods** — Request-response pairs that expect a result or error (e.g., `initialize`, `session/new`, `session/prompt`)
- **Notifications** — One-way messages that don't expect a response (e.g., `session/update`, `session/cancel`)

### Transport

The primary transport is **stdio**: the client launches the agent as a subprocess, JSON-RPC messages flow over stdin/stdout delimited by newlines. Agents may write logs to stderr. Custom transports are allowed but must preserve JSON-RPC format.

## Usage Examples

Initialize and create a session:

```json
// Client → Agent: Initialize
{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":1,"clientCapabilities":{"fs":{"readTextFile":true,"writeTextFile":true},"terminal":true}}}

// Agent → Client: Response with capabilities
{"jsonrpc":"2.0","id":0,"result":{"protocolVersion":1,"agentCapabilities":{"loadSession":true,"promptCapabilities":{"image":true}},"authMethods":[]}}

// Client → Agent: Create session
{"jsonrpc":"2.0","id":1,"method":"session/new","params":{"cwd":"/home/user/project","mcpServers":[]}}

// Agent → Client: Session created
{"jsonrpc":"2.0","id":1","result":{"sessionId":"sess_abc123"}}
```

Send a prompt turn:

```json
{"jsonrpc":"2.0","id":2,"method":"session/prompt","params":{"sessionId":"sess_abc123","prompt":[{"type":"text","text":"Fix the bug in main.py"}]}}
```

## Advanced Topics

**Initialization and Capabilities**: Version negotiation, capability exchange, authentication methods → [Initialization](reference/01-initialization.md)

**Session Lifecycle**: Creating, loading, resuming, listing, and managing sessions → [Session Lifecycle](reference/02-session-lifecycle.md)

**Prompt Turn Protocol**: The core conversation flow — user messages, agent processing, output streaming, cancellation → [Prompt Turn Protocol](reference/03-prompt-turn.md)

**Tool Calls and Permissions**: Tool call lifecycle, permission requests, content and locations → [Tool Calls and Permissions](reference/04-tool-calls.md)

**File System and Terminals**: Agent file read/write operations, terminal command execution → [File System and Terminals](reference/05-file-system-terminals.md)

**Session Modes and Config**: Operating modes (ask/architect/code), session configuration options → [Session Modes and Config](reference/06-session-modes-config.md)

**Content Blocks and Resources**: Text, image, audio, embedded resources in prompts and outputs → [Content Blocks](reference/07-content-blocks.md)

**Transports and Extensibility**: stdio transport details, custom transports, `_meta` field, extension methods → [Transports and Extensibility](reference/08-transports-extensibility.md)

**Agents and Clients Ecosystem**: Compatible agents (Cline, Codex, Gemini CLI, Goose, etc.) and clients (VS Code, Cursor, Zed, JetBrains) → [Ecosystem](reference/09-ecosystem.md)

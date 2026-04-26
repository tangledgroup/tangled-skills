---
name: pi-mono-0-66-1
description: Complete implementation guide for pi-mono monorepo architecture covering provider abstraction, agent runtime, terminal UI rendering, extension system, session management, and tool implementation patterns. Use when building, debugging, or extending the pi coding agent — a minimal terminal-based AI coding harness that runs in interactive, print, JSON, RPC, and SDK embedding modes.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.66.1"
tags:
  - ai-coding-agent
  - terminal-harness
  - extensions
  - tui
  - session-management
  - providers
  - tools
category: ai-tooling
external_references:
  - https://github.com/badlogic/pi-mono
  - https://pi.dev/
  - https://www.npmjs.com/package/@mariozechner/pi-coding-agent
---

# pi-mono 0.66.1

## Overview

Pi is a minimal terminal coding harness — an AI coding agent that runs in your terminal with four modes: interactive TUI, print (non-interactive), JSON event stream, and RPC for process integration. It also provides an SDK for embedding in other applications. Pi ships with powerful defaults but skips features like sub-agents and plan mode by design, instead letting you build what you want via TypeScript extensions, skills, prompt templates, and themes.

The monorepo (`pi-mono`) contains four core packages:

- `@mariozechner/pi-ai` — LLM provider abstraction (streaming, tool calls, cost tracking)
- `@mariozechner/pi-agent-core` — Agent loop and message types
- `@mariozechner/pi-tui` — Terminal UI components (Text, Box, Container, SelectList, etc.)
- `@mariozechner/pi-coding-agent` — CLI, interactive mode, extensions system, session management

Install via npm: `npm install -g @mariozechner/pi-coding-agent`. Authenticate with API keys or subscriptions (`/login`). Default tools are `read`, `bash`, `edit`, and `write`.

## When to Use

- Building custom pi extensions (tools, commands, UI components, event handlers)
- Debugging pi's session management, compaction, or branching behavior
- Integrating pi programmatically via SDK or RPC mode
- Creating custom providers, models, or OAuth flows
- Understanding pi's architecture for contribution or forking

## Core Concepts

**Extensions** are TypeScript modules that register tools, commands, shortcuts, and event handlers via the `ExtensionAPI`. They are the primary extension mechanism — no MCP, no built-in sub-agents. Everything is built with extensions.

**Skills** follow the Agent Skills standard (`SKILL.md` in directories). Loaded on-demand via `/skill:name` or auto-discovered by description matching.

**Sessions** are JSONL files with tree structure (`id`/`parentId`), enabling in-place branching without creating new files. Navigate with `/tree`, fork with `/fork`.

**Compaction** summarizes older messages when context approaches limits, keeping recent work intact. Lossy but recoverable via `/tree`.

## Advanced Topics

**Architecture & Monorepo Structure**: Package layout, build system, path resolution → [Architecture](reference/01-architecture.md)

**Extensions System**: Tool registration, event hooks, custom UI, state management, rendering → [Extensions](reference/02-extensions.md)

**Session Management**: JSONL format, tree structure, branching, compaction, fork/clone → [Sessions](reference/03-sessions.md)

**Providers & Models**: Built-in providers, custom models.json, OAuth, API types, compat flags → [Providers](reference/04-providers.md)

**TUI Components**: Component interface, built-in components, theming, overlays, patterns → [TUI](reference/05-tui.md)

**SDK & RPC**: Programmatic embedding, AgentSession, RPC protocol, event streaming → [SDK and RPC](reference/06-sdk-rpc.md)

**Settings, Keybindings & Packages**: Configuration files, resource loading, package management → [Configuration](reference/07-configuration.md)

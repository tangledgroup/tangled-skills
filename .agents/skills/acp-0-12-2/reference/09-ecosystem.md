# Agents and Clients Ecosystem

## Overview

ACP has broad adoption across the AI coding agent ecosystem. The protocol is maintained by Zed Industries and JetBrains with contributions from the community.

## Official SDKs

- **TypeScript**: `@agentclientprotocol/sdk` — npm package with examples
- **Python**: `python-sdk` — Python library with examples
- **Rust**: `agent-client-protocol` — Cargo crate with agent and client examples
- **Java**: `java-sdk` — Java library with examples
- **Kotlin**: `acp-kotlin` — JVM support with samples

## Compatible Agents

Agents that implement ACP:

- **Cline** — Autonomous coding agent CLI (create/edit files, run commands, browser)
- **Codebuddy Code** — Tencent Cloud's intelligent coding tool
- **Codex CLI** — OpenAI's coding assistant via ACP adapter
- **Corust Agent** — Rust-focused co-building agent
- **crow-cli** — Minimal ACP native coding agent
- **Cursor** — Cursor's coding agent
- **DeepAgents** — LangChain-powered coding and general purpose agent
- **Factory Droid** — Factory AI coding agent
- **fast-agent** — Multi-provider code and build agent
- **Gemini CLI** — Google's official CLI for Gemini
- **GitHub Copilot** — GitHub's AI pair programmer
- **goose** — Block's local, extensible, open source AI agent
- **Junie** — JetBrains' AI coding agent
- **Kilo (Kilo Code)** — Open source coding agent
- **Kimi CLI** — Moonshot AI's coding assistant
- **Minion Code** — Enhanced AI code assistant on Minion framework
- **Mistral Vibe** — Mistral's open-source coding assistant
- **Nova** — Compass AI's fully-fledged software engineer agent
- **OpenCode** — Open source coding agent
- **pi ACP** — ACP adapter for pi coding agent
- **Qoder CLI** — AI coding assistant with agentic capabilities
- **Qwen Code** — Alibaba's Qwen coding assistant
- **Stakpak** — Open-source DevOps agent in Rust

## Compatible Clients

Clients that support ACP:

- **VS Code** — Via the vscode-acp extension
- **Cursor** — Native ACP support
- **Zed** — Native ACP support (protocol creator)
- **JetBrains IDEs** — Via Junie integration
- **acp-ui** — Cross-platform desktop client for any ACP agent
- **Open-ACP** — Self-hosted bridge for messaging platforms (Telegram, Discord)

## Agent Registry

A public registry of ACP-compatible agents is maintained at `agentclientprotocol.com`. Clients can fetch it programmatically:

```bash
curl https://cdn.agentclientprotocol.com/registry/v1/latest/registry.json
```

The registry JSON contains all agent metadata including distribution information for automatic installation.

## Community Libraries

Additional community integrations include:
- WeChat bridge (wechat-acp) — Bridge WeChat messages to ACP agents
- Obsidian integration (obsidian-agent-client) — Bring AI agents into Obsidian
- Emacs support (acp.el) — ACP implementation in Emacs Lisp
- Go SDK (acp-go-sdk by Coder) — Go language bindings

## Protocol Governance

ACP follows a structured RFD (Request for Discussion) process for protocol changes. Completed RFDs include session config options, session list, session info update, agent registry, session resume, and session close. Draft RFDs cover topics like session fork, request cancellation, MCP over ACP, proxy chains, auth methods, and streamable HTTP transport.

The protocol is maintained under Apache License 2.0 with no CLA requirement for contributors.
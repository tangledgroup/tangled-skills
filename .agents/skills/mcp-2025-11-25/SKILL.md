---
name: mcp-2025-11-25
description: Model Context Protocol (MCP) version 2025-11-25 specification covering client-host-server architecture, JSON-RPC messaging, tools, resources, prompts, sampling, elicitation, authorization, and transport mechanisms. Use when building MCP clients or servers, implementing LLM tool integrations, creating AI application connectors, configuring stdio or Streamable HTTP transports, or working with any protocol that connects language models to external data sources and capabilities.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2025-11-25"
tags:
  - mcp
  - model-context-protocol
  - llm
  - ai-integration
  - json-rpc
  - tools
  - sampling
  - elicitation
category: protocol
external_references:
  - https://modelcontextprotocol.io/specification/2025-11-25
  - https://github.com/modelcontextprotocol/modelcontextprotocol
---

# Model Context Protocol (MCP) 2025-11-25

## Overview

Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. It provides a standardized way to connect language models with the context they need, whether building AI-powered IDEs, enhancing chat interfaces, or creating custom AI workflows.

The protocol uses JSON-RPC 2.0 messages over stateful connections with capability negotiation between clients and servers. It takes inspiration from the Language Server Protocol (LSP) in its client-server architecture and JSON-RPC foundation, but diverges by focusing on LLM context exchange rather than language services.

### Key Architecture

MCP follows a **client-host-server** architecture:

- **Hosts**: LLM applications that initiate connections and coordinate multiple clients
- **Clients**: Connectors within the host, each maintaining a 1:1 session with a server
- **Servers**: Services that provide context (resources), capabilities (tools), and workflows (prompts)

The protocol is built on several design principles:

- Servers should be extremely easy to build
- Servers should be highly composable
- Servers cannot read the full conversation or see into other servers
- Features can be added progressively through capability negotiation

## When to Use

- Building MCP server implementations that expose tools, resources, or prompts
- Developing MCP clients that connect AI applications to external services
- Implementing stdio or Streamable HTTP transport for MCP communication
- Integrating LLM tool calling with external APIs and data sources
- Creating sampling flows where servers request LLM generations through clients
- Building elicitation workflows for user input collection
- Configuring OAuth 2.1 authorization for MCP server access
- Implementing task-augmented requests for long-running operations

## Core Concepts

### Capability Negotiation

MCP uses a capability-based negotiation system. During initialization, clients and servers declare their supported features. Capabilities determine which protocol features are available during a session:

- **Server capabilities**: `prompts`, `resources`, `tools`, `logging`, `completions`, `tasks`
- **Client capabilities**: `roots`, `sampling`, `elicitation`, `tasks`

Both parties must respect declared capabilities throughout the session.

### Content Types

MCP supports multiple content types across its features:

- **Text**: Plain text messages and data
- **Image**: Base64-encoded images with MIME type
- **Audio**: Base64-encoded audio with MIME type
- **Resource links**: References to MCP resources by URI
- **Embedded resources**: Full resource content inline

### Annotations

Resources, tools, prompts, and content blocks support optional annotations:

- `audience`: Intended audience(s) — `"user"` and/or `"assistant"`
- `priority`: Importance from 0.0 (optional) to 1.0 (required)
- `lastModified`: ISO 8601 timestamp of last modification

## Quick Reference

### Protocol Version

`2025-11-25` — the protocol version string used in `initialize` requests and the `MCP-Protocol-Version` HTTP header.

### JSON-RPC Error Codes

| Code | Meaning |
|------|----------|
| `-32700` | Parse error |
| `-32600` | Invalid request (e.g., non-task-augmented when required) |
| `-32601` | Method not found (capability not supported) |
| `-32602` | Invalid params |
| `-32603` | Internal error |
| `-32002` | Resource not found |
| `-32042` | URL elicitation required |
| `-1` | User rejected (sampling) |

### Transport Comparison

- **stdio**: Client launches server as subprocess, JSON-RPC over stdin/stdout, newline-delimited. Best for local integrations.
- **Streamable HTTP**: Server runs independently, client POSTs JSON-RPC messages to single endpoint, SSE for server-to-client. Supports multiple clients, session management, resumability.

## Security Principles

MCP enables powerful capabilities through arbitrary data access and code execution paths. Key security principles:

- **User Consent**: Users must explicitly consent to all data access and operations
- **Data Privacy**: Hosts must obtain explicit user consent before exposing data to servers
- **Tool Safety**: Tools represent arbitrary code execution — hosts must obtain explicit consent before invocation
- **Sampling Controls**: Users must approve LLM sampling requests and control what prompts are sent
- **Token Validation**: MCP servers MUST validate access tokens and MUST NOT accept tokens intended for other resources

## Advanced Topics

**Architecture and Design Principles**: Core components, capability negotiation → [Architecture](reference/01-architecture-overview.md)

**Lifecycle and Transports**: Initialization, stdio, Streamable HTTP, authorization → [Lifecycle & Transports](reference/02-lifecycle-transports.md)

**Base Utilities**: Cancellation, ping, progress tracking, tasks → [Base Utilities](reference/03-base-utilities.md)

**Server Features**: Tools, resources, prompts, completions, logging, pagination → [Server Features](reference/04-server-features.md)

**Client Features**: Roots, sampling, elicitation (form and URL modes) → [Client Features](reference/05-client-features.md)

**Schema Reference**: Complete JSON-RPC message types and data structures → [Schema Reference](reference/06-schema-reference.md)

**Authorization Extensions**: Optional extensions for client credentials and enterprise authorization → See [ext-auth repository](https://github.com/modelcontextprotocol/ext-auth)

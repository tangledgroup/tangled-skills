---
name: a2a-1-0-0
description: The Agent2Agent (A2A) Protocol v1.0.0 is an open standard enabling communication and interoperability between independent, opaque AI agent systems. Use when building multi-agent systems where agents need to discover each other's capabilities via Agent Cards, negotiate interaction modalities (text, files, structured data), securely collaborate on long-running tasks with streaming (SSE) and push notifications, and exchange information without exposing internal state, memory, or tools. Covers JSON-RPC 2.0, gRPC, and HTTP+JSON/REST protocol bindings, custom binding guidelines, extensions, and enterprise security patterns.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - agent-communication
  - multi-agent
  - interoperability
  - protocol
  - json-rpc
  - grpc
  - rest
  - streaming
  - push-notifications
  - extensions
category: protocol
external_references:
  - https://github.com/a2aproject/A2A
  - https://a2a-protocol.org/latest/
---

# Agent2Agent (A2A) Protocol 1.0.0

## Overview

The Agent2Agent (A2A) Protocol is an open standard designed to facilitate communication and interoperability between independent, potentially opaque AI agent systems. In an ecosystem where agents might be built using different frameworks (ADK, LangGraph, CrewAI), languages, or by different vendors, A2A provides a common language and interaction model.

A2A enables agents to:

- Discover each other's capabilities via Agent Cards.
- Negotiate interaction modalities (text, files, structured data).
- Manage collaborative tasks through a defined lifecycle.
- Securely exchange information to achieve user goals **without needing access to each other's internal state, memory, or tools.**

### Guiding Principles

- **Simple:** Reuses existing standards — HTTP(S), JSON-RPC 2.0, Server-Sent Events, gRPC.
- **Enterprise Ready:** Addresses authentication, authorization, security, privacy, tracing, and monitoring.
- **Async First:** Designed for long-running tasks and human-in-the-loop interactions.
- **Modality Agnostic:** Supports text, audio/video (via file references), structured data/forms, and potentially embedded UI components.
- **Opaque Execution:** Agents collaborate based on declared capabilities without sharing internal thoughts, plans, or tool implementations.

### Three-Layer Architecture

A2A is organized into three distinct layers:

1. **Canonical Data Model** — Core data structures (Task, Message, AgentCard, Part, Artifact) defined as Protocol Buffers.
2. **Abstract Operations** — Fundamental capabilities independent of transport (SendMessage, GetTask, CancelTask, etc.).
3. **Protocol Bindings** — Concrete mappings to JSON-RPC 2.0, gRPC, and HTTP+JSON/REST, plus custom binding guidelines.

### SDKs and Tooling

Official SDKs are available in Python (`a2a-sdk`), Go, JavaScript/TypeScript (`@a2a-js/sdk`), Java (Maven), and .NET (NuGet package `A2A`). The project also provides the A2A Inspector for validation and a Technology Compatibility Kit (TCK) for conformance testing.

## When to Use

- Building multi-agent systems where independent agents need to collaborate as peers.
- Creating agent-to-agent communication layers (as opposed to agent-to-tool, which is MCP's domain).
- Implementing agent discovery via Agent Cards at well-known URIs or curated registries.
- Managing long-running tasks with streaming (SSE) or push notification (webhook) updates.
- Building enterprise-grade agent systems requiring authentication, authorization, and observability.
- Integrating agents across different frameworks (Google ADK, LangGraph, BeeAI, CrewAI).
- Designing custom protocol bindings (WebSocket, MQTT) for specialized environments.

## Core Concepts at a Glance

**Actors:** User (human or automated service), A2A Client (client agent initiating requests), A2A Server (remote agent exposing an opaque endpoint).

**Fundamental Objects:** Agent Card (digital business card with identity, capabilities, skills), Task (stateful unit of work with lifecycle), Message (single communication turn with Parts), Part (content container: text, file URL/inline, or structured data), Artifact (tangible output deliverable).

**Interaction Mechanisms:** Polling (request/response), Streaming via SSE (real-time updates), Push Notifications (webhook-based async delivery).

**Task Lifecycle:** submitted → working → completed / failed / canceled / rejected / input-required / auth-required. Terminal states are immutable — refinements start new tasks within the same `contextId`.

## Usage Examples

### Discovering an Agent Card

```http
GET /.well-known/agent-card.json HTTP/1.1
Host: agent.example.com
```

Returns a JSON document with the agent's name, description, supported interfaces (protocol bindings with URLs), capabilities, skills, and security requirements.

### Sending a Message (HTTP+JSON)

```http
POST /message:send HTTP/1.1
Host: agent.example.com
Content-Type: application/a2a+json
Authorization: Bearer token
A2A-Version: 1.0

{
  "message": {
    "role": "ROLE_USER",
    "parts": [{"text": "What is the weather today?"}],
    "messageId": "msg-uuid"
  }
}
```

**Response:**

```json
{
  "task": {
    "id": "task-uuid",
    "contextId": "context-uuid",
    "status": {"state": "TASK_STATE_COMPLETED"},
    "artifacts": [{
      "artifactId": "artifact-uuid",
      "name": "Weather Report",
      "parts": [{"text": "Today will be sunny with a high of 75°F"}]
    }]
  }
}
```

### Python SDK Quickstart

```python
from a2a import create_client, new_text_message, Role
from a2a.types import SendMessageRequest

# Fetch agent card and create client
card = await resolver.get_agent_card()
client = create_client(card)

# Send message
response = await client.send_message(
    SendMessageRequest(message=new_text_message("Hello", Role.ROLE_USER))
)
task = response.result.task
```

## A2A vs MCP

A2A and MCP are complementary protocols:

- **MCP (Model Context Protocol):** Standardizes how agents connect to and use tools, APIs, and data sources. Agent-to-tool communication for stateless, structured operations.
- **A2A:** Standardizes how independent agents communicate and collaborate as peers. Agent-to-agent communication for stateful, multi-turn interactions with reasoning, planning, and delegation.

An A2A client agent might request an A2A server agent to perform a complex task. The server agent internally uses MCP to interact with underlying tools, APIs, or data sources to fulfill the A2A task. Wrapping agents as simple MCP tools is fundamentally limiting — agents should be exposed as agents, not tools.

## Advanced Topics

**Core Concepts & Architecture**: Actors, objects, task lifecycle, multi-turn patterns, agent response types, parallel follow-ups → [Core Concepts](reference/01-core-concepts.md)

**Protocol Data Model**: Task, Message, Part, Artifact, AgentCard, streaming events, push notifications, field presence semantics → [Data Model Reference](reference/02-data-model.md)

**Protocol Bindings**: JSON-RPC 2.0, gRPC, HTTP+JSON/REST detailed specifications with method mappings and error handling → [Protocol Bindings](reference/03-protocol-bindings.md)

**Streaming & Async Operations**: SSE streaming, push notifications, webhooks, security considerations, reconnection → [Streaming & Async](reference/04-streaming-async.md)

**Security & Enterprise Features**: Authentication, authorization, TLS, Agent Card signing (JWS/JCS), in-task auth, observability → [Security Guide](reference/05-security-enterprise.md)

**Extensions & Custom Bindings**: Extension mechanism, declaration, activation, governance, custom protocol bindings → [Extensions & Bindings](reference/06-extensions-bindings.md)

**Agent Discovery**: Well-known URI, curated registries, direct configuration, caching, security → [Agent Discovery](reference/07-agent-discovery.md)

**SDKs & Tutorials**: Python SDK patterns, AgentExecutor, server setup, client interactions, streaming examples → [SDK & Tutorials](reference/08-sdks-tutorials.md)

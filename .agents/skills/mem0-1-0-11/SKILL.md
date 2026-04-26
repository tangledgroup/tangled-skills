---
name: mem0-1-0-11
description: A skill for using Mem0 v1.0.11, a universal self-improving memory layer for LLM applications that enables persistent context across sessions with support for both managed platform and open-source deployments.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.0.11"
tags:
  - memory
  - llm
  - ai-agents
  - vector-search
  - langchain
  - llama-index
category: ai-infrastructure
external_references:
  - https://github.com/mem0ai/mem0/tree/v1.0.11/docs
  - https://app.mem0.ai
  - https://arxiv.org/pdf/2504.19413.pdf
  - https://docs.mem0.ai
  - https://github.com/mem0ai/mem0
  - https://github.com/mem0ai/mem0/blob/v1.0.11/MIGRATION_GUIDE_v1.0.md
  - https://mem0.dev/DiG
---

# Mem0 v1.0.11

## Overview

Mem0 ("mem-zero") is a self-improving memory layer for LLM applications that enables persistent context across sessions. Unlike traditional RAG systems that are stateless, Mem0 creates **stateful agents** that remember user preferences, learn from interactions, and evolve behavior over time. It combines vector embeddings with optional graph databases for comprehensive recall — achieving **+26% accuracy over OpenAI Memory**, **91% faster responses**, and **90% lower token usage** on the LOCOMO benchmark.

Mem0 offers two deployment modes:

- **Mem0 Platform** — Fully managed service at `api.mem0.ai` with automatic scaling, SOC 2 compliance, graph memory, webhooks, and a dashboard. Accessed via API key.
- **Mem0 Open Source** — Self-hosted SDK (Python + Node.js) with full control over LLMs, vector stores, embedders, and rerankers. Runs on your infrastructure.

Both modes share the same core memory pipeline: information extraction → conflict resolution → dual storage (vector + optional graph).

## When to Use

- Building AI assistants or chatbots that need to remember users across sessions
- Creating customer support agents that recall past tickets and preferences
- Developing multi-agent systems where agents share or isolate memory
- Implementing personalized recommendations based on historical interactions
- Any LLM application where stateless context windows are insufficient
- Migrating from OpenAI's native Memory API to a more cost-effective, faster alternative

## Core Concepts

### Memory Layers

Mem0 organizes memory into four layers:

- **Conversation memory** — In-flight messages within a single turn (tool calls, chain-of-thought). Lost after the turn.
- **Session memory** — Short-lived facts for a current task or channel. Scoped by `session_id` / `run_id`.
- **User memory** — Long-lived knowledge tied to a person or account. Scoped by `user_id`. Persists across interactions.
- **Organizational memory** — Shared context available to multiple agents or teams.

### The Memory Pipeline

Every `add` call passes through three stages:

1. **Information extraction** — An LLM identifies key facts, preferences, and decisions from the conversation.
2. **Conflict resolution** — Existing memories are checked for duplicates or contradictions; latest truth wins.
3. **Storage** — Memories land in vector storage (and optionally graph storage) for fast retrieval.

### Entity Scoping

Mem0 scopes memories by entity identifiers to prevent cross-contamination:

- `user_id` — Persistent persona or account
- `agent_id` — Distinct agent persona or tool
- `app_id` — White-label app or product surface
- `run_id` — Short-lived flow, ticket, or conversation thread

### Response Format (v1.0+)

All operations return a consistent format: `{"results": [...]}`. This replaced the pre-v1.0 behavior where responses varied by operation. No more `version` or `output_format` parameters needed.

## Installation / Setup

### Python SDK

```bash
pip install mem0ai
```

### Node.js SDK

```bash
npm install mem0ai
```

### CLI

```bash
npm install -g @mem0/cli   # or: pip install mem0-cli
mem0 init
```

### Platform Setup

1. Sign up at [app.mem0.ai](https://app.mem0.ai)
2. Get an API key from the dashboard
3. Initialize the client:

```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")
```

### Open Source Setup

```python
import os
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

from mem0 import Memory
m = Memory()
```

Default OSS components (override via `Memory.from_config`):

- LLM: OpenAI `gpt-4.1-nano-2025-04-14`
- Embeddings: OpenAI `text-embedding-3-small`
- Vector store: Local Qdrant at `/tmp/qdrant`
- History store: SQLite at `~/.mem0/history.db`

## Usage Examples

### Basic Add and Search

```python
from mem0 import Memory

m = Memory()

# Add memories from a conversation
messages = [
    {"role": "user", "content": "Hi, I'm Alex. I love basketball and gaming."},
    {"role": "assistant", "content": "Hey Alex! I'll remember your interests."}
]
result = m.add(messages, user_id="alex")

# Search for relevant memories
results = m.search("What do you know about me?", user_id="alex")
for hit in results["results"]:
    print(hit["memory"])
```

### Platform API with Filters

```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

# Add with entity scoping
messages = [
    {"role": "user", "content": "I'm planning a trip to Tokyo next month."},
    {"role": "assistant", "content": "Great! I'll remember that for future suggestions."}
]
client.add(messages, user_id="alice")

# Search with logical filters
results = client.search(
    "What are Alice's hobbies?",
    filters={
        "OR": [
            {"user_id": "alice"},
            {"agent_id": {"in": ["travel-assistant", "customer-support"]}}
        ]
    }
)
```

### Full Chat with Memory Loop

```python
from openai import OpenAI
from mem0 import Memory

openai_client = OpenAI()
memory = Memory()

def chat_with_memories(message: str, user_id: str = "default_user") -> str:
    # Retrieve relevant memories
    relevant = memory.search(query=message, user_id=user_id, limit=3)
    memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant["results"])

    # Generate response with memory context
    system_prompt = f"You are a helpful AI.\nUser Memories:\n{memories_str}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
    response = openai_client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14", messages=messages
    )
    assistant_response = response.choices[0].message.content

    # Store the conversation as new memory
    messages.append({"role": "assistant", "content": assistant_response})
    memory.add(messages, user_id=user_id)

    return assistant_response
```

## Advanced Topics

**Memory Operations**: Add, search, update, and delete workflows with Platform vs OSS differences → [Memory Operations](reference/01-memory-operations.md)

**Configuration & Components**: LLM providers (18+), vector databases (24+), embedders (10+), rerankers (5+) with full setup guides → [Configuration and Components](reference/02-configuration-components.md)

**Platform Features**: Graph memory, entity scoping, async clients, multimodal support, webhooks, custom categories, advanced retrieval → [Platform Features](reference/03-platform-features.md)

**Open Source Features**: Self-hosted graph memory (Neo4j, Memgraph), REST API server, async memory, metadata filtering, OpenAI compatibility → [Open Source Features](reference/04-open-source-features.md)

**API Reference**: REST endpoints for the managed Platform (`/v1/` paths) and OSS server (`/memories` paths) → [API Reference](reference/05-api-reference.md)

**Integrations & Migration**: LangChain, CrewAI, LlamaIndex, AutoGen, Vercel AI SDK, MCP, and v0→v1 migration guide → [Integrations and Migration](reference/06-integrations-migration.md)

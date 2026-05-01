---
name: mem0-2-0-1
description: A skill for using Mem0 v2.0.1, a self-improving memory layer for LLM agents that enables persistent context across sessions with single-pass ADD-only extraction, multi-signal hybrid search (semantic + BM25 + entity linking), and support for both managed platform and open-source deployments.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2.0.1"
tags:
  - memory
  - llm
  - ai-agents
  - vector-search
  - hybrid-search
  - entity-linking
category: ai-infrastructure
external_references:
  - https://docs.mem0.ai/llms.txt
  - https://github.com/mem0ai/mem0
  - https://app.mem0.ai
  - https://arxiv.org/pdf/2504.19413.pdf
  - https://mem0.dev/DiG
---

# Mem0 v2.0.1

## Overview

Mem0 ("mem-zero") is a self-improving memory layer for LLM agents that enables persistent context across sessions. It creates **stateful agents** that remember user preferences, learn from interactions, and evolve behavior over time. Unlike traditional RAG systems that are stateless, Mem0 stores extracted facts in vector storage with optional graph connections, achieving **+20 points on LoCoMo (71.4 → 91.6)** and **+26 points on LongMemEval (67.8 → 93.4)** while cutting extraction latency roughly in half.

v2 introduces a fundamentally redesigned memory algorithm:

- **Single-pass ADD-only extraction** — one LLM call per `add()`, no UPDATE/DELETE during extraction. Memories accumulate; nothing is overwritten.
- **Multi-signal hybrid search** — semantic embeddings, BM25 keyword matching, and entity linking scored in parallel and fused.
- **Entity linking** — entities are extracted, embedded, and linked across memories for retrieval boosting.
- **Agent-generated facts as first-class** — when an agent confirms an action, that information is stored with equal weight.

Mem0 offers two deployment modes:

- **Mem0 Platform** — Fully managed service at `api.mem0.ai` with automatic scaling, dashboard, graph memory, webhooks, and per-user API keys. Accessed via `MemoryClient`.
- **Mem0 Open Source** — Self-hosted SDK (Python + Node.js) with full control over LLMs, vector stores, embedders, and rerankers. Accessed via `Memory`.

## When to Use

- Building AI assistants or chatbots that need to remember users across sessions
- Creating customer support agents that recall past tickets and preferences
- Developing multi-agent systems where agents share or isolate memory
- Implementing personalized recommendations based on historical interactions
- Any LLM application where stateless context windows are insufficient
- Replacing OpenAI's native Memory API with a more cost-effective, faster alternative

## Core Concepts

### Memory Layers

Mem0 organizes memory into four layers:

- **Conversation memory** — In-flight messages within a single turn (tool calls, chain-of-thought). Lost after the turn.
- **Session memory** — Short-lived facts for a current task or channel. Scoped by `run_id`. Expires automatically when the session ends.
- **User memory** — Long-lived knowledge tied to a person or account. Scoped by `user_id`. Persists across interactions.
- **Organizational memory** — Shared context available to multiple agents or teams.

### The Memory Pipeline (v2)

Every `add()` call passes through three stages:

1. **Information extraction** — An LLM identifies key facts, preferences, and decisions from the conversation in a single pass. No UPDATE/DELETE — memories only accumulate.
2. **Conflict resolution** — Existing memories are checked for duplicates or contradictions; latest truth wins.
3. **Storage** — Memories land in vector storage with entity embeddings for future retrieval.

### Search Pipeline (v2)

1. **Query processing** — Natural-language query is cleaned and enriched.
2. **Multi-signal retrieval** — Semantic embeddings, BM25 keyword matching, and entity matching run in parallel.
3. **Filtering & reranking** — Logical filters narrow candidates; optional reranker fine-tunes ordering.
4. **Results delivery** — Formatted memories with metadata, timestamps, and categories return to the caller.

### Entity Scoping

Mem0 scopes memories by entity identifiers:

- `user_id` — Persistent persona or account
- `agent_id` — Distinct agent persona or tool
- `app_id` — White-label app or product surface
- `run_id` — Short-lived flow, ticket, or conversation thread

Use `run_id` when you want short-term context to expire automatically; rely on `user_id` for lasting personalization.

### Response Format

All operations return a consistent format: `{"results": [...]}`. No more `version` or `output_format` parameters needed.

## Installation / Setup

### Python SDK

```bash
pip install mem0ai
```

For enhanced hybrid search with BM25 keyword matching and entity extraction, install with NLP support:

```bash
pip install mem0ai[nlp]
python -m spacy download en_core_web_sm
```

### Node.js SDK

```bash
npm install mem0ai
```

### CLI

```bash
npm install -g @mem0/cli   # or: pip install mem0-cli

mem0 init
mem0 add "Prefers dark mode and vim keybindings" --user-id alice
mem0 search "What does Alice prefer?" --user-id alice
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
from mem0 import Memory

m = Memory()  # needs OPENAI_API_KEY; see reference for custom providers
```

Default OSS components (override via `Memory.from_config`):

- LLM: OpenAI `gpt-5-mini` (via `OPENAI_API_KEY`)
- Embeddings: OpenAI `text-embedding-3-small`
- Vector store: Local Qdrant at `/tmp/qdrant`
- History store: SQLite at `~/.mem0/history.db`

### Self-Hosted Server

```bash
cd server && make bootstrap   # one command: stack + admin + first API key
# or manual:
cd server && docker compose up -d    # http://localhost:3000
```

Auth is on by default. Set `AUTH_DISABLED=true` for local dev only.

## Usage Examples

### Basic Add and Search (OSS)

```python
from mem0 import Memory

m = Memory()

# Add memories from a conversation
messages = [
    {"role": "user", "content": "Hi, I'm Alex. I love basketball and gaming."},
    {"role": "assistant", "content": "Hey Alex! I'll remember your interests."}
]
result = m.add(messages, user_id="alex")

# Search with filters dict (v2: entity IDs inside filters)
results = m.search("What do you know about me?", filters={"user_id": "alex"})
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
    filters={"user_id": "alice"}
)

# Get all memories for a user
all_memories = client.get_all(user_id="alice")

# Update a specific memory
client.update(memory_id="<id>", data="Alice loves mountain hiking")

# Delete
client.delete(memory_id="<id>")
client.delete_all(user_id="alice")
```

### Full Chat with Memory Loop

```python
from openai import OpenAI
from mem0 import Memory

openai_client = OpenAI()
memory = Memory()

def chat_with_memories(message: str, user_id: str = "default_user") -> str:
    # Retrieve relevant memories
    relevant = memory.search(query=message, filters={"user_id": user_id}, top_k=3)
    memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant["results"])

    # Generate response with memory context
    system_prompt = f"You are a helpful AI.\nUser Memories:\n{memories_str}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
    response = openai_client.chat.completions.create(
        model="gpt-5-mini", messages=messages
    )
    assistant_response = response.choices[0].message.content

    # Store the conversation as new memory
    messages.append({"role": "assistant", "content": assistant_response})
    memory.add(messages, user_id=user_id)

    return assistant_response
```

### TypeScript / JavaScript (Platform)

```ts
import MemoryClient from "mem0ai";

const client = new MemoryClient({ apiKey: "your-api-key" });

await client.add(
  [{ role: "user", content: "I love hiking on weekends" }],
  { user_id: "alice" }
);

const results = await client.search("What does Alice like?", { user_id: "alice" });
```

### TypeScript / JavaScript (OSS)

```ts
import { Memory } from "mem0ai/oss";

const memory = new Memory();

await memory.add("I love hiking on weekends", { userId: "alice" });
const results = await memory.search("What does Alice like?", { userId: "alice" });
```

## Advanced Topics

**Memory Operations**: Add, search, update, delete workflows with v2 pipeline details and Platform vs OSS differences → [Memory Operations](reference/01-memory-operations.md)

**Configuration & Components**: LLM providers (18+), vector databases (24+), embedders (10+), rerankers (6+) with full setup guides → [Configuration and Components](reference/02-configuration-components.md)

**Platform Features**: Entity scoping, async clients, multimodal support, webhooks, custom categories, advanced retrieval, v2 memory filters → [Platform Features](reference/03-platform-features.md)

**Open Source Features**: Self-hosted REST API server, async memory, metadata filtering, reranker search, OpenAI compatibility → [Open Source Features](reference/04-open-source-features.md)

**API Reference**: REST endpoints for the managed Platform and OSS server → [API Reference](reference/05-api-reference.md)

**Integrations & Migration**: LangChain, CrewAI, LlamaIndex, AutoGen, Vercel AI SDK, MCP, and v1→v2 migration guide → [Integrations and Migration](reference/06-integrations-migration.md)

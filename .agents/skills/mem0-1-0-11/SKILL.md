---
name: mem0-1-0-11
description: A skill for using Mem0 v1.0.11, a universal self-improving memory layer for LLM applications that enables persistent context across sessions with support for both managed platform and open-source deployments.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.0.0"
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
---

# Mem0 v1.0.11

## Overview

Mem0 is a universal, self-improving memory layer for LLM applications that enables persistent context across sessions. It automatically extracts, stores, and retrieves relevant memories from conversations, allowing AI agents to remember user preferences, past interactions, and domain knowledge without manual prompt engineering.

**Key capabilities:**
- **Automatic memory extraction** - LLM-powered fact extraction from conversation transcripts
- **Multi-tier memory** - User, session, and agent-scoped memory organization
- **Hybrid search** - Vector similarity with optional reranking for precision
- **Graph memory** - Relationship-aware recall with Neo4j or Memgraph backends
- **Dual deployment** - Managed platform API or self-hosted open-source stack
- **Framework integrations** - LangChain, LlamaIndex, CrewAI, AutoGen, Vercel AI SDK, and 20+ partners

## When to Use

Use Mem0 when:
- Building AI assistants that need to remember user preferences across sessions
- Creating customer support bots that should recall past tickets and interactions
- Developing multi-agent systems requiring shared memory pools
- Implementing personalized recommendations based on historical data
- Needing audit trails for memory changes (compliance/debugging)
- Building RAG applications with persistent knowledge updates

**Don't use Mem0 when:**
- You only need single-session context (use standard prompt engineering instead)
- Your application requires sub-millisecond latency (vector search adds overhead)
- Memory is purely transient and never needs retrieval

## Core Concepts

### Memory Types

| Type | Scope | Use Case |
|------|-------|----------|
| **User Memory** | `user_id` | Personal preferences, habits, long-term facts |
| **Session Memory** | `run_id` | Temporary context within a conversation |
| **Agent Memory** | `agent_id` | Knowledge shared across all users for a specific agent |

### Memory Operations

1. **Add** - Extract facts from conversation messages and store as memories
2. **Search** - Retrieve relevant memories using semantic similarity
3. **Update** - Modify existing memory content
4. **Delete** - Remove individual or scoped memories
5. **History** - Audit trail of memory changes

### Architecture Components

- **LLM** - Fact extraction and memory summarization (OpenAI, Anthropic, Ollama, etc.)
- **Embedder** - Vector generation for semantic search (OpenAI, Vertex AI, HuggingFace)
- **Vector Store** - Memory storage and retrieval (Qdrant, Chroma, Pinecone, pgvector)
- **Reranker** - Optional precision layer for search results (Cohere, SentenceTransformer)
- **Graph DB** - Optional relationship tracking (Neo4j, Memgraph)

## Installation / Setup

### Platform API (Managed)

```bash
pip install mem0ai
# or
npm install mem0ai
```

Get API key from [Mem0 Platform](https://app.mem0.ai/dashboard/settings?tab=api-keys)

### Open Source (Self-Hosted)

```bash
pip install mem0ai
```

**Default configuration:**
- LLM: OpenAI `gpt-4.1-nano-2025-04-14`
- Embedder: OpenAI `text-embedding-3-small`
- Vector store: Qdrant (local, `/tmp/qdrant`)
- History store: SQLite (`~/.mem0/history.db`)

## Usage Examples

### Quick Start - Platform API

```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

# Add a memory from conversation
messages = [
    {"role": "user", "content": "I'm a vegetarian and allergic to nuts."},
    {"role": "assistant", "content": "Got it! I'll remember your dietary preferences."}
]
client.add(messages, user_id="alice")

# Search memories
results = client.search(
    "What are my dietary restrictions?",
    filters={"user_id": "alice"}
)
print(results)
```

### Quick Start - Open Source

```python
from mem0 import Memory

# Initialize with defaults (requires OPENAI_API_KEY env var)
memory = Memory()

# Add memory
messages = [
    {"role": "user", "content": "I love sci-fi movies but not thrillers."},
    {"role": "assistant", "content": "Got it! I'll suggest sci-fi in the future."}
]
result = memory.add(messages, user_id="alice")

# Search memories
results = memory.search("What movies does Alice like?", user_id="alice")
print(results)
```

### Node.js SDK

```javascript
import { MemoryClient } from "mem0ai"; // Platform API
// or
import { Memory } from "mem0ai/oss";   // Open Source

const client = new MemoryClient({ apiKey: "your-api-key" });

const messages = [
  { role: "user", content: "I prefer coffee over tea." },
  { role: "assistant", content: "Noted! Coffee it is." }
];

await client.add(messages, { user_id: "alice" });

const results = await client.search(
  "What does Alice prefer to drink?",
  { filters: { user_id: "alice" } }
);
```

### Async Operations (Python)

```python
from mem0 import AsyncMemory

memory = AsyncMemory()

# All operations are awaitable
result = await memory.add(
    messages=[{"role": "user", "content": "I travel to SF often"}],
    user_id="alice"
)

results = await memory.search("Where does Alice travel?", user_id="alice")

# Batch operations
tasks = [
    memory.add(messages=[...], user_id=f"user_{i}")
    for i in range(5)
]
await asyncio.gather(*tasks)
```

## Advanced Topics

See reference files for detailed guides:

- **[Configuration](references/01-configuration.md)** - Custom LLMs, vector stores, embedders, rerankers
- **[Memory Operations](references/02-memory-operations.md)** - Complete CRUD operations with filters and metadata
- **[Integrations](references/03-integrations.md)** - LangChain, CrewAI, AutoGen, Vercel AI SDK patterns
- **[Async Patterns](references/04-async-patterns.md)** - FastAPI integration, concurrency, error handling
- **[Platform Features](references/05-platform-features.md)** - Graph memory, webhooks, MCP, exports
- **[Research & Analysis](references/06-research-analysis.md)** - Academic paper analysis, LoCoMo benchmarks, production insights

## Migration from v0.x

v1.0 introduced breaking changes:
- API modernization with new client interfaces
- Async-by-default clients in Python
- Azure OpenAI support
- Enhanced reranker integration

See [MIGRATION_GUIDE_v1.0.md](https://github.com/mem0ai/mem0/blob/v1.0.11/MIGRATION_GUIDE_v1.0.md) for upgrade instructions.

## References

- **Official Documentation**: https://docs.mem0.ai
- **GitHub Repository**: https://github.com/mem0ai/mem0
- **Migration Guide v1.0**: https://github.com/mem0ai/mem0/blob/v1.0.11/MIGRATION_GUIDE_v1.0.md
- **Research Paper**: "Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory" (arXiv:2504.19413)
- **Paper PDF**: https://arxiv.org/pdf/2504.19413.pdf
- **Platform Dashboard**: https://app.mem0.ai
- **Discord Community**: https://mem0.dev/DiG

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Empty search results | Verify embedder model matches vector dimensions; check `user_id` filter scope |
| Qdrant connection errors | Confirm port 6333 is accessible; check API key if using managed Qdrant |
| Memory not persisting | Ensure `infer=True` (default) for automatic extraction; raw inserts skip conflict resolution |
| Slow operations | Enable reranker for precision; tune `top_k` parameter; consider caching |
| Dimension mismatch | Match embedder output dimensions with vector store configuration |

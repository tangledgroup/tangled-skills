# Integrations and Migration

## Agent Framework Integrations

### LangChain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from mem0 import Memory

memory = Memory()
llm = ChatOpenAI(model="gpt-4.1-mini")

def chat_with_langchain(message, user_id="user"):
    # Search memories
    results = memory.search(message, user_id=user_id)
    context = "\n".join(r["memory"] for r in results["results"])

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a helpful assistant.\nMemories: {context}"),
        ("human", "{input}")
    ])
    chain = prompt | llm
    response = chain.invoke({"input": message})

    # Store conversation
    memory.add([
        {"role": "user", "content": message},
        {"role": "assistant", "content": response.content}
    ], user_id=user_id)

    return response.content
```

### LangGraph

Build stateful, multi-actor applications with persistent memory. Use Mem0 as a node in the graph that injects context from past interactions.

### CrewAI

Tailor CrewAI agent outputs with personalized memory. Each crew member can have its own `agent_id` scope.

### LlamaIndex

Enhance RAG applications with intelligent memory layer alongside document retrieval.

### AutoGen

Microsoft's multi-agent conversation framework with Mem0 memory persistence across agent interactions.

### OpenAI Agents SDK

Use Mem0 as a tool within OpenAI's agent framework for persistent context.

### Google AI ADK

Google AI Agent Development Kit with Mem0 persistent memory layer.

### Mastra

TypeScript agent framework integration with Mem0 memory capabilities.

### Vercel AI SDK

Build AI-powered web applications with persistent memory using the Vercel AI SDK.

## Voice & Real-time Integrations

- **LiveKit** — Real-time voice and video AI with persistent memory
- **Pipecat** — Voice AI pipeline framework with memory capabilities
- **ElevenLabs** — Voice synthesis integration with conversational memory

## Developer Tools

- **Dify** — LLMOps platform integration
- **Flowise** — No-code LLM workflow builder
- **AgentOps** — Agent observability and monitoring
- **Raycast** — Quick memory access extension

## MCP Integration

Mem0 provides a Model Context Protocol (MCP) server for integrating with AI coding assistants like Claude Code, Cursor, Windsurf, and Gemini.

```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")
# MCP tools expose add, search, update, delete operations
# to AI agents through the standard MCP protocol
```

## CLI

```bash
npm install -g @mem0/cli   # or: pip install mem0-cli
mem0 init
mem0 add "Prefers dark mode and vim keybindings" --user-id alice
mem0 search "What does Alice prefer?" --user-id alice
```

## Migration Guide: v0 to v1

### What Changed

Mem0 v1.0 simplified the API by removing confusing version parameters. Everything now returns a consistent format: `{"results": [...]}`.

### Steps to Migrate

1. Upgrade: `pip install mem0ai==1.0.0`
2. Remove `version` and `output_format` parameters from code
3. Update response handling to use `result["results"]` instead of treating responses as lists

### Code Changes

**Memory API:**

```python
# Before (v0)
memory = Memory(config=MemoryConfig(version="v1.1"))
result = memory.add("I like pizza")

# After (v1.0+)
memory = Memory()
result = memory.add("I like pizza")
```

**Client API:**

```python
# Before (v0)
client.add(messages, output_format="v1.1")
client.search(query, version="v2", output_format="v1.1")

# After (v1.0+)
client.add(messages)
client.search(query)
```

**Response Handling:**

```python
# Before (v0)
result = memory.add("I like pizza")
for item in result:  # Treating as list
    print(item)

# After (v1.0+)
result = memory.add("I like pizza")
for item in result["results"]:
    print(item)
```

### Enhanced Message Handling (v1.0+)

Platform client now accepts three formats:

```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-key")

# 1. Single string (auto-converted to user message)
client.add("I like pizza", user_id="alice")

# 2. Single message dict
client.add({"role": "user", "content": "I like pizza"}, user_id="alice")

# 3. List of messages (conversation)
client.add([
    {"role": "user", "content": "I like pizza"},
    {"role": "assistant", "content": "I'll remember that!"}
], user_id="alice")
```

### Common Migration Issues

**`KeyError: 'results'`?** — Code still treating response as list. Update to `response["results"]`.

**`TypeError: unexpected keyword argument`?** — Still passing old `version` or `output_format` parameters. Remove them.

**Deprecation warnings?** — Remove explicit `version="v1.0"` from config.

### Configuration Changes

```python
# Before (v0)
config = MemoryConfig(
    version="v1.1",
    vector_store=VectorStoreConfig(...)
)

# After (v1.0+)
config = MemoryConfig(
    vector_store=VectorStoreConfig(...)
)
```

### Testing Migration

```python
from mem0 import Memory

memory = Memory()

result = memory.add("I like pizza", user_id="test")
assert "results" in result

search = memory.search("food", user_id="test")
assert "results" in search

all_memories = memory.get_all(user_id="test")
assert "results" in all_memories

print("Migration successful!")
```

## Platform vs Open Source Comparison

| Feature | Platform | Open Source |
|---------|----------|-------------|
| Setup | API key, no infra | Self-hosted, full control |
| Vector store | Managed | Choose from 24+ providers |
| Graph memory | Built-in | Neo4j, Memgraph, Neptune, Kuzu, AGE |
| Reranking | Toggle `rerank=True` | Configure provider |
| Dashboard | Web UI at app.mem0.ai | Custom tooling |
| Scaling | Automatic | Manual / Docker Compose |
| SOC 2 / GDPR | Built-in | Self-managed |
| Webhooks | Supported | Not available |
| Async mode | Default True | `AsyncMemory` class |
| Cost | Per-usage pricing | Free (open-source) |

## Research

Mem0 is backed by peer-reviewed research:

> Chhikara, P. et al. "Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory." arXiv:2504.19413 (2025).

Key findings:

- **+26% accuracy** over OpenAI Memory on LOCOMO benchmark
- **91% faster** responses than full-context approaches
- **90% lower** token usage than full-context approaches

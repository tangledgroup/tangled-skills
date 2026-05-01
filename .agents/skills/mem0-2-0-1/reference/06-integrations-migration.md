# Integrations and Migration

## Agent Frameworks

### LangChain

Integrate Mem0 as a LangChain tool or memory component:

```python
from langchain.agents import AgentExecutor
from mem0_langchain import Mem0

memory = Mem0()
# Use as tool in agent
agent = create_agent(tools=[memory], llm=llm)
```

### LangGraph

Build stateful multi-actor LangGraph apps with Mem0:

```python
from langgraph.graph import StateGraph
from mem0 import Memory

memory = Memory()

def chat_node(state):
    results = memory.search(state["query"], filters={"user_id": state["user_id"]})
    # Use results to inform response
    return {"context": results}

graph = StateGraph(State)
graph.add_node("chat", chat_node)
```

### CrewAI

Tailor CrewAI outputs with Mem0:

```python
from crewai import Agent, Task, Crew
from mem0 import Memory

memory = Memory()
agent = Agent(role="Support Agent", memory=memory)
```

### LlamaIndex

Layer memory on a LlamaIndex RAG app:

```python
from llama_index.core import VectorStoreIndex
from mem0 import Memory

memory = Memory()
# Use Mem0 alongside index for personalized context
```

### AutoGen

Integrate with Microsoft AutoGen multi-agent systems.

### Agno, Camel AI, ChatDev, Hermes

First-class integrations available for each framework. See docs at `docs.mem0.ai/integrations/`.

### OpenAI Agents SDK

Expose Mem0 as a tool in the OpenAI Agents SDK:

```python
from openai import OpenAI
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

# Register as tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_memories",
            "description": "Search user memories",
            "parameters": {...}
        }
    }
]
```

### Google AI ADK

Integrate with Google's Agent Development Kit.

### Vercel AI SDK

Use `@mem0/vercel-ai-provider` for React/Next.js applications:

```ts
import { createMem0 } from "@mem0/vercel-ai-provider";

const mem0 = createMem0({ apiKey: process.env.MEM0_API_KEY });
```

### Mastra

Integrate with Mastra (TypeScript) agent framework.

## AI Coding Tools

### Claude Code

Wire memory into Claude Code via MCP or the in-repo skill at `skills/mem0/`.

### Cursor

Wire memory into Cursor via MCP server connection.

### Codex

Wire memory into Codex / other editor assistants via MCP.

### OpenClaw

Wire Mem0 into Claude Code or editors via OpenClaw integration.

## MCP Integration

The hosted MCP server is at `https://mcp.mem0.ai` and requires a Platform API key. Self-hosted MCP ships with `openmemory/api/` (FastAPI).

9 MCP tools: `add_memory`, `search_memories`, `get_memories`, `get_memory`, `update_memory`, `delete_memory`, `delete_all_memories`, `delete_entities`, `list_entities`.

## Voice & Real-Time

- **LiveKit** — Real-time voice/video with memory
- **Pipecat** — Voice pipeline integration
- **ElevenLabs** — Voice synthesis with memory context

## Cloud & Infrastructure

- **AWS Bedrock** — Deploy with AWS managed model services

## Developer Tools

- **Dify** — LLMOps platform integration
- **Flowise** — No-code workflow builder
- **AgentOps** — Agent observability with memory metadata
- **Keywords AI** — Monitoring integration
- **Raycast** — Quick memory access via Raycast extension

## Migration: v1 to v2

### Breaking Changes

| Change | Old (v1) | New (v2) | Migration |
|---|---|---|---|
| Entity IDs on search/get_all | Top-level kwargs | Inside `filters` dict | `m.search("q", filters={"user_id": "..."})` — top-level kwargs raise `ValueError` |
| `top_k` default | 100 | 20 | Pass `top_k=100` explicitly to restore |
| `threshold` default | None (no filtering) | 0.1 | Pass `threshold=0.0` for old behavior |
| `threshold` validation | Any float | Must be in `[0, 1]` | Out-of-range values raise `ValueError` |
| `rerank` default | True | False | Pass `rerank=True` to restore |
| Entity ID validation | Any string | Trimmed; empty/whitespace rejected | Pass non-empty identifier without internal spaces |
| `messages` in `add()` | Could be None | Must be str/dict/list[dict] | Other types raise `Mem0ValidationError` |
| Extraction model | ADD + UPDATE + DELETE | ADD-only (single pass) | Memories accumulate; nothing is overwritten during extraction |

### Migration Steps

1. **Update installation**: `pip install --upgrade mem0ai` or `npm install mem0ai@latest`

2. **Update search calls**: Move entity IDs from top-level kwargs into `filters` dict:

```python
# Old (v1)
m.search("query", user_id="alice")

# New (v2)
m.search("query", filters={"user_id": "alice"})
```

3. **Update add calls**: Ensure `messages` is never None and is a valid type:

```python
# Valid in v2
m.add([{"role": "user", "content": "Hello"}], user_id="alice")
m.add("Simple string message", user_id="alice")
```

4. **Update vector store dependencies**: If using entity linking, install NLP extras:

```bash
pip install mem0ai[nlp]
python -m spacy download en_core_web_sm
```

5. **Review defaults**: Check if your code relies on old defaults for `top_k`, `threshold`, or `rerank` and adjust explicitly.

### Common Issues After Migration

- **`ValueError: Top-level entity parameters not supported`** — Move entity IDs into `filters` dict on `search()` and `get_all()`.
- **Search returns fewer results** — Default `top_k` is now 20 (was 100) and `threshold` is 0.1 (was None). Adjust explicitly.
- **Score values are different** — v2 uses multi-signal scoring (semantic + BM25 + entity). Scores are not directly comparable with v1.
- **spaCy model not found** — Install NLP extras and download the model.
- **Entity store collection creation fails** — Check vector store connectivity and permissions.

## Migration: OSS to Platform

Move from self-hosted to managed Mem0 Platform:

1. Replace `Memory()` with `MemoryClient(api_key="...")`
2. Provider configuration (LLM, embedder, vector store) is handled server-side on Platform
3. Platform-only features become available: webhooks, custom categories, advanced retrieval
4. API surface is aligned between OSS v2 and Platform for `add()`, `search()`, `update()`, `delete()`

# SDKs & Tutorials

## Available SDKs

Official A2A SDKs are available in five languages:

- **Python:** `a2a-sdk` (PyPI) — primary reference implementation
- **Go:** Official Go SDK
- **JavaScript/TypeScript:** `@a2a-js/sdk`
- **Java:** Maven package
- **.NET:** NuGet package `A2A`

The project also provides the A2A Inspector for validation and a Technology Compatibility Kit (TCK) for conformance testing.

## Python SDK Patterns

### Core Components

The Python SDK provides these key abstractions:

- **`a2a.types`:** Data types (Message, Task, Part, AgentCard, AgentSkill, etc.)
- **`a2a.server`:** Server-side components (AgentExecutor, DefaultRequestHandler, TaskStore)
- **`create_client()`:** Client factory based on Agent Card
- **`new_text_message()`:** Helper to create text Parts
- **Route factories:** `create_agent_card_routes()`, `create_jsonrpc_routes()`, `create_rest_routes()`

### Server Setup

A2A servers are built by combining an AgentExecutor (your business logic) with the SDK's request handling infrastructure:

```python
from a2a.server import DefaultRequestHandler, create_agent_card_routes, create_jsonrpc_routes
from a2a.server.agent_execution import AgentExecutor
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from starlette.applications import Starlette
import uvicorn

# 1. Define your agent executor (implements execute and cancel)
class MyAgentExecutor(AgentExecutor):
    async def execute(self, context, event_queue):
        # Process the request and enqueue events
        ...

    async def cancel(self, context, event_queue):
        # Handle cancellation
        ...

# 2. Define the Agent Card
agent_card = AgentCard(
    name="My Agent",
    description="An example A2A agent",
    version="1.0.0",
    supported_interfaces=[...],
    capabilities=AgentCapabilities(streaming=True),
    skills=[
        AgentSkill(
            id="my-skill",
            name="My Skill",
            description="Does something useful",
            tags=["example"],
            examples=["Do something"],
        )
    ],
)

# 3. Create the request handler
request_handler = DefaultRequestHandler(
    agent_executor=MyAgentExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)

# 4. Build the Starlette app with routes
app = Starlette(routes=(
    create_agent_card_routes(agent_card) +
    create_jsonrpc_routes(request_handler, '/')
))

# 5. Run the server
uvicorn.run(app, host='127.0.0.1', port=9999)
```

### AgentExecutor Interface

The `AgentExecutor` abstract base class defines two primary methods:

- **`async def execute(self, context: RequestContext, event_queue: EventQueue)`:** Handles incoming requests that expect a response or stream of events. The `RequestContext` provides the user's message and any existing task details. The `EventQueue` is used to send back `Message`, `Task`, `TaskStatusUpdateEvent`, or `TaskArtifactUpdateEvent` objects.
- **`async def cancel(self, context: RequestContext, event_queue: EventQueue)`:** Handles requests to cancel an ongoing task.

### Typical Execute Flow

1. A2A server retrieves the current task from context (creates new task if none exists) and adds it to the EventQueue
2. Enqueue a `TaskStatusUpdateEvent` with state `TASK_STATE_WORKING`
3. Execute business logic
4. Enqueue a `TaskArtifactUpdateEvent` containing the result
5. Enqueue a `TaskStatusUpdateEvent` with state `TASK_STATE_COMPLETED`

### Client Setup

```python
from a2a import create_client, new_text_message, Role
from a2a.types import SendMessageRequest

# Fetch agent card
card = await resolver.get_agent_card()

# Create non-streaming client
client = create_client(card)

# Send message
response = await client.send_message(
    SendMessageRequest(message=new_text_message("Say hello.", Role.ROLE_USER))
)
task = response.result.task

# Create streaming client
streaming_client = create_client(card, streaming=True)

# Send streaming message
async for chunk in await streaming_client.send_message(
    SendMessageRequest(message=new_text_message("Say hello.", Role.ROLE_USER))
):
    print(chunk)

await streaming_client.close()
```

### Streaming Response Pattern

A streaming response yields discrete chunks:

1. Initial `task` object with `TASK_STATE_SUBMITTED`
2. `status_update` with `TASK_STATE_WORKING`
3. `artifact_update` with the result content
4. Final `status_update` with `TASK_STATE_COMPLETED`

### Multi-Turn Conversation Pattern

For interactions requiring clarification:

1. Client sends initial ambiguous query
2. Agent responds with Task in `TASK_STATE_INPUT_REQUIRED`, status message contains the question
3. Client sends follow-up message including `taskId` and `contextId` from the first turn's response
4. Agent resumes processing within the same task

### Task Store

The `DefaultRequestHandler` uses a `TaskStore` to manage the lifecycle of tasks, especially for stateful interactions, streaming, and resubscription. Even simple agent executors need a task store. The SDK provides `InMemoryTaskStore` for development; production deployments should use persistent stores.

### Server Frameworks

The route factories produce Starlette-compatible routes that can be attached to:
- **Starlette:** Native support
- **FastAPI:** Compatible via Starlette integration
- Other ASGI frameworks

This gives developers control over authentication, logging, and other middleware features.

## Python Tutorial Overview

The official Python tutorial covers building an A2A agent step by step:

1. **Introduction:** Basic concepts and components of an A2A server
2. **Setup:** Python environment and A2A SDK installation
3. **Agent Skills & Agent Card:** Defining what the agent can do and how it describes itself
4. **The Agent Executor:** Implementing agent logic via the `AgentExecutor` interface
5. **Starting the Server:** Running with Starlette/Uvicorn
6. **Interacting with the Server:** Sending requests as a client
7. **Streaming & Multi-Turn Interactions:** Advanced patterns with LangGraph integration
8. **Next Steps:** Further exploration

### Hello World Example

The `helloworld` sample demonstrates:
- Simple `AgentSkill` definition ("Returns hello world")
- Basic `AgentCard` with JSONRPC interface
- Minimal `AgentExecutor` that returns "Hello, World!"
- Non-streaming and streaming client interactions
- Extended Agent Card support

### LangGraph Example

The `langgraph` sample demonstrates:
- LLM integration (Gemini via LangChain/LangGraph)
- Task state management with `InMemoryTaskStore`
- Streaming with `TaskStatusUpdateEvent` and `TaskArtifactUpdateEvent`
- Multi-turn conversation (`TASK_STATE_INPUT_REQUIRED`)
- Tool usage within the agent (e.g., currency exchange rate lookup)

## A2A Request Lifecycle

The complete request lifecycle follows four main steps:

1. **Agent Discovery:** Client fetches Agent Card from `/.well-known/agent-card.json`
2. **Authentication:** Client parses `securitySchemes`, obtains credentials via out-of-band flow (e.g., OAuth 2.0)
3. **sendMessage API:** Client sends POST with credentials; server processes and returns Task
4. **sendMessageStream API:** Client receives real-time stream of task events (submitted → working → artifact updates → completed)

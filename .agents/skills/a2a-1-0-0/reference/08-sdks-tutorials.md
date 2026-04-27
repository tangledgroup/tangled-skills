# SDKs & Tutorials

## Available SDKs

Official A2A SDKs are available in five languages:

- **Python:** `a2a-sdk` (PyPI) — primary reference implementation
- **Go:** Official Go SDK
- **JavaScript/TypeScript:** `@a2a-js/sdk`
- **Java:** Maven package
- **.NET:** NuGet package `A2A`

The project also provides the A2A Inspector for validation and a Technology Compatibility Kit (TCK) for conformance testing.

## Python SDK Overview

### Core Modules

- **`a2a.types`:** Data types — `AgentCard`, `AgentSkill`, `AgentCapabilities`, `AgentInterface`, `Message`, `Task`, `Part`, `Role`, etc.
- **`a2a.server`:** Server-side components — `AgentExecutor`, `DefaultRequestHandler`, `A2AStarletteApplication`
- **`a2a.server.agent_execution`:** `AgentExecutor` abstract base class, `RequestContext`
- **`a2a.server.events`:** `EventQueue` for sending events back to clients
- **`a2a.server.routes`:** Route factories — `create_agent_card_routes()`, `create_jsonrpc_routes()`, `create_rest_routes()`
- **`a2a.server.tasks`:** Task stores — `InMemoryTaskStore`, `InMemoryPushNotificationConfigStore`, `BasePushNotificationSender`
- **`a2a.client`:** Client components — `A2ACardResolver`, `ClientConfig`, `create_client()`
- **`a2a.helpers`:** Utility functions — `new_text_message()`, `new_text_artifact()`, `new_task_from_user_message()`, `display_agent_card()`
- **`a2a.utils`:** Utilities — `new_agent_text_message()`, `new_task()`
- **`a2a.types.a2a_pb2`:** Protocol Buffer types — `TaskStatusUpdateEvent`, `TaskArtifactUpdateEvent`, `TaskState`, `TaskStatus`, `Role`, `SendMessageRequest`, etc.

### Environment Setup

```bash
# Clone the samples repository
git clone https://github.com/a2aproject/a2a-samples.git -b main --depth 1
cd a2a-samples

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install SDK and dependencies
pip install -r samples/python/requirements.txt

# Verify installation
python -c "import a2a; print('A2A SDK imported successfully')"
```

## Agent Skills & Agent Card

### AgentSkill

An `AgentSkill` describes a specific capability or function the agent can perform. It tells clients what kinds of tasks the agent is good for.

**Attributes (defined in `a2a.types`):**

- `id` (str): Unique identifier for the skill
- `name` (str): Human-readable name
- `description` (str): Detailed explanation of what the skill does
- `tags` (list[str]): Keywords for categorization and discovery
- `examples` (list[str]): Sample prompts or use cases
- `input_modes` (list[str]): Supported input MIME types (e.g., `"text/plain"`, `"application/json"`)
- `output_modes` (list[str]): Supported output MIME types
- `security_requirements` (list[str]): Security schemes necessary for this skill

**Example:**

```python
from a2a.types import AgentSkill

skill = AgentSkill(
    id='hello_world',
    name='Returns hello world',
    description='just returns hello world',
    tags=['hello world'],
    examples=['hi', 'hello world'],
)
```

### AgentCard

The Agent Card is a JSON document that an A2A Server makes available, typically at `/.well-known/agent-card.json`. It's the digital business card for the agent.

**Key attributes (defined in `a2a.types`):**

- `name`, `description`, `version`: Basic identity information
- `supported_interfaces`: Ordered list of `AgentInterface` objects (endpoints and protocols). First entry is preferred.
- `capabilities`: `AgentCapabilities` object declaring supported features (`streaming`, `push_notifications`, `extended_agent_card`)
- `default_input_modes` / `default_output_modes`: Default MIME types for the agent
- `skills`: List of `AgentSkill` objects
- `provider`: Organization information
- `security_schemes` / `security`: Authentication requirements

**Public Agent Card example:**

```python
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)

skill = AgentSkill(
    id='hello_world',
    name='Returns hello world',
    description='just returns hello world',
    tags=['hello world'],
    examples=['hi', 'hello world'],
)

public_agent_card = AgentCard(
    name='Hello World Agent',
    description='Just a hello world agent',
    version='0.0.1',
    default_input_modes=['text/plain'],
    default_output_modes=['text/plain'],
    capabilities=AgentCapabilities(
        streaming=True,
        extended_agent_card=True,
    ),
    supported_interfaces=[
        AgentInterface(
            protocol_binding='JSONRPC',
            url='http://127.0.0.1:9999',
        )
    ],
    skills=[skill],  # Only the basic skill for the public card
)
```

### Extended Agent Card

Agents can serve a richer Agent Card to authenticated clients. The extended card includes additional skills, capabilities, or configuration not exposed publicly.

```python
extended_skill = AgentSkill(
    id='super_hello_world',
    name='Returns a SUPER Hello World',
    description='A more enthusiastic greeting, only for authenticated users.',
    tags=['hello world', 'super', 'extended'],
    examples=['super hi', 'give me a super hello'],
)

extended_agent_card = AgentCard(
    name='Hello World Agent - Extended Edition',
    description='The full-featured hello world agent for authenticated users.',
    version='0.0.2',
    default_input_modes=['text/plain'],
    default_output_modes=['text/plain'],
    capabilities=AgentCapabilities(
        streaming=True,
        extended_agent_card=True,
    ),
    supported_interfaces=[
        AgentInterface(
            protocol_binding='JSONRPC',
            url='http://127.0.0.1:9999',
        )
    ],
    skills=[skill, extended_skill],  # Both skills for the extended card
)
```

The `DefaultRequestHandler` serves the public card at `/.well-known/agent-card.json` and the extended card via the `GetExtendedAgentCard` RPC method to authenticated clients. Clients should replace their cached public Agent Card with the extended version for the session duration.

## The Agent Executor

The core logic of how an A2A agent processes requests and generates responses/events is handled by an **Agent Executor**. The SDK provides an abstract base class `a2a.server.agent_execution.AgentExecutor` that you implement.

### AgentExecutor Interface

Two primary methods:

- **`async def execute(self, context: RequestContext, event_queue: EventQueue)`:** Handles incoming requests that expect a response or stream of events. The `RequestContext` provides the user's message and any existing task details. The `EventQueue` is used to send back `Message`, `Task`, `TaskStatusUpdateEvent`, or `TaskArtifactUpdateEvent` objects.
- **`async def cancel(self, context: RequestContext, event_queue: EventQueue)`:** Handles requests to cancel an ongoing task.

### Hello World Executor (Complete Example)

```python
from a2a.helpers import (
    new_task_from_user_message,
    new_text_artifact,
    new_text_message,
)
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types.a2a_pb2 import (
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)


class HelloWorldAgent:
    """Business logic layer."""

    async def invoke(self) -> str:
        return 'Hello, World!'


class HelloWorldAgentExecutor(AgentExecutor):
    """A2A protocol bridge to business logic."""

    def __init__(self) -> None:
        self.agent = HelloWorldAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        # Step 1: Get or create task
        task = context.current_task or new_task_from_user_message(
            context.message
        )
        await event_queue.enqueue_event(task)

        # Step 2: Signal working state
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(
                    state=TaskState.TASK_STATE_WORKING,
                    message=new_text_message('Processing request...'),
                ),
            )
        )

        # Step 3: Execute business logic
        result = await self.agent.invoke()

        # Step 4: Enqueue artifact with result
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                artifact=new_text_artifact(name='result', text=result),
            )
        )

        # Step 5: Signal completion
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED),
            )
        )

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')
```

**Execute flow explained:**

1. The A2A server retrieves the current task from context. If none exists, it creates a new task and enqueues it
2. Enqueue `TaskStatusUpdateEvent` with state `TASK_STATE_WORKING`
3. Execute actual business logic
4. Enqueue `TaskArtifactUpdateEvent` containing the result
5. Enqueue `TaskStatusUpdateEvent` with state `TASK_STATE_COMPLETED`

Both `Send Message` and `Send Streaming Message` requests are handled by the same `execute` method — the SDK's request handler determines whether to stream based on the client's request type.

### TaskUpdater Helper

For more complex executors, the SDK provides `TaskUpdater` as a convenience wrapper around `EventQueue`:

```python
from a2a.server.tasks import TaskUpdater
from a2a.utils import new_agent_text_message, new_task
from a2a.types import TaskState

# In execute method:
task = context.current_task or new_task(context.message)
await event_queue.enqueue_event(task)
updater = TaskUpdater(event_queue, task.id, task.context_id)

# Update status with message
await updater.update_status(
    TaskState.working,
    new_agent_text_message('Processing...', task.context_id, task.id),
)

# Add artifact
await updater.add_artifact(
    [Part(root=TextPart(text='result'))],
    name='output',
)

# Mark complete
await updater.complete()
```

## Starting the Server

### Route Factories

The Python SDK provides route factories that produce Starlette-compatible routes:

- **`create_agent_card_routes(public_agent_card)`:** Returns routes that expose the Agent Card at `/.well-known/agent-card.json` for public discovery
- **`create_jsonrpc_routes(request_handler, '/')`:** Returns routes that handle all A2A JSON-RPC method calls by delegating to the request handler
- **`create_rest_routes()`:** Returns REST-style routes

### Default Server Setup (Starlette + Uvicorn)

```python
import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from starlette.applications import Starlette

request_handler = DefaultRequestHandler(
    agent_executor=HelloWorldAgentExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=public_agent_card,
    extended_agent_card=extended_agent_card,
)

routes = []
routes.extend(create_agent_card_routes(public_agent_card))
routes.extend(create_jsonrpc_routes(request_handler, '/'))

app = Starlette(routes=routes)
uvicorn.run(app, host='127.0.0.1', port=9999)
```

### DefaultRequestHandler

The `DefaultRequestHandler` is the core server-side component. It:

- Routes incoming A2A RPC calls to appropriate methods on your executor (`execute`, `cancel`)
- Uses the `TaskStore` to manage task lifecycle (stateful interactions, streaming, resubscription)
- Verifies the agent's declared capabilities when processing requests (e.g., checks whether streaming or push notifications are supported)
- Serves the extended Agent Card via `GetExtendedAgentCard` RPC method

### A2AStarletteApplication (Higher-Level API)

For more complex setups, the SDK provides `A2AStarletteApplication`:

```python
from a2a.server.apps import A2AStarletteApplication
from a2a.server.tasks import (
    BasePushNotificationSender,
    InMemoryPushNotificationConfigStore,
    InMemoryTaskStore,
)
import httpx

httpx_client = httpx.AsyncClient()
push_config_store = InMemoryPushNotificationConfigStore()
push_sender = BasePushNotificationSender(
    httpx_client=httpx_client,
    config_store=push_config_store,
)

request_handler = DefaultRequestHandler(
    agent_executor=CurrencyAgentExecutor(),
    task_store=InMemoryTaskStore(),
    push_config_store=push_config_store,
    push_sender=push_sender,
)

server = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler,
)

uvicorn.run(server.build(), host='localhost', port=10000)
```

### Framework Compatibility

The route factories produce Starlette-compatible routes that can be attached to:
- **Starlette:** Native support
- **FastAPI:** Compatible via Starlette integration
- Other ASGI frameworks

This gives developers control over authentication, logging, and other middleware features.

## Interacting with the Server (Client)

### A2ACardResolver

Fetches the Agent Card from a server's `/.well-known/agent-card.json` endpoint:

```python
import httpx
from a2a.client import A2ACardResolver

base_url = 'http://127.0.0.1:9999'

async with httpx.AsyncClient() as httpx_client:
    resolver = A2ACardResolver(
        httpx_client=httpx_client,
        base_url=base_url,
    )
    agent_card = await resolver.get_agent_card()
```

### Creating a Client

```python
from a2a.client import ClientConfig, create_client

# Non-streaming client
config = ClientConfig(streaming=False)
client = await create_client(agent=agent_card, client_config=config)

# Streaming client
streaming_config = ClientConfig(streaming=True)
streaming_client = await create_client(
    agent=agent_card,
    client_config=streaming_config,
)
```

### Sending a Non-Streaming Message

```python
from a2a.helpers import new_text_message
from a2a.types.a2a_pb2 import Role, SendMessageRequest

message = new_text_message('Say hello.', role=Role.ROLE_USER)
request = SendMessageRequest(message=message)

async for chunk in client.send_message(request):
    print(chunk)  # Single final Task or Message response
```

The `send_message` method returns an async iterator that yields a single final `Task` or `Message` response from the agent.

### Sending a Streaming Message

```python
streaming_response = streaming_client.send_message(request)

async for chunk in streaming_response:
    print('Response chunk:')
    print(chunk)

await streaming_client.close()  # Release the underlying HTTP connection
```

A streaming response yields discrete chunks:
1. Initial `task` with `TASK_STATE_SUBMITTED`
2. `status_update` with `TASK_STATE_WORKING` and progress message
3. `artifact_update` with the result content
4. Final `status_update` with `TASK_STATE_COMPLETED`

### Fetching Extended Agent Card

```python
from a2a.types.a2a_pb2 import GetExtendedAgentCardRequest
from a2a.helpers import display_agent_card

extended_card = await client.get_extended_agent_card(
    GetExtendedAgentCardRequest()
)
display_agent_card(extended_card)
```

### Complete Test Client Example

```python
import asyncio
import httpx

from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import display_agent_card, new_text_message
from a2a.types.a2a_pb2 import (
    GetExtendedAgentCardRequest,
    Role,
    SendMessageRequest,
)


async def main() -> None:
    base_url = 'http://127.0.0.1:9999'

    async with httpx.AsyncClient() as httpx_client:
        # 1. Fetch agent card
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        public_card = await resolver.get_agent_card()
        display_agent_card(public_card)

        # 2. Non-streaming call
        config = ClientConfig(streaming=False)
        client = await create_client(agent=public_card, client_config=config)

        message = new_text_message('Say hello.', role=Role.ROLE_USER)
        request = SendMessageRequest(message=message)

        async for chunk in client.send_message(request):
            print(chunk)

        # 3. Streaming call
        streaming_config = ClientConfig(streaming=True)
        streaming_client = await create_client(
            agent=public_card, client_config=streaming_config
        )

        async for chunk in streaming_client.send_message(request):
            print('Chunk:', chunk)

        await streaming_client.close()

        # 4. Extended agent card
        extended_card = await client.get_extended_agent_card(
            GetExtendedAgentCardRequest()
        )
        display_agent_card(extended_card)

        await client.close()


if __name__ == '__main__':
    asyncio.run(main())
```

## LangGraph Example (Advanced)

The LangGraph sample demonstrates an LLM-powered agent with streaming, multi-turn conversations, and tool use.

### Server Setup

```python
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import (
    BasePushNotificationSender,
    InMemoryPushNotificationConfigStore,
    InMemoryTaskStore,
)
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
import httpx
import uvicorn

capabilities = AgentCapabilities(streaming=True, push_notifications=True)
skill = AgentSkill(
    id='convert_currency',
    name='Currency Exchange Rates Tool',
    description='Helps with exchange values between various currencies',
    tags=['currency conversion', 'currency exchange'],
    examples=['What is exchange rate between USD and GBP?'],
)
agent_card = AgentCard(
    name='Currency Agent',
    description='Helps with exchange rates for currencies',
    version='1.0.0',
    default_input_modes=['text/plain'],
    default_output_modes=['text/plain'],
    capabilities=capabilities,
    skills=[skill],
)

httpx_client = httpx.AsyncClient()
push_config_store = InMemoryPushNotificationConfigStore()
push_sender = BasePushNotificationSender(
    httpx_client=httpx_client,
    config_store=push_config_store,
)
request_handler = DefaultRequestHandler(
    agent_executor=CurrencyAgentExecutor(),
    task_store=InMemoryTaskStore(),
    push_config_store=push_config_store,
    push_sender=push_sender,
)
server = A2AStarletteApplication(
    agent_card=agent_card, http_handler=request_handler
)

uvicorn.run(server.build(), host='localhost', port=10000)
```

### LLM-Powered Executor with TaskUpdater

```python
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError, InvalidParamsError, Part, TaskState, TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError


class CurrencyAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = CurrencyAgent()  # LangGraph + LLM agent

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        query = context.get_user_input()
        task = context.current_task or new_task(context.message)
        await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        try:
            async for item in self.agent.stream(query, task.context_id):
                if not item['is_task_complete'] and not item['require_user_input']:
                    # Intermediate progress update
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            item['content'], task.context_id, task.id,
                        ),
                    )
                elif item['require_user_input']:
                    # Multi-turn: agent needs clarification
                    await updater.update_status(
                        TaskState.input_required,
                        new_agent_text_message(
                            item['content'], task.context_id, task.id,
                        ),
                        final=True,
                    )
                    break
                else:
                    # Task complete — add artifact and finalize
                    await updater.add_artifact(
                        [Part(root=TextPart(text=item['content']))],
                        name='conversion_result',
                    )
                    await updater.complete()
                    break
        except Exception as e:
            raise ServerError(error=InternalError()) from e

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise ServerError(error=UnsupportedOperationError())
```

### Key Patterns Demonstrated

1. **LLM Integration:** The `CurrencyAgent` uses LangGraph with an LLM (e.g., Gemini) and tools (e.g., exchange rate lookup). The executor bridges the LLM's streaming output to A2A events.

2. **Task State Management:** `DefaultRequestHandler` with `InMemoryTaskStore` persists and retrieves task state across interactions. For `Send Message`, the handler returns a full `Task` object.

3. **Streaming Events:** The executor enqueues different event types as the LLM processes:
   - `TaskStatusUpdateEvent` for intermediate progress ("Looking up exchange rates...")
   - `TaskArtifactUpdateEvent` when the final answer is ready
   - Final `TaskStatusUpdateEvent` with `TASK_STATE_COMPLETED` to close the stream

4. **Multi-Turn Conversation:** When the agent needs clarification (e.g., user asks "how much is 100 USD?"), the executor transitions to `TASK_STATE_INPUT_REQUIRED` with a question message. The stream closes. The client then sends a follow-up message with the same `taskId` and `contextId` to provide missing information, continuing the same task.

### Key Source Files in LangGraph Sample

- `__main__.py`: Server setup using `A2AStarletteApplication` and `DefaultRequestHandler`
- `agent.py`: The `CurrencyAgent` with LangGraph, LLM model, and tool definitions
- `agent_executor.py`: The `CurrencyAgentExecutor` implementing `execute` and `cancel`
- `test_client.py`: Demonstrates single-turn, streaming, and multi-turn interactions

## A2A Request Lifecycle

The complete request lifecycle follows four main steps:

1. **Agent Discovery:** Client fetches Agent Card from `/.well-known/agent-card.json`
2. **Authentication:** Client parses `securitySchemes`, obtains credentials via out-of-band flow (e.g., OAuth 2.0)
3. **sendMessage API:** Client sends POST with credentials; server processes and returns Task
4. **sendMessageStream API:** Client receives real-time stream of task events (submitted → working → artifact updates → completed)

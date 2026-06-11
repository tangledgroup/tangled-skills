# Responses API

## Contents
- Basic Usage
- Streaming Responses
- Background Tasks
- Structured Outputs (Parse)
- Tool Calling
- Input Tokens Counting
- WebSocket Connections

## Basic Usage

The Responses API is the primary interface for interacting with OpenAI models. Use `client.responses.create()`:

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5.2",
    instructions="You are a coding assistant.",
    input="How do I check if an object is an instance of a class?",
)
print(response.output_text)
```

Async:

```python
from openai import AsyncOpenAI
client = AsyncOpenAI()

response = await client.responses.create(
    model="gpt-5.2",
    input="Explain disestablishmentarianism to a five year old.",
)
print(response.output_text)
```

### Input as Structured Messages

Pass a list of message items instead of a plain string:

```python
response = client.responses.create(
    model="gpt-5.2",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "What is in this image?"},
                {"type": "input_image", "image_url": "https://example.com/photo.jpg"},
            ],
        }
    ],
)
```

### Key Parameters

- `model` — Model identifier (e.g., `gpt-5.2`, `gpt-4o-2024-08-06`)
- `instructions` — System-level instructions
- `input` — String or list of `ResponseInputItemParam`
- `stream` — Enable SSE streaming (`True`/`False`)
- `background` — Run in background, resumable via `response_id`
- `tools` — List of tool definitions
- `tool_choice` — `"auto"`, `"none"`, or `{"type": "function", "name": "..."}`
- `max_output_tokens` — Max tokens in response
- `temperature` — Sampling temperature (0-2)
- `previous_response_id` — Chain responses for multi-turn
- `truncation` — `"auto"` or message list management strategy
- `store` — Whether to store the response (`True`/`False`)

## Streaming Responses

Pass `stream=True` and iterate over events:

```python
stream = client.responses.create(
    model="gpt-5.2",
    input="Write a one-sentence bedtime story about a unicorn.",
    stream=True,
)
for event in stream:
    print(event)
```

Async:

```python
stream = await client.responses.create(
    model="gpt-5.2",
    input="Tell me a joke.",
    stream=True,
)
async for event in stream:
    print(event)
```

### Streaming with Structured Outputs

Use `client.responses.stream()` as a context manager with `text_format`:

```python
from pydantic import BaseModel
from typing import List

class Step(BaseModel):
    explanation: str
    output: str

class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str

with client.responses.stream(
    input="solve 8x + 31 = 2",
    model="gpt-4o-2024-08-06",
    text_format=MathResponse,
) as stream:
    for event in stream:
        if "output_text" in event.type:
            print(event)
    print(stream.get_final_response())
```

## Background Tasks

Set `background=True` to start a response that continues server-side. Resume later with the response ID:

```python
id = None
with client.responses.create(
    input="solve 8x + 31 = 2",
    model="gpt-4o-2024-08-06",
    background=True,
    stream=True,
) as stream:
    for event in stream:
        if event.type == "response.created":
            id = event.response.id
        if "output_text" in event.type:
            print(event)
        if event.sequence_number == 10:
            break

# Resume from sequence 11
with client.responses.retrieve(response_id=id, stream=True, starting_after=10) as stream:
    for event in stream:
        if "output_text" in event.type:
            print(event)
```

### Background Streaming

Combine `background=True` with `client.responses.stream()`:

```python
id = None
with client.responses.stream(
    input="solve 8x + 31 = 2",
    model="gpt-4o-2024-08-06",
    text_format=MathResponse,
    background=True,
) as stream:
    for event in stream:
        if event.type == "response.created":
            id = event.response.id
        if "output_text" in event.type:
            print(event)
        if event.sequence_number == 10:
            break

# Resume streaming from where you left off
with client.responses.stream(
    response_id=id,
    starting_after=10,
    text_format=MathResponse,
) as stream:
    for event in stream:
        if "output_text" in event.type:
            print(event)
    print(stream.get_final_response())
```

## Structured Outputs (Parse)

Use `client.responses.parse()` with a Pydantic model to get typed output:

```python
from pydantic import BaseModel
from typing import List

class Step(BaseModel):
    explanation: str
    output: str

class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str

rsp = client.responses.parse(
    input="solve 8x + 31 = 2",
    model="gpt-4o-2024-08-06",
    text_format=MathResponse,
)

for output in rsp.output:
    if output.type != "message":
        raise Exception("Unexpected non-message")
    for item in output.content:
        if item.type != "output_text":
            raise Exception("Unexpected output type")
        if not item.parsed:
            raise Exception("Could not parse response")
        print(item.parsed)
        print("answer:", item.parsed.final_answer)
```

## Tool Calling

Define tools as dictionaries and pass to `client.responses.create()`:

```python
from typing import List
from openai.types.responses.tool_param import ToolParam
from openai.types.responses.response_input_item_param import ResponseInputItemParam

tools: List[ToolParam] = [
    {
        "type": "function",
        "name": "get_current_weather",
        "description": "Get current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City and state"},
                "unit": {"type": "string", "enum": ["c", "f"]},
            },
            "required": ["location", "unit"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]

input_items: List[ResponseInputItemParam] = [
    {
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": "What's the weather in San Francisco?"}],
    }
]

response = client.responses.create(
    model="gpt-5",
    instructions="You are a concise assistant.",
    input=input_items,
    tools=tools,
    tool_choice={"type": "function", "name": "get_current_weather"},
)
```

### Streaming with Tools

```python
import openai
from pydantic import BaseModel

class Query(BaseModel):
    table_name: str
    columns: List[str]

with client.responses.stream(
    model="gpt-4o-2024-08-06",
    input="look up all my orders in november",
    tools=[openai.pydantic_function_tool(Query)],
) as stream:
    for event in stream:
        print(event)
```

### Structured Outputs with Tools

```python
response = client.responses.parse(
    model="gpt-4o-2024-08-06",
    input="look up all my orders in november of last year",
    tools=[openai.pydantic_function_tool(Query)],
)

function_call = response.output[0]
assert function_call.type == "function_call"
assert isinstance(function_call.parsed_arguments, Query)
print("table name:", function_call.parsed_arguments.table_name)
```

## Input Tokens Counting

Estimate input token count before generating a full response:

```python
response = client.responses.input_tokens.count(
    model="gpt-5",
    instructions="You are a concise assistant.",
    input=input_items,
    tools=tools,
    tool_choice={"type": "function", "name": "get_current_weather"},
)
print(f"input tokens: {response.input_tokens}")
```

## WebSocket Connections

For persistent multi-turn conversations with tool calling, use `client.responses.connect()`:

```python
from openai import OpenAI

client = OpenAI()

with client.responses.connect() as connection:
    # Create a response with streaming and forced tool choice
    connection.response.create(
        model="gpt-5.2",
        input="What's the inventory for sku-123?",
        stream=True,
        tools=TOOLS,
        tool_choice={"type": "function", "name": "get_sku_inventory"},
    )

    for event in connection:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
        elif event.type == "response.output_item.done" and event.item.type == "function_call":
            # Handle tool call, compute output, send back
            tool_output = {"type": "function_call_output", "call_id": event.item.call_id, "output": json.dumps(result)}
            # Continue conversation with tool output as input
            connection.response.create(
                model="gpt-5.2",
                input=[tool_output],
                stream=True,
                previous_response_id=event.response.id,
                tools=TOOLS,
                tool_choice="none",
            )
```

For beta WebSocket behavior, pass `extra_headers={"OpenAI-Beta": "responses_websockets=2026-02-06"}`.

See the full multi-turn example with chained `previous_response_id` and tool I/O in the [websocket.py](https://github.com/openai/openai-python/blob/v2.38.0/examples/responses/websocket.py) reference implementation.

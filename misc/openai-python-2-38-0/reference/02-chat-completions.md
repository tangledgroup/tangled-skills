# Chat Completions

## Contents
- Basic Usage
- Streaming
- Structured Outputs (Parse)
- Function Tools
- Streaming with Parse
- Streaming with Tools

## Basic Usage

The Chat Completions API is the legacy standard for generating text, supported indefinitely:

```python
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[
        {"role": "developer", "content": "Talk like a pirate."},
        {"role": "user", "content": "What is 2+2?"},
    ],
)
print(completion.choices[0].message.content)
```

### Response Object

The response is a Pydantic model. Access properties:

```python
print(completion.id)
print(completion.model)
print(completion.choices[0].message.content)
print(completion.usage)  # prompt_tokens, completion_tokens, total_tokens
print(completion._request_id)  # public _request_id for debugging
```

Serialize: `completion.to_json()`, `completion.to_dict()`.

Check if a field is explicitly `null` vs missing:

```python
if response.my_field is None:
    if 'my_field' not in response.model_fields_set:
        print('Field missing from JSON')
    else:
        print('Field is explicitly null')
```

## Streaming

Pass `stream=True` to receive chunks via SSE:

```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "How do I list files in Python?"}],
    stream=True,
)
for chunk in stream:
    if not chunk.choices:
        continue
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

Async:

```python
stream = await client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True,
)
async for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

### Manual Stream Control

```python
stream = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="1,2,3,",
    max_tokens=5,
    temperature=0,
    stream=True,
)
first = next(stream)  # manually get first chunk
print(first.to_json())
for data in stream:   # iterate remaining
    print(data.to_json())
```

## Structured Outputs (Parse)

Use `client.chat.completions.parse()` with a Pydantic model to get typed responses:

```python
from typing import List
from pydantic import BaseModel
from openai import OpenAI

class Step(BaseModel):
    explanation: str
    output: str

class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str

client = OpenAI()
completion = client.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "solve 8x + 31 = 2"},
    ],
    response_format=MathResponse,
)
message = completion.choices[0].message

if message.parsed:
    print(message.parsed.steps)
    print("answer:", message.parsed.final_answer)
else:
    print(message.refusal)
```

## Function Tools

Use `openai.pydantic_function_tool()` to auto-generate tool definitions from Pydantic models:

```python
from enum import Enum
from typing import List, Union
from pydantic import BaseModel
import openai
from openai import OpenAI

class Table(str, Enum):
    orders = "orders"
    customers = "customers"

class Column(str, Enum):
    id = "id"
    status = "status"

class Operator(str, Enum):
    eq = "="
    gt = ">"
    lt = "<"

class Condition(BaseModel):
    column: str
    operator: Operator
    value: Union[str, int]

class Query(BaseModel):
    table_name: Table
    columns: List[Column]
    conditions: List[Condition]

client = OpenAI()
completion = client.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You help users query data."},
        {"role": "user", "content": "look up all my orders in november"},
    ],
    tools=[openai.pydantic_function_tool(Query)],
)

tool_call = (completion.choices[0].message.tool_calls or [])[0]
assert isinstance(tool_call.function.parsed_arguments, Query)
print(tool_call.function.parsed_arguments.table_name)
```

### Manual Tool Definitions

Define tools as dictionaries without Pydantic:

```python
completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "What's the weather in SF?"}],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "unit": {"type": "string", "enum": ["c", "f"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ],
)

# Check for tool calls
if completion.choices[0].message.tool_calls:
    for call in completion.choices[0].message.tool_calls:
        print(call.function.name)
        import json
        args = json.loads(call.function.arguments)
        # Execute the function, then continue the conversation
```

## Streaming with Parse

Use `client.chat.completions.stream()` as a context manager for streaming structured outputs:

```python
with client.chat.completions.stream(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "solve 8x + 31 = 2"},
    ],
    response_format=MathResponse,
) as stream:
    for event in stream:
        if event.type == "content.delta":
            print(event.delta, end="", flush=True)
        elif event.type == "content.done":
            print()
            if event.parsed is not None:
                print(f"answer: {event.parsed.final_answer}")
        elif event.type == "refusal.delta":
            print(event.delta, end="", flush=True)

    print("---")
    print(stream.get_final_completion())
```

## Streaming with Tools

Stream tool calls as they are generated:

```python
from pydantic import BaseModel
import openai
from openai import OpenAI

class GetWeather(BaseModel):
    city: str
    country: str

client = OpenAI()
with client.chat.completions.stream(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "user", "content": "What's the weather in SF and New York?"},
    ],
    tools=[openai.pydantic_function_tool(GetWeather, name="get_weather")],
    parallel_tool_calls=True,
) as stream:
    for event in stream:
        if event.type in ("tool_calls.function.arguments.delta", "tool_calls.function.arguments.done"):
            print(event)

    print(stream.get_final_completion())
```

The `.parse_stream()` returned tool calls are automatically deserialized into the specified Pydantic type.

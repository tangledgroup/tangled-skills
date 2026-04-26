# Chat Completions

The Chat Completions API is the previous standard for generating text, supported indefinitely alongside the Responses API. It uses a `messages` array with role-based conversation turns.

## Basic Usage

```python
from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[
        {"role": "developer", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
)

print(completion.choices[0].message.content)
```

## Message Roles

- `developer` — system-level instructions (replaces the old `system` role)
- `user` — user input
- `assistant` — model responses (include for multi-turn context)
- `tool` — results from function/tool calls

## Function Calling

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City and state"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
    tools=tools,
    tool_choice="auto",  # "auto", "none", or {"type": "function", "function": {"name": "get_current_weather"}}
)

message = completion.choices[0].message
if message.tool_calls:
    for tool_call in message.tool_calls:
        print(tool_call.function.name)
        print(tool_call.function.arguments)
```

### Handling Tool Responses

```python
messages = [
    {"role": "user", "content": "What's the weather in SF?"},
    {"role": "assistant", "content": None, "tool_calls": [
        {
            "id": "call_abc",
            "type": "function",
            "function": {"name": "get_current_weather", "arguments": '{"location": "San Francisco"}'},
        }
    ]},
    {"role": "tool", "tool_call_id": "call_abc", "content": "{\"temperature\": 72, \"unit\": \"fahrenheit\"}"},
]

completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=messages,
    tools=tools,
)
print(completion.choices[0].message.content)
```

## Streaming

```python
stream = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Tell me a joke."}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Logprobs

Request token log probabilities:

```python
completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Hello"}],
    logprobs=True,
    top_logprobs=5,  # top N alternative tokens per position
)

for top in completion.choices[0].logprobs.content[0].top_logprobs:
    print(top.token, top.logprob)
```

## Response Format

```python
# JSON object
completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "List 3 colors in JSON."}],
    response_format={"type": "json_object"},
)

# Text (default)
completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Hello"}],
    response_format={"type": "text"},
)
```

## Vision with Chat Completions

```python
completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is in this image?"},
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/image.jpg", "detail": "auto"},
                },
            ],
        }
    ],
)
```

## Reasoning Effort

```python
completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Solve this complex problem..."}],
    reasoning_effort="high",  # "low", "medium", "high"
)
```

## Managed Foreground

For extended operations, use `managed_foreground`:

```python
completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Research this topic thoroughly..."}],
    managed_foreground={"type": "default"},
)
```

## Usage

```python
completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Hello"}],
)

print(completion.usage.prompt_tokens)
print(completion.usage.completion_tokens)
print(completion.usage.total_tokens)
```

## Retrieval and Management

```python
# Retrieve a completion by ID
completion = client.chat.completions.retrieve("completion_abc123")

# List completions (paginated)
for c in client.chat.completions.list(limit=20):
    print(c.id)

# Update metadata
updated = client.chat.completions.update(
    "completion_abc123",
    metadata={"key": "value"},
)

# Delete a completion
deleted = client.chat.completions.delete("completion_abc123")

# List messages for a stored completion
messages = client.chat.completions.messages.list("completion_abc123")
```

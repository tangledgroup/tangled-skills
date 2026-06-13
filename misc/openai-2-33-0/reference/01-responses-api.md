# Responses API

The Responses API is the primary interface for generating text from OpenAI models. It replaces the Chat Completions API as the recommended approach, though Chat Completions remains supported indefinitely.

## Basic Usage

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.2",
    instructions="You are a helpful coding assistant.",
    input="How do I read a CSV file in Python?",
)

print(response.output_text)
```

## Multi-Turn Conversations

Pass an array of message objects for conversation history:

```python
response = client.responses.create(
    model="gpt-5.2",
    instructions="You are a tutor.",
    input=[
        {"role": "user", "content": "What is recursion?"},
        {"role": "assistant", "content": "Recursion is when a function calls itself..."},
        {"role": "user", "content": "Can you show an example in Python?"},
    ],
)
```

## Structured Output (JSON Schema)

Force the model to return JSON matching a specific schema:

```python
response = client.responses.create(
    model="gpt-5.2",
    input="Extract the name, age, and city from: 'John is 30, lives in NYC'",
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "person_info",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "city": {"type": "string"},
                },
                "required": ["name", "age", "city"],
            },
        },
    },
)
```

Other response formats: `{"type": "json_object"}` for free-form JSON, `{"type": "text"}` (default).

## Function Calling

Define tools the model can call:

```python
response = client.responses.create(
    model="gpt-5.2",
    input="What's the weather in Tokyo?",
    tools=[
        {
            "type": "function",
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                },
                "required": ["city"],
            },
        }
    ],
)

# Check for function calls in output
for item in response.output:
    if hasattr(item, "type") and item.type == "function_call":
        print(item.call_id, item.name, item.arguments)
```

## Streaming

```python
stream = client.responses.create(
    model="gpt-5.2",
    input="Write a short story about a robot.",
    stream=True,
)

for event in stream:
    # Events include text deltas, function calls, usage updates, etc.
    if hasattr(event, "type") and "text.delta" in event.type:
        print(event.delta, end="", flush=True)
```

Async streaming uses `async for`:

```python
async for event in stream:
    print(event)
```

## Vision

Pass images alongside text input:

```python
# From URL
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

# From base64
import base64
with open("photo.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

response = client.responses.create(
    model="gpt-5.2",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Describe this image."},
                {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"},
            ],
        }
    ],
)
```

## Temperature and Top P

Control randomness:

```python
response = client.responses.create(
    model="gpt-5.2",
    input="Write a creative haiku.",
    temperature=0.8,   # 0.0-2.0, higher = more creative
    top_p=0.95,        # 0.0-1.0, nucleus sampling
)
```

## Max Output Tokens

Limit response length:

```python
response = client.responses.create(
    model="gpt-5.2",
    input="Summarize this document...",
    max_output_tokens=500,
)
```

## Reasoning Effort

For models that support extended reasoning:

```python
response = client.responses.create(
    model="gpt-5.2",
    input="Solve this complex math problem...",
    reasoning={"effort": "high"},  # "low", "medium", "high"
)
```

## Parallel Function Calls

Enable multiple function calls in a single response:

```python
response = client.responses.create(
    model="gpt-5.2",
    input="What's the weather in NYC, London, and Tokyo?",
    tools=[weather_tool],
    parallel_tool_calls=True,
)
```

## Usage Metadata

Access token usage from the response:

```python
response = client.responses.create(
    model="gpt-5.2",
    input="Hello",
)

print(response.usage.input_tokens)
print(response.usage.output_tokens)
print(response.usage.total_tokens)
```

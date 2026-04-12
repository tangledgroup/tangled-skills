# Responses API and Chat Completions

Comprehensive guide to text generation with OpenAI models using both the new Responses API (recommended) and the traditional Chat Completions API.

## Responses API

The Responses API is the primary interface for interacting with OpenAI models. It provides a unified, simplified approach to generating responses.

### Basic Usage

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

### Request Parameters

#### Core Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | str | Yes | Model ID (e.g., "gpt-5.2", "gpt-4o", "o3") |
| `input` | str \| list | Yes | Text, image, or file inputs to generate response from |
| `instructions` | str | No | System/developer message inserted into model's context |
| `stream` | bool | No | Stream response using server-sent events |

#### Control Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `temperature` | float | 1.0 | Sampling temperature (0-2). Higher = more random |
| `top_p` | float | 1.0 | Nucleus sampling (0-1). Alternative to temperature |
| `max_output_tokens` | int | - | Upper bound on generated tokens (including reasoning) |
| `top_logprobs` | int | 0 | Top N log probabilities per token (0-20) |

#### Advanced Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | ResponseTextConfigParam | Text response config (plain text or JSON) |
| `tools` | Iterable[ToolParam] | Tools model may call (built-in, MCP, custom functions) |
| `tool_choice` | ToolChoice | How model selects which tools to use |
| `parallel_tool_calls` | bool | Allow parallel tool execution |
| `max_tool_calls` | int | Max total built-in tool calls per response |
| `previous_response_id` | str | ID of previous response for multi-turn conversations |
| `conversation` | str \| ConversationParam | Conversation context (alternative to previous_response_id) |
| `store` | bool | Store response for later retrieval |
| `metadata` | dict | Up to 16 key-value pairs for organization |

#### Safety and Caching

| Parameter | Type | Description |
|-----------|------|-------------|
| `safety_identifier` | str | Stable user identifier for abuse detection (max 64 chars) |
| `prompt_cache_key` | str | Cache key for similar requests (replaces deprecated `user`) |
| `prompt_cache_retention` | "in-memory" \| "24h" | Extended prompt caching retention policy |
| `service_tier` | "auto" \| "default" \| "flex" \| "scale" \| "priority" | Processing tier for request |

#### Reasoning Models (gpt-5, o-series)

| Parameter | Type | Description |
|-----------|------|-------------|
| `reasoning` | Reasoning | Configuration for reasoning models |

#### Truncation and Context

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `truncation` | "auto" \| "disabled" | "disabled" | How to handle context window overflow |
| `context_management` | Iterable[ContextManagement] | - | Context compaction configuration |

#### Background Processing

| Parameter | Type | Description |
|-----------|------|-------------|
| `background` | bool | Run response generation in background |

#### Include Additional Data

| Parameter | Type | Description |
|-----------|------|-------------|
| `include` | List[ResponseIncludable] | Extra output data to include (sources, logprobs, etc.) |

### Streaming Responses

Stream tokens as they're generated for real-time applications:

```python
from openai import OpenAI

client = OpenAI()

stream = client.responses.create(
    model="gpt-5.2",
    input="Write a one-sentence bedtime story about a unicorn.",
    stream=True,
)

for event in stream:
    print(event)
```

**Async streaming:**

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main():
    stream = await client.responses.create(
        model="gpt-5.2",
        input="Write a poem about Python.",
        stream=True,
    )
    
    async for event in stream:
        print(event)

asyncio.run(main())
```

### Vision (Image Input)

**With image URL:**

```python
prompt = "What is in this image?"
img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/2023_06_08_Raccoon1.jpg/1599px-2023_06_08_Raccoon1.jpg"

response = client.responses.create(
    model="gpt-5.2",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": img_url},
            ],
        }
    ],
)

print(response.output_text)
```

**With base64-encoded image:**

```python
import base64
from openai import OpenAI

client = OpenAI()

prompt = "What is in this image?"
with open("image.png", "rb") as image_file:
    b64_image = base64.b64encode(image_file.read()).decode("utf-8")

response = client.responses.create(
    model="gpt-5.2",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:image/png;base64,{b64_image}"},
            ],
        }
    ],
)

print(response.output_text)
```

### Multi-turn Conversations

Use `previous_response_id` to maintain conversation state:

```python
from openai import OpenAI

client = OpenAI()

# First turn
response1 = client.responses.create(
    model="gpt-5.2",
    instructions="You are a helpful assistant.",
    input="What is the capital of France?",
)

print(response1.output_text)  # "Paris"

# Second turn - reference previous response
response2 = client.responses.create(
    model="gpt-5.2",
    instructions="You are a helpful assistant.",
    input="What is its population?",
    previous_response_id=response1.id,  # Maintains conversation context
)

print(response2.output_text)  # Will know "its" refers to Paris
```

### Using Conversation Context

Alternative approach using `conversation` parameter:

```python
from openai import OpenAI

client = OpenAI()

# Create or reference a conversation
conversation_id = "conv_abc123"

response = client.responses.create(
    model="gpt-5.2",
    conversation=conversation_id,
    input="Tell me about Python programming.",
)

# Items are automatically added to the conversation
# Next request will include previous context
response2 = client.responses.create(
    model="gpt-5.2",
    conversation=conversation_id,
    input="What about async programming?",
)
```

### Structured Outputs (JSON Mode)

Force the model to return valid JSON:

```python
from openai import OpenAI
import json

client = OpenAI()

response = client.responses.create(
    model="gpt-5.2",
    input="Extract the person's name and age from: 'My name is Alice and I am 30.'",
    text={
        "format": {
            "type": "json_schema",
            "name": "person_info",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "age"],
                "additionalProperties": False
            }
        }
    },
)

# Parse the structured output
data = json.loads(response.output_text)
print(data)  # {"name": "Alice", "age": 30}
```

### Tool Use with Responses API

#### Built-in Tools (Web Search, File Search)

```python
from openai import OpenAI

client = OpenAI()

# Enable web search tool
response = client.responses.create(
    model="gpt-5.2",
    input="What is the current weather in Tokyo?",
    tools=[
        {"type": "web_search_preview", "search_context_size": "low"}
    ],
)

print(response.output_text)
```

#### Custom Function Tools

```python
from openai import OpenAI
import json

client = OpenAI()

# Define custom tools
tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["location"]
        },
        "strict": True
    }
]

# Request with tool choice
response = client.responses.create(
    model="gpt-5.2",
    input="What's the weather in Boston?",
    tools=tools,
    tool_choice={"type": "function", "name": "get_weather"},
)

# Check if tool was called
for output in response.output:
    if output.type == "function_call":
        print(f"Function: {output.name}")
        print(f"Arguments: {output.arguments}")
```

#### MCP (Model Context Protocol) Tools

```python
from openai import OpenAI

client = OpenAI()

# Connect to MCP server for third-party integrations
response = client.responses.create(
    model="gpt-5.2",
    input="Search my Google Drive for the project document",
    tools=[
        {
            "type": "mcp",
            "server_label": "google-drive",
            "tools": ["search", "read_file"]
        }
    ],
)
```

### Service Tiers

Control processing priority and cost:

```python
from openai import OpenAI

client = OpenAI()

# Use flex processing for cost savings (slower)
response = client.responses.create(
    model="gpt-5.2",
    input="Analyze this complex dataset...",
    service_tier="flex",  # auto, default, flex, scale, priority
)

# Check which tier was actually used
print(response.service_tier)  # May differ from requested
```

**Service Tiers:**
- `auto` - Use project default setting
- `default` - Standard pricing and performance
- `flex` - Flex processing (cost savings, variable latency)
- `scale` - Scale processing for large workloads
- `priority` - Priority processing (lowest latency, higher cost)

### Prompt Caching

Optimize costs with prompt caching:

```python
from openai import OpenAI

client = OpenAI()

# Use prompt cache key for similar requests
response = client.responses.create(
    model="gpt-5.2",
    input="Translate to French: Hello, how are you?",
    prompt_cache_key="user_123_translation_request",  # Stable identifier
    prompt_cache_retention="24h",  # Keep cache for 24 hours
)

# Check cache stats
print(response.usage.cache_creation_input_tokens)  # Tokens added to cache
print(response.usage.cache_read_input_tokens)  # Tokens read from cache
```

### Reasoning Models (gpt-5, o-series)

Configure reasoning capabilities:

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="o3",
    input="Solve this complex mathematical problem...",
    reasoning={
        "effort": "high",  # low, medium, high
        "summary": "detailed"  # none, detailed, auto
    },
)

# Access reasoning content
for output in response.output:
    if output.type == "reasoning":
        print(f"Reasoning: {output.summary}")
```

### Background Processing

Run responses asynchronously:

```python
from openai import OpenAI

client = OpenAI()

# Start background processing
response = client.responses.create(
    model="gpt-5.2",
    input="Generate a comprehensive analysis...",
    background=True,  # Process in background
)

# Response will have status indicating background processing
print(response.status)  # "in_progress" or similar

# Poll for completion if needed
```

### Including Additional Data

Request extra output information:

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.2",
    input="Search for recent AI developments",
    tools=[{"type": "web_search_preview"}],
    include=[
        "web_search_call.action.sources",  # Include search sources
        "message.output_text.logprobs",    # Include log probabilities
        "code_interpreter_call.outputs",   # Include code outputs
        "file_search_call.results",        # Include file search results
        "reasoning.encrypted_content",     # Include encrypted reasoning
    ],
)

# Access included data
for output in response.output:
    if hasattr(output, 'sources'):
        print(f"Sources: {output.sources}")
```

### Context Management

Manage long conversations with compaction:

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.2",
    input="Continue our conversation...",
    previous_response_id="resp_prev123",
    context_management=[
        {
            "type": "compaction",
            "compact_threshold": 10000  # Compact when tokens exceed threshold
        }
    ],
    truncation="auto",  # Auto-truncate if needed
)
```

### Safety Identifiers

Implement abuse detection:

```python
from openai import OpenAI
import hashlib

client = OpenAI()

# Create stable user identifier (hash email/username)
user_email = "user@example.com"
safety_id = hashlib.sha256(user_email.encode()).hexdigest()[:64]

response = client.responses.create(
    model="gpt-5.2",
    input="User request here",
    safety_identifier=safety_id,  # For abuse detection
)
```

## Chat Completions API

The traditional chat interface, supported indefinitely. Use this for existing applications or when specific chat features are needed.

The traditional chat interface, supported indefinitely. Use this for existing applications or when specific chat features are needed.

### Basic Usage

```python
from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is quantum computing?"},
    ],
)

print(completion.choices[0].message.content)
```

### Message Roles

- **system**: Sets model behavior and personality (optional but recommended)
- **user**: User input or questions
- **assistant**: Model's previous responses
- **developer**: Alternative to system role for instructions

### Multi-turn Conversations

```python
from openai import OpenAI

client = OpenAI()

messages = [
    {"role": "system", "content": "You are a math tutor."},
    {"role": "user", "content": "What is the quadratic formula?"},
]

# First response
response1 = client.chat.completions.create(
    model="gpt-5.2",
    messages=messages,
)

messages.append(response1.choices[0].message)

# Follow-up question
messages.append({"role": "user", "content": "Can you give me an example?"})

response2 = client.chat.completions.create(
    model="gpt-5.2",
    messages=messages,
)

print(response2.choices[0].message.content)
```

### Streaming Chat Completions

```python
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Tell me a joke."}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Function Calling (Tool Use)

Define functions the model can call:

```python
from openai import OpenAI

client = OpenAI()

# Define available functions
functions = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    }
]

response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[
        {"role": "user", "content": "What's the weather in Boston?"}
    ],
    functions=functions,
)

# Check if model wants to call a function
message = response.choices[0].message
if message.function_call:
    # Extract function name and arguments
    func_name = message.function_call.name
    func_args = json.loads(message.function_call.arguments)
    
    # Execute the function
    if func_name == "get_weather":
        result = get_weather(location=func_args["location"], unit=func_args.get("unit", "fahrenheit"))
    
    # Send result back to model
    messages = [
        {"role": "user", "content": "What's the weather in Boston?"},
        message,
        {"role": "function", "name": func_name, "content": str(result)}
    ]
    
    final_response = client.chat.completions.create(
        model="gpt-5.2",
        messages=messages,
        functions=functions,
    )
    
    print(final_response.choices[0].message.content)
else:
    print(message.content)
```

### Structured Outputs (JSON Mode)

Force the model to return valid JSON:

```python
from openai import OpenAI
import json

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[
        {"role": "system", "content": "Extract the person's name and age."},
        {"role": "user", "content": "My name is Alice and I am 30 years old."}
    ],
    response_format={"type": "json_object"},
)

data = json.loads(response.choices[0].message.content)
print(data)  # {"name": "Alice", "age": 30}
```

### Temperature and Sampling

Control creativity and determinism:

```python
# Deterministic (low temperature)
response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    temperature=0.0,  # Most deterministic
)

# Creative (high temperature)
response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Write a haiku about cats."}],
    temperature=1.0,  # More creative
)

# Use top_p for nucleus sampling
response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Explain machine learning."}],
    temperature=0.7,
    top_p=0.9,  # Consider top 90% of probability mass
)
```

### Multiple Completions

Generate multiple variations:

```python
response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Give me a tagline for a coffee shop."}],
    n=3,  # Generate 3 variations
)

for choice in response.choices:
    print(choice.message.content)
```

### Logprobs

Get token probabilities for analysis:

```python
response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "The capital of France is"}],
    logprobs=True,
    top_logprobs=5,  # Top 5 alternatives per position
)

choice = response.choices[0]
for logprob in choice.logprobs.content:
    print(f"Token: {logprob.token}, Prob: {logprob.logprob}")
```

### Stop Sequences

Custom stop tokens:

```python
response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "List fruits:"}],
    stop=["\n\n", "END"],  # Stop at double newline or "END"
)

print(response.choices[0].message.content)
```

## Model Selection

### Available Models

| Model | Use Case | Context Window |
|-------|----------|----------------|
| `gpt-5.2` | Latest, most capable | 128K tokens |
| `gpt-4o` | High performance, vision | 128K tokens |
| `gpt-4o-mini` | Cost-effective, fast | 128K tokens |
| `gpt-3.5-turbo` | Legacy, basic tasks | 16K tokens |

### Listing Models

```python
from openai import OpenAI

client = OpenAI()

models = client.models.list()
for model in models:
    print(model.id, model.owned_by)
```

## Response Objects

### Responses API Response

```python
response = client.responses.create(
    model="gpt-5.2",
    input="What is Python?",
)

# Access response text
print(response.output_text)

# Access metadata
print(response.id)           # Response ID
print(response.model)        # Model used
print(response._request_id)  # Request ID for debugging

# Convert to dict or JSON
print(response.to_dict())
print(response.to_json())
```

### Chat Completion Response

```python
completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Hello"}],
)

# Access choices
print(completion.choices[0].message.content)
print(completion.choices[0].message.role)

# Access usage information
print(completion.usage.prompt_tokens)
print(completion.usage.completion_tokens)
print(completion.usage.total_tokens)

# Access request ID
print(completion._request_id)
```

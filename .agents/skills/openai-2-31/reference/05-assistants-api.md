# Assistants API

Comprehensive guide to building stateful AI assistants with tool use, file search, code interpreter, and multi-turn conversations using the Assistants API.

## Overview

The Assistants API is a stateful evolution of Chat Completions that simplifies creating assistant-like experiences with built-in support for:

- **Code Interpreter** - Execute Python code in a sandboxed environment
- **File Search** - RAG (retrieval-augmented generation) with uploaded files
- **Function Calling** - Custom tool integration
- **Stateful Threads** - Persistent conversation history
- **Multi-step Tool Use** - Automatic tool execution chains

## Core Concepts

### Assistants

An Assistant encapsulates:
- Base model (e.g., gpt-4o)
- Instructions/system prompt
- Tools (Code Interpreter, File Search, custom functions)
- Associated files for context

### Threads

A Thread represents a conversation state:
- Contains messages between user and assistant
- Independent from Assistants (one thread, multiple assistants)
- Persistent across runs

### Runs

A Run executes an Assistant on a Thread:
- Triggers the assistant to process messages
- May involve multiple tool calls
- Has lifecycle states (queued, in_progress, completed, etc.)

## Basic Usage

### Creating an Assistant

```python
from openai import OpenAI

client = OpenAI()

assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Answer questions briefly, in a sentence or less.",
    model="gpt-4o",
)

print(f"Assistant ID: {assistant.id}")
```

### Assistant Configuration Options

```python
assistant = client.beta.assistants.create(
    name="Research Assistant",
    instructions="""You are a research assistant that helps users find and analyze information.
    Use the provided files to answer questions accurately.""",
    model="gpt-4o",
    tools=[
        {"type": "code_interpreter"},
        {"type": "file_search"},
    ],
    tool_resources={
        "file_search": {
            "vector_stores": [
                {"id": "vs_123"}  # Reference existing vector store
            ]
        }
    },
    temperature=0.7,
    top_p=1.0,
    response_format="auto",  # auto or json_object
    metadata={
        "department": "research",
        "version": "1.0"
    },
)
```

### Available Tools

| Tool | Description |
|------|-------------|
| `code_interpreter` | Execute Python code in sandbox |
| `file_search` | RAG with uploaded files |
| `function` | Custom function definitions |

### Creating a Thread

```python
from openai import OpenAI

client = OpenAI()

# Create empty thread
thread = client.beta.threads.create()
print(f"Thread ID: {thread.id}")

# Create thread with initial message
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "I need help solving this equation: 3x + 11 = 14",
        }
    ]
)
```

### Adding Messages to a Thread

```python
# Add text message
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="What is the capital of France?",
)

# Add message with file reference
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Analyze this document",
    attachments=[
        {
            "file_id": "file-abc123",
            "tools": [{"type": "file_search"}],
        }
    ],
)

# Add image message
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=[
        {"type": "input_text", "text": "What's in this image?"},
        {
            "type": "image_file",
            "image_file": {"file_id": "file-img123"},
        },
    ],
)
```

### Creating a Run

```python
# Create run (async operation)
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

print(f"Run ID: {run.id}")
print(f"Status: {run.status}")  # Initially "queued"
```

### Run Configuration

```python
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Override: Answer in Spanish",  # Override assistant instructions
    additional_instructions="Be very concise",   # Append to instructions
    additional_messages=[                        # Add messages before running
        {"role": "user", "content": "Extra context"}
    ],
    tools=[{"type": "code_interpreter"}],        # Override tools
    temperature=0.5,                             # Override temperature
    max_completion_tokens=1000,                  # Limit output tokens
    truncation_strategy={                        # Handle context window limits
        "type": "auto",
        "last_messages": 10,
    },
)
```

### Polling for Run Completion

```python
import time

def wait_on_run(run, thread_id):
    """Poll run until completion."""
    while run.status in ["queued", "in_progress"]:
        time.sleep(1.0)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        print(f"Status: {run.status}")
    
    return run

# Usage
run = wait_on_run(run, thread.id)
print(f"Final status: {run.status}")
```

### Retrieving Messages

```python
# Get all messages in thread (reverse chronological)
messages = client.beta.threads.messages.list(
    thread_id=thread.id,
    order="desc",
)

for message in messages:
    print(f"{message.role}: {message.content[0].text.value}")

# Get specific message
message = client.beta.threads.messages.retrieve(
    thread_id=thread.id,
    message_id=message.id,
)
```

### Complete Example

```python
from openai import OpenAI
import time

client = OpenAI()

# 1. Create assistant
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Answer questions briefly.",
    model="gpt-4o",
)

# 2. Create thread with message
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "I need to solve the equation 3x + 11 = 14. Can you help me?",
        }
    ]
)

# 3. Create run
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

# 4. Wait for completion
while run.status in ["queued", "in_progress"]:
    time.sleep(1.0)
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id,
    )

# 5. Get response messages
messages = client.beta.threads.messages.list(
    thread_id=thread.id,
    order="desc",
)

for message in messages:
    if message.role == "assistant" and message.content:
        print(message.content[0].text.value)
```

## Streaming Runs

Stream run events in real-time:

```python
from openai import OpenAI

client = OpenAI()

stream = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    stream=True,
)

for event in stream:
    print(f"{event.event}: {event.data.id if hasattr(event.data, 'id') else ''}")
    
    # Handle different event types
    if event.event == "thread.run.completed":
        print("Run completed!")
    elif event.event == "thread.message.created":
        print("New message created")
    elif event.event == "thread.message.delta":
        # Stream message content as it's generated
        if hasattr(event.delta, 'content') and event.delta.content:
            print(event.delta.content[0].text.value, end="", flush=True)
```

## Code Interpreter Tool

Execute Python code in a sandboxed environment:

```python
# Create assistant with code interpreter
assistant = client.beta.assistants.create(
    name="Data Analyst",
    instructions="You are a data analyst. Use code interpreter to analyze data.",
    model="gpt-4o",
    tools=[{"type": "code_interpreter"}],
)

# Upload file for analysis
file = client.files.create(
    file=open("sales_data.csv", "rb"),
    purpose="assistants",
)

# Create thread with file attachment
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "Analyze this sales data and create a chart",
            "attachments": [
                {
                    "file_id": file.id,
                    "tools": [{"type": "code_interpreter"}],
                }
            ],
        }
    ]
)

# Run assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

# Wait and retrieve results
while run.status in ["queued", "in_progress"]:
    time.sleep(1.0)
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id,
    )

# Get messages (including code output/images)
messages = client.beta.threads.messages.list(thread_id=thread.id)
```

## File Search Tool (RAG)

### Creating a Vector Store

```python
from openai import OpenAI

client = OpenAI()

# Upload files
file1 = client.files.create(
    file=open("document1.pdf", "rb"),
    purpose="assistants",
)

file2 = client.files.create(
    file=open("document2.pdf", "rb"),
    purpose="assistants",
)

# Create vector store with files
vector_store = client.beta.vector_stores.create(
    name="product_docs",
    file_ids=[file1.id, file2.id],
)

print(f"Vector Store ID: {vector_store.id}")
```

### Vector Store Operations

```python
# Retrieve vector store
vector_store = client.beta.vector_stores.retrieve(
    vector_store_id="vs_123",
)

# Add files to existing vector store
client.beta.vector_stores.file_ids.create(
    vector_store_id="vs_123",
    file_ids=["file-abc", "file-def"],
)

# List files in vector store
files = client.beta.vector_stores.files.list(
    vector_store_id="vs_123",
)

# Delete file from vector store
client.beta.vector_stores.files.delete(
    vector_store_id="vs_123",
    file_id="file-abc",
)

# Delete vector store
client.beta.vector_stores.delete(vector_store_id="vs_123")
```

### Using File Search in Assistant

```python
assistant = client.beta.assistants.create(
    name="Product Expert",
    instructions="Answer questions about our products using the provided documentation.",
    model="gpt-4o",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_stores": [{"id": "vs_123"}]
        }
    },
)

# Create thread and run
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "What are the specifications of product X?",
        }
    ]
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
)
```

## Custom Function Tools

Define custom functions for the assistant to call:

```python
from openai import OpenAI
import json

client = OpenAI()

# Define function schema
functions = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g. San Francisco",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit",
                    },
                },
                "required": ["location"],
            },
        },
    }
]

# Create assistant with function tool
assistant = client.beta.assistants.create(
    name="Weather Assistant",
    instructions="Help users get weather information.",
    model="gpt-4o",
    tools=functions,
)

# Implement function
def get_weather(location: str, unit: str = "fahrenheit") -> dict:
    """Actual implementation of the weather function."""
    # Call real weather API or return mock data
    return {
        "location": location,
        "temperature": 72 if unit == "fahrenheit" else 22,
        "unit": unit,
        "condition": "sunny",
    }

# Create thread and run
thread = client.beta.threads.create(
    messages=[
        {"role": "user", "content": "What's the weather in Boston?"}
    ]
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

# Handle required action (function calling)
while run.status == "requires_action":
    required = run.required_action
    
    # Extract function calls
    for tool_call in required.submit_tool_outputs.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # Execute function
        if function_name == "get_weather":
            result = get_weather(
                location=arguments["location"],
                unit=arguments.get("unit", "fahrenheit"),
            )
        
        # Submit tool outputs
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=[
                {
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(result),
                }
            ],
        )
    
    # Wait for completion
    while run.status in ["queued", "in_progress"]:
        time.sleep(1.0)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )

# Get final response
messages = client.beta.threads.messages.list(thread_id=thread.id)
```

## Run Steps

Inspect detailed execution steps:

```python
# List run steps
steps = client.beta.threads.runs.steps.list(
    thread_id=thread.id,
    run_id=run.id,
)

for step in steps:
    print(f"Step {step.id}: {step.type} - {step.status}")
    
    # Get step details
    step_details = client.beta.threads.runs.steps.retrieve(
        thread_id=thread.id,
        run_id=run.id,
        step_id=step.id,
    )
    
    if step.step_details.type == "tool_calls":
        for tool_call in step_details.step_details.tool_calls:
            print(f"  Tool: {tool_call.function.name}")
```

## Thread Management

### Deleting Threads

```python
client.beta.threads.delete(thread_id=thread.id)
```

### Modifying Messages

```python
# Update message metadata
message = client.beta.threads.messages.update(
    thread_id=thread.id,
    message_id=message.id,
    metadata={"processed": "true"},
)

# Delete message
client.beta.threads.messages.delete(
    thread_id=thread.id,
    message_id=message.id,
)
```

## Best Practices

1. **Choose the right tools:** Only enable tools you actually need
2. **Set appropriate timeouts:** Runs expire after 5 minutes by default
3. **Handle errors gracefully:** Check run status and last_error
4. **Manage context window:** Use truncation_strategy for long conversations
5. **Stream when possible:** Better UX for users
6. **Cache vector stores:** Reuse across assistants to save costs
7. **Monitor token usage:** Check run.usage for cost tracking

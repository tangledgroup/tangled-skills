# Assistants API

The Assistants API (available under `client.beta`) enables building multi-turn conversational agents with persistent threads, tool use, file search, and code interpretation.

## Core Objects

- **Assistant** — defines instructions, model, tools, and file references
- **Thread** — a conversation session between an assistant and a user
- **Message** — individual messages within a thread
- **Run** — execution of an assistant on a thread
- **Run Step** — granular steps within a run (tool calls, message creation)

## Creating an Assistant

```python
from openai import OpenAI

client = OpenAI()

assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a patient math tutor. Help students understand concepts step by step.",
    model="gpt-5.2",
    tools=[
        {"type": "code_interpreter"},
        {
            "type": "file_search",
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_distance",
                "description": "Calculate distance between two points",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "x1": {"type": "number"},
                        "y1": {"type": "number"},
                        "x2": {"type": "number"},
                        "y2": {"type": "number"},
                    },
                    "required": ["x1", "y1", "x2", "y2"],
                },
            },
        },
    ],
)
```

## Thread and Message Management

```python
# Create a thread
thread = client.beta.threads.create()

# Add a message
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="What is the Pythagorean theorem?",
)

# List messages
messages = client.beta.threads.messages.list(thread_id=thread.id)
```

## Running an Assistant

### Polling (Simplest)

```python
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

if run.status == "completed":
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for msg in messages:
        if msg.role == "assistant":
            print(msg.content[0].text.value)
```

### Streaming

```python
from openai.lib.streaming import AssistantEventHandler

class MyEventHandler(AssistantEventHandler):
    def on_text_created(self, text):
        print("\nAssistant: ", end="", flush=True)

    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

with client.beta.threads.runs.create_and_stream(
    thread_id=thread.id,
    assistant_id=assistant.id,
    event_handler=MyEventHandler(),
) as stream:
    stream.until_done()
```

## Function Calling with Assistants

When the assistant calls a function, the run status becomes `requires_action`:

```python
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

if run.status == "requires_action":
    tool_outputs = []
    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
        if tool_call.function.name == "calculate_distance":
            import json
            args = json.loads(tool_call.function.arguments)
            result = ((args["x2"]-args["x1"])**2 + (args["y2"]-args["y1"])**2)**0.5
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": str(result),
            })

    # Submit results and continue
    run = client.beta.threads.runs.submit_tool_outputs_and_poll(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=tool_outputs,
    )
```

## Run Steps

Inspect individual steps of a run:

```python
steps = client.beta.threads.runs.steps.list(
    thread_id=thread.id,
    run_id=run.id,
)

for step in steps:
    if step.type == "tool_calls":
        for tool_call in step.step_details.tool_calls:
            if tool_call.type == "code_interpreter":
                print("Code executed:", tool_call.code_interpreter.input)
            elif tool_call.type == "file_search":
                print("File search performed")
```

## Code Interpreter

Enable code execution within the assistant:

```python
assistant = client.beta.assistants.create(
    name="Data Analyst",
    model="gpt-5.2",
    tools=[{"type": "code_interpreter"}],
)

# Upload files for the code interpreter to use
file = client.files.create(
    file=open("data.csv", "rb"),
    purpose="assistants",
)

# Attach file to thread
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Analyze this dataset",
    attachments=[
        {
            "file_id": file.id,
            "tools": [{"type": "code_interpreter"}],
        }
    ],
)
```

## File Search

Enable RAG-like file search:

```python
assistant = client.beta.assistants.create(
    name="Research Assistant",
    model="gpt-5.2",
    tools=[{"type": "file_search"}],
)

# Upload and attach files
file = client.files.create(
    file=open("research_paper.pdf", "rb"),
    purpose="assistants",
)

client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="What are the key findings?",
    attachments=[
        {
            "file_id": file.id,
            "tools": [{"type": "file_search"}],
        }
    ],
)
```

## Managing Assistants

```python
# List assistants
assistants = client.beta.assistants.list(limit=20)

# Retrieve
assistant = client.beta.assistants.retrieve("asst_abc123")

# Update
updated = client.beta.assistants.update(
    "asst_abc123",
    instructions="Updated instructions here.",
)

# Delete
deleted = client.beta.assistants.delete("asst_abc123")
```

## Managing Threads

```python
# Create with initial messages
thread = client.beta.threads.create(
    messages=[
        {"role": "user", "content": "Hello!"},
    ],
)

# Retrieve
thread = client.beta.threads.retrieve("thread_abc123")

# Update metadata
updated = client.beta.threads.update(
    "thread_abc123",
    metadata={"key": "value"},
)

# Delete
deleted = client.beta.threads.delete("thread_abc123")
```

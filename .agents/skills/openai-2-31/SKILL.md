---
name: openai-2-31
description: Python SDK for OpenAI API v2.31 providing type-safe access to Responses API, Chat Completions, embeddings, audio transcription/synthesis, image generation, assistants, fine-tuning, and batch operations with sync/async clients. Use when building Python applications that integrate with OpenAI models for text generation, vision, audio processing, or automated assistants.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - openai
  - python
  - llm
  - chat-completions
  - embeddings
  - assistants
  - fine-tuning
  - audio
  - vision
category: development
required_environment_variables:
  - name: OPENAI_API_KEY
    prompt: "Please provide your OpenAI API key"
    help: "Get your API key from https://platform.openai.com/settings/organization/api-keys"
    required_for: "full functionality"
  - name: OPENAI_WEBHOOK_SECRET
    prompt: "Provide your OpenAI webhook secret (optional)"
    help: "Required for webhook signature verification, get from OpenAI platform settings"
    required_for: "webhook verification"
---

# OpenAI Python SDK v2.31

Comprehensive toolkit for the OpenAI Python library (v2.31+) providing type-safe access to all OpenAI API endpoints including the new Responses API, Chat Completions, embeddings, audio processing, image generation, Assistants API, fine-tuning, and batch operations. Supports both synchronous and asynchronous clients with full type definitions powered by Pydantic and httpx.

## When to Use

- Building Python applications that generate text with GPT models (Responses API or Chat Completions)
- Creating conversational AI assistants with stateful threads and tool use
- Processing audio (speech-to-text transcription, text-to-speech synthesis)
- Generating images with DALL-E 3 or GPT-Image models
- Computing embeddings for semantic search, clustering, or classification
- Fine-tuning models on custom datasets
- Processing large batches of requests cost-effectively
- Building real-time voice conversations with the Realtime API
- Using vision capabilities to analyze images and videos

## Setup

### Installation

```bash
# Basic installation
pip install openai

# With aiohttp support for improved async concurrency
pip install openai[aiohttp]

# Verify installation
python -c "import openai; print(openai.__version__)"
```

**Requirements:** Python 3.9 or higher

### Authentication

Set your API key as an environment variable (recommended):

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

Or use python-dotenv with a `.env` file:

```bash
# .env file
OPENAI_API_KEY=sk-your-api-key-here

# Install and load
pip install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv()
```

### Client Initialization

**Synchronous client:**

```python
from openai import OpenAI

client = OpenAI(
    # api_key is automatically loaded from OPENAI_API_KEY env var
    # Can also specify explicitly: api_key="sk-..."
)
```

**Asynchronous client:**

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()
```

See [Client Configuration](references/02-client-config.md) for advanced options including timeouts, retries, proxies, and workload identity authentication.

## Quick Start

### Responses API (Recommended)

The Responses API is the primary, unified interface for all OpenAI models with support for:
- Multi-turn conversations with state management
- Built-in tools (web search, file search)
- Custom function calling and MCP integrations
- Structured JSON outputs with schema validation
- Reasoning models (gpt-5, o-series)
- Prompt caching and service tiers
- Background processing

```python
from openai import OpenAI

client = OpenAI()

# Basic usage
response = client.responses.create(
    model="gpt-5.2",
    instructions="You are a helpful coding assistant.",
    input="How do I read a CSV file in Python?",
)

print(response.output_text)

# Multi-turn conversation
response2 = client.responses.create(
    model="gpt-5.2",
    input="Can you show me an example with pandas?",
    previous_response_id=response.id,  # Maintains context
)

# With tools
response3 = client.responses.create(
    model="gpt-5.2",
    input="What's the latest news about AI?",
    tools=[{"type": "web_search_preview"}],
)

# Structured JSON output
response4 = client.responses.create(
    model="gpt-5.2",
    input="Extract data from this text...",
    text={"format": {"type": "json_schema", "schema": {...}}},
)
```

See [Responses API Guide](references/01-responses-api.md) for comprehensive examples including tools, structured outputs, reasoning models, and advanced features.

### Chat Completions API

The traditional chat interface (supported indefinitely):

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

See [Chat Completions Guide](references/01-responses-api.md) for streaming, function calling, and vision examples.

### Embeddings

Generate vector representations for text:

```python
from openai import OpenAI

client = OpenAI()

embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input="The food was delicious and the waiter...",
)

print(embedding.data[0].embedding)  # List of floats
```

See [Embeddings Guide](references/03-embeddings-audio.md) for batch processing and use cases.

### Audio Processing

Transcribe audio to text:

```python
from openai import OpenAI

client = OpenAI()

transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=open("audio.mp3", "rb"),
)

print(transcription.text)
```

See [Audio Processing Guide](references/03-embeddings-audio.md) for speech synthesis and advanced options.

### Image Generation

Generate images with DALL-E 3:

```python
from openai import OpenAI

client = OpenAI()

response = client.images.generate(
    model="dall-e-3",
    prompt="A cute baby sea otter floating on its back",
    size="1024x1024",
    n=1,
)

print(response.data[0].url)
```

See [Image Generation Guide](references/04-images-moderation.md) for variations and edits.

### Assistants API

Create stateful assistants with tool use:

```python
from openai import OpenAI

client = OpenAI()

# Create an assistant
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor.",
    model="gpt-4o",
)

# Create a thread and add a message
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="How do I solve 3x + 11 = 14?",
)

# Create a run to execute the assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

# Poll for completion and retrieve messages
run = client.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id,
)
```

See [Assistants API Guide](references/05-assistants-api.md) for tool use, file search, and code interpreter.

## Reference Files

- [`references/01-responses-api.md`](references/01-responses-api.md) - Responses API and Chat Completions with streaming, function calling, and vision
- [`references/02-client-config.md`](references/02-client-config.md) - Client configuration, authentication, retries, timeouts, and error handling
- [`references/03-embeddings-audio.md`](references/03-embeddings-audio.md) - Embeddings for search/classification and audio transcription/synthesis
- [`references/04-images-moderation.md`](references/04-images-moderation.md) - Image generation with DALL-E and content moderation
- [`references/05-assistants-api.md`](references/05-assistants-api.md) - Stateful assistants with threads, runs, tools, and file search
- [`references/06-fine-tuning-batch.md`](references/06-fine-tuning-batch.md) - Model fine-tuning and batch processing for cost efficiency
- [`references/07-advanced-topics.md`](references/07-advanced-topics.md) - Realtime API, webhooks, pagination, Azure OpenAI, and custom requests

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/openai-2-31/`). All paths are relative to this directory.

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `AuthenticationError` | Invalid or missing API key | Verify `OPENAI_API_KEY` is set correctly |
| `RateLimitError` | Too many requests | Implement exponential backoff or reduce request rate |
| `NotFoundError` | Invalid model or resource ID | Check model name and resource IDs |
| `BadRequestError` | Invalid request parameters | Validate request structure against API docs |
| `APIConnectionError` | Network issues | Check network connectivity and timeout settings |

See [Error Handling](references/02-client-config.md#error-handling) for detailed examples.

### Rate Limits

- Automatic retries (2x by default) for 429, 5xx, and connection errors
- Configure with `max_retries` parameter
- Use batch API for large-scale processing

### Debugging

Enable logging:

```bash
export OPENAI_LOG=info  # or 'debug' for verbose output
```

Access request IDs from responses:

```python
response = client.responses.create(model="gpt-5.2", input="test")
print(response._request_id)  # For reporting issues to OpenAI
```

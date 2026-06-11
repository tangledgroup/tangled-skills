---
name: openai-python-2-38-0
description: Complete toolkit for OpenAI Python SDK 2.38.0 providing typed sync/async clients for the Responses API, Chat Completions API, Realtime API, multimodal (audio/image/video), and Azure OpenAI. Use when building Python applications that call OpenAI models, stream responses, handle tool calling, authenticate via workload identity, or integrate with Azure OpenAI.
---

# OpenAI Python SDK 2.38.0

## Overview

The `openai` Python package (v2.38.0) provides typed, synchronous and asynchronous access to the OpenAI REST API. Generated from the OpenAI OpenAPI spec via Stainless, it offers full type definitions for all request parameters and response fields, with both sync (`OpenAI`) and async (`AsyncOpenAI`) clients powered by `httpx`.

The primary API is the [Responses API](https://platform.openai.com/docs/api-reference/responses), with the Chat Completions API still supported indefinitely. The SDK also supports the Realtime API (WebSocket-based, low-latency conversations), multimodal operations (audio, images, video, vision), file uploads, webhooks, and Azure OpenAI.

Requires Python 3.9+. Install with `pip install openai`. For realtime audio support: `pip install openai[realtime]`. For aiohttp backend: `pip install openai[aiohttp]`.

## When to Use

- Calling OpenAI models from Python (chat, completions, responses)
- Streaming responses via Server-Sent Events (SSE)
- Structured outputs with Pydantic models (`response_format`, `.parse()`)
- Tool calling / function calling with `pydantic_function_tool`
- Realtime API for low-latency conversational audio/text
- Audio operations: text-to-speech, speech-to-text, Whisper transcription
- Image generation (DALL-E), image streaming, video generation (Sora)
- Vision (image input via URLs or base64)
- Azure OpenAI integration with `AzureOpenAI`
- Workload identity authentication (Kubernetes, Azure, GCP)
- Webhook signature verification
- Chunked file uploads for large files

## Core Concepts

### Client Initialization

```python
from openai import OpenAI

# Reads OPENAI_API_KEY from environment
client = OpenAI()

# Explicit key
client = OpenAI(api_key="sk-...")

# Custom base URL (e.g., proxy or compatible server)
client = OpenAI(base_url="https://my-proxy.example.com/v1")
```

Async client mirrors sync:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()
response = await client.responses.create(model="gpt-5.2", input="Hello")
```

### Responses API (Primary)

The Responses API is the current primary interface:

```python
response = client.responses.create(
    model="gpt-5.2",
    instructions="You are a coding assistant.",
    input="How do I check if an object is an instance of a class?",
)
print(response.output_text)
```

### Chat Completions API (Legacy, Supported Indefinitely)

```python
completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[
        {"role": "developer", "content": "Talk like a pirate."},
        {"role": "user", "content": "What is 2+2?"},
    ],
)
print(completion.choices[0].message.content)
```

### Streaming

Both APIs support streaming via SSE:

```python
stream = client.responses.create(
    model="gpt-5.2",
    input="Write a one-sentence bedtime story.",
    stream=True,
)
for event in stream:
    print(event)
```

For Chat Completions:

```python
stream = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
```

### Error Handling

All errors inherit from `openai.APIError`. Catch specific subclasses:

```python
import openai

try:
    client.fine_tuning.jobs.create(model="gpt-4o", training_file="file-abc123")
except openai.APIConnectionError as e:
    print("Server could not be reached")
except openai.RateLimitError as e:
    print("Rate limited (429); back off")
except openai.APIStatusError as e:
    print(f"Error {e.status_code}: {e.response}")
```

| Status Code | Error Type |
|---|---|
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 403 | `PermissionDeniedError` |
| 404 | `NotFoundError` |
| 422 | `UnprocessableEntityError` |
| 429 | `RateLimitError` |
| >=500 | `InternalServerError` |
| N/A | `APIConnectionError` |

### Retries and Timeouts

Retries are enabled by default (2 attempts) for connection errors, 408, 409, 429, and >=500. Configure with `max_retries`:

```python
client = OpenAI(max_retries=0)  # disable
# Per-request override:
client.with_options(max_retries=5).chat.completions.create(...)
```

Default timeout is 10 minutes. Override:

```python
client = OpenAI(timeout=20.0)  # 20 seconds
# Granular control:
import httpx
client = OpenAI(timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0))
```

### Pagination

List methods return auto-paginating iterators:

```python
for job in client.fine_tuning.jobs.list(limit=20):
    print(job.id)
```

For manual page control, use `.has_next_page()`, `.next_page_info()`, `.get_next_page()`.

### Response Types and Raw Access

Responses are Pydantic models with `to_json()` and `to_dict()` helpers. Access raw response headers:

```python
response = client.chat.completions.with_raw_response.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.headers.get("x-request-id"))
completion = response.parse()
```

For streaming raw responses (read body lazily):

```python
with client.chat.completions.with_streaming_response.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Hello"}],
) as response:
    for line in response.iter_lines():
        print(line)
```

### Request IDs

Access `response._request_id` on any response object. For failed requests, catch `APIStatusError` and read `exc.request_id`.

## Advanced Topics

**Responses API**: Streaming, background tasks, structured outputs, tool calling, input tokens, websocket connections → [Responses API](reference/01-responses-api.md)

**Chat Completions**: Parsing with Pydantic, function tools, streaming completions, structured parsing → [Chat Completions](reference/02-chat-completions.md)

**Multimodal**: Audio (TTS, STT, Whisper), images (DALL-E, streaming), video (Sora), vision input → [Multimodal](reference/03-multimodal.md)

**Realtime API**: WebSocket connections, session management, conversation items, audio I/O, error handling → [Realtime API](reference/04-realtime-api.md)

**Advanced Patterns**: Azure OpenAI, workload identity auth, file uploads, webhooks, HTTP client config, aiohttp backend → [Advanced Patterns](reference/05-advanced-patterns.md)

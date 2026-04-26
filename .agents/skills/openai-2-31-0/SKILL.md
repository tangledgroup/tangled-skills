---
name: openai-2-31-0
description: Python SDK for OpenAI API v2.31 providing type-safe access to Responses API, Chat Completions, embeddings, audio transcription/synthesis, image generation, assistants, fine-tuning, and batch operations with sync/async clients. Use when building Python applications that integrate with OpenAI models for text generation, vision, audio processing, or automated assistants.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2.31.0"
tags:
  - openai
  - llm
  - ai
  - chat-completions
  - responses-api
  - embeddings
  - assistants
  - python-sdk
category: sdk
external_references:
  - https://platform.openai.com/docs/
  - https://github.com/openai/openai-python
---

# OpenAI Python SDK v2.31

## Overview

The OpenAI Python library provides convenient access to the OpenAI REST API from any Python 3.9+ application. Generated from the official OpenAPI specification with Stainless, it includes type definitions for all request parameters and response fields, and offers both synchronous and asynchronous clients powered by httpx (with optional aiohttp backend).

The primary API is the [Responses API](https://platform.openai.com/docs/api-reference/responses), with the previous Chat Completions API supported indefinitely. Additional capabilities include embeddings, audio transcription and synthesis, image generation, fine-tuning, batch processing, assistants, vector stores, real-time WebSocket conversations, moderations, and more.

## When to Use

- Building Python applications that call OpenAI models (GPT-4, GPT-5, o-series, etc.)
- Generating text via the Responses API or Chat Completions API
- Creating embeddings for semantic search or RAG pipelines
- Transcribing audio, translating speech, or generating speech from text
- Generating images with DALL·E models
- Building automated assistants with threads, runs, and tool use
- Fine-tuning models on custom datasets
- Processing requests in batch for cost efficiency
- Implementing real-time conversational experiences via WebSocket

## Installation / Setup

Install from PyPI:

```bash
pip install openai
```

For aiohttp backend support (improved async concurrency):

```bash
pip install "openai[aiohttp]"
```

### Configuration

Set the `OPENAI_API_KEY` environment variable or pass it directly:

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
```

Recommended: use a `.env` file with `python-dotenv` to avoid storing keys in source control. Get an API key at [platform.openai.com](https://platform.openai.com/settings/organization/api-keys).

### Client Options

The constructor accepts additional configuration:

```python
from openai import OpenAI, Timeout

client = OpenAI(
    api_key="sk-...",
    organization="org-xyz",
    project="proj-abc",
    base_url="https://api.openai.com/v1",  # default
    timeout=Timeout(connect=5.0, read=60.0, write=60.0, pool=5.0),
    max_retries=2,  # default
    http_client=my_httpx_client,  # custom httpx client
)
```

Default timeout is 10 minutes (600s). Default max retries is 2 with exponential backoff starting at 0.5s (max 8s).

## Core Concepts

### Two API Paradigms

**Responses API** — the current primary interface. Uses `input` (array of messages) and `instructions` instead of `messages` and `system`. Returns structured `Response` objects with `output_text`, `output`, and usage metadata.

```python
response = client.responses.create(
    model="gpt-5.2",
    instructions="You are a coding assistant.",
    input="How do I check if a Python object is an instance of a class?",
)
print(response.output_text)
```

**Chat Completions API** — the previous standard, supported indefinitely. Uses `messages` array with `role`/`content` pairs.

```python
completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[
        {"role": "developer", "content": "You are a coding assistant."},
        {"role": "user", "content": "How do I check if a Python object is an instance of a class?"},
    ],
)
print(completion.choices[0].message.content)
```

### Sync and Async Clients

`OpenAI` is synchronous. `AsyncOpenAI` is asynchronous — identical API surface with `await`:

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main():
    response = await client.responses.create(
        model="gpt-5.2",
        input="Explain quantum computing simply.",
    )
    print(response.output_text)

asyncio.run(main())
```

### Streaming

Both APIs support server-sent events (SSE) streaming via `stream=True`:

```python
stream = client.responses.create(
    model="gpt-5.2",
    input="Write a short poem.",
    stream=True,
)
for event in stream:
    print(event)
```

### Type Safety

Request parameters use `TypedDict`. Responses are Pydantic models with helper methods:

- `model.to_json()` — serialize back to JSON string
- `model.to_dict()` — convert to dictionary

Set `python.analysis.typeCheckingMode` to `"basic"` in VS Code for type error display.

### Pagination

List methods return auto-paginating iterators:

```python
all_jobs = []
for job in client.fine_tuning.jobs.list(limit=20):
    all_jobs.append(job)
```

For manual control, use `.has_next_page()`, `.next_page_info()`, and `.get_next_page()`.

### Azure OpenAI

Use `AzureOpenAI` / `AsyncAzureOpenAI` for Azure deployments:

```python
from openai.lib.azure import AzureOpenAI

client = AzureOpenAI(
    api_key="...",
    azure_endpoint="https://<resource>.openai.azure.com/",
    api_version="2025-01-01-preview",
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### Workload Identity Authentication

For cloud-managed environments, use short-lived tokens instead of API keys:

```python
from openai import OpenAI
from openai.auth import k8s_service_account_token_provider

client = OpenAI(
    workload_identity={
        "client_id": "your-client-id",
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": k8s_service_account_token_provider(
            "/var/run/secrets/kubernetes.io/serviceaccount/token"
        ),
    },
)
```

Providers available: `k8s_service_account_token_provider`, `azure_managed_identity_token_provider`, `gcp_id_token_provider`, or custom callable.

### Error Handling

The SDK raises typed exceptions:

- `APIStatusError` — 4xx/5xx responses (has `status_code`, `response`, `request_id`)
- `RateLimitError` — 429 rate limit
- `AuthenticationError` — 401 auth failure
- `NotFoundError` — 404 resource not found
- `BadRequestError` — 400 bad request
- `APIConnectionError` — network issues
- `APITimeoutError` — request timeout
- `InternalServerError` — 5xx server error

```python
from openai import OpenAI, APIStatusError, RateLimitError

client = OpenAI()
try:
    response = client.responses.create(model="gpt-5.2", input="Hello")
except RateLimitError:
    print("Rate limited, retry later")
except APIStatusError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## Advanced Topics

**Responses API**: The primary text generation interface with structured output → [Responses API](reference/01-responses-api.md)

**Chat Completions**: Legacy API with function calling, vision, and tool use → [Chat Completions](reference/02-chat-completions.md)

**Audio**: Transcription, translation, and speech synthesis → [Audio](reference/03-audio.md)

**Embeddings and Images**: Vector embeddings and image generation/editing → [Embeddings and Images](reference/04-embeddings-images.md)

**Assistants API**: Threads, runs, tools, and file search for automated agents → [Assistants API](reference/05-assistants-api.md)

**Fine-Tuning**: Custom model training with supervised, DPO, and reinforcement methods → [Fine-Tuning](reference/06-fine-tuning.md)

**Realtime API**: Low-latency conversational WebSocket interface → [Realtime API](reference/07-realtime-api.md)

**Batch Processing and Files**: Bulk request processing and file management → [Batch and Files](reference/08-batch-files.md)

**Vector Stores**: Managed document storage for assistant file search → [Vector Stores](reference/09-vector-stores.md)

**Other APIs**: Moderations, models, evaluations, skills, videos, containers, webhooks → [Other APIs](reference/10-other-apis.md)

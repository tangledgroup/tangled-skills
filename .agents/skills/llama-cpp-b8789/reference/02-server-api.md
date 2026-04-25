# Server API Reference for llama.cpp b8789

## Overview

The `llama-server` provides an OpenAI-compatible HTTP API for LLM inference with additional features like multimodal support, function calling, and speculative decoding.

**Default endpoint:** `http://127.0.0.1:8080`

## Authentication

**API Key (optional):**
```bash
llama-server --api-key my-secret-key
```

Multiple keys: `--api-key key1,key2,key3`
Key file: `--api-key-file /path/to/keys.txt`

**Headers:**
```
Authorization: Bearer my-secret-key
```

## Health Check

### GET `/health` or `/v1/health`

No authentication required.

**Response when loading:**
```json
HTTP 503
{
  "error": {
    "code": 503,
    "message": "Loading model",
    "type": "unavailable_error"
  }
}
```

**Response when ready:**
```json
HTTP 200
{
  "status": "ok"
}
```

## Chat Completions (OpenAI-Compatible)

### POST `/v1/chat/completions`

**Request:**
```json
{
  "model": "gemma-3-1b",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "What is quantum computing?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 512,
  "top_p": 0.9,
  "stream": false
}
```

**Response:**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1704067200,
  "model": "gemma-3-1b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Quantum computing is a type of computing..."
      },
      "finish_reason": "stop",
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 42,
    "total_tokens": 57
  }
}
```

### Streaming Responses

Set `"stream": true` in request:

```json
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","choices":[{"delta":{"content":"Quantum"}}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","choices":[{"delta":{"content":" computing"}}]}

data: [DONE]
```

### Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | - | Model name (matches server alias) |
| `messages` | array | - | Array of {role, content} objects |
| `temperature` | float | 0.8 | Sampling temperature |
| `max_tokens` | int | -1 | Max tokens to generate (-1 = infinity) |
| `top_p` | float | 0.95 | Nucleus sampling threshold |
| `top_k` | int | 40 | Top-k sampling (0 = disabled) |
| `min_p` | float | 0.05 | Min-p sampling threshold |
| `frequency_penalty` | float | 0.0 | Frequency penalty (0-2) |
| `presence_penalty` | float | 0.0 | Presence penalty (0-2) |
| `repeat_penalty` | float | 1.0 | Repeat penalty |
| `stop` | string|array | null | Stop sequences |
| `stream` | bool | false | Enable streaming |
| `n` | int | 1 | Number of completions to generate |
| `seed` | int | -1 | Random seed (-1 = random) |

### Multimodal Input

**Image input (base64):**
```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,iVBORw0KGgo..."
          }
        },
        {
          "type": "text",
          "text": "What is in this image?"
        }
      ]
    }
  ]
}
```

**Image input (file URL):**
```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "file:///path/to/image.png"
          }
        },
        {
          "type": "text",
          "text": "Describe this image"
        }
      ]
    }
  ]
}
```

## Completions (Legacy)

### POST `/completion`

Non-OpenAI-compatible legacy endpoint:

```json
{
  "prompt": "Building a website can be done in 10 steps:",
  "n_predict": 128,
  "temperature": 0.8,
  "top_k": 40,
  "top_p": 0.9,
  "repeat_penalty": 1.1,
  "stop": ["\n\n"],
  "stream": false
}
```

**Response:**
```json
{
  "completion": " First, plan your site structure...",
  "model": "gemma-3-1b",
  "context": [...],
  "embedding": null,
  "timing": {
    "load_ms": 1234.5,
    "prompt_processing_ms": 45.6,
    "predicted_tokens": 89,
    "prediction_ms": 234.5
  }
}
```

## Embeddings

### POST `/v1/embeddings`

**Request:**
```json
{
  "model": "all-minilm",
  "input": ["Hello world", "How are you?"]
}
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.01, -0.02, 0.03, ...],
      "index": 0
    },
    {
      "object": "embedding",
      "embedding": [0.02, -0.01, 0.04, ...],
      "index": 1
    }
  ],
  "model": "all-minilm",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

## Function Calling / Tool Use

### POST `/v1/chat/completions` with Tools

**Request:**
```json
{
  "model": "llama-3.1-8b",
  "messages": [
    {
      "role": "user",
      "content": "What's the weather in Paris?"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
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
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

**Response with tool call:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "tool_calls": [
          {
            "id": "call_123",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\": \"Paris\", \"unit\": \"celsius\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

**Continue with tool result:**
```json
{
  "messages": [
    {"role": "user", "content": "What's the weather in Paris?"},
    {"role": "assistant", "tool_calls": [...]},
    {
      "role": "tool",
      "tool_call_id": "call_123",
      "content": "{\"temperature\": 18, \"condition\": \"sunny\"}"
    }
  ]
}
```

## JSON Schema Constraints

Force structured output:

```json
{
  "messages": [{"role": "user", "content": "Create a user object"}],
  "grammar": "{\"type\": \"object\", \"properties\": {\"name\": {\"type\": \"string\"}, \"age\": {\"type\": \"integer\"}}}"
}
```

Or use `--json-schema` flag when starting server.

## Models Management

### GET `/v1/models`

List loaded models:

```json
{
  "object": "list",
  "data": [
    {
      "id": "gemma-3-1b",
      "object": "model",
      "owned_by": "ggml-org",
      "permission": []
    }
  ]
}
```

### POST `/lora-adapters`

Apply LoRA adapters at runtime:

```json
{
  "path": "/path/to/lora-adapter.gguf",
  "scale": 1.0
}
```

## Monitoring

### GET `/metrics`

Prometheus-compatible metrics (enable with `--metrics`):

```
# HELP llama_requests_total Total number of requests
# TYPE llama_requests_total counter
llama_requests_total{slot_id="0"} 42

# HELP llama_tokens_generated Total tokens generated
# TYPE llama_tokens_generated counter
llama_tokens_generated{slot_id="0"} 1523
```

### GET `/slots`

Slot status monitoring:

```json
[
  {
    "id": 0,
    "state": "processing",
    "n_prompt_tokens": 15,
    "n_predicted_tokens": 42,
    "prompt_processing": 45.6,
    "prediction_durations": [5.2, 4.8, 5.1]
  }
]
```

## Configuration Endpoints

### POST `/props`

Change server properties at runtime (enable with `--props`):

```json
{
  "n_parallel": 4,
  "ctx_size": 8192
}
```

## Anthropic-Compatible API

### POST `/anthropic/v1/messages`

**Request:**
```json
{
  "model": "claude-3-haiku",
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "max_tokens": 1024,
  "temperature": 0.7
}
```

## Server Startup Options

**Basic:**
```bash
llama-server -m model.gguf --host 0.0.0.0 --port 8080
```

**With GPU:**
```bash
llama-server -m model.gguf --n-gpu-layers 99
```

**From Hugging Face:**
```bash
llama-server -hf ggml-org/gemma-3-1b-it-GGUF
```

**Multimodal:**
```bash
llama-server -hf ggml-org/gemma-3-4b-it-GGUF --mmproj-auto
```

**Speculative decoding:**
```bash
llama-server -m model.gguf \
  --model-draft draft-model.gguf \
  --draft-max 16
```

**SSL/TLS:**
```bash
llama-server -m model.gguf \
  --ssl-cert-file /path/to/cert.pem \
  --ssl-key-file /path/to/key.pem
```

**Full options:**
```bash
llama-server --help
```

## Rate Limiting

Control concurrency with `--parallel`:

```bash
# Allow 4 simultaneous requests
llama-server -m model.gguf --parallel 4
```

## Context Management

**Enable prompt caching:**
```bash
llama-server --cache-prompt
```

**Set context size:**
```bash
llama-server -c 8192
```

**KV cache quantization:**
```bash
llama-server --cache-type-k q4_0 --cache-type-v q4_0
```

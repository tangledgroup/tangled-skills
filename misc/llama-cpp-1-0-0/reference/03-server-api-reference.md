# Server API Reference

## llama-server Overview

`llama-server` is a lightweight HTTP server providing OpenAI-compatible APIs for local LLM inference. It supports chat completions, text completions, embeddings, reranking, tool calling, multimodal input, and streaming responses.

```bash
llama-server -m model.gguf --port 8080
```

## OpenAI-Compatible Endpoints

### GET `/v1/models`

Returns loaded model information:

```json
{
  "object": "list",
  "data": [{
    "id": "model.gguf",
    "object": "model",
    "created": 1735142223,
    "owned_by": "llamacpp"
  }]
}
```

### POST `/v1/chat/completions`

Chat completions with streaming support. Uses the model's chat template for message formatting.

Request body:

```json
{
  "model": "local",
  "messages": [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 256,
  "stream": false
}
```

Response includes a `timings` object:

```json
{
  "choices": [{"message": {"role": "assistant", "content": "Hello!"}}],
  "timings": {
    "cache_n": 10,
    "prompt_n": 5,
    "prompt_ms": 50.2,
    "predicted_n": 20,
    "predicted_ms": 400.0,
    "predicted_per_second": 50.0
  }
}
```

Supported parameters beyond OpenAI spec:

- `mirostat` — Mirostat sampling (0=disabled, 1=Mirostat, 2=Mirostat 2.0)
- `dynatemp_range` — dynamic temperature range
- `reasoning_format` — reasoning output format (`none`, `deepseek`, `auto`)
- `chat_template_kwargs` — additional Jinja template parameters
- `parallel_tool_calls` — enable multiple tool calls

### POST `/v1/completions`

Legacy text completions API (OAI-compatible). Accepts `prompt` as string.

### POST `/v1/embeddings`

Generate text embeddings. Requires model with pooling type other than `none`.

```json
{
  "input": "hello world",
  "model": "embed-model"
}
```

### POST `/v1/messages`

Anthropic-compatible Messages API. Supports streaming via Server-Sent Events.

## Non-OpenAI Endpoints

### POST `/completion`

Low-level completion endpoint (not OAI-compatible). Rich parameter set:

- `prompt` — text, token array, or mixed
- `temperature`, `top_k`, `top_p`, `min_p` — sampling parameters
- `n_predict` — max tokens to generate (-1 = infinity)
- `repeat_penalty`, `presence_penalty`, `frequency_penalty`
- `samplers` — ordered sampler chain
- `grammar` — GBNF grammar for constrained output
- `json_schema` — JSON schema (auto-converted to grammar)
- `logit_bias` — token-level probability modification
- `n_probs` — return top-N token probabilities
- `stream` — SSE streaming mode
- `lora` — per-request LoRA adapter scaling

### POST `/embedding`

Non-OAI embedding endpoint supporting all pooling types including `none` (returns unnormalized per-token embeddings).

### POST `/reranking`

Rerank documents against a query. Requires reranker model with `--embedding --pooling rank`:

```json
{
  "query": "What is panda?",
  "top_n": 3,
  "documents": ["hi", "it is a bear", "The giant panda..."]
}
```

### POST `/tokenize` / POST `/detokenize`

Convert text to tokens and vice versa.

### POST `/apply-template`

Apply chat template to messages without inference. Returns formatted prompt string.

### POST `/infill`

Code infilling endpoint for Fill-In-the-Middle (FIM) models:

```json
{
  "input_prefix": "def hello(",
  "input_suffix": "):\n    print('world')",
  "input_extra": [{"filename": "main.py", "text": "..."}]
}
```

### GET `/props`

Server properties including model path, chat template, generation settings, and modalities.

### GET `/slots`

Per-slot processing state (speed, tokens processed, sampling parameters). Disable with `--no-slots`.

### GET `/metrics`

Prometheus-compatible metrics (enable with `--metrics`):

- `llamacpp:prompt_tokens_total`
- `llamacpp:tokens_predicted_total`
- `llamacpp:prompt_tokens_seconds`
- `llamacpp:predicted_tokens_seconds`
- `llamacpp:kv_cache_usage_ratio`
- `llamacpp:n_tokens_max`

## Router Mode

Start without a model to enable dynamic model loading:

```bash
llama-server --models-dir ./my_models
```

Models are loaded on-demand based on the `"model"` field in requests. Directory structure:

```
models/
├── llama-3.2-1b-Q4_K_M.gguf          # single file
├── gemma-3-4b-it-Q8_0/               # multimodal
│   ├── gemma-3-4b-it-Q8_0.gguf
│   └── mmproj-F16.gguf
└── Kimi-K2-IQ1_S/                    # multi-shard
    ├── Kimi-K2-IQ1_S-00001-of-00006.gguf
    └── ...
```

### Router Endpoints

- `GET /models` — list available models and their status
- `POST /models/load` — load a model by name
- `POST /models/unload` — unload a model

### Model Presets

Define per-model configurations in INI format:

```ini
[*]
c = 8192
n-gpu-layers = 8

[ggml-org/MY-MODEL-GGUF:Q8_0]
chat-template = chatml
n-gpu-layers = 123
jinja = true

[custom_model]
model = /path/to/model-Q4_K_M.gguf
```

Load with `llama-server --models-preset ./my-models.ini`

## Function Calling

Enable with `--jinja` flag. Supports OpenAI-style function calling:

```bash
llama-server --jinja -fa -hf bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M
```

Native format handlers for: Llama 3.1/3.2/3.3, Functionary v3.1/v3.2, Hermes 2/3, Qwen 2.5, Mistral Nemo, Firefunction v2, Command R7B, DeepSeek R1. Generic fallback for unrecognized templates.

```json
{
  "messages": [{"role": "user", "content": "What is the weather in Paris?"}],
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "parameters": {"type": "object", "properties": {"location": {"type": "string"}}}
    }
  }]
}
```

## Sleeping on Idle

Auto-sleep after inactivity with `--sleep-idle-seconds N`. Model unloads from RAM; reloads on next request.

## Health Check

```bash
# Returns 200 with {"status": "ok"} when ready
# Returns 503 while model is loading
curl http://localhost:8080/health
```

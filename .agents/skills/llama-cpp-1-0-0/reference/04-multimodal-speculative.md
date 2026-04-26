# Multimodal and Speculative Decoding

## Multimodal Support

llama.cpp supports multimodal input (image and audio) via `libmtmd`. Currently supported through `llama-mtmd-cli` and `llama-server` via the OpenAI-compatible `/chat/completions` API.

### Enabling Multimodal

Two methods:

1. **Hugging Face** — automatic mmproj download with `-hf`:
   ```bash
   llama-server -hf ggml-org/gemma-3-4b-it-GGUF
   # Disable auto mmproj: --no-mmproj
   # Custom mmproj: --mmproj local_file.gguf
   ```

2. **Local files** — specify text model and projector separately:
   ```bash
   llama-server -m gemma-3-4b-it-Q4_K_M.gguf --mmproj mmproj-gemma-3-4b-it-Q4_K_M.gguf
   ```

Disable GPU offload for the projector with `--no-mmproj-offload`.

### Vision Models

Pre-quantized models available at https://huggingface.co/collections/ggml-org/multimodal-ggufs-68244e01ff1f39e5bebeeedc:

- **Gemma 3**: `ggml-org/gemma-3-4b-it-GGUF`, `gemma-3-12b-it-GGUF`, `gemma-3-27b-it-GGUF`
- **Qwen2.5 VL**: `Qwen2.5-VL-3B-Instruct-GGUF` through `Qwen2.5-VL-72B-Instruct-GGUF`
- **Qwen2 VL**: `Qwen2-VL-2B-Instruct-GGUF`, `Qwen2-VL-7B-Instruct-GGUF`
- **Pixtral 12B**: `pixtral-12b-GGUF`
- **SmolVLM**: `SmolVLM-Instruct-GGUF`, `SmolVLM2-2.2B-Instruct-GGUF`
- **InternVL 2.5/3**: `InternVL2_5-4B-GGUF`, `InternVL3-8B-Instruct-GGUF`
- **Llama 4 Scout**: `Llama-4-Scout-17B-16E-Instruct-GGUF`
- **Moondream2**: `moondream2-20250414-GGUF`
- **Mistral Small 3.1 24B**: `Mistral-Small-3.1-24B-Instruct-2503-GGUF`

### Audio Models

- **Ultravox 0.5**: `ultravox-v0_5-llama-3_2-1b-GGUF`, `ultravox-v0_5-llama-3_1-8b-GGUF`
- **Voxtral Mini**: `Voxtral-Mini-3B-2507-GGUF`
- **Qwen3-ASR**: `Qwen3-ASR-0.6B-GGUF`, `Qwen3-ASR-1.7B-GGUF`

### Mixed Modalities (Audio + Vision)

- **Qwen2.5 Omni**: `Qwen2.5-Omni-3B-GGUF`, `Qwen2.5-Omni-7B-GGUF`
- **Qwen3 Omni**: `Qwen3-Omni-30B-A3B-Instruct-GGUF`
- **Gemma 4**: `gemma-4-E2B-it-GGUF`, `gemma-4-26B-A4B-it-GGUF`

### Multimodal in API

Via the `/chat/completions` endpoint, include images using `image_url` content parts (base64 or remote URL):

```json
{
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "What is in this image?"},
      {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
    ]
  }]
}
```

## Speculative Decoding

Speculative decoding accelerates token generation by predicting multiple tokens ahead and verifying them in a single batch. Computing N tokens in a batch (prompt processing) is more efficient than computing N sequentially (response generation).

### Draft Model

A smaller "draft" model generates candidate tokens that the main model verifies:

```bash
llama-server -m large-model.gguf -md draft-model.gguf
```

The draft model should be a small variant of the target model.

### N-gram Speculation (No Draft Model)

Several n-gram based methods work without a separate draft model:

**ngram-simple** — simplest self-speculative approach:
```bash
llama-server -m model.gguf --spec-type ngram-simple --draft-max 64
```

**ngram-map-k** — hash-map based, tracks acceptance per n-gram:
```bash
llama-server -m model.gguf --spec-type ngram-map-k --draft-max 64
```

**ngram-map-k4v** — experimental, tracks up to 4 candidate continuations per key:
```bash
llama-server -m model.gguf --spec-type ngram-map-k4v \
  --spec-ngram-size-n 8 --spec-ngram-size-m 8 \
  --spec-ngram-min-hits 2 --draft-max 64
```

**ngram-mod** — shared hash pool across server slots (~16 MB):
```bash
llama-server -m model.gguf --spec-type ngram-mod \
  --spec-ngram-size-n 24 --draft-min 48 --draft-max 64
```

### Speculative Parameters

- `--draft-max N` — max draft tokens (default: 16)
- `--draft-min N` — min draft tokens (default: 0)
- `--spec-ngram-size-n N` — lookup n-gram length (default: 12)
- `--spec-ngram-size-m M` — draft m-gram length (default: 48)
- `--spec-ngram-min-hits N` — minimum occurrence count for ngram-map (default: 1)

### Statistics

Each implementation prints acceptance statistics:

```
draft acceptance rate = 0.57576 (171 accepted / 297 generated)
statistics ngram_simple: #calls = 15, #gen drafts = 5, #acc drafts = 5,
  #gen tokens = 187, #acc tokens = 73
```

Higher acceptance rate means more speedup. Ideal use cases:

- Source code rewriting (high repetition patterns)
- Reasoning models (repeat thinking in final answer)
- Summarization tasks

### Mixing Draft Model with N-gram

Draft model and draftless speculation can be combined. Draftless decoding has higher precedence when both are configured.

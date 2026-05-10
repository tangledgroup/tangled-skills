---
name: llama-cpp-1-0-0
description: C/C++ LLM inference library with GGUF support, quantization, GPU acceleration (CUDA/Metal/HIP/Vulkan/SYCL), OpenAI-compatible server, and speculative decoding. Use when building local LLM inference applications, deploying models on edge devices, creating OpenAI-compatible API servers, or working with GGUF models.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - llm
  - inference
  - gguf
  - quantization
  - cuda
  - metal
  - server
  - local-ai
category: machine-learning
external_references:
  - https://github.com/ggml-org/llama.cpp/tree/b8789
  - https://github.com/ggml-org/llama.cpp/blob/b8789/docs/gguf.md
  - https://github.com/ggml-org/llama.cpp/issues/9289
  - https://github.com/ggml-org/llama.cpp/issues/9291
  - https://github.com/orgs/ggml-org/packages/container/package/llama.cpp
  - https://huggingface.co/models?search=ggml-org
  - https://github.com/ggml-org/llama.cpp/tree/b8789/docs
---

# llama.cpp b8789

## Overview

llama.cpp is a plain C/C++ implementation for LLM inference with minimal setup and state-of-the-art performance across a wide range of hardware — locally and in the cloud. It requires no external dependencies beyond system libraries, making it ideal for edge deployment, embedded systems, and resource-constrained environments.

Key capabilities:

- **GGUF model format** — native support for GGUF files with extensive quantization options
- **Multi-backend GPU acceleration** — CUDA (NVIDIA), Metal (Apple Silicon), HIP (AMD), Vulkan, SYCL (Intel), MUSA (Moore Threads), CANN (Ascend NPU)
- **OpenAI-compatible HTTP server** — `llama-server` with full chat completions, embeddings, and tool calling support
- **Multimodal input** — image and audio support via libmtmd for vision-language models
- **Speculative decoding** — draft model and n-gram based acceleration
- **Function calling** — OpenAI-style tool use with native format handlers for Llama 3.x, Hermes, Qwen, Mistral, and more
- **Grammar-constrained generation** — GBNF grammars and JSON schema support for structured outputs
- **CPU optimizations** — ARM NEON, AVX/AVX2/AVX512/AMX, RVV/ZVFH, ZenDNN, Arm KleidiAI

## When to Use

- Running LLM inference locally without cloud dependencies
- Deploying models on edge devices with limited resources
- Building OpenAI-compatible API endpoints for local model serving
- Implementing multimodal AI (vision + text) applications
- Quantizing large models for reduced memory footprint
- Creating structured output pipelines with grammar constraints
- Developing cross-platform AI applications (Windows, macOS, Linux, Android)
- Building tools that integrate with LLMs via the `libllama` C API

## Core Tools

**`llama-cli`** — Interactive CLI for conversation mode, completion, and experimentation. Supports chat templates, multimodal input, speculative decoding, grammar constraints, and all sampling parameters.

```bash
# Local model file
llama-cli -m my_model.gguf

# Download from Hugging Face
llama-cli -hf ggml-org/gemma-3-1b-it-GGUF

# Multimodal model with image
llama-cli -hf ggml-org/gemma-3-4b-it-GGUF --image photo.jpg
```

**`llama-server`** — Lightweight OpenAI-compatible HTTP server for serving LLMs. Supports chat completions, embeddings, reranking, tool calling, multimodal input, router mode (multiple models), and streaming.

```bash
# Start server on port 8080
llama-server -m model.gguf --port 8080

# With Hugging Face model
llama-server -hf ggml-org/gemma-3-1b-it-GGUF

# Router mode (multiple models)
llama-server --models-dir ./my_models
```

**`llama-quantize`** — Convert GGUF models between quantization formats. Supports Q4_K_M, Q8_0, IQ2_XS, and many other schemes.

```bash
# Quantize to Q4_K_M
llama-quantize input-f32.gguf output-Q4_K_M.gguf Q4_K_M

# With importance matrix for quality
llama-quantize --imatrix imatrix.gguf input-f16.gguf output-Q4_K_M.gguf Q4_K_M
```

**`llama-perplexity`** — Measure model perplexity (quality metric) over text files.

```bash
llama-perplexity -m model.gguf -f test-corpus.txt
```

**`llama-bench`** — Benchmark inference performance across various parameters.

```bash
llama-bench -m model.gguf
```

## Installation / Setup

### Pre-built Packages

- **Homebrew** (macOS/Linux): `brew install llama.cpp`
- **Winget** (Windows): `winget install llama.cpp`
- **MacPorts** (macOS): `sudo port install llama.cpp`
- **Nix** (macOS/Linux): `nix profile install nixpkgs#llama-cpp`

### Docker

Official images available on GitHub Container Registry:

```bash
# Full image with conversion tools
docker run -v /path/to/models:/models ghcr.io/ggml-org/llama.cpp:full --run -m /models/model.gguf

# CUDA variant
docker run --gpus all -v /path/to/models:/models ghcr.io/ggml-org/llama.cpp:full-cuda -m /models/model.gguf -ngl 99

# Server image
docker run -v /path/to/models:/models -p 8080:8080 ghcr.io/ggml-org/llama.cpp:server -m /models/model.gguf --port 8080
```

### Build from Source

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp

# CPU-only build
cmake -B build
cmake --build build --config Release

# CUDA build
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release

# Metal (macOS, enabled by default)
cmake -B build
cmake --build build --config Release
```

## Usage Examples

### Interactive Chat

```bash
# Auto-detects chat template and enters conversation mode
llama-cli -m model.gguf -cnv

# With custom chat template
llama-cli -m model.gguf -cnv --chat-template chatml

# With system prompt
llama-cli -m model.gguf -sys "You are a helpful coding assistant."
```

### Constrained Output with Grammar

```bash
# JSON output via grammar file
llama-cli -m model.gguf -n 256 --grammar-file grammars/json.gbnf \
  -p 'Request: schedule a call at 8pm; Command:'

# JSON schema (auto-converted to grammar)
llama-cli -m model.gguf -j '{"type":"object","properties":{"name":{"type":"string"},"age":{"type":"integer"}}}' \
  -p 'Generate a person object.'
```

### OpenAI-Compatible API

```bash
# Start server
llama-server -m model.gguf --port 8080

# Chat completion via curl
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "messages": [
      {"role": "user", "content": "What is 2+2?"}
    ]
  }'

# Python with openai library
python3 -c "
import openai
client = openai.OpenAI(base_url='http://localhost:8080/v1', api_key='sk-no-key-required')
resp = client.chat.completions.create(model='local', messages=[{'role':'user','content':'Hello'}])
print(resp.choices[0].message.content)
"
```

### Embeddings

```bash
# Serve embedding model
llama-server -m embedding-model.gguf --embedding --pooling cls -ub 8192

# Query embeddings
curl http://localhost:8080/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "hello world", "model": "embed"}'
```

### Speculative Decoding

```bash
# Draft model (smaller model accelerates larger one)
llama-server -m large-model.gguf -md draft-model.gguf

# N-gram speculative decoding (no draft model needed)
llama-server -m model.gguf --spec-type ngram-simple --draft-max 64
```

### Multimodal (Vision + Text)

```bash
# CLI with vision model
llama-mtmd-cli -hf ggml-org/gemma-3-4b-it-GGUF

# Server with multimodal support
llama-server -hf ggml-org/gemma-3-4b-it-GGUF

# Local files
llama-server -m text-model.gguf --mmproj mmproj.gguf
```

## Advanced Topics

**Building and Backends**: CUDA, Metal, HIP, Vulkan, SYCL, CANN, ZenDNN, KleidiAI, OpenVINO build configurations and runtime tuning → [Building and Backends](reference/01-building-backends.md)

**Model Quantization**: Quantization formats (Q4_K_M, Q8_0, IQ2_XS, etc.), importance matrices, quality vs size tradeoffs, perplexity measurement → [Model Quantization](reference/02-model-quantization.md)

**Server API Reference**: OpenAI-compatible endpoints (`/v1/chat/completions`, `/v1/embeddings`, `/v1/completions`), router mode, multimodal, function calling, streaming → [Server API Reference](reference/03-server-api-reference.md)

**Multimodal and Speculative Decoding**: Vision/audio models, libmtmd integration, draft model decoding, n-gram speculation, performance tuning → [Multimodal and Speculative Decoding](reference/04-multimodal-speculative.md)

**Grammar-Constrained Generation**: GBNF grammar format, JSON schema to grammar conversion, structured output patterns, LLGuidance integration → [Grammar-Constrained Generation](reference/05-grammar-constrained-generation.md)

**libllama C API**: Core data structures (`llama_model`, `llama_context`), context management, batch decoding, sampler chains, LoRA adapters, KV cache → [libllama C API](reference/06-libllama-api.md)

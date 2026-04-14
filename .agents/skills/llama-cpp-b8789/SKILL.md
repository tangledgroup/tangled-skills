# llama.cpp b8789

---
name: llama-cpp-b8789
description: C/C++ LLM inference library providing GGUF model support, quantization, GPU acceleration (CUDA/Metal/HIP/Vulkan/SYCL), OpenAI-compatible server, multimodal processing, and speculative decoding for running large language models locally with high performance across diverse hardware platforms.
license: MIT
author: Tangled Skills <skills@tangled.dev>
version: "1.0.0"
tags:
  - llm
  - inference
  - gguf
  - quantization
  - cuda
  - metal
  - server
category: machine-learning
external_references:
  - https://github.com/ggml-org/llama.cpp/tree/b8789
  - https://github.com/ggml-org/llama.cpp/tree/b8789/docs
---

**llama.cpp** is a high-performance C/C++ library for running large language models (LLMs) with minimal dependencies and state-of-the-art performance across diverse hardware platforms. Commit `b8789` represents a mature release with comprehensive model support, multimodal capabilities, and production-ready server infrastructure.

## When to Use

Use this skill when:
- Running LLMs locally without external API dependencies
- Deploying models on edge devices or resource-constrained environments
- Needing GPU acceleration via CUDA, Metal, HIP, Vulkan, SYCL, or ROCm
- Building OpenAI-compatible inference servers
- Implementing quantization to reduce model memory footprint (4-bit, 5-bit, 6-bit, 8-bit)
- Working with GGUF format models from Hugging Face
- Requiring multimodal capabilities (vision, audio processing)
- Implementing function calling / tool use for LLM agents
- Using speculative decoding for faster token generation

## Core Concepts

### GGUF Format

GGUF (Generative AI GPU File Format) is the native model format for llama.cpp:
- Stores weights in quantized or full precision
- Embeds tokenizer data and chat templates
- Enables memory-mapped loading for efficient I/O
- Supports multimodal projector files (.gguf for mmproj)

### Quantization Types

| Type | Bits | Description | Use Case |
|------|------|-------------|----------|
| `Q4_K_S` | ~4.0 | Small 4-bit quantization | Minimal memory, good quality |
| `Q4_K_M` | ~4.2 | Medium 4-bit (recommended) | Best balance speed/quality |
| `Q5_K_M` | ~5.0 | Medium 5-bit | Higher quality, more VRAM |
| `Q6_K` | ~6.0 | 6-bit quantization | Near-lossless quality |
| `Q8_0` | ~8.0 | 8-bit quantization | Almost full precision |
| `IQ2_XS` | ~2.0 | Extreme 2-bit compression | Ultra-low memory |

### Hardware Backends

- **CPU**: AVX, AVX2, AVX512, NEON, RVV optimizations
- **CUDA**: NVIDIA GPU acceleration with custom kernels
- **Metal**: Apple Silicon GPU (macOS/iOS)
- **HIP**: AMD GPU via ROCm
- **Vulkan**: Cross-platform GPU support
- **SYCL**: Intel GPU (Data Center Max, Arc, iGPU)
- **MUSA**: Moore Threads GPU
- **OpenVINO**: Intel CPU/GPU/NPU

## Quick Start

### Installation

**Homebrew (macOS/Linux):**
```bash
brew install llama.cpp
```

**Winget (Windows):**
```powershell
winget install llama.cpp
```

**Docker:**
```bash
docker pull ghcr.io/ggml-org/llama.cpp:server
```

**From Source:**
```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release
```

### Running a Model

**CLI Interactive Mode:**
```bash
# Download from Hugging Face and run
llama-cli -hf ggml-org/gemma-3-1b-it-GGUF

# Use local GGUF file
llama-cli -m my-model-Q4_K_M.gguf
```

**OpenAI-Compatible Server:**
```bash
llama-server -hf ggml-org/gemma-3-1b-it-GGUF --host 0.0.0.0 --port 8080
```

**With CUDA GPU:**
```bash
llama-server -m model.gguf --n-gpu-layers 99
```

## API Endpoints

See [Server API Reference](references/02-server-api.md) for complete endpoint documentation including:
- `/v1/chat/completions` - OpenAI-compatible chat
- `/v1/embeddings` - Embedding generation
- `/completion` - Legacy completion endpoint
- Function calling and tool use
- Multimodal input support

## Model Support

See [Supported Models](references/03-models.md) for comprehensive lists of:
- Text-only models (LLaMA, Mistral, Qwen, Gemma, Phi, etc.)
- Multimodal models (vision + audio)
- Code generation models
- Reasoning models with thinking tags

## Advanced Topics

### Quantization Guide
See [Quantization](references/04-quantization.md) for:
- Creating quantized models from GGUF
- Quant type selection guidelines
- Per-tensor vs per-block strategies

### Multimodal Processing
See [Multimodal Support](references/05-multimodal.md) for:
- Vision models (Gemma 3, Qwen2-VL, InternVL)
- Audio models (Ultravox, Qwen3-ASR)
- OCR capabilities
- Image/audio input formats

### Function Calling
See [Function Calling](references/06-function-calling.md) for:
- OpenAI-style tool use
- Native format handlers (Llama 3, Hermes, Qwen)
- JSON schema constraints
- Built-in server tools

### Speculative Decoding
See [Speculative Decoding](references/07-speculative-decoding.md) for:
- Draft model acceleration
- N-gram based methods
- Performance optimization

### GPU Offloading
See [GPU Configuration](references/08-gpu-config.md) for:
- Multi-GPU setups
- Tensor splitting strategies
- VRAM optimization
- Backend-specific tuning

## Build Options

See [Build Guide](references/01-build-guide.md) for:
- CPU-only builds
- CUDA, HIP, Metal, Vulkan backends
- BLAS acceleration (OpenBLAS, oneMKL)
- Docker container builds
- Platform-specific instructions

## Troubleshooting

### Common Issues

**"Cannot find valid GPU for '-arch=native'"**:
```bash
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="86;89"
```

**VRAM exhaustion**:
- Reduce `--n-gpu-layers` to keep some layers on CPU
- Use smaller quantization (Q4_K_M instead of Q8_0)
- Enable unified memory: `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1`

**Slow prompt processing**:
- Increase batch size: `--batch-size 2048`
- Enable Flash Attention: `--flash-attn on`
- Use GPU for more layers

**Context overflow**:
- Reduce context size: `--ctx-size 4096`
- Enable KV cache quantization: `--cache-type-k q4_0 --cache-type-v q4_0`

## References

- **Official Repository**: https://github.com/ggml-org/llama.cpp/tree/b8789
- **Documentation**: https://github.com/ggml-org/llama.cpp/tree/b8789/docs
- **GGUF Format Spec**: https://github.com/ggml-org/llama.cpp/blob/b8789/docs/gguf.md
- **Changelog (libllama API)**: https://github.com/ggml-org/llama.cpp/issues/9289
- **Changelog (Server API)**: https://github.com/ggml-org/llama.cpp/issues/9291
- **Hugging Face GGUF Models**: https://huggingface.co/models?search=ggml-org
- **Docker Images**: https://github.com/orgs/ggml-org/packages/container/package/llama.cpp

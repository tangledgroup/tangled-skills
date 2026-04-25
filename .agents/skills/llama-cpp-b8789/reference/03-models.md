# Supported Models for llama.cpp b8789

## Text-Only Models

### LLaMA Family

| Model | Parameters | Hugging Face | Notes |
|-------|------------|--------------|-------|
| LLaMA 3.1 | 8B, 70B | `meta-llama/Llama-3.1-*` | Native function calling |
| LLaMA 3.2 | 1B, 3B | `meta-llama/Llama-3.2-*` | Edge-optimized |
| LLaMA 3.3 | 70B | `meta-llama/Llama-3.3-70B-Instruct` | Mixture of experts |
| LLaMA 2 | 7B, 13B, 70B | `meta-llama/Llama-2-*` | Legacy but stable |

**Usage:**
```bash
llama-server -hf ggml-org/Llama-3.1-8B-Instruct-GGUF
```

### Mistral Family

| Model | Parameters | Hugging Face | Notes |
|-------|------------|--------------|-------|
| Mistral v0.3 | 7B | `mistralai/Mistral-7B-Instruct-v0.3` | Standard instruct |
| Mistral Nemo | 12B | `mistralai/Mistral-Nemo-Instruct-2407` | Native tool use |
| Mixtral 8x7B | 47B (MoE) | `mistralai/Mixtral-8x7B-Instruct-v0.1` | Sparse MoE |
| Mixtral 8x22B | 141B (MoE) | `mistralai/Mixtral-8x22B-Instruct-v0.1` | Large sparse MoE |

**Usage:**
```bash
llama-server -hf ggml-org/Mistral-7B-Instruct-v0.3-GGUF
```

### Qwen Family

| Model | Parameters | Hugging Face | Notes |
|-------|------------|--------------|-------|
| Qwen2.5 | 0.5B-72B | `Qwen/Qwen2.5-*` | Hermes format tools |
| Qwen2.5 Coder | 0.5B-32B | `Qwen/Qwen2.5-Coder-*` | Code generation |
| Qwen3 | 0.6B-30B | `Qwen/Qwen3-*` | Latest generation |
| QwQ | 32B | `Qwen/QwQ-32B-Preview` | Reasoning model |

**Usage:**
```bash
llama-server -hf ggml-org/Qwen2.5-7B-Instruct-GGUF
```

### Gemma Family

| Model | Parameters | Hugging Face | Notes |
|-------|------------|--------------|-------|
| Gemma 2 | 2B, 9B, 27B | `google/gemma-2-*` | Google's open model |
| Gemma 3 | 1B, 4B, 12B, 27B | `google/gemma-3-*` | Multimodal support |
| Gemma 4 | 2B-31B | `google/gemma-4-*` | Audio+vision capable |

**Usage:**
```bash
llama-server -hf ggml-org/gemma-3-1b-it-GGUF
```

### Phi Family (Microsoft)

| Model | Parameters | Hugging Face | Notes |
|-------|------------|--------------|-------|
| Phi-3 | 3.8B, 14B | `microsoft/Phi-3-*` | Small, efficient |
| Phi-3.5 | 3.8B, 14B | `microsoft/Phi-3.5-*` | Improved reasoning |
| Phi-4 | 14B | `microsoft/phi-4` | Latest generation |

**Usage:**
```bash
llama-server -hf ggml-org/Phi-3.5-mini-instruct-GGUF
```

### DeepSeek

| Model | Parameters | Hugging Face | Notes |
|-------|------------|--------------|-------|
| DeepSeek-Coder | 1.3B-33B | `deepseek-ai/deepseek-coder-*` | Code generation |
| DeepSeek-V2/V3 | 236B (MoE) | `deepseek-ai/DeepSeek-V3` | Massive MoE |
| DeepSeek-R1 | 7B-70B | `deepseek-ai/DeepSeek-R1-*` | Reasoning model |

**Usage:**
```bash
llama-server -hf ggml-org/DeepSeek-R1-Distill-Qwen-7B-GGUF
```

### Other Notable Models

| Model | Parameters | Hugging Face | Notes |
|-------|------------|--------------|-------|
| Falcon3 | 8B+ | `tiiuae/Falcon3-*` | TII UAE |
| OLMo | 1B-7B | `allenai/OLMo-*` | AllenAI open weights |
| Grok-2 | 121B (MoE) | `xai-org/grok-2` | xAI |
| Command R | 35B, 104B | `CohereForAI/c4ai-command-r-*` | Cohere |
| Yi | 1.5B-34B | `01-ai/Yi-*` | 01.AI |

## Multimodal Models

### Vision Models

**Gemma 3 Vision:**
```bash
llama-server -hf ggml-org/gemma-3-4b-it-GGUF
llama-server -hf ggml-org/gemma-3-12b-it-GGUF
llama-server -hf ggml-org/gemma-3-27b-it-GGUF
```

**Qwen2.5-VL:**
```bash
llama-server -hf ggml-org/Qwen2.5-VL-3B-Instruct-GGUF
llama-server -hf ggml-org/Qwen2.5-VL-7B-Instruct-GGUF
llama-server -hf ggml-org/Qwen2.5-VL-32B-Instruct-GGUF
llama-server -hf ggml-org/Qwen2.5-VL-72B-Instruct-GGUF
```

**Qwen2-VL:**
```bash
llama-server -hf ggml-org/Qwen2-VL-2B-Instruct-GGUF
llama-server -hf ggml-org/Qwen2-VL-7B-Instruct-GGUF
```

**InternVL:**
```bash
llama-server -hf ggml-org/InternVL2_5-1B-GGUF
llama-server -hf ggml-org/InternVL2_5-4B-GGUF
llama-server -hf ggml-org/InternVL3-8B-Instruct-GGUF
llama-server -hf ggml-org/InternVL3-14B-Instruct-GGUF
```

**SmolVLM:**
```bash
llama-server -hf ggml-org/SmolVLM-Instruct-GGUF
llama-server -hf ggml-org/SmolVLM2-2.2B-Instruct-GGUF
```

**Other Vision Models:**
```bash
# Pixtral 12B
llama-server -hf ggml-org/pixtral-12b-GGUF

# Llama 4 Scout (vision)
llama-server -hf ggml-org/Llama-4-Scout-17B-16E-Instruct-GGUF

# Moondream2
llama-server -hf ggml-org/moondream2-20250414-GGUF
```

### Audio Models

**Ultravox:**
```bash
llama-server -hf ggml-org/ultravox-v0_5-llama-3_2-1b-GGUF
llama-server -hf ggml-org/ultravox-v0_5-llama-3_1-8b-GGUF
```

**Voxtral (Mistral):**
```bash
llama-server -hf ggml-org/Voxtral-Mini-3B-2507-GGUF
```

**Qwen3-ASR:**
```bash
llama-server -hf ggml-org/Qwen3-ASR-0.6B-GGUF
llama-server -hf ggml-org/Qwen3-ASR-1.7B-GGUF
```

### Multimodal (Vision + Audio)

**Qwen2.5-Omni:**
```bash
llama-server -hf ggml-org/Qwen2.5-Omni-3B-GGUF
llama-server -hf ggml-org/Qwen2.5-Omni-7B-GGUF
```

**Qwen3-Omni:**
```bash
llama-server -hf ggml-org/Qwen3-Omni-30B-A3B-Instruct-GGUF
llama-server -hf ggml-org/Qwen3-Omni-30B-A3B-Thinking-GGUF
```

**Gemma 4:**
```bash
llama-server -hf ggml-org/gemma-4-E2B-it-GGUF
llama-server -hf ggml-org/gemma-4-E4B-it-GGUF
llama-server -hf ggml-org/gemma-4-26B-A4B-it-GGUF
```

### OCR Models

**PaddleOCR-VL:** See https://github.com/ggml-org/llama.cpp/pull/18825

**GLM-OCR:** See https://github.com/ggml-org/llama.cpp/pull/19677

**Deepseek-OCR:** See https://github.com/ggml-org/llama.cpp/pull/17400

**HunyuanOCR:** See https://github.com/ggml-org/llama.cpp/pull/21395

## Code Generation Models

### Qwen Coder Series
```bash
llama-server -hf ggml-org/Qwen2.5-Coder-1.5B-Instruct-GGUF
llama-server -hf ggml-org/Qwen2.5-Coder-3B-Instruct-GGUF
llama-server -hf ggml-org/Qwen2.5-Coder-7B-Instruct-GGUF
llama-server -hf ggml-org/Qwen2.5-Coder-14B-Instruct-GGUF
llama-server -hf ggml-org/Qwen2.5-Coder-32B-Instruct-GGUF
```

### DeepSeek Coder
```bash
llama-server -hf ggml-org/DeepSeek-Coder-V2-Lite-Instruct-GGUF
llama-server -hf ggml-org/DeepSeek-Coder-V2-Instruct-GGUF
```

### StarCoder
```bash
# Various StarCoder models available on Hugging Face
llama-server -m starcoder-15b-Q4_K_M.gguf
```

## Reasoning Models

### DeepSeek R1 Distills
```bash
llama-server -hf ggml-org/DeepSeek-R1-Distill-Qwen-1.5B-GGUF
llama-server -hf ggml-org/DeepSeek-R1-Distill-Qwen-7B-GGUF
llama-server -hf ggml-org/DeepSeek-R1-Distill-Qwen-14B-GGUF
llama-server -hf ggml-org/DeepSeek-R1-Distill-Qwen-32B-GGUF
llama-server -hf ggml-org/DeepSeek-R1-Distill-Llama-8B-GGUF
llama-server -hf ggml-org/DeepSeek-R1-Distill-Llama-70B-GGUF
```

### Native Reasoning Models
```bash
# QwQ (Qwen reasoning)
llama-server -hf ggml-org/QwQ-32B-Preview-GGUF

# OpenThinker
llama-server -hf ggml-org/OpenThinker-7B-GGUF
```

**Enable reasoning extraction:**
```bash
llama-server --reasoning-format deepseek
```

## Finding Models on Hugging Face

**Search for GGUF models:**
- https://huggingface.co/models?search=gguf
- https://huggingface.co/ggml-org (official quantized models)

**Filter by task:**
- Text generation: `pipeline_tag=text2text-generation&sort=trending&search=gguf`
- Vision: `pipeline_tag=image-text-to-text&sort=trending&search=gguf`
- Code: `pipeline_tag=text-generation&sort=trending&search=coder+gguf`

## Model Quantization Selection

| Use Case | Recommended Quant | Memory Savings |
|----------|------------------|----------------|
| Minimal RAM | `IQ2_XS`, `IQ2_S` | ~75% reduction |
| Low RAM (recommended) | `Q4_K_S`, `Q4_K_M` | ~60% reduction |
| Balanced quality | `Q5_K_M`, `Q5_K_S` | ~50% reduction |
| High quality | `Q6_K`, `Q8_0` | ~30-50% reduction |
| Maximum quality | `BF16`, `F16` | No compression |

**Example with specific quant:**
```bash
llama-server -hf ggml-org/Qwen2.5-7B-Instruct-GGUF:Q4_K_M
llama-server -hf ggml-org/gemma-3-1b-it-GGUF:Q5_K_M
```

## Loading Custom Models

**From local file:**
```bash
llama-server -m /path/to/model-Q4_K_M.gguf
```

**With multimodal projector:**
```bash
llama-server -m model.gguf --mmproj mmproj.gguf
```

**From URL:**
```bash
llama-server --model-url https://example.com/model.gguf
```

**Docker Hub models:**
```bash
llama-server --docker-repo ai/gemma3:latest
```

## Model Metadata Override

**Override tokenizer settings:**
```bash
llama-server -m model.gguf \
  --override-kv tokenizer.ggml.add_bos_token=bool:false,tokenizer.ggml.add_eos_token=bool:false
```

**Override tensor placement:**
```bash
llama-server -m model.gguf \
  --override-tensor 'blk.31.*=cpu'  # Keep last layer on CPU
```

## Chat Templates

See [Function Calling](06-function-calling.md) for template formats and function calling support.

**Common templates:**
- `llama3` - LLaMA 3.x native format
- `gemma` - Gemma instruction format
- `qwen` - Qwen chat format
- `mistral-v3` - Mistral v0.3 format
- `deepseek` - DeepSeek with reasoning

**Override template:**
```bash
llama-server --chat-template llama3
llama-server --chat-template-file /path/to/template.jinja
```

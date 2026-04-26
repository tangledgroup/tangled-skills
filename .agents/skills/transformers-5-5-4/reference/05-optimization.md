# Inference Optimization

## Overview

Transformers provides multiple optimization techniques that can be stacked for maximum performance:

- **Compilation** — torch.compile reduces Python overhead and fuses operations
- **Attention backends** — FlashAttention reduces memory traffic
- **Kernels** — Optimized compute kernels from the Hub
- **Quantization** — Lower precision weights reduce memory and increase speed
- **Caching** — KV cache reuse speeds up autoregressive generation
- **Parallelism** — Distribute models across devices
- **Continuous batching** — Dynamic scheduling for serving

## Compilation

`torch.compile` fuses operations and creates hardware-tuned kernels. Pass a fixed-size cache to trigger automatic compilation:

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", dtype=torch.float16, device_map="auto")
inputs = tokenizer("The French Bread Law states", return_tensors="pt").to(model.device)

output = model.generate(**inputs, do_sample=False, max_new_tokens=20, cache_implementation="static")
```

Do not call `torch.compile(model)` outside of `generate()` — it causes recompilation every step.

## Attention Backends

Alternative attention implementations reduce memory usage:

```python
# FlashAttention-2 (requires flash-attn package)
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-0.6B",
    attn_implementation="flash_attention_2"
)

# SDPA (PyTorch's scaled dot-product attention, no extra install)
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-0.6B",
    attn_implementation="sdpa"
)

# Hub kernels (loads optimized kernels from Hugging Face Hub)
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-0.6B",
    attn_implementation="kernels-community/flash-attn2"
)
```

## KV Cache Strategies

The KV cache stores past key-value pairs to avoid recomputation during autoregressive generation.

### Dynamic Cache (Default)

Grows dynamically as generation progresses. Compatible with sliding window attention.

```python
model.generate(**inputs, use_cache=True)  # Default behavior
# Or explicitly:
model.generate(**inputs, cache_implementation="dynamic")
```

### Static Cache

Pre-allocates fixed maximum size. Enables torch.compile optimization but uses more memory.

```python
model.generate(**inputs, cache_implementation="static")
```

### Cache Offloading

Moves KV cache for all but the current layer to CPU. Use when GPU memory is constrained:

```python
model.generate(**inputs, cache_implementation="offloaded")
# Or static + offloaded:
model.generate(**inputs, cache_implementation="offloaded_static")
```

Fallback pattern for OOM situations:

```python
def resilient_generate(model, *args, **kwargs):
    try:
        return model.generate(*args, **kwargs)
    except torch.OutOfMemoryError:
        torch.cuda.empty_cache()
        kwargs["cache_implementation"] = "offloaded"
        return model.generate(*args, **kwargs)
```

## Quantization

Quantization reduces model precision to save memory and increase speed.

### bitsandbytes (4-bit / 8-bit)

On-the-fly quantization, no calibration needed:

```python
from transformers import BitsAndBytesConfig, AutoModelForCausalLM
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4",
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto"
)
```

### GPTQ (4-bit / 8-bit)

Post-training quantization with calibration:

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "model-name-gptq",
    device_map="auto"
)
```

### AWQ (4-bit)

Activation-aware weight quantization:

```python
from awq import AutoAWQForCausalLM

model = AutoAWQForCausalLM.from_quantized("model-name-awq", fuse_layers=True)
```

### GGUF / GGML (llama.cpp)

Load GGUF quantized models directly:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("model-name-gguf", torchscript=True)
model = AutoModelForCausalLM.from_pretrained(
    "model-name-gguf",
    device_map="cpu",  # or "cuda" with llama.cpp CUDA support
    torch_dtype=torch.float16,
)
```

### Quantization Comparison

- **bitsandbytes** — On-the-fly, supports PEFT fine-tuning, works on CPU/CUDA/Metal
- **GPTQ** — Pre-quantized, fast inference, no on-the-fly quantization
- **AWQ** — Activation-aware, better accuracy than standard 4-bit
- **GGUF** — llama.cpp format, CPU-friendly, multiple quantization levels (Q2-K to Q8)
- **compressed-tensors** — 1/8-bit, supports PEFT
- **torchao** — PyTorch's native quantization, 4/8-bit

## Tensor Parallelism

Split model layers across multiple GPUs:

```python
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    tp_plan="auto"
)
print(model._tp_plan)  # Inspect parallelism plan
```

## Continuous Batching

Process multiple requests concurrently with dynamic scheduling:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-0.6B",
    attn_implementation="paged|sdpa",
    device_map="cuda",
    torch_dtype=torch.bfloat16,
)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")

prompts = [
    "The Le Décret Pain states that a baguette must",
    "Explain gravity in one sentence.",
    "Name the capital of France.",
]
inputs = [tokenizer.encode(p) for p in prompts]

gen_config = GenerationConfig(
    max_new_tokens=32,
    eos_token_id=tokenizer.eos_token_id,
    pad_token_id=tokenizer.pad_token_id,
    do_sample=False,
    max_batch_tokens=512,
)

outputs = model.generate_batch(inputs=inputs, generation_config=gen_config)

for request_id, output in outputs.items():
    text = tokenizer.decode(output.generated_tokens, skip_special_tokens=True)
    print(f"[{request_id}] {text}")
```

## Serving with CLI

Run a local inference server:

```bash
transformers serve Qwen/Qwen3-0.6B
# Chat directly from the terminal
transformers chat Qwen/Qwen2.5-0.5B-Instruct
```

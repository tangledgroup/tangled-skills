# Optimization and Deployment - Complete Guide

Comprehensive guide to quantization, model compilation, FlashAttention, model sharding, and deployment patterns for production use.

## Overview

This reference covers techniques to optimize Transformers models for production deployment:
- **Quantization**: Reduce memory usage by 50-75%
- **Compilation**: 10-30% speedup with `torch.compile`
- **FlashAttention**: 20-40% faster attention computation
- **Model Sharding**: Distribute large models across devices
- **Deployment Patterns**: Production-ready serving strategies

## Quantization

### 8-bit Quantization

Reduce memory usage by ~50% with minimal quality loss:

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# Simple 8-bit loading
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    load_in_8bit=True,
    device_map="auto"
)

# With configuration
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,  # Threshold for outlier handling
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    quantization_config=quantization_config,
    device_map="auto"
)
```

### 4-bit Quantization (NF4)

Reduce memory usage by ~75%:

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# Optimal 4-bit configuration
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",  # Normal Float 4 (optimal for LLMs)
    bnb_4bit_compute_dtype=torch.float16,  # Compute in FP16
    bnb_4bit_use_double_quant=True,  # Quantize quantization constants
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    quantization_config=quantization_config,
    device_map="auto",
    torch_dtype=torch.float16
)

# Memory comparison (Llama-8B):
# Full precision (FP16): ~16GB
# 8-bit quantized: ~8GB
# 4-bit quantized: ~5GB
```

### Quantization-Aware Training

Fine-tune after quantization to recover quality:

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments, Trainer

# Load quantized model
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    quantization_config=quantization_config,
    device_map="auto",
    torch_dtype=torch.float16,
    attn_implementation="flash_attention_2"  # Optional: use FlashAttention
)

# Fine-tune with QLoRA (Quantized LoRA)
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# Train
training_args = TrainingArguments(
    output_dir="./qlora-results",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    num_train_epochs=3,
    fp16=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()

# Merge adapters and save
model.merge_and_unload()
model.save_pretrained("./final-quantized-model")
```

## Model Compilation (PyTorch 2.0+)

### Basic Compilation

10-30% speedup for generation and training:

```python
from transformers import AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8b")

# Compile model (first run will be slow)
model = torch.compile(
    model,
    mode="reduce-overhead",  # Optimize for inference
    fullgraph=True  # Try to compile entire model
)

# First generation compiles the model (slow)
# Subsequent generations are fast
outputs = model.generate(**inputs, max_new_tokens=100)
```

### Compilation Modes

```python
# Reduce overhead mode (best for inference)
model = torch.compile(model, mode="reduce-overhead")

# Max autotune mode (best for training)
model = torch.compile(model, mode="max-autotune")

# Default mode
model = torch.compile(model)
```

### Compilation with Training

```python
from transformers import AutoModelForSequenceClassification, Trainer, TrainingArguments

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")

# Compile before training
model = torch.compile(model, mode="max-autotune")

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()  # Compilation happens during first epoch
```

## FlashAttention

### FlashAttention 2

20-40% faster attention, especially for long sequences:

```python
from transformers import AutoModelForCausalLM

# Load with FlashAttention 2
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    attn_implementation="flash_attention_2",  # Enable FlashAttention 2
    torch_dtype=torch.float16,
    device_map="auto"
)

# Requires:
# - Ampere+ GPU (A100, H100, RTX 30xx/40xx)
# - FlashAttention installed: pip install flash-attn --no-build-isolation
```

### Checking FlashAttention Availability

```python
from transformers.utils import is_flash_attn_2_available

if is_flash_attn_2_available():
    print("FlashAttention 2 is available")
    model = AutoModelForCausalLM.from_pretrained(
        "model-name",
        attn_implementation="flash_attention_2"
    )
else:
    print("FlashAttention 2 not available, using default")
    model = AutoModelForCausalLM.from_pretrained("model-name")
```

### FlashAttention with Different Models

```python
# Llama models
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    attn_implementation="flash_attention_2"
)

# Mistral models
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    attn_implementation="flash_attention_2"
)

# BERT models (for training)
from transformers import AutoModelForSequenceClassification
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    attn_implementation="flash_attention_2"
)
```

## Model Sharding and Device Mapping

### Automatic Device Mapping

Distribute model across multiple GPUs automatically:

```python
from transformers import AutoModelForCausalLM

# Simple automatic mapping
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    device_map="auto"  # Automatically distribute layers across GPUs
)

# Sequential mapping (one layer at a time for memory efficiency)
model = AutoModelForCausalLM.from_pretrained(
    "very-large-model",
    device_map="sequential"
)
```

### Manual Device Mapping

Fine-grained control over layer placement:

```python
from transformers import AutoModelForCausalLM

# Map specific layers to specific GPUs
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    device_map={
        "model.embed_tokens": 0,
        "model.layers.0": 0,
        "model.layers.1": 0,
        "model.layers.2": 1,
        "model.layers.3": 1,
        # ... etc
        "lm_head": 0
    }
)

# Or use a balanced distribution
from transformers import AutoModelForCausalLM
import torch

num_gpus = torch.cuda.device_count()
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    device_map="balanced"  # Balance memory usage across GPUs
)
```

### CPU Offloading

Run models larger than GPU memory:

```python
from transformers import AutoModelForCausalLM

# Offload some layers to CPU
model = AutoModelForCausalLM.from_pretrained(
    "very-large-model",
    device_map="auto",
    offload_folder="./offload",  # Temporary folder for offloaded layers
    offload_state_dict=True,
)

# Or use CPU offloading explicitly
model = AutoModelForCausalLM.from_pretrained(
    "very-large-model",
    device_map="auto",
    offload_folder="./offload",
    offload_index=50,  # Offload every 50th layer
)
```

### Disk Offloading for Inference

```python
from transformers import AutoModelForCausalLM, pipeline

# Load with disk offloading
model = AutoModelForCausalLM.from_pretrained(
    "very-large-model",
    device_map="auto",
    offload_folder="./offload",
)

# Use with pipeline
pipe = pipeline("text-generation", model=model)
result = pipe("Hello, world!", max_new_tokens=50)
```

## Deployment Patterns

### Production Pipeline Serving

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

class ModelServer:
    def __init__(self, model_name: str, device: str = "auto"):
        # Load optimized model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map=device,
            attn_implementation="flash_attention_2" if device != "cpu" else None
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
    
    def generate(self, prompt: str, max_tokens: int = 100) -> str:
        result = self.pipeline(
            prompt,
            max_new_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        return result[0]["generated_text"]

# Usage
server = ModelServer("meta-llama/Llama-3.1-8b")
response = server.generate("Explain quantum computing:")
```

### FastAPI Integration

Production-ready API with async support:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import uvicorn

app = FastAPI(title="Transformers Inference API")

# Load model at startup
model_name = "meta-llama/Llama-3.1-8b"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

class GenerationRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7
    top_p: float = 0.9

class GenerationResponse(BaseModel):
    generated_text: str

@app.post("/generate", response_model=GenerationResponse)
async def generate(request: GenerationRequest):
    try:
        inputs = tokenizer(request.prompt, return_tensors="pt")
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        generated_text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        
        return GenerationResponse(generated_text=generated_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "model": model_name}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Batch Inference Server

Handle multiple requests efficiently:

```python
from fastapi import FastAPI
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List

app = FastAPI()

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8b")

@app.post("/batch-generate")
async def batch_generate(prompts: List[str], max_tokens: int = 100):
    # Tokenize all prompts
    inputs = tokenizer(
        prompts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    )
    
    # Move to device
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    # Batch generation
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        pad_token_id=tokenizer.eos_token_id,
        temperature=0.7,
        top_p=0.9
    )
    
    # Decode results
    results = []
    for i, output in enumerate(outputs):
        generated_text = tokenizer.decode(output[inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        results.append({"prompt": prompts[i], "generated_text": generated_text})
    
    return {"results": results}
```

### Streaming API with SSE

Server-Sent Events for real-time streaming:

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.streamers import TextStreamer
import torch

app = FastAPI()

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8b")

class StreamGenerator(TextStreamer):
    def __init__(self, tokenizer):
        super().__init__(tokenizer, skip_prompt=True)
    
    def on_finalized_text(self, word: str, stream_end: bool = False):
        yield f"data: {word}\n\n"

@app.get("/stream")
async def stream_generation(prompt: str):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    streamer = StreamGenerator(tokenizer)
    
    def generate():
        model.generate(
            **inputs,
            max_new_tokens=100,
            streamer=streamer,
            temperature=0.7,
            top_p=0.9
        )
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

## Performance Monitoring

### Benchmarking Inference Speed

```python
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8b")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8b")

prompt = "Explain machine learning: "
inputs = tokenizer(prompt, return_tensors="pt")

# Warmup
_ = model.generate(**inputs, max_new_tokens=10)

# Benchmark
num_iterations = 10
times = []

for _ in range(num_iterations):
    start = time.time()
    outputs = model.generate(**inputs, max_new_tokens=100)
    end = time.time()
    times.append(end - start)

avg_time = sum(times) / num_iterations
tokens_generated = 100
tokens_per_second = tokens_generated / avg_time

print(f"Average generation time: {avg_time:.2f}s")
print(f"Tokens per second: {tokens_per_second:.2f}")
```

### Memory Profiling

```python
import torch
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8b")

# Count parameters
num_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {num_params:,}")

# Estimate memory usage (FP16)
memory_gb = (num_params * 2) / (1024**3)  # 2 bytes per FP16 param
print(f"Estimated model memory: {memory_gb:.2f} GB")

# Check actual memory usage
torch.cuda.memory_summary()
```

## Best Practices for Production

### 1. Use Quantization for Memory Efficiency

```python
# 4-bit quantization for production
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    quantization_config=quantization_config,
    device_map="auto"
)
```

### 2. Enable FlashAttention for Speed

```python
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8b",
    attn_implementation="flash_attention_2",
    torch_dtype=torch.float16,
)
```

### 3. Compile Model for Additional Speedup

```python
model = torch.compile(model, mode="reduce-overhead")
```

### 4. Use Batch Processing

```python
# Process multiple requests in batch
inputs = tokenizer(batch_prompts, padding=True, return_tensors="pt")
outputs = model.generate(**inputs, pad_token_id=tokenizer.eos_token_id)
```

### 5. Implement Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_generation(prompt: str):
    """Cache frequent prompts"""
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=50)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### 6. Monitor and Log

```python
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def inference_timer(prompt_length: int):
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        logger.info(f"Inference time: {duration:.3f}s for {prompt_length} tokens")
        tokens_per_sec = prompt_length / duration
        logger.info(f"Speed: {tokens_per_sec:.2f} tokens/s")
```

## Troubleshooting

### CUDA Out of Memory

```python
# Use quantization
quantization_config = BitsAndBytesConfig(load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained(
    "large-model",
    quantization_config=quantization_config,
    device_map="auto"
)

# Or use CPU offloading
model = AutoModelForCausalLM.from_pretrained(
    "large-model",
    device_map="auto",
    offload_folder="./offload"
)
```

### Slow Inference After Compilation

First run is slow (compilation), subsequent runs are fast:

```python
model = torch.compile(model)

# Warmup run
_ = model.generate(**inputs, max_new_tokens=10)

# Now benchmark actual performance
outputs = model.generate(**inputs, max_new_tokens=100)
```

### FlashAttention Not Available

```python
from transformers.utils import is_flash_attn_2_available

if is_flash_attn_2_available():
    model = AutoModelForCausalLM.from_pretrained(
        "model-name",
        attn_implementation="flash_attention_2"
    )
else:
    # Install FlashAttention
    # pip install flash-attn --no-build-isolation
    model = AutoModelForCausalLM.from_pretrained("model-name")
```

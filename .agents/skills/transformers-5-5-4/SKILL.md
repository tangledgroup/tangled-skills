---
name: transformers-5-5-4
description: Complete toolkit for Hugging Face Transformers 5.5.4 providing state-of-the-art pretrained models for NLP, computer vision, audio, video, and multimodal tasks with Pipeline API, Trainer, generation features, quantization, and support for 1M+ model checkpoints on the Hub. Use when building Python applications that integrate pretrained transformer models for text generation, image classification, speech recognition, chat, fine-tuning, or any task requiring access to the Hugging Face ecosystem.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - nlp
  - machine-learning
  - deep-learning
  - pytorch
  - huggingface
  - pretrained-models
  - inference
  - training
  - computer-vision
  - audio
  - multimodal
category: machine-learning
external_references:
  - https://github.com/huggingface/transformers/tree/v5.5.4/docs
  - https://huggingface.co/docs/transformers/en/index
---

# Transformers 5.5.4

## Overview

Transformers acts as the model-definition framework for state-of-the-art machine learning models across text, computer vision, audio, video, and multimodal domains — for both inference and training. It centralizes model definitions so they are compatible across the ecosystem: training frameworks (Axolotl, Unsloth, DeepSpeed, FSDP, PyTorch-Lightning), inference engines (vLLM, SGLang, TGI), and adjacent libraries (llama.cpp, mlx).

Over 1M+ model checkpoints are available on the [Hugging Face Hub](https://huggingface.co/models?library=transformers). The library supports 450+ model architectures including BERT, GPT-2, Llama, Mistral, Gemma, Whisper, CLIP, DINOv2, and many more.

Transformers works with Python 3.10+ and PyTorch 2.4+.

## When to Use

- Loading pretrained models for text generation, classification, question answering, or any NLP task
- Running inference on computer vision models (image classification, object detection, segmentation)
- Processing audio with automatic speech recognition or audio classification
- Building multimodal applications combining text, images, and audio
- Fine-tuning large language models with the Trainer API
- Optimizing inference with quantization, caching, compilation, or parallelism
- Chatting with LLMs using chat templates
- Deploying models to production with serialization and export

## Core Concepts

Transformers is built around three core abstractions:

**Configuration** (`PreTrainedConfig`) — Specifies model attributes like number of hidden layers, vocabulary size, activation function, and attention heads. Each architecture has its own config class.

**Model** (`PreTrainedModel`) — The neural network defined by the configuration. Models come as barebones (returning hidden states) or with task-specific heads attached (e.g., `LlamaForCausalLM` for text generation vs `LlamaModel` for raw outputs). Use `from_pretrained()` to load weights from the Hub or a local directory.

**Preprocessor** — Converts raw inputs into tensors the model can process. Tokenizers handle text, image processors handle images, feature extractors handle audio, and processors combine multiple modalities.

Every pretrained model inherits from these three base classes, enabling a unified API across all architectures.

## Installation / Setup

Install Transformers with pip or uv:

```bash
pip install transformers
# or
uv pip install transformers
```

For GPU acceleration, install PyTorch with CUDA support:

```bash
pip install torch
```

Test the installation:

```python
from transformers import pipeline
print(pipeline('sentiment-analysis')('hugging face is the best'))
# [{'label': 'POSITIVE', 'score': 0.9998704791069031}]
```

### Cache Directory

Models downloaded from the Hub are cached locally. Default location: `~/.cache/huggingface/hub`. Override with environment variables (by priority):

- `HF_HUB_CACHE` (default)
- `HF_HOME`
- `XDG_CACHE_HOME` + `/huggingface`

### Offline Mode

Set `HF_HUB_OFFLINE=1` to prevent HTTP calls, or use `local_files_only=True` in `from_pretrained()`.

## Usage Examples

### Quick Inference with Pipeline

The `pipeline()` function is the simplest way to run inference:

```python
from transformers import pipeline

# Text generation
gen = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B")
gen("the secret to baking a good cake is ")

# Sentiment analysis
sentiment = pipeline("sentiment-analysis")
sentiment("This movie was amazing!")

# Image classification
classify = pipeline("image-classification", model="facebook/dinov2-small-imagenet1k-1-layer")
classify("https://huggingface.co/datasets/Narsil/image_dummy/raw/main/parrots.png")

# Automatic speech recognition
asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")
asr("https://huggingface.co/datasets/Narsil/asr_dummy/resolve/main/mlk.flac")
```

### Loading Models Manually

Use AutoClasses to load models without knowing the exact architecture:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

inputs = tokenizer(["The secret to baking a good cake is "], return_tensors="pt").to(model.device)
generated_ids = model.generate(**inputs, max_new_tokens=30)
print(tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0])
```

Key loading parameters:

- `device_map="auto"` — Automatically distributes model weights across available devices (GPU first)
- `dtype="auto"` — Loads weights in their native precision (avoids double-loading in float32)

### Chat with LLMs

Use chat templates to format conversations correctly:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("HuggingFaceH4/zephyr-7b-beta")
model = AutoModelForCausalLM.from_pretrained(
    "HuggingFaceH4/zephyr-7b-beta",
    device_map="auto",
    dtype=torch.bfloat16
)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing in one sentence."},
]

tokenized_chat = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt"
)

outputs = model.generate(tokenized_chat, max_new_tokens=128)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Fine-tuning with Trainer

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from transformers import DataCollatorForLanguageModeling
from datasets import load_dataset

model_name = "Qwen/Qwen3-0.6B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, dtype="auto")

dataset = load_dataset("karthiksagarn/astro_horoscope", split="train")

def tokenize(batch):
    return tokenizer(batch["horoscope"], truncation=True, max_length=512)

dataset = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)
dataset = dataset.train_test_split(test_size=0.1)

training_args = TrainingArguments(
    output_dir="qwen3-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    gradient_checkpointing=True,
    bf16=True,
    learning_rate=2e-5,
    logging_steps=10,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    processing_class=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

trainer.train()
trainer.push_to_hub()
```

## Advanced Topics

**Models and AutoClasses**: Loading strategies, sharded checkpoints, Big Model Inference, device mapping, data types → [Models](reference/01-models.md)

**Tokenizers and Preprocessors**: Fast tokenizers, encoding/decoding, batch processing, special tokens, chat templates, image/video processors → [Tokenizers](reference/02-tokenizers.md)

**Text Generation**: The generate API, decoding strategies (greedy, sampling, beam search), streaming, watermarking, generation configuration → [Text Generation](reference/03-text-generation.md)

**Training and Fine-tuning**: Trainer API, TrainingArguments, data collators, callbacks, distributed training, PEFT → [Training](reference/04-training.md)

**Inference Optimization**: Quantization (bitsandbytes, GPTQ, AWQ, GGUF), attention backends, KV caching, torch.compile, continuous batching, tensor parallelism → [Optimization](reference/05-optimization.md)

**Pipeline API**: Task-specific pipelines, batching, FP16 inference, custom pipelines, streaming → [Pipelines](reference/06-pipelines.md)

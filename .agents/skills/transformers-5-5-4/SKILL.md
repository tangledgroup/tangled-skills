---
name: transformers-5-5-4
description: Complete toolkit for Hugging Face Transformers 5.5.4 providing state-of-the-art pretrained models for NLP, computer vision, audio, video, and multimodal tasks with Pipeline API, Trainer, generation features, and support for 1M+ model checkpoints on the Hub.
license: MIT
author: Tangled Skills
version: "1.0.0"
tags:
  - nlp
  - machine-learning
  - deep-learning
  - pytorch
  - huggingface
  - pretrained-models
  - inference
  - training
category: machine-learning
external_references:
  - https://github.com/huggingface/transformers/tree/v5.5.4/docs
  - https://huggingface.co/docs/transformers/en/index
---

# Transformers 5.5.4

<h3 align="center">
    State-of-the-art Machine Learning for Text, Vision, Audio, and Multimodal Models
</h3>

Transformers is the model-definition framework for state-of-the-art machine learning models across text, computer vision, audio, video, and multimodal domains. It centralizes model definitions to ensure compatibility across the ecosystem including training frameworks (Axolotl, Unsloth, DeepSpeed, FSDP), inference engines (vLLM, SGLang, TGI), and adjacent libraries (llama.cpp, mlx).

With **1M+ pretrained model checkpoints** on the [Hugging Face Hub](https://huggingface.co/models), Transformers provides everything needed for inference and training with cutting-edge models.

## Overview

Transformers acts as the pivot across frameworks: if a model definition is supported, it will be compatible with the majority of training frameworks, inference engines, and modeling libraries that leverage the model definition from `transformers`.

### Key Features

- **Pipeline API**: Simple and optimized inference for 50+ tasks including text generation, image segmentation, speech recognition, document QA
- **Trainer**: Comprehensive training with mixed precision, `torch.compile`, FlashAttention, and distributed training
- **Generation API**: Fast text generation with LLMs and VLMs, streaming, and multiple decoding strategies
- **1M+ Models**: Access to pretrained models on the Hugging Face Hub
- **Multi-framework**: PyTorch support with Python 3.10+ and PyTorch 2.4+

### Design Principles

1. **Fast and easy to use**: Every model implements three main classes (configuration, model, preprocessor) for quick inference/training
2. **Pretrained models**: Reduce carbon footprint, compute cost, and time by using pretrained models with state-of-the-art performance

## When to Use

Use Transformers 5.5.4 when:

- **Inference tasks**: Text classification, generation, QA, summarization, translation, named entity recognition
- **Vision tasks**: Image classification, object detection, segmentation, depth estimation
- **Audio tasks**: Speech recognition, audio classification, speaker verification
- **Multimodal tasks**: Vision-language models, document understanding, image captioning
- **Training/fine-tuning**: Adapt pretrained models to custom datasets with Trainer or custom loops
- **Production deployment**: Optimize models with quantization, compilation, and efficient inference
- **Research**: Experiment with cutting-edge architectures (Llama, Mistral, Qwen, CLIP, Whisper, etc.)

## Installation

### Quick Start with uv

```bash
# Create virtual environment
uv venv .env
source .env/bin/activate

# Install Transformers
uv pip install transformers
```

### GPU Acceleration

For CUDA-enabled GPUs:

```bash
# Check GPU availability
nvidia-smi

# Install PyTorch with CUDA support (follow https://pytorch.org/get-started/locally/)
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install Transformers
uv pip install transformers
```

### CPU-Only Installation

```bash
uv pip install torch --index-url https://download.pytorch.org/whl/cpu
uv pip install transformers
```

### Test Installation

```bash
python -c "from transformers import pipeline; print(pipeline('sentiment-analysis')('hugging face is the best'))"
# [{'label': 'POSITIVE', 'score': 0.9998704791069031}]
```

### Install from Source (Latest)

```bash
uv pip install git+https://github.com/huggingface/transformers
```

### Editable Install (Development)

```bash
git clone https://github.com/huggingface/transformers.git
cd transformers
uv pip install -e .
```

## Quick Start

### Using Pipeline API

The simplest way to use Transformers:

```python
from transformers import pipeline

# Text classification
classifier = pipeline("sentiment-analysis")
result = classifier("I love using Transformers!")
# [{'label': 'POSITIVE', 'score': 0.9998}]

# Question answering
qa = pipeline("question-answering")
result = qa(
    question="What's my name?",
    context="My name is Sarah and I work at Hugging Face"
)
# {'answer': 'Sarah', 'score': 0.9998}

# Text generation
generator = pipeline("text-generation", model="meta-llama/Llama-3.1-8b")
result = generator("Once upon a time", max_length=50)
```

### Using Specific Models

```python
from transformers import pipeline

# Use a specific model from the Hub
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
result = classifier(
    ["I love this product!", "This is terrible"],
    ["positive", "negative"]
)

# Load with custom configuration
generator = pipeline(
    "text-generation",
    model="mistralai/Mistral-7B-v0.1",
    device=0,  # GPU
    tokenizer_kwargs={"padding_side": "left"}
)
```

### Working with Models Directly

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# Load model and tokenizer
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Tokenize input
inputs = tokenizer("I love this!", return_tensors="pt")

# Run inference
with torch.no_grad():
    outputs = model(**inputs)
    probabilities = torch.softmax(outputs.logits, dim=-1)

print(probabilities)
```

## Core Concepts

### Model Architecture Pattern

Every model in Transformers follows a consistent three-class pattern:

1. **Configuration** (`{Model}Config`): Stores hyperparameters and architecture settings
2. **Model** (`{Model}For{Task}`): The neural network implementation
3. **Preprocessor** (Tokenizer/FeatureExtractor/ImageProcessor): Converts raw input to model format

```python
from transformers import AutoConfig, AutoModel, AutoTokenizer

# 1. Load configuration
config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=3)

# 2. Load model with config
model = AutoModel.from_pretrained("bert-base-uncased", config=config)

# 3. Load preprocessor
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
```

### The Hub Integration

Transformers integrates seamlessly with the Hugging Face Hub:

```python
from transformers import AutoModelFromPretrained

# Download and cache automatically
model = AutoModel.from_pretrained("bert-base-uncased")

# Use local files only (offline mode)
model = AutoModel.from_pretrained("./local/path", local_files_only=True)

# Load from specific revision
model = AutoModel.from_pretrained("bert-base-uncased", revision="main")

# Use environment variables for cache location
# HF_HUB_CACHE, HF_HOME, or XDG_CACHE_HOME
```

### Device Management

```python
from transformers import pipeline

# Automatic device placement (GPU if available)
pipe = pipeline("sentiment-analysis")

# Force CPU
pipe = pipeline("sentiment-analysis", device=-1)

# Force GPU
pipe = pipeline("sentiment-analysis", device=0)

# Multiple GPUs with model parallelism
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("large-model")
model = model.half().cuda(0)
```

## Reference Files

For detailed coverage of specific topics, see:

### Core Functionality

- [`references/01-pipeline-api.md`](references/01-pipeline-api.md) - Complete Pipeline API guide with 50+ task types, batching, streaming, and customization
- [`references/02-models-and-tokenizers.md`](references/02-models-and-tokenizers.md) - Model loading, tokenizer patterns, auto classes, and configuration management
- [`references/03-generation-api.md`](references/03-generation-api.md) - Text generation with LLMs, decoding strategies, streaming, and advanced features

### Training and Optimization

- [`references/04-training-with-trainer.md`](references/04-training-with-trainer.md) - Trainer API, custom training loops, distributed training, and mixed precision
- [`references/05-optimization-and-deployment.md`](references/05-optimization-and-deployment.md) - Quantization, torch.compile, FlashAttention, model sharding, and deployment patterns

### Advanced Topics

- [`references/06-custom-models-and-pipelines.md`](references/06-custom-models-and-pipelines.md) - Creating custom models, pipelines, and integrating with external frameworks
- [`references/07-multimodal-and-specialized-tasks.md`](references/07-multimodal-and-specialized-tasks.md) - Vision, audio, multimodal models, and specialized task implementations

## Common Patterns

### Batch Processing

```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis")

# Process multiple inputs
results = classifier([
    "I love this!",
    "This is terrible",
    "It's okay"
])

# Batch processing with streaming
for result in classifier(
    ["text 1", "text 2", "text 3"],
    batch_size=8,
    truncation=True
):
    print(result)
```

### Zero-Shot Classification

```python
from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

result = classifier(
    sequence="I bought a new car and love it",
    candidate_labels=["vehicle review", "food review", "travel blog"]
)
# {'sequence': '...', 'labels': ['vehicle review', ...], 'scores': [0.92, ...]}
```

### Conversational AI

```python
from transformers import pipeline

chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")

conversation = chatbot(
    [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"}
    ],
    text="What do you like to do?"
)
```

### Model Saving and Loading

```python
from transformers import AutoModel, AutoTokenizer

# Save to local directory
model.save_pretrained("./my-model")
tokenizer.save_pretrained("./my-model")

# Load from local directory
model = AutoModel.from_pretrained("./my-model")
tokenizer = AutoTokenizer.from_pretrained("./my-model")

# Push to Hub
model.push_to_hub("username/my-model")
tokenizer.push_to_hub("username/my-model")
```

## Troubleshooting

### Common Issues

**Memory errors with large models:**
```python
# Use quantization
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "large-model",
    load_in_8bit=True,
    device_map="auto"
)
```

**Slow inference:**
```python
# Enable batching and GPU
pipe = pipeline("text-generation", device=0)
results = pipe(["prompt 1", "prompt 2"], batch_size=4)

# Use torch.compile (PyTorch 2.0+)
model = model.compile()
```

**Token limit exceeded:**
```python
# Adjust truncation
tokenizer(text, truncation=True, max_length=512)

# Or use sliding window for long documents
from transformers import TruncationStrategy
tokenizer(text, truncation=TruncationStrategy.LONGEST_FIRST, max_length=512)
```

### Environment Variables

```bash
# Cache directory
export HF_HUB_CACHE=/path/to/cache

# Offline mode
export HF_HUB_OFFLINE=1

# Disable telemetry
export HF_DISABLED_TELEMETRY=1

# Authentication token
export HUGGING_FACE_HUB_TOKEN=your_token
```

## Performance Tips

1. **Use batching** for multiple inputs to maximize GPU utilization
2. **Enable quantization** (8-bit/4-bit) to reduce memory usage by 50-75%
3. **Use `device_map="auto"`** for automatic multi-GPU distribution
4. **Compile models** with `torch.compile()` for 10-30% speedup
5. **Stream generation** for interactive applications
6. **Cache tokenizers** to avoid reprocessing common inputs

## Resources

### Official Documentation

- [Transformers Documentation](https://huggingface.co/docs/transformers)
- [Model Documentation](https://huggingface.co/docs/transformers/model_doc)
- [Pipeline Tutorial](https://huggingface.co/docs/transformers/main/en/pipeline_tutorial)
- [LLM Tutorial](https://huggingface.co/docs/transformers/main/en/llm_tutorial)

### Learning Resources

- [Hugging Face LLM Course](https://huggingface.co/learn/llm-course) - Comprehensive course on transformer models
- [Transformers Course](https://huggingface.co/learn/nlp-course) - NLP fundamentals with Transformers
- [Hub Documentation](https://huggingface.co/docs/hub) - Working with the Hugging Face Hub

### Community

- [GitHub Discussions](https://github.com/huggingface/transformers/discussions)
- [Hugging Face Forums](https://discuss.huggingface.co/)
- [Slack Community](https://huggingface.co/slack)

## Version Information

- **Version**: 5.5.4
- **Python**: 3.10+
- **PyTorch**: 2.4+
- **License**: Apache 2.0
- **Repository**: https://github.com/huggingface/transformers

## See Also

Related skills in this repository:
- `peft` - Parameter-efficient fine-tuning
- `accelerate` - Distributed training and mixed precision
- `datasets` - Working with datasets
- `evaluate` - Model evaluation metrics
- `sentence-transformers` - Sentence embeddings

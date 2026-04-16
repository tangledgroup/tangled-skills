# Qwen3-VL-Reranker Model Architecture

This reference document provides detailed technical specifications and architectural insights into the Qwen3-VL-Reranker model series.

## Overview

Qwen3-VL-Reranker is built upon the Qwen3-VL foundation model, fine-tuned specifically for multimodal reranking tasks. The architecture uses a **single-tower design with cross-attention mechanisms** to compute precise relevance scores between query-document pairs.

## Model Specifications

### Qwen3-VL-Reranker-2B

| Parameter | Value |
|-----------|-------|
| Base Model | Qwen3-VL-2B-Instruct |
| Parameters | 2 Billion |
| Layers | 28 |
| Hidden Size | 2560 |
| Attention Heads | 20 |
| Feedforward Dimension | 6400 |
| Context Length | 32K tokens |
| Vocabulary Size | 152,064 |

### Qwen3-VL-Reranker-8B

| Parameter | Value |
|-----------|-------|
| Base Model | Qwen3-VL-8B-Instruct |
| Parameters | 8 Billion |
| Layers | 36 |
| Hidden Size | 5120 |
| Attention Heads | 40 |
| Feedforward Dimension | 13,824 |
| Context Length | 32K tokens |
| Vocabulary Size | 152,064 |

## Single-Tower Architecture

### Key Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Query-Document Pair                       │
│                  (concatenated input)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │   Qwen3-VL Encoder        │
        │   - Vision Encoder        │
        │   - Language Model        │
        │   - Cross-Attention       │
        └──────────────┬───────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │   Classification Head     │
        │   - Pooling Layer         │
        │   - Scoring Output        │
        └──────────────┬───────────┘
                       │
                       ▼
                Relevance Score
                   (0.0 - 1.0)
```

### Cross-Attention Mechanism

Unlike dual-tower embedding models that produce independent vectors, the reranker uses cross-attention to model interactions between query and document:

1. **Input Concatenation**: Query and document are concatenated into a single sequence
2. **Joint Encoding**: Both parts are processed together through transformer layers
3. **Cross-Attention**: Attention mechanisms allow tokens from query to attend to tokens from document and vice versa
4. **Pooling**: Special token (e.g., `[EOS]` or dedicated pooling token) aggregates joint representation
5. **Classification Head**: Final layer outputs relevance score

### Mathematical Formulation

Given a query `q` and document `d`:

```
x = concatenate(q, d)  # Input sequence
h = Transformer(x)     # Joint encoding with cross-attention
h_pooled = Pool(h)     # Extract pooled representation
score = σ(MLP(h_pooled))  # Sigmoid activation for 0-1 score
```

Where:
- `σ` is the sigmoid function
- Score ranges from 0.0 (irrelevant) to 1.0 (highly relevant)

## Comparison: Single-Tower vs Dual-Tower

| Aspect | Single-Tower (Reranker) | Dual-Tower (Embedding) |
|--------|-------------------------|------------------------|
| **Input** | Query-document pair | Single input (query OR document) |
| **Attention** | Cross-attention between query and doc | Independent encoding |
| **Output** | Relevance score | Embedding vector |
| **Computation** | O(n × m) for n queries, m docs | O(n + m) for independent encoding |
| **Use Case** | Precise re-ranking of top-k | Fast retrieval across large corpus |
| **Accuracy** | Higher (models interactions) | Lower (independent vectors) |
| **Latency** | Higher (joint processing) | Lower (parallelizable) |

### When to Use Each

**Use Dual-Tower (Embedding) for:**
- Initial recall from large corpora (10K+ documents)
- Real-time search with strict latency requirements
- Pre-computable document embeddings
- Approximate nearest neighbor (ANN) search

**Use Single-Tower (Reranker) for:**
- Re-ranking top-k candidates (typically 50-500)
- Precision-critical applications
- Complex multimodal matching tasks
- Scenarios where query-document interaction matters

## Vision-Language Integration

### Multi-Modal Input Processing

The model handles various input modalities through a unified processing pipeline:

#### Text Inputs
```python
{"text": "A woman playing with her dog on a beach."}
```
- Tokenized using Qwen3 tokenizer
- Converted to token embeddings
- Processed through language model layers

#### Image Inputs
```python
{"image": "path/to/image.jpg"}
```
- Resized and patched (e.g., 14x14 or 14x14 patches)
- Encoded through vision encoder (ViT-based)
- Projected to language model embedding space
- Special tokens (`<|vision_start|>`, `<|vision_end|>`) mark image regions

#### Video Inputs
```python
{"video": "path/to/video.mp4", "fps": 1.0}
```
- Sampled at specified frame rate (e.g., 1 fps)
- Each frame processed as image input
- Temporal information preserved through sequence ordering
- Maximum frame limit enforced (default: 64 frames)

#### Mixed Modalities
```python
{
    "text": "A woman playing with her dog",
    "image": "beach_scene.jpg"
}
```
- Text and visual tokens interleaved in sequence
- Cross-modal attention enables joint understanding
- Special tokens demarcate modality boundaries

## Chat Template

The model uses a specialized chat template for reranking tasks:

```jinja
{%- if messages[0].role == 'system' %}
    {%- if messages[0].content is string %}
        {{- messages[0].content }}
    {%- else %}
        {%- for content in messages[0].content %}
            {%- if 'text' in content %}
                {{- content.text }}
            {%- endif %}
        {%- endfor %}
    {%- endif %}
    {{- '\n\n' }}
{%- endif %}
{%- for message in messages %}
    {%- if message.role == "user" %}
        {{- '' + message.role + '\n' }}
        {%- if message.content is string %}
            {{- message.content }}
        {%- else %}
            {%- for content in message.content %}
                {%- if content.type == 'image' or 'image' in content %}
                    {%- if add_vision_id %}Picture {{ image_count.value }}: {% endif -%}
                     {{- '<|vision_start|>' + content.image + '<|vision_end|>\n' }}
                {%- elif 'text' in content %}
                    {{- content.text }}
                {%- endif %}
            {%- endfor %}
        {%- endif %}
        {{- '\n</think>\n' }}
    {%- elif message.role == "assistant" %}
        {{- '' + message.role + '\n' }}
        {%- if message.content is string %}
            {{- message.content }}
        {%- else %}
            {%- for content_item in message.content %}
                {%- if 'text' in content_item %}
                    {{- content_item.text }}
                {%- endif %}
            {%- endfor %}
        {%- endif %}
        {{- '\n</think>\n' }}
    {%- endif %}
{%- endfor %}
```

## Configuration Files

### config.json

```json
{
  "architectures": ["Qwen3VLForConditionalGeneration"],
  "model_type": "qwen3_vl",
  "hidden_size": 2560,
  "num_hidden_layers": 28,
  "num_attention_heads": 20,
  "intermediate_size": 6400,
  "max_position_embeddings": 32768,
  "vocab_size": 152064,
  "tokenizer_config": {
    "bos_token": null,
    "eos_token": "</s>",
    "pad_token": "</s>",
    "unk_token": null
  }
}
```

### Special Configuration for Reranking

When using vLLM or other inference frameworks, special overrides are needed:

```python
hf_overrides = {
    "architectures": ["Qwen3VLForSequenceClassification"],
    "classifier_from_token": ["no", "yes"],
    "is_original_qwen3_reranker": True,
}
```

## Training Details

### Fine-tuning Approach

The reranker is fine-tuned from Qwen3-VL-Instruct base models using:

1. **Contrastive Learning**: Positive (relevant) and negative (irrelevant) query-document pairs
2. **Pointwise Supervision**: Direct relevance score regression with labeled data
3. **Pairwise Ranking**: Preference optimization between document pairs

### Data Sources

Training data includes:
- Multimodal retrieval datasets (MMEB-V2, MMTEB)
- Visual document retrieval (JinaVDR, ViDoRe)
- Image-text matching datasets
- Video-text pairing datasets
- Synthetic query-document pairs

### Loss Functions

Primary loss functions used during training:

**Pointwise MSE Loss:**
```
L_pointwise = Σ (score_pred - score_gold)²
```

**Pairwise Hinge Loss:**
```
L_pairwise = max(0, margin - score_positive + score_negative)
```

**Listwise ListNet Loss:**
```
P(y|x) = softmax([score_1, score_2, ..., score_n])
L_listwise = -Σ y_i * log(P_i)
```

## Hardware Requirements

### Inference Memory Usage

| Model | Precision | GPU Memory (batch=1) | GPU Memory (batch=32) |
|-------|-----------|---------------------|----------------------|
| 2B    | FP16      | ~5 GB               | ~8 GB                |
| 2B    | BF16      | ~5 GB               | ~8 GB                |
| 2B    | FP4       | ~2 GB               | ~4 GB                |
| 8B    | FP16      | ~16 GB              | ~24 GB               |
| 8B    | BF16      | ~16 GB              | ~24 GB               |
| 8B    | FP4       | ~6 GB               | ~10 GB               |

### Recommended Hardware

**For 2B Model:**
- Minimum: GPU with 8GB VRAM (e.g., RTX 3070, T4)
- Recommended: GPU with 16GB VRAM (e.g., RTX 3080, A10)

**For 8B Model:**
- Minimum: GPU with 16GB VRAM (e.g., RTX 3090, A100 24GB)
- Recommended: GPU with 24GB+ VRAM (e.g., RTX 4090, A100 40GB)

## Quantization Support

The model supports various quantization schemes:

### Static Quantization

| Precision | Memory Reduction | Accuracy Impact | Use Case |
|-----------|-----------------|-----------------|----------|
| FP16      | 2x vs FP32      | None            | Default  |
| INT8      | 4x vs FP32      | ~1-2%           | Production |
| FP4       | 8x vs FP32      | ~2-3%           | Edge deployment |
| INT4      | 8x vs FP32      | ~3-5%           | Resource-constrained |

### Implementation

```python
# Using transformers with bitsandbytes
import torch
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained(
    "Qwen/Qwen3-VL-Reranker-2B",
    torch_dtype=torch.float16,
    load_in_8bit=True,  # or load_in_4bit=True
    device_map="auto"
)
```

## Performance Characteristics

### Latency (Single GPU, Batch Size = 1)

| Model | Precision | Text-Only | Text+Image | Video (30 frames) |
|-------|-----------|-----------|------------|-------------------|
| 2B    | BF16      | ~50ms     | ~150ms     | ~800ms            |
| 2B    | FP4       | ~30ms     | ~100ms     | ~500ms            |
| 8B    | BF16      | ~150ms    | ~400ms     | ~2000ms           |
| 8B    | FP4       | ~80ms     | ~250ms     | ~1200ms           |

*Measured on NVIDIA A100 with Flash Attention 2 enabled*

### Throughput (Single GPU)

| Model | Precision | Batch Size | Queries/sec (text) | Queries/sec (multimodal) |
|-------|-----------|------------|-------------------|-------------------------|
| 2B    | BF16      | 32         | ~400              | ~150                    |
| 2B    | FP4       | 32         | ~600              | ~250                    |
| 8B    | BF16      | 32         | ~150              | ~60                     |
| 8B    | FP4       | 32         | ~250              | ~120                    |

## Best Practices for Deployment

1. **Use Flash Attention 2**: Enable with `attn_implementation="flash_attention_2"` for 2-3x speedup
2. **Choose appropriate precision**: BF16 for best accuracy, FP4/INT4 for memory-constrained scenarios
3. **Batch similar queries**: Group text-only and multimodal queries separately for optimal performance
4. **Cache vision encodings**: Pre-compute image/video embeddings for static documents
5. **Monitor GPU utilization**: Adjust batch size to maintain >80% GPU utilization
6. **Use model parallelism**: For 8B model on multiple GPUs, use tensor parallelism

## Limitations

- **Context Length**: Maximum 32K tokens; very long documents may need truncation
- **Video Frames**: Default max 64 frames; longer videos lose temporal information
- **Multilingual Performance**: Best in English; 30+ languages supported but with varying quality
- **Real-time Constraints**: Not suitable for millisecond-latency requirements on large corpora

## Future Improvements

Planned enhancements in future versions:
- Longer context support (128K+)
- Improved video temporal modeling
- Enhanced multilingual capabilities
- Distilled variants for edge deployment
- Streaming inference support

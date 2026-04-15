# Qwen3-VL-Embedding Model Architecture

## Technical Specifications

### Model Variants

| Model | Size | Layers | Sequence Length | Embedding Dimension | Quantization | MRL Support | Instruction Aware |
|-------|------|--------|-----------------|---------------------|--------------|-------------|-------------------|
| Qwen3-VL-Embedding-2B | 2B | 28 | 32K | 2048 | Yes | Yes (64-2048) | Yes |
| Qwen3-VL-Embedding-8B | 8B | 36 | 32K | 4096 | Yes | Yes (64-4096) | Yes |

### Base Models

- **Qwen3-VL-Embedding-2B**: Built on `Qwen/Qwen3-VL-2B-Instruct`
- **Qwen3-VL-Embedding-8B**: Built on `Qwen/Qwen3-VL-8B-Instruct`

## Architecture Design

### Dual-Tower Architecture (Embedding Model)

The Qwen3-VL-Embedding model uses a **dual-tower architecture** designed for efficient retrieval:

```
Input (text/image/video) → Qwen3-VL Backbone → [EOS] Token Hidden State → Projection Layer → Embedding Vector
```

**Key characteristics:**

1. **Independent Encoding**: Each input is encoded independently, enabling efficient large-scale retrieval
2. **EOS Token Extraction**: The hidden state at the `[EOS]` token from the last layer serves as the semantic representation
3. **Projection Layer**: LoRA-adapted projection maps the hidden state to the target embedding dimension
4. **No Cross-Attention**: Unlike the reranker, embeddings are computed without cross-modal interaction

### Comparison with Reranker Architecture

| Aspect | Embedding Model | Reranker Model |
|--------|-----------------|----------------|
| **Architecture** | Dual-Tower | Single-Tower |
| **Input** | Single item (text/image/video) | Pair (query, document) |
| **Mechanism** | Independent encoding | Cross-attention fusion |
| **Output** | Semantic vector | Relevance score |
| **Use Case** | Initial recall (fast) | Re-ranking (precise) |
| **Complexity** | O(n) for n items | O(n×m) for n queries × m documents |

## LoRA Configuration

Both embedding and reranker models use LoRA (Low-Rank Adaptation) for efficient fine-tuning:

| Parameter | Value |
|-----------|-------|
| **Rank** | 32 |
| **Alpha** | 32 |
| **Target Modules** | q_proj, v_proj, k_proj, up_proj, down_proj, gate_proj |

### LoRA Target Modules Explained

- **q_proj, k_proj, v_proj**: Query, key, and value projections in attention layers
- **up_proj, down_proj**: MLP up-projection and down-projection layers
- **gate_proj**: Gating mechanism in feed-forward networks

This configuration adapts approximately 10-15% of model parameters while maintaining full model capabilities.

## Input Processing Pipeline

### Text Processing

```
Raw Text → Tokenizer → Token IDs + Attention Mask → Model → Hidden States
```

- **Tokenizer**: Qwen2.5 tokenizer with 151,936 vocabulary size
- **Special Tokens**: `<|im_start|>`, `<|im_end|>`, `<|endoftext|>`
- **Max Length**: 32,768 tokens (configurable via `max_length` parameter)

### Image Processing

```
Image → Resize/Pad → Patch Extraction → Vision Encoder → Image Embeddings → Language Model
```

**Pixel constraints:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_pixels` | 4,096 | Minimum image resolution (e.g., 64×64) |
| `max_pixels` | 1,843,200 | Maximum per-image resolution (e.g., 1280×1440) |
| `total_pixels` | 7,864,320 | Maximum total pixels for videos (×2 in model) |

**Example calculations:**

- Single image max: 1280×1440 = 1,843,200 pixels
- 16-frame video: 7,864,320 / 16 = 491,520 pixels per frame (e.g., 800×614)
- 64-frame video: 7,864,320 / 64 = 122,880 pixels per frame (e.g., 480×256)

### Video Processing

```
Video File → Frame Sampling (fps, max_frames) → Per-Frame Processing → Temporal Aggregation → Model
```

**Sampling parameters:**

- **fps**: Frames per second (default: 1.0)
- **max_frames**: Maximum frames to sample (default: 64)

**Example:** A 120-second video with `fps=1.0` and `max_frames=64`:
- Total frames at 1 fps: 120 frames
- After max_frames limit: 64 frames (uniformly sampled)
- Effective sampling: 1 frame every ~1.875 seconds

## Chat Template

The model uses a chat template for instruction-aware embeddings:

```jinja
{%- set default_system_message = "Represent the user's input." -%}
{%- if messages[0].role == 'system' %}
    {{- '<|im_start|>system\n' }}
    {{- messages[0].content }}
    {{- '\n\n' }}
{%- else %}
    {{- '<|im_start|>system\n' + default_system_message + '<|im_end|>\n' }}
{%- endif %}
{{- '<|im_start|>user\n' }}
{{- messages[1].content }}
{{- '<|im_end|>\n' }}
{{- '<|im_start|>assistant\n' }}
```

**Example formatted input:**

```
<|im_start|>system
Retrieve images or text relevant to the user's query.<|im_end|>
<|im_start|>user
A woman playing with her dog on a beach at sunset.<|im_end|>
<|im_start|>assistant
```

## Embedding Dimension Details

### Matryoshka Representation Learning (MRL)

MRL enables embeddings to be truncated to different dimensions while preserving semantic quality:

**Supported dimensions:**
- **Qwen3-VL-Embedding-2B**: 64, 128, 256, 512, 1024, 2048
- **Qwen3-VL-Embedding-8B**: 64, 128, 256, 512, 1024, 2048, 4096

**Performance vs. Dimension trade-off:**

| Dimension | Storage (bytes/item) | Retrieval Speed | Quality Retention |
|-----------|---------------------|-----------------|-------------------|
| 64 | 256 B (FP32) | Fastest | ~85% |
| 128 | 512 B | Very Fast | ~92% |
| 256 | 1 KB | Fast | ~96% |
| 512 | 2 KB | Fast | ~98% |
| 1024 | 4 KB | Moderate | ~99% |
| 2048/4096 | 8-16 KB | Baseline | 100% |

**Usage recommendation:**
- **Initial recall**: Use 256-512 dimensions for fast filtering
- **Re-ranking**: Use 1024-2048 dimensions for precision
- **Storage-constrained**: Use 128-256 dimensions with acceptable quality loss

## Quantization Support

The model supports post-training quantization for memory-efficient deployment:

| Precision | Memory Reduction | Speedup | Quality Loss |
|-----------|-----------------|---------|--------------|
| FP16 | 50% | 1.2-1.5x | Negligible |
| INT8 | 75% | 1.5-2x | <1% |
| FP4 | 75% | 2-3x | 1-2% |

**Recommended quantization by use case:**
- **Development**: BF16 (full precision)
- **Production API**: FP16 (balanced)
- **Edge deployment**: INT8 or FP4 (memory-constrained)

## Hardware Requirements

### Minimum Requirements

| Model | GPU Memory (FP16) | GPU Memory (INT8) | CPU Memory |
|-------|-------------------|-------------------|------------|
| 2B | ~6 GB | ~4 GB | ~16 GB |
| 8B | ~16 GB | ~8 GB | ~32 GB |

### Recommended Hardware

- **2B Model**: NVIDIA RTX 3060 (12GB) or better
- **8B Model**: NVIDIA RTX 3090/4090 (24GB) or A100 (40GB)
- **Batch Processing**: Multiple GPUs with NVLink for large batches

### Inference Performance (Single GPU)

| Model | Precision | Batch Size | Latency (ms) | Throughput (items/s) |
|-------|-----------|------------|--------------|---------------------|
| 2B | BF16 | 1 | ~50 | ~20 |
| 2B | BF16 | 32 | ~80 | ~400 |
| 8B | BF16 | 1 | ~150 | ~7 |
| 8B | BF16 | 32 | ~200 | ~160 |

*Measured on NVIDIA A100 with Flash Attention 2 enabled*

## Memory Optimization Techniques

### Gradient Checkpointing

For fine-tuning or memory-constrained environments:

```python
model = Qwen3VLEmbedder(
    model_name_or_path="Qwen/Qwen3-VL-Embedding-8B",
    use_gradient_checkpointing=True
)
```

### CPU Offloading

Use `device_map="auto"` for automatic layer offloading:

```python
from transformers import AutoModelForImageTextToText

model = AutoModelForImageTextToText.from_pretrained(
    "Qwen/Qwen3-VL-Embedding-8B",
    device_map="auto",  # Automatically distributes layers across CPU/GPU
    torch_dtype=torch.float16
)
```

### Batch Size Tuning

Find optimal batch size for your hardware:

```python
def find_optimal_batch_size(model, max_memory_gb=20):
    """Binary search for largest batch size that fits in memory."""
    low, high = 1, 256
    while low < high:
        mid = (low + high + 1) // 2
        # Test with dummy input
        try:
            dummy_input = [{"text": "test"}] * mid
            _ = model.process(dummy_input)
            low = mid
        except RuntimeError as e:
            if "out of memory" in str(e):
                high = mid - 1
            else:
                raise
    return low
```

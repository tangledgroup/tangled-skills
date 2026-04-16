# Transformers API Reference

## Installation

```bash
# Clone the repository
git clone https://github.com/QwenLM/Qwen3-VL-Embedding.git
cd Qwen3-VL-Embedding

# Setup environment (installs uv and all dependencies)
bash scripts/setup_environment.sh
source .venv/bin/activate
```

### Required Dependencies

```toml
# From pyproject.toml
requires-python = ">=3.11"
dependencies = [
    "accelerate>=1.12.0",
    "datasets>=4.4.2",
    "decord>=0.6.0",
    "ipykernel>=7.1.0",
    "matplotlib>=3.10.8",
    "ninja>=1.13.0",
    "opencv-python-headless>=4.12.0.88",
    "qwen-vl-utils>=0.0.14",
    "scipy>=1.16.3",
    "setuptools>=80.9.0",
    "torch==2.8.*",
    "torchvision>=0.23.0",
    "transformers>=4.57.3",
]
```

### Model Download

**From Hugging Face:**
```bash
uv pip install huggingface-hub
huggingface-cli download Qwen/Qwen3-VL-Embedding-2B --local-dir ./models/Qwen3-VL-Embedding-2B
```

**From ModelScope (alternative):**
```bash
uv pip install modelscope
modelscope download --model qwen/Qwen3-VL-Embedding-2B --local_dir ./models/Qwen3-VL-Embedding-2B
```

## Qwen3VLEmbedder Class

### Constructor

```python
from src.models.qwen3_vl_embedding import Qwen3VLEmbedder

model = Qwen3VLEmbedder(
    model_name_or_path="./models/Qwen3-VL-Embedding-2B",  # or "Qwen/Qwen3-VL-Embedding-8B"
    max_length=8192,           # Default context length (truncation limit)
    min_pixels=4096,           # Minimum pixels for input images
    max_pixels=1843200,        # Maximum pixels for input images (1280×1440)
    total_pixels=7864320,      # Max total pixels for videos (×2 in model)
    fps=1.0,                   # Default video frame sampling rate
    max_frames=64,             # Maximum frames for video input
    default_instruction="Represent the user's input.",
    torch_dtype=torch.bfloat16,         # Optional: use bfloat16 precision
    attn_implementation="flash_attention_2"  # Optional: accelerate & save memory
)
```

### Process Method

```python
embeddings = model.process(inputs, normalize=True)
```

**Parameters:**
- `inputs`: List of dictionaries (see Input Format below)
- `normalize`: Whether to L2-normalize embeddings (default: True)

**Returns:** Tuple of `(embeddings_tensor, attention_mask)` or just embeddings tensor

## Input Format

### Multimodal Object Structure

Each input is a dictionary with optional keys:

| Key | Type | Description |
|-----|------|-------------|
| `text` | `str` or `List[str]` | Text input (single string or list) |
| `image` | `str`, `PIL.Image.Image`, or `List[...]` | Image: local path, URL, PIL instance, or list |
| `video` | `str`, `List[str]`, `List[PIL.Image.Image]` | Video: file path, URL, or frame sequence |
| `instruction` | `str` (optional) | Task description for relevance evaluation |
| `fps` | `float` (optional) | Video frame sampling rate per second |
| `max_frames` | `int` (optional) | Maximum frames to sample from video |

### Image Input Types

- **Local file path**: `"./path/to/image.jpg"`
- **URL**: `"https://example.com/image.png"`
- **PIL Image instance**: `Image.open("path/to/image.jpg")`
- **Multiple images**: List of any combination above

### Video Input Types

- **Video file path**: `"./path/to/video.mp4"`
- **URL**: `"https://example.com/video.mp4"`
- **Frame sequence**: `["frame1.jpg", "frame2.jpg", ...]` or `[PIL.Image, PIL.Image, ...]`
- **Multiple videos**: List of any combination above

## Usage Examples

### Text-Only Embeddings

```python
import torch
from src.models.qwen3_vl_embedding import Qwen3VLEmbedder

model = Qwen3VLEmbedder(
    model_name_or_path="Qwen/Qwen3-VL-Embedding-2B",
    torch_dtype=torch.bfloat16,
)

inputs = [
    {"text": "A woman playing with her dog on a beach at sunset.",
     "instruction": "Retrieve images or text relevant to the user's query."},
    {"text": "A joyful moment with a golden retriever on a sun-drenched beach at sunset."}
]

embeddings = model.process(inputs)
print(f"Shape: {embeddings.shape}")  # (2, 2048) for 2B model

# Similarity matrix
similarity = embeddings @ embeddings.T
print(similarity)
```

### Image-Only Embeddings

```python
inputs = [
    {"image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"}
]

embeddings = model.process(inputs)
```

### Multimodal (Text + Image)

```python
inputs = [{
    "text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset.",
    "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"
}]

embeddings = model.process(inputs)
```

### Video Input

```python
inputs = [{
    "text": "Describe the action in this video.",
    "video": "./path/to/video.mp4",
    "fps": 1.0,       # Optional: frames per second
    "max_frames": 64  # Optional: max frames to sample
}]

embeddings = model.process(inputs)
```

### Mixed Modalities (Text + Image + Video)

```python
inputs = [{
    "text": "Compare the image and video content.",
    "image": "./path/to/image.jpg",
    "video": ["frame1.jpg", "frame2.jpg", "frame3.jpg"]  # Frame sequence
}]

embeddings = model.process(inputs)
```

### Custom Instruction for Task-Specific Embeddings

```python
inputs = [
    {"text": "Product description about wireless headphones.",
     "instruction": "Retrieve product descriptions for e-commerce search."},
    {"text": "Best noise-cancelling headphones 2024 review.",
     "instruction": "Retrieve product descriptions for e-commerce search."}
]

embeddings = model.process(inputs)
```

### Dimension Truncation (MRL)

```python
# Get full embeddings (2048-dim for 2B, 4096-dim for 8B)
full_embeddings = model.process(inputs)

# Truncate to smaller dimension for efficiency
small_dim = 256
truncated = full_embeddings[:, :small_dim]
```

## Key Implementation Details

### EOS Token Pooling

The model extracts the embedding from the `[EOS]` token position:

```python
@staticmethod
def _pooling_last(hidden_state, attention_mask):
    """Pool last hidden state by attention mask."""
    flipped_tensor = attention_mask.flip(dims=[1])
    last_one_positions = flipped_tensor.argmax(dim=1)
    col = attention_mask.shape[1] - last_one_positions - 1
    row = torch.arange(hidden_state.shape[0], device=hidden_state.device)
    return hidden_state[row, col]
```

### Token Truncation

The `_truncate_tokens` method preserves special tokens while truncating:

```python
def _truncate_tokens(self, token_ids, max_length):
    """Truncate to max_length while keeping all special tokens."""
    special_token_ids = set(self.processor.tokenizer.all_special_ids)
    num_special = sum(1 for t in token_ids if t in special_token_ids)
    num_non_special_to_keep = max_length - num_special

    final_token_ids = []
    non_special_kept_count = 0
    for token_idx in token_ids:
        if token_idx in special_token_ids:
            final_token_ids.append(token_idx)
        elif non_special_kept_count < num_non_special_to_keep:
            final_token_ids.append(token_idx)
            non_special_kept_count += 1
    return final_token_ids
```

### Instruction Formatting

Instructions are automatically appended with a period if missing:

```python
if instruction:
    instruction = instruction.strip()
    if instruction and not unicodedata.category(instruction[-1]).startswith('P'):
        instruction = instruction + '.'
```

## References

- Source Code: https://github.com/QwenLM/Qwen3-VL-Embedding/tree/main/src/models
- Transformers Docs: https://huggingface.co/docs/transformers

# vLLM Inference API

## Prerequisites

```bash
# Requires vLLM >= 0.14.0
pip install vllm>=0.14.0
```

## Quick Start with vLLM

### Model Initialization

```python
from vllm import LLM

llm = LLM(
    model="Qwen/Qwen3-VL-Embedding-2B",  # or "Qwen/Qwen3-VL-Embedding-8B"
    runner="pooling",                      # Required for embedding models
    dtype='bfloat16',                      # Recommended precision
    trust_remote_code=True,                # Required to load custom model
)
```

### Input Formatting

```python
import os
from typing import List, Dict, Any
from vllm.multimodal.utils import fetch_image
from PIL import Image

def format_input_to_conversation(
    input_dict: Dict[str, Any],
    default_instruction: str = "Represent the user's input."
) -> List[Dict]:
    """Format a single input dict into conversation format."""
    content = []

    instruction = input_dict.get('instruction') or default_instruction
    text = input_dict.get('text')
    image = input_dict.get('image')

    # Handle image input
    if image:
        if isinstance(image, str):
            if image.startswith(('http://', 'https://')):
                image_content = image
            else:
                abs_image_path = os.path.abspath(image)
                image_content = 'file://' + abs_image_path
        else:
            image_content = image

        content.append({'type': 'image', 'image': image_content})

    # Handle text input
    if text:
        content.append({'type': 'text', 'text': text})

    # Handle empty input
    if not content:
        content.append({'type': 'text', 'text': ""})

    return [
        {"role": "system", "content": [{"type": "text", "text": instruction}]},
        {"role": "user", "content": content}
    ]

def prepare_vllm_inputs(
    input_dict: Dict[str, Any],
    llm: LLM
) -> Dict[str, Any]:
    """Convert input dict to vLLM-compatible format."""
    conversation = format_input_to_conversation(input_dict)

    # Generate prompt from chat template
    prompt_text = llm.llm_engine.tokenizer.apply_chat_template(
        conversation,
        tokenize=False,
        add_generation_prompt=True
    )

    # Prepare multimodal data
    multi_modal_data = None
    image = input_dict.get('image')
    if image:
        if isinstance(image, str):
            if image.startswith(('http://', 'https://')):
                try:
                    multi_modal_data = {"image": fetch_image(image)}
                except Exception as e:
                    print(f"Warning: Failed to fetch image {image}: {e}")
            else:
                abs_path = os.path.abspath(image)
                if os.path.exists(abs_path):
                    multi_modal_data = {"image": Image.open(abs_path)}
        else:
            multi_modal_data = {"image": image}

    return {
        "prompt": prompt_text,
        "multi_modal_data": multi_modal_data
    }
```

### Batch Embedding Generation

```python
# Prepare input samples
inputs = [
    {
        "text": "A woman playing with her dog on a beach at sunset.",
        "instruction": "Retrieve images or text relevant to the user's query.",
    },
    {
        "text": "A joyful moment with a golden retriever on a sun-drenched beach.",
    },
    {
        "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"
    },
    {
        "text": "A woman shares a joyful moment with her golden retriever.",
        "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"
    }
]

# Convert to vLLM format
vllm_inputs = [prepare_vllm_inputs(inp, llm) for inp in inputs]

# Generate embeddings (single call for batch)
outputs = llm.embed(vllm_inputs)

# Extract embedding vectors
import numpy as np
embeddings_list = [output.outputs.embedding for output in outputs]
embeddings = np.array(embeddings_list)

print(f"Embeddings shape: {embeddings.shape}")  # (4, dim)
```

### Similarity Computation

```python
# Cosine similarity matrix
similarity_scores = embeddings @ embeddings.T
print("Similarity Score Matrix:")
print(similarity_scores)

# Find most similar pair
max_idx = np.unravel_index(np.argmax(similarity_scores), similarity_scores.shape)
print(f"Most similar: indices {max_idx[0]} and {max_idx[1]}")
```

## vLLM vs Transformers Comparison

| Aspect | Transformers API | vLLM API |
|--------|-----------------|----------|
| **Best for** | Fine-grained control, customization | Batch inference, serving |
| **Throughput** | Single/batch processing | High-throughput batching |
| **Setup** | Simple import | Requires vLLM >= 0.14.0 |
| **Memory** | Higher per-request overhead | Optimized for concurrent requests |
| **Input handling** | Automatic multimodal processing | Manual formatting required |
| **Output format** | PyTorch tensors | numpy arrays via `.outputs.embedding` |

## Performance Tips

### For Transformers (Single Request)
```python
# Use bfloat16 and flash attention for speed
model = Qwen3VLEmbedder(
    model_name_or_path="Qwen/Qwen3-VL-Embedding-2B",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"  # Requires flash-attn
)
```

### For vLLM (Batch/Serving)
```python
# bfloat16 is recommended for best performance
llm = LLM(
    model="Qwen/Qwen3-VL-Embedding-8B",
    runner="pooling",
    dtype='bfloat16',
    trust_remote_code=True,
)
```

## Key Differences from Transformers API

### vLLM Advantages
- Single `llm.embed()` call handles entire batch
- Automatic memory management across requests
- Optimized for high-concurrency serving
- No manual tensor device management needed

### vLLM Limitations
- Requires manual prompt formatting via chat template
- Less flexible for custom input processing
- Multimodal data must be pre-loaded (PIL images)
- URL fetching requires `fetch_image()` utility

## References

- vLLM Docs: https://docs.vllm.ai/en/latest/
- Embedding vLLM Example: https://github.com/QwenLM/Qwen3-VL-Embedding/blob/main/examples/embedding_vllm.ipynb
- Reranker vLLM Example: https://github.com/QwenLM/Qwen3-VL-Embedding/blob/main/examples/reranker_vllm.ipynb

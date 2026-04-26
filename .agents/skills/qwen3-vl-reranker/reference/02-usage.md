# Usage Patterns

## Sentence Transformers API

The simplest integration path. Uses `CrossEncoder` for pair scoring and ranking:

```python
from sentence_transformers import CrossEncoder
import torch

model = CrossEncoder("Qwen/Qwen3-VL-Reranker-2B")

query = "A woman playing with her dog on a beach at sunset."
documents = [
    "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset...",
    "https://example.com/demo.jpeg",
    {
        "text": "A woman shares a joyful moment with her golden retriever...",
        "image": "https://example.com/demo.jpeg",
    },
]

# Score pairs
prompt = "Retrieve images or text relevant to the user's query."
pairs = [(query, doc) for doc in documents]
scores = model.predict(pairs, prompt=prompt)
print(scores)
# [1.8125, 0.5625, 1.3125]

# Rank documents (returns sorted list with corpus_id and score)
rankings = model.rank(query, documents, prompt=prompt)
print(rankings)
# [{'corpus_id': 0, 'score': 1.8125}, {'corpus_id': 2, 'score': 1.3125}, {'corpus_id': 1, 'score': 0.5625}]

# Optional: map raw scores to [0, 1] with sigmoid
scores = model.predict(pairs, activation_fn=torch.nn.Sigmoid(), prompt=prompt)
print(scores)
# [0.8594, 0.6367, 0.7891]
```

The default prompt is `"query"` with instruction `"Retrieve text relevant to the user's query."` Customize via the `prompt` parameter for task-specific optimization.

## Transformers API (Qwen3VLReranker class)

Requires `transformers>=4.57.0`, `qwen-vl-utils>=0.0.14`, `torch==2.8.0`. Uses the official `Qwen3VLReranker` wrapper from the GitHub repository:

```python
from scripts.qwen3_vl_reranker import Qwen3VLReranker

model = Qwen3VLReranker(
    model_name_or_path="Qwen/Qwen3-VL-Reranker-2B",
    # Recommended for production:
    # torch_dtype=torch.bfloat16,
    # attn_implementation="flash_attention_2"
)

inputs = {
    "instruction": "Retrieve images or text relevant to the user's query.",
    "query": {"text": "A woman playing with her dog on a beach at sunset."},
    "documents": [
        {"text": "A woman shares a joyful moment with her golden retriever..."},
        {"image": "https://example.com/demo.jpeg"},
        {"text": "A woman shares a joyful moment...", "image": "https://example.com/demo.jpeg"}
    ],
    "fps": 1.0,
    "max_frames": 64
}

scores = model.process(inputs)
print(scores)
# [0.8613, 0.6757, 0.8125]
```

## vLLM Deployment

For high-throughput serving, use vLLM (>= 0.14.0) with pooling runner:

```python
from vllm import LLM, EngineArgs
from vllm.entrypoints.score_utils import ScoreMultiModalParam
from pathlib import Path
import os

def format_document_to_score_param(doc_dict):
    content = []
    text = doc_dict.get('text')
    image = doc_dict.get('image')

    if text:
        content.append({"type": "text", "text": text})

    if image:
        image_url = image
        if isinstance(image, str) and not image.startswith(('http', 'https', 'oss')):
            image_url = 'file://' + os.path.abspath(image)
        content.append({
            "type": "image_url",
            "image_url": {"url": image_url}
        })

    if not content:
        content.append({"type": "text", "text": ""})

    return {"content": content}


engine_args = EngineArgs(
    model="Qwen/Qwen3-VL-Reranker-2B",
    runner="pooling",
    dtype="bfloat16",
    trust_remote_code=True,
    hf_overrides={
        "architectures": ["Qwen3VLForSequenceClassification"],
        "classifier_from_token": ["no", "yes"],
        "is_original_qwen3_reranker": True,
    },
)

llm = LLM(**vars(engine_args))

# Optional: load chat template
template_path = Path("vllm/examples/pooling/score/template/qwen3_vl_reranker.jinja")
chat_template = template_path.read_text() if template_path.exists() else None

query_text = "A woman playing with her dog on a beach at sunset."
documents = [
    {"text": "A woman shares a joyful moment..."},
    {"image": "https://example.com/demo.jpeg"},
    {"text": "...", "image": "https://example.com/demo.jpeg"}
]

scores = []
for doc_dict in documents:
    doc_param = format_document_to_score_param(doc_dict)
    outputs = llm.score(query_text, doc_param, chat_template=chat_template)
    scores.append(outputs[0].outputs.score)

print(scores)
```

## Input Format Specification

### Multimodal Object

A dictionary with optional keys:

- **`text`**: String or list of strings
- **`image`**: Local file path, URL, PIL.Image instance, or list of any combination
- **`video`**: Local file path, URL, sequence of frames (list of image paths or PIL images), or list of any combination

All input types support both single objects and lists.

### Video Sampling Settings

Only effective when video is a file path:

- **`fps`**: Frame sampling rate in frames per second (default: 1.0)
- **`max_frames`**: Maximum number of frames to sample (default: 64)

### Reranker Input Structure

```python
{
    "instruction": "Task description for relevance evaluation.",
    "query": <multimodal object>,
    "documents": [<multimodal object>, ...],
    "fps": 1.0,           # optional, for video inputs
    "max_frames": 64      # optional, for video inputs
}
```

## Instruction Customization

The `instruction` field guides the model's relevance judgment. Examples:

- `"Retrieve images or text relevant to the user's query."` — general multimodal retrieval
- `"Find documents that answer the user's question."` — QA-oriented retrieval
- `"Rank visual documents by their relevance to the search query."` — document retrieval

Write instructions in English for best results, even with non-English queries and documents.

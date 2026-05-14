# Pipeline API

## Overview

The `pipeline()` function is a high-level inference wrapper that handles preprocessing, model loading, and postprocessing. It abstracts away the complexity of working with models directly.

```python
from transformers import pipeline

pipe = pipeline("text-classification")
pipe("This restaurant is awesome")
# [{'label': 'POSITIVE', 'score': 0.9998743534088135}]
```

## Available Tasks

### Natural Language Processing

- `text-classification` — Sentiment analysis, text categorization
- `token-classification` — Named entity recognition
- `question-answering` — Extractive QA
- `fill-mask` — Masked language modeling
- `text2text-generation` — Translation, summarization
- `summarization` — Text summarization
- `translation` — Machine translation (specify `src_lang` and `tgt_lang`)
- `zero-shot-classification` — Classify text into custom categories
- `feature-extraction` — Get embeddings/hidden states

### Computer Vision

- `image-classification` — Classify images
- `object-detection` — Detect objects in images
- `image-segmentation` — Segment image regions
- `depth-estimation` — Estimate depth from images
- `video-classification` — Classify videos
- `image-to-image` — Image transformation

### Audio

- `automatic-speech-recognition` — Transcribe speech to text
- `audio-classification` — Classify audio clips
- `text-to-audio` — Generate audio from text

### Multimodal

- `document-question-answering` — QA on document images
- `visual-question-answering` — Answer questions about images
- `image-to-text` — Image captioning

## Pipeline Usage Patterns

### Single Item

```python
pipe = pipeline("text-classification")
result = pipe("This is great!")
```

### Batch Items

```python
pipe = pipeline("text-classification")
results = pipe(["This is great!", "This is terrible."])
```

### Custom Model

```python
pipe = pipeline(model="FacebookAI/roberta-large-mnli")
pipe("This restaurant is awesome")
# Task inferred from model card
```

### Device Placement

```python
from accelerate import Accelerator

device = Accelerator().device  # Auto-detect GPU or CPU
pipe = pipeline("text-generation", model="meta-llama/Llama-2-7b-hf", device=device)
```

## Pipeline Batching

Enable batching for throughput on static datasets:

```python
from transformers import pipeline
from torch.utils.data import Dataset

pipe = pipeline("text-classification", device=0)

class MyDataset(Dataset):
    def __len__(self):
        return 5000
    def __getitem__(self, i):
        return "This is a test"

for out in pipe(MyDataset(), batch_size=64):
    print(out)
```

Batching performance depends on hardware and data regularity:

- GPU + uniform sequence length → significant speedup
- CPU or variable lengths → may slow down or cause OOM
- Latency-constrained (live inference) → don't batch
- Throughput-constrained (batch processing) → batch on GPU

## FP16 Inference

Run models in half precision for faster inference with minimal accuracy loss:

```python
pipe = pipeline("text-classification", model="bert-base", dtype=torch.float16)
```

## Streaming with Datasets

Process large datasets without loading everything into memory:

```python
import datasets
from transformers import pipeline
from transformers.pipelines.pt_utils import KeyDataset

pipe = pipeline("text-classification", device=0)
dataset = datasets.load_dataset("imdb", split="test")

for out in pipe(KeyDataset(dataset, "text"), batch_size=8):
    print(out)
```

## Custom Pipelines

Subclass a pipeline for custom preprocessing or postprocessing:

```python
from transformers import TextClassificationPipeline

class MyPipeline(TextClassificationPipeline):
    def postprocess(self, model_outputs, **kwargs):
        # Custom postprocessing
        results = super().postprocess(model_outputs, **kwargs)
        return [{"label": r["label"], "score": r["score"] * 100} for r in results]

pipe = pipeline("text-classification", model="bert-base", pipeline_class=MyPipeline)
```

## Pipeline vs Direct Model

Use `pipeline()` when:

- You want the simplest possible API
- You need preprocessing/postprocessing handled automatically
- You're prototyping or building applications

Use direct model (`model.generate()`, `model(**inputs)`) when:

- You need fine-grained control over generation parameters
- You're doing research or custom training loops
- You need to optimize inference with specific caching/quantization strategies
- You're building a serving application

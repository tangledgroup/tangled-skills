# Pipeline API - Complete Guide

The Pipeline API is Transformers' simplest and most powerful interface for running inference on 50+ different tasks without needing to understand the underlying model architecture.

## Overview

Pipelines encapsulate all the complex code from the library, offering a simple API dedicated to specific tasks. They automatically handle:

- Model loading and configuration
- Tokenization/preprocessing
- Inference execution
- Post-processing of results

## Basic Usage

### Auto-detect Task

```python
from transformers import pipeline

# Pipeline auto-selects a default model for the task
classifier = pipeline("sentiment-analysis")
result = classifier("I love Transformers!")
# [{'label': 'POSITIVE', 'score': 0.9998}]
```

### Specify Model

```python
# Use a specific model from the Hub
classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# Or use a model that defines its own task
pipe = pipeline(model="FacebookAI/roberta-large-mnli")  # Auto-detects task from model card
```

### Batch Processing

```python
classifier = pipeline("sentiment-analysis")

# Process list of inputs
results = classifier([
    "This is amazing!",
    "This is terrible",
    "It's okay"
])

# Results: [
#   {'label': 'POSITIVE', 'score': 0.9998},
#   {'label': 'NEGATIVE', 'score': 0.9996},
#   {'label': 'NEGATIVE', 'score': 0.7234}
# ]
```

## Pipeline Batching and Streaming

### Batch Size Control

```python
from transformers import pipeline

pipe = pipeline("text-classification", device=0)

# Process with custom batch size
for result in pipe(
    ["text 1", "text 2", "text 3"],
    batch_size=8,
    truncation=True
):
    print(result)
```

### Streaming from Generators

```python
from transformers import pipeline

pipe = pipeline("text-classification")

def data_generator():
    """Yield data from any source"""
    yield "First text"
    yield "Second text"
    yield "Third text"

for out in pipe(data_generator()):
    print(out)
```

### Streaming from Datasets

```python
import datasets
from transformers import pipeline
from transformers.pipelines.pt_utils import KeyDataset

pipe = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h", device=0)
dataset = datasets.load_dataset("superb", name="asr", split="test")

for out in pipe(KeyDataset(dataset, "file")):
    print(out["text"])
```

## Task-Specific Pipelines

### Natural Language Processing

#### Text Classification

```python
from transformers import pipeline

# Binary/multi-class classification
classifier = pipeline("text-classification")
result = classifier("I love this product!")
# [{'label': 'POSITIVE', 'score': 0.9998}]

# Top-k predictions
classifier = pipeline("text-classification", top_k=3)
result = classifier("The movie was okay")
# [
#   {'label': 'NEGATIVE', 'score': 0.6},
#   {'label': 'POSITIVE', 'score': 0.3},
#   {'label': 'NEUTRAL', 'score': 0.1}
# ]

# Return all probabilities
classifier = pipeline("text-classification", return_all_scores=True)
result = classifier("Great experience")
```

#### Zero-Shot Classification

```python
from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Classify into custom labels
result = classifier(
    sequence="I bought a new car and love driving it",
    candidate_labels=["vehicle review", "food review", "travel blog"]
)
# {
#   'sequence': '...',
#   'labels': ['vehicle review', 'travel blog', 'food review'],
#   'scores': [0.92, 0.05, 0.03]
# }

# Multi-label classification
result = classifier(
    ["This movie was amazing", "The food was terrible"],
    ["positive", "negative"],
    hypothesis_template="This text is {}"
)
```

#### Question Answering

```python
from transformers import pipeline

qa_pipeline = pipeline("question-answering")

# Extractive QA
result = qa_pipeline(
    question="What is the capital of France?",
    context="Paris is the capital of France and is known as the City of Light."
)
# {'answer': 'Paris', 'score': 0.99, 'start': 0, 'end': 5}

# With custom model
qa_pipeline = pipeline(
    "question-answering",
    model="deepset/roberta-base-squad2"
)

# Handle unanswerable questions
result = qa_pipeline(
    question="What color is the sky at night?",
    context="The ocean is blue during the day."
)
# {'answer': '', 'score': 0.0, ...}  # Model doesn't know
```

#### Conversational AI

```python
from transformers import pipeline

# Load conversational pipeline
conversation_pipeline = pipeline(
    "conversational",
    model="microsoft/DialoGPT-medium"
)

# Initialize conversation
conversation = conversation_pipeline(
    text="Hello, how are you?"
)

# Continue conversation
conversation = conversation_pipeline(
    past_user_inputs=["Hello, how are you?", "What's the weather like?"],
    generated_responses=["I'm doing well!", "It's sunny today"],
    text="That sounds nice!"
)
```

#### Text Generation

```python
from transformers import pipeline

# Basic generation
generator = pipeline("text-generation", model="gpt2")
result = generator("Once upon a time", max_length=50)

# With modern LLMs
generator = pipeline(
    "text-generation",
    model="meta-llama/Llama-3.1-8b",
    tokenizer_kwargs={"padding_side": "left"}
)

result = generator(
    "Explain quantum computing in simple terms:",
    max_new_tokens=100,
    temperature=0.7,
    top_p=0.9,
    do_sample=True
)

# Stream generation
for token in generator("Hello, my name is", max_new_tokens=50, stream=True):
    print(token["generated_text"], end="", flush=True)
```

#### Summarization

```python
from transformers import pipeline

summarizer = pipeline("summarization")

article = """
Transformers are revolutionizing natural language processing. 
The architecture, introduced in the paper "Attention is All You Need", 
has become the foundation for models like BERT, GPT, and T5. 
These models have achieved state-of-the-art results on numerous tasks.
"""

summary = summarizer(article, max_length=50, min_length=20)
# [{'summary_text': 'Transformers revolutionize NLP. The architecture from "Attention is All You Need" underpins BERT, GPT, and T5.'}]

# Extractive vs abstractive
summarizer_extractive = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    extractive=False  # Default: abstractive
)
```

#### Translation

```python
from transformers import pipeline

# English to French
translator = pipeline("translation_en_to_fr", model="Helsinki-NLP/opus-mt-en-fr")
result = translator("Hello, how are you?")
# [{'translated_text': 'Bonjour, comment allez-vous ?'}]

# Custom translation model
translator = pipeline(
    "translation",
    model="Helsinki-NLP/opus-mt-de-en"  # German to English
)
result = translator("Guten Tag, wie geht es Ihnen?")
```

#### Named Entity Recognition

```python
from transformers import pipeline

ner = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")

result = ner("John works at Google in Mountain View.")
# [
#   {'entity': 'PERSON', 'word': 'John', 'score': 0.99},
#   {'entity': 'ORG', 'word': 'Google', 'score': 0.98},
#   {'entity': 'LOC', 'word': 'Mountain View', 'score': 0.97}
# ]

# Group entities by type
result = ner(
    "John works at Google in Mountain View.",
    aggregation_strategy="simple"
)
# [
#   {'entity_group': 'PERSON', 'word': 'John', 'score': 0.99},
#   {'entity_group': 'ORG', 'word': 'Google', 'score': 0.98},
#   {'entity_group': 'LOC', 'word': 'Mountain View', 'score': 0.97}
# ]
```

#### Token Classification

```python
from transformers import pipeline

# POS tagging
pos_tagger = pipeline(
    "token-classification",
    model="vblagoje/bert-english-uncased-finetuned-pos"
)

result = pos_tagger("The quick brown fox jumps over the lazy dog")
# [
#   {'entity': 'DT', 'word': 'The', 'score': 0.99},
#   {'entity': 'JJ', 'word': 'quick', 'score': 0.98},
#   ...
# ]
```

### Computer Vision

#### Image Classification

```python
from transformers import pipeline

classifier = pipeline("image-classification")

# From URL
result = classifier("https://images.unsplash.com/photo-1543362906-acfc16ae6efb")
# [{'label': 'Siamese cat', 'score': 0.97}]

# From PIL image
from PIL import Image
image = Image.open("cat.jpg")
result = classifier(image)

# With custom model
classifier = pipeline(
    "image-classification",
    model="google/vit-base-patch16-224"
)
```

#### Object Detection

```python
from transformers import pipeline

detector = pipeline("object-detection", model="facebook/detr-resnet-50")

image = "https://images.unsplash.com/photo-1560343090-f0409e92791a"
result = detector(image)
# [
#   {
#     'label': 'person',
#     'score': 0.95,
#     'box': {'xmin': 100, 'ymin': 50, 'xmax': 300, 'ymax': 400}
#   }
# ]

# Filter by confidence threshold
detector = pipeline("object-detection", threshold=0.8)
```

#### Image Segmentation

```python
from transformers import pipeline

# Semantic segmentation
segmenter = pipeline(
    "image-segmentation",
    model="facebook/detr-resnet-50-panoptic"
)

result = segmenter("https://images.unsplash.com/photo-1560343090-f0409e92791a")
# Returns segmentation masks with labels

# Instance segmentation
segmenter = pipeline(
    "image-segmentation",
    model="intel/dpvit-small-224-quickstart-instance-segmentation"
)
```

#### Depth Estimation

```python
from transformers import pipeline
import cv2

estimator = pipeline("depth-estimation")

image = cv2.imread("scene.jpg")
depth_map = estimator(image)

# Visualize depth
import numpy as np
depth_np = np.array(depth_map["predicted_depth"])
cv2.imwrite("depth.png", (depth_np * 255).astype(np.uint8))
```

### Audio Processing

#### Automatic Speech Recognition

```python
from transformers import pipeline

transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")

# From file
result = transcriber("audio_file.mp3")
# {'text': 'Hello, welcome to Transformers!'}

# From numpy array
import soundfile as sf
audio, sample_rate = sf.read("audio.wav")
result = transcriber(audio, sampling_rate=sample_rate)

# With timestamp
result = transcriber(
    "audio.mp3",
    return_timestamps=True
)
# {'chunks': [{'text': 'Hello', 'timestamp': (0.0, 1.2)}, ...]}

# Multilingual with language detection
result = transcriber("audio.mp3", generate_kwargs={"language": "en"})
```

#### Audio Classification

```python
from transformers import pipeline

classifier = pipeline(
    "audio-classification",
    model="superb/hubert-large-superb-er"
)

result = classifier("speech_sample.wav")
# [{'label': 'speech', 'score': 0.95}]
```

#### Speaker Verification

```python
from transformers import pipeline
import numpy as np

verifier = pipeline("speaker-verification", model="SpeechBrain/ecapa_tdnn_librispeech")

# Compare two audio files
score = verifier(
    "speaker1_sample1.wav",
    "speaker1_sample2.wav"
)
# {'score': 0.95}  # High score = same speaker

threshold = 0.6
if score["score"] > threshold:
    print("Same speaker")
else:
    print("Different speakers")
```

### Multimodal Tasks

#### Document Question Answering

```python
from transformers import pipeline

# Visual question answering on documents
doc_qa = pipeline(
    "document-question-answering",
    model="impira/layoutlm-document-qa"
)

result = doc_qa(
    image="invoice.png",
    question="What is the total amount?"
)
# {'answer': '$1,234.56', 'score': 0.95}
```

#### Image Captioning

```python
from transformers import pipeline

captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large")

result = captioner("https://images.unsplash.com/photo-1543362906-acfc16ae6efb")
# [{'generated_text': 'a white cat sitting on a table'}]

# With parameters
result = captioner(
    "cat.jpg",
    max_new_tokens=50,
    num_return_sequences=3
)
```

#### Visual Question Answering

```python
from transformers import pipeline

vqa = pipeline("image-question-answering", model="dandelin/vilt-b32-finetuned-vqa")

result = vqa(
    image="https://images.unsplash.com/photo-1543362906-acfc16ae6efb",
    question="What color is the cat?"
)
# {'answer': 'white', 'score': 0.92}
```

## Pipeline Configuration

### Device Management

```python
from transformers import pipeline

# Auto-detect (GPU if available)
pipe = pipeline("sentiment-analysis")

# Force CPU
pipe = pipeline("sentiment-analysis", device=-1)

# Specific GPU
pipe = pipeline("sentiment-analysis", device=0)

# Multiple GPUs (model parallelism)
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "large-model",
    device_map="auto"  # Automatic multi-GPU distribution
)
pipe = pipeline("text-generation", model=model)
```

### Performance Optimization

```python
from transformers import pipeline

# Enable batching
pipe = pipeline(
    "text-classification",
    batch_size=32,
    device=0
)

# Use FP16 precision (requires CUDA)
pipe = pipeline(
    "text-generation",
    model="gpt2",
    model_kwargs={"torch_dtype": torch.float16}
)

# Enable tensor parallelism for large models
pipe = pipeline(
    "text-generation",
    model="large-llm",
    model_kwargs={
        "device_map": "auto",
        "torch_dtype": torch.float16,
        "attn_implementation": "flash_attention_2"
    }
)
```

### Custom Post-processing

```python
from transformers import pipeline

# Add custom post-processing
def custom_post_process(model_outputs):
    """Custom formatting of results"""
    return {
        "label": model_outputs[0]["label"],
        "confidence": round(model_outputs[0]["score"], 4),
        "normalized": model_outputs[0]["score"] > 0.5
    }

pipe = pipeline("sentiment-analysis")
result = pipe("I love this!")
custom_result = custom_post_process(result)
```

## Pipeline Best Practices

1. **Use batching** for multiple inputs to maximize throughput
2. **Enable GPU** when available for significant speedups
3. **Set appropriate batch_size** based on your GPU memory
4. **Use truncation** for long inputs to avoid OOM errors
5. **Cache pipelines** - don't recreate them in loops
6. **Stream generation** for interactive applications

## Troubleshooting

### Out of Memory

```python
# Reduce batch size
pipe = pipeline("text-generation", batch_size=4)

# Use quantization
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "large-model",
    load_in_8bit=True,
    device_map="auto"
)
pipe = pipeline("text-generation", model=model)
```

### Slow Inference

```python
# Enable GPU
pipe = pipeline("sentiment-analysis", device=0)

# Use smaller model
pipe = pipeline("sentiment-analysis", model="distilbert-base-uncased")

# Compile model (PyTorch 2.0+)
model = pipe.model.compile()
```

## Available Tasks

Complete list of supported pipeline tasks:

**NLP**: `text-classification`, `text-generation`, `fill-mask`, `question-answering`, `summarization`, `translation`, `zero-shot-classification`, `ner`, `token-classification`, `conversational`, `feature-extraction`

**Vision**: `image-classification`, `object-detection`, `image-segmentation`, `depth-estimation`, `image-to-text`, `image-question-answering`, `zero-shot-image-classification`

**Audio**: `automatic-speech-recognition`, `audio-classification`, `speaker-verification`, `text-to-speech`

**Multimodal**: `document-question-answering`, `visual-question-answering`, `video-classification`

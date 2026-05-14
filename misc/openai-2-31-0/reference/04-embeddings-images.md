# Embeddings and Images

## Embeddings

Generate dense vector representations of text for semantic search, clustering, and RAG pipelines.

### Basic Usage

```python
from openai import OpenAI

client = OpenAI()

embedding = client.embeddings.create(
    model="text-embedding-3-small",  # or text-embedding-3-large
    input="The food was delicious and the atmosphere was cozy.",
)

vector = embedding.data[0].embedding  # list of floats
print(len(vector))  # dimensionality
```

### Multiple Inputs

Pass a list of strings for batch embedding:

```python
embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input=["First document text...", "Second document text..."],
)

for i, item in enumerate(embedding.data):
    print(f"Document {i}: {len(item.embedding)} dimensions")
```

### Dimensions

Truncate embeddings to a specific dimension (Matryoshka property):

```python
embedding = client.embeddings.create(
    model="text-embedding-3-large",
    input="Your text here.",
    dimensions=256,  # reduce from default 3072
)
```

### Model Options

- `text-embedding-3-small` — 1536 dimensions, fast and cost-effective
- `text-embedding-3-large` — 3072 dimensions, highest performance

## Images

Generate, edit, and create variations of images using DALL·E models.

### Image Generation

```python
response = client.images.generate(
    model="dall-e-3",
    prompt="A serene lake surrounded by mountains at sunset",
    size="1024x1024",  # 1024x1024, 1024x1792, 1792x1024 (dall-e-3)
                       # 256x256, 512x512, 1024x1024 (dall-e-2)
    quality="standard",  # standard or hd (dall-e-3)
    style="vivid",       # vivid or natural (dall-e-3)
    n=1,                 # number of images
    response_format="url",  # url or b64_json
)

print(response.data[0].url)
```

### Base64 Response

```python
response = client.images.generate(
    model="dall-e-3",
    prompt="A cute baby otter",
    response_format="b64_json",
)

import base64
image_data = base64.b64decode(response.data[0].b64_json)
with open("otter.png", "wb") as f:
    f.write(image_data)
```

### Image Editing

Create image variations with a mask (transparent PNG):

```python
response = client.images.edit(
    model="dall-e-2",
    image=open("original.png", "rb"),
    mask=open("mask.png", "rb"),  # transparent areas will be inpainted
    prompt="A golden retriever sitting in a garden",
    size="1024x1024",
    n=1,
)
```

### Image Variation

Generate variations of an existing image:

```python
response = client.images.create_variation(
    image=open("source.png", "rb"),
    n=2,
    size="1024x1024",
)
```

### Streaming Image Generation

```python
stream = client.images.generate(
    model="dall-e-3",
    prompt="A futuristic cityscape",
    stream=True,
)

for event in stream:
    if event.type == "image.gen.partial_image":
        # Progress update with partial image data
        pass
    elif event.type == "image.gen.completed":
        print(event.image.url)
```

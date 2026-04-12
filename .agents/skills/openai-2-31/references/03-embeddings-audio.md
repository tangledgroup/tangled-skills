# Embeddings and Audio Processing

Comprehensive guide to generating embeddings for semantic search, classification, and clustering, plus audio transcription and text-to-speech synthesis.

## Embeddings

Embeddings are vector representations of text that capture semantic meaning. Use them for semantic search, clustering, classification, and recommendation systems.

### Basic Usage

```python
from openai import OpenAI

client = OpenAI()

embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input="The food was delicious and the waiter...",
)

# Get the vector (list of floats)
vector = embedding.data[0].embedding
print(f"Vector dimension: {len(vector)}")  # 1536 for text-embedding-3-small
```

### Embedding Models

| Model | Dimensions | Max Tokens | Use Case |
|-------|------------|------------|----------|
| `text-embedding-3-small` | 1536 | 8191 | Cost-effective, good performance |
| `text-embedding-3-large` | 3072 | 8191 | Best performance, higher cost |
| `text-embedding-ada-002` | 1536 | 8191 | Legacy model |

### Embedding Multiple Texts

Batch embeddings for efficiency:

```python
from openai import OpenAI

client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=[
        "What is the capital of France?",
        "How do you bake a cake?",
        "Explain quantum computing.",
    ],
)

for i, data in enumerate(response.data):
    print(f"Text {i}: {len(data.embedding)} dimensions")
```

### Specifying Dimensions

Reduce dimensions for efficiency (3-small and 3-large only):

```python
# Default: 1536 dimensions
embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input="Sample text",
)

# Reduced: 256 dimensions (faster, less storage)
embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input="Sample text",
    dimensions=256,
)

print(len(embedding.data[0].embedding))  # 256
```

### Embedding Usage Information

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Sample text",
)

print(f"Prompt tokens: {response.usage.prompt_tokens}")
print(f"Total cost: ${response.usage.total_tokens * 0.00000010 / 1000:.6f}")
```

### Async Embeddings

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def get_embedding(text: str) -> list:
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding

async def main():
    vectors = await asyncio.gather(
        get_embedding("Text one"),
        get_embedding("Text two"),
        get_embedding("Text three"),
    )
    print(f"Generated {len(vectors)} embeddings")

asyncio.run(main())
```

## Semantic Search with Embeddings

### Basic Implementation

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

# Database of documents
documents = [
    "Python is a programming language",
    "Java is widely used for enterprise applications",
    "Machine learning is a subset of AI",
    "Deep learning uses neural networks",
]

# Pre-compute embeddings for documents
doc_embeddings = []
for doc in documents:
    emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=doc,
    ).data[0].embedding
    doc_embeddings.append(emb)

doc_embeddings_np = np.array(doc_embeddings)

# Search function
def semantic_search(query: str, top_k: int = 3) -> list:
    # Embed the query
    query_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
    ).data[0].embedding
    
    # Calculate cosine similarity
    similarities = np.dot(doc_embeddings_np, query_emb) / (
        np.linalg.norm(doc_embeddings_np, axis=1) * np.linalg.norm(query_emb)
    )
    
    # Get top-k results
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    return [
        (documents[i], similarities[i]) 
        for i in top_indices
    ]

# Test search
results = semantic_search("What programming languages exist?")
for doc, score in results:
    print(f"{score:.3f}: {doc}")
```

### Production-Ready with faiss

```python
import faiss
import numpy as np
from openai import OpenAI

client = OpenAI()

# Create index
dimension = 1536
index = faiss.IndexFlatIP(dimension)  # Inner product (cosine with normalized vectors)

# Add documents
documents = ["doc1", "doc2", "doc3"]
embeddings = []

for doc in documents:
    emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=doc,
    ).data[0].embedding
    embeddings.append(np.array(emb, dtype='float32'))

# Normalize for cosine similarity
embeddings_np = np.array(embeddings, dtype='float32')
faiss.normalize_L2(embeddings_np)

# Add to index
index.add(embeddings_np)

# Search
query = "search query"
query_emb = client.embeddings.create(
    model="text-embedding-3-small",
    input=query,
).data[0].embedding

query_np = np.array(query_emb, dtype='float32').reshape(1, -1)
faiss.normalize_L2(query_np)

# Find nearest neighbors
distances, indices = index.search(query_np, k=3)

for i, idx in enumerate(indices[0]):
    print(f"{distances[0][i]:.3f}: {documents[idx]}")
```

## Classification with Embeddings

### Zero-Shot Classification

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

def classify_text(text: str, labels: list) -> tuple:
    """Classify text into one of the given labels."""
    
    # Embed the text and all labels
    inputs = [text] + labels
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=inputs,
    )
    
    # Get embeddings
    text_embedding = np.array(response.data[0].embedding)
    label_embeddings = np.array([
        emb.embedding for emb in response.data[1:]
    ])
    
    # Calculate similarities
    similarities = np.dot(label_embeddings, text_embedding) / (
        np.linalg.norm(label_embeddings, axis=1) * np.linalg.norm(text_embedding)
    )
    
    # Get best match
    best_idx = np.argmax(similarities)
    return labels[best_idx], similarities[best_idx]

# Example usage
text = "I love this product, it's amazing!"
labels = ["positive", "negative", "neutral"]

label, confidence = classify_text(text, labels)
print(f"Label: {label}, Confidence: {confidence:.3f}")
```

## Clustering with Embeddings

```python
from openai import OpenAI
from sklearn.cluster import KMeans
import numpy as np

client = OpenAI()

# Get embeddings for documents
documents = [
    "Python tutorial for beginners",
    "Advanced machine learning techniques",
    "How to cook pasta",
    "Baking chocolate cake recipe",
    "Deep learning with neural networks",
    "Grilling steak tips",
]

embeddings = []
for doc in documents:
    emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=doc,
    ).data[0].embedding
    embeddings.append(emb)

embeddings_np = np.array(embeddings)

# Cluster into 3 groups
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(embeddings_np)

# Display results
for i, (doc, cluster) in enumerate(zip(documents, clusters)):
    print(f"Cluster {cluster}: {doc}")
```

## Audio Processing

### Speech-to-Text (Transcription)

Basic transcription:

```python
from openai import OpenAI

client = OpenAI()

transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=open("speech.mp3", "rb"),
)

print(transcription.text)
```

### Transcription Options

```python
from openai import OpenAI

client = OpenAI()

# With language and prompt
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=open("speech.mp3", "rb"),
    language="en",  # ISO 639-1 language code
    prompt="This is a technical presentation about ",  # Priming prompt
    response_format="json",  # text, json, srt, verbose_json, vtt
    temperature=0.0,  # 0.0-1.0, lower is more deterministic
)

print(transcription.text)
```

### Verbose Transcription (Word Timestamps)

```python
from openai import OpenAI
import json

client = OpenAI()

transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=open("speech.mp3", "rb"),
    response_format="verbose_json",
)

print(f"Text: {transcription.text}")
print(f"Language: {transcription.language}")
print(f"Duration: {transcription.duration}")

# Word-level timestamps
if hasattr(transcription, 'words'):
    for word in transcription.words[:5]:  # First 5 words
        print(f"{word.start}-{word.end}: {word.word}")
```

### Translation (Non-English to English)

```python
from openai import OpenAI

client = OpenAI()

translation = client.audio.translations.create(
    model="whisper-1",
    file=open("foreign_speech.mp3", "rb"),
)

print(translation.text)  # Translated to English
```

### Streaming Audio Transcription

For large files or streaming:

```python
from openai import OpenAI

client = OpenAI()

# Use with smaller audio chunks
def transcribe_audio_chunk(audio_data: bytes) -> str:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_data,  # Can be bytes
    )
    return transcription.text

# Process audio in chunks
with open("large_audio.mp3", "rb") as f:
    chunk_size = 1024 * 30  # 30KB chunks
    while chunk := f.read(chunk_size):
        text = transcribe_audio_chunk(chunk)
        print(text, end=" ")
```

### Supported Audio Formats

- mp3
- mp4
- mpeg
- mpga
- m4a
- wav
- webm

**Limits:**
- Max file size: 25 MB
- Max duration: 5 hours (for some formats)

## Text-to-Speech (Speech Synthesis)

### Basic Speech Generation

```python
from openai import OpenAI

client = OpenAI()

speech = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello, welcome to our application!",
)

# Save to file
with open("output.mp3", "wb") as f:
    f.write(speech.read())
```

### Voice Options

| Voice | Description |
|-------|-------------|
| `alloy` | Balanced, natural |
| `echo` | Deep, resonant |
| `fable` | Warm, storytelling |
| `onyx` | Professional, clear |
| `nova` | Bright, energetic |
| `shimmer` | Soft, gentle |

### Model Options

| Model | Speed | Quality | Cost |
|-------|-------|---------|------|
| `tts-1` | Standard | High | $0.015/1K chars |
| `tts-1-hd` | Standard | Higher | $0.030/1K chars |

### Advanced Speech Options

```python
from openai import OpenAI

client = OpenAI()

# With custom response format
speech = client.audio.speech.create(
    model="tts-1-hd",  # Higher quality
    voice="nova",
    input="The weather today is sunny and warm.",
    response_format="wav",  # mp3, wav, flac, pcm, ogg
)

# Stream directly to file
with open("output.wav", "wb") as f:
    for chunk in speech.iter_bytes():
        f.write(chunk)
```

### Async Speech Generation

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def generate_speech(text: str, voice: str = "alloy") -> bytes:
    speech = await client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )
    return await speech.read()

async def main():
    audio_data = await generate_speech("Hello from async!")
    
    with open("async_output.mp3", "wb") as f:
        f.write(audio_data)

asyncio.run(main())
```

### Streaming Speech to Speaker

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def stream_speech_to_speaker(text: str):
    speech = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )
    
    # Stream chunks (requires audio playback library)
    async for chunk in speech.iter_bytes():
        # Send to speaker/playback system
        play_audio_chunk(chunk)

async def play_audio_chunk(chunk: bytes):
    # Implement with your audio library (e.g., pygame, sounddevice)
    pass
```

## Best Practices

### Embeddings

1. **Choose the right model:** Use 3-small for cost-effectiveness, 3-large for best performance
2. **Reduce dimensions** when possible for faster search and lower storage
3. **Batch requests** to reduce API calls and improve throughput
4. **Cache embeddings** for static content to avoid redundant API calls
5. **Normalize vectors** before cosine similarity calculations
6. **Use appropriate indexing:** FAISS, Annoy, or HNSW for large-scale search

### Audio Transcription

1. **Specify language** when known for better accuracy
2. **Use prompts** to prime the model for domain-specific content
3. **Choose response format** based on needs (json for timestamps, srt for subtitles)
4. **Process in chunks** for very long audio files
5. **Use verbose_json** when word-level timing is needed

### Text-to-Speech

1. **Choose voice appropriately:** Different voices suit different use cases
2. **Use tts-1-hd** for premium quality applications
3. **Stream output** for real-time applications
4. **Cache generated speech** for frequently used phrases
5. **Consider response format:** wav for editing, mp3 for storage efficiency

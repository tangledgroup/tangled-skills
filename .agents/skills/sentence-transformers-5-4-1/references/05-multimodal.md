# Multimodal Applications

Guide to using Sentence Transformers for image, audio, and video processing alongside text.

## Overview

Sentence Transformers supports multimodal models that can:
- Encode images and text into a shared embedding space
- Process audio clips and transcriptions
- Handle video frames with captions
- Perform cross-modal retrieval (text-to-image, image-to-text)

## Image-Text Models

### CLIP Models

CLIP (Contrastive Language-Image Pre-training) models encode both images and text:

```python
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np

# Load CLIP model
model = SentenceTransformer("clip-ViT-B-32")

# Text queries
texts = [
    "A cute cat sitting on a windowsill",
    "Beautiful sunset over the ocean",
    "Person playing guitar outdoors",
]

# Images (PIL images or file paths)
images = [
    Image.open("cat.jpg"),
    Image.open("sunset.jpg"),
    Image.open("guitar.jpg"),
]

# Encode both modalities
text_embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
image_embeddings = model.encode(images, normalize_embeddings=True, convert_to_numpy=True)

print(f"Text embeddings shape: {text_embeddings.shape}")  # (3, 512)
print(f"Image embeddings shape: {image_embeddings.shape}")  # (3, 512)

# Both are in the same embedding space!
```

### Text-to-Image Retrieval

```python
from sentence_transformers import SentenceTransformer
from PIL import Image
import glob
import numpy as np

model = SentenceTransformer("clip-ViT-B-32")

# Load image corpus
image_paths = glob.glob("dataset/images/*.jpg")
images = [Image.open(path) for path in image_paths]

# Encode all images (do once, cache results)
image_embeddings = model.encode(
    images,
    normalize_embeddings=True,
    convert_to_numpy=True,
    batch_size=64,
    show_progress_bar=True
)

def text_to_image_search(query, top_k=5):
    """Search for images given a text query"""
    # Encode query
    query_embedding = model.encode(query, normalize_embeddings=True)
    
    # Compute similarities
    similarities = image_embeddings @ query_embedding
    
    # Get top-k results
    top_indices = similarities.argsort()[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        results.append({
            'path': image_paths[idx],
            'score': float(similarities[idx])
        })
    
    return results

# Search
results = text_to_image_search("a dog playing in the park", top_k=5)
for result in results:
    print(f"{result['score']:.3f} - {result['path']}")
```

### Image-to-Text Retrieval

```python
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np

model = SentenceTransformer("clip-ViT-B-32")

# Image query
query_image = Image.open("query.jpg")
query_embedding = model.encode(query_image, normalize_embeddings=True)

# Text corpus (captions, descriptions, etc.)
text_corpus = [
    "A golden retriever playing fetch in the park",
    "Sunset over mountains with snow-capped peaks",
    "Person riding a bicycle on beach",
    "Cat sleeping on windowsill",
]

text_embeddings = model.encode(text_corpus, normalize_embeddings=True)

# Find most similar texts
similarities = text_embeddings @ query_embedding
top_indices = similarities.argsort()[::-1][:3]

print("Most similar text descriptions:")
for idx in top_indices:
    print(f"{similarities[idx]:.3f} - {text_corpus[idx]}")
```

### Zero-Shot Image Classification

```python
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np

model = SentenceTransformer("clip-ViT-B-32")

# Load image
image = Image.open("example.jpg")
image_embedding = model.encode(image, normalize_embeddings=True)

# Define possible classes as text prompts
classes = [
    "A photo of a cat",
    "A photo of a dog",
    "A photo of a bird",
    "A photo of a car",
    "A photo of a person",
]

class_embeddings = model.encode(classes, normalize_embeddings=True)

# Compute similarities
similarities = class_embeddings @ image_embedding

# Get predicted class
predicted_class = classes[similarities.argmax()]
confidence = similarities.max().item()

print(f"Predicted: {predicted_class} (confidence: {confidence:.3f})")

# Show all scores
for cls, sim in zip(classes, similarities):
    print(f"  {cls}: {sim:.3f}")
```

## Advanced CLIP Usage

### Custom Prompts

```python
from sentence_transformers import SentenceTransformer
from PIL import Image

model = SentenceTransformer("clip-ViT-B-32")

# Use custom text templates for better classification
image = Image.open("example.jpg")
image_embedding = model.encode(image, normalize_embeddings=True)

# Template-ensembled prompts
templates = [
    "A photo of a {}.",
    "A picture of a {}.",
    "A image of a {}.",
    "This is a {}.",
]

classes = ["cat", "dog", "bird"]

# Ensemble scores across templates
all_scores = {}
for cls in classes:
    prompts = [template.format(cls) for template in templates]
    prompt_embeddings = model.encode(prompts, normalize_embeddings=True)
    
    # Average similarity across templates
    similarities = prompt_embeddings @ image_embedding
    all_scores[cls] = similarities.mean().item()

# Get prediction
predicted_class = max(all_scores, key=all_scores.get)
print(f"Predicted: {predicted_class}")
for cls, score in sorted(all_scores.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cls}: {score:.3f}")
```

### Fine-Tuned CLIP Models

```python
from sentence_transformers import SentenceTransformer
from PIL import Image

# Use domain-specific fine-tuned CLIP models
# Fashion-specific
model = SentenceTransformer("clip-ViT-B-32-fashion")

# Medical imaging
model = SentenceTransformer("clip-ViT-B-32-medical")

# Food classification
model = SentenceTransformer("clip-ViT-B-32-food")

# Use same API as base CLIP
image = Image.open("fashion_item.jpg")
embedding = model.encode(image)
```

## Audio Processing

### Audio Embeddings

```python
from sentence_transformers import SentenceTransformer
import torch

# Load audio model (Wav2Vec2 or similar)
model = SentenceTransformer("sentence-transformers/Wav2Vec2-base")

# Load audio files (as numpy arrays or file paths)
audio_files = [
    "speech1.wav",
    "speech2.wav",
    "speech3.wav",
]

# Encode audio files
embeddings = model.encode(audio_files, batch_size=8, show_progress_bar=True)
print(f"Audio embeddings shape: {embeddings.shape}")
```

### Audio-Text Retrieval

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Load audio-text model
model = SentenceTransformer("sentence-transformers/audio-text-clip")

# Audio query
audio_query = "query.wav"
audio_embedding = model.encode(audio_query, normalize_embeddings=True)

# Text corpus
texts = [
    "Someone saying hello",
    "Music playing in the background",
    "Dog barking loudly",
    "Car engine starting",
]

text_embeddings = model.encode(texts, normalize_embeddings=True)

# Find most similar descriptions
similarities = text_embeddings @ audio_embedding
top_idx = similarities.argmax()

print(f"Most likely: {texts[top_idx]} (score: {similarities[top_idx]:.3f})")
```

## Video Processing

### Video Frame Embeddings

```python
from sentence_transformers import SentenceTransformer
from PIL import Image
import cv2
import numpy as np

model = SentenceTransformer("clip-ViT-B-32")

def extract_video_frames(video_path, max_frames=10):
    """Extract key frames from video"""
    cap = cv2.VideoCapture(video_path)
    frames = []
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, total_frames // max_frames)
    
    for i in range(0, total_frames, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if ret:
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            frames.append(pil_image)
    
    cap.release()
    return frames

def encode_video(video_path):
    """Encode video as average of frame embeddings"""
    frames = extract_video_frames(video_path)
    
    # Encode all frames
    frame_embeddings = model.encode(
        frames,
        normalize_embeddings=True,
        batch_size=8,
        convert_to_numpy=True
    )
    
    # Average pooling across frames
    video_embedding = frame_embeddings.mean(axis=0, keepdims=True)
    return video_embedding

# Encode videos
video1_embedding = encode_video("video1.mp4")
video2_embedding = encode_video("video2.mp4")

# Compute similarity
from sklearn.metrics.pairwise import cosine_similarity
similarity = cosine_similarity(video1_embedding, video2_embedding)[0, 0]
print(f"Video similarity: {similarity:.3f}")
```

### Video-Text Search

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("clip-ViT-B-32")

# Video corpus (pre-computed embeddings)
video_paths = ["video1.mp4", "video2.mp4", "video3.mp4"]
video_embeddings = np.array([
    encode_video(path) for path in video_paths
])

def search_videos_by_text(query, top_k=3):
    """Search videos using text query"""
    query_embedding = model.encode(query, normalize_embeddings=True)
    
    # Compute similarities
    similarities = video_embeddings @ query_embedding
    
    # Get top-k results
    top_indices = similarities.argsort()[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        results.append({
            'path': video_paths[idx],
            'score': float(similarities[idx])
        })
    
    return results

# Search
results = search_videos_by_text("cooking tutorial pasta", top_k=3)
for result in results:
    print(f"{result['score']:.3f} - {result['path']}")
```

## Multimodal Clustering

### Joint Image-Text Clustering

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from PIL import Image
import numpy as np

model = SentenceTransformer("clip-ViT-B-32")

# Mixed modalities
images = [Image.open(f"image{i}.jpg") for i in range(10)]
texts = ["A cat", "A dog", "A car", ...]  # 10 text descriptions

# Encode all into same space
image_embeddings = model.encode(images, normalize_embeddings=True)
text_embeddings = model.encode(texts, normalize_normalize=True)

# Combine embeddings
all_embeddings = np.vstack([image_embeddings, text_embeddings])
all_labels = ['img'] * len(images) + ['txt'] * len(texts)

# Cluster
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(all_embeddings)

# Display clusters
for cluster_id in range(3):
    cluster_items = [
        (i, all_labels[i]) 
        for i in range(len(all_embeddings)) 
        if clusters[i] == cluster_id
    ]
    print(f"\nCluster {cluster_id}:")
    for idx, modality in cluster_items:
        print(f"  {modality} item {idx}")
```

## Model Options

| Model | Modalities | Dimensions | Best For |
|-------|------------|------------|----------|
| `clip-ViT-B-32` | Image-Text | 512 | General multimodal |
| `clip-ViT-L-14` | Image-Text | 768 | Higher accuracy |
| `clip-resnet-50` | Image-Text | 2048 | Faster inference |
| `sentence-transformers/Wav2Vec2-base` | Audio | 768 | Speech processing |
| `BeIR/multilingual-clip-ViT-B-32` | Image-Text (ML) | 512 | Multilingual |

## Performance Tips

1. **Batch processing**: Use batch_size for encoding multiple images/audio files
2. **Cache embeddings**: Pre-compute and store corpus embeddings
3. **Resize images**: CLIP models expect specific sizes (224x224, 336x336)
4. **GPU acceleration**: Multimodal models benefit significantly from GPU
5. **Use appropriate model size**: ViT-B-32 for speed, ViT-L-14 for accuracy

## Troubleshooting

### Issue: Images not loading correctly

**Solution**: Ensure images are in RGB format and correct size:
```python
from PIL import Image
image = Image.open("path.jpg").convert("RGB").resize((224, 224))
```

### Issue: Audio format errors

**Solution**: Convert to mono and correct sample rate:
```python
import soundfile as sf
data, sr = sf.read("audio.wav")
if len(data.shape) > 1:
    data = data.mean(axis=1)  # Convert to mono
```

### Issue: Poor cross-modal retrieval

**Solution**: 
- Use domain-specific fine-tuned models
- Try template ensembling for text prompts
- Consider fine-tuning on your domain data

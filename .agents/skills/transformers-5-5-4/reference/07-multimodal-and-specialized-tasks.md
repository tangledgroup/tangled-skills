# Multimodal and Specialized Tasks - Complete Guide

Comprehensive guide to vision, audio, multimodal models, and specialized task implementations in Transformers 5.5.4.

## Overview

This reference covers:
- **Vision Models**: Image classification, detection, segmentation
- **Audio Models**: Speech recognition, audio classification
- **Multimodal Models**: Vision-language, document understanding
- **Specialized Tasks**: Video, depth estimation, visual question answering

## Vision Models

### Image Classification

Basic image classification with pretrained models:

```python
from transformers import AutoModelForImageClassification, AutoImageProcessor
from PIL import Image
import requests

# Load model and processor
model_name = "google/vit-base-patch16-224"
model = AutoModelForImageClassification.from_pretrained(model_name)
processor = AutoImageProcessor.from_pretrained(model_name)

# Load image
url = "https://images.unsplash.com/photo-1543362906-acfc16ae6efb"
image = Image.open(requests.get(url, stream=True).raw)

# Preprocess
inputs = processor(images=image, return_tensors="pt")

# Predict
import torch
with torch.no_grad():
    outputs = model(**inputs)
    probabilities = torch.softmax(outputs.logits, dim=-1)

# Get prediction
predicted_class_id = torch.argmax(probabilities).item()
confidence = probabilities[0, predicted_class_id].item()
label = model.config.id2label[predicted_class_id]

print(f"Predicted: {label} (confidence: {confidence:.4f})")
```

### Using Pipeline for Image Classification

```python
from transformers import pipeline
from PIL import Image

# Create classifier
classifier = pipeline("image-classification")

# From URL
result = classifier("https://images.unsplash.com/photo-1543362906-acfc16ae6efb")
print(result)  # [{'label': 'Siamese cat', 'score': 0.97}]

# From PIL Image
image = Image.open("cat.jpg")
result = classifier(image)

# With custom model
classifier = pipeline(
    "image-classification",
    model="google/vit-base-patch16-224"
)
```

### Object Detection

Detect objects in images with bounding boxes:

```python
from transformers import AutoModelForObjectDetection, AutoImageProcessor
from PIL import Image
import torch

# Load model and processor
model_name = "facebook/detr-resnet-50"
model = AutoModelForObjectDetection.from_pretrained(model_name)
processor = AutoImageProcessor.from_pretrained(model_name)

# Load image
image = Image.open("image.jpg")

# Preprocess
inputs = processor(images=image, return_tensors="pt")

# Predict
with torch.no_grad():
    outputs = model(**inputs)

# Post-process
target_sizes = [image.size[::-1]]  # (height, width)
results = processor.post_process_object_detection(
    outputs,
    threshold=0.5,
    target_sizes=target_sizes
)

# Parse results
bbox = results[0]["boxes"]
labels = results[0]["labels"]
scores = results[0]["scores"]

for box, label, score in zip(bbox, labels, scores):
    print(f"Label: {model.config.id2label[label.item()]}, "
          f"Score: {score.item():.4f}, "
          f"Box: {box.tolist()}")
```

### Image Segmentation

Semantic and instance segmentation:

```python
from transformers import AutoModelForImageSegmentation, AutoImageProcessor
from PIL import Image
import torch
import numpy as np

# Load model
model_name = "facebook/detr-resnet-50-panoptic"
model = AutoModelForImageSegmentation.from_pretrained(model_name)
processor = AutoImageProcessor.from_pretrained(model_name)

# Load image
image = Image.open("image.jpg")

# Preprocess
inputs = processor(images=image, return_tensors="pt")

# Predict
with torch.no_grad():
    outputs = model(**inputs)

# Post-process
target_sizes = [image.size[::-1]]
segmentation = processor.post_process_semantic_segmentation(
    outputs,
    target_sizes=target_sizes
)[0]

# Convert to RGB mask
colors = np.random.randint(0, 255, (len(model.config.labels), 3))
mask_image = colors[segmentation.cpu().numpy()]

# Display
import matplotlib.pyplot as plt
plt.imshow(mask_image)
plt.show()
```

### Depth Estimation

Estimate depth from single images:

```python
from transformers import AutoModel, AutoImageProcessor
import cv2
import torch
import numpy as np

# Load model
model_name = "Intel/dpt-large"
model = AutoModel.from_pretrained(model_name)
processor = AutoImageProcessor.from_pretrained(model_name)

# Load image
image = cv2.imread("scene.jpg")
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Preprocess
inputs = processor(images=image_rgb, return_tensors="pt")

# Predict
with torch.no_grad():
    outputs = model(**inputs)

# Get depth map
predicted_depth = torch.nn.functional.interpolate(
    outputs.predicted_depth.unsqueeze(1),
    size=image.shape[:2][::-1],
    mode="bilinear",
    align_corners=False
).squeeze(1)

# Normalize and visualize
depth_np = predicted_depth.cpu().numpy()[0]
depth_min, depth_max = depth_np.min(), depth_np.max()
depth_normalized = (depth_np - depth_min) / (depth_max - depth_min)

# Save depth map
cv2.imwrite("depth.png", (depth_normalized * 255).astype(np.uint8))
```

## Audio Models

### Automatic Speech Recognition (ASR)

Transcribe speech to text:

```python
from transformers import AutoModelForCTC, AutoProcessor
import torch
import soundfile as sf

# Load model and processor
model_name = "openai/whisper-large-v3"
model = AutoModelForCTC.from_pretrained(model_name)
processor = AutoProcessor.from_pretrained(model_name)

# Load audio
audio, sample_rate = sf.read("audio.wav")

# Preprocess
inputs = processor(
    audio,
    sampling_rate=sample_rate,
    return_tensors="pt",
    padding=True
)

# Transcribe
with torch.no_grad():
    outputs = model(**inputs)
    predicted_ids = torch.argmax(outputs.logits, dim=-1)

# Decode
transcription = processor.batch_decode(predicted_ids)[0]
print(f"Transcription: {transcription}")
```

### Using Pipeline for ASR

```python
from transformers import pipeline

# Create transcriber
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")

# From file
result = transcriber("audio.wav")
print(result["text"])

# From numpy array
import soundfile as sf
audio, sample_rate = sf.read("audio.wav")
result = transcriber(audio, sampling_rate=sample_rate)

# With timestamps
result = transcriber(
    "audio.wav",
    return_timestamps=True
)
print(result["chunks"])  # List of {text, timestamp}

# Specify language
result = transcriber(
    "audio.wav",
    generate_kwargs={"language": "en"}
)
```

### Audio Classification

Classify audio segments:

```python
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
import torch
import soundfile as sf

# Load model
model_name = "superb/hubert-large-superb-er"
model = AutoModelForAudioClassification.from_pretrained(model_name)
extractor = AutoFeatureExtractor.from_pretrained(model_name)

# Load audio
audio, sample_rate = sf.read("audio.wav")

# Preprocess
inputs = extractor(
    audio,
    sampling_rate=sample_rate,
    return_tensors="pt",
    padding=True
)

# Classify
with torch.no_grad():
    outputs = model(**inputs)
    probabilities = torch.softmax(outputs.logits, dim=-1)

# Get prediction
predicted_class = torch.argmax(probabilities).item()
confidence = probabilities[0, predicted_class].item()
label = model.config.id2label[predicted_class]

print(f"Predicted: {label} (confidence: {confidence:.4f})")
```

### Speaker Verification

Verify if two audio samples are from the same speaker:

```python
from transformers import AutoModel, AutoFeatureExtractor
import torch
import soundfile as sf
from sklearn.metrics.pairwise import cosine_similarity

# Load model
model_name = "SpeechBrain/ecapa_tdnn_librispeech"
model = AutoModel.from_pretrained(model_name)
extractor = AutoFeatureExtractor.from_pretrained(model_name)

# Load audio samples
audio1, sr1 = sf.read("speaker1_sample1.wav")
audio2, sr2 = sf.read("speaker1_sample2.wav")

# Extract embeddings
def extract_embedding(audio, sample_rate):
    inputs = extractor(audio, sampling_rate=sample_rate, return_tensors="pt", padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Get speaker embedding (last hidden state)
    embedding = outputs.last_hidden_state.mean(dim=1)
    embedding = torch.nn.functional.normalize(embedding, dim=-1)
    return embedding

embedding1 = extract_embedding(audio1, sr1)
embedding2 = extract_embedding(audio2, sr2)

# Compute similarity
similarity = cosine_similarity(embedding1.cpu().numpy(), embedding2.cpu().numpy())[0, 0]

threshold = 0.6
if similarity > threshold:
    print(f"Same speaker (similarity: {similarity:.4f})")
else:
    print(f"Different speakers (similarity: {similarity:.4f})")
```

## Multimodal Models

### Vision-Language Models (BLIP)

Image captioning and visual question answering:

```python
from transformers import BlipForQuestionAnswering, BlipProcessor
from PIL import Image

# Load model and processor
model_name = "Salesforce/blip-vqa-base"
model = BlipForQuestionAnswering.from_pretrained(model_name)
processor = BlipProcessor.from_pretrained(model_name)

# Load image
image = Image.open("image.jpg")

# Visual question answering
question = "What color is the cat?"
inputs = processor(image, question, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)

# Generate answer
answer_ids = outputs.logits.argmax(dim=-1)
answer = processor.decode(answer_ids, skip_special_tokens=True)
print(f"Answer: {answer}")
```

### Image Captioning

Generate captions for images:

```python
from transformers import BlipForConditionalGeneration, BlipProcessor
from PIL import Image

# Load model
model_name = "Salesforce/blip-image-captioning-large"
model = BlipForConditionalGeneration.from_pretrained(model_name)
processor = BlipProcessor.from_pretrained(model_name)

# Load image
image = Image.open("image.jpg")

# Generate caption
inputs = processor(image, return_tensors="pt")

with torch.no_grad():
    output_ids = model.generate(
        **inputs,
        max_new_tokens=50,
        num_return_sequences=3,  # Generate multiple captions
        no_repeat_ngram_size=2
    )

# Decode captions
captions = processor.batch_decode(output_ids, skip_special_tokens=True)
for i, caption in enumerate(captions):
    print(f"Caption {i+1}: {caption}")
```

### Document Question Answering

QA on documents with layout information:

```python
from transformers import LayoutLMv3ForQuestionAnswering, LayoutLMv3Processor
from PIL import Image

# Load model
model_name = "impira/layoutlm-document-qa"
model = LayoutLMv3ForQuestionAnswering.from_pretrained(model_name)
processor = LayoutLMv3Processor.from_pretrained(model_name)

# Prepare document
image = Image.open("invoice.png")
question = "What is the total amount?"

# For LayoutLM, you need:
# 1. Image
# 2. Text tokens
# 3. Bounding boxes for each token

# Example with OCR-extracted data
text = "Invoice Total: $1,234.56"
bbox = [[0, 0, 200, 50]]  # [x0, y0, x1, y1]

inputs = processor(
    image,
    text,
    question,
    boxes=bbox,
    return_tensors="pt",
    padding=True
)

with torch.no_grad():
    outputs = model(**inputs)

# Extract answer
answer_start = torch.argmax(outputs.start_logits)
answer_end = torch.argmax(outputs.end_logits)

print(f"Answer span: {text[answer_start:item()]:answer_end.item()+1]}")
```

### Multimodal Document Understanding

Process documents with both text and images:

```python
from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import json

# Load model (Donut for document understanding)
model_name = "naver-clova-ix/donut-base-finetuned-cord"
model = VisionEncoderDecoderModel.from_pretrained(model_name)
processor = DonutProcessor.from_pretrained(model_name)

# Load document image
image = Image.open("document.png")

# Preprocess
pixel_values = processor(images=image, return_tensors="pt").pixel_values

# Generate
generated_ids = model.generate(pixel_values)

# Decode
prediction = processor.decode(generated_ids[0], skip_special_tokens=True)
parsed_output = json.loads(prediction)

print(json.dumps(parsed_output, indent=2))
```

## Video Models

### Video Classification

Classify video clips:

```python
from transformers import VideoMAEForVideoClassification, AutoImageProcessor
import torch
import numpy as np

# Load model
model_name = "microsoft/video-mae-base"
model = VideoMAEForVideoClassification.from_pretrained(model_name)
processor = AutoImageProcessor.from_pretrained(model_name)

# Prepare video frames (list of PIL images or numpy array)
# Shape: (num_frames, height, width, channels)
video_frames = [frame1, frame2, frame3, ...]  # List of frames

# Preprocess
inputs = processor(videos=video_frames, return_tensors="pt")

# Classify
with torch.no_grad():
    outputs = model(**inputs)
    probabilities = torch.softmax(outputs.logits, dim=-1)

# Get prediction
predicted_class = torch.argmax(probabilities).item()
confidence = probabilities[0, predicted_class].item()
label = model.config.id2label[predicted_class]

print(f"Predicted: {label} (confidence: {confidence:.4f})")
```

### Video Action Recognition

Recognize actions in videos:

```python
from transformers import VidotronForVideoClassification, AutoFeatureExtractor
import torch

# Load model
model_name = "google/vidotron-t-16m"
model = VidotronForVideoClassification.from_pretrained(model_name)
extractor = AutoFeatureExtractor.from_pretrained(model_name)

# Prepare video (tensor of shape [batch, channels, frames, height, width])
video_tensor = torch.randn(1, 3, 16, 224, 224)  # Example input

# Extract features
inputs = extractor(videos=video_tensor, return_tensors="pt")

# Classify
with torch.no_grad():
    outputs = model(**inputs)
    probabilities = torch.softmax(outputs.logits, dim=-1)

predicted_class = torch.argmax(probabilities).item()
label = model.config.id2label[predicted_class]
print(f"Action: {label}")
```

## Zero-Shot Tasks

### Zero-Shot Image Classification

Classify images without training on specific classes:

```python
from transformers import AutoModelForZeroShotImageClassification, AutoProcessor
from PIL import Image

# Load model
model_name = "laion/clip-vit-large-patch14"
model = AutoModelForZeroShotImageClassification.from_pretrained(model_name)
processor = AutoProcessor.from_pretrained(model_name)

# Load image
image = Image.open("image.jpg")

# Define candidate labels
candidate_labels = ["cat", "dog", "bird", "fish"]

# Preprocess
inputs = processor(
    images=image,
    text=candidate_labels,
    return_tensors="pt",
    padding=True
)

# Predict
with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)

# Get prediction
predicted_class_id = torch.argmax(probabilities).item()
confidence = probabilities[0, predicted_class_id].item()
label = candidate_labels[predicted_class_id]

print(f"Predicted: {label} (confidence: {confidence:.4f})")
```

### Zero-Shot Object Detection

Detect objects without specific training:

```python
from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor
from PIL import Image

# Load model
model_name = "google/owlvit-base-patch32"
model = AutoModelForZeroShotObjectDetection.from_pretrained(model_name)
processor = AutoProcessor.from_pretrained(model_name)

# Load image
image = Image.open("image.jpg")

# Define text prompts (what to look for)
text_inputs = ["a photo of a cat", "a photo of a dog", "a photo of a bird"]

# Preprocess
inputs = processor(images=image, text=text_inputs, return_tensors="pt")

# Predict
with torch.no_grad():
    outputs = model(**inputs)

# Post-process
target_sizes = [image.size[::-1]]
results = processor.post_process_zero_shot_object_detection(
    outputs,
    threshold=0.5,
    target_sizes=target_sizes
)

# Parse results
boxes = results[0]["boxes"]
labels = results[0]["labels"]
scores = results[0]["scores"]

for box, label, score in zip(boxes, labels, scores):
    print(f"Label: {text_inputs[label.item()]}, "
          f"Score: {score.item():.4f}, "
          f"Box: {box.tolist()}")
```

## Specialized Processors

### Combined Text-Image Processing

Process multiple modalities together:

```python
from transformers import AutoProcessor
from PIL import Image

# Load processor for multimodal model
model_name = "Salesforce/blip-image-captioning-large"
processor = AutoProcessor.from_pretrained(model_name)

# Process both image and text
image = Image.open("image.jpg")
text = "Describe this image"

inputs = processor(
    images=image,
    text=text,
    return_tensors="pt",
    padding=True
)

print(inputs.keys())  # dict_keys(['pixel_values', 'input_ids', 'attention_mask'])
```

### Feature Extractors for Audio

Extract audio features:

```python
from transformers import AutoFeatureExtractor
import soundfile as sf

# Load feature extractor
extractor = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")

# Load audio
audio, sample_rate = sf.read("audio.wav")

# Extract features
features = extractor(audio, sampling_rate=sample_rate, return_tensors="pt")
print(features.input_values.shape)  # torch.Size([1, sequence_length])
```

## Best Practices for Multimodal Models

1. **Use appropriate image sizes** - Most models expect 224x224 or 384x384
2. **Normalize inputs correctly** - Use the model's processor/feature extractor
3. **Batch processing** - Process multiple images/audio files together for efficiency
4. **GPU acceleration** - Multimodal models benefit significantly from GPU
5. **Check model card** - Each model may have specific input requirements

## Troubleshooting

### Image Size Mismatch

```python
# Check expected image size
processor = AutoImageProcessor.from_pretrained("model-name")
print(processor.size)  # {'height': 224, 'width': 224}

# Resize image to match
from PIL import Image
image = Image.open("image.jpg")
image = image.resize((224, 224))
```

### Audio Sample Rate Issues

```python
# Check expected sample rate
extractor = AutoFeatureExtractor.from_pretrained("model-name")
print(extractor.sampling_rate)  # e.g., 16000

# Resample if needed
import soundfile as sf
from scipy.signal import resample

audio, original_sr = sf.read("audio.wav")
target_sr = 16000

if original_sr != target_sr:
    num_samples = int(len(audio) * target_sr / original_sr)
    audio = resample(audio, num_samples)
```

### Memory Issues with Large Images

```python
# Resize large images before processing
from PIL import Image

image = Image.open("large_image.jpg")
max_size = 1024
image.thumbnail((max_size, max_size))  # Resize while maintaining aspect ratio

# Or use smaller model
model_name = "google/vit-tiny-patch16-224"  # Smaller variant
```

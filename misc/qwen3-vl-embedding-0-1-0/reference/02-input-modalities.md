# Input Modalities

## Multimodal Object Specification

Each input to the embedding model is a dictionary that can contain any combination of the following keys:

### Text

- **Type**: String or list of strings
- Single text string or multiple text segments combined into one input

```python
{"text": "A woman playing with her dog on a beach at sunset."}
{"text": ["First paragraph", "Second paragraph"]}
```

### Image

- **Supported formats**:
  - Local file path (string)
  - URL / network path (string)
  - `PIL.Image.Image` instance
  - List of any combination above (multiple images in one input)

```python
{"image": "path/to/photo.jpg"}
{"image": "https://example.com/image.png"}
{"image": pil_image_instance}
{"image": ["photo1.jpg", "photo2.jpg"]}
```

### Video

- **Supported formats**:
  - Local file path (string)
  - URL / network path (string)
  - Sequence of frames (list of image paths or `PIL.Image.Image` instances)
  - List of any combination above (multiple videos in one input)

```python
{"video": "path/to/video.mp4"}
{"video": "https://example.com/video.mp4"}
{"video": ["frame1.jpg", "frame2.jpg", "frame3.jpg"]}
```

### Video Sampling Settings

Only effective when video input is a file path:

- **fps**: Frame sampling rate (frames per second), default `1.0`
- **max_frames**: Maximum number of frames to sample, default `64`

```python
{
    "video": "path/to/video.mp4",
    "fps": 2.0,
    "max_frames": 128
}
```

### Instruction (Optional)

Task description that guides the embedding toward specific semantics:

```python
{
    "text": "What is shown in this image?",
    "instruction": "Find images matching this description."
}
```

- Default instruction if omitted: `"Represent the user's input"`
- Using task-specific instructions typically improves performance by 1-5%
- Write instructions in English for best results, even in multilingual contexts

## Mixed-Modal Inputs

Any combination of text, image, and video can be provided in a single input dictionary:

```python
# Text + Image
{
    "text": "A description of the scene",
    "image": "path/to/image.jpg"
}

# Text + Video
{
    "text": "What happens in this video?",
    "video": "path/to/video.mp4",
    "fps": 1.0,
    "max_frames": 64
}

# Image + Video (no text)
{
    "image": "reference_image.jpg",
    "video": "clip.mp4"
}

# All three modalities
{
    "text": "Compare this image with the video",
    "image": "photo.jpg",
    "video": "clip.mp4"
}
```

## Batch Input Format

The embedding model accepts a **list of input dictionaries**:

```python
inputs = [
    {"text": "First query"},
    {"image": "photo1.jpg"},
    {"text": "Second query", "image": "photo2.jpg"},
    {"video": "clip.mp4", "fps": 1.0}
]

embeddings = model.process(inputs)
# Returns numpy array of shape (len(inputs), embedding_dim)
```

## Image Resolution Handling

The model automatically handles image resolution within configured bounds:

- `min_pixels=4096`: Minimum pixels for input images
- `max_pixels=1843200`: Maximum pixels per image (~1280x1440)
- `total_pixels=7864320`: Maximum total pixels for video input (multiplied by 2 internally)
  - For a 16-frame video, each frame can have up to ~983040 pixels (~1280x768)

Images outside these bounds are automatically resized while maintaining aspect ratio.

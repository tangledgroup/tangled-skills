# Image Generation and Content Moderation

Comprehensive guide to generating images with DALL-E 3 and GPT-Image models, plus content moderation for safety filtering.

## Image Generation

### Basic Image Generation (DALL-E 3)

```python
from openai import OpenAI

client = OpenAI()

response = client.images.generate(
    model="dall-e-3",
    prompt="A cute baby sea otter floating on its back in crystal clear water",
    size="1024x1024",
    n=1,  # Number of images to generate
)

# Get image URL (expires after 1 hour)
image_url = response.data[0].url
print(image_url)

# Or get base64 encoded image
if hasattr(response.data[0], 'b64_json'):
    import base64
    image_data = base64.b64decode(response.data[0].b64_json)
    
    with open("output.png", "wb") as f:
        f.write(image_data)
```

### Model Options

| Model | Description | Max Size |
|-------|-------------|----------|
| `dall-e-3` | Latest, highest quality | 1024x1024, 1792x1024, 1024x1792 |
| `dall-e-2` | Legacy, faster | 1024x1024, 512x512, 256x256 |

### Size Options (DALL-E 3)

- `1024x1024` - Square (default)
- `1792x1024` - Landscape
- `1024x1792` - Portrait

### Quality and Style

```python
from openai import OpenAI

client = OpenAI()

response = client.images.generate(
    model="dall-e-3",
    prompt="A futuristic city with flying cars",
    size="1024x1024",
    quality="hd",  # "standard" or "hd" (hd costs more)
    style="vivid",  # "vivid" or "natural"
    n=1,
)

print(response.data[0].url)
```

**Quality:**
- `standard` - Standard quality, lower cost
- `hd` - High definition, higher cost

**Style:**
- `vivid` - Highly detailed, artistic, saturated colors
- `natural` - More realistic, natural tones

### Response Formats

```python
from openai import OpenAI

client = OpenAI()

# URL format (default)
response = client.images.generate(
    model="dall-e-3",
    prompt="A sunset over mountains",
    size="1024x1024",
    response_format="url",  # url or b64_json
)

print(response.data[0].url)

# Base64 format
response = client.images.generate(
    model="dall-e-3",
    prompt="A sunset over mountains",
    size="1024x1024",
    response_format="b64_json",
)

import base64
image_data = base64.b64decode(response.data[0].b64_json)

with open("sunset.png", "wb") as f:
    f.write(image_data)
```

### Generating Multiple Images

```python
from openai import OpenAI

client = OpenAI()

# Generate up to 10 images (DALL-E 3), more for DALL-E 2
response = client.images.generate(
    model="dall-e-3",
    prompt="Different styles of cats wearing hats",
    size="1024x1024",
    n=10,  # Maximum for DALL-E 3 is 1 (use variations instead)
)

for i, image in enumerate(response.data):
    print(f"Image {i+1}: {image.url}")
```

### Image Variations

Create variations of an existing image:

```python
from openai import OpenAI

client = OpenAI()

# Generate variations from an image URL
response = client.images.variations.create(
    model="dall-e-2",  # Only DALL-E 2 supports variations
    image=open("input.png", "rb"),
    n=2,
    size="1024x1024",
)

for i, image in enumerate(response.data):
    print(f"Variation {i+1}: {image.url}")
```

**Requirements:**
- Image must be square (1024x1024 recommended)
- Only DALL-E 2 supports this feature
- Image must be hosted URL or uploaded file

### Image Edits (Inpainting)

Edit specific parts of an image using a mask:

```python
from openai import OpenAI

client = OpenAI()

# Edit image with mask (white areas will be edited)
response = client.images.edits.create(
    model="dall-e-2",  # Only DALL-E 2 supports edits
    image=open("base_image.png", "rb"),
    mask=open("mask.png", "rb"),  # Optional, if not provided entire image can be edited
    prompt="Add a top hat to the person",
    n=1,
    size="1024x1024",
)

print(response.data[0].url)
```

**Requirements:**
- Mask should be PNG with transparency or black/white
- White/transparent areas indicate where to edit
- Only DALL-E 2 supports this feature

### Async Image Generation

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def generate_image(prompt: str) -> str:
    response = await client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )
    return response.data[0].url

async def generate_multiple_images(prompts: list) -> list:
    tasks = [generate_image(prompt) for prompt in prompts]
    urls = await asyncio.gather(*tasks)
    return urls

async def main():
    prompts = [
        "A cute robot gardening",
        "A dragon reading a book",
        "An astronaut playing guitar",
    ]
    
    urls = await generate_multiple_images(prompts)
    for i, url in enumerate(urls):
        print(f"Image {i+1}: {url}")

asyncio.run(main())
```

## GPT-Image (Newer Model)

Generate images with the newer GPT-Image model:

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-image-1",
    input="A serene forest with a small wooden cabin",
)

# Check if response contains image
if hasattr(response, 'output') and response.output:
    for output in response.output:
        if output.type == "image":
            print(output.image_url)
```

## Content Moderation

Moderate content to detect harmful or inappropriate text, images, or conversations.

### Text Moderation

```python
from openai import OpenAI

client = OpenAI()

moderation = client.moderations.create(
    input="I am planning to commit a crime and here's how...",
)

# Check results
result = moderation.results[0]

print(f"Flagged: {result.flagged}")
print(f"Categories:")
for category, flagged in result.categories.items():
    print(f"  {category}: {flagged}")

print(f"Category Scores:")
for category, score in result.category_scores.items():
    print(f"  {category}: {score:.4f}")
```

### Moderation Categories

| Category | Description |
|----------|-------------|
| `sexual` | Sexually explicit content |
| `sexual/minors` | Sexual content involving minors |
| `violence` | Violent content |
| `violence/graphic` | Graphically violent content |
| `self-harm` | Self-harm content |
| `hate` | Hate speech |
| `harassment` | Harassment or bullying |
| `harassment/threatening` | Threatening harassment |
| `illegal` | Illegal activities |
| `sexual/violence` | Sexual violence |

### Moderating Multiple Inputs

```python
from openai import OpenAI

client = OpenAI()

moderation = client.moderations.create(
    input=[
        "This is a harmless message",
        "I want to hurt someone",
        "How do I make a cake?",
    ],
)

for i, result in enumerate(moderation.results):
    status = "⚠️ FLAGGED" if result.flagged else "✅ OK"
    print(f"{status} - Input {i+1}")
    
    if result.flagged:
        for category, flagged in result.categories.items():
            if flagged:
                print(f"  Reason: {category}")
```

### Chat Moderation Helper

```python
from openai import OpenAI

client = OpenAI()

def should_moderate_message(message: str) -> bool:
    """Check if a message should be moderated."""
    moderation = client.moderations.create(input=message)
    return moderation.results[0].flagged

def moderate_chat_session(messages: list) -> list:
    """Filter out inappropriate messages from a chat session."""
    clean_messages = []
    
    for msg in messages:
        content = msg.get("content", "")
        
        if not should_moderate_message(content):
            clean_messages.append(msg)
        else:
            print(f"Message flagged: {content[:50]}...")
    
    return clean_messages

# Example usage
chat_messages = [
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm doing well, thank you!"},
    {"role": "user", "content": "Inappropriate content here"},
    {"role": "assistant", "content": "Let's keep the conversation appropriate."},
]

clean_chat = moderate_chat_session(chat_messages)
print(f"Clean messages: {len(clean_chat)} out of {len(chat_messages)}")
```

### Custom Moderation Thresholds

```python
from openai import OpenAI

client = OpenAI()

def custom_moderation(text: str, threshold: float = 0.5) -> dict:
    """Moderate with custom score thresholds."""
    moderation = client.moderations.create(input=text)
    result = moderation.results[0]
    
    # Check specific category scores against threshold
    concerning_categories = {
        'violence': result.category_scores.get('violence', 0),
        'hate': result.category_scores.get('hate', 0),
        'harassment': result.category_scores.get('harassment', 0),
        'self-harm': result.category_scores.get('self-harm', 0),
    }
    
    flagged_categories = {
        cat: score for cat, score in concerning_categories.items()
        if score > threshold
    }
    
    return {
        'flagged': len(flagged_categories) > 0,
        'categories': flagged_categories,
        'max_score': max(concerning_categories.values()) if concerning_categories else 0,
    }

# Example usage
text = "This content might be borderline"
result = custom_moderation(text, threshold=0.3)

print(f"Flagged: {result['flagged']}")
print(f"Categories: {result['categories']}")
print(f"Max score: {result['max_score']:.4f}")
```

### Async Moderation

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def moderate_text(text: str) -> bool:
    moderation = await client.moderations.create(input=text)
    return moderation.results[0].flagged

async def moderate_multiple_texts(texts: list) -> list:
    """Moderate multiple texts concurrently."""
    tasks = [moderate_text(text) for text in texts]
    results = await asyncio.gather(*tasks)
    return results

async def main():
    texts = [
        "Hello, nice to meet you!",
        "This is inappropriate content",
        "What's the weather like?",
    ]
    
    results = await moderate_multiple_texts(texts)
    
    for text, flagged in zip(texts, results):
        status = "⚠️ FLAGGED" if flagged else "✅ OK"
        print(f"{status}: {text[:40]}...")

asyncio.run(main())
```

## Best Practices

### Image Generation

1. **Write detailed prompts:** Be specific about style, composition, and details
2. **Use DALL-E 3 for quality:** Better prompt understanding and image quality
3. **Choose appropriate size:** Use landscape/portrait orientations when needed
4. **Consider quality vs cost:** HD quality costs more but looks better
5. **Style selection:** Vivid for artistic, natural for realistic images
6. **Cache generated images:** URLs expire after 1 hour, download if needed long-term
7. **Handle rate limits:** Image generation is more expensive and may have stricter limits

### Content Moderation

1. **Moderate user input:** Check all user-generated content before processing
2. **Use appropriate thresholds:** Adjust based on your application's tolerance
3. **Consider context:** Some content may be flagged but acceptable in context
4. **Log moderation results:** Track what gets flagged for analysis
5. **Provide feedback:** Let users know why content was rejected
6. **Combine with other checks:** Use moderation as one layer of safety

### Prompt Engineering for Images

**Good prompts include:**
- Subject description ("A golden retriever puppy")
- Setting/background ("in a sunny meadow")
- Style/medium ("photorealistic", "watercolor painting", "3D render")
- Lighting/atmosphere ("golden hour lighting", "moody atmosphere")
- Composition ("close-up", "wide angle", "bird's eye view")

**Example:**
```python
prompt = """
A photorealistic portrait of an elderly fisherman with weathered face,
sitting on a wooden dock at sunset. Golden hour lighting, warm tones,
detailed skin texture, fishing rod beside him, ocean waves in background,
shallow depth of field, professional photography style
"""

response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="hd",
    style="natural",
)
```

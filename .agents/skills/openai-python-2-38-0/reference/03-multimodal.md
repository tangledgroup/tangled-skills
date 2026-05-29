# Multimodal: Audio, Images, Video, Vision

## Contents
- Text-to-Speech (TTS)
- Speech-to-Text (STT / Whisper)
- Image Generation (DALL-E)
- Image Streaming
- Video Generation (Sora)
- Vision (Image Input)

## Text-to-Speech (TTS)

Generate speech audio from text:

```python
from pathlib import Path
from openai import OpenAI

openai = OpenAI()
speech_file_path = Path("speech.mp3")

# Stream response directly to file
with openai.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input="the quick brown fox jumped over the lazy dogs",
) as response:
    response.stream_to_file(speech_file_path)
```

### Streaming Audio Playback

For real-time audio playback with time-to-first-byte metrics:

```python
import time
import asyncio
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

openai = AsyncOpenAI()

async def main():
    start_time = time.time()
    async with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        response_format="pcm",
        input="I see skies of blue and clouds of white...",
    ) as response:
        print(f"Time to first byte: {int((time.time() - start_time) * 1000)}ms")
        await LocalAudioPlayer().play(response)
        print(f"Total time: {int((time.time() - start_time) * 1000)}ms")

asyncio.run(main())
```

Available voices: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`. Response formats: `mp3` (default), `opus`, `aac`, `flac`, `pcm`.

## Speech-to-Text (STT / Whisper)

Transcribe audio to text using Whisper:

```python
from pathlib import Path
from openai import OpenAI

openai = OpenAI()
speech_file_path = Path("speech.mp3")

transcription = openai.audio.transcriptions.create(
    model="whisper-1",
    file=speech_file_path,
)
print(transcription.text)
```

### Translate Audio

Translate non-English audio to English:

```python
translation = openai.audio.translations.create(
    model="whisper-1",
    file=speech_file_path,
)
print(translation.text)
```

### Live Microphone Recording

Record from microphone and transcribe:

```python
import asyncio
from openai import AsyncOpenAI
from openai.helpers import Microphone

openai = AsyncOpenAI()

async def main():
    print("Recording for the next 10 seconds...")
    recording = await Microphone(timeout=10).record()
    print("Recording complete")

    transcription = await openai.audio.transcriptions.create(
        model="whisper-1",
        file=recording,
    )
    print(transcription.text)

asyncio.run(main())
```

## Image Generation (DALL-E)

Generate images from text prompts:

```python
from openai import OpenAI

openai = OpenAI()
response = openai.images.generate(
    prompt="An astronaut lounging in a tropical resort in space, pixel art",
    model="dall-e-3",
)
print(response)  # Contains URL(s) to generated image(s)
```

## Image Streaming

Stream partial images as they are generated (progressive disclosure):

```python
import base64
from pathlib import Path
from openai import OpenAI

client = OpenAI()

stream = client.images.generate(
    model="gpt-image-1",
    prompt="A cute baby sea otter",
    n=1,
    size="1024x1024",
    stream=True,
    partial_images=3,
)

for event in stream:
    if event.type == "image_generation.partial_image":
        print(f"Partial image {event.partial_image_index + 1}/3 received")
        image_data = base64.b64decode(event.b64_json)
        with open(f"partial_{event.partial_image_index + 1}.png", "wb") as f:
            f.write(image_data)
    elif event.type == "image_generation.completed":
        print("Final image completed!")
        image_data = base64.b64decode(event.b64_json)
        with open("final_image.png", "wb") as f:
            f.write(image_data)
```

## Video Generation (Sora)

Generate videos using Sora models with polling:

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main():
    video = await client.videos.create_and_poll(
        model="sora-2",
        prompt="A video of the words 'Thank you' in sparkling letters",
    )
    if video.status == "completed":
        print("Video completed:", video)
    else:
        print(f"Video creation failed. Status: {video.status}")

asyncio.run(main())
```

## Vision (Image Input)

Pass images to models for analysis via the Responses API.

### With Image URL

```python
prompt = "What is in this image?"
img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/2023_06_08_Raccoon1.jpg/1599px-2023_06_08_Raccoon1.jpg"

response = client.responses.create(
    model="gpt-5.2",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": img_url},
            ],
        }
    ],
)
print(response.output_text)
```

### With Base64-Encoded Image

```python
import base64

with open("path/to/image.png", "rb") as image_file:
    b64_image = base64.b64encode(image_file.read()).decode("utf-8")

response = client.responses.create(
    model="gpt-5.2",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "What is in this image?"},
                {"type": "input_image", "image_url": f"data:image/png;base64,{b64_image}"},
            ],
        }
    ],
)
print(response.output_text)
```

# Audio

The OpenAI SDK provides three audio capabilities: transcription (speech-to-text), translation (non-English to English text), and speech synthesis (text-to-speech).

## Transcription

Convert audio to text using Whisper models:

```python
from openai import OpenAI

client = OpenAI()

with open("recording.m4a", "rb") as audio:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio,
    )
    print(transcription.text)
```

### Response Formats

Control the output format:

```python
# Simple text (default)
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio,
    response_format="text",
)

# JSON with timestamps
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio,
    response_format="verbose_json",
)
print(transcription.words)  # word-level timestamps
print(transcription.segments)  # segment-level data
```

### Streaming Transcription

```python
with open("recording.m4a", "rb") as audio:
    stream = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio,
        stream=True,
    )
    for event in stream:
        if event.type == "text.delta":
            print(event.delta, end="", flush=True)
```

### Language and Temperature

```python
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio,
    language="en",        # hint the input language (ISO 639-1)
    temperature=0.0,       # 0.0-1.0, lower = more deterministic
    prompt="Technical terms: ...",  # prefix to guide transcription
)
```

### Diarization

Identify different speakers:

```python
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio,
    diarization=True,
)
```

## Translation

Translate non-English audio to English text:

```python
with open("french_audio.mp3", "rb") as audio:
    translation = client.audio.translations.create(
        model="whisper-1",
        file=audio,
    )
    print(translation.text)
```

Supports the same `response_format` options as transcription.

## Speech (Text-to-Speech)

Generate spoken audio from text:

```python
speech_file_path = "speech.mp3"

with client.audio.speech.stream(
    model="gpt-4o-mini-tts",
    voice="alloy",  # alloy, ash, ballad, coral, echo, shimmer
    input="The quick brown fox jumps over the lazy dog.",
    response_format="mp3",  # mp3, opus, aac, flac, wav, pcm
    speed=1.0,  # 0.25-4.0
) as response:
    with open(speech_file_path, "wb") as f:
        for data in response:
            f.write(data)
```

### Non-Streaming Speech

```python
response = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input="Hello, world!",
    response_format="mp3",
)
response.stream_to_file("output.mp3")
```

### Supported Audio Formats

- `mp3` — default, good compression
- `opus` — low latency streaming
- `aac` — widely compatible
- `flac` — lossless
- `wav` — uncompressed
- `pcm` — raw 16-bit PCM

### File Upload

Pass files as tuples of `(filename, contents, media_type)` or as `PathLike`:

```python
from pathlib import Path

transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=Path("recording.m4a"),
)
```

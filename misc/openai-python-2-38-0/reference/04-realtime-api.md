# Realtime API

## Contents
- Overview
- Basic Text Connection
- Session Configuration
- Conversation Items
- Audio I/O
- Error Handling
- Azure OpenAI Realtime

## Overview

The Realtime API enables low-latency, multi-modal conversational experiences over WebSocket. It supports text and audio as both input and output, plus function calling. The SDK uses the `websockets` library internally (install with `openai[realtime]`).

Connections are managed via `client.realtime.connect()` as an async context manager. Client-sent events configure sessions or send inputs; server-sent events deliver responses.

## Basic Text Connection

```python
import asyncio
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI()
    async with client.realtime.connect(model="gpt-realtime") as connection:
        await connection.session.update(
            session={
                "output_modalities": ["text"],
                "model": "gpt-realtime",
                "type": "realtime",
            }
        )

        user_input = input("Enter a message: ")
        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": user_input}],
            }
        )
        await connection.response.create()

        async for event in connection:
            if event.type == "response.output_text.delta":
                print(event.delta, flush=True, end="")
            elif event.type == "response.output_text.done":
                print()
            elif event.type == "response.done":
                break

asyncio.run(main())
```

## Session Configuration

Update session settings after connecting:

```python
await connection.session.update(
    session={
        "type": "realtime",
        "model": "gpt-realtime",
        "output_modalities": ["text"],  # or ["text", "audio"]
        "audio": {
            "input": {
                "turn_detection": {"type": "server_vad"}  # automatic voice activity detection
            }
        },
    }
)
```

Key session options:
- `output_modalities` — `["text"]`, `["audio"]`, or `["text", "audio"]`
- `audio.input.turn_detection` — `{"type": "server_vad"}` for automatic, or `None` for manual turn control
- `instructions` — System instructions for the model
- `voice` — Voice for audio output
- `temperature` — Sampling temperature

## Conversation Items

Send messages to the conversation:

```python
# Text message
await connection.conversation.item.create(
    item={
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": "Hello!"}],
    }
)

# Trigger model response
await connection.response.create()
```

## Audio I/O

### Sending Audio

Append audio chunks to the input buffer:

```python
import base64

# Send audio chunk (base64-encoded PCM)
await connection.input_audio_buffer.append(
    audio=base64.b64encode(audio_data).decode("utf-8")
)

# In manual turn detection mode, commit the buffer and create response
await connection.input_audio_buffer.commit()
await connection.response.create()
```

### Receiving Audio

Handle audio delta events:

```python
async for event in connection:
    if event.type == "response.output_audio.delta":
        bytes_data = base64.b64decode(event.delta)
        # Play or buffer the audio data
        audio_player.add_data(bytes_data)
    elif event.type == "response.output_audio_transcript.delta":
        print(event.delta, end="", flush=True)
    elif event.type == "response.done":
        break
```

### Push-to-Talk Pattern

For manual turn detection (`turn_detection: None`):

```python
# When user starts speaking:
await connection.input_audio_buffer.append(audio=chunk)

# When user stops speaking (e.g., key press):
await connection.input_audio_buffer.commit()
await connection.response.create()

# Cancel in-progress response if new audio arrives:
await connection.send({"type": "response.cancel"})
```

See `examples/realtime/push_to_talk_app.py` for a full TUI implementation with Textual, microphone input, and audio playback.

## Error Handling

The Realtime API sends `error` events over the WebSocket — no exceptions are raised. You must handle errors yourself:

```python
async for event in connection:
    if event.type == "error":
        print(f"Error: {event.error.type}")
        print(f"Code: {event.error.code}")
        print(f"Event ID: {event.error.event_id}")
        print(f"Message: {event.error.message}")
    # ... handle other events
```

The connection stays open after errors and remains usable.

## Azure OpenAI Realtime

Use the standard `AsyncOpenAI` client with a WebSocket URL derived from your Azure endpoint:

```python
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncOpenAI

async def main():
    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(
        credential, "https://cognitiveservices.azure.com/.default"
    )
    token = await token_provider()

    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]

    # Convert HTTPS to WSS
    base_url = endpoint.replace("https://", "wss://").rstrip("/") + "/openai/v1"

    client = AsyncOpenAI(websocket_base_url=base_url, api_key=token)

    async with client.realtime.connect(model=deployment_name) as connection:
        await connection.session.update(
            session={
                "output_modalities": ["text"],
                "model": deployment_name,
                "type": "realtime",
            }
        )

        user_input = input("Enter a message: ")
        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": user_input}],
            }
        )
        await connection.response.create()

        async for event in connection:
            if event.type == "response.output_text.delta":
                print(event.delta, flush=True, end="")
            elif event.type == "response.output_text.done":
                print()
            elif event.type == "response.done":
                break

    await credential.close()

asyncio.run(main())
```

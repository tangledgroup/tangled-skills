# Realtime API

The Realtime API enables low-latency, multi-modal conversational experiences over WebSocket. It supports text and audio as both input and output, with function calling support.

## Basic Connection

```python
import asyncio
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI()

    async with client.realtime.connect(model="gpt-realtime") as connection:
        # Configure session
        await connection.session.update(
            session={"type": "realtime", "output_modalities": ["text"]}
        )

        # Send a message
        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Tell me a joke!"}],
            }
        )

        # Trigger response
        await connection.response.create()

        # Listen for events
        async for event in connection:
            if event.type == "response.output_text.delta":
                print(event.delta, flush=True, end="")
            elif event.type == "response.output_text.done":
                print()
            elif event.type == "response.done":
                break

asyncio.run(main())
```

## Audio Input/Output

For voice conversations, set audio output modality:

```python
async with client.realtime.connect(model="gpt-realtime") as connection:
    await connection.session.update(
        session={
            "type": "realtime",
            "output_modalities": ["audio"],
            "voice": "alloy",
        }
    )

    # Send audio input (PCM 24kHz, 16-bit mono)
    await connection.input_audio_buffer.append(
        audio=audio_chunk_base64
    )

    # Commit and generate response
    await connection.input_audio_buffer.commit()
    await connection.response.create()

    async for event in connection:
        if event.type == "response.audio.delta":
            # Write audio delta to output
            pass
        elif event.type == "response.done":
            break
```

## Session Configuration

```python
await connection.session.update(
    session={
        "type": "realtime",
        "model": "gpt-realtime",
        "voice": "alloy",  # alloy, ash, ballad, coral, echo, shimmer
        "instructions": "You are a helpful assistant.",
        "input_audio_format": "pcm16",
        "output_audio_format": "pcm16",
        "input_audio_transcription": {
            "model": "whisper-1",
        },
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 500,
        },
        "tools": [
            {
                "type": "function",
                "name": "get_weather",
                "description": "Get weather for a city",
                "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
            }
        ],
        "tool_choice": "auto",
        "temperature": 0.8,
    }
)
```

## Event Types

### Client Events (you send)

- `session.update` — update session configuration
- `conversation.item.create` — add a message item
- `conversation.item.delete` — remove an item
- `conversation.item.truncate` — truncate audio content
- `input_audio_buffer.append` — append audio chunk
- `input_audio_buffer.commit` — commit buffer for processing
- `input_audio_buffer.clear` — clear the buffer
- `response.create` — trigger model response
- `response.cancel` — cancel in-progress response

### Server Events (you receive)

- `session.created` / `session.updated` — session lifecycle
- `conversation.created` — conversation started
- `conversation.item.create` / `conversation.item.delete` — item changes
- `input_audio_buffer.speech_started` / `speech_stopped` — VAD detection
- `input_audio_buffer.committed` / `cleared` — buffer state
- `response.created` / `response.done` — response lifecycle
- `response.text.delta` / `response.text.done` — text streaming
- `response.audio.delta` / `response.audio.done` — audio streaming
- `response.audio_transcript.delta` / `done` — transcript of audio output
- `response.function_call_arguments.delta` / `done` — function call args
- `rate_limits.updated` — rate limit info
- `error` — error event

## Error Handling

Errors come as events, not exceptions:

```python
async for event in connection:
    if event.type == "error":
        print(f"Error type: {event.error.type}")
        print(f"Error code: {event.error.code}")
        print(f"Message: {event.error.message}")
        print(f"Event ID: {event.error.event_id}")
        # Connection stays open and usable
```

## Function Calling

```python
async for event in connection:
    if event.type == "response.function_call_arguments.done":
        import json
        args = json.loads(event.arguments)
        # Execute the function
        result = await execute_function(event.name, args)
        # Send result back
        await connection.conversation.item.create(
            item={
                "type": "function_call_output",
                "call_id": event.call_id,
                "output": json.dumps(result),
            }
        )
        # Trigger next response
        await connection.response.create()
```

## Transcription

Enable real-time speech transcription:

```python
await connection.session.update(
    session={
        "input_audio_transcription": {
            "model": "whisper-1",
        },
    }
)
```

Transcription events:
- `conversation.item.input_audio_transcription.completed` — final transcript
- `conversation.item.input_audio_transcription.delta` — partial transcript
- `conversation.item.input_audio_transcription.failed` — error

## Reconnection

The SDK supports automatic reconnection with customizable overrides:

```python
from openai import AsyncOpenAI
from openai.types.websocket_reconnection import ReconnectingOverrides

async with client.realtime.connect(
    model="gpt-realtime",
    reconnecting_overrides=ReconnectingOverrides(
        max_reconnect_attempts=5,
        initial_delay_ms=1000,
        max_delay_ms=30000,
    ),
) as connection:
    async for event in connection:
        if isinstance(event, ReconnectingEvent):
            print(f"Reconnecting... attempt {event.attempt}")
```

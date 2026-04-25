# Advanced Topics

Comprehensive guide to advanced OpenAI SDK features including Realtime API, webhooks, pagination, Azure OpenAI integration, and custom requests.

## Realtime API

The Realtime API enables low-latency, multi-modal conversational experiences with text and audio over WebSocket connections.

### Basic Text Conversation

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

        # Send user message
        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Say hello!"}],
            }
        )
        
        # Create response
        await connection.response.create()

        # Stream events
        async for event in connection:
            if event.type == "response.output_text.delta":
                print(event.delta, flush=True, end="")

            elif event.type == "response.output_text.done":
                print()

            elif event.type == "response.done":
                break

asyncio.run(main())
```

### Audio Conversation (Push-to-Talk)

```python
import asyncio
from openai import AsyncOpenAI

async def realtime_audio_conversation():
    client = AsyncOpenAI()

    async with client.realtime.connect(model="gpt-realtime") as connection:
        # Configure for audio output
        await connection.session.update(
            session={
                "type": "realtime",
                "output_modalities": ["audio"],
                "voice": "alloy",
            }
        )

        # Send audio input (PCM data, 24kHz, 1 channel, int16)
        async def send_audio(audio_data: bytes):
            await connection.input_audio_buffer.append(input_audio=audio_data)
            await connection.input_audio_buffer.commit()

        # Start response generation
        await connection.response.create()

        # Stream events
        async for event in connection:
            if event.type == "response.audio.delta":
                # Play audio chunk
                play_audio(event.delta)
            
            elif event.type == "response.done":
                print("Response complete")

def play_audio(audio_data: str):
    """Decode base64 audio and play through speakers."""
    import base64
    # Implement with your audio library (e.g., sounddevice, pygame)
    audio_bytes = base64.b64decode(audio_data)
    # Play audio_bytes...
```

### Realtime Error Handling

```python
import asyncio
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI()

    async with client.realtime.connect(model="gpt-realtime") as connection:
        async for event in connection:
            if event.type == "error":
                print(f"Error type: {event.error.type}")
                print(f"Error code: {event.error.code}")
                print(f"Error message: {event.error.message}")
                print(f"Event ID: {event.error.event_id}")
                
                # Connection stays open, handle appropriately
                continue
            
            # Handle other events...

asyncio.run(main())
```

### Session Configuration

```python
await connection.session.update(
    session={
        "type": "realtime",
        "modalities": ["text", "audio"],
        "instructions": "You are a helpful assistant.",
        "voice": "alloy",  # alloy, echo, fable, onyx, nova, shimmer
        "input_audio_format": "pcm16",
        "output_audio_format": "pcm16",
        "input_audio_transcription": {
            "model": "whisper-1"
        },
        "turn_detection": {
            "type": "server_vad",  # Server-side voice activity detection
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 200,
        },
        "tools": [
            {
                "type": "function",
                "name": "get_weather",
                "description": "Get weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    },
                    "required": ["location"]
                }
            }
        ],
        "tool_choice": "auto",  # auto, none, or specific tool
        "temperature": 0.8,
        "max_response_output_tokens": 1024,
    }
)
```

## Webhooks

Receive real-time notifications for events like response completion or failures.

### Setting Up Webhooks

1. Create a webhook endpoint in your application
2. Configure webhook URL in OpenAI platform settings
3. Get webhook secret for signature verification

### Parsing and Verifying Webhooks

```python
from openai import OpenAI
from flask import Flask, request

app = Flask(__name__)
client = OpenAI()  # Uses OPENAI_WEBHOOK_SECRET env var


@app.route("/webhook", methods=["POST"])
def webhook():
    request_body = request.get_data(as_text=True)

    try:
        # Verify and parse in one step
        event = client.webhooks.unwrap(request_body, request.headers)

        if event.type == "response.completed":
            print("Response completed:", event.data)
        elif event.type == "response.failed":
            print("Response failed:", event.data)
        else:
            print(f"Event type: {event.type}")

        return "ok", 200
        
    except Exception as e:
        print(f"Invalid signature: {e}")
        return "Invalid signature", 400


if __name__ == "__main__":
    app.run(port=8000)
```

### Manual Signature Verification

```python
import json
from openai import OpenAI
from flask import Flask, request

app = Flask(__name__)
client = OpenAI()


@app.route("/webhook", methods=["POST"])
def webhook():
    request_body = request.get_data(as_text=True)

    try:
        # Verify signature first
        client.webhooks.verify_signature(request_body, request.headers)

        # Then parse the body
        event = json.loads(request_body)
        print("Verified event:", event)

        return "ok", 200
        
    except Exception as e:
        print(f"Invalid signature: {e}")
        return "Invalid signature", 400
```

### Webhook Event Types

| Event Type | Description |
|------------|-------------|
| `response.completed` | Response generation completed successfully |
| `response.failed` | Response generation failed |
| `fine_tuning_job.succeeded` | Fine-tuning job completed |
| `fine_tuning_job.failed` | Fine-tuning job failed |

## Pagination

List methods return paginated results with auto-paginating iterators.

### Auto-Pagination

```python
from openai import OpenAI

client = OpenAI()

# Automatically fetches all pages
all_files = []
for file in client.files.list(limit=20):
    all_files.append(file)

print(f"Total files: {len(all_files)}")
```

### Async Auto-Pagination

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main():
    all_jobs = []
    
    async for job in client.fine_tuning.jobs.list(limit=20):
        all_jobs.append(job)
    
    print(f"Total jobs: {len(all_jobs)}")

asyncio.run(main())
```

### Manual Pagination Control

```python
# Get first page
first_page = client.fine_tuning.jobs.list(limit=20)

# Check if more pages exist
if first_page.has_next_page():
    print(f"Next page info: {first_page.next_page_info()}")
    
    # Get next page explicitly
    next_page = first_page.get_next_page()
    print(f"Items on next page: {len(next_page.data)}")

# Access cursor for manual pagination
print(f"After cursor: {first_page.after}")
print(f"Before cursor: {first_page.before}")

# Iterate over current page only
for job in first_page.data:
    print(job.id)
```

### Pagination Parameters

```python
# List with specific parameters
files = client.files.list(
    limit=10,          # Maximum items per page (default 20)
    order="desc",      # Sort order (asc or desc)
)

# For threads/messages with filters
messages = client.beta.threads.messages.list(
    thread_id="thread_123",
    limit=20,
    order="desc",
    run_id="run_456",  # Filter by run ID
)
```

## Azure OpenAI Integration

Use the `AzureOpenAI` client for Azure deployments.

### Basic Azure Setup

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2024-02-01",  # API version
    azure_endpoint="https://your-endpoint.openai.azure.com",
    # api_key loaded from AZURE_OPENAI_API_KEY env var
)

completion = client.chat.completions.create(
    model="deployment-name",  # Your deployment name (not model name)
    messages=[
        {"role": "user", "content": "Hello from Azure!"}
    ],
)

print(completion.choices[0].message.content)
```

### Azure Configuration Options

```python
client = AzureOpenAI(
    azure_endpoint="https://your-endpoint.openai.azure.com",
    api_version="2024-02-01",
    api_key="your-api-key",  # Or use AZURE_OPENAI_API_KEY env var
    
    # Optional: Azure Active Directory authentication
    azure_ad_token="your-token",  # Or use AZURE_OPENAI_AD_TOKEN env var
    
    # Custom token provider
    azure_ad_token_provider=my_token_provider_function,
    
    # Deployment name (default for all requests)
    azure_deployment="gpt-35-turbo",
)
```

### Azure with Managed Identity

```python
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Create token provider
credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(
    credential, "https://cognitiveservices.azure.com/.default"
)

# Create client with managed identity
client = AzureOpenAI(
    azure_endpoint="https://your-endpoint.openai.azure.com",
    api_version="2024-02-01",
    azure_ad_token_provider=token_provider,
)

completion = client.chat.completions.create(
    model="deployment-name",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### Azure Embeddings

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://your-endpoint.openai.azure.com",
    api_version="2024-02-01",
)

embedding = client.embeddings.create(
    model="text-embedding-ada-002",  # Deployment name
    input="Sample text for embedding",
)

print(f"Embedding dimension: {len(embedding.data[0].embedding)}")
```

## Custom/Undocumented Requests

### Accessing Undocumented Endpoints

```python
import httpx
from openai import OpenAI

client = OpenAI()

# Make raw HTTP request to undocumented endpoint
response = client.post(
    "/custom-endpoint",
    cast_to=httpx.Response,
    body={"custom_param": "value"},
)

print(response.headers.get("x-custom-header"))
print(response.text)
```

### Extra Parameters

Add undocumented parameters to standard requests:

```python
# Extra headers
response = client.responses.create(
    model="gpt-5.2",
    input="Test",
    extra_headers={"X-Custom-Header": "custom-value"},
)

# Extra query parameters
response = client.responses.create(
    model="gpt-5.2",
    input="Test",
    extra_query={"debug": "true"},
)

# Extra body fields
response = client.responses.create(
    model="gpt-5.2",
    input="Test",
    extra_body={"experimental_feature": True},
)
```

### Accessing Undocumented Response Fields

```python
response = client.responses.create(
    model="gpt-5.2",
    input="Test",
)

# Access unknown fields directly (may be None if not present)
print(response.unknown_field)

# Get all extra fields as dictionary
if response.model_extra:
    print("Extra fields:", response.model_extra)
```

### Raw Response Access

```python
from openai import OpenAI

client = OpenAI()

# Eagerly read full response
response = client.responses.with_raw_response.create(
    model="gpt-5.2",
    input="Test",
)

# Access headers
print(response.headers.get("X-Request-ID"))
print(response.http_response.headers)

# Get the parsed response object
result = response.parse()
print(result.output_text)
```

### Streaming Raw Response

```python
from openai import OpenAI

client = OpenAI()

with client.responses.with_streaming_response.create(
    model="gpt-5.2",
    input="Stream this",
) as response:
    # Access headers before reading body
    print(response.headers.get("X-Request-ID"))
    
    # Stream line by line
    for line in response.iter_lines():
        print(line)
    
    # Or read as JSON
    # data = response.json()
    
    # Or read raw bytes
    # content = response.read()
```

## Advanced Client Features

### Per-Request Options

Override client settings for specific requests:

```python
from openai import OpenAI

client = OpenAI()

# Override timeout for slow request
response = client.with_options(timeout=60.0).responses.create(
    model="gpt-5.2",
    input="This might take a while",
)

# Override retries for critical request
response = client.with_options(max_retries=10).responses.create(
    model="gpt-5.2",
    input="Critical request",
)

# Override base URL for specific endpoint
response = client.with_options(base_url="https://staging.api.openai.com/v1").responses.create(
    model="gpt-5.2",
    input="Test on staging",
)
```

### Determining Null vs Missing Fields

```python
# Check if a field is explicitly null or missing from response
if response.my_field is None:
    if 'my_field' not in response.model_fields_set:
        print('Field is missing from JSON response')
    else:
        print('Field is explicitly null in JSON response')
```

### Request ID Tracking

```python
from openai import OpenAI

client = OpenAI()

# From successful response
response = client.responses.create(
    model="gpt-5.2",
    input="Test",
)
print(f"Request ID: {response._request_id}")

# From error (must catch exception)
import openai

try:
    client.responses.create(model="invalid", input="test")
except openai.APIStatusError as exc:
    print(f"Request ID from error: {exc.request_id}")
    raise
```

## Logging and Debugging

### Enable SDK Logging

```bash
# Info level logging
export OPENAI_LOG=info

# Debug level (verbose)
export OPENAI_LOG=debug
```

### Programmatic Logging

```python
import logging
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable OpenAI SDK logging
logging.getLogger("openai").setLevel(logging.DEBUG)

client = OpenAI()
```

### Debugging Requests

```python
import openai
from openai import OpenAI

client = OpenAI()

try:
    response = client.responses.create(
        model="gpt-5.2",
        input="Test",
    )
except openai.APIError as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e.message}")
    print(f"Status code: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
    print(f"Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'}")
    
    # For status errors, access full response
    if isinstance(e, openai.APIStatusError):
        print(f"Response body: {e.body}")
```

## Best Practices

### Realtime API

1. **Handle errors gracefully:** Error events don't close the connection
2. **Configure turn detection:** Use VAD for natural conversations
3. **Manage audio buffers:** Commit audio chunks appropriately
4. **Choose right voice:** Match voice to your application tone
5. **Test latency:** Realtime API is optimized for low latency

### Webhooks

1. **Always verify signatures:** Never trust webhook payloads without verification
2. **Use raw body:** Don't parse JSON before verification
3. **Handle retries:** OpenAI may retry failed deliveries
4. **Respond quickly:** Return 200 OK promptly
5. **Log events:** Track webhook deliveries for debugging

### Azure OpenAI

1. **Use managed identity:** Prefer over API keys in Azure
2. **Match API version:** Ensure compatibility with features used
3. **Handle deployment names:** Use deployment names, not model names
4. **Check region availability:** Not all models available in all regions

### Custom Requests

1. **Use documented API first:** Custom requests should be last resort
2. **Validate responses:** Undocumented endpoints may have different response formats
3. **Monitor for changes:** Undocumented features may change without notice
4. **Report needs:** If you need undocumented features, consider requesting them officially

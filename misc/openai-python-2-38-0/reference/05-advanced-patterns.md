# Advanced Patterns

## Contents
- Azure OpenAI
- Workload Identity Authentication
- File Uploads
- Chunked File Uploads
- Webhook Verification
- Module-Level Client
- Raw and Streaming Responses
- Custom HTTP Client
- aiohttp Backend
- Context Manager for Client Lifecycle
- Logging

## Azure OpenAI

Use `AzureOpenAI` instead of `OpenAI`. The Azure API shape differs from the core API, so static types for responses/params may not always match:

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2023-07-01-preview",
    azure_endpoint="https://example-endpoint.openai.azure.com",
)

completion = client.chat.completions.create(
    model="deployment-name",
    messages=[{"role": "user", "content": "Hello"}],
)
print(completion.to_json())
```

### With Deployment Set on Client

```python
client = AzureOpenAI(
    api_version="2023-07-01-preview",
    azure_endpoint="https://example-resource.azure.openai.com/",
    azure_deployment="deployment-name",
)

completion = client.chat.completions.create(
    model="",  # empty when deployment is set on client
    messages=[{"role": "user", "content": "Hello"}],
)
```

### Azure AD Authentication

```python
from openai.lib.azure import AzureOpenAI, AsyncAzureOpenAI, AzureADTokenProvider
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

scopes = "https://cognitiveservices.azure.com/.default"
token_provider: AzureADTokenProvider = get_bearer_token_provider(
    DefaultAzureCredential(), scopes
)

client = AzureOpenAI(
    api_version="2023-07-01-preview",
    azure_endpoint="https://my-resource.openai.azure.com",
    azure_ad_token_provider=token_provider,
)
```

Async variant uses `azure.identity.aio`:

```python
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

token_provider = get_bearer_token_provider(DefaultAzureCredential(), scopes)
client = AsyncAzureOpenAI(
    api_version="2023-07-01-preview",
    azure_endpoint="https://my-resource.openai.azure.com",
    azure_ad_token_provider=token_provider,
)
```

### Azure-Specific Options

- `azure_endpoint` (or `AZURE_OPENAI_ENDPOINT` env var)
- `azure_deployment`
- `api_version` (or `OPENAI_API_VERSION` env var)
- `azure_ad_token` (or `AZURE_OPENAI_AD_TOKEN` env var)
- `azure_ad_token_provider`

## Workload Identity Authentication

For cloud-managed environments, use short-lived tokens instead of long-lived API keys:

### Kubernetes

```python
from openai import OpenAI
from openai.auth import k8s_service_account_token_provider

client = OpenAI(
    workload_identity={
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": k8s_service_account_token_provider(
            "/var/run/secrets/kubernetes.io/serviceaccount/token"
        ),
    },
)
```

### Azure Managed Identity

```python
from openai import OpenAI
from openai.auth import azure_managed_identity_token_provider

client = OpenAI(
    workload_identity={
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": azure_managed_identity_token_provider(
            resource="https://management.azure.com/",
        ),
    },
)
```

### Google Cloud Platform

```python
from openai import OpenAI
from openai.auth import gcp_id_token_provider

client = OpenAI(
    workload_identity={
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": gcp_id_token_provider(audience="https://api.openai.com/v1"),
    },
)
```

### Custom Token Provider

```python
def get_custom_token() -> str:
    return "your-jwt-token"

client = OpenAI(
    workload_identity={
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": {
            "token_type": "jwt",
            "get_token": get_custom_token,
        },
    }
)
```

### Custom Refresh Buffer

Default refresh buffer is 1200 seconds (20 minutes) before expiration:

```python
client = OpenAI(
    workload_identity={
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": k8s_service_account_token_provider("/var/token"),
        "refresh_buffer_seconds": 120.0,
    }
)
```

Tokens are cached — the provider's `get_token` is called only when the token needs refreshing.

## File Uploads

Pass files as `bytes`, `PathLike`, or `(filename, contents, media_type)` tuples:

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()
client.files.create(
    file=Path("input.jsonl"),
    purpose="fine-tune",
)
```

Async client reads `PathLike` files asynchronously automatically.

## Chunked File Uploads

For large files, use chunked uploads:

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()
file = Path("/tmp/big_test_file.txt")

# From disk
upload = client.uploads.upload_file_chunked(
    file=file,
    mime_type="txt",
    purpose="batch",
)

# From in-memory bytes
data = file.read_bytes()
upload = client.uploads.upload_file_chunked(
    file=data,
    filename="my_file.txt",
    bytes=len(data),
    mime_type="txt",
    purpose="batch",
)
```

## Webhook Verification

Verify webhook signatures using `client.webhooks.unwrap()` (verify + parse) or `client.webhooks.verify_signature()` (verify only):

### Unwrap (Verify and Parse)

```python
from openai import OpenAI
from flask import Flask, request

app = Flask(__name__)
client = OpenAI()  # Uses OPENAI_WEBHOOK_SECRET env var by default

@app.route("/webhook", methods=["POST"])
def webhook():
    request_body = request.get_data(as_text=True)
    try:
        event = client.webhooks.unwrap(request_body, request.headers)
        if event.type == "response.completed":
            print("Response completed:", event.data)
        elif event.type == "response.failed":
            print("Response failed:", event.data)
        return "ok"
    except Exception as e:
        print("Invalid signature:", e)
        return "Invalid signature", 400
```

### Verify Signature Only

```python
import json

@app.route("/webhook", methods=["POST"])
def webhook():
    request_body = request.get_data(as_text=True)
    try:
        client.webhooks.verify_signature(request_body, request.headers)
        event = json.loads(request_body)
        print("Verified event:", event)
        return "ok"
    except Exception as e:
        return "Invalid signature", 400
```

The `body` parameter must be the raw JSON string — do not parse it first. Webhook secret defaults to `OPENAI_WEBHOOK_SECRET` environment variable, or pass explicitly as `secret=...`.

## Module-Level Client

Use the `openai` module directly for a global client (legacy pattern):

```python
import openai

openai.api_key = "sk-..."
openai.base_url = "https://..."
openai.default_headers = {"x-foo": "true"}

stream = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

## Raw and Streaming Responses

### Raw Response (Access Headers)

```python
response = client.chat.completions.with_raw_response.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.headers.get("x-request-id"))
completion = response.parse()
```

Returns a `LegacyAPIResponse` object. In the next major version, `content` and `text` will be methods instead of properties.

### Streaming Response (Lazy Body Read)

```python
with client.chat.completions.with_streaming_response.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "Hello"}],
) as response:
    print(response.headers.get("X-My-Header"))
    for line in response.iter_lines():
        print(line)
```

Returns `APIResponse` (sync) or `AsyncAPIResponse` (async). Context manager is required so the response closes reliably. Available methods: `.read()`, `.text()`, `.json()`, `.iter_bytes()`, `.iter_text()`, `.iter_lines()`, `.parse()`.

## Custom HTTP Client

Pass a custom httpx client for proxies, transports, or advanced configuration:

```python
import httpx
from openai import OpenAI, DefaultHttpxClient

client = OpenAI(
    base_url="http://my.test.server.example.com:8083/v1",
    http_client=DefaultHttpxClient(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

Override per-request with `with_options()`:

```python
client.with_options(http_client=DefaultHttpxClient(...))
```

## aiohttp Backend

For improved async concurrency, use aiohttp instead of httpx:

```bash
pip install openai[aiohttp]
```

```python
import asyncio
from openai import AsyncOpenAI, DefaultAioHttpClient

async def main():
    async with AsyncOpenAI(
        http_client=DefaultAioHttpClient(),
    ) as client:
        completion = await client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model="gpt-5.2",
        )

asyncio.run(main())
```

## Context Manager for Client Lifecycle

By default, HTTP connections close when the client is garbage collected. Manually manage lifecycle:

```python
from openai import OpenAI

with OpenAI() as client:
    # make requests
    response = client.responses.create(model="gpt-5.2", input="Hello")
# HTTP client is now closed
```

Or call `.close()` explicitly.

## Logging

Enable via environment variable:

```bash
export OPENAI_LOG=info    # info level
export OPENAI_LOG=debug   # verbose
```

Uses the standard library `logging` module.

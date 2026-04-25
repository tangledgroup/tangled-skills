# Client Configuration and Error Handling

Comprehensive guide to configuring OpenAI clients, authentication methods, error handling, retries, timeouts, and advanced client options.

## Basic Client Setup

### Synchronous Client

```python
from openai import OpenAI

# Uses OPENAI_API_KEY environment variable by default
client = OpenAI()

# Or specify API key explicitly (not recommended for production)
client = OpenAI(api_key="sk-your-api-key")

# Specify base URL for custom endpoints
client = OpenAI(base_url="https://api.openai.com/v1")
```

### Asynchronous Client

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main():
    response = await client.responses.create(
        model="gpt-5.2",
        input="Hello!",
    )
    print(response.output_text)

import asyncio
asyncio.run(main())
```

## Authentication Methods

### Environment Variable (Recommended)

```bash
export OPENAI_API_KEY="sk-your-api-key"
```

```python
from openai import OpenAI

client = OpenAI()  # Automatically reads OPENAI_API_KEY
```

### Using python-dotenv

```python
# .env file
OPENAI_API_KEY=sk-your-api-key

# Load in code
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()
```

### Workload Identity Authentication

For cloud environments (Kubernetes, Azure, GCP), use workload identity with short-lived tokens instead of long-lived API keys.

#### Kubernetes Service Account Tokens

```python
from openai import OpenAI
from openai.auth import k8s_service_account_token_provider

client = OpenAI(
    workload_identity={
        "client_id": "your-client-id",
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": k8s_service_account_token_provider(
            "/var/run/secrets/kubernetes.io/serviceaccount/token"
        ),
    },
    organization="org-xyz",
    project="proj-abc",
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

#### Azure Managed Identity

```python
from openai import OpenAI
from openai.auth import azure_managed_identity_token_provider

client = OpenAI(
    workload_identity={
        "client_id": "your-client-id",
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": azure_managed_identity_token_provider(
            resource="https://management.azure.com/",
        ),
    },
)
```

#### Google Cloud Platform (Compute Engine)

```python
from openai import OpenAI
from openai.auth import gcp_id_token_provider

client = OpenAI(
    workload_identity={
        "client_id": "your-client-id",
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": gcp_id_token_provider(audience="https://api.openai.com/v1"),
    },
)
```

#### Custom Token Provider

```python
from openai import OpenAI

def get_custom_token() -> str:
    # Implement your token retrieval logic
    return "your-jwt-token"

client = OpenAI(
    workload_identity={
        "client_id": "your-client-id",
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": {
            "token_type": "jwt",
            "get_token": get_custom_token,
        },
    }
)
```

#### Custom Token Refresh Buffer

```python
from openai import OpenAI
from openai.auth import k8s_service_account_token_provider

client = OpenAI(
    workload_identity={
        "client_id": "your-client-id",
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": k8s_service_account_token_provider("/var/token"),
        "refresh_buffer_seconds": 120.0,  # Refresh 2 minutes before expiration
    }
)
```

## Client Configuration Options

### Timeouts

Default timeout is 10 minutes. Configure with float (seconds) or httpx.Timeout:

```python
import httpx
from openai import OpenAI

# Simple timeout (20 seconds)
client = OpenAI(timeout=20.0)

# Granular control
client = OpenAI(
    timeout=httpx.Timeout(
        connect=5.0,   # Connection timeout
        read=30.0,     # Read timeout
        write=10.0,    # Write timeout
        pool=5.0,      # Pool timeout
    )
)

# Per-request override
response = client.with_options(timeout=5.0).responses.create(
    model="gpt-5.2",
    input="Quick response needed",
)
```

On timeout, `APITimeoutError` is raised (and retried by default).

### Retries

Automatic retries for connection errors, 408, 409, 429, and 5xx errors:

```python
from openai import OpenAI

# Disable retries
client = OpenAI(max_retries=0)

# Increase retries (default is 2)
client = OpenAI(max_retries=5)

# Per-request override
response = client.with_options(max_retries=10).responses.create(
    model="gpt-5.2",
    input="Retry this request",
)
```

### Organization and Project

Specify organization for billing and access control:

```python
client = OpenAI(
    organization="org-xyz123",
    project="proj-abc456",
)
```

Or use environment variables:
```bash
export OPENAI_ORG_ID="org-xyz123"
export OPENAI_PROJECT_ID="proj-abc456"
```

### Base URL

Use custom endpoints (e.g., for testing or proxies):

```python
client = OpenAI(base_url="http://localhost:8000/v1")
```

Or use environment variable:
```bash
export OPENAI_BASE_URL="http://localhost:8000/v1"
```

### HTTP Client Customization

Configure proxies, transports, and advanced httpx options:

```python
import httpx
from openai import OpenAI, DefaultHttpxClient

# Using a proxy
client = OpenAI(
    http_client=DefaultHttpxClient(proxy="http://proxy.example.com:8080")
)

# Custom transport
client = OpenAI(
    http_client=DefaultHttpxClient(
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    )
)

# Per-request customization
response = client.with_options(
    http_client=DefaultHttpxClient(proxy="http://different-proxy:8080")
).responses.create(model="gpt-5.2", input="test")
```

### Async Client with aiohttp

For improved concurrency performance:

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
        response = await client.responses.create(
            model="gpt-5.2",
            input="Using aiohttp backend",
        )
        print(response.output_text)

asyncio.run(main())
```

### Context Manager

Manually manage HTTP resources:

```python
from openai import OpenAI

with OpenAI() as client:
    # Make requests here
    response = client.responses.create(
        model="gpt-5.2",
        input="Hello!",
    )

# HTTP client is now closed
```

## Error Handling

### Error Types

All errors inherit from `openai.APIError`:

| Status Code | Error Type | Cause |
|-------------|------------|-------|
| 400 | `BadRequestError` | Invalid request parameters |
| 401 | `AuthenticationError` | Invalid or missing API key |
| 403 | `PermissionDeniedError` | Insufficient permissions |
| 404 | `NotFoundError` | Resource not found |
| 422 | `UnprocessableEntityError` | Invalid input data |
| 429 | `RateLimitError` | Rate limit exceeded |
| >=500 | `InternalServerError` | Server error |
| N/A | `APIConnectionError` | Network/connectivity issue |

### Basic Error Handling

```python
import openai
from openai import OpenAI

client = OpenAI()

try:
    response = client.responses.create(
        model="gpt-5.2",
        input="Test request",
    )
except openai.APIConnectionError as e:
    print("Network error - server unreachable")
    print(e.__cause__)  # Underlying exception
except openai.RateLimitError as e:
    print("Rate limited - back off and retry")
    print(e.status_code)
except openai.AuthenticationError as e:
    print("Authentication failed")
    print(e.status_code)
except openai.APIStatusError as e:
    print(f"API error: {e.status_code}")
    print(e.response)  # Full response object
except openai.APIError as e:
    print(f"General API error: {e}")
```

### Accessing Request IDs

For debugging and reporting issues:

```python
from openai import OpenAI

client = OpenAI()

# From successful response
response = client.responses.create(
    model="gpt-5.2",
    input="Test",
)
print(response._request_id)  # req_123...

# From error (must catch exception)
try:
    client.responses.create(model="invalid-model", input="test")
except openai.APIStatusError as exc:
    print(exc.request_id)  # req_456...
    raise
```

### Detailed Error Information

```python
import openai

try:
    client.fine_tuning.jobs.create(
        model="gpt-4o",
        training_file="file-invalid",
    )
except openai.NotFoundError as e:
    print(f"Status: {e.status_code}")
    print(f"Message: {e.message}")
    print(f"Body: {e.body}")  # Parsed error body
    print(f"Request ID: {e.request_id}")
```

## Logging

Enable logging for debugging:

```bash
# Info level
export OPENAI_LOG=info

# Debug level (verbose)
export OPENAI_LOG=debug
```

Or configure programmatically:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("openai").setLevel(logging.DEBUG)
```

## Advanced Features

### Accessing Raw Response Headers

```python
from openai import OpenAI

client = OpenAI()

# Using with_raw_response (eagerly reads body)
response = client.responses.with_raw_response.create(
    model="gpt-5.2",
    input="Test",
)

print(response.headers.get('X-Request-ID'))
result = response.parse()  # Get the actual response object
print(result.output_text)
```

### Streaming Raw Response

For granular control over response reading:

```python
from openai import OpenAI

client = OpenAI()

with client.responses.with_streaming_response.create(
    model="gpt-5.2",
    input="Stream this",
) as response:
    print(response.headers.get("X-Request-ID"))
    
    # Read line by line
    for line in response.iter_lines():
        print(line)
```

### Custom/Undocumented Endpoints

Make requests to undocumented endpoints:

```python
import httpx
from openai import OpenAI

client = OpenAI()

response = client.post(
    "/custom-endpoint",
    cast_to=httpx.Response,
    body={"custom_param": "value"},
)

print(response.headers.get("x-custom-header"))
```

### Extra Parameters

Add undocumented parameters to requests:

```python
response = client.responses.create(
    model="gpt-5.2",
    input="Test",
    extra_headers={"X-Custom-Header": "value"},
    extra_query={"custom_query": "param"},
    extra_body={"custom_field": "data"},
)
```

### Accessing Undocumented Response Fields

```python
response = client.responses.create(
    model="gpt-5.2",
    input="Test",
)

# Access unknown fields directly
print(response.unknown_field)

# Get all extra fields as dict
print(response.model_extra)
```

### Determining if Field is Null vs Missing

```python
if response.my_field is None:
    if 'my_field' not in response.model_fields_set:
        print('Field is missing from JSON')
    else:
        print('Field is explicitly null in JSON')
```

## Azure OpenAI

Use `AzureOpenAI` class for Azure deployments:

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2024-02-01",
    azure_endpoint="https://your-endpoint.openai.azure.com",
    # api_key is loaded from AZURE_OPENAI_API_KEY env var
)

completion = client.chat.completions.create(
    model="deployment-name",  # Your deployment name
    messages=[
        {"role": "user", "content": "Hello from Azure!"}
    ],
)

print(completion.choices[0].message.content)
```

### Azure Configuration Options

- `azure_endpoint` (or `AZURE_OPENAI_ENDPOINT` env var)
- `azure_deployment` - Deployment name
- `api_version` (or `OPENAI_API_VERSION` env var)
- `azure_ad_token` (or `AZURE_OPENAI_AD_TOKEN` env var)
- `azure_ad_token_provider` - Custom token provider

### Azure with Managed Identity

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://your-endpoint.openai.azure.com",
    api_version="2024-02-01",
    azure_ad_token_provider=my_token_provider,
)
```

## Best Practices

1. **Use environment variables** for API keys, never hardcode them
2. **Enable retries** for production applications (default is 2)
3. **Set appropriate timeouts** based on your use case
4. **Handle errors gracefully** with specific exception handling
5. **Log request IDs** for debugging production issues
6. **Use context managers** to ensure proper resource cleanup
7. **Implement exponential backoff** for rate limit errors
8. **Use workload identity** in cloud environments instead of API keys

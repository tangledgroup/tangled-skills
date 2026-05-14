# Configuration and Client Options

## Config Object

The `botocore.config.Config` class provides client-specific configuration that overrides settings from environment variables and config files:

```python
import boto3
from botocore.config import Config

config = Config(
    region_name='us-east-1',
    retries={
        'max_attempts': 10,
        'mode': 'adaptive'
    },
    connect_timeout=5,
    read_timeout=30,
    signature_version='s3v4',
    parameter_validation=True,
    tcp_keepalive=True
)

client = boto3.client('s3', config=config)
```

Key Config options:

- `retries` — dictionary with `max_attempts` (int) and `mode` (`legacy`, `standard`, `adaptive`)
- `connect_timeout` — seconds before connection times out (default: 5)
- `read_timeout` — seconds before read operation times out (default: 60 for most services, varies by service)
- `signature_version` — signing algorithm (`s3v4`, `v4`, `v4a`)
- `parameter_validation` — validate parameters before sending (default: True)
- `tcp_keepalive` — enable TCP keep-alive on sockets (default: False)
- `user_agent_extra` — additional user agent string
- `sts_region` — region for STS endpoint resolution

## Proxy Configuration

Specify proxy servers via environment variables:

```bash
export HTTPS_PROXY=http://proxy.example.com:8080
export HTTP_PROXY=http://proxy.example.com:8080
```

Or via Config object with additional proxy settings:

```python
from botocore.config import Config

config = Config(
    proxies={
        'https': 'http://proxy.example.com:8080',
        'http': 'http://proxy.example.com:8080'
    },
    proxy_config={
        'ca_bundle': '/path/to/cert.pem',
        'use_forwarding_for_https': True
    }
)

client = boto3.client('s3', config=config)
```

The `use_forwarding_for_https` option in `proxy_config` enables CONNECT tunneling for HTTPS through the proxy.

## Dual-Stack Endpoints

Enable IPv4/IPv6 dual-stack endpoints:

```python
from botocore.config import Config

config = Config(use_dualstack_endpoint=True)
client = boto3.client('s3', config=config)
```

Or via environment variable `AWS_USE_DUALSTACK_ENDPOINT=1`.

## FIPS Endpoints

Enable Federal Information Processing Standards endpoints:

```python
from botocore.config import Config

config = Config(use_fips_endpoint=True)
client = boto3.client('s3', config=config)
```

Or via environment variable `AWS_USE_FIPS_ENDPOINT=1`.

## S3-Specific Configuration

S3 client supports additional configuration options via the `s3` key in Config:

```python
from botocore.config import Config

config = Config(
    s3={
        'use_accelerate_endpoint': True,
        'addressing_style': 'path',  # or 'virtual', 'auto'
        'us_east_1_regional_endpoint': True,
        'payload_signing_enabled': True,
        'disable_multi_region_access_points': False,
        'disable_express_session_auth': False
    }
)

client = boto3.client('s3', config=config)
```

S3 configuration options:

- `use_accelerate_endpoint` — enable S3 Transfer Acceleration
- `addressing_style` — URL style: `path`, `virtual`, or `auto` (default)
- `us_east_1_regional_endpoint` — use regional endpoint for us-east-1
- `payload_signing_enabled` — sign request payloads
- `disable_multi_region_access_points` — disable Multi-Region Access Points
- `disable_express_session_auth` — opt out of S3 Express One Zone session authentication

## Retry Configuration

Configure retries at multiple levels:

**AWS config file:**

```ini
[default]
retry_max_attempts = 10
retry_mode = adaptive
```

**Environment variables:**

```bash
export AWS_MAX_ATTEMPTS=10
export AWS_RETRY_MODE=adaptive
```

**Config object (highest priority):**

```python
from botocore.config import Config

config = Config(
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

client = boto3.client('s3', config=config)
```

## Client Context Parameters

Some services accept service-specific configuration via `client_context_params`:

```python
from botocore.config import Config

config = Config(
    client_context_params={
        'stsRegionalEndpoints': 'regional'  # or 'legacy'
    }
)

client = boto3.client('sts', config=config)
```

Available context parameters vary by service. Refer to individual service documentation for supported parameters.

## Checksum Configuration

Control when checksums are calculated and validated:

```python
from botocore.config import Config

config = Config(
    request_checksum_calculation='when_required',  # 'when_required', 'always', 'never'
    response_checksum_validation='when_required'   # 'when_required', 'always', 'never'
)

client = boto3.client('s3', config=config)
```

## SigV4a Signing

Sign requests across multiple regions with SigV4a:

```python
from botocore.config import Config

config = Config(
    sigv4a_signing_region_set=['us-east-1', 'eu-west-1', 'ap-southeast-1']
)

client = boto3.client('s3', config=config)
```

Or via environment variable:

```bash
export AWS_SIGV4A_SIGNING_REGION_SET="us-east-1,eu-west-1,ap-southeast-1"
```

## Endpoint URL Override

Point clients at custom endpoints (local testing, VPC endpoints, etc.):

```python
# LocalStack or custom endpoint
client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    region_name='us-east-1'
)

# VPC endpoint
client = boto3.client(
    'dynamodb',
    endpoint_url='https://vpce-xxxxx.vpce-svc-xxxxx.us-east-1.vpce.amazonaws.com'
)
```

## API Version

Pin a specific API version for a service:

```ini
# In ~/.aws/config
[default]
services = myservices

[plugins]
myservices = my_boto_service

# Or programmatically
client = boto3.client('s3', api_version='2006-03-01')
```

## Configuration Precedence

Configuration values follow this lookup order (highest to lowest priority):

1. `Config` object passed to client/resource creation
2. Environment variables
3. AWS config file (`~/.aws/config`)
4. Shared credentials file (`~/.aws/credentials`)
5. Boto2 config file (`~/.boto`)
6. Container credential provider
7. EC2 instance metadata service

Configurations are not atomic — individual values can be overridden at different levels independently.

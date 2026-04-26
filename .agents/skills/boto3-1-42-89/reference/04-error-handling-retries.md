# Error Handling and Retries

## Exception Sources

Boto3 exceptions come from two sources:

- **Botocore exceptions** — statically defined in the botocore package, related to client-side behaviors, configurations, or validations
- **AWS service exceptions** — dynamic errors from AWS services, varying by service and subject to change

### Botocore Exceptions

Common botocore exception classes:

- `ClientError` — generic error wrapper for all AWS service errors
- `ConnectionError` — network connectivity issues
- `EndpointConnectionError` — unable to connect to the service endpoint
- `ProxyConnectionError` — proxy connection failures
- `SSLError` — SSL/TLS negotiation errors
- `NoCredentialsError` — no credentials found in the credential chain
- `PartialCredentialsError` — incomplete credentials (missing key or secret)
- `ProfileNotFound` — specified profile does not exist
- `ParamValidationError` — invalid parameters passed to an operation
- `WaiterError` — waiter timed out waiting for resource state
- `InvalidEndpointConfigurationError` — invalid endpoint configuration
- `HTTPClientError` — underlying HTTP client error

```python
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ConnectionError

try:
    s3 = boto3.client('s3')
    response = s3.head_object(Bucket='my-bucket', Key='file.txt')
except NoCredentialsError:
    print("AWS credentials not found")
except ConnectionError:
    print("Could not connect to AWS")
except ClientError as e:
    error_code = e.response['Error']['Code']
    error_message = e.response['Error']['Message']
    print(f"AWS Error: {error_code} - {error_message}")
```

List all available botocore exceptions:

```python
import botocore.exceptions

for name in dir(botocore.exceptions):
    obj = getattr(botocore.exceptions, name)
    if isinstance(obj, type) and issubclass(obj, Exception):
        print(name)
```

### AWS Service Exceptions

AWS service errors are wrapped in `ClientError`. The error response follows a consistent structure:

```python
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')

try:
    s3_client.head_object(Bucket='nonexistent-bucket', Key='file.txt')
except ClientError as e:
    error_code = e.response['Error']['Code']       # '404' or 'NoSuchBucket'
    error_message = e.response['Error']['Message']  # descriptive message
    http_status = e.response['ResponseMetadata']['HTTPStatusCode']
    request_id = e.response['ResponseMetadata']['RequestId']
    print(f"Error {error_code}: {error_message}")
    print(f"HTTP Status: {http_status}, Request ID: {request_id}")
```

### Dynamic Service Exceptions

Access service-specific exception classes dynamically from the client:

```python
import boto3

s3_client = boto3.client('s3')

try:
    s3_client.head_object(Bucket='nonexistent', Key='file.txt')
except s3_client.exceptions.ClientError as e:
    print(f"S3 error: {e}")

# Service-specific exceptions (example with DynamoDB)
dynamodb = boto3.client('dynamodb')

try:
    dynamodb.put_item(TableName='my-table', Item={'id': {'S': '1'}})
except dynamodb.exceptions.ResourceNotFoundException:
    print("Table does not exist")
except dynamdb.exceptions.ProvisionedThroughputExceededException:
    print("Rate limited")
```

## Retry Modes

Boto3 supports three retry modes with different behavior:

### Legacy Mode (Default)

The default mode for backward compatibility:

- Default maximum attempts: 5 (including initial request)
- Retries on HTTP status codes: 429, 500, 502, 503, 504, 509
- Exponential backoff with base factor of 2
- No circuit breaking

```python
from botocore.config import Config

config = Config(retries={'mode': 'legacy', 'max_attempts': 5})
client = boto3.client('s3', config=config)
```

### Standard Mode

Standardized across AWS SDKs with extended functionality:

- Default maximum attempts: 3 (including initial request)
- Circuit-breaking to prevent retries during service outages
- Retries on HTTP status codes: 500, 502, 503, 504 (plus transient error codes)
- Exponential backoff with base factor of 2, maximum 20 seconds

```python
from botocore.config import Config

config = Config(retries={'mode': 'standard', 'max_attempts': 10})
client = boto3.client('s3', config=config)
```

### Adaptive Mode

Experimental mode with client-side rate limiting:

- All standard mode features plus adaptive rate limiting
- Token bucket algorithm dynamically adjusts call rate
- Rate-limit variables updated based on error responses
- Adapts to service error/exception state

```python
from botocore.config import Config

config = Config(retries={'mode': 'adaptive', 'max_attempts': 10})
client = boto3.client('s3', config=config)
```

## Configuring Retries

Retries can be configured at multiple levels:

**AWS config file (`~/.aws/config`):**

```ini
[default]
retry_max_attempts = 10
retry_mode = standard
```

**Environment variables:**

```bash
export AWS_MAX_ATTEMPTS=10
export AWS_RETRY_MODE=standard
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

## Detecting Retries

Check if a request was retried using response metadata:

```python
response = s3_client.list_buckets()
attempts = response['ResponseMetadata']['Retries']
print(f"Request was retried {attempts} times")
```

The `Retries` field in `ResponseMetadata` indicates the number of retry attempts made.

## Parsing Error Responses

Extract additional metadata from error responses:

```python
import boto3
from botocore.exceptions import ClientError

sqs = boto3.client('sqs')

try:
    sqs.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/123456789012/my-queue',
        MessageBody='test'
    )
except ClientError as e:
    error = e.response['Error']
    print(f"Code: {error['Code']}")
    print(f"Message: {error['Message']}")
    print(f"Type: {error.get('Type', 'N/A')}")

    metadata = e.response['ResponseMetadata']
    print(f"HTTP Status: {metadata['HTTPStatusCode']}")
    print(f"Request ID: {metadata['RequestId']}")
    print(f"Retries: {metadata.get('Retries', 0)}")
```

## Waiter Errors

Waiters raise `WaiterError` when the desired state is not reached within the timeout:

```python
from botocore.exceptions import WaiterError

ec2 = boto3.client('ec2')
instance_id = 'i-1234567890abcdef0'

try:
    ec2.get_waiter('instance_running').wait(
        InstanceIds=[instance_id],
        WaiterConfig={
            'Delay': 5,       # seconds between checks
            'MaxAttempts': 25  # maximum polling attempts
        }
    )
except WaiterError as e:
    print(f"Instance did not reach running state: {e}")
```

List available waiters for a client:

```python
print(ec2.waiter_names)
# ['instance_exists', 'instance_running', 'instance_stopped', ...]
```

# Error Handling

## Exception Types

### Botocore Exceptions (Client-Side)

These exceptions are statically defined in the `botocore.exceptions` module:

```python
import botocore.exceptions

# Common exceptions
botocore.exceptions.ClientError              # AWS service errors
botocore.exceptions.ParamValidationError     # Invalid parameters
botocore.exceptions.NoCredentialsError       # No credentials found
botocore.exceptions.PartialCredentialsError  # Incomplete credentials
botocore.exceptions.CredentialRetrievalError # Failed to retrieve credentials
botocore.exceptions.NoRegionError            # No region configured
botocore.exceptions.EndpointConnectionError  # Cannot connect to endpoint
botocore.exceptions.ConnectionError          # General connection error
botocore.exceptions.ReadTimeoutError         # Read timeout
botocore.exceptions.ConnectTimeoutError      # Connection timeout
botocore.exceptions.SSLError                 # SSL/TLS errors
botocore.exceptions.WaiterError              # Waiter timeout/failure
botocore.exceptions.PaginationError          # Pagination issues
```

### AWS Service Exceptions (Server-Side)

Service exceptions are wrapped in `ClientError` and must be parsed:

```python
import botocore.exceptions
import boto3

s3 = boto3.client('s3')

try:
    s3.head_bucket(Bucket='non-existent-bucket')
    
except botocore.exceptions.ClientError as e:
    error_code = e.response['Error']['Code']
    error_message = e.response['Error']['Message']
    request_id = e.response['ResponseMetadata']['RequestId']
    
    if error_code == '404':
        print("Bucket not found")
    elif error_code == 'NoSuchBucket':
        print(f"Bucket does not exist: {error_message}")
    elif error_code == 'AccessDenied':
        print(f"Access denied: {error_message}")
    else:
        print(f"Error {error_code}: {error_message} (Request ID: {request_id})")
```

## Error Response Structure

All `ClientError` responses follow this structure:

```python
{
    'Error': {
        'Code': 'ExceptionName',      # e.g., 'NoSuchBucket', 'AccessDenied'
        'Message': 'Human-readable error message',
        # Service-specific fields may be present
        'BucketName': 'my-bucket'     # S3-specific
    },
    'ResponseMetadata': {
        'RequestId': '1234567890ABCDEF',
        'HostId': 'hashed-host-id',
        'HTTPStatusCode': 404,
        'HTTPHeaders': {
            'x-amzn-ErrorType': 'NotFoundException',
            # ... other headers
        },
        'RetryAttempts': 0
    }
}
```

## Catching Botocore Exceptions

### Basic Exception Handling

```python
import boto3
import botocore.exceptions

s3 = boto3.client('s3')

try:
    response = s3.get_object(Bucket='my-bucket', Key='file.txt')
    
except botocore.exceptions.ClientError as e:
    # AWS service error
    handle_client_error(e)
    
except botocore.exceptions.ParamValidationError as e:
    # Invalid parameters passed to API call
    print(f"Invalid parameters: {e}")
    
except botocore.exceptions.NoCredentialsError:
    # No credentials configured
    print("Please configure AWS credentials")
    
except botocore.exceptions.NoRegionError:
    # No region specified
    print("Please specify a region")
    
except botocore.exceptions.ConnectionError as e:
    # Network connectivity issue
    print(f"Connection error: {e}")
    
except botocore.exceptions.SSLError as e:
    # SSL/TLS handshake failed
    print(f"SSL error: {e}")
```

### Parsing ClientError Responses

```python
import boto3
import botocore.exceptions

s3 = boto3.client('s3')

def handle_s3_error(error):
    """Parse and handle S3-specific errors"""
    error_code = error.response['Error']['Code']
    
    error_handlers = {
        'NoSuchBucket': handle_no_such_bucket,
        'NoSuchKey': handle_no_such_key,
        'AccessDenied': handle_access_denied,
        'InvalidArgument': handle_invalid_argument,
        'SlowDown': handle_slow_down,
        'InternalError': handle_internal_error,
    }
    
    handler = error_handlers.get(error_code)
    if handler:
        handler(error)
    else:
        handle_unknown_error(error)

def handle_no_such_bucket(error):
    bucket_name = error.response['Error'].get('BucketName')
    print(f"Bucket not found: {bucket_name}")

def handle_access_denied(error):
    print(f"Access denied - check IAM permissions")
    
def handle_slow_down(error):
    print("Throttled - implement exponential backoff")
    
def handle_unknown_error(error):
    code = error.response['Error']['Code']
    message = error.response['Error']['Message']
    request_id = error.response['ResponseMetadata']['RequestId']
    print(f"Unknown error {code}: {message} (Request ID: {request_id})")

try:
    s3.get_object(Bucket='my-bucket', Key='file.txt')
except botocore.exceptions.ClientError as e:
    handle_s3_error(e)
```

## Service-Specific Exceptions

### Using Client Exception Classes

Boto3 provides dynamically generated exception classes:

```python
import boto3

s3 = boto3.client('s3')

try:
    s3.create_bucket(Bucket='existing-bucket')
    
except s3.exceptions.BucketAlreadyExists:
    print("Bucket already exists")
    
except s3.exceptions.AlreadyInUse:
    print("Bucket name is already in use")
    
except s3.exceptions.NoSuchBucket:
    print("Bucket does not exist")

# List available exceptions
print(dir(s3.exceptions))
```

### EC2 Exception Handling

```python
import boto3

ec2 = boto3.client('ec2')

try:
    ec2.run_instances(...)
    
except ec2.exceptions.InvalidInstanceIDMalformed:
    print("Invalid instance ID format")
    
except ec2.exceptions.LimitExceededException:
    print("VPC or subnet limit exceeded")
    
except ec2.exceptions.IncorrectInstanceState:
    print("Instance is in incorrect state for operation")
    
except ec2.exceptions.ClientError as e:
    # Generic handler for other errors
    error_code = e.response['Error']['Code']
    if error_code == 'InsufficientInstanceCapacity':
        print("No capacity available for instance type")
    else:
        raise
```

### DynamoDB Exception Handling

```python
import boto3

dynamodb = boto3.client('dynamodb')

try:
    response = dynamodb.put_item(
        TableName='my-table',
        Item={'id': {'S': 'item-id'}, 'data': {'S': 'value'}}
    )
    
except dynamodb.exceptions.ResourceNotFoundException:
    print("Table does not exist")
    
except dynamodb.exceptions.ProvisionedThroughputExceededException:
    print("Throttled - increase provisioned throughput")
    
except dynamobb.exceptions.ValidationException:
    print("Invalid item structure or attributes")
    
except dynamodb.exceptions.ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'ConditionalCheckFailedException':
        print("Conditional write failed - item already exists or condition not met")
    else:
        raise
```

### SQS Exception Handling

```python
import boto3

sqs = boto3.client('sqs')

try:
    response = sqs.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/123456789012/my-queue',
        MessageBody='Hello, World!'
    )
    
except sqs.exceptions.QueueDoesNotExist:
    print("Queue does not exist")
    
except sqs.exceptions.MessageTooLongException:
    print("Message exceeds maximum size (256 KB)")
    
except sqs.exceptions.ThrottlingException:
    print("Throttled - reduce send rate")
```

## Waiter Errors

Waiters raise `WaiterError` when conditions aren't met within timeout:

```python
import boto3
import botocore.exceptions

ec2 = boto3.client('ec2')

# Launch instance
response = ec2.run_instances(
    ImageId='ami-12345678',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro'
)
instance_id = response['Instances'][0]['InstanceId']

try:
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    print(f"Instance {instance_id} is running")
    
except botocore.exceptions.WaiterError as e:
    print(f"Waiter failed: {e}")
    print(f"Last service state: {e.last_response}")
    
# Custom waiter configuration
try:
    waiter_config = {
        'Delay': 10,        # Wait 10 seconds between attempts
        'MaxAttempts': 30   # Try up to 30 times (5 minutes total)
    }
    waiter = ec2.get_waiter('instance_terminated', waiter_config)
    waiter.wait(InstanceIds=[instance_id])
    
except botocore.exceptions.WaiterError as e:
    error_code = e.response['Error']['Code'] if 'response' in e else 'Unknown'
    print(f"Waiter timeout or failure: {error_code}")
```

## Retry and Throttling Handling

### Automatic Retries

Boto3 automatically retries for transient errors when using retry modes:

```python
from botocore.config import Config
import boto3

# Standard retry mode (recommended)
config = Config(
    retries={
        'mode': 'standard',      # or 'adaptive' for high-throughput
        'total_max_attempts': 10
    }
)

s3 = boto3.client('s3', config=config)
```

### Manual Retry with Exponential Backoff

```python
import boto3
import time
import random
from botocore.exceptions import ClientError, WaiterError

def retry_with_backoff(func, max_attempts=5, base_delay=1.0):
    """Retry function with exponential backoff and jitter"""
    for attempt in range(max_attempts):
        try:
            return func()
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            # Retry on throttling or transient errors
            if error_code in ['Throttling', 'ProvisionedThroughputExceeded', 
                             'RequestLimitExceeded', 'SlowDown', 'InternalError']:
                if attempt < max_attempts - 1:
                    delay = (2 ** attempt) * base_delay + random.uniform(0, 1)
                    print(f"Retry {attempt + 1}/{max_attempts} after {delay:.2f}s")
                    time.sleep(delay)
                    continue
                    
            # Don't retry on permanent errors
            raise
            
        except Exception as e:
            # Retry on unexpected errors too
            if attempt < max_attempts - 1:
                delay = (2 ** attempt) * base_delay + random.uniform(0, 1)
                time.sleep(delay)
                continue
            raise
    
    raise Exception(f"Max retries ({max_attempts}) exceeded")

# Usage
s3 = boto3.client('s3')

def upload_file():
    s3.put_object(Bucket='my-bucket', Key='file.txt', Body=b'data')

retry_with_backoff(upload_file, max_attempts=10)
```

### Adaptive Rate Limiting

```python
from botocore.config import Config
import boto3

# Adaptive mode adjusts retry rate based on service responses
config = Config(
    retries={
        'mode': 'adaptive',
        'total_max_attempts': 20
    }
)

sqs = boto3.client('sqs', config=config)

# Send messages with automatic rate limiting
for i in range(1000):
    try:
        sqs.send_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/123456789012/my-queue',
            MessageBody=f'Message {i}'
        )
    except Exception as e:
        # Adaptive mode handles most throttling automatically
        print(f"Failed after retries: {e}")
        raise
```

## Logging and Debugging

### Enable Boto3 Logging

```python
import boto3
import logging

# Enable debug logging for all Boto3 components
boto3.set_stream_logger('', logging.DEBUG)

# Or log to file
logging.basicConfig(
    filename='boto3.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log specific components only
boto3.set_stream_logger('botocore', logging.DEBUG)
boto3.set_stream_logger('botocore.retryhandler', logging.DEBUG)
boto3.set_stream_logger('boto3', logging.WARNING)
```

### Environment Variables for Debugging

```bash
# Enable debug logging
export AWS_SDK_UA_APP_ID=myapp-debug

# Log retry attempts
export BOTOCORE_DEBUG=1

# Verbose HTTP debugging
export REQUESTS_CA_BUNDLE=/path/to/certs.pem
```

### Capturing Request/Response Metadata

```python
import boto3
import logging

logger = logging.getLogger(__name__)

s3 = boto3.client('s3')

try:
    response = s3.get_object(Bucket='my-bucket', Key='file.txt')
    
except botocore.exceptions.ClientError as e:
    # Log complete error information for debugging
    logger.error(
        "AWS Error",
        extra={
            'error_code': e.response['Error']['Code'],
            'error_message': e.response['Error']['Message'],
            'request_id': e.response['ResponseMetadata']['RequestId'],
            'host_id': e.response['ResponseMetadata'].get('HostId'),
            'http_status_code': e.response['ResponseMetadata']['HTTPStatusCode'],
            'retry_attempts': e.response['ResponseMetadata']['RetryAttempts']
        }
    )
```

## Best Practices

1. **Always catch specific exceptions first**, then generic ones
2. **Parse error codes** to implement appropriate handling logic
3. **Log request IDs** for AWS support tickets
4. **Implement exponential backoff** with jitter for retries
5. **Don't retry on permanent errors** (AccessDenied, ValidationException)
6. **Use waiter patterns** instead of manual polling loops
7. **Configure appropriate retry modes** for your workload
8. **Monitor retry metrics** to identify systemic issues

## Common Error Codes by Service

### S3 Errors

| Error Code | Meaning | Action |
|------------|---------|--------|
| NoSuchBucket | Bucket doesn't exist | Create bucket or check name |
| NoSuchKey | Object doesn't exist | Verify object key |
| AccessDenied | IAM/bucket policy denial | Check permissions |
| InvalidArgument | Invalid parameter value | Validate input parameters |
| SlowDown | Throttled (S3) | Implement backoff |
| InternalError | S3 internal error | Retry with backoff |

### EC2 Errors

| Error Code | Meaning | Action |
|------------|---------|--------|
| InvalidInstanceID.Malformed | Bad instance ID format | Validate instance ID |
| InsufficientInstanceCapacity | No capacity available | Try different AZ/instance type |
| LimitExceeded | Quota exceeded | Request quota increase |
| IncorrectInstanceState | Wrong state for operation | Wait for correct state |

### DynamoDB Errors

| Error Code | Meaning | Action |
|------------|---------|--------|
| ResourceNotFoundException | Table doesn't exist | Create table first |
| ProvisionedThroughputExceeded | Throttled | Increase throughput or use DAX |
| ValidationException | Invalid request structure | Validate item format |
| ConditionalCheckFailed | Condition not met | Handle existing item case |

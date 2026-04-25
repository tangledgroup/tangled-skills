# Clients and Resources

## Interface Comparison

| Feature | Clients (Low-level) | Resources (High-level) |
|---------|---------------------|------------------------|
| **API Mapping** | 1:1 with AWS service APIs | Object-oriented abstraction |
| **Coverage** | All service operations | Subset of common operations |
| **Thread Safety** | ✅ Thread-safe | ❌ Not thread-safe |
| **Response Format** | Raw dictionaries | Resource objects |
| **New Features** | Immediate support | May lag behind API updates |
| **Learning Curve** | Requires AWS API knowledge | More intuitive Python API |
| **Performance** | Slightly faster | Additional abstraction overhead |

## Client Interface

### Creating Clients

```python
import boto3

# Using default session and credentials
s3 = boto3.client('s3')

# Specify region
ec2 = boto3.client('ec2', region_name='us-west-2')

# Use specific profile
session = boto3.Session(profile_name='production')
dynamodb = session.client('dynamodb')

# Provide credentials directly (not recommended for production)
client = boto3.client(
    's3',
    aws_access_key_id='ACCESS_KEY',
    aws_secret_access_key='SECRET_KEY',
    region_name='us-east-1'
)

# With custom configuration
from botocore.config import Config

config = Config(
    retries={'mode': 'standard', 'total_max_attempts': 10}
)
s3 = boto3.client('s3', config=config)
```

### Client Methods

Client methods map directly to AWS service API operations (snake_case):

```python
import boto3

s3 = boto3.client('s3')

# List buckets (maps to ListBuckets API)
response = s3.list_buckets()

# Create bucket (maps to CreateBucket API)
response = s3.create_bucket(
    Bucket='my-unique-bucket',
    CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
)

# Put object (maps to PutObject API)
response = s3.put_object(
    Bucket='my-bucket',
    Key='path/to/file.txt',
    Body=b'file content',
    Metadata={'custom-key': 'custom-value'}
)

# Get object (maps toGetObject API)
response = s3.get_object(
    Bucket='my-bucket',
    Key='path/to/file.txt'
)
content = response['Body'].read()

# Delete object (maps to DeleteObject API)
response = s3.delete_object(
    Bucket='my-bucket',
    Key='path/to/file.txt'
)
```

### Client Response Structure

All client responses are Python dictionaries:

```python
response = s3.list_buckets()

# Response structure
{
    'Buckets': [
        {
            'Name': 'bucket-name',
            'CreationDate': datetime.datetime(2024, 1, 1, 0, 0, 0, tzinfo=tzutc())
        }
    ],
    'Owner': {
        'DisplayName': 'user-display-name',
        'ID': 'owner-id'
    },
    'ResponseMetadata': {
        'RequestId': 'request-id',
        'HostId': 'host-id',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {...},
        'RetryAttempts': 0
    }
}

# Access response data
for bucket in response.get('Buckets', []):
    print(bucket['Name'])

# Check HTTP status code
status = response['ResponseMetadata']['HTTPStatusCode']
```

### Client Metadata

```python
import boto3

s3 = boto3.client('s3')

# Access client metadata
print(s3.meta.service_model.service_name)  # 's3'
print(s3.meta.region_name)  # 'us-east-1'
print(s3.meta.endpoint_url)  # 'https://s3.us-east-1.amazonaws.com'

# Get available waiter names
print(s3.waiter_names)
# ['bucket_exists', 'bucket_not_exists', 'object_exists', 'object_not_exists']

# Get service exceptions
print(dir(s3.exceptions))
# [AccessDenied, BucketAlreadyExists, NoSuchBucket, ...]
```

### Client Waiters

Waiters poll for resource state changes:

```python
import boto3

s3 = boto3.client('s3')

# Create a bucket
s3.create_bucket(Bucket='my-bucket')

# Wait for bucket to exist
waiter = s3.get_waiter('bucket_exists')
waiter.wait(Bucket='my-bucket')

# Or use one-liner syntax
s3.get_waiter('bucket_exists').wait(Bucket='my-bucket')

# Wait with custom configuration
waiter_config = {
    'Delay': 5,      # Seconds between attempts
    'MaxAttempts': 20
}
waiter = s3.get_waiter('object_exists', waiter_config)
waiter.wait(Bucket='my-bucket', Key='file.txt')

# List available waiters for a client
print(s3.waiter_names)
```

### Client Paginators

Paginators handle automatic pagination:

```python
import boto3

s3 = boto3.client('s3')

# Get paginator for an operation
paginator = s3.get_paginator('list_objects_v2')

# Paginate through all results
page_iterator = paginator.paginate(Bucket='my-bucket')

for page in page_iterator:
    if 'Contents' in page:
        for obj in page['Contents']:
            print(obj['Key'])

# Configure pagination
page_iterator = paginator.paginate(
    Bucket='my-bucket',
    PaginationConfig={
        'PageSize': 100,           # Items per page
        'MaxItems': 1000,          # Total items to return
        'StartingToken': 'token'   # Resume from specific position
    }
)

# Filter with JMESPath
filtered = page_iterator.search("Contents[?Size > `1048576`].Key")
for key in filtered:
    print(f"Large file: {key}")
```

## Resource Interface

### Creating Resources

```python
import boto3

# Create resource with default session
s3 = boto3.resource('s3')

# Specify region
ec2 = boto3.resource('ec2', region_name='us-west-2')

# Use custom session
session = boto3.Session(profile_name='production')
dynamodb = session.resource('dynamodb')

# With custom configuration
from botocore.config import Config

config = Config(retries={'mode': 'standard'})
s3 = boto3.resource('s3', config=config)
```

### Resource Identifiers and Attributes

Resources have identifiers (required) and attributes (lazy-loaded):

```python
import boto3

s3 = boto3.resource('s3')

# Bucket resource - 'name' is the identifier
bucket = s3.Bucket('my-bucket')
print(bucket.name)  # Identifier, available immediately

# Object resource - both bucket_name and key are identifiers
obj = s3.Object('my-bucket', 'path/to/file.txt')
print(obj.bucket_name)  # Identifier
print(obj.key)          # Identifier

# Attributes are lazy-loaded
print(obj.last_modified)  # Triggers HeadObject API call
print(obj.etag)           # Also triggers load if not already loaded

# Explicitly load attributes
obj.load()  # Makes API call to fetch all attributes

# Reload attributes
obj.reload()  # Refreshes from server
```

### Resource Actions

Actions are methods that make API calls:

```python
import boto3

s3 = boto3.resource('s3')

# Upload file
bucket = s3.Bucket('my-bucket')
bucket.upload_file('local-file.txt', 'remote-file.txt')

# Download file
bucket.download_file('remote-file.txt', 'downloaded.txt')

# Copy object
obj = bucket.Object('source.txt')
obj.copy_from(Key='destination.txt')

# Delete object
obj.delete()

# Get object metadata
response = obj.get()
content = response['Body'].read()

# Send SQS message
sqs = boto3.resource('sqs')
queue = sqs.Queue(url='https://sqs.us-east-1.amazonaws.com/123456789012/my-queue')
queue.send_message(MessageBody='Hello, World!')

# Receive messages
messages = queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=5)
for msg in messages:
    print(msg.body)
    msg.delete()  # Delete after processing
```

### Resource Collections

Collections provide iterable access to groups of resources:

```python
import boto3

s3 = boto3.resource('s3')

# Iterate over all buckets
for bucket in s3.buckets.all():
    print(bucket.name)

# Filter collections
for obj in bucket.objects.filter(Prefix='images/'):
    print(obj.key)

# Limit results
for bucket in s3.buckets.limit(10):
    print(bucket.name)

# Control page size
for obj in bucket.objects.page_size(100):
    print(obj.key)

# Chain filters
base = ec2.instances.filter(InstanceIds=['i-123', 'i-456'])
running = base.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

for instance in running:
    print(instance.id)
```

### Batch Actions

Batch actions operate on entire collections:

```python
import boto3

s3 = boto3.resource('s3')
bucket = s3.Bucket('my-bucket')

# Delete all objects in bucket (DANGEROUS!)
bucket.objects.delete()

# Delete objects with prefix
bucket.objects.filter(Prefix='temp/').delete()

# SQS batch receive and delete
sqs = boto3.resource('sqs')
queue = sqs.Queue(url='queue-url')

messages = queue.receive_messages(MaxNumberOfMessages=10)
for msg in messages:
    print(msg.body)
    
# Batch delete
receipt_handles = [(msg, msg.receipt_handle) for msg in messages]
queue.delete_messages_batch(DeleteMessageEntries=receipt_handles)
```

### Sub-resources

Sub-resources are related to parent resources and share identifiers:

```python
import boto3

s3 = boto3.resource('s3')

# Bucket is a resource, Object is a sub-resource of Bucket
bucket = s3.Bucket('my-bucket')
obj = bucket.Object(key='file.txt')  # Sub-resource

print(obj.bucket_name)  # Inherited from parent bucket

# EC2 instance and its sub-resources
ec2 = boto3.resource('ec2')
instance = ec2.Instance('i-1234567890abcdef0')

# Security groups are related resources
for sg in instance.security_groups:
    print(sg.id)

# Create a volume as sub-resource of instance
volume = instance.create_volume(...)
```

### References

References point to related resources without sharing identifiers:

```python
import boto3

ec2 = boto3.resource('ec2')
instance = ec2.Instance('i-1234567890abcdef0')

# VPC and subnet are references (many-to-one relationships)
vpc = instance.vpc
subnet = instance.subnet

print(vpc.id)  # May trigger API call to load reference
print(subnet.id)
```

## Thread Safety

### Clients (Thread-Safe)

```python
import boto3
from concurrent.futures import ThreadPoolExecutor

# Create single client - safe to share across threads
s3_client = boto3.client('s3')

def process_file(filename):
    s3_client.put_object(
        Bucket='my-bucket',
        Key=filename,
        Body=open(filename, 'rb').read()
    )

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(process_file, ['file1.txt', 'file2.txt', 'file3.txt'])
```

### Resources (Not Thread-Safe)

```python
import boto3
from concurrent.futures import ThreadPoolExecutor

def process_with_resource(filename):
    # Create new resource per thread
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('my-bucket')
    bucket.upload_file(filename, filename)

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(process_with_resource, ['file1.txt', 'file2.txt'])
```

### Sessions (Not Thread-Safe)

```python
import boto3
import boto3.session
from concurrent.futures import ThreadPoolExecutor

def worker(task_id):
    # Create new session per thread
    session = boto3.session.Session()
    s3 = session.client('s3')
    # ... use s3 client ...

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(worker, range(10))
```

## When to Use Each Interface

### Use Clients When:
- You need access to the latest AWS API features
- You want thread-safe objects for concurrent applications
- You need fine-grained control over API parameters
- You're working with services that have limited resource modeling
- Performance is critical (slightly faster than resources)

### Use Resources When:
- You're doing common operations on well-modeled services (S3, EC2, SQS)
- You prefer object-oriented Python code
- You want automatic pagination through collections
- You're building prototypes or scripts
- Readability is more important than performance

## Migration from Resources to Clients

```python
# Resource approach
s3 = boto3.resource('s3')
bucket = s3.Bucket('my-bucket')
for obj in bucket.objects.all():
    print(obj.key)
    if obj.size > 1048576:
        obj.delete()

# Equivalent client approach
s3_client = boto3.client('s3')
paginator = s3_client.get_paginator('list_objects_v2')

for page in paginator.paginate(Bucket='my-bucket'):
    if 'Contents' in page:
        for obj in page['Contents']:
            print(obj['Key'])
            if obj['Size'] > 1048576:
                s3_client.delete_object(Bucket='my-bucket', Key=obj['Key'])
```

## Common Patterns

### Factory Pattern for Clients

```python
import boto3
from botocore.config import Config

class AWSServiceFactory:
    def __init__(self, region=None, profile=None):
        self.region = region
        self.profile = profile
        self._clients = {}
        
    def _get_session(self):
        if self.profile:
            return boto3.Session(profile_name=self.profile)
        return boto3.session.Session()
    
    def client(self, service_name, **kwargs):
        key = (service_name, kwargs.get('region_name', self.region))
        
        if key not in self._clients:
            session = self._get_session()
            config = kwargs.pop('config', None)
            region = kwargs.pop('region_name', self.region)
            
            client_kwargs = {**kwargs}
            if region:
                client_kwargs['region_name'] = region
            if config:
                client_kwargs['config'] = config
                
            self._clients[key] = session.client(service_name, **client_kwargs)
        
        return self._clients[key]

# Usage
factory = AWSServiceFactory(region='us-east-1')
s3 = factory.client('s3')
ec2 = factory.client('ec2', region_name='eu-west-1')
```

### Context Manager for Temporary Resources

```python
from contextlib import contextmanager
import boto3

@contextmanager
def s3_client(region=None):
    """Context manager for S3 client with automatic cleanup"""
    client = boto3.client('s3', region_name=region)
    try:
        yield client
    finally:
        # Cleanup if needed (e.g., close connections)
        pass

# Usage
with s3_client('us-east-1') as s3:
    response = s3.list_buckets()
```

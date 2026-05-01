# S3 Operations

## Managed Transfer

Boto3 provides `boto3.s3.transfer` for high-performance file transfers with automatic multipart support, threading, and progress callbacks:

```python
import boto3
from boto3.s3.transfer import TransferConfig

s3_client = boto3.client('s3')

# Simple upload
s3_client.upload_file('local-file.txt', 'my-bucket', 'remote-key.txt')

# Simple download
s3_client.download_file('my-bucket', 'remote-key.txt', 'local-file.txt')

# With transfer configuration
config = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,   # 8 MB threshold for multipart
    max_concurrency=10,                      # max thread pool size
    multipart_chunksize=8 * 1024 * 1024,    # chunk size for multipart
    use_threads=True,                        # enable threading
    max_io_queue=100                        # max I/O queue size
)

s3_client.upload_file('large-file.zip', 'my-bucket', 'large-file.zip', Config=config)
```

Transfer configuration options:

- `multipart_threshold` — file size threshold to trigger multipart upload (default: 8 MB)
- `multipart_chunksize` — size of each part in multipart upload (default: 8 MB)
- `max_concurrency` — maximum number of threads for transfers (default: 10)
- `use_threads` — whether to use threading for multipart uploads (default: True)
- `max_io_queue` — size of the I/O queue (default: 100)
- `subdirectory` — subdirectory to create within bucket
- `sse_kms_key_id` — KMS key ID for server-side encryption
- `sse_algorithm` — encryption algorithm (`AES256`, `aws:kms`)
- `request_payer` — who pays for request (`requester` for requester-pays buckets)
- `transfer_mode` — transfer manager selection: `auto` (default), `crt`, or `legacy`

## Resource-Based S3 Operations

The S3 resource provides an object-oriented interface:

```python
import boto3

s3 = boto3.resource('s3')

# Create a bucket
bucket = s3.create_bucket(Bucket='my-new-bucket', CreateBucketConfiguration={
    'LocationConstraint': 'eu-west-1'
})

# Access an existing bucket
bucket = s3.Bucket('my-bucket')

# List objects
for obj in bucket.objects.all():
    print(obj.key, obj.size, obj.last_modified)

# Upload data
bucket.put_object(Key='hello.txt', Body=b'Hello, World!')

# Download data
obj = bucket.Object('hello.txt')
data = obj.get()['Body'].read()

# Delete object
obj.delete()

# Batch delete objects
bucket.objects.filter(Prefix='logs/').delete()
```

## Presigned URLs

Generate time-limited URLs for private objects without requiring AWS credentials:

```python
import boto3
from datetime import timedelta

s3_client = boto3.client('s3')

# Generate presigned URL (valid for 1 hour by default)
url = s3_client.generate_presigned_url(
    'get_object',
    Params={
        'Bucket': 'my-bucket',
        'Key': 'private-file.txt'
    },
    ExpiresIn=3600  # seconds
)

# Presigned URL for PUT (upload)
url = s3_client.generate_presigned_url(
    'put_object',
    Params={
        'Bucket': 'my-bucket',
        'Key': 'uploaded-file.txt'
    },
    ExpiresIn=3600,
    HttpMethod='PUT'
)

# Presigned URL with custom headers
url = s3_client.generate_presigned_url(
    'get_object',
    Params={
        'Bucket': 'my-bucket',
        'Key': 'private-file.txt',
        'ResponseContentDisposition': 'attachment; filename="download.txt"',
        'ResponseContentType': 'application/octet-stream'
    },
    ExpiresIn=3600
)
```

## Bucket Policies

Manage bucket-level access policies:

```python
import boto3
import json

s3_client = boto3.client('s3')

# Put bucket policy
policy = {
    'Version': '2012-10-17',
    'Statement': [{
        'Effect': 'Allow',
        'Principal': '*',
        'Action': ['s3:GetObject'],
        'Resource': 'arn:aws:s3:::my-bucket/*'
    }]
}

s3_client.put_bucket_policy(
    Bucket='my-bucket',
    Policy=json.dumps(policy)
)

# Get bucket policy
response = s3_client.get_bucket_policy(Bucket='my-bucket')
print(response['Policy'])

# Delete bucket policy
s3_client.delete_bucket_policy(Bucket='my-bucket')
```

## Access Control Lists (ACLs)

Set object-level permissions:

```python
import boto3

s3_client = boto3.client('s3')

# Upload with public-read ACL
s3_client.put_object(
    Bucket='my-bucket',
    Key='public-file.txt',
    Body=b'Hello, World!',
    ACL='public-read'
)

# Valid ACL values: private, public-read, public-read-write,
# authenticated-read, aws-exec-read, bucket-owner-read,
# bucket-owner-full-control, log-delivery-write
```

## CORS Configuration

Configure Cross-Origin Resource Sharing:

```python
import boto3

s3_client = boto3.client('s3')

cors_config = {
    'CORSRules': [{
        'AllowedOrigins': ['https://example.com'],
        'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE'],
        'AllowedHeaders': ['*'],
        'MaxAgeSeconds': 3000
    }]
}

s3_client.put_bucket_cors(
    Bucket='my-bucket',
    CORSConfiguration=cors_config
)
```

## Static Website Hosting

Configure an S3 bucket as a static website:

```python
import boto3

s3_client = boto3.client('s3')

# Enable website hosting
s3_client.put_bucket_website(
    Bucket='my-bucket',
    WebsiteConfiguration={
        'IndexDocument': {'Suffix': 'index.html'},
        'ErrorDocument': {'Key': 'error.html'}
    }
)

# Access via http://my-bucket.s3-website-us-east-1.amazonaws.com/
```

## Multi-Region Access Points

Access data across multiple AWS regions through a single DNS name:

```python
import boto3
from botocore.config import Config

config = Config(
    s3={
        'disable_multi_region_access_points': False
    }
)

client = boto3.client('s3', config=config)
response = client.list_objects_v2(Bucket='my-mrap-bucket')
```

Requires AWS CRT dependency (`botocore[crt]`) for full functionality.

## S3 Transfer Acceleration

Speed up uploads using CloudFront edge locations:

```python
import boto3
from botocore.config import Config

config = Config(s3={'use_accelerate_endpoint': True})
client = boto3.client('s3', config=config)

# Enable acceleration on the bucket
client.put_bucket_accelerate_configuration(
    Bucket='my-bucket',
    AccelerateConfiguration={'Status': 'Enabled'}
)
```

## Copying Objects

Copy objects within or between buckets:

```python
import boto3

s3_client = boto3.client('s3')

# Copy within same bucket
s3_client.copy_object(
    Bucket='my-bucket',
    Key='dest-key.txt',
    CopySource={'Bucket': 'my-bucket', 'Key': 'source-key.txt'}
)

# Copy between buckets
s3_client.copy_object(
    Bucket='destination-bucket',
    Key='dest-key.txt',
    CopySource={'Bucket': 'source-bucket', 'Key': 'source-key.txt'}
)

# For large files, use copy_obj helper
from boto3.s3.transfer import copy
copy(
    {'Bucket': 'source-bucket', 'Key': 'large-file.zip'},
    'destination-bucket',
    'large-file.zip',
    client=s3_client,
    config=TransferConfig(multipart_chunksize=8 * 1024 * 1024)
)
```

## Progress Callbacks

Track upload/download progress:

```python
import boto3

class ProgressCallback:
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            print(f"\r{self._filename}: {self._seen_so_far}/{self._size} ({percentage:.1f}%)", end='')

s3_client = boto3.client('s3')
s3_client.upload_file(
    'large-file.zip',
    'my-bucket',
    'large-file.zip',
    Callback=ProgressCallback('large-file.zip')
)
```

## S3 Control (Access Grants)

S3 Access Grants provides centralized authorization for cross-account data access:

```python
import boto3

s3control = boto3.client('s3control')

# List data locations
response = s3control.list_data_locations(AccountId='123456789012')

# Get data access credentials
response = s3control.get_data_access(
    AccountId='123456789012',
    DataAccessTarget={'GrantDefinitionId': 'def-xxxxx'}
)
```

## S3 Tables (Nested Types)

As of version 1.42.80, S3 Tables supports nested types for complex column schemas:

```python
import boto3

s3tables = boto3.client('s3tables')

# Create table with nested struct type
response = s3tables.create_table(
    Name='my-table',
    BucketName='my-bucket',
    TableBucketArn='arn:aws:s3:::my-bucket',
    ColumnSchema=[
        {'Name': 'id', 'Type': 'bigint'},
        {
            'Name': 'address',
            'Type': {
                'StructType': {
                    'Members': {
                        'street': {'Type': 'string'},
                        'city': {'Type': 'string'},
                        'zip': {'Type': 'string'}
                    }
                }
            }
        }
    ]
)
```

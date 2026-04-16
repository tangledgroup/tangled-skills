# Pagination and Collections

## Paginators (Client Interface)

### Basic Pagination

Some AWS operations return truncated results requiring pagination. Paginators automate this process:

```python
import boto3

s3 = boto3.client('s3')

# Get paginator for list_objects_v2 operation
paginator = s3.get_paginator('list_objects_v2')

# Create page iterator
page_iterator = paginator.paginate(Bucket='my-bucket')

# Iterate through all pages
for page in page_iterator:
    if 'Contents' in page:
        for obj in page['Contents']:
            print(obj['Key'])
```

### Paginator Configuration

```python
import boto3

s3 = boto3.client('s3')
paginator = s3.get_paginator('list_objects_v2')

# Configure pagination behavior
page_iterator = paginator.paginate(
    Bucket='my-bucket',
    PaginationConfig={
        'PageSize': 100,           # Items per API call
        'MaxItems': 1000,          # Total items to return (across all pages)
        'StartingToken': 'token'   # Resume from specific position
    }
)

# Process limited results
count = 0
for page in page_iterator:
    if 'Contents' in page:
        for obj in page['Contents']:
            print(obj['Key'])
            count += 1
            
print(f"Processed {count} objects")
```

### Pagination Parameters Explained

| Parameter | Description | Default |
|-----------|-------------|---------|
| PageSize | Number of items per API request | Service-specific |
| MaxItems | Maximum total items to return | Unlimited |
| StartingToken | Resume token from previous pagination | Beginning |

### Getting Resumption Token

```python
import boto3

s3 = boto3.client('s3')
paginator = s3.get_paginator('list_objects_v2')

# Get first page
page_iterator = paginator.paginate(Bucket='my-bucket', PaginationConfig={'PageSize': 100})

for i, page in enumerate(page_iterator):
    print(f"Page {i + 1}")
    
    # Get token to resume later
    if page.get('IsTruncated'):
        token = page['NextContinuationToken']
        print(f"Resumption token: {token}")
        
        # Save token for later resumption
        break

# Resume from saved token later
resumed_iterator = paginator.paginate(
    Bucket='my-bucket',
    PaginationConfig={
        'StartingToken': token
    }
)
```

### JMESPath Filtering with Paginators

JMESPath allows client-side filtering of paginated results:

```python
import boto3

s3 = boto3.client('s3')
paginator = s3.get_paginator('list_objects_v2')
page_iterator = paginator.paginate(Bucket='my-bucket')

# Filter objects larger than 1MB (1048576 bytes)
large_files = page_iterator.search("Contents[?Size > `1048576`].Key")
for key in large_files:
    print(f"Large file: {key}")

# Filter by prefix and size
filtered = page_iterator.search(
    "Contents[?contains(Key, 'images/') && Size > `1024000`]"
)
for obj in filtered:
    print(f"{obj['Key']}: {obj['Size']} bytes")

# Extract specific fields
summaries = page_iterator.search("Contents[].{Name: Key, Size: Size, Type: StorageClass}")
for summary in summaries:
    print(f"{summary['Name']}: {summary['Size']} ({summary['Type']})")

# Get total size of all objects
total_size_query = "sum(Contents[].Size)"
total_size = page_iterator.search(total_size_query)
print(f"Total size: {total_size} bytes")
```

### Common JMESPath Expressions

```python
# List only keys
keys = page_iterator.search("Contents[].Key")

# Filter by storage class
standard_objects = page_iterator.search("Contents[?StorageClass == 'STANDARD']")

# Get objects modified after specific timestamp (client-side filtering)
recent = page_iterator.search(
    "Contents[?LastModified > `2024-01-01T00:00:00Z`]"
)

# Sort by size (descending)
sorted_by_size = page_iterator.search("sort_by(Contents, &Size)[-5:]")

# Group by prefix (first path component)
grouped = page_iterator.search(
    "group_by(Contents, &Key) | {images: @['images/'], docs: @['docs/']}"
)
```

### EC2 Paginator Examples

```python
import boto3

ec2 = boto3.client('ec2')

# List all instances across all regions
paginator = ec2.get_paginator('describe_instances')

for page in paginator.paginate():
    for reservation in page['Reservations']:
        for instance in reservation['Instances']:
            print(f"{instance['InstanceId']}: {instance['State']['Name']}")

# Filter running instances with JMESPath
running = paginator.paginate(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
)
instance_ids = running.search("Reservations[].Instances[].InstanceId")

for instance_id in instance_ids:
    print(instance_id)

# List all VPCs
vpc_paginator = ec2.get_paginator('describe_vpcs')
for page in vpc_paginator.paginate():
    for vpc in page['Vpcs']:
        print(f"{vpc['VpcId']}: {vpc['State']}")
```

### DynamoDB Paginator Examples

```python
import boto3

dynamodb = boto3.client('dynamodb')

# Scan entire table
paginator = dynamodb.get_paginator('scan')

for page in paginator.paginate(TableName='my-table'):
    for item in page['Items']:
        print(item)

# Query with pagination
paginator = dynamodb.get_paginator('query')

for page in paginator.paginate(
    TableName='my-table',
    KeyConditionExpression='pk = :pk',
    ExpressionAttributeValues={':pk': {'S': 'user#123'}}
):
    for item in page['Items']:
        print(item)

# Filter results with JMESPath
high_value_items = paginator.paginate(TableName='my-table').search(
    "Items[?price > `100`]"
)
for item in high_value_items:
    print(item)
```

## Collections (Resource Interface)

### Basic Collection Usage

Collections provide iterable access to resource groups:

```python
import boto3

s3 = boto3.resource('s3')

# Iterate over all buckets
for bucket in s3.buckets.all():
    print(bucket.name)

# Iterate over objects in a bucket
bucket = s3.Bucket('my-bucket')
for obj in bucket.objects.all():
    print(obj.key)

# SQS - list all queues
sqs = boto3.resource('sqs')
for queue in sqs.queues.all():
    print(queue.url)
```

### Collection Filtering

Filter collections server-side using the `filter()` method:

```python
import boto3

s3 = boto3.resource('s3')
bucket = s3.Bucket('my-bucket')

# Filter by prefix
for obj in bucket.objects.filter(Prefix='images/'):
    print(obj.key)

# Filter by suffix
for obj in bucket.objects.filter(Suffix='.jpg'):
    print(obj.key)

# Multiple filters (all must match)
for obj in bucket.objects.filter(Prefix='docs/', Delimiter='/'):
    print(obj.key)

# EC2 - filter instances
ec2 = boto3.resource('ec2')

filters = [
    {'Name': 'instance-state-name', 'Values': ['running']},
    {'Name': 'instance-type', 'Values': ['t2.micro', 't3.micro']}
]

for instance in ec2.instances.filter(Filters=filters):
    print(f"{instance.id}: {instance.instance_type}")
```

### Collection Limiting

Limit the number of results returned:

```python
import boto3

s3 = boto3.resource('s3')

# Get first 10 buckets
for bucket in s3.buckets.limit(10):
    print(bucket.name)

# Limit objects in bucket
bucket = s3.Bucket('my-bucket')
for obj in bucket.objects.limit(100):
    print(obj.key)
```

### Collection Page Size

Control the number of items fetched per API call:

```python
import boto3

s3 = boto3.resource('s3')
bucket = s3.Bucket('my-bucket')

# Fetch 50 objects at a time (helpful for slow connections)
for obj in bucket.objects.page_size(50):
    print(obj.key)

# Chain with limit
for obj in bucket.objects.page_size(100).limit(500):
    print(obj.key)
```

### Collection Chaining

Collection methods return new collections and can be chained:

```python
import boto3

ec2 = boto3.resource('ec2')

# Build base collection
base = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}]
)

# Create filtered views (doesn't modify base)
running = base.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
stopped = base.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])

# Further filter
t2_instances = running.filter(
    Filters=[{'Name': 'instance-type', 'Values': ['t2.micro']}]
)

print("All instances:")
for instance in base:
    print(instance.id)

print("\nRunning t2.micro instances:")
for instance in t2_instances:
    print(instance.id)
```

### Batch Actions

Perform actions on entire collections:

```python
import boto3

s3 = boto3.resource('s3')
bucket = s3.Bucket('my-bucket')

# Delete all objects (DANGEROUS!)
# bucket.objects.delete()

# Delete objects with prefix
bucket.objects.filter(Prefix='temp/').delete()

# Delete specific objects
objects_to_delete = [
    bucket.Object(key='file1.txt'),
    bucket.Object(key='file2.txt')
]
for obj in objects_to_delete:
    obj.delete()

# SQS batch operations
sqs = boto3.resource('sqs')
queue = sqs.Queue(url='https://sqs.us-east-1.amazonaws.com/123456789012/my-queue')

# Receive up to 10 messages
messages = queue.receive_messages(
    MaxNumberOfMessages=10,
    WaitTimeSeconds=5,
    VisibilityTimeout=300
)

# Process and delete in batch
receipt_handles = []
for msg in messages:
    print(msg.body)
    receipt_handles.append({'Id': str(len(receipt_handles)), 'ReceiptHandle': msg.receipt_handle})

if receipt_handles:
    queue.delete_messages_batch(DeleteMessageEntries=receipt_handles)
```

### Collection Metadata

```python
import boto3

s3 = boto3.resource('s3')
bucket = s3.Bucket('my-bucket')

# Get collection operation name
print(bucket.objects.meta.data_load_service_method)  # 'list_objects'

# Access underlying client
client = bucket.meta.client
response = client.list_objects_v2(Bucket=bucket.name)
```

## DynamoDB Specific Pagination

### Scan Operation

```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('my-table')

# Scan all items (expensive for large tables)
for item in table.scan().iter_all():
    print(item)

# Scan with filter
response = table.scan(
    FilterExpression='age > :age',
    ExpressionAttributeValues={':age': 30}
)

for item in response['Items']:
    print(item)

# Paginated scan
paginator = table.meta.client.get_paginator('scan')
for page in paginator.paginate(TableName='my-table'):
    for item in page['Items']:
        print(item)
```

### Query Operation

```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('my-table')

# Query by partition key
response = table.query(
    KeyConditionExpression='pk = :pk',
    ExpressionAttributeValues={':pk': {'S': 'user#123'}}
)

for item in response['Items']:
    print(item)

# Query with sort key range
response = table.query(
    KeyConditionExpression='pk = :pk AND begins_with(sk, :sk_prefix)',
    ExpressionAttributeValues={
        ':pk': {'S': 'user#123'},
        ':sk_prefix': {'S': 'order#'}
    }
)

# Query with pagination
paginator = table.meta.client.get_paginator('query')
for page in paginator.paginate(
    TableName='my-table',
    KeyConditionExpression='pk = :pk',
    ExpressionAttributeValues={':pk': {'S': 'user#123'}}
):
    for item in page['Items']:
        print(item)
```

## SQS Specific Patterns

### Long Polling with Pagination

```python
import boto3
import time

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/my-queue'

# Long polling (waits up to 20 seconds for messages)
response = sqs.receive_message(
    QueueUrl=queue_url,
    MaxNumberOfMessages=10,
    WaitTimeSeconds=20,  # Long polling
    AttributeNames=['All'],
    MessageAttributeNames=['All']
)

if 'Messages' in response:
    for msg in response['Messages']:
        print(msg['Body'])
        
        # Delete after processing
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg['ReceiptHandle']
        )
```

### Batch Receive and Delete

```python
import boto3

sqs = boto3.resource('sqs')
queue = sqs.Queue(url='queue-url')

# Receive batch
messages = queue.receive_messages(
    MaxNumberOfMessages=10,
    WaitTimeSeconds=5
)

# Process messages
processed_handles = []
for msg in messages:
    try:
        # Process message
        data = msg.body
        print(data)
        
        # Track for deletion
        processed_handles.append(msg.receipt_handle)
        
    except Exception as e:
        print(f"Failed to process: {e}")

# Batch delete successfully processed messages
if processed_handles:
    delete_entries = [
        {'Id': str(i), 'ReceiptHandle': handle}
        for i, handle in enumerate(processed_handles)
    ]
    queue.delete_messages_batch(DeleteMessageEntries=delete_entries)
```

## Best Practices

1. **Always use paginators** instead of manual token management
2. **Set MaxItems** to prevent processing unlimited data
3. **Use JMESPath filtering** for client-side filtering after pagination
4. **Save resumption tokens** for long-running operations
5. **Limit collection results** when you don't need all items
6. **Use batch actions** for efficient bulk operations
7. **Implement error handling** around pagination (some items may fail)
8. **Monitor API costs** - some paginated operations can be expensive

## Common Pitfalls

### Infinite Loops with Collections

```python
# WRONG - Can cause infinite loop if items are added during iteration
for obj in bucket.objects.all():
    if should_delete(obj):
        obj.delete()  # Modifying collection while iterating

# CORRECT - Collect first, then delete
objects_to_delete = [obj for obj in bucket.objects.all() if should_delete(obj)]
for obj in objects_to_delete:
    obj.delete()
```

### Missing Empty Page Handling

```python
# WRONG - Assumes Contents key always exists
for page in paginator.paginate(Bucket='my-bucket'):
    for obj in page['Contents']:  # KeyError if empty bucket
        print(obj['Key'])

# CORRECT - Check for key existence
for page in paginator.paginate(Bucket='my-bucket'):
    if 'Contents' in page:
        for obj in page['Contents']:
            print(obj['Key'])
```

### Forgetting Pagination Token

```python
# WRONG - Manual pagination without token handling
response = s3.list_objects_v2(Bucket='my-bucket')
for obj in response['Contents']:
    process(obj)
# Only processes first 1000 objects!

# CORRECT - Use paginator
paginator = s3.get_paginator('list_objects_v2')
for page in paginator.paginate(Bucket='my-bucket'):
    if 'Contents' in page:
        for obj in page['Contents']:
            process(obj)
```

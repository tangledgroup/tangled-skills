# AWS Service Examples

## Amazon S3 (Simple Storage Service)

### Bucket Operations

```python
import boto3

s3 = boto3.client('s3')

# List all buckets
response = s3.list_buckets()
for bucket in response['Buckets']:
    print(bucket['Name'])

# Create bucket in specific region
s3.create_bucket(
    Bucket='my-unique-bucket-name',
    CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
)

# Wait for bucket to exist
waiter = s3.get_waiter('bucket_exists')
waiter.wait(Bucket='my-unique-bucket-name')

# Get bucket location
location = s3.get_bucket_location(Bucket='my-unique-bucket-name')
print(location['LocationConstraint'])

# Delete empty bucket
s3.delete_bucket(Bucket='my-unique-bucket-name')
```

### Object Operations

```python
import boto3

s3 = boto3.client('s3')

# Upload from file
with open('local-file.txt', 'rb') as f:
    s3.upload_fileobj(
        f,
        'my-bucket',
        'remote-file.txt',
        ExtraArgs={'ContentType': 'text/plain'}
    )

# Upload from string
s3.put_object(
    Bucket='my-bucket',
    Key='greeting.txt',
    Body=b'Hello, World!',
    ContentType='text/plain'
)

# Download object
response = s3.get_object(Bucket='my-bucket', Key='remote-file.txt')
content = response['Body'].read()

# Download to file
s3.download_file('my-bucket', 'remote-file.txt', 'local-file.txt')

# Copy object within bucket
s3.copy_object(
    Bucket='my-bucket',
    Key='new-file.txt',
    CopySource={'Bucket': 'my-bucket', 'Key': 'original-file.txt'}
)

# Copy object across buckets
s3.copy_object(
    Bucket='destination-bucket',
    Key='copied-file.txt',
    CopySource={'Bucket': 'source-bucket', 'Key': 'original.txt'}
)

# Delete object
s3.delete_object(Bucket='my-bucket', Key='file-to-delete.txt')

# Batch delete objects
objects_to_delete = [
    {'Key': 'file1.txt'},
    {'Key': 'file2.txt'},
    {'Key': 'file3.txt'}
]

s3.delete_objects(
    Bucket='my-bucket',
    Delete={'Objects': objects_to_delete}
)
```

### S3 Resource Interface

```python
import boto3

s3 = boto3.resource('s3')

# Upload file
bucket = s3.Bucket('my-bucket')
bucket.upload_file('local.txt', 'remote.txt')

# Download file
bucket.download_file('remote.txt', 'local.txt')

# List objects
for obj in bucket.objects.all():
    print(f"{obj.key}: {obj.size} bytes")

# Filter by prefix
for obj in bucket.objects.filter(Prefix='images/'):
    print(obj.key)

# Delete object
obj = bucket.Object('file.txt')
obj.delete()

# Copy object
obj.copy_from(Bucket='source-bucket', Key='source-key.txt')

# Get object metadata
obj.load()  # Triggers HeadObject
print(f"Size: {obj.size}")
print(f"Last Modified: {obj.last_modified}")
print(f"ETag: {obj.e_tag}")
```

### Presigned URLs

```python
import boto3
from datetime import timedelta

s3 = boto3.client('s3')

# Generate presigned GET URL (expires in 1 hour)
url = s3.generate_presigned_url(
    'get_object',
    Params={
        'Bucket': 'my-bucket',
        'Key': 'private-file.txt'
    },
    ExpiresIn=3600  # seconds
)
print(f"Download URL: {url}")

# Generate presigned PUT URL
upload_url = s3.generate_presigned_url(
    'put_object',
    Params={
        'Bucket': 'my-bucket',
        'Key': 'uploaded-file.txt'
    },
    ExpiresIn=3600
)
print(f"Upload URL: {upload_url}")

# Use with resource interface
s3_resource = boto3.resource('s3')
obj = s3_resource.Object('my-bucket', 'private-file.txt')
url = obj.generate_presigned_url('get', ExpiresIn=3600)
```

### S3 Bucket Policies

```python
import boto3
import json

s3 = boto3.client('s3')

# Create public read bucket policy
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": ["arn:aws:s3:::my-bucket/*"]
        }
    ]
}

# Put bucket policy
s3.put_bucket_policy(
    Bucket='my-bucket',
    Policy=json.dumps(policy)
)

# Get bucket policy
response = s3.get_bucket_policy(Bucket='my-bucket')
policy = json.loads(response['Policy'])
print(json.dumps(policy, indent=2))

# Delete bucket policy
s3.delete_bucket_policy(Bucket='my-bucket')
```

### S3 Lifecycle Configuration

```python
import boto3

s3 = boto3.client('s3')

# Configure lifecycle rules
lifecycle_config = {
    'Rules': [
        {
            'Id': 'TransitionToIA',
            'Status': 'Enabled',
            'Filter': {'Prefix': 'logs/'},
            'Transitions': [
                {
                    'Days': 30,
                    'StorageClass': 'GLACIER'
                }
            ]
        },
        {
            'Id': 'ExpireOldFiles',
            'Status': 'Enabled',
            'Filter': {'Prefix': 'temp/'},
            'Expiration': {'Days': 7}
        }
    ]
}

s3.put_bucket_lifecycle_configuration(
    Bucket='my-bucket',
    LifecycleConfiguration=lifecycle_config
)

# Get lifecycle config
response = s3.get_bucket_lifecycle_configuration(Bucket='my-bucket')
print(response['Rules'])

# Delete lifecycle config
s3.delete_bucket_lifecycle_configuration(Bucket='my-bucket')
```

## Amazon EC2 (Elastic Compute Cloud)

### Instance Management

```python
import boto3

ec2 = boto3.client('ec2')

# Launch instance
response = ec2.run_instances(
    ImageId='ami-0c55b159cbfafe1f0',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    KeyName='my-key-pair',
    SecurityGroups=['sg-0123456789abcdef0'],
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name', 'Value': 'MyInstance'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        }
    ]
)

instance_id = response['Instances'][0]['InstanceId']
print(f"Launched instance: {instance_id}")

# Wait for instance to be running
waiter = ec2.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance_id])

# Describe instances
response = ec2.describe_instances(
    InstanceIds=[instance_id],
    Filters=[
        {'Name': 'instance-state-name', 'Values': ['running']}
    ]
)

for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        print(f"{instance['InstanceId']}: {instance['State']['Name']}")

# Stop instance
ec2.stop_instances(InstanceIds=[instance_id])

# Wait for instance to be stopped
waiter = ec2.get_waiter('instance_stopped')
waiter.wait(InstanceIds=[instance_id])

# Start instance
ec2.start_instances(InstanceIds=[instance_id])

# Terminate instance
ec2.terminate_instances(InstanceIds=[instance_id])

# Wait for termination
waiter = ec2.get_waiter('instance_terminated')
waiter.wait(InstanceIds=[instance_id])
```

### EC2 Resource Interface

```python
import boto3

ec2 = boto3.resource('ec2')

# Get instance by ID
instance = ec2.Instance('i-1234567890abcdef0')
print(f"Instance: {instance.id}, State: {instance.state['Name']}")

# Wait for instance state
instance.wait_until_running()

# Stop and start
instance.stop()
instance.wait_until_stopped()
instance.start()
instance.wait_until_running()

# Terminate
instance.terminate()
instance.wait_until_terminated()

# List all running instances
for instance in ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
):
    print(f"{instance.id}: {instance.instance_type}")

# Create and manage tags
instance.create_tags(Tags=[{'Key': 'Environment', 'Value': 'Production'}])
print(instance.tags)

# Get related resources
print(f"VPC: {instance.vpc.id if instance.vpc else 'None'}")
print(f"Subnet: {instance.subnet.id if instance.subnet else 'None'}")
```

### Security Groups

```python
import boto3

ec2 = boto3.client('ec2')

# Create security group
response = ec2.create_security_group(
    GroupName='my-security-group',
    Description='Security group for web servers',
    VpcId='vpc-12345678'
)
sg_id = response['GroupId']

# Add inbound rules
ec2.authorize_security_group_ingress(
    GroupId=sg_id,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrBlock': '0.0.0.0/0', 'Description': 'HTTP'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 443,
            'ToPort': 443,
            'IpRanges': [{'CidrBlock': '0.0.0.0/0', 'Description': 'HTTPS'}]
        }
    ]
)

# Add outbound rules
ec2.authorize_security_group_egress(
    GroupId=sg_id,
    IpPermissions=[
        {
            'IpProtocol': '-1',  # All protocols
            'IpRanges': [{'CidrBlock': '0.0.0.0/0'}]
        }
    ]
)

# Revoke rules
ec2.revoke_security_group_ingress(
    GroupId=sg_id,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrBlock': '0.0.0.0/0'}]
        }
    ]
)

# Delete security group
ec2.delete_security_group(GroupId=sg_id)
```

## Amazon DynamoDB

### Table Operations

```python
import boto3

dynamodb = boto3.client('dynamodb')

# Create table
response = dynamodb.create_table(
    TableName='users',
    KeySchema=[
        {'AttributeName': 'user_id', 'KeyType': 'HASH'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'user_id', 'AttributeType': 'S'}
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait for table to be active
waiter = dynamodb.get_waiter('table_exists')
waiter.wait(TableName='users')

# Describe table
response = dynamodb.describe_table(TableName='users')
print(response['Table'])

# Update table throughput
dynamodb.update_table(
    TableName='users',
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

# Delete table
dynamodb.delete_table(TableName='users')
```

### Item Operations

```python
import boto3

dynamodb = boto3.client('dynamodb')

# Put item
dynamodb.put_item(
    TableName='users',
    Item={
        'user_id': {'S': 'user123'},
        'name': {'S': 'John Doe'},
        'email': {'S': 'john@example.com'},
        'age': {'N': '30'}
    }
)

# Get item
response = dynamodb.get_item(
    TableName='users',
    Key={'user_id': {'S': 'user123'}}
)
item = response.get('Item')
print(item)

# Update item
dynamodb.update_item(
    TableName='users',
    Key={'user_id': {'S': 'user123'}},
    UpdateExpression='SET #email = :email, age = :age',
    ExpressionAttributeNames={'#email': 'email'},
    ExpressionAttributeValues={
        ':email': {'S': 'newemail@example.com'},
        ':age': {'N': '31'}
    }
)

# Delete item
dynamodb.delete_item(
    TableName='users',
    Key={'user_id': {'S': 'user123'}}
)

# Batch write items
dynamodb.batch_write_item(
    RequestItems={
        'users': [
            {
                'PutRequest': {
                    'Item': {
                        'user_id': {'S': 'user456'},
                        'name': {'S': 'Jane Doe'}
                    }
                }
            },
            {
                'PutRequest': {
                    'Item': {
                        'user_id': {'S': 'user789'},
                        'name': {'S': 'Bob Smith'}
                    }
                }
            }
        ]
    }
)
```

### Query and Scan

```python
import boto3

dynamodb = boto3.client('dynamodb')

# Query by partition key
response = dynamodb.query(
    TableName='users',
    KeyConditionExpression='user_id = :uid',
    ExpressionAttributeValues={
        ':uid': {'S': 'user123'}
    }
)
for item in response['Items']:
    print(item)

# Query with sort key range
response = dynamodb.query(
    TableName='orders',
    KeyConditionExpression='user_id = :uid AND begins_with(order_id, :prefix)',
    ExpressionAttributeValues={
        ':uid': {'S': 'user123'},
        ':prefix': {'S': '2024-'}
    }
)

# Scan table (use sparingly on large tables)
response = dynamodb.scan(
    TableName='users',
    FilterExpression='age > :min_age',
    ExpressionAttributeValues={
        ':min_age': {'N': '25'}
    }
)

# Paginated scan
paginator = dynamodb.get_paginator('scan')
for page in paginator.paginate(TableName='users'):
    for item in page['Items']:
        print(item)
```

### DynamoDB Resource Interface

```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')

# Put item (Python types, no type wrappers)
table.put_item(
    Item={
        'user_id': 'user123',
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 30
    }
)

# Get item
response = table.get_item(Key={'user_id': 'user123'})
item = response.get('Item')
print(item)

# Query
response = table.query(
    KeyConditionExpression='user_id = :uid',
    ExpressionAttributeValues={':uid': 'user123'}
)
for item in response['Items']:
    print(item)

# Scan with filter
response = table.scan(
    FilterExpression='age > :min_age',
    ExpressionAttributeValues={':min_age': 25}
)

# Batch get items
keys = [
    {'user_id': 'user123'},
    {'user_id': 'user456'},
    {'user_id': 'user789'}
]
response = table.batch_get_item(Keys=keys)
for item in response['Responses']['users']:
    print(item)
```

## Amazon SQS (Simple Queue Service)

### Queue Operations

```python
import boto3

sqs = boto3.client('sqs')

# Create queue
response = sqs.create_queue(
    QueueName='my-queue',
    Attributes={
        'VisibilityTimeout': '300',
        'MessageRetentionPeriod': '1209600',  # 14 days
        'ReceiveMessageWaitTimeSeconds': '20'  # Long polling
    }
)
queue_url = response['QueueUrl']

# Get queue attributes
response = sqs.get_queue_attributes(
    QueueUrl=queue_url,
    AttributeNames=['All']
)
print(response['Attributes'])

# Set queue attributes
sqs.set_queue_attributes(
    QueueUrl=queue_url,
    Attributes={
        'VisibilityTimeout': '600'
    }
)

# Delete queue
sqs.delete_queue(QueueUrl=queue_url)
```

### Message Operations

```python
import boto3

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/my-queue'

# Send message
response = sqs.send_message(
    QueueUrl=queue_url,
    MessageBody='Hello, World!'
)
print(f"Message ID: {response['MessageId']}")

# Send message with delay
sqs.send_message(
    QueueUrl=queue_url,
    MessageBody='Delayed message',
    DelaySeconds=60  # 1 minute delay
)

# Send message with attributes
sqs.send_message(
    QueueUrl=queue_url,
    MessageBody='Message with attributes',
    MessageAttributes={
        'Temperature': {
            'DataType': 'Number',
            'StringValue': '25.5'
        }
    }
)

# Send batch messages
entries = [
    {'Id': '1', 'MessageBody': 'Message 1'},
    {'Id': '2', 'MessageBody': 'Message 2'},
    {'Id': '3', 'MessageBody': 'Message 3'}
]

response = sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)
for result in response['Successful']:
    print(f"Sent: {result['Id']}")

# Receive messages (long polling)
response = sqs.receive_message(
    QueueUrl=queue_url,
    MaxNumberOfMessages=10,
    WaitTimeSeconds=20,  # Long polling
    VisibilityTimeout=300,
    AttributeNames=['All'],
    MessageAttributeNames=['All']
)

if 'Messages' in response:
    for msg in response['Messages']:
        print(f"Body: {msg['Body']}")
        
        # Delete after processing
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg['ReceiptHandle']
        )

# Batch delete messages
receipt_handles = [
    {'Id': '1', 'ReceiptHandle': handle1},
    {'Id': '2', 'ReceiptHandle': handle2}
]
sqs.delete_message_batch(QueueUrl=queue_url, Entries=receipt_handles)

# Purge queue (waits 60 seconds)
sqs.purge_queue(QueueUrl=queue_url)
```

## AWS Lambda

### Function Management

```python
import boto3
import json
import zipfile
import io

lambda_client = boto3.client('lambda')

# Create deployment package in memory
def create_lambda_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('lambda_function.py', '''
def handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps("Hello from Lambda!")
    }
''')
    zip_buffer.seek(0)
    return zip_buffer.read()

# Create function
response = lambda_client.create_function(
    FunctionName='my-function',
    Runtime='python3.11',
    Role='arn:aws:iam::123456789012:role/lambda-execution-role',
    Handler='lambda_function.handler',
    Code={'ZipFile': create_lambda_zip()},
    Description='My Lambda function',
    Timeout=30,
    MemorySize=128,
    Environment={
        'Variables': {
            'ENVIRONMENT': 'production'
        }
    }
)

# Invoke function synchronously
response = lambda_client.invoke(
    FunctionName='my-function',
    InvocationType='RequestResponse',
    Payload=json.dumps({'key': 'value'})
)
result = json.loads(response['Body'].read())
print(result)

# Invoke function asynchronously
lambda_client.invoke(
    FunctionName='my-function',
    InvocationType='Event',  # Fire and forget
    Payload=json.dumps({'key': 'value'})
)

# Update function configuration
lambda_client.update_function_configuration(
    FunctionName='my-function',
    Timeout=60,
    MemorySize=256
)

# Get function configuration
response = lambda_client.get_function_configuration(FunctionName='my-function')
print(response)

# Delete function
lambda_client.delete_function(FunctionName='my-function')
```

## AWS IAM (Identity and Access Management)

### User Management

```python
import boto3

iam = boto3.client('iam')

# Create user
response = iam.create_user(UserName='john.doe')
print(f"Created user: {response['User']['UserName']}")

# Create access key for user
response = iam.create_access_key(UserName='john.doe')
key = response['AccessKey']
print(f"Access Key ID: {key['AccessKeyId']}")
print(f"Secret Access Key: {key['SecretAccessKey']}")  # Only shown once!

# List access keys
response = iam.list_access_keys(UserName='john.doe')
for key in response['AccessKeyMetadata']:
    print(f"{key['AccessKeyId']}: {key['Status']}")

# Delete access key
iam.delete_access_key(
    UserName='john.doe',
    AccessKeyId='AKIAIOSFODNN7EXAMPLE'
)

# Delete user (must delete all keys/policies first)
iam.delete_user(UserName='john.doe')
```

### Policy Management

```python
import boto3
import json

iam = boto3.client('iam')

# Create managed policy
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:PutObject"],
            "Resource": "arn:aws:s3:::my-bucket/*"
        }
    ]
}

response = iam.create_policy(
    PolicyName='s3-access-policy',
    PolicyDocument=json.dumps(policy_document),
    Description='Policy for S3 bucket access'
)
policy_arn = response['Policy']['Arn']

# Attach policy to user
iam.attach_user_policy(
    UserName='john.doe',
    PolicyArn=policy_arn
)

# Detach policy from user
iam.detach_user_policy(
    UserName='john.doe',
    PolicyArn=policy_arn
)

# Delete policy
iam.delete_policy(PolicyArn=policy_arn)
```

### Role Management

```python
import boto3
import json

iam = boto3.client('iam')

# Create role
trust_relationship = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }
    ]
}

response = iam.create_role(
    RoleName='ec2-role',
    AssumeRolePolicyDocument=json.dumps(trust_relationship),
    Description='Role for EC2 instances'
)
role_arn = response['Role']['Arn']

# Attach policy to role
iam.attach_role_policy(
    RoleName='ec2-role',
    PolicyArn='arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'
)

# Get role
response = iam.get_role(RoleName='ec2-role')
print(json.dumps(response['Role'], indent=2, default=str))

# Delete role
iam.delete_role(RoleName='ec2-role')
```

## Best Practices by Service

### S3
- Use presigned URLs for temporary access
- Implement lifecycle policies for cost optimization
- Enable versioning for critical data
- Use server-side encryption (SSE-S3, SSE-KMS)
- Implement bucket policies for access control

### EC2
- Use instance profiles instead of embedding credentials
- Implement tags for resource organization
- Use security groups over NACLs when possible
- Monitor with CloudWatch
- Use Auto Scaling for variable workloads

### DynamoDB
- Design tables around access patterns
- Use on-demand capacity for unpredictable workloads
- Implement proper indexing (LSI/GSI)
- Use batch operations for efficiency
- Monitor throttling and adjust throughput

### SQS
- Use long polling (WaitTimeSeconds=20)
- Implement dead-letter queues for failed messages
- Set appropriate visibility timeouts
- Use FIFO queues for ordering requirements
- Monitor queue depth and age of oldest message

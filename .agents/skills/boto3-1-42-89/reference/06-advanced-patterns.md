# Advanced Patterns

## Async Clients (aioboto3)

Boto3 clients are not natively async. For asyncio applications, use `aioboto3` which wraps Boto3 with thread pool execution:

```python
import aioboto3
import asyncio

async def list_buckets():
    async with aioboto3.Session(profile_name='my-profile') as session:
        async with session.client('s3') as s3:
            response = await s3.list_buckets()
            for bucket in response['Buckets']:
                print(bucket['Name'])

asyncio.run(list_buckets())
```

Note: aioboto3 runs Boto3 calls in a thread pool. The underlying Botocore client is not truly async but is made non-blocking from the event loop perspective.

## STS Assume Role

Programmatically assume IAM roles for cross-account access or temporary credentials:

```python
import boto3
from datetime import datetime

sts = boto3.client('sts')

# Basic assume role
response = sts.assume_role(
    RoleArn='arn:aws:iam::987654321098:role/CrossAccountRole',
    RoleSessionName='MySession',
    DurationSeconds=3600
)

credentials = response['Credentials']
print(f"Access Key: {credentials['AccessKeyId']}")
print(f"Secret Key: {credentials['SecretAccessKey']}")
print(f"Session Token: {credentials['SessionToken']}")
print(f"Expires: {credentials['Expiration']}")

# Create a client with assumed credentials
s3 = boto3.client(
    's3',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
    region_name='us-east-1'
)

# Assume role with external ID (cross-account security)
response = sts.assume_role(
    RoleArn='arn:aws:iam::987654321098:role/ExternalRole',
    RoleSessionName='ExternalSession',
    ExternalId='my-external-id-12345'
)

# Assume role with tags (for cost tracking)
response = sts.assume_role(
    RoleArn='arn:aws:iam::987654321098:role/TaggedRole',
    RoleSessionName='TaggedSession',
    Tags=[
        {'Key': 'Project', 'Value': 'my-project'},
        {'Key': 'Environment', 'Value': 'production'}
    ]
)

# Assume role with SSO (AWS IAM Identity Center)
response = sts.assume_role_with_sso(
    RoleName='AdministratorAccess',
    AccountId='123456789012',
    AccessToken='sso-access-token',
    Region='us-east-1'
)

# Assume role with web identity (OIDC federation)
response = sts.assume_role_with_web_identity(
    RoleArn='arn:aws:iam::123456789012:role/OIDCRole',
    RoleSessionName='WebIdentitySession',
    WebIdentityToken='oidc-token-content',
    ProviderId='arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com'
)
```

## Cross-Account Access Pattern

Combine sessions with assumed role credentials for clean cross-account workflows:

```python
import boto3
from botocore.exceptions import ClientError

def get_cross_account_client(service_name, role_arn, external_id=None, region='us-east-1'):
    """Get a Boto3 client for a different AWS account via STS assume role."""
    sts = boto3.client('sts', region_name=region)

    kwargs = {
        'RoleArn': role_arn,
        'RoleSessionName': f'{service_name}-session',
        'DurationSeconds': 900
    }

    if external_id:
        kwargs['ExternalId'] = external_id

    response = sts.assume_role(**kwargs)
    creds = response['Credentials']

    return boto3.client(
        service_name,
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretAccessKey'],
        aws_session_token=creds['SessionToken'],
        region_name=region
    )

# Usage
remote_s3 = get_cross_account_client(
    's3',
    'arn:aws:iam::987654321098:role/S3AccessRole',
    external_id='my-external-id'
)

for bucket in remote_s3.list_buckets()['Buckets']:
    print(bucket['Name'])
```

## Custom Events and Extensibility

Boto3/Botocore fires events that can be hooked into for custom behavior:

```python
import boto3
from botocore.handlers import disable_signing

# Add a custom event handler
s3 = boto3.client('s3')

def add_custom_header(request, **kwargs):
    request.headers['X-Custom-Header'] = 'my-value'

# Called before every request
s3.meta.events.register('before-send.s3', add_custom_header)

# Disable signing for anonymous requests (e.g., public S3 buckets)
session = boto3.Session()
session.events.register('choose-signer.s3.*', disable_signing)
anonymous_s3 = session.client('s3')

# Custom retry handler
def on_before_send(request, **kwargs):
    # Add custom logic before sending
    pass

s3.meta.events.register('before-send', on_before_send)
```

### Common Event Names

- `before-call.{service}.{operation}` — before making an API call
- `after-call.{service}.{operation}` — after receiving a response
- `before-send.{service}` — before sending the HTTP request
- `response-received.{service}` — after receiving HTTP response
- `needs-retry.{service}.{operation}` — before retrying a failed request
- `before-parameter-build.{service}.{operation}` — before building request parameters
- `create-client.{service}` — when a client is created
- `choose-signer.{service}.{operation}` — choose signing method

## Custom Endpoint Resolution

Override endpoint resolution for custom deployments:

```python
import boto3
from botocore.config import Config

# Custom endpoint (LocalStack, VPC endpoints, etc.)
config = Config(
    endpoint_url='http://localhost:4566',
    signature_version='s3v4',
    s3={'addressing_style': 'path'}
)

s3 = boto3.client('s3', config=config, region_name='us-east-1')
```

## Resource Loading and Reloading

Resource attributes are cached. Use `reload()` to fetch fresh data:

```python
import boto3

ec2 = boto3.resource('ec2')
instance = ec2.Instance('i-1234567890abcdef0')

# Initial load (makes API call)
print(instance.state['Name'])

# After some time, reload to get current state
instance.reload()
print(instance.state['Name'])  # updated state

# Reload multiple instances
ec2.instances.filter(InstanceIds=['i-aaa', 'i-bbb']).reload()
```

## JMESPath Queries with Paginators

Use JMESPath expressions with paginators to extract specific data:

```python
import boto3

ec2_client = boto3.client('ec2')
paginator = ec2_client.get_paginator('describe_instances')

# Extract only instance IDs and states using JMESPath
all_instances = paginator.paginate(
    PaginationConfig={'MaxItems': 100}
).search('Reservations[*].Instances[*].[InstanceId, State.Name]')

for instance_id, state in all_instances:
    print(f"{instance_id}: {state}")
```

## DynamoDB Type Serialization

When using the low-level DynamoDB client, Python types must be converted to DynamoDB format:

```python
import boto3
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer

dynamo_client = boto3.client('dynamodb')
serializer = TypeSerializer()
deserializer = TypeDeserializer()

# Serialize Python values to DynamoDB format
item = {
    'user_id': serializer('user-001'),           # {'S': 'user-001'}
    'age': serializer(30),                       # {'N': '30'}
    'active': serializer(True),                  # {'BOOL': True}
    'tags': serializer(['python', 'aws']),       # {'L': [{'S': 'python'}, {'S': 'aws'}]}
    'metadata': serializer({'key': 'value'}),    # {'M': {'key': {'S': 'value'}}}
    'empty': serializer(None)                    # {'NULL': True}
}

dynamo_client.put_item(TableName='Users', Item=item)

# Deserialize DynamoDB responses
response = dynamo_client.get_item(
    TableName='Users',
    Key={'user_id': {'S': 'user-001'}}
)
item = response.get('Item', {})
print(deserializer(item['age']))  # 30
```

## Conditional Operations

Use condition expressions for atomic updates and deletes:

```python
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

# Conditional put (only if item doesn't exist)
table.put_item(
    Item={'user_id': 'user-001', 'name': 'John'},
    ConditionExpression='attribute_not_exists(user_id)'
)

# Conditional update (only if current value matches)
from boto3.dynamodb.conditions import Attr
table.update_item(
    Key={'user_id': 'user-001'},
    UpdateExpression='SET #n = :val',
    ConditionExpression='attribute_exists(user_id)',
    ExpressionAttributeNames={'#n': 'name'},
    ExpressionAttributeValues={':val': 'Jane'}
)

# Conditional delete
table.delete_item(
    Key={'user_id': 'user-001'},
    ConditionExpression='attribute_exists(user_id)'
)
```

## S3 Select and Glacier Select

Query data in S3 objects without downloading the entire file:

```python
import boto3
import csv
import io

s3 = boto3.client('s3')

response = s3.select_object_content(
    Bucket='my-bucket',
    Key='data.csv',
    ExpressionType='SQL',
    Expression="SELECT * FROM S3Object s WHERE s.price > 100",
    InputSerialization={'CSV': {'FileHeaderInfo': 'USE'}},
    OutputSerialization={'CSV': {}}
)

# Process the payload events
for event in response['Payload']:
    if 'Records' in event:
        records = event['Records']['Payload']
        reader = csv.reader(io.StringIO(records.decode('utf-8')))
        for row in reader:
            print(row)
```

## Batch Operations

Many services support batch operations for efficiency:

```python
# DynamoDB batch write
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

with table.batch_writer() as batch:
    for i in range(25):  # max 25 per batch, auto-splits
        batch.put_item(Item={'user_id': f'user-{i}', 'name': f'User {i}'})

# DynamoDB batch get
dynamo_client = boto3.client('dynamodb')
response = dynamo_client.batch_get_item(
    RequestItems={
        'Users': {
            'Keys': [
                {'user_id': {'S': 'user-001'}},
                {'user_id': {'S': 'user-002'}}
            ]
        }
    }
)

# SQS batch send
sqs = boto3.client('sqs')
sqs.send_message_batch(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/123456789012/my-queue',
    Entries=[
        {'Id': 'msg-1', 'MessageBody': 'Hello 1'},
        {'Id': 'msg-2', 'MessageBody': 'Hello 2'},
    ]
)
```

## Multi-Region Operations

Operate across multiple AWS regions:

```python
import boto3

# List all regions
ec2 = boto3.client('ec2')
regions = [r['RegionName'] for r in ec2.describe_regions()['Regions']]

# Create clients for each region
for region in regions:
    s3_client = boto3.client('s3', region_name=region)
    # perform operations...

# Session-based multi-region
session = boto3.Session(profile_name='default')
clients = {
    region: session.client('ec2', region_name=region)
    for region in ['us-east-1', 'eu-west-1', 'ap-southeast-1']
}
```

## Resource Lifecycle Management

Use waiters for reliable resource lifecycle management:

```python
import boto3

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

# EC2 instance lifecycle
instances = ec2.create_instances(
    ImageId='ami-0abcdef1234567890',
    MinCount=1, MaxCount=1,
    InstanceType='t3.micro'
)
instance = instances[0]

# Wait for various states
instance.wait_until_running()
instance.wait_until_stopped()
instance.wait_until_terminated()

# S3 bucket lifecycle
s3_client = boto3.client('s3')
s3_client.create_bucket(Bucket='my-bucket')
s3_client.get_waiter('bucket_exists').wait(Bucket='my-bucket')

# Lambda function lifecycle
lambda_client = boto3.client('lambda')
lambda_client.get_waiter('function_active_v2').wait(
    FunctionName='my-function',
    WaiterConfig={'Delay': 5, 'MaxAttempts': 60}
)
```

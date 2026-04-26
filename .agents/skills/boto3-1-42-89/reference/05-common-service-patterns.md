# Common Service Patterns

## EC2 Instance Management

```python
import boto3

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

# Launch an instance
instances = ec2.create_instances(
    ImageId='ami-0abcdef1234567890',
    MinCount=1,
    MaxCount=1,
    InstanceType='t3.micro',
    KeyName='my-key-pair',
    SecurityGroupIds=['sg-0123456789abcdef0'],
    TagSpecifications=[{
        'ResourceType': 'instance',
        'Tags': [{'Key': 'Name', 'Value': 'my-instance'}]
    }]
)

instance = instances[0]
print(f"Launched instance: {instance.id}")

# Wait for instance to be running
instance.wait_until_running()
instance.reload()  # refresh attributes
print(f"Public IP: {instance.public_ip}")

# Stop and start
instance.stop()
instance.wait_until_stopped()
instance.start()
instance.wait_until_running()

# Terminate
instance.terminate()
instance.wait_until_terminated()

# Describe instances (client API)
response = ec2_client.describe_instances(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
)

# List all running instances
for reservation in response['Reservations']:
    for inst in reservation['Instances']:
        print(inst['InstanceId'], inst['InstanceState']['Name'])
```

### Key Pairs

```python
# Create key pair
response = ec2_client.create_key_pair(KeyName='my-key')
private_key = response['KeyMaterial']  # save this, it's shown only once

# Delete key pair
ec2_client.delete_key_pair(KeyName='my-key')
```

### Security Groups

```python
# Create security group
sg = ec2.create_security_group(
    GroupName='my-sg',
    Description='My security group',
    VpcId='vpc-0123456789abcdef0'
)

# Authorize inbound rule
sg.authorize_ingress(
    IpPermissions=[{
        'IpProtocol': 'tcp',
        'FromPort': 443,
        'ToPort': 443,
        'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTPS from anywhere'}]
    }]
)

# Delete security group
sg.delete()
```

### Elastic IP Addresses

```python
# Allocate EIP
allocation = ec2_client.allocate_address(Domain='vpc')
allocation_id = allocation['AllocationId']

# Associate with instance
ec2_client.associate_address(
    AllocationId=allocation_id,
    InstanceId='i-1234567890abcdef0'
)

# Release EIP
ec2_client.release_address(AllocationId=allocation_id)
```

## Lambda Functions

```python
import boto3
import zipfile
import io

lambda_client = boto3.client('lambda')

# Deploy a function (zip the code in memory)
def create_lambda_zip(handler_code):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('lambda_function.py', handler_code)
    zip_buffer.seek(0)
    return zip_buffer.read()

code = create_lambda_zip("""
def lambda_handler(event, context):
    return {'statusCode': 200, 'body': 'Hello from Lambda!'}
""")

# Create function
lambda_client.create_function(
    FunctionName='my-function',
    Runtime='python3.12',
    Role='arn:aws:iam::123456789012:role/lambda-execution-role',
    Handler='lambda_function.lambda_handler',
    Code={'ZipFile': code},
    Description='My Lambda function',
    Timeout=30,
    MemorySize=256
)

# Invoke function
response = lambda_client.invoke(
    FunctionName='my-function',
    Payload=b'{}'
)
result = response['Payload'].read().decode('utf-8')

# List functions
functions = lambda_client.list_functions()
for f in functions['Functions']:
    print(f['FunctionName'], f['Runtime'])

# Delete function
lambda_client.delete_function(FunctionName='my-function')
```

## DynamoDB Operations

```python
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
dynamo_client = boto3.client('dynamodb')

# Create table
table = dynamodb.create_table(
    TableName='Users',
    KeySchema=[
        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
        {'AttributeName': 'sort_key', 'KeyType': 'RANGE'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'user_id', 'AttributeType': 'S'},
        {'AttributeName': 'sort_key', 'AttributeType': 'S'}
    ],
    BillingMode='PAY_PER_REQUEST'
)
table.wait_until_exists()

# Put item
table.put_item(
    Item={
        'user_id': 'user-001',
        'sort_key': 'profile',
        'name': 'John Doe',
        'email': 'john@example.com'
    }
)

# Get item
response = table.get_item(
    Key={'user_id': 'user-001', 'sort_key': 'profile'}
)
item = response.get('Item')

# Query with key condition
response = table.query(
    KeyConditionExpression=Key('user_id').eq('user-001')
)
for item in response['Items']:
    print(item)

# Scan with filter
response = table.scan(
    FilterExpression=Attr('email').contains('@example.com')
)

# Update item
table.update_item(
    Key={'user_id': 'user-001', 'sort_key': 'profile'},
    UpdateExpression='SET #n = :val',
    ExpressionAttributeNames={'#n': 'name'},
    ExpressionAttributeValues={':val': 'Jane Doe'},
    ReturnValues='ALL_NEW'
)

# Delete item
table.delete_item(Key={'user_id': 'user-001', 'sort_key': 'profile'})

# Batch write
with table.batch_writer() as batch:
    for i in range(100):
        batch.put_item(Item={
            'user_id': f'user-{i:03d}',
            'sort_key': 'profile',
            'name': f'User {i}'
        })

# Low-level client API (TypeSerializer available)
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer

serializer = TypeSerializer()
deserializer = TypeDeserializer()

# Client API requires DynamoDB format
dynamo_client.put_item(
    TableName='Users',
    Item={
        'user_id': {'S': 'user-001'},
        'sort_key': {'S': 'profile'},
        'name': {'S': 'John Doe'}
    }
)
```

## SQS Messaging

```python
import boto3
import json

sqs = boto3.client('sqs')

# Create queue
response = sqs.create_queue(
    QueueName='my-queue',
    Attributes={
        'VisibilityTimeout': '30',
        'DelaySeconds': '0',
        'MessageRetentionPeriod': '86400'  # 1 day
    }
)
queue_url = response['QueueUrl']

# Send message
sqs.send_message(
    QueueUrl=queue_url,
    MessageBody=json.dumps({'action': 'process', 'data': 'value'}),
    MessageAttributes={
        'EventType': {
            'DataType': 'String',
            'StringValue': 'order.created'
        }
    }
)

# Receive messages
response = sqs.receive_message(
    QueueUrl=queue_url,
    MaxNumberOfMessages=10,
    WaitTimeSeconds=5,       # long polling
    VisibilityTimeout=30,
    MessageAttributeNames=['All']
)

for message in response.get('Messages', []):
    body = json.loads(message['Body'])
    print(body)

    # Delete after processing
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message['ReceiptHandle']
    )

# Dead-letter queue setup
# First create the DLQ
dlq_response = sqs.create_queue(QueueName='my-queue-dlq')
dlq_arn = sqs.get_queue_attributes(
    QueueUrl=dlq_response['QueueUrl'],
    AttributeNames=['QueueArn']
)['Attributes']['QueueArn']

# Then create the main queue with redrive policy
sqs.create_queue(
    QueueName='my-queue-with-dlq',
    Attributes={
        'RedrivePolicy': json.dumps({
            'deadLetterTargetArn': dlq_arn,
            'maxReceiveCount': 3
        })
    }
)

# List queues
response = sqs.list_queues()
for url in response.get('QueueUrls', []):
    print(url)

# Delete queue
sqs.delete_queue(QueueUrl=queue_url)
```

## SNS Topics

```python
import boto3
import json

sns = boto3.client('sns')

# Create topic
response = sns.create_topic(Name='my-topic')
topic_arn = response['TopicArn']

# Subscribe (email)
sns.subscribe(
    TopicArn=topic_arn,
    Protocol='email',
    Endpoint='user@example.com'
)

# Subscribe (SQS)
sns.subscribe(
    TopicArn=topic_arn,
    Protocol='sqs',
    Endpoint='arn:aws:sqs:us-east-1:123456789012:my-queue'
)

# Publish message
sns.publish(
    TopicArn=topic_arn,
    Message=json.dumps({'event': 'order.placed', 'order_id': '12345'}),
    Subject='New Order'
)

# Publish to specific protocol
sns.publish(
    TopicArn=topic_arn,
    Message='Plain text for email subscribers',
    MessageStructure='json',
    Message=json.dumps({
        'default': 'Fallback message',
        'email': '<h1>HTML email content</h1>',
        'sqs': json.dumps({'structured': 'data'})
    })
)

# List topics
for topic in sns.list_topics()['Topics']:
    print(topic['TopicArn'])

# Unsubscribe
sns.unsubscribe(SubscriptionArn='arn:aws:sns:...')

# Delete topic
sns.delete_topic(TopicArn=topic_arn)
```

## CloudWatch Monitoring

```python
import boto3
from datetime import datetime, timedelta

cloudwatch = boto3.client('cloudwatch')

# Put custom metric
cloudwatch.put_metric_data(
    Namespace='MyApp/Custom',
    MetricData=[{
        'MetricName': 'OrderCount',
        'Value': 42,
        'Unit': 'Count',
        'Dimensions': [{'Name': 'Region', 'Value': 'us-east-1'}]
    }]
)

# Get metrics
response = cloudwatch.get_metric_statistics(
    Namespace='AWS/Lambda',
    MetricName='Errors',
    Dimensions=[{'Name': 'FunctionName', 'Value': 'my-function'}],
    StartTime=datetime.now() - timedelta(hours=1),
    EndTime=datetime.now(),
    Period=300,
    Statistics=['Average', 'Maximum', 'Minimum', 'Sum']
)

# Create alarm
cloudwatch.put_metric_alarm(
    AlarmName='LambdaErrorsHigh',
    AlarmDescription='Alert when Lambda errors exceed threshold',
    MetricName='Errors',
    Namespace='AWS/Lambda',
    Dimensions=[{'Name': 'FunctionName', 'Value': 'my-function'}],
    Statistic='Sum',
    Period=300,
    EvaluationPeriods=2,
    Threshold=5,
    ComparisonOperator='GreaterThanThreshold',
    ActionsEnabled=True,
    AlarmActions=['arn:aws:sns:us-east-1:123456789012:my-topic']
)

# Describe alarms
response = cloudwatch.describe_alarms(
    AlarmNamePrefix='Lambda'
)

# CloudWatch Logs
logs = boto3.client('logs')

# Create log group
logs.create_log_group(logGroupName='/my/app/logs')

# Put log events
logs.put_log_events(
    logGroupName='/my/app/logs',
    logStreamName='stream-1',
    logEvents=[{
        'timestamp': int(datetime.now().timestamp() * 1000),
        'message': 'Application started successfully'
    }]
)

# Query logs (Logs Insights)
response = logs.start_query(
    logGroupName='/my/app/logs',
    queryString='fields @timestamp, @message | filter @message like /error/ | sort @timestamp desc | limit 20',
    startTime=int((datetime.now() - timedelta(hours=1)).timestamp()),
    endTime=int(datetime.now().timestamp())
)
query_id = response['queryId']

# Get query results
result = logs.get_query_results(queryId=query_id)
```

## IAM Administration

```python
import boto3

iam = boto3.client('iam')

# Create user
iam.create_user(UserName='new-user')

# Create access key
response = iam.create_access_key(UserName='new-user')
access_key = response['AccessKey']
print(f"Access Key ID: {access_key['AccessKeyId']}")
print(f"Secret Access Key: {access_key['SecretAccessKey']}")

# Attach managed policy
iam.attach_user_policy(
    UserName='new-user',
    PolicyArn='arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'
)

# Create inline policy
import json
policy_doc = {
    'Version': '2012-10-17',
    'Statement': [{
        'Effect': 'Allow',
        'Action': ['s3:GetObject', 's3:ListBucket'],
        'Resource': [
            'arn:aws:s3:::my-bucket',
            'arn:aws:s3:::my-bucket/*'
        ]
    }]
}

iam.put_user_policy(
    UserName='new-user',
    PolicyName='CustomS3Access',
    PolicyDocument=json.dumps(policy_doc)
)

# List users
for user in iam.list_users()['Users']:
    print(user['UserName'], user['CreateDate'])

# Create role
assume_role_policy = {
    'Version': '2012-10-17',
    'Statement': [{
        'Effect': 'Allow',
        'Principal': {'Service': 'ec2.amazonaws.com'},
        'Action': 'sts:AssumeRole'
    }]
}

iam.create_role(
    RoleName='my-ec2-role',
    AssumeRolePolicyDocument=json.dumps(assume_role_policy)
)

# Delete user (after removing all policies and keys)
iam.delete_access_key(UserName='new-user', AccessKeyId=access_key['AccessKeyId'])
iam.detach_user_policy(UserName='new-user', PolicyArn='arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess')
iam.delete_user_policy(UserName='new-user', PolicyName='CustomS3Access')
iam.delete_user(UserName='new-user')
```

## Secrets Manager

```python
import boto3
import json

sm = boto3.client('secretsmanager')

# Create secret
sm.create_secret(
    Name='my-app/database-credentials',
    SecretString=json.dumps({
        'username': 'admin',
        'password': 'super-secret-password',
        'host': 'db.example.com',
        'port': 5432
    })
)

# Get secret
response = sm.get_secret_value(SecretId='my-app/database-credentials')
secret = json.loads(response['SecretString'])
print(f"Database: {secret['host']}:{secret['port']}")

# Update secret
sm.put_secret_value(
    SecretId='my-app/database-credentials',
    SecretString=json.dumps({
        'username': 'admin',
        'password': 'new-rotated-password',
        'host': 'db.example.com',
        'port': 5432
    })
)

# List secrets
for secret in sm.list_secrets()['SecretList']:
    print(secret['Name'], secret.get('Description', ''))

# Delete secret (with recovery window)
sm.delete_secret(
    SecretId='my-app/database-credentials',
    ForceDeleteWithoutRecovery=False,
    RecoveryWindowInDays=30
)
```

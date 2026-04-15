---
name: boto3-1-42-89
description: Complete toolkit for AWS SDK for Python (Boto3) 1.42.89 providing high-level resource interface and low-level client access to 200+ AWS services with automatic pagination, retries, credential management, and session handling. Use when building Python applications that require AWS service integration including S3, EC2, Lambda, DynamoDB, SQS, SNS, IAM, and all other AWS services.
license: MIT
author: Generated from official documentation
version: "1.0.0"
tags:
  - aws
  - boto3
  - cloud
  - python
  - sdk
category: cloud-services
external_references:
  - https://github.com/boto/boto3/tree/1.42.89
  - https://boto3.amazonaws.com/v1/documentation/api/latest/
---

# Boto3 1.42.89 - AWS SDK for Python

## Overview

Boto3 is the Amazon Web Services (AWS) Software Development Kit (SDK) for Python, enabling developers to interact with 200+ AWS services through a Pythonic API. Version 1.42.89 provides both high-level resource interfaces (object-oriented) and low-level client interfaces (direct API access) with automatic handling of pagination, retries, credentials, and error management.

**Key Features:**
- **Resource Interface**: Object-oriented abstraction for common operations
- **Client Interface**: Low-level 1:1 mapping to AWS service APIs
- **Automatic Pagination**: Seamless iteration over large result sets
- **Built-in Retries**: Configurable retry modes (legacy, standard, adaptive)
- **Credential Management**: Support for IAM roles, environment variables, config files, SSO, and more
- **Session Management**: Isolated configurations for different AWS accounts/regions
- **200+ Services**: Comprehensive AWS service coverage

## When to Use

Use this skill when:
- Building Python applications that interact with AWS services
- Need to manage S3 buckets, EC2 instances, Lambda functions, DynamoDB tables, etc.
- Implementing cloud infrastructure automation and deployment scripts
- Creating data pipelines using AWS services (S3, Kinesis, Glue, Redshift)
- Building serverless applications with Lambda, API Gateway, DynamoDB
- Managing IAM users, roles, policies, and permissions
- Working with message queues (SQS) or pub/sub systems (SNS)
- Need thread-safe client access to AWS services
- Implementing retry logic for transient AWS service errors

## Core Concepts

### Clients vs Resources

Boto3 provides two interfaces for interacting with AWS services:

**Clients (Low-level)**: Direct mapping to AWS service APIs
- All service operations supported
- Methods match AWS API operation names (snake_case)
- Thread-safe, can be shared across threads
- Returns raw response dictionaries

**Resources (High-level)**: Object-oriented abstraction
- Higher-level, more Pythonic API
- Lazy-loaded attributes
- Not thread-safe, create per thread
- Limited to modeled operations (may not include newest features)

### Credential Resolution Order

Boto3 searches for credentials in this order (stops at first match):

1. Parameters passed to `boto3.client()` or `Session`
2. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
3. Assume role provider (configured in `~/.aws/config`)
4. Assume role with web identity provider
5. AWS IAM Identity Center (SSO) credentials
6. Shared credential file (`~/.aws/credentials`)
7. Login with console credentials (requires CRT)
8. AWS config file (`~/.aws/config`)
9. Boto2 config file (`~/.boto`)
10. Container credential provider (ECS/EKS)
11. Instance metadata service (EC2 IAM roles)

### Retry Modes

| Mode | Max Attempts | Features | Best For |
|------|-------------|----------|----------|
| **legacy** | 5 (default) | Basic exponential backoff, limited error types | Backward compatibility |
| **standard** | 3 | Circuit breaker, expanded error handling, 20s max backoff | Production use |
| **adaptive** | Configurable | All standard features + dynamic rate limiting | High-throughput applications |

## Installation / Setup

### Install Boto3

```bash
# Standard installation
pip install boto3

# With AWS Common Runtime for enhanced performance
pip install boto3[crt]

# Specific version
pip install boto3==1.42.89
```

### Configure Credentials

**Option 1: Using AWS CLI (recommended)**
```bash
aws configure
# Enter your access key, secret key, region, and output format
```

**Option 2: Manual configuration**

Create `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY

[production]
aws_access_key_id = PROD_ACCESS_KEY
aws_secret_access_key = PROD_SECRET_KEY
```

Create `~/.aws/config`:
```ini
[default]
region = us-east-1
output = json

[profile production]
region = us-west-2
```

**Option 3: Environment variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## Usage Examples

### Basic Client Usage

```python
import boto3

# Create a low-level client
s3_client = boto3.client('s3', region_name='us-east-1')

# List all buckets
response = s3_client.list_buckets()
for bucket in response['Buckets']:
    print(bucket['Name'])

# Create a bucket
s3_client.create_bucket(
    Bucket='my-unique-bucket-name',
    CreateBucketConfiguration={'LocationConstraint': 'us-east-1'}
)

# Upload a file
with open('local-file.txt', 'rb') as data:
    s3_client.put_object(
        Bucket='my-unique-bucket-name',
        Key='remote-file.txt',
        Body=data
    )

# Download a file
response = s3_client.get_object(
    Bucket='my-unique-bucket-name',
    Key='remote-file.txt'
)
with open('downloaded-file.txt', 'wb') as data:
    data.write(response['Body'].read())
```

### Basic Resource Usage

```python
import boto3

# Create a resource object
s3 = boto3.resource('s3', region_name='us-east-1')

# List all buckets
for bucket in s3.buckets.all():
    print(bucket.name)

# Get a specific bucket
bucket = s3.Bucket('my-unique-bucket-name')

# Upload a file
bucket.upload_file('local-file.txt', 'remote-file.txt')

# Download a file
bucket.download_file('remote-file.txt', 'downloaded-file.txt')

# List objects in bucket
for obj in bucket.objects.all():
    print(obj.key)

# Delete an object
obj = bucket.Object('remote-file.txt')
obj.delete()
```

### Using Sessions for Multiple Configurations

```python
import boto3

# Create sessions with different profiles
dev_session = boto3.Session(profile_name='development')
prod_session = boto3.Session(profile_name='production')

# Create clients from each session
dev_s3 = dev_session.client('s3')
prod_s3 = prod_session.client('s3')

# Or specify credentials directly
custom_session = boto3.Session(
    aws_access_key_id='ACCESS_KEY',
    aws_secret_access_key='SECRET_KEY',
    region_name='us-west-2'
)
s3_client = custom_session.client('s3')
```

### Error Handling

```python
import boto3
import botocore.exceptions

s3_client = boto3.client('s3')

try:
    s3_client.head_bucket(Bucket='non-existent-bucket')
    
except botocore.exceptions.ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == '404':
        print("Bucket does not exist")
    elif error_code == 'NoSuchBucket':
        print("The specified bucket does not exist")
    else:
        print(f"Error: {e.response['Error']['Message']}")
        
except botocore.exceptions.NoCredentialsError:
    print("Credentials not configured")
    
except botocore.exceptions.ParamValidationError as e:
    print(f"Invalid parameters: {e}")
```

### Using Waiters

```python
import boto3

ec2 = boto3.client('ec2')

# Launch an instance
response = ec2.run_instances(
    ImageId='ami-0c55b159cbfafe1f0',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro'
)

instance_id = response['Instances'][0]['InstanceId']

# Wait for instance to be running
waiter = ec2.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance_id])

print(f"Instance {instance_id} is now running")

# Wait for instance to be terminated
ec2.terminate_instances(InstanceIds=[instance_id])
waiter = ec2.get_waiter('instance_terminated')
waiter.wait(InstanceIds=[instance_id])
```

### Using Paginators

```python
import boto3

s3_client = boto3.client('s3')

# List all objects across all pages
paginator = s3_client.get_paginator('list_objects_v2')
page_iterator = paginator.paginate(Bucket='my-bucket')

for page in page_iterator:
    if 'Contents' in page:
        for obj in page['Contents']:
            print(obj['Key'])

# With JMESPath filtering
filtered = page_iterator.search("Contents[?Size > `1048576`].Key")
for key in filtered:
    print(f"Large file: {key}")
```

### Configuring Retries

```python
import boto3
from botocore.config import Config

# Configure retry behavior
config = Config(
    retries={
        'mode': 'standard',
        'total_max_attempts': 10
    }
)

s3_client = boto3.client('s3', config=config)

# Or use adaptive mode for high-throughput scenarios
adaptive_config = Config(
    retries={
        'mode': 'adaptive',
        'total_max_attempts': 20
    }
)
```

## Advanced Topics

See the following reference files for detailed coverage:

- [Configuration and Credentials](refs/01-configuration-credentials.md) - Complete guide to credential providers, config files, environment variables, IAM roles, SSO, and advanced configuration options
- [Clients and Resources](refs/02-clients-resources.md) - Deep dive into client vs resource interfaces, thread safety, metadata access, and when to use each approach
- [Error Handling](refs/03-error-handling.md) - Comprehensive error handling patterns, exception types, parsing error responses, and best practices for production code
- [Pagination and Collections](refs/04-pagination-collections.md) - Working with paginators, resource collections, filtering, JMESPath queries, and batch operations
- [Sessions and Threading](refs/05-sessions-threading.md) - Session management, multi-threaded applications, connection pooling, and concurrency patterns
- [AWS Service Examples](refs/06-service-examples.md) - Practical examples for S3, EC2, DynamoDB, SQS, Lambda, IAM, and other commonly used services

## Best Practices

1. **Use clients for new features**: Resources may not include the latest AWS API features; clients always have full coverage
2. **Implement proper error handling**: Always catch `botocore.exceptions.ClientError` and parse error codes
3. **Use waiters for state changes**: Don't poll manually; use built-in waiters for resource state transitions
4. **Configure retries appropriately**: Use 'standard' mode for production, 'adaptive' for high-throughput scenarios
5. **Manage credentials securely**: Never hardcode credentials; use IAM roles, environment variables, or AWS Secrets Manager
6. **Reuse clients when possible**: Clients are thread-safe and can be shared across threads (not processes)
7. **Use paginators for large datasets**: Don't manually handle pagination tokens; use the paginator abstraction
8. **Enable logging for debugging**: Set `BOTO_DEBUGGINGS=1` or configure Python logging to see retry attempts

## Troubleshooting

### Common Issues

**"Could not connect to the endpoint URL"**
- Verify region is correctly configured
- Check network connectivity and VPC settings
- Ensure service exists in the specified region

**"No credentials provided"**
- Run `aws configure` or set environment variables
- If on EC2, verify IAM role is attached with correct permissions
- Check credential file permissions (should be 600)

**"Access Denied" errors**
- Verify IAM policy has required permissions
- Check resource-based policies (S3 bucket policy, KMS key policy)
- Ensure no explicit deny policies are blocking access

**Throttling errors**
- Implement exponential backoff with jitter
- Use adaptive retry mode for automatic rate limiting
- Consider increasing service quotas if consistently throttled

### Debugging

```python
import boto3
import logging

# Enable Boto3 debug logging
boto3.set_stream_logger('', logging.DEBUG)

# Or use environment variable
# export AWS_SDK_UA_APP_ID=myapp
# export BOTOCORE_DEBUG=1
```

## References

- **Official Documentation**: https://boto3.amazonaws.com/v1/documentation/api/latest/
- **GitHub Repository**: https://github.com/boto/boto3/tree/1.42.89
- **AWS Service API References**: https://docs.aws.amazon.com/
- **Botocore Configuration**: https://docs.aws.amazon.com/botocore/latest/reference/config.html
- **AWS SDK Best Practices**: https://docs.aws.amazon.com/sdkref/latest/guide/feature-overview.html
- **Changelog**: https://github.com/boto/boto3/blob/develop/CHANGELOG.rst

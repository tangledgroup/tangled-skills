---
name: boto3-1-42-89
description: Complete toolkit for AWS SDK for Python (Boto3) 1.42.89 providing high-level resource interface and low-level client access to 200+ AWS services with automatic pagination, retries, credential management, and session handling. Use when building Python applications that require AWS service integration including S3, EC2, Lambda, DynamoDB, SQS, SNS, IAM, and all other AWS services.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.42.89"
tags:
  - aws
  - boto3
  - cloud
  - python
  - sdk
category: cloud-services
external_references:
  - https://github.com/boto/boto3/tree/1.42.89
  - https://docs.aws.amazon.com/
  - https://docs.aws.amazon.com/botocore/latest/reference/config.html
  - https://docs.aws.amazon.com/sdkref/latest/guide/feature-overview.html
  - https://github.com/boto/boto3/blob/develop/CHANGELOG.rst
  - https://boto3.amazonaws.com/v1/documentation/api/latest/
---

# Boto3 1.42.89 — AWS SDK for Python

## Overview

Boto3 is the Amazon Web Services (AWS) Software Development Kit (SDK) for Python, allowing Python developers to write software that makes use of AWS services like Amazon S3, Amazon EC2, AWS Lambda, DynamoDB, and over 200 other services. The name "Boto" refers to the freshwater dolphin native to the Amazon River.

The SDK is composed of two key packages:

- **Botocore** — the library providing low-level functionality shared between the Python SDK and AWS CLI
- **Boto3** — the package implementing the Python SDK itself, built on top of Botocore

Boto3 provides two interfaces to AWS services:

- **Low-level clients** — methods that map close to 1:1 with AWS API operations, returning raw response dictionaries
- **High-level resources** — object-oriented abstractions over clients, providing models, collections, and waiters with more Pythonic APIs

### Version Details

Version 1.42.89 requires Python 3.10 or later. It depends on:

- `botocore>=1.42.89,<1.43.0`
- `jmespath>=0.7.1,<2.0.0`
- `s3transfer>=0.16.0,<0.17.0`

Optional CRT dependency: `botocore[crt]>=1.21.0,<2.0a0` enables AWS Common Runtime features like Amazon EventBridge Global Endpoints, S3 Multi-Region Access Points, and SigV4a signing.

Python 3.8 support ended on 2025-04-22. Python 3.9 support ends on 2026-04-29.

## When to Use

Use this skill when building Python applications that integrate with AWS services:

- Cloud infrastructure management (EC2, VPC, Auto Scaling, ECS, EKS)
- Object storage operations (S3 uploads, downloads, presigned URLs, multipart transfers)
- Serverless application development (Lambda, API Gateway, DynamoDB, SQS, SNS)
- Data processing pipelines (Kinesis, Glue, EMR, Athena, Redshift)
- Identity and access management (IAM users, roles, policies, STS assume role)
- Monitoring and observability (CloudWatch metrics/logs/alarms, X-Ray)
- AI/ML workloads (Bedrock, SageMaker, Comprehend, Rekognition, Polly, Transcribe)
- Networking and CDN (Route 53, CloudFront, Global Accelerator, VPC endpoints)
- Database operations (RDS, DynamoDB, DocumentDB, Neptune, ElastiCache, Keyspaces)
- Security and compliance (KMS, GuardDuty, Config, Secrets Manager, Certificate Manager)
- Cost management and billing (Budgets, Cost Explorer, Billing Conductor)

## Core Concepts

### Clients vs Resources

**Clients** provide a low-level interface where methods map directly to AWS API operations. Parameters and responses are Python dictionaries that mirror the AWS API specification. Method names are snake-cased versions of the API operation names.

```python
import boto3

# Low-level client
ec2 = boto3.client('ec2', region_name='us-east-1')
response = ec2.describe_instances()
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        print(instance['InstanceId'])
```

**Resources** provide a higher-level, object-oriented interface. They model AWS entities as Python objects with attributes, methods, and sub-resources.

```python
import boto3

# High-level resource
s3 = boto3.resource('s3')
for bucket in s3.buckets.all():
    print(bucket.name)

# Access an existing bucket and list objects
bucket = s3.Bucket('my-bucket')
for obj in bucket.objects.all():
    print(obj.key, obj.size)
```

Resources automatically handle pagination through collections and provide waiters for common polling patterns.

### Sessions

Sessions encapsulate configuration including credentials, region, and service settings. They are the factory for creating clients and resources. All clients and resources created from a session share its configuration.

```python
import boto3

# Default session (uses default credential chain)
s3 = boto3.client('s3')

# Named session with explicit configuration
session = boto3.Session(
    profile_name='my-profile',
    region_name='eu-west-1'
)
ec2 = session.client('ec2')
dynamodb = session.resource('dynamodb')
```

### Collections

Collections provide an iterable interface to groups of resources. They support filtering, limiting, and batch actions without making API calls until iteration begins.

```python
# Filter EC2 instances by state
running = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
for instance in running:
    print(instance.id, instance.state['Name'])

# Batch terminate instances
instances_to_stop = [i for i in running if i.tags and any(t['Key'] == 'Environment' and t['Value'] == 'dev' for t in i.tags)]
ec2.instances.filter(InstanceIds=[i.id for i in instances_to_stop]).stop()
```

Collections are chainable and return copies, supporting lazy evaluation patterns.

### Paginators

Paginators automatically handle pagination across AWS API responses that return partial results. They abstract away `NextToken`, `Marker`, and other pagination parameters.

```python
# List all S3 objects (handles pagination automatically)
paginator = s3_client.get_paginator('list_objects_v2')
for page in paginator.paginate(Bucket='my-bucket'):
    for obj in page.get('Contents', []):
        print(obj['Key'])

# Pass pagination config to limit page size
for page in paginator.paginate(Bucket='my-bucket', PaginationConfig={'MaxItems': 100, 'PageSize': 10}):
    for obj in page.get('Contents', []):
        print(obj['Key'])
```

### Waiters

Waiters poll an AWS resource until it reaches a desired state or times out. They use exponential backoff internally.

```python
# Wait for EC2 instance to be running
instance = ec2.create_instances(ImageId='ami-12345', MinCount=1, MaxCount=1)[0]
instance.wait_until_running()

# Wait for S3 bucket to exist
s3_client = boto3.client('s3')
s3_client.create_bucket(Bucket='my-bucket')
s3_client.get_waiter('bucket_exists').wait(Bucket='my-bucket')
```

Available waiters can be listed via `client.waiter_names`.

## Advanced Topics

**Credentials and Authentication**: Credential chain, profiles, IAM roles, SSO, web identity, and environment variables → [Credentials and Authentication](reference/01-credentials-authentication.md)

**Configuration and Client Options**: Config objects, retry modes, proxies, timeouts, dual-stack, FIPS endpoints, and client context parameters → [Configuration and Client Options](reference/02-configuration-options.md)

**S3 Operations**: Managed transfers, multipart uploads, presigned URLs, transfer configuration, S3 control, and S3 Express → [S3 Operations](reference/03-s3-operations.md)

**Error Handling and Retries**: Botocore exceptions, service exceptions, retry modes (legacy/standard/adaptive), and error parsing → [Error Handling and Retries](reference/04-error-handling-retries.md)

**Common Service Patterns**: EC2 instance management, Lambda deployment, DynamoDB operations, SQS messaging, CloudWatch monitoring, and IAM administration → [Common Service Patterns](reference/05-common-service-patterns.md)

**Advanced Patterns**: Async clients, custom events, extensibility hooks, STS assume role, and cross-account access → [Advanced Patterns](reference/06-advanced-patterns.md)

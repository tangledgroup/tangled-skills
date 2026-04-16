# RustFS Advanced Features

This reference covers advanced features including versioning, replication, lifecycle management, event notifications, S3 Select, and more.

## Object Versioning

Versioning preserves all versions of objects in a bucket, enabling recovery from accidental deletions or overwrites.

### Enable Versioning

```bash
# Using AWS CLI
aws s3api put-bucket-versioning \
  --bucket my-bucket \
  --versioning-configuration Status=Enabled \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# Using mc
mc version enable myrustfs/my-bucket
```

### Suspend Versioning

```bash
# Suspend (keeps existing versions, prevents new ones)
aws s3api put-bucket-versioning \
  --bucket my-bucket \
  --versioning-configuration Status=Suspended \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin
```

### List Object Versions

```bash
# List all versions
aws s3api list-object-versions \
  --bucket my-bucket \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# Using mc
mc version ls myrustfs/my-bucket
```

### Get Specific Version

```bash
# Download specific version
aws s3api get-object \
  --bucket my-bucket \
  --key myfile.txt \
  --version-id v1234567890 \
  ./myfile-v1.txt \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# Using mc
mc cat myrustfs/my-bucket/myfile.txt --version-id v1234567890
```

### Delete Specific Version

```bash
# Delete specific version (not the object itself)
aws s3api delete-object \
  --bucket my-bucket \
  --key myfile.txt \
  --version-id v1234567890 \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# Using mc
mc version rm myrustfs/my-bucket/myfile.txt v1234567890
```

### Versioning with Delete Markers

When versioning is enabled, deleting an object creates a "delete marker":

```bash
# Delete object (creates delete marker)
aws s3api delete-object \
  --bucket my-bucket \
  --key myfile.txt \
  --endpoint-url http://localhost:9000

# Object appears deleted but versions still exist
aws s3api list-objects-v2 --bucket my-bucket --endpoint-url http://localhost:9000

# List shows delete marker as latest "version"
aws s3api list-object-versions --bucket my-bucket --endpoint-url http://localhost:9000

# Remove delete marker to restore object
aws s3api delete-object \
  --bucket my-bucket \
  --key myfile.txt \
  --version-id <delete-marker-version-id> \
  --endpoint-url http://localhost:9000
```

## Bucket Replication

Replicate objects across buckets in different locations or clusters.

**Note:** Bucket replication is available but should be tested thoroughly in alpha.93.

### Prerequisites

1. Enable versioning on both source and destination buckets
2. Configure replication IAM role with appropriate permissions
3. Ensure network connectivity between clusters (for cross-cluster replication)

### Configure Replication

```bash
# Create replication configuration
cat > replication-config.json <<EOF
{
  "Role": "arn:aws:iam:::role/rustfs-replication",
  "Rules": [
    {
      "ID": "ReplicateAllObjects",
      "Status": "Enabled",
      "Priority": 1,
      "Filter": {},
      "Destination": {
        "Bucket": "arn:aws:s3:::destination-bucket",
        "StorageClass": "STANDARD",
        "ReplicationTime": {
          "Status": "Enabled",
          "Time": {
            "Minutes": 15
          }
        },
        "Metric": {
          "Status": "Enabled"
        }
      },
      "SourceSelectionCriteria": {
        "SseKmsEncryptedObjects": {
          "Status": "Disabled"
        }
      }
    },
    {
      "ID": "ReplicateLogsOnly",
      "Status": "Enabled",
      "Priority": 2,
      "Filter": {
        "Prefix": "logs/"
      },
      "Destination": {
        "Bucket": "arn:aws:s3:::compliance-bucket",
        "StorageClass": "STANDARD"
      }
    }
  ]
}
EOF

# Apply replication configuration
aws s3api put-bucket-replication \
  --bucket source-bucket \
  --replication-configuration file://replication-config.json \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin
```

### Replication with Tags

```bash
# Replicate only tagged objects
cat > replication-tagged.json <<EOF
{
  "Role": "arn:aws:iam:::role/rustfs-replication",
  "Rules": [
    {
      "ID": "ReplicateImportant",
      "Status": "Enabled",
      "Priority": 1,
      "Filter": {
        "And": {
          "Prefix": "important/",
          "Tag": [
            {
              "Key": "replicate",
              "Value": "true"
            }
          ]
        }
      },
      "Destination": {
        "Bucket": "arn:aws:s3:::destination-bucket"
      }
    }
  ]
}
EOF

aws s3api put-bucket-replication \
  --bucket source-bucket \
  --replication-configuration file://replication-tagged.json \
  --endpoint-url http://localhost:9000
```

### Monitor Replication Status

```bash
# Check replication status of specific object
aws s3api list-object-versions \
  --bucket source-bucket \
  --prefix myfile.txt \
  --endpoint-url http://localhost:9000 \
  --query "Versions[*].{Key:Key,VersionId:VersionId,ReplicationStatus:ReplicationStatus}"

# Get replication metrics from CloudWatch (if integrated)
```

### Replication Configuration Management

```bash
# Get current replication configuration
aws s3api get-bucket-replication \
  --bucket source-bucket \
  --endpoint-url http://localhost:9000

# Delete replication configuration
aws s3api delete-bucket-replication \
  --bucket source-bucket \
  --endpoint-url http://localhost:9000
```

## Lifecycle Management

Automate object transitions and expirations based on rules.

**Note:** Lifecycle management is under testing in alpha.93. Test thoroughly before production use.

### Basic Lifecycle Rules

```bash
# Create lifecycle configuration
cat > lifecycle-config.json <<EOF
{
  "Rules": [
    {
      "ID": "ExpireOldLogs",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "logs/"
      },
      "Expiration": {
        "Days": 30
      }
    },
    {
      "ID": "TransitionToGlacier",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "archives/"
      },
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ]
    },
    {
      "ID": "ExpireTempFiles",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "temp/"
      },
      "Expiration": {
        "Days": 7
      }
    }
  ]
}
EOF

# Apply lifecycle configuration
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --lifecycle-configuration file://lifecycle-config.json \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin
```

### Lifecycle with Tags

```bash
# Lifecycle rules based on tags
cat > lifecycle-tagged.json <<EOF
{
  "Rules": [
    {
      "ID": "ExpireTemporary",
      "Status": "Enabled",
      "Filter": {
        "Tag": {
          "Key": "expiration",
          "Value": "30days"
        }
      },
      "Expiration": {
        "Days": 30
      }
    },
    {
      "ID": "TransitionImportant",
      "Status": "Enabled",
      "Filter": {
        "Tag": {
          "Key": "importance",
          "Value": "high"
        }
      },
      "Transitions": [
        {
          "Days": 180,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --lifecycle-configuration file://lifecycle-tagged.json \
  --endpoint-url http://localhost:9000
```

### Versioned Object Lifecycle

```bash
# Manage versioned objects
cat > lifecycle-versioned.json <<EOF
{
  "Rules": [
    {
      "ID": "ExpireOldVersions",
      "Status": "Enabled",
      "Filter": {
        "Prefix": ""
      },
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 365
      },
      "ExpiresAfter": {
        "Days": 730
      }
    },
    {
      "ID": "TransitionOldVersions",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "data/"
      },
      "NoncurrentVersionTransitions": [
        {
          "NoncurrentDays": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "NoncurrentDays": 90,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket versioned-bucket \
  --lifecycle-configuration file://lifecycle-versioned.json \
  --endpoint-url http://localhost:9000
```

### Abort Incomplete Multipart Uploads

```bash
# Clean up incomplete uploads
cat > lifecycle-multipart.json <<EOF
{
  "Rules": [
    {
      "ID": "AbortIncompleteUploads",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "uploads/"
      },
      "AbortIncompleteMultipartUpload": {
        "DaysAfterInitiation": 7
      }
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --lifecycle-configuration file://lifecycle-multipart.json \
  --endpoint-url http://localhost:9000
```

### Lifecycle Management Operations

```bash
# Get lifecycle configuration
aws s3api get-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --endpoint-url http://localhost:9000

# Delete lifecycle configuration
aws s3api delete-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --endpoint-url http://localhost:9000
```

## Event Notifications

Trigger actions when objects are created, deleted, or restored.

### SNS Topic Configuration

```bash
# Create notification configuration with SNS
cat > notification-sns.json <<EOF
{
  "NotificationConfiguration": {
    "TopicConfigurations": [
      {
        "Id": "ObjectCreatedNotifications",
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:object-created",
        "Events": [
          "s3:ObjectCreated:*"
        ],
        "Filter": {
          "S3Key": {
            "FilterRules": [
              {
                "Name": "prefix",
                "Value": "uploads/"
              },
              {
                "Name": "suffix",
                "Value": ".jpg"
              }
            ]
          }
        }
      },
      {
        "Id": "ObjectRemovedNotifications",
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:object-removed",
        "Events": [
          "s3:ObjectRemoved:*"
        ]
      }
    ]
  }
}
EOF

# Apply notification configuration
aws s3api put-bucket-notification-configuration \
  --bucket my-bucket \
  --notification-configuration file://notification-sns.json \
  --endpoint-url http://localhost:9000
```

### SQS Queue Configuration

```bash
# Create notification configuration with SQS
cat > notification-sqs.json <<EOF
{
  "NotificationConfiguration": {
    "QueueConfigurations": [
      {
        "Id": "UploadNotifications",
        "QueueArn": "arn:aws:sqs:us-east-1:123456789012:upload-queue",
        "Events": [
          "s3:ObjectCreated:Put",
          "s3:ObjectCreated:Post"
        ],
        "Filter": {
          "S3Key": {
            "FilterRules": [
              {
                "Name": "prefix",
                "Value": "data/"
              }
            ]
          }
        }
      },
      {
        "Id": "DeleteNotifications",
        "QueueArn": "arn:aws:sqs:us-east-1:123456789012:delete-queue",
        "Events": [
          "s3:ObjectRemoved:Delete"
        ]
      }
    ]
  }
}
EOF

aws s3api put-bucket-notification-configuration \
  --bucket my-bucket \
  --notification-configuration file://notification-sqs.json \
  --endpoint-url http://localhost:9000
```

### Lambda Function Configuration

```bash
# Create notification configuration with Lambda
cat > notification-lambda.json <<EOF
{
  "NotificationConfiguration": {
    "LambdaFunctionConfigurations": [
      {
        "Id": "ImageProcessing",
        "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:process-image",
        "Events": [
          "s3:ObjectCreated:*"
        ],
        "Filter": {
          "S3Key": {
            "FilterRules": [
              {
                "Name": "suffix",
                "Value": ".png"
              }
            ]
          }
        }
      }
    ]
  }
}
EOF

aws s3api put-bucket-notification-configuration \
  --bucket images-bucket \
  --notification-configuration file://notification-lambda.json \
  --endpoint-url http://localhost:9000
```

### Notification Management

```bash
# Get notification configuration
aws s3api get-bucket-notification-configuration \
  --bucket my-bucket \
  --endpoint-url http://localhost:9000

# Delete notification configuration
aws s3api delete-bucket-notification-configuration \
  --bucket my-bucket \
  --endpoint-url http://localhost:9000
```

## S3 Select

Query objects directly in S3 using SQL-like syntax.

### Query CSV Objects

```bash
# Create expression for CSV query
cat > select-csv.json <<EOF
{
  "Expression": "SELECT * FROM S3Object s WHERE s.year = '2024'",
  "ExpressionType": "SQL",
  "InputSerialization": {
    "CSV": {
      "FileHeaderInfo": "USE",
      "RecordDelimiter": "\n",
      "FieldDelimiter": ","
    }
  },
  "OutputSerialization": {
    "CSV": {
      "RecordDelimiter": "\n",
      "FieldDelimiter": ","
    }
  }
}
EOF

# Execute query
aws s3api select-object-content \
  --bucket data-bucket \
  --key sales.csv \
  --expression-type SQL \
  --expression "SELECT year, SUM(amount) FROM S3Object s GROUP BY year" \
  --input-serialization '{ "CSV": { "FileHeaderInfo": "USE" } }' \
  --output-serialization '{ "CSV": {} }' \
  --endpoint-url http://localhost:9000 \
  --query 'Payload.Records[].Payload' \
  --output text
```

### Query JSON Objects

```bash
# Query JSON array
aws s3api select-object-content \
  --bucket data-bucket \
  --key users.json \
  --expression-type SQL \
  --expression "SELECT name, email FROM S3Object s WHERE s.age > 18" \
  --input-serialization '{ "JSON": {} }' \
  --output-serialization '{ "JSON": { "RecordDelimiter": "\n" } }' \
  --endpoint-url http://localhost:9000
```

### Query with Compression

```bash
# Query compressed CSV (GZIP)
aws s3api select-object-content \
  --bucket data-bucket \
  --key logs.csv.gz \
  --expression-type SQL \
  --expression "SELECT * FROM S3Object s LIMIT 100" \
  --input-serialization '{
    "CSV": { "FileHeaderInfo": "USE" },
    "CompressionType": "GZIP"
  }' \
  --output-serialization '{ "CSV": {} }' \
  --endpoint-url http://localhost:9000

# Query compressed JSON (BZIP2)
aws s3api select-object-content \
  --bucket data-bucket \
  --key events.json.bz2 \
  --expression-type SQL \
  --expression "SELECT event_type, COUNT(*) FROM S3Object s GROUP BY event_type" \
  --input-serialization '{
    "JSON": {},
    "CompressionType": "BZIP2"
  }' \
  --output-serialization '{ "JSON": {} }' \
  --endpoint-url http://localhost:9000
```

## Object Tagging

Organize and manage objects with metadata tags.

### Tag Objects

```bash
# Tag single object
aws s3api put-object-tagging \
  --bucket my-bucket \
  --key important-file.txt \
  --tagging 'TagSet=[{Key=project,Value=alpha},{Key=priority,Value=high},{Key=owner,Value=team-a}]' \
  --endpoint-url http://localhost:9000

# Using mc
mc tag add myrustfs/my-bucket/important-file.txt project=alpha,priority=high,owner=team-a
```

### Get Tags

```bash
# Get object tags
aws s3api get-object-tagging \
  --bucket my-bucket \
  --key important-file.txt \
  --endpoint-url http://localhost:9000

# Using mc
mc tag ls myrustfs/my-bucket/important-file.txt
```

### Delete Tags

```bash
# Remove all tags
aws s3api delete-object-tagging \
  --bucket my-bucket \
  --key important-file.txt \
  --endpoint-url http://localhost:9000

# Using mc
mc tag rm myrustfs/my-bucket/important-file.txt --all
```

### Tag Buckets

```bash
# Tag bucket
aws s3api put-bucket-tagging \
  --bucket my-bucket \
  --tagging 'TagSet=[{Key=environment,Value=production},{Key=cost-center,Value=engineering}]' \
  --endpoint-url http://localhost:9000

# Get bucket tags
aws s3api get-bucket-tagging \
  --bucket my-bucket \
  --endpoint-url http://localhost:9000
```

### List Objects by Tag

```bash
# List objects with specific tag
aws s3api list-object-v2 \
  --bucket my-bucket \
  --endpoint-url http://localhost:9000 \
  --query "Contents[].{Key:Key,Tags:Tags}"

# Note: Filter by tag requires client-side filtering or S3 Select
```

## Multipart Uploads

Handle large file uploads efficiently.

### Programmatic Multipart Upload

```bash
# 1. Initiate multipart upload
aws s3api create-multipart-upload \
  --bucket my-bucket \
  --key large-file.tar.gz \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# Response includes UploadId, e.g., "abc123-def456"

# 2. Upload parts (example with 3 parts)
aws s3api upload-part \
  --bucket my-bucket \
  --key large-file.tar.gz \
  --part-number 1 \
  --upload-id abc123-def456 \
  --body part1.data \
  --endpoint-url http://localhost:9000

aws s3api upload-part \
  --bucket my-bucket \
  --key large-file.tar.gz \
  --part-number 2 \
  --upload-id abc123-def456 \
  --body part2.data \
  --endpoint-url http://localhost:9000

aws s3api upload-part \
  --bucket my-bucket \
  --key large-file.tar.gz \
  --part-number 3 \
  --upload-id abc123-def456 \
  --body part3.data \
  --endpoint-url http://localhost:9000

# 3. Complete multipart upload
aws s3api complete-multipart-upload \
  --bucket my-bucket \
  --key large-file.tar.gz \
  --upload-id abc123-def456 \
  --multipart-upload 'Parts=[
    {ETag="etag1", PartNumber=1},
    {ETag="etag2", PartNumber=2},
    {ETag="etag3", PartNumber=3}
  ]' \
  --endpoint-url http://localhost:9000
```

### Using mc for Multipart Upload

```bash
# mc handles multipart automatically for large files
mc cp large-file.tar.gz myrustfs/my-bucket/

# Check upload progress
mc cp --progress large-file.tar.gz myrustfs/my-bucket/
```

### Abort Incomplete Upload

```bash
# List incomplete uploads
aws s3api list-multipart-uploads \
  --bucket my-bucket \
  --endpoint-url http://localhost:9000

# Abort specific upload
aws s3api abort-multipart-upload \
  --bucket my-bucket \
  --key large-file.tar.gz \
  --upload-id abc123-def456 \
  --endpoint-url http://localhost:9000
```

## Bucket Policies

Fine-grained access control using JSON policies.

### Public Read Policy

```bash
# Allow public read access
cat > public-read.json <<EOF
{
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
EOF

aws s3api put-bucket-policy \
  --bucket my-bucket \
  --policy file://public-read.json \
  --endpoint-url http://localhost:9000
```

### Cross-Account Access

```bash
# Allow specific AWS account to access bucket
cat > cross-account.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CrossAccountAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111122223333:root"
      },
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": ["arn:aws:s3:::shared-bucket/*"]
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket shared-bucket \
  --policy file://cross-account.json \
  --endpoint-url http://localhost:9000
```

### IP-Based Restriction

```bash
# Restrict access to specific IP ranges
cat > ip-restriction.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "IPRestriction",
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:*"],
      "Resource": ["arn:aws:s3:::my-bucket/*"],
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": ["203.0.113.0/24", "198.51.100.0/24"]
        }
      }
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket my-bucket \
  --policy file://ip-restriction.json \
  --endpoint-url http://localhost:9000
```

### TLS-Only Access

```bash
# Require HTTPS/TLS for all requests
cat > tls-required.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TLSEnforcement",
      "Effect": "Deny",
      "Principal": "*",
      "Action": ["s3:*"],
      "Resource": ["arn:aws:s3:::my-bucket/*"],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket my-bucket \
  --policy file://tls-required.json \
  --endpoint-url http://localhost:9000
```

### Policy Management

```bash
# Get bucket policy
aws s3api get-bucket-policy \
  --bucket my-bucket \
  --endpoint-url http://localhost:9000

# Delete bucket policy
aws s3api delete-bucket-policy \
  --bucket my-bucket \
  --endpoint-url http://localhost:9000

# Validate policy (using AWS CLI)
aws s3api get-bucket-policy --bucket my-bucket | aws s3api validate-policy --policy document
```

## Encryption

### Server-Side Encryption (SSE-S3)

```bash
# Upload with default encryption
aws s3api put-object \
  --bucket encrypted-bucket \
  --key secret.txt \
  --body secret.txt \
  --server-side-encryption AES256 \
  --endpoint-url http://localhost:9000

# Set bucket default encryption
cat > encryption-config.json <<EOF
{
  "Rules": [
    {
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }
  ]
}
EOF

aws s3api put-bucket-encryption \
  --bucket encrypted-bucket \
  --server-side-encryption-configuration file://encryption-config.json \
  --endpoint-url http://localhost:9000
```

### Server-Side Encryption with KMS (SSE-KMS)

**Note:** KMS is under testing in alpha.93.

```bash
# Upload with KMS encryption
aws s3api put-object \
  --bucket encrypted-bucket \
  --key secret.txt \
  --body secret.txt \
  --server-side-encryption aws:kms \
  --server-side-encryption-aws-kms-key-id alias/my-key \
  --endpoint-url http://localhost:9000

# Set KMS encryption default
cat > kms-encryption.json <<EOF
{
  "Rules": [
    {
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "alias/my-key"
      }
    }
  ]
}
EOF

aws s3api put-bucket-encryption \
  --bucket encrypted-bucket \
  --server-side-encryption-configuration file://kms-encryption.json \
  --endpoint-url http://localhost:9000
```

### Client-Side Encryption

Client-side encryption should be implemented in your application code before uploading to RustFS.

## Additional Features

### Bitrot Protection

RustFS includes automatic bitrot protection with hash verification:

- Enabled by default on all reads
- Background scanner verifies data integrity periodically
- Automatic healing of corrupted shards

```bash
# Bitrot is always enabled, but you can skip verification for performance
export RUSTFS_OBJECT_GET_SKIP_BITROT_VERIFY=true  # Not recommended in production
```

### Healing and Scrubbing

```bash
# Trigger heal via mc
mc admin heal myrustfs --recursive --dry-run  # Preview what would be healed
mc admin heal myrustfs --recursive            # Actually heal

# Via API (admin endpoint)
curl -X POST "http://localhost:9000/minio/admin/v3/heal" \
  -d '{"mode":"full","recursive":true}' \
  -H "Authorization: AWS rustfsadmin:rustfsadmin"
```

See [`06-troubleshooting.md`](06-troubleshooting.md) for detailed healing procedures.

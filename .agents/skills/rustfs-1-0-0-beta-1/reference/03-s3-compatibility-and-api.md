# S3 Compatibility and API

## Full S3 API Support

RustFS implements the complete AWS S3 API, including:

- **PutObject / GetObject / DeleteObject**: Basic CRUD operations
- **ListObjectsV2**: Object listing with pagination
- **MultipartUpload**: Large file uploads split into parts
- **CopyObject**: Server-side object copying
- **SelectObjectContent (S3 Select)**: SQL queries on objects in-place
- **Presigned URLs**: Time-limited access links for GET/PUT operations
- **Bucket Policies**: S3-style IAM policies with prefix-level scoping
- **Versioning**: Object versioning per bucket
- **Lifecycle Rules**: Automated transitions and expirations

## Policy Improvements (beta.1)

The beta.1 release includes significant policy and IAM improvements:

- Bucket-scoped `ListBucket` policies now correctly honor `s3:prefix` conditions
- Gateway `ListBucket` resources are preserved in policy evaluation
- `AssumeRole` actions are allowed in system policies
- IAM not-found errors correctly map to HTTP 404 responses
- Portable IAM storage and derived authentication are preserved across operations

### Policy Example (Prefix-Scoped ListBucket)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::my-bucket"],
      "Condition": {
        "StringLike": {
          "s3:prefix": ["data/*"]
        }
      }
    }
  ]
}
```

## SDK Support

RustFS works with any S3-compatible SDK:

- **Python**: Boto3 (recommended), `boto3.client('s3', endpoint_url='http://...')`
- **JavaScript/TypeScript**: AWS SDK v3 (`@aws-sdk/client-s3`)
- **Java**: AWS SDK for Java v2
- **Rust**: `aws-sdk-s3` crate
- **Go**: `github.com/aws/aws-sdk-go-v2/service/s3`
- **MinIO Client (mc)**: Full S3-compatible CLI tool

## Versioning States

Per-bucket versioning supports three states:
- **Enabled**: All versions retained, soft deletes only
- **Suspended**: New objects overwrite existing keys
- **Default (disabled)**: No version tracking

Switch from suspended to enabled is supported. Switching from enabled to suspended is not reversible for existing objects.

## Usage Limits

- Maximum object size: 5 TiB (via multipart upload)
- Maximum part size: 5 GiB per part
- Minimum part size: 5 MiB (except the last part)
- Maximum parts per upload: 10,000
- Bucket name: 3-63 characters, lowercase letters, numbers, hyphens, dots

## WebDAV (beta.1)

The beta.1 release fixes URL-encoded filename decoding in WebDAV path parsing, ensuring files with special characters (spaces, percent signs, unicode) are correctly handled when accessed via WebDAV protocol.

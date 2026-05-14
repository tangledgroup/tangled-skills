# S3 Compatibility and API

## Full S3 Protocol Support

RustFS strictly adheres to AWS S3 API standards, supporting both Signature V2 and V4 authentication. It enables seamless integration across public cloud, private cloud, data center, multi-cloud, hybrid cloud, and edge environments.

Supported S3 features:
- Core CRUD operations (PUT, GET, DELETE, LIST)
- Multipart upload for large objects
- Pre-signed URLs
- S3 Select for querying CSV, Parquet, JSON
- Bucket and object versioning
- Object tagging
- CORS configuration

## SDK Support

RustFS works with any S3-compatible SDK. Officially tested with:

- **Rust**: AWS SDK for Rust
- **Python**: boto3
- **Java**: AWS SDK for Java
- **JavaScript/TypeScript**: aws-sdk-js-v3
- **Go**: aws-sdk-go-v2
- **MinIO Client (mc)**: CLI tool for S3 operations

### MinIO Client Examples

```bash
# Configure alias
mc alias set myrustfs http://localhost:9000 rustfsadmin rustfsadmin

# Create bucket
mc mb myrustfs/my-bucket

# Upload file
mc cp local-file.txt myrustfs/my-bucket/

# Download file
mc cp myrustfs/my-bucket/file.txt .

# List objects
mc ls myrustfs/my-bucket/

# Versioning
mc version enable myrustfs/my-bucket
```

### Rust SDK Example

Initialize client using AWS SDK for Rust:

```rust
use aws_config::{BehaviorVersion, DefaultsMode};
use aws_credential_types::Credentials;
use aws_sdk_s3::{Client, config::Region};

let credentials = Credentials::new(
    "access-key-id",
    "secret-access-key",
    None, None, "rustfs",
);

let config = aws_config::defaults(BehaviorVersion::latest())
    .region(Region::new("us-east-1"))
    .credentials_provider(credentials)
    .endpoint_url("http://localhost:9000")
    .load()
    .await;

let client = Client::new(&config);
```

Create bucket:
```rust
client.create_bucket().bucket("my-bucket").send().await?;
```

List buckets:
```rust
let res = client.list_buckets().send().await?;
for bucket in res.buckets() {
    println!("Bucket: {}", bucket.name());
}
```

List objects:
```rust
let res = client.list_objects_v2().bucket("my-bucket").send().await?;
for obj in res.contents() {
    println!("Object: {}", obj.key());
}
```

## Versioning

RustFS implements S3-compatible versioning with three bucket states:

1. **Unversioned** (default) — No versioning performed
2. **Enabled** — Full versioning, unique ID per object version
3. **Suspended** — Stops accumulating new versions, retains existing

Versioning cannot be disabled once enabled, only suspended. Requires erasure coding and at least 4 disks.

Features:
- Unique version ID per object
- Point-in-time recovery
- Delete markers prevent accidental deletion
- `mc undo` to rollback PUT/DELETE operations
- `mc rewind` to view buckets at any point in time
- Foundation for object locking and lifecycle management

## Usage Limits

### S3 API Limits

- Maximum object size: 5 TiB
- Minimum object size: 0 B
- Single PUT (non-multipart): max 500 GiB
- Multipart upload: max 5 TiB
- Maximum parts per upload: 10,000
- Part size range: 5 MiB–5 GiB (last part can be 0 B)
- Max objects returned per LIST: 1,000
- Bucket name max length: 63 characters
- Object name max length: 1,024 characters
- Object path segment max length: 255 characters
- Max versions per object: 10,000 (configurable)

### Erasure Coding Limits

- Maximum servers per cluster: no hard limit
- Minimum servers: 1
- Minimum drives for single server: 1 (no redundancy in SNSD)
- Minimum drives for 2+ servers: 1 per server
- Maximum drives per server: no hard limit
- Read quorum: N/2
- Write quorum: (N/2) + 1

### Object Naming Limits

Object names are limited by the underlying OS and filesystem. Windows restricts characters like `^`, `*`, `|`, `\`, `/`, `&`, `"`, `;`.

Namespace conflicts to avoid:
```bash
PUT data/hello/2025/first/a.csv
PUT data/hello/2025/first    # Conflicts with prefix

PUT data/hello/2025/first/
PUT data/hello/2025/first/vendors.csv    # Conflicts with existing object
```

LIST operations at conflicting paths return empty result sets.

## OpenStack Swift API

RustFS provides native OpenStack Swift protocol support with Keystone authentication via `X-Auth-Token` headers. This enables integration with OpenStack ecosystems alongside S3 compatibility.

Swift metadata operations are partially supported (under development).

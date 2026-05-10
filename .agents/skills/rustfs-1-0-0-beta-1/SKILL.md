---
name: rustfs-1-0-0-beta-1
description: High-performance distributed object storage system with S3-compatible API, OpenStack Swift support, and comprehensive observability features built in Rust. Use when deploying S3-compatible storage backends, configuring distributed clusters, integrating with Kubernetes via Helm, setting up TLS/mTLS, or building data lake solutions requiring high-throughput storage.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - object-storage
  - s3
  - swift
  - distributed-systems
  - observability
  - data-lake
  - rust
category: storage
external_references:
  - https://rustfs.com/
  - https://github.com/rustfs/rustfs
---

# RustFS 1.0.0-beta.1

## Overview

RustFS is a high-performance, distributed object storage system built in Rust. It combines the simplicity of MinIO with the memory safety and raw performance of Rust, delivering full S3 compatibility under the permissive Apache 2.0 license. Unlike competitors using AGPL licensing, RustFS avoids legal restrictions while providing enterprise-grade features for data lakes, AI/ML workloads, and big data pipelines.

Key characteristics:
- **Rust-based**: Memory safety by design with C/C++ level performance
- **S3 Compatible**: Full AWS S3 API support including S3 Select
- **OpenStack Swift**: Native Swift protocol with Keystone authentication
- **Distributed Architecture**: Decentralized peer-to-peer design, no single point of failure
- **Apache 2.0 License**: Permissive licensing for unrestricted commercial use
- **No Telemetry**: Full data sovereignty, GDPR/CCPA/APPI compliant
- **Observability**: Built-in OpenTelemetry integration with Prometheus, Grafana, Jaeger, Tempo
- **Beta Release**: v1.0.0-beta.1 marks transition from alpha with improved metrics, replication fixes, IAM hardening, and console-managed module switches

## When to Use

- Deploying S3-compatible object storage on-premises or in private cloud
- Replacing MinIO with a permissively licensed alternative (drop-in binary replacement)
- Building data lake infrastructure for Spark, Presto/Trino, Iceberg, Hudi, Delta Lake
- Storing AI/ML training datasets and model artifacts at scale
- Implementing cold archiving or long-term data retention with WORM support
- Setting up cross-region active-active replication for disaster recovery
- Integrating object storage with OpenStack via Swift API and Keystone
- Deploying lightweight edge storage (binary under 100 MB)
- Replacing HDFS with a cloud-native, multi-protocol alternative
- Configuring observability pipelines with Prometheus metrics and distributed tracing

## Core Concepts

**Object**: The fundamental unit of storage — files, byte streams, or any unstructured data. Maximum size is 5 TiB via multipart upload.

**Bucket**: A logical container for objects. Data is isolated between buckets. Similar to a top-level directory from the client perspective.

**Drive**: The physical disk storing data, passed as a parameter at startup. All object data resides on these drives. JBOD mode is recommended (no hardware RAID).

**Set (Erasure Set / Stripe)**: A group of drives distributed across different nodes. An object is stored within a single set. The cluster automatically divides into sets based on scale. One object = one set. One cluster = multiple sets.

**Erasure Coding**: Reed-Solomon based data protection. Data split into `k` data shards and `m` parity shards (total `n=k+m`). Default is 12+4 configuration, tolerating up to 4 disk failures. Far more storage-efficient than triple replication.

**Self-Healing**: Automatic data repair through read-time verification, background scanning, and manual triggers. Detects and repairs bit rot, shard corruption, and disk failures transparently.

## Installation / Setup

### One-Click Installation (Linux)

```bash
curl -O https://rustfs.com/install_rustfs.sh && bash install_rustfs.sh
```

Default port is `9000` (S3 API) and `9001` (Console). Default data path: `/data/rustfs0`.

### Docker Quick Start

The container runs as non-root user `rustfs` (UID `10001`). Set host directory ownership accordingly:

```bash
mkdir -p data logs
chown -R 10001:10001 data logs

docker run -d \
  -p 9000:9000 -p 9001:9001 \
  -v $(pwd)/data:/data \
  -v $(pwd)/logs:/logs \
  rustfs/rustfs:v1.0.0-beta.1
```

With Podman, replace `docker` with `podman`. For full observability stack (Grafana, Prometheus, Jaeger, Tempo):

```bash
docker compose --profile observability up -d
```

### Kubernetes / Helm

Follow the [Helm Chart README](https://charts.rustfs.com/) for cloud-native deployment on Kubernetes. The beta.1 release fixes Helm rollingUpdate rendering (only rendered when strategy type is RollingUpdate).

### Nix Flake

```bash
nix run github:rustfs/rustfs
nix build github:rustfs/rustfs
./result/bin/rustfs --help
```

### Build from Source

```bash
./docker-buildx.sh --build-arg RELEASE=latest
./docker-buildx.sh --push
make docker-buildx                    # Build locally
make docker-buildx-push               # Build and push
```

Multi-architecture builds: `linux/amd64`, `linux/arm64`.

### Key Environment Variables

- `RUSTFS_VOLUMES=/data/rustfs{0..3}` — Define storage volumes
- `RUSTFS_ADDRESS=0.0.0.0:9000` — S3 API bind address
- `RUSTFS_CONSOLE_ADDRESS=0.0.0.0:9001` — Console bind address
- `RUSTFS_ACCESS_KEY=rustfsadmin` — Default access key
- `RUSTFS_SECRET_KEY=rustfsadmin` — Default secret key
- `RUSTFS_TLS_PATH=/opt/tls` — TLS certificate directory

### Accessing RustFS

Console: `http://localhost:9001`, default credentials `rustfsadmin` / `rustfsadmin`. For HTTPS access, configure TLS via `RUSTFS_TLS_PATH`.

## Usage Examples

### Create a Bucket (S3 API)

```bash
mc alias set myrustfs http://localhost:9000 rustfsadmin rustfsadmin
mc mb myrustfs/my-bucket
```

### Upload and Download Objects

```bash
mc cp local-file.txt myrustfs/my-bucket/
mc cp myrustfs/my-bucket/local-file.txt .
```

### Python SDK (Boto3)

```python
import boto3
from botocore.client import Config

s3 = boto3.client(
    's3',
    endpoint_url='http://192.168.1.100:9000',
    aws_access_key_id='rustfsadmin',
    aws_secret_access_key='rustfssecret',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# Create bucket
s3.create_bucket(Bucket='my-bucket')

# Upload file
s3.upload_file('hello.txt', 'my-bucket', 'hello.txt')

# List objects
response = s3.list_objects_v2(Bucket='my-bucket')
for obj in response.get('Contents', []):
    print(f"- {obj['Key']} ({obj['Size']} bytes)")

# Generate presigned URL (10 min expiry)
url = s3.generate_presigned_url(
    ClientMethod='get_object',
    Params={'Bucket': 'my-bucket', 'Key': 'hello.txt'},
    ExpiresIn=600
)
```

### OIDC Authentication (Microsoft Entra ID)

```bash
RUSTFS_IDENTITY_OPENID_ENABLE=on
RUSTFS_IDENTITY_OPENID_CONFIG_URL="https://login.microsoftonline.com/<tenant-id>/v2.0/.well-known/openid-configuration"
RUSTFS_IDENTITY_OPENID_CLIENT_ID="<client-id>"
RUSTFS_IDENTITY_OPENID_CLIENT_SECRET="<client-secret>"
RUSTFS_IDENTITY_OPENID_SCOPES="openid,profile,email"
RUSTFS_IDENTITY_OPENID_GROUPS_CLAIM="groups"
RUSTFS_IDENTITY_OPENID_ROLES_CLAIM="roles"
```

The `roles_claim` setting is optional. When unset, only the `groups` claim contributes to authorization. For Microsoft Entra ID app roles, set `roles_claim=roles` so both console admin checks and bucket IAM policies can evaluate those roles.

## Advanced Topics

**Architecture and Design**: Decentralized P2P design, consistency model, erasure coding principles → [Architecture and Design](reference/01-architecture-and-design.md)

**Deployment Modes**: SNSD, SNMD, MNMD configurations, hardware checklists, filesystem requirements → [Deployment Modes](reference/02-deployment-modes.md)

**S3 Compatibility and API**: Full S3 API support, SDKs, versioning states, usage limits → [S3 Compatibility and API](reference/03-s3-compatibility-and-api.md)

**Security and Encryption**: TLS configuration, server-side encryption (SSE-S3, SSE-C), KMS integration, IAM policies, WORM object locking → [Security and Encryption](reference/04-security-and-encryption.md)

**Data Protection and Replication**: Erasure coding details, self-healing processes, cross-region replication, lifecycle management → [Data Protection and Replication](reference/05-data-protection-and-replication.md)

**Solutions and Integrations**: Data lake architecture, AI/ML storage, HDFS replacement, SQL Server integration, cold archiving, observability stack → [Solutions and Integrations](reference/06-solutions-and-integrations.md)

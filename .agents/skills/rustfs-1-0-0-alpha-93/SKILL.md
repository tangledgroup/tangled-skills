---
name: rustfs-1-0-0-alpha-93
description: High-performance distributed object storage system with S3-compatible API, OpenStack Swift support, and comprehensive observability features built in Rust. Use when deploying S3-compatible storage backends, configuring distributed clusters, integrating with Kubernetes via Helm, setting up TLS/mTLS, implementing Swift/Keystone authentication, or building data lake solutions requiring high-throughput storage.
license: Apache-2.0
author: Generated from rustfs/rustfs v1.0.0-alpha.93
version: "1.0.0-alpha.93"
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

# RustFS 1.0.0-alpha.93

## Overview

RustFS is a high-performance, distributed object storage system built in Rust that provides S3-compatible API, OpenStack Swift support, and comprehensive observability features. It combines the simplicity of MinIO with memory safety and raw performance of Rust, offering full S3 compatibility under the permissive Apache 2.0 license.

Key capabilities include:
- **S3 Compatibility**: Full S3 API support for seamless integration with existing applications
- **OpenStack Swift**: Native Swift protocol support with Keystone authentication
- **Distributed Architecture**: Scalable, fault-tolerant design with erasure coding
- **Data Lake Optimized**: High-throughput performance for AI/ML and big data workloads
- **Observability**: Built-in OpenTelemetry support with Prometheus, Grafana, Tempo, and Jaeger
- **Multi-Tenancy**: Complete IAM system with policies, users, groups, and OIDC integration
- **Console UI**: Web-based management interface for buckets, objects, users, and monitoring

## When to Use

Use this skill when:
- Deploying RustFS as an S3-compatible object storage backend
- Configuring distributed or single-node RustFS clusters
- Integrating RustFS with Kubernetes via Helm charts
- Setting up TLS/mTLS for secure communications
- Implementing OpenStack Swift/Keystone authentication
- Configuring observability (OpenTelemetry, Prometheus, Grafana)
- Managing buckets, objects, versioning, and lifecycle policies
- Troubleshooting performance or connectivity issues
- Building data lake solutions requiring high-throughput storage

## Core Concepts

### Architecture Modes

| Mode | Use Case | Description |
|------|----------|-------------|
| **Single Node** | Development, small deployments | All data on local disk with erasure coding across drives |
| **Distributed** | Production, large-scale | Multi-node cluster with replication and healing (under testing in alpha.93) |

### Storage Volumes

RustFS uses the `RUSTFS_VOLUMES` environment variable to define storage paths:
- **Single volume**: `/data`
- **Multiple volumes**: `/data/rustfs{0..3}` expands to `/data/rustfs0`, `/data/rustfs1`, etc.
- **Minimum drives**: 4 recommended for erasure coding (2 data + 2 parity)

### Ports and Services

| Port | Service | Protocol |
|------|---------|----------|
| 9000 | S3 API | HTTP/HTTPS |
| 9001 | Console UI | HTTP/HTTPS |
| 4317 | OpenTelemetry gRPC | OTLP/gRPC |
| 4318 | OpenTelemetry HTTP | OTLP/HTTP |

### Security Model

- **Access Key/Secret Key**: Default credentials (`rustfsadmin`/`rustfsadmin`)
- **IAM System**: Users, groups, policies with S3-compatible permissions
- **OIDC Integration**: External identity provider support
- **OpenStack Keystone**: X-Auth-Token authentication for Swift API
- **TLS/mTLS**: Certificate-based encryption and mutual authentication

## Installation Methods

### Method 1: One-Click Installer

```bash
curl -O https://rustfs.com/install_rustfs.sh && bash install_rustfs.sh
```

Installs latest release to `/opt/rustfs` with systemd service.

### Method 2: Docker/Podman

**Quick start:**
```bash
# Create data directory (must be owned by UID 10001)
mkdir -p data logs
chown -R 10001:10001 data logs

# Run with latest version
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  -v $(pwd)/data:/data \
  -v $(pwd)/logs:/logs \
  rustfs/rustfs:latest

# Or with Podman
podman run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  -v $(pwd)/data:/data \
  -v $(pwd)/logs:/logs \
  rustfs/rustfs:latest
```

**With environment variables:**
```bash
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  -e RUSTFS_VOLUMES=/data/rustfs{0..3} \
  -e RUSTFS_ACCESS_KEY=myaccesskey \
  -e RUSTFS_SECRET_KEY=mysecretkey \
  -e RUSTFS_CONSOLE_ENABLE=true \
  -v $(pwd)/data:/data \
  rustfs/rustfs:1.0.0-alpha.93
```

### Method 3: Docker Compose with Observability

```yaml
# docker-compose.yml
services:
  rustfs:
    image: rustfs/rustfs:latest
    container_name: rustfs-server
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - RUSTFS_VOLUMES=/data/rustfs{0..3}
      - RUSTFS_ADDRESS=0.0.0.0:9000
      - RUSTFS_CONSOLE_ADDRESS=0.0.0.0:9001
      - RUSTFS_CONSOLE_ENABLE=true
      - RUSTFS_ACCESS_KEY=rustfsadmin
      - RUSTFS_SECRET_KEY=rustfsadmin
      - RUSTFS_OBS_LOGGER_LEVEL=info
      - RUSTFS_OBS_ENDPOINT=http://otel-collector:4318
    volumes:
      - ./data:/data
      - ./logs:/app/logs
    restart: unless-stopped

  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    volumes:
      - ./otel-collector-config.yaml:/etc/otelcol-contrib/otel-collector.yml:ro
    ports:
      - "4317:4317"
      - "4318:4318"
    profiles:
      - observability

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yaml:/etc/prometheus/prometheus.yml:ro
    ports:
      - "9090:9090"
    profiles:
      - observability

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    profiles:
      - observability
```

Start with observability:
```bash
docker compose --profile observability up -d
```

### Method 4: Kubernetes (Helm)

```bash
# Add RustFS Helm repository
helm repo add rustfs https://charts.rustfs.com
helm repo update

# Create namespace
kubectl create namespace rustfs

# Install with default values
helm install rustfs rustfs/rustfs --namespace rustfs

# Install with custom values
helm install rustfs rustfs/rustfs \
  --namespace rustfs \
  --set persistence.size=100Gi \
  --set replicaCount=3 \
  --set service.type=LoadBalancer
```

See [Installation Guide](references/01-installation.md) for complete installation options.

### Method 5: Nix Flake

```bash
# Run without installing
nix run github:rustfs/rustfs

# Build binary
nix build github:rustfs/rustfs
./result/bin/rustfs --help

# From local checkout
cd rustfs
nix build
nix run
```

### Method 6: x-cmd

```bash
# Run without installing
x rustfs

# Install globally
x env use rustfs
rustfs --help
```

## Basic Usage

### Access Console

1. Navigate to `http://localhost:9001`
2. Login with default credentials: `rustfsadmin` / `rustfsadmin`
3. Create buckets and upload objects via web interface

### Create Bucket via S3 API

```bash
# Using AWS CLI (works with any S3-compatible client)
aws s3api create-bucket --bucket my-bucket \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# Verify bucket exists
aws s3api list-buckets \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin
```

### Upload and Download Objects

```bash
# Upload file
aws s3 cp my-file.txt s3://my-bucket/my-file.txt \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# Download file
aws s3 cp s3://my-bucket/my-file.txt ./downloaded.txt \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# List objects
aws s3 ls s3://my-bucket/ \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin
```

### Using mc (MinIO Client)

```bash
# Install mc
curl https://min.io/client/mc.sh | bash

# Configure RustFS endpoint
mc alias set myrustfs http://localhost:9000 rustfsadmin rustfsadmin

# Create bucket
mc mb myrustfs/my-bucket

# Upload file
mc cp my-file.txt myrustfs/my-bucket/

# List contents
mc ls myrustfs/my-bucket/
```

See [Configuration Reference](references/02-configuration.md) for environment variables and settings.


## See Also

- [Advanced Features](references/03-advanced-features.md) - Advanced configuration, observability, troubleshooting, and performance tuning

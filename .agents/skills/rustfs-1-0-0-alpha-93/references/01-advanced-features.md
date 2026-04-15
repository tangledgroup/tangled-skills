# RustFS Advanced Features

This reference covers advanced configuration, observability setup, troubleshooting, and performance tuning.

## Advanced Features

### Versioning

Enable versioning to preserve all object versions:

```bash
# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-bucket \
  --versioning-configuration Status=Enabled \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# List versions
aws s3api list-object-versions \
  --bucket my-bucket \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin
```

### Bucket Replication

Configure cross-region or cross-cluster replication (see [Advanced Features](refs/03-advanced-features.md)):

```bash
# Create replication configuration
cat > replication-config.json <<EOF
{
  "Role": "arn:aws:iam:::role/rustfs-replication",
  "Rules": [
    {
      "ID": "ReplicateAll",
      "Status": "Enabled",
      "Priority": 1,
      "Filter": {},
      "Destination": {
        "Bucket": "arn:aws:s3:::destination-bucket",
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
  --endpoint-url http://localhost:9000
```

### Lifecycle Management

Automate object transitions and expirations (under testing in alpha.93):

```bash
# Create lifecycle configuration
cat > lifecycle-config.json <<EOF
{
  "Rules": [
    {
      "ID": "TransitionToIA",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "logs/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER"
        }
      ]
    },
    {
      "ID": "ExpireOldObjects",
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
  --endpoint-url http://localhost:9000
```

### Event Notifications

Configure event triggers for uploads, deletions, etc.:

```bash
# Create notification configuration
cat > notification-config.json <<EOF
{
  "NotificationConfiguration": {
    "TopicConfigurations": [
      {
        "Id": "UploadNotifications",
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:my-topic",
        "Events": ["s3:ObjectCreated:*"]
      }
    ],
    "QueueConfigurations": [
      {
        "Id": "DeleteNotifications",
        "QueueArn": "arn:aws:sqs:us-east-1:123456789012:my-queue",
        "Events": ["s3:ObjectRemoved:*"]
      }
    ]
  }
}
EOF

# Apply notification configuration
aws s3api put-bucket-notification-configuration \
  --bucket my-bucket \
  --notification-configuration file://notification-config.json \
  --endpoint-url http://localhost:9000
```

See [Advanced Features](refs/03-advanced-features.md) for detailed workflows.

### IAM and Access Control

Manage users, groups, and policies via Console or API:

```bash
# Create user (via mc)
mc admin user add myrustfs newuser newpassword

# Create policy
cat > reader-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::my-bucket/*",
        "arn:aws:s3:::my-bucket"
      ]
    }
  ]
}
EOF

mc admin policy add myrustfs reader file://reader-policy.json

# Attach policy to user
mc admin policy attach myrustfs reader --user newuser
```

### OpenStack Swift Integration

RustFS supports Swift API with Keystone authentication:

```bash
# Install Swift client
pip install python-swiftclient

# Configure Swift connection
export OS_AUTH_URL=http://keystone:5000/v3
export OS_PROJECT_NAME=myproject
export OS_USERNAME=myuser
export OS_PASSWORD=mypassword

# List containers (buckets)
swift list

# Upload object
swift upload my-container myfile.txt

# Download object
swift download my-container myfile.txt
```

See [OpenStack Integration](refs/04-openstack-integration.md) for detailed Swift/Keystone setup.

## Observability

### Built-in Metrics

RustFS exposes Prometheus metrics at `/metrics` endpoint when observability is configured.

### OpenTelemetry Configuration

```bash
# Configure OpenTelemetry endpoint
export RUSTFS_OBS_ENDPOINT=http://otel-collector:4318
export RUSTFS_OBS_LOGGER_LEVEL=info

# Log to file directory
export RUSTFS_OBS_LOG_DIRECTORY=/var/log/rustfs

# Log sampling ratio (1.0 = all logs)
export RUSTFS_OBS_LOGGER_SAMPLE_RATIO=1.0
```

### Grafana Dashboards

Access Grafana at `http://localhost:3000` (when using docker-compose with observability profile):
- Default credentials: `admin` / `admin`
- Pre-configured dashboards for RustFS metrics
- Trace visualization via Tempo/Jaeger integration

See [Observability Guide](refs/05-observability.md) for complete monitoring setup.

## Troubleshooting

### Common Issues

**Permission denied on data directory:**
```bash
# Ensure data directory is owned by UID 10001 (rustfs user)
chown -R 10001:10001 /path/to/data
```

**Cannot connect to console:**
```bash
# Verify console is enabled
grep RUSTFS_CONSOLE_ENABLE /proc/$(pidof rustfs)/environ

# Check if port 9001 is listening
netstat -tlnp | grep 9001
```

**High memory usage:**
```bash
# Adjust buffer profile for your workload
export RUSTFS_BUFFER_PROFILE=GeneralPurpose  # or DataLake, AI, WebServer

# Reduce concurrent disk reads
export RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=32
```

See [Troubleshooting Guide](refs/06-troubleshooting.md) for detailed diagnostics.

## Performance Tuning

### Buffer Profiles

Optimize for different workloads:

| Profile | Use Case | Description |
|---------|----------|-------------|
| `GeneralPurpose` | Mixed workloads | Balanced settings for general use |
| `DataLake` | Big data, analytics | Optimized for large sequential reads |
| `AI` | Machine learning | Tuned for high-throughput tensor access |
| `WebServer` | Content delivery | Optimized for small object serving |

```bash
# Set buffer profile
export RUSTFS_BUFFER_PROFILE=DataLake
```

### Concurrent Operations

Tune concurrency limits:

```bash
# Maximum concurrent disk reads (default: 64)
export RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=128

# High concurrency threshold (default: 8)
export RUSTFS_OBJECT_HIGH_CONCURRENCY_THRESHOLD=16

# Medium concurrency threshold (default: 4)
export RUSTFS_OBJECT_MEDIUM_CONCURRENCY_THRESHOLD=8
```

See [Performance Tuning](refs/07-performance.md) for advanced optimization.

## References

- **Official Documentation**: https://docs.rustfs.com
- **GitHub Repository**: https://github.com/rustfs/rustfs
- **Helm Charts**: https://charts.rustfs.com
- **Docker Hub**: https://hub.docker.com/r/rustfs/rustfs
- **Release Notes**: https://github.com/rustfs/rustfs/releases/tag/1.0.0-alpha.93

### Reference Files

- [`refs/01-installation.md`](refs/01-installation.md) - Complete installation methods and deployment patterns
- [`refs/02-configuration.md`](refs/02-configuration.md) - Environment variables, TLS setup, and configuration options
- [`refs/03-advanced-features.md`](refs/03-advanced-features.md) - Versioning, replication, lifecycle, notifications, S3 Select
- [`refs/04-openstack-integration.md`](refs/04-openstack-integration.md) - Swift API and Keystone authentication setup
- [`refs/05-observability.md`](refs/05-observability.md) - OpenTelemetry, Prometheus, Grafana, tracing configuration
- [`refs/06-troubleshooting.md`](refs/06-troubleshooting.md) - Common issues, debugging, log analysis, health checks
- [`refs/07-performance.md`](refs/07-performance.md) - Performance tuning, buffer profiles, concurrency optimization

### Related Skills

Consider these skills for complementary technologies:
- `podman-5-8-1` for container management without Docker daemon
- `podman-compose-1-5-0` for multi-container RustFS deployments
- `sqlalchemy-2-0` if integrating with relational databases for metadata
- `redis-py-7-4` for caching layers or session management

## Version Information

- **Version**: 1.0.0-alpha.93
- **Rust Version**: 1.93.0
- **License**: Apache 2.0
- **Status**: Alpha (some features under testing: distributed mode, lifecycle, KMS)
- **Minimum Requirements**: 
  - CPU: 2 cores recommended
  - Memory: 4GB minimum
  - Storage: 4 drives minimum for erasure coding
  - Network: Gigabit+ for production

# RustFS Configuration Reference

This reference covers all configuration options, environment variables, and settings for RustFS 1.0.0-alpha.93.

## Configuration Methods

RustFS supports multiple configuration methods with the following precedence (highest to lowest):

1. **Command-line arguments** (highest priority)
2. **Environment variables** (prefix: `RUSTFS_`)
3. **Default values** (lowest priority)

## Core Environment Variables

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_ADDRESS` | `:9000` | Address for S3 API listener (host:port) |
| `RUSTFS_CONSOLE_ADDRESS` | `:9001` | Address for Console UI listener |
| `RUSTFS_CONSOLE_ENABLE` | `true` | Enable/disable console UI |
| `RUSTFS_VOLUMES` | `/data` | Storage volumes (supports expansion: `/data/rustfs{0..3}`) |

```bash
# Single address binding
export RUSTFS_ADDRESS=:9000

# Specific interface binding
export RUSTFS_ADDRESS=0.0.0.0:9000

# Multiple interfaces (not supported, use load balancer instead)
```

### Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_ACCESS_KEY` | `rustfsadmin` | Access key for authentication |
| `RUSTFS_SECRET_KEY` | `rustfsadmin` | Secret key (minimum 8 characters) |
| `RUSTFS_ROOT_USER` | - | Root username for console (alternative to access key) |
| `RUSTFS_ROOT_PASSWORD` | - | Root password for console (alternative to secret key) |

```bash
# Set custom credentials
export RUSTFS_ACCESS_KEY=myaccesskey123
export RUSTFS_SECRET_KEY=mysecretkey123456789

# Or use root user/password
export RUSTFS_ROOT_USER=admin
export RUSTFS_ROOT_PASSWORD=securepassword123
```

### File-based Credentials

For better security, use files instead of environment variables:

```bash
# Create credential files
echo -n "myaccesskey" > /etc/rustfs/access.key
echo -n "mysecretkey" > /etc/rustfs/secret.key
chmod 600 /etc/rustfs/*.key

# Reference in environment
export RUSTFS_ACCESS_KEY_FILE=/etc/rustfs/access.key
export RUSTFS_SECRET_KEY_FILE=/etc/rustfs/secret.key
```

## CORS Configuration

### S3 API CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_CORS_ALLOWED_ORIGINS` | `*` | Comma-separated list of allowed origins |
| `RUSTFS_CORS_ALLOWED_METHODS` | `*` | Allowed HTTP methods |
| `RUSTFS_CORS_ALLOWED_HEADERS` | `*` | Allowed request headers |
| `RUSTFS_CORS_ALLOWED_CREDENTIALS` | `false` | Allow credentials in CORS requests |
| `RUSTFS_CORS_MAX_AGE` | `3600` | Preflight cache duration (seconds) |

```bash
# Allow specific origins
export RUSTFS_CORS_ALLOWED_ORIGINS="https://app1.example.com,https://app2.example.com"

# Allow all origins (development only)
export RUSTFS_CORS_ALLOWED_ORIGINS="*"

# Configure methods and headers
export RUSTFS_CORS_ALLOWED_METHODS="GET,PUT,POST,DELETE,HEAD"
export RUSTFS_CORS_ALLOWED_HEADERS="Content-Type,Authorization,X-Amz-Date,X-Amz-Security-Token"
```

### Console CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_CONSOLE_CORS_ALLOWED_ORIGINS` | `*` | Allowed origins for console |
| `RUSTFS_CONSOLE_RATE_LIMIT_ENABLE` | `false` | Enable rate limiting |
| `RUSTFS_CONSOLE_RATE_LIMIT_RPM` | `100` | Requests per minute limit |
| `RUSTFS_CONSOLE_AUTH_TIMEOUT` | `3600` | Session timeout (seconds) |

```bash
# Restrict console access
export RUSTFS_CONSOLE_CORS_ALLOWED_ORIGINS="https://console.example.com"

# Enable rate limiting
export RUSTFS_CONSOLE_RATE_LIMIT_ENABLE=true
export RUSTFS_CONSOLE_RATE_LIMIT_RPM=50

# Shorten session timeout
export RUSTFS_CONSOLE_AUTH_TIMEOUT=1800  # 30 minutes
```

## TLS/SSL Configuration

### Basic TLS Setup

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_TLS_PATH` | `` | Directory containing TLS certificates |
| `RUSTFS_TRUST_SYSTEM_CA` | `false` | Trust system CA certificates |
| `RUSTFS_TRUST_LEAF_CERT_AS_CA` | `false` | Trust leaf certificates as CA |

Expected files in `RUSTFS_TLS_PATH`:
- `rustfs_cert.pem` - Server certificate
- `rustfs_key.pem` - Server private key
- `public.crt` - Public certificate (optional)
- `ca.crt` - CA certificate (optional)
- `client_ca.crt` - Client CA for mTLS (optional)

```bash
# Set TLS path
export RUSTFS_TLS_PATH=/etc/rustfs/tls

# Trust system CAs (for internal CAs)
export RUSTFS_TRUST_SYSTEM_CA=true

# Enable TLS key logging (debugging only)
export RUSTFS_TLS_KEYLOG=1
```

### Certificate Generation

```bash
# Generate self-signed certificate (development only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/rustfs/tls/rustfs_key.pem \
  -out /etc/rustfs/tls/rustfs_cert.pem \
  -subj "/CN=example.com/O=RustFS/C=US"

# Generate CSR for CA-signed certificate
openssl req -new -newkey rsa:2048 -nodes \
  -keyout /etc/rustfs/tls/rustfs_key.pem \
  -out /etc/rustfs/tls/cert.csr \
  -subj "/CN=example.com/O=RustFS/C=US"

# Submit cert.csr to CA, then save signed certificate as rustfs_cert.pem
```

### mTLS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_SERVER_MTLS_ENABLE` | `false` | Require client certificates |
| `RUSTFS_MTLS_CLIENT_CERT` | `client_cert.pem` | Client certificate path |
| `RUSTFS_MTLS_CLIENT_KEY` | `client_key.pem` | Client private key path |

```bash
# Enable mTLS
export RUSTFS_SERVER_MTLS_ENABLE=true
export RUSTFS_TLS_PATH=/etc/rustfs/tls

# Required files:
# /etc/rustfs/tls/client_ca.crt (CA for verifying client certs)
# /etc/rustfs/tls/rustfs_cert.pem (server certificate)
# /etc/rustfs/tls/rustfs_key.pem (server key)
```

### TLS Hot Reload

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_TLS_RELOAD_ENABLE` | `false` | Enable automatic certificate reload |
| `RUSTFS_TLS_RELOAD_INTERVAL` | `30` | Reload interval (seconds, min: 5) |

```bash
# Enable hot reload for certificates
export RUSTFS_TLS_RELOAD_ENABLE=true
export RUSTFS_TLS_RELOAD_INTERVAL=60
```

## HTTP/2 Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_H2_INITIAL_STREAM_WINDOW_SIZE` | `4194304` (4MB) | Initial stream window size |
| `RUSTFS_H2_INITIAL_CONN_WINDOW_SIZE` | `8388608` (8MB) | Initial connection window |
| `RUSTFS_H2_MAX_FRAME_SIZE` | `524288` (512KB) | Maximum frame size |
| `RUSTFS_H2_MAX_HEADER_LIST_SIZE` | `65536` (64KB) | Max header list size |
| `RUSTFS_H2_MAX_CONCURRENT_STREAMS` | `2048` | Max concurrent streams |
| `RUSTFS_H2_KEEP_ALIVE_INTERVAL` | `20` | Keep-alive interval (seconds) |
| `RUSTFS_H2_KEEP_ALIVE_TIMEOUT` | `10` | Keep-alive timeout (seconds) |

```bash
# Increase window sizes for high-throughput
export RUSTFS_H2_INITIAL_STREAM_WINDOW_SIZE=8388608  # 8MB
export RUSTFS_H2_INITIAL_CONN_WINDOW_SIZE=16777216   # 16MB

# Adjust for many concurrent connections
export RUSTFS_H2_MAX_CONCURRENT_STREAMS=4096
```

## HTTP/1.1 Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_HTTP1_HEADER_READ_TIMEOUT` | `5` | Header read timeout (seconds) |
| `RUSTFS_HTTP1_MAX_BUF_SIZE` | `65536` (64KB) | Maximum buffer size |

```bash
# Increase for large headers
export RUSTFS_HTTP1_MAX_BUF_SIZE=131072  # 128KB
```

## Observability Configuration

### Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_OBS_LOGGER_LEVEL` | `error` | Log level (trace, debug, info, warn, error) |
| `RUSTFS_OBS_LOG_DIRECTORY` | - | Log output directory (empty = stdout) |
| `RUSTFS_OBS_LOGGER_SAMPLE_RATIO` | `1.0` | Sampling ratio (1.0 = all logs) |
| `RUSTFS_OBS_ENDPOINT` | `` | OpenTelemetry endpoint URL |

```bash
# Set log level
export RUSTFS_OBS_LOGGER_LEVEL=debug

# Log to file directory
export RUSTFS_OBS_LOG_DIRECTORY=/var/log/rustfs

# Sample logs (reduce volume)
export RUSTFS_OBS_LOGGER_SAMPLE_RATIO=0.5  # 50% of logs

# Send to OpenTelemetry collector
export RUSTFS_OBS_ENDPOINT=http://otel-collector:4318
```

### Metrics

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_OBS_SERVICE_VERSION` | `1.0.0` | Service version for metrics |
| `RUSTFS_METER_INTERVAL` | `30` | Meter interval (seconds) |

```bash
# Set custom service version
export RUSTFS_OBS_SERVICE_VERSION=1.0.0-alpha.93

# Adjust meter interval
export RUSTFS_METER_INTERVAL=60
```

## Object Storage Configuration

### Buffer Profiles

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_BUFFER_PROFILE` | `GeneralPurpose` | Buffer profile (GeneralPurpose, DataLake, AI, WebServer) |

```bash
# Optimize for data lake workloads
export RUSTFS_BUFFER_PROFILE=DataLake

# Optimize for AI/ML workloads
export RUSTFS_BUFFER_PROFILE=AI

# Optimize for web serving
export RUSTFS_BUFFER_PROFILE=WebServer
```

### Concurrency Control

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_OBJECT_HIGH_CONCURRENCY_THRESHOLD` | `8` | High concurrency threshold |
| `RUSTFS_OBJECT_MEDIUM_CONCURRENCY_THRESHOLD` | `4` | Medium concurrency threshold |
| `RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS` | `64` | Max concurrent disk reads |

```bash
# Adjust for high-concurrency workloads
export RUSTFS_OBJECT_HIGH_CONCURRENCY_THRESHOLD=16
export RUSTFS_OBJECT_MEDIUM_CONCURRENCY_THRESHOLD=8
export RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=128
```

### Timeout Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_OBJECT_GET_TIMEOUT` | `30` | GetObject timeout (seconds) |
| `RUSTFS_OBJECT_DISK_READ_TIMEOUT` | `10` | Disk read timeout (seconds) |
| `RUSTFS_OBJECT_MIN_TIMEOUT` | `5` | Minimum timeout (seconds) |
| `RUSTFS_OBJECT_MAX_TIMEOUT` | `300` | Maximum timeout (seconds) |
| `RUSTFS_OBJECT_BYTES_PER_SECOND` | `1048576` (1MB/s) | Throughput estimate for dynamic timeout |

```bash
# Increase timeouts for large objects
export RUSTFS_OBJECT_GET_TIMEOUT=60
export RUSTFS_OBJECT_MAX_TIMEOUT=600  # 10 minutes

# Adjust throughput estimate
export RUSTFS_OBJECT_BYTES_PER_SECOND=5242880  # 5MB/s
```

### Bitrot Protection

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_OBJECT_GET_SKIP_BITROT_VERIFY` | `false` | Skip bitrot verification on reads |

```bash
# Disable bitrot verification for performance (not recommended)
export RUSTFS_OBJECT_GET_SKIP_BITROT_VERIFY=true
```

## KMS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_KMS_ENABLE` | `false` | Enable Key Management Service |
| `RUSTFS_KMS_BACKEND` | `local` | KMS backend (local, vault) |
| `RUSTFS_KMS_VAULT_MOUNT_PATH` | `vault` | Vault transit mount path |

```bash
# Enable local KMS
export RUSTFS_KMS_ENABLE=true
export RUSTFS_KMS_BACKEND=local

# Enable Vault backend
export RUSTFS_KMS_ENABLE=true
export RUSTFS_KMS_BACKEND=vault
export RUSTFS_KMS_VAULT_MOUNT_PATH=transit
```

## Update Check

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_CHECK_UPDATE` | `true` | Enable update checking |

```bash
# Disable update checks
export RUSTFS_CHECK_UPDATE=false
```

## User/Group Configuration

For running as non-root user:

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTFS_UID` | - | User ID to run as |
| `RUSTFS_GID` | - | Group ID to run as |
| `RUSTFS_USERNAME` | - | Username to run as |
| `RUSTFS_GROUPNAME` | - | Group name to run as |

```bash
# Set specific UID/GID
export RUSTFS_UID=10001
export RUSTFS_GID=10001

# Or use username/groupname
export RUSTFS_USERNAME=rustfs
export RUSTFS_GROUPNAME=rustfs
```

## Complete Docker Example

```bash
docker run -d \
  --name rustfs \
  -p 9000:9000 \
  -p 9001:9001 \
  -v /data/rustfs:/data \
  -v /var/log/rustfs:/logs \
  -v /etc/rustfs/tls:/opt/tls:ro \
  -e RUSTFS_VOLUMES=/data/rustfs{0..3} \
  -e RUSTFS_ADDRESS=0.0.0.0:9000 \
  -e RUSTFS_CONSOLE_ADDRESS=0.0.0.0:9001 \
  -e RUSTFS_CONSOLE_ENABLE=true \
  -e RUSTFS_ACCESS_KEY=myaccesskey \
  -e RUSTFS_SECRET_KEY=mysecretkey \
  -e RUSTFS_TLS_PATH=/opt/tls \
  -e RUSTFS_CORS_ALLOWED_ORIGINS="https://app.example.com" \
  -e RUSTFS_CONSOLE_CORS_ALLOWED_ORIGINS="https://console.example.com" \
  -e RUSTFS_OBS_LOGGER_LEVEL=info \
  -e RUSTFS_OBS_LOG_DIRECTORY=/logs \
  -e RUSTFS_OBS_ENDPOINT=http://otel-collector:4318 \
  -e RUSTFS_BUFFER_PROFILE=DataLake \
  -e RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=128 \
  -e RUSTFS_CHECK_UPDATE=false \
  rustfs/rustfs:1.0.0-alpha.93
```

## Configuration Validation

### Verify Environment Variables

```bash
# Check running configuration
docker exec rustfs env | grep RUSTFS

# Or for systemd service
systemctl show rustfs | grep Environment
```

### Test Configuration

```bash
# Start with verbose logging to verify config
export RUSTFS_OBS_LOGGER_LEVEL=debug
rustfs --console-enable true /tmp/test/{0..3}

# Check health endpoint
curl http://localhost:9000/health

# Verify TLS (if enabled)
curl -k https://localhost:9000/health
```

## Best Practices

### Security

1. **Change default credentials** in production:
   ```bash
   export RUSTFS_ACCESS_KEY=$(openssl rand -hex 16)
   export RUSTFS_SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **Use TLS in production**:
   ```bash
   export RUSTFS_TLS_PATH=/etc/rustfs/tls
   ```

3. **Restrict CORS origins**:
   ```bash
   export RUSTFS_CORS_ALLOWED_ORIGINS="https://your-app.example.com"
   ```

4. **Run as non-root user**:
   ```bash
   export RUSTFS_UID=10001
   export RUSTFS_GID=10001
   ```

### Performance

1. **Match buffer profile to workload**:
   - Data Lake: `DataLake`
   - AI/ML: `AI`
   - Web serving: `WebServer`
   - Mixed: `GeneralPurpose`

2. **Tune concurrency for hardware**:
   ```bash
   # For SSDs with high IOPS
   export RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=128
   
   # For HDDs
   export RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=32
   ```

3. **Enable observability for monitoring**:
   ```bash
   export RUSTFS_OBS_LOGGER_LEVEL=info
   export RUSTFS_OBS_ENDPOINT=http://otel-collector:4318
   ```

### Operations

1. **Log rotation** when using file logs:
   ```bash
   # /etc/logrotate.d/rustfs
   /var/log/rustfs/*.log {
       daily
       rotate 14
       compress
       delaycompress
       missingok
       notifempty
       copytruncate
   }
   ```

2. **Certificate renewal** with hot reload:
   ```bash
   export RUSTFS_TLS_RELOAD_ENABLE=true
   export RUSTFS_TLS_RELOAD_INTERVAL=300  # 5 minutes
   ```

3. **Health checks for orchestration**:
   ```bash
   curl -f http://localhost:9000/health || exit 1
   curl -f http://localhost:9001/rustfs/console/health || exit 1
   ```

## Troubleshooting Configuration

See [`06-troubleshooting.md`](06-troubleshooting.md) for configuration-related issues and solutions.

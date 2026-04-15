# RustFS Performance Tuning Guide

This reference covers performance optimization, tuning parameters, and best practices for maximizing RustFS 1.0.0-alpha.93 throughput and efficiency.

## Performance Overview

### Key Performance Metrics

| Metric | Target (Small Objects) | Target (Large Objects) | Measurement |
|--------|------------------------|------------------------|-------------|
| P50 Latency | < 10ms | < 50ms | Request duration |
| P95 Latency | < 50ms | < 200ms | Request duration |
| P99 Latency | < 100ms | < 500ms | Request duration |
| Throughput | > 1000 req/s | > 100 MB/s | Requests/bytes per second |
| CPU Usage | < 70% | < 80% | Per-core utilization |
| Memory | < 4GB (typical) | < 8GB (data lake) | RSS memory |

### Hardware Recommendations

#### Minimum Requirements

| Component | Specification | Use Case |
|-----------|---------------|----------|
| CPU | 2 cores | Development, testing |
| Memory | 4GB RAM | Small deployments |
| Storage | 4 drives (SSD recommended) | Erasure coding minimum |
| Network | 1Gbps | Basic workloads |

#### Production Recommendations

| Component | Specification | Use Case |
|-----------|---------------|----------|
| CPU | 8+ cores | High-throughput production |
| Memory | 16-32GB RAM | Data lake, AI workloads |
| Storage | NVMe SSDs (4+ drives) | Maximum performance |
| Network | 10Gbps+ | Large file transfers |

## Buffer Profile Configuration

RustFS provides pre-configured buffer profiles optimized for different workloads.

### Available Profiles

#### GeneralPurpose (Default)

Balanced settings for mixed workloads:

```bash
export RUSTFS_BUFFER_PROFILE=GeneralPurpose
```

**Best for:**
- Mixed read/write operations
- Variable object sizes
- General file storage
- Development environments

#### DataLake

Optimized for large sequential reads and analytics:

```bash
export RUSTFS_BUFFER_PROFILE=DataLake
```

**Best for:**
- Big data processing (Spark, Presto)
- Large file transfers (>100MB)
- Sequential access patterns
- Data warehouse workloads

**Benefits:**
- Larger buffers for streaming I/O
- Optimized for throughput over latency
- Better performance with parallel readers

#### AI

Tuned for machine learning and tensor operations:

```bash
export RUSTFS_BUFFER_PROFILE=AI
```

**Best for:**
- ML training data access
- Tensor/NDArray storage
- High-throughput small object reads
- Concurrent model serving

**Benefits:**
- Optimized for random access patterns
- Reduced latency for metadata operations
- Better concurrency handling

#### WebServer

Optimized for serving many small objects:

```bash
export RUSTFS_BUFFER_PROFILE=WebServer
```

**Best for:**
- Static content delivery
- CDN origin storage
- Many concurrent small requests
- Web application assets

**Benefits:**
- Lower memory footprint per request
- Faster connection handling
- Optimized HTTP/2 behavior

### Custom Buffer Tuning

For advanced use cases, tune individual parameters:

```bash
# Increase buffer sizes for large file transfers
export RUSTFS_BUFFER_SIZE=8388608  # 8MB buffers

# Reduce for memory-constrained environments
export RUSTFS_BUFFER_SIZE=1048576  # 1MB buffers
```

## Concurrency Control

### Concurrent Disk Reads

Control the number of simultaneous disk read operations:

| Value | Use Case | Hardware |
|-------|----------|----------|
| 32 | HDD, low-end SSD | SATA SSD, mechanical drives |
| 64 (default) | Standard SSD | NVMe Gen3 |
| 128 | High-performance SSD | NVMe Gen4+ |
| 256 | Enterprise storage | RAID arrays, all-NVMe |

```bash
# Adjust for your storage hardware
export RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=128
```

**Impact:**
- **Higher values**: Better throughput on fast storage, higher memory usage
- **Lower values**: Reduced memory pressure, potentially lower throughput

### Concurrency Thresholds

RustFS adapts buffer sizes based on concurrent request count:

```bash
# Medium concurrency threshold (default: 4)
# Buffers reduced to 75% when requests > 4
export RUSTFS_OBJECT_MEDIUM_CONCURRENCY_THRESHOLD=8

# High concurrency threshold (default: 8)
# Buffers reduced to 40% when requests > 8
export RUSTFS_OBJECT_HIGH_CONCURRENCY_THRESHOLD=16
```

**Strategy:**
- Increase thresholds for high-concurrency workloads
- Decrease for memory-constrained environments
- Monitor `rustfs_concurrent_requests` metric

### Timeout Configuration

Prevent resource exhaustion with timeouts:

```bash
# GetObject timeout (default: 30s)
export RUSTFS_OBJECT_GET_TIMEOUT=60

# Disk read timeout (default: 10s)
export RUSTFS_OBJECT_DISK_READ_TIMEOUT=15

# Minimum timeout (default: 5s)
export RUSTFS_OBJECT_MIN_TIMEOUT=10

# Maximum timeout (default: 300s)
export RUSTFS_OBJECT_MAX_TIMEOUT=600

# Throughput estimate for dynamic timeout (default: 1MB/s)
export RUSTFS_OBJECT_BYTES_PER_SECOND=5242880  # 5MB/s
```

**Dynamic Timeout Calculation:**
```
timeout = min(max(
  (object_size / bytes_per_second) * buffer_factor,
  min_timeout
), max_timeout)
```

## HTTP/2 Tuning

### Stream Window Size

Control flow control window sizes for HTTP/2:

```bash
# Initial stream window size (default: 4MB)
export RUSTFS_H2_INITIAL_STREAM_WINDOW_SIZE=8388608  # 8MB

# Initial connection window size (default: 8MB)
export RUSTFS_H2_INITIAL_CONN_WINDOW_SIZE=16777216   # 16MB
```

**Impact:**
- **Larger windows**: Better throughput for large transfers
- **Smaller windows**: Lower memory usage, better fairness

### Frame and Header Limits

```bash
# Max frame size (default: 512KB, range: 16KB-16MB)
export RUSTFS_H2_MAX_FRAME_SIZE=1048576  # 1MB

# Max header list size (default: 64KB)
export RUSTFS_H2_MAX_HEADER_LIST_SIZE=131072  # 128KB
```

### Concurrent Streams

```bash
# Max concurrent streams per connection (default: 2048)
export RUSTFS_H2_MAX_CONCURRENT_STREAMS=4096
```

**Impact:**
- Higher values allow more parallel operations per connection
- Increases memory usage proportionally

### Keep-Alive Settings

```bash
# Keep-alive interval (default: 20s)
export RUSTFS_H2_KEEP_ALIVE_INTERVAL=30

# Keep-alive timeout (default: 10s)
export RUSTFS_H2_KEEP_ALIVE_TIMEOUT=15
```

## HTTP/1.1 Tuning

For clients using HTTP/1.1:

```bash
# Header read timeout (default: 5s)
export RUSTFS_HTTP1_HEADER_READ_TIMEOUT=10

# Max buffer size (default: 64KB)
export RUSTFS_HTTP1_MAX_BUF_SIZE=131072  # 128KB
```

## Storage Optimization

### Erasure Coding Configuration

RustFS uses erasure coding by default (typically 4+4 data/parity shards):

**Minimum drives:** 4 (2 data + 2 parity)
**Recommended drives:** 8-16 for optimal performance

```bash
# Configure volumes for erasure coding
export RUSTFS_VOLUMES=/data/rustfs{0..7}  # 8 drives
```

**Drive count vs. performance:**
- 4 drives: Minimum viable, ~50% storage efficiency
- 8 drives: Good balance, ~67% efficiency
- 12+ drives: Optimal for large deployments, ~75%+ efficiency

### Bitrot Protection

Bitrot verification is enabled by default:

```bash
# Skip bitrot verification on reads (NOT RECOMMENDED)
export RUSTFS_OBJECT_GET_SKIP_BITROT_VERIFY=true
```

**Performance impact:**
- **Enabled (default)**: Full data integrity, ~5-10% CPU overhead
- **Disabled**: Faster reads, risk of undetected corruption

**Recommendation:** Keep enabled in production; background scanner handles integrity checks.

### I/O Scheduler Tuning

For optimal performance on Linux:

```bash
# Check current I/O scheduler
cat /sys/block/sda/queue/scheduler

# Set to mq-deadline or none (for NVMe)
echo mq-deadline | sudo tee /sys/block/sda/queue/scheduler

# Make permanent (add to /etc/fstab or systemd unit)
```

**Scheduler recommendations:**
- **NVMe**: `none` or `mq-deadline`
- **SATA SSD**: `mq-deadline` or `kyber`
- **HDD**: `bfq` or `mq-deadline`

## Network Optimization

### TCP Tuning (System-wide)

**/etc/sysctl.d/99-rustfs.conf:**
```bash
# Increase TCP buffer sizes
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728

# Enable TCP optimizations
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 5

# Increase file descriptors
fs.file-max = 2097152
net.core.somaxconn = 65535
```

Apply changes:
```bash
sudo sysctl --system
```

### Connection Limits

```bash
# Increase ulimit for RustFS process
ulimit -n 65536  # Max open files

# In Docker
docker run --ulimit nofile=65536:65536 rustfs/rustfs:latest

# In systemd (in service file)
LimitNOFILE=65536
```

## Monitoring Performance

### Key Metrics to Watch

#### Request Metrics

```promql
# Request rate
rate(rustfs_requests_total[5m])

# Error rate
rate(rustfs_errors_total[5m])

# Latency percentiles
histogram_quantile(0.50, rate(rustfs_request_duration_seconds_bucket[5m]))  # P50
histogram_quantile(0.95, rate(rustfs_request_duration_seconds_bucket[5m]))  # P95
histogram_quantile(0.99, rate(rustfs_request_duration_seconds_bucket[5m]))  # P99
```

#### Storage Metrics

```promql
# I/O throughput
rate(rustfs_io_read_bytes_total[5m]) + rate(rustfs_io_write_bytes_total[5m])

# I/O operations per second
rate(rustfs_io_operations_total[5m])

# Storage utilization
rustfs_usage_bytes / rustfs_capacity_bytes * 100
```

#### Resource Metrics

```promql
# Concurrent requests
rustfs_concurrent_requests

# Bucket and object counts
rustfs_buckets_count
rustfs_objects_count
```

### Performance Dashboards

Create Grafana dashboards with these panels:

**Overview:**
- Request rate (req/s)
- Error rate (% of total)
- P50/P95/P99 latency
- Storage usage gauge

**I/O Performance:**
- Read/write throughput (MB/s)
- IOPS (operations/sec)
- Disk utilization per drive

**Resources:**
- Concurrent requests over time
- Memory usage trend
- CPU utilization

### Benchmarking

#### Sequential Read Test

```bash
# Create large test file
dd if=/dev/zero of=/tmp/testfile bs=1M count=1024

# Upload
aws s3 cp /tmp/testfile s3://test-bucket/largefile \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# Download and measure speed
time aws s3 cp s3://test-bucket/largefile /tmp/downloaded \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# Cleanup
rm /tmp/testfile /tmp/downloaded
```

#### Concurrent Upload Test

```bash
# Upload multiple files in parallel
for i in {1..100}; do
  dd if=/dev/zero of=/tmp/file$i bs=1M count=10 &
done
wait

for i in {1..100}; do
  aws s3 cp /tmp/file$i s3://test-bucket/file$i \
    --endpoint-url http://localhost:9000 &
done
wait

# Cleanup
rm /tmp/file{1..100}
```

#### Small Object Test

```bash
# Create many small files
mkdir -p /tmp/small-objects
for i in {1..1000}; do
  echo "small object $i" > /tmp/small-objects/object$i.txt
done

# Upload all
cd /tmp/small-objects
aws s3 cp . s3://test-bucket/small-objects/ \
  --endpoint-url http://localhost:9000 \
  --recursive

# Measure listing performance
time aws s3 ls s3://test-bucket/small-objects/ \
  --endpoint-url http://localhost:9000 | wc -l
```

## Workload-Specific Tuning

### Data Lake / Analytics

```bash
docker run -d \
  -e RUSTFS_BUFFER_PROFILE=DataLake \
  -e RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=128 \
  -e RUSTFS_H2_INITIAL_STREAM_WINDOW_SIZE=8388608 \
  -e RUSTFS_H2_MAX_CONCURRENT_STREAMS=4096 \
  --memory=16g \
  rustfs/rustfs:latest
```

**Key optimizations:**
- Large buffer profile for sequential I/O
- High concurrent disk reads
- Increased HTTP/2 window sizes

### AI / Machine Learning

```bash
docker run -d \
  -e RUSTFS_BUFFER_PROFILE=AI \
  -e RUSTFS_OBJECT_HIGH_CONCURRENCY_THRESHOLD=16 \
  -e RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=256 \
  --memory=32g \
  rustfs/rustfs:latest
```

**Key optimizations:**
- AI profile for random access patterns
- Higher concurrency thresholds
- Maximum disk I/O parallelism

### Web Serving / CDN Origin

```bash
docker run -d \
  -e RUSTFS_BUFFER_PROFILE=WebServer \
  -e RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=64 \
  -e RUSTFS_H2_KEEP_ALIVE_INTERVAL=10 \
  --memory=8g \
  rustfs/rustfs:latest
```

**Key optimizations:**
- Web server profile for many small objects
- Moderate concurrent reads
- Aggressive keep-alive for connection reuse

### Development / Testing

```bash
docker run -d \
  -e RUSTFS_BUFFER_PROFILE=GeneralPurpose \
  -e RUSTFS_OBS_LOGGER_LEVEL=debug \
  --memory=4g \
  rustfs/rustfs:latest
```

**Key optimizations:**
- Default balanced profile
- Debug logging for troubleshooting
- Lower memory requirements

## Advanced Tuning

### Custom Workload Profile

Create custom configuration for specific workloads:

```bash
# Example: High-throughput video streaming
docker run -d \
  -e RUSTFS_BUFFER_PROFILE=DataLake \
  -e RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=128 \
  -e RUSTFS_OBJECT_HIGH_CONCURRENCY_THRESHOLD=32 \
  -e RUSTFS_H2_INITIAL_STREAM_WINDOW_SIZE=16777216 \
  -e RUSTFS_H2_INITIAL_CONN_WINDOW_SIZE=33554432 \
  -e RUSTFS_H2_MAX_CONCURRENT_STREAMS=8192 \
  -e RUSTFS_OBJECT_GET_TIMEOUT=300 \
  --memory=32g \
  --ulimit nofile=65536:65536 \
  rustfs/rustfs:latest
```

### Memory-Constrained Environments

```bash
docker run -d \
  -e RUSTFS_BUFFER_PROFILE=WebServer \
  -e RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=16 \
  -e RUSTFS_OBJECT_HIGH_CONCURRENCY_THRESHOLD=4 \
  -e RUSTFS_H2_MAX_CONCURRENT_STREAMS=512 \
  --memory=2g \
  --memory-swap=2g \
  rustfs/rustfs:latest
```

### Multi-Tenant Optimization

For environments serving multiple tenants:

```bash
docker run -d \
  -e RUSTFS_BUFFER_PROFILE=GeneralPurpose \
  -e RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=64 \
  -e RUSTFS_CONSOLE_RATE_LIMIT_ENABLE=true \
  -e RUSTFS_CONSOLE_RATE_LIMIT_RPM=100 \
  --memory=16g \
  rustfs/rustfs:latest
```

## Performance Troubleshooting

### Identify Bottlenecks

#### CPU Bound

**Symptoms:** High CPU usage, slow request processing

**Diagnosis:**
```bash
docker stats rustfs --no-stream
# Look for high %CPU

curl http://localhost:9000/metrics | grep rustfs_concurrent_requests
# Many concurrent requests with high latency
```

**Solutions:**
- Increase CPU allocation
- Reduce concurrency thresholds
- Optimize buffer profile

#### Memory Bound

**Symptoms:** OOM kills, swap usage, slow performance

**Diagnosis:**
```bash
docker stats rustfs --no-stream
# Look for MEM% near limit

dmesg | grep -i 'killed process'
# Check for OOM killer
```

**Solutions:**
- Increase memory allocation
- Use WebServer buffer profile
- Reduce concurrent operations

#### I/O Bound

**Symptoms:** High disk utilization, slow transfers

**Diagnosis:**
```bash
iostat -xzd 1
# Look for high %util

curl http://localhost:9000/metrics | grep rustfs_io_
# Check I/O throughput vs expectations
```

**Solutions:**
- Upgrade to faster storage (NVMe)
- Increase concurrent disk reads
- Adjust I/O scheduler

#### Network Bound

**Symptoms:** Slow transfers, connection timeouts

**Diagnosis:**
```bash
iftop -P
# Monitor network usage

netstat -s | grep -A5 TCP
# Check for retransmissions
```

**Solutions:**
- Upgrade network (10Gbps+)
- Tune TCP parameters
- Increase HTTP/2 window sizes

### Validate Improvements

After tuning, validate improvements:

```bash
# Run same benchmark before and after
time aws s3 cp largefile s3://bucket/ \
  --endpoint-url http://localhost:9000

# Compare metrics in Grafana
# Check P50/P95/P99 latency improvements
# Verify throughput increases
```

## Best Practices Summary

1. **Match buffer profile to workload**: Don't use DataLake for web serving
2. **Monitor key metrics**: Latency, throughput, error rate
3. **Start with defaults**: Only tune when you have measured bottlenecks
4. **Test changes incrementally**: Change one parameter at a time
5. **Consider hardware limits**: Software tuning can't overcome bad hardware
6. **Use observability**: Enable metrics and tracing for diagnosis
7. **Plan for growth**: Test under expected peak loads
8. **Document configurations**: Keep records of what works for your workload

## Further Reading

- [`05-observability.md`](05-observability.md) - Monitoring and metrics configuration
- [`06-troubleshooting.md`](06-troubleshooting.md) - Performance troubleshooting
- [RustFS Documentation](https://docs.rustfs.com) - Official documentation
- [Performance Benchmarks](https://github.com/rustfs/rustfs#rustfs-vs-minio-performance) - Comparative benchmarks

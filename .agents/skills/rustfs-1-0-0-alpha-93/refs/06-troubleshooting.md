# RustFS Troubleshooting Guide

This reference covers common issues, debugging techniques, log analysis, and recovery procedures for RustFS 1.0.0-alpha.93.

## Quick Diagnostic Commands

### Health Checks

```bash
# S3 API health
curl -f http://localhost:9000/health && echo "OK" || echo "FAILED"

# Console health
curl -f http://localhost:9001/rustfs/console/health && echo "OK" || echo "FAILED"

# Detailed health info
curl http://localhost:9000/minio.health/live | jq .

# Readiness check
curl http://localhost:9000/minio.health/ready | jq .
```

### Service Status

```bash
# Docker container status
docker ps | grep rustfs

# Container logs (last 100 lines)
docker logs --tail 100 rustfs

# Follow logs in real-time
docker logs -f rustfs

# Systemd service status (if installed via script)
systemctl status rustfs
journalctl -u rustfs -n 50
```

### Resource Usage

```bash
# Container resource usage
docker stats rustfs --no-stream

# Check disk usage
df -h /data
du -sh /data/*

# Check network connections
netstat -tlnp | grep -E '9000|9001'
ss -tlnp | grep -E '9000|9001'
```

## Common Issues and Solutions

### Permission Denied on Data Directory

**Symptom:** Container fails to start with "permission denied" errors.

**Cause:** Data directory not owned by UID 10001 (rustfs user in container).

**Solution:**
```bash
# Check current ownership
ls -la /path/to/data

# Change ownership to rustfs user (UID 10001)
sudo chown -R 10001:10001 /path/to/data

# Verify ownership
ls -la /path/to/data

# Restart container
docker restart rustfs
```

**Prevention:** Always set ownership before starting container:
```bash
mkdir -p ~/rustfs/{data,logs}
chown -R 10001:10001 ~/rustfs/{data,logs}
```

### Cannot Connect to Console

**Symptom:** Console UI at port 9001 is unreachable.

**Diagnosis:**
```bash
# Check if console is enabled
docker exec rustfs env | grep RUSTFS_CONSOLE_ENABLE

# Check if port is listening
docker exec rustfs netstat -tlnp | grep 9001

# Check container logs for errors
docker logs rustfs | grep -i console
```

**Solutions:**

1. **Console disabled:**
```bash
# Enable console
docker stop rustfs
docker run -d \
  -e RUSTFS_CONSOLE_ENABLE=true \
  -p 9001:9001 \
  rustfs/rustfs:latest
```

2. **Port not published:**
```bash
# Restart with port mapping
docker stop rustfs && docker rm rustfs
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  rustfs/rustfs:latest
```

3. **Wrong address binding:**
```bash
# Bind to all interfaces
docker run -d \
  -e RUSTFS_CONSOLE_ADDRESS=0.0.0.0:9001 \
  rustfs/rustfs:latest
```

### Connection Refused on S3 API

**Symptom:** S3 clients cannot connect to port 9000.

**Diagnosis:**
```bash
# Check if RustFS is running
docker ps | grep rustfs

# Check port binding
docker port rustfs

# Test from inside container
docker exec rustfs curl -f http://localhost:9000/health

# Test from host
curl -f http://localhost:9000/health
```

**Solutions:**

1. **Container not running:**
```bash
docker start rustfs
```

2. **Firewall blocking port:**
```bash
# Check firewall rules
sudo iptables -L -n | grep 9000

# Add firewall rule (Ubuntu/Debian)
sudo ufw allow 9000/tcp
sudo ufw allow 9001/tcp

# Or (RHEL/CentOS)
sudo firewall-cmd --add-port=9000/tcp --permanent
sudo firewall-cmd --add-port=9001/tcp --permanent
sudo firewall-cmd --reload
```

3. **Wrong endpoint URL:**
```bash
# Verify you're using correct endpoint
# Default: http://localhost:9000
# Not: https://... (unless TLS is configured)
```

### High Memory Usage

**Symptom:** RustFS consuming excessive memory.

**Diagnosis:**
```bash
# Check memory usage
docker stats rustfs --no-stream

# Check buffer profile
docker exec rustfs env | grep RUSTFS_BUFFER_PROFILE

# Check concurrent requests
curl http://localhost:9000/metrics | grep rustfs_concurrent_requests
```

**Solutions:**

1. **Adjust buffer profile:**
```bash
# For lower memory usage
docker stop rustfs
docker run -d \
  -e RUSTFS_BUFFER_PROFILE=WebServer \
  --memory=4g \
  rustfs/rustfs:latest
```

2. **Limit concurrent operations:**
```bash
docker run -d \
  -e RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=32 \
  -e RUSTFS_OBJECT_HIGH_CONCURRENCY_THRESHOLD=4 \
  rustfs/rustfs:latest
```

3. **Set memory limits:**
```bash
docker run -d \
  --memory=8g \
  --memory-swap=8g \
  rustfs/rustfs:latest
```

### Slow Performance

**Symptom:** Uploads/downloads are slower than expected.

**Diagnosis:**
```bash
# Check I/O metrics
curl http://localhost:9000/metrics | grep rustfs_io_

# Check request latency
curl http://localhost:9000/metrics | grep rustfs_request_duration

# Monitor disk I/O
iostat -x 1

# Check network throughput
iftop -P
```

**Solutions:**

1. **Optimize buffer profile for workload:**
```bash
# For data lake / large files
docker run -d \
  -e RUSTFS_BUFFER_PROFILE=DataLake \
  rustfs/rustfs:latest

# For many small objects
docker run -d \
  -e RUSTFS_BUFFER_PROFILE=WebServer \
  rustfs/rustfs:latest
```

2. **Increase concurrent disk reads (for SSDs):**
```bash
docker run -d \
  -e RUSTFS_OBJECT_MAX_CONCURRENT_DISK_READS=128 \
  rustfs/rustfs:latest
```

3. **Use HTTP/2 tuning:**
```bash
docker run -d \
  -e RUSTFS_H2_INITIAL_STREAM_WINDOW_SIZE=8388608 \
  -e RUSTFS_H2_MAX_CONCURRENT_STREAMS=4096 \
  rustfs/rustfs:latest
```

4. **Check disk performance:**
```bash
# Test disk speed inside container
docker exec rustfs dd if=/dev/zero of=/data/test bs=1M count=1024 oflag=direct
rm /data/test
```

### Authentication Failures

**Symptom:** "Access Denied" or "Signature Does Not Match" errors.

**Diagnosis:**
```bash
# Check configured credentials
docker exec rustfs env | grep RUSTFS_ACCESS_KEY
docker exec rustfs env | grep RUSTFS_SECRET_KEY

# Test with curl
curl -u rustfsadmin:rustfsadmin http://localhost:9000/listbuckets
```

**Solutions:**

1. **Verify credentials match:**
```bash
# Ensure client uses same credentials as server
aws s3api list-buckets \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin
```

2. **Check for custom credentials:**
```bash
# If you set custom credentials, use those
docker exec rustfs env | grep -E 'RUSTFS_(ACCESS|SECRET)_KEY'

# Update client configuration accordingly
aws s3api list-buckets \
  --endpoint-url http://localhost:9000 \
  --access-key <actual-access-key> \
  --secret-access-key <actual-secret-key>
```

3. **Time synchronization:**
```bash
# S3 signatures require synchronized time
date
# If time is wrong, sync it:
sudo ntpdate pool.ntp.org
# Or enable chronyd/ntpd
```

### TLS/SSL Issues

**Symptom:** TLS handshake failures or certificate errors.

**Diagnosis:**
```bash
# Check TLS configuration
docker exec rustfs env | grep RUSTFS_TLS

# Test TLS connection
curl -kv https://localhost:9000/health

# Check certificate files
ls -la /path/to/tls/
```

**Solutions:**

1. **Self-signed certificate (development only):**
```bash
# Generate self-signed cert
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls/rustfs_key.pem \
  -out tls/rustfs_cert.pem \
  -subj "/CN=localhost/O=RustFS/C=US"

# Mount TLS directory
docker run -d \
  -v $(pwd)/tls:/opt/tls:ro \
  -e RUSTFS_TLS_PATH=/opt/tls \
  rustfs/rustfs:latest

# Test with insecure flag (dev only)
curl -k https://localhost:9000/health
```

2. **Trust system CAs:**
```bash
docker run -d \
  -e RUSTFS_TRUST_SYSTEM_CA=true \
  rustfs/rustfs:latest
```

3. **Enable TLS key logging (debugging):**
```bash
docker run -d \
  -e RUSTFS_TLS_KEYLOG=1 \
  rustfs/rustfs:latest

# View TLS keys in logs
docker logs rustfs | grep TLS
```

### Data Corruption / Bitrot

**Symptom:** Objects return incorrect data or checksum errors.

**Diagnosis:**
```bash
# Check for bitrot detections
curl http://localhost:9000/metrics | grep rustfs_bitrot

# Run heal scan (dry run)
mc admin heal myrustfs --recursive --dry-run

# Check heal metrics
curl http://localhost:9000/metrics | grep rustfs_heal
```

**Solutions:**

1. **Run healing operation:**
```bash
# Using mc
mc admin heal myrustfs --recursive

# Or via API
curl -X POST "http://localhost:9000/minio/admin/v3/heal" \
  -d '{"mode":"full","recursive":true}' \
  -H "Authorization: AWS rustfsadmin:rustfsadmin"
```

2. **Enable bitrot verification:**
```bash
# Ensure bitrot verification is enabled (default)
docker exec rustfs env | grep RUSTFS_OBJECT_GET_SKIP_BITROT_VERIFY
# Should be empty or false

# If disabled, re-enable it
docker run -d \
  -e RUSTFS_OBJECT_GET_SKIP_BITROT_VERIFY=false \
  rustfs/rustfs:latest
```

3. **Check disk health:**
```bash
# Run SMART diagnostics
smartctl -a /dev/sda

# Check for I/O errors
dmesg | grep -i 'i/o error'
```

### Container Crash Loop

**Symptom:** Container repeatedly restarts.

**Diagnosis:**
```bash
# Check container status
docker ps -a | grep rustfs

# View last logs
docker logs rustfs --tail 200

# Check exit code
docker inspect rustfs | grep -A5 State

# Inspect resource limits
docker inspect rustfs | grep -i memory
```

**Solutions:**

1. **Check for OOM kills:**
```bash
# View system logs
dmesg | grep -i 'killed process'

# Increase memory limit
docker stop rustfs && docker rm rustfs
docker run -d \
  --memory=8g \
  --memory-swap=8g \
  rustfs/rustfs:latest
```

2. **Check data directory permissions:**
```bash
sudo chown -R 10001:10001 /path/to/data
docker restart rustfs
```

3. **Check disk space:**
```bash
df -h /data

# If full, clean up space or expand volume
```

4. **Run without data directory (test):**
```bash
# Test if it's data-related
docker run --rm rustfs/rustfs:latest /tmp/test/{0..3}
# If this works, issue is with data directory
```

## Log Analysis

### Log Levels and Output

```bash
# Change log level to debug for troubleshooting
docker stop rustfs && docker rm rustfs
docker run -d \
  -e RUSTFS_OBS_LOGGER_LEVEL=debug \
  rustfs/rustfs:latest

# View logs
docker logs -f rustfs
```

### Search Logs for Errors

```bash
# Find all errors
docker logs rustfs | grep -i error

# Find specific error patterns
docker logs rustfs | grep -i "permission denied"
docker logs rustfs | grep -i "connection refused"
docker logs rustfs | grep -i "timeout"

# Count error types
docker logs rustfs | grep -i error | sort | uniq -c | sort -rn
```

### Structured Log Format

RustFS logs are structured with the following fields:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "message": "Request completed",
  "method": "PUT",
  "path": "/my-bucket/my-object",
  "duration_ms": 45,
  "size_bytes": 1024,
  "status_code": 200
}
```

### Log Rotation

For file-based logging, configure logrotate:

**/etc/logrotate.d/rustfs:**
```bash
/var/log/rustfs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    size 100M
    create 0644 rustfs rustfs
}
```

## Performance Debugging

### Profile Request Latency

```bash
# Get latency metrics
curl http://localhost:9000/metrics | grep rustfs_request_duration_seconds

# Parse histogram data
curl http://localhost:9000/metrics | \
  grep 'rustfs_request_duration_seconds_bucket' | \
  awk -F',' '{print $2, $3}'

# Calculate percentiles in Grafana or Prometheus
```

### Monitor I/O Performance

```bash
# Check I/O metrics
curl http://localhost:9000/metrics | grep rustfs_io_

# Real-time disk I/O monitoring
iostat -xzd 1

# Monitor specific disk
iotop -oPa
```

### Network Debugging

```bash
# Check network statistics
netstat -s | grep -A5 TCP

# Monitor connections
ss -s

# Trace network path
traceroute localhost:9000

# Capture packets (if needed)
tcpdump -i any port 9000 -w rustfs.pcap
```

### CPU Profiling

```bash
# Check CPU usage
docker stats rustfs --no-stream

# Enable pprof endpoint (development only)
docker run -d \
  -p 6060:6060 \
  -e RUSTFS_PROFILER_ENABLE=true \
  rustfs/rustfs:latest

# Access profiler at http://localhost:6060/debug/pprof/
```

## Recovery Procedures

### Backup and Restore

#### Backup Buckets

```bash
# Using mc mirror
mc mirror myrustfs/source-bucket backup-bucket

# Or using AWS CLI
aws s3 sync s3://source-bucket s3://backup-bucket \
  --endpoint-url http://localhost:9000
```

#### Restore from Backup

```bash
# Restore specific bucket
mc mirror backup-bucket myrustfs/restored-bucket

# Or restore entire instance
mc mirror --overwrite backup-rustfs/ rustfs/
```

### Migrate Data to New Instance

```bash
# Using mc (fastest for large datasets)
mc alias set source http://old-rustfs:9000 rustfsadmin rustfsadmin
mc alias set dest http://new-rustfs:9000 rustfsadmin rustfsadmin
mc mirror --overwrite source/ dest/

# Using AWS CLI (supports multipart)
aws s3 sync s3://source-bucket s3://dest-bucket \
  --endpoint-url http://old-rustfs:9000 \
  --multipart-upload-threshold 64MB
```

### Emergency Stop and Start

```bash
# Graceful shutdown
docker stop rustfs

# Force stop (if graceful fails)
docker stop -t 0 rustfs

# Clean restart
docker stop rustfs && docker rm rustfs
docker run -d --name rustfs rustfs/rustfs:latest

# Restart with same configuration
docker-compose restart rustfs
```

### Heal After Node Failure

```bash
# Check heal status
mc admin info myrustfs

# Trigger full heal
mc admin heal myrustfs --recursive

# Heal specific bucket
mc admin heal myrustfs/my-bucket --recursive

# Preview what would be healed
mc admin heal myrustfs --recursive --dry-run
```

## Kubernetes Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl get pods -n rustfs

# View pod logs
kubectl logs -n rustfs rustfs-xxxxx

# Describe pod for events
kubectl describe pod -n rustfs rustfs-xxxxx

# Check persistent volume
kubectl get pvc -n rustfs
kubectl describe pvc -n rustfs rustfs-data
```

### Service Not Accessible

```bash
# Check service
kubectl get svc -n rustfs

# Check endpoints
kubectl get endpoints -n rustfs

# Test from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  curl -f http://rustfs:9000/health

# Check ingress (if using)
kubectl get ingress -n rustfs
kubectl describe ingress -n rustfs rustfs
```

### Resource Issues

```bash
# Check resource usage
kubectl top pods -n rustfs

# Scale deployment
kubectl scale deployment rustfs --replicas=3 -n rustfs

# Update resource limits
kubectl set resources deployment rustfs \
  --limits=memory=8Gi,cpu=4000m \
  --requests=memory=4Gi,cpu=2000m \
  -n rustfs
```

## Support and Escalation

### Before Opening an Issue

1. **Check existing issues**: https://github.com/rustfs/rustfs/issues
2. **Review documentation**: https://docs.rustfs.com
3. **Gather diagnostic information**:
   ```bash
   # Version info
   rustfs version
   
   # Environment
   docker exec rustfs env | grep RUSTFS
   
   # Logs (last 500 lines)
   docker logs rustfs --tail 500 > rustfs-logs.txt
   
   # Metrics snapshot
   curl http://localhost:9000/metrics > rustfs-metrics.txt
   ```

4. **Create minimal reproduction**: Document exact steps to reproduce the issue

### Where to Get Help

- **Bug reports**: https://github.com/rustfs/rustfs/issues
- **Questions and discussions**: https://github.com/rustfs/rustfs/discussions
- **FAQ**: https://github.com/rustfs/rustfs/discussions/categories/q-a
- **Email (business)**: hello@rustfs.com

### Issue Template

```markdown
**Description:**
[Brief description of the issue]

**Environment:**
- RustFS version: 1.0.0-alpha.93
- Deployment method: Docker/Podman/Kubernetes/Binary
- OS: [Your OS and version]
- Container runtime: [Docker/Podman version]

**Steps to Reproduce:**
1. [First step]
2. [Second step]
3. [Expected vs actual behavior]

**Logs:**
[Relevant log excerpts]

**Configuration:**
[Environment variables or config files, redact secrets]

**Additional Context:**
[Any other relevant information]
```

## Performance Tuning Reference

For performance optimization beyond troubleshooting, see [`07-performance.md`](07-performance.md).

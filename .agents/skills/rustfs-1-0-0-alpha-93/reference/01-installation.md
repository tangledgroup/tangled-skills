# RustFS Installation Guide

This reference covers all installation methods for RustFS 1.0.0-alpha.93, including deployment patterns and best practices.

## Quick Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **One-click installer** | Quick setup on Linux | Automatic, systemd integration | Linux only |
| **Docker/Podman** | Development, testing | Isolated, easy cleanup | Requires container runtime |
| **Docker Compose** | Full stack with observability | All-in-one, pre-configured monitoring | More complex |
| **Helm/Kubernetes** | Production clusters | Scalable, HA, managed | Requires K8s cluster |
| **Nix Flake** | Reproducible builds | Declarative, version pinning | Requires Nix |
| **Binary download** | Custom deployments | Full control, no dependencies | Manual setup |

## Method 1: One-Click Installer (Linux)

### Installation

```bash
# Download and run installer
curl -O https://rustfs.com/install_rustfs.sh && bash install_rustfs.sh

# Or with wget
wget https://rustfs.com/install_rustfs.sh && bash install_rustfs.sh
```

The installer:
- Downloads latest release binary to `/opt/rustfs`
- Creates systemd service `rustfs.service`
- Sets up default data directory `/var/lib/rustfs`
- Starts the service automatically

### Verify Installation

```bash
# Check service status
systemctl status rustfs

# View logs
journalctl -u rustfs -f

# Check if ports are listening
netstat -tlnp | grep -E '9000|9001'
```

### Configuration

Edit `/etc/rustfs/rustfs.env` before starting:

```bash
# Edit configuration
sudo nano /etc/rustfs/rustfs.env

# Restart service
sudo systemctl restart rustfs
```

### Uninstall

```bash
# Stop and disable service
sudo systemctl stop rustfs
sudo systemctl disable rustfs

# Remove binary and config
sudo rm -rf /opt/rustfs /etc/rustfs /var/lib/rustfs

# Remove systemd unit
sudo rm /etc/systemd/system/rustfs.service
sudo systemctl daemon-reload
```

## Method 2: Docker/Podman Single Container

### Prerequisites

- Docker 20.10+ or Podman 4.0+
- At least 4GB RAM
- Directory for data persistence

### Quick Start

```bash
# Create directories
mkdir -p ~/rustfs/{data,logs}
cd ~/rustfs

# Set ownership (UID 10001 is rustfs user in container)
chown -R 10001:10001 data logs

# Run with Docker
docker run -d \
  --name rustfs \
  -p 9000:9000 \
  -p 9001:9001 \
  -v $(pwd)/data:/data \
  -v $(pwd)/logs:/logs \
  -e RUSTFS_VOLUMES=/data/rustfs{0..3} \
  -e RUSTFS_ACCESS_KEY=myaccesskey123 \
  -e RUSTFS_SECRET_KEY=mysecretkey123456 \
  rustfs/rustfs:1.0.0-alpha.93

# Or with Podman (rootless)
podman run -d \
  --name rustfs \
  -p 9000:9000 \
  -p 9001:9001 \
  -v $(pwd)/data:/data \
  -v $(pwd)/logs:/logs \
  -e RUSTFS_VOLUMES=/data/rustfs{0..3} \
  -e RUSTFS_ACCESS_KEY=myaccesskey123 \
  -e RUSTFS_SECRET_KEY=mysecretkey123456 \
  rustfs/rustfs:1.0.0-alpha.93
```

### Access Points

- **S3 API**: `http://localhost:9000`
- **Console UI**: `http://localhost:9001` (login: `myaccesskey123` / `mysecretkey123456`)

### Stop and Remove

```bash
# Stop container
docker stop rustfs
# or
podman stop rustfs

# Remove container (data preserved in volume)
docker rm rustfs
# or
podman rm rustfs
```

## Method 3: Docker Compose with Observability

### Complete docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Main RustFS service
  rustfs:
    image: rustfs/rustfs:1.0.0-alpha.93
    container_name: rustfs-server
    security_opt:
      - "no-new-privileges:true"
    ports:
      - "9000:9000"  # S3 API
      - "9001:9001"  # Console
    environment:
      - RUSTFS_VOLUMES=/data/rustfs{0..3}
      - RUSTFS_ADDRESS=0.0.0.0:9000
      - RUSTFS_CONSOLE_ADDRESS=0.0.0.0:9001
      - RUSTFS_CONSOLE_ENABLE=true
      - RUSTFS_CORS_ALLOWED_ORIGINS=*
      - RUSTFS_CONSOLE_CORS_ALLOWED_ORIGINS=*
      - RUSTFS_ACCESS_KEY=rustfsadmin
      - RUSTFS_SECRET_KEY=rustfsadmin
      - RUSTFS_OBS_LOGGER_LEVEL=info
      - RUSTFS_OBS_ENDPOINT=http://otel-collector:4318
      - RUSTFS_TLS_PATH=/opt/tls
    volumes:
      - ./data/pro:/data
      - ./logs:/app/logs
      - ./tls:/opt/tls:ro  # Optional: TLS certificates
    networks:
      - rustfs-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "sh", "-c", "curl -f http://127.0.0.1:9000/health && curl -f http://127.0.0.1:9001/rustfs/console/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      otel-collector:
        condition: service_started
        required: false

  # OpenTelemetry Collector
  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.115.0
    container_name: otel-collector
    command: ["--config=/etc/otelcol-contrib/otel-collector.yml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otelcol-contrib/otel-collector.yml:ro
    ports:
      - "1888:1888"   # pprof
      - "8888:8888"   # Prometheus metrics for Collector
      - "8889:8889"   # Prometheus metrics for app indicators
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
    networks:
      - rustfs-network
    restart: unless-stopped
    profiles:
      - observability

  # Prometheus for metrics storage
  prometheus:
    image: prom/prometheus:v2.52.0
    container_name: prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--web.enable-lifecycle"
    volumes:
      - ./prometheus.yaml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - rustfs-network
    restart: unless-stopped
    profiles:
      - observability

  # Grafana for visualization
  grafana:
    image: grafana/grafana:11.2.0
    container_name: grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./grafana/datasources:/etc/grafana/provisioning/datasources:ro
    ports:
      - "3000:3000"
    networks:
      - rustfs-network
    restart: unless-stopped
    depends_on:
      - prometheus
    profiles:
      - observability

  # Tempo for trace storage
  tempo-init:
    image: busybox:latest
    container_name: tempo-init
    user: root
    command: ["sh", "-c", "chown -R 10001:10001 /var/tempo"]
    volumes:
      - tempo_data:/var/tempo
    networks:
      - rustfs-network
    restart: "no"
    profiles:
      - observability

  tempo:
    image: grafana/tempo:2.5.1
    container_name: tempo
    user: "10001"
    command: ["-config.file=/etc/tempo.yaml"]
    volumes:
      - ./tempo.yaml:/etc/tempo.yaml:ro
      - tempo_data:/var/tempo
    ports:
      - "3200:3200"  # Tempo
      - "4317"       # OTLP gRPC
      - "4318"       # OTLP HTTP
    networks:
      - rustfs-network
    restart: unless-stopped
    profiles:
      - observability

  # Jaeger for trace visualization (alternative to Tempo)
  jaeger:
    image: jaegertracing/all-in-one:1.68.0
    container_name: jaeger
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"
      - "14268:14268"
    networks:
      - rustfs-network
    restart: unless-stopped
    profiles:
      - observability

volumes:
  prometheus_data:
  grafana_data:
  tempo_data:

networks:
  rustfs-network:
    driver: bridge
```

### Supporting Configuration Files

**otel-collector-config.yaml:**
```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
  otlp:
    endpoints:
      - tempo:4317
      - jaeger:4317
    tls:
      insecure: true

service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp]
```

**prometheus.yaml:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'rustfs'
    static_configs:
      - targets: ['rustfs:9000']
    metrics_path: '/metrics'

  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8888']

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

**tempo.yaml:**
```yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        http:
          endpoint: 0.0.0.0:4318
        grpc:
          endpoint: 0.0.0.0:4317

ingester:
  max_block_duration: 5m

storage:
  trace:
    backend: local
    wal:
      path: /var/tempo/wal
    local:
      path: /var/tempo/blocks

traceserver:
  http_server:
    http_listen_port: 14268
```

### Deployment

```bash
# Create directory structure
mkdir -p data logs tls grafana/{dashboards,datasources}

# Set permissions
chown -R 10001:10001 data

# Start with observability
docker compose --profile observability up -d

# Or without observability (RustFS only)
docker compose up -d rustfs

# View logs
docker compose logs -f rustfs

# Check status
docker compose ps
```

## Method 4: Kubernetes with Helm

### Prerequisites

- Kubernetes cluster 1.25+
- Helm 3.10+
- Persistent Volume provisioner (e.g., Longhorn, Rook-Ceph, or cloud storage)

### Installation

```bash
# Add RustFS Helm repository
helm repo add rustfs https://charts.rustfs.com
helm repo update

# Create namespace
kubectl create namespace rustfs

# Install with default values
helm install rustfs rustfs/rustfs \
  --namespace rustfs

# Install with custom values
helm install rustfs rustfs/rustfs \
  --namespace rustfs \
  -f custom-values.yaml
```

### Custom Values Example

**custom-values.yaml:**
```yaml
replicaCount: 3

service:
  type: LoadBalancer
  port: 9000
  consolePort: 9001

persistence:
  enabled: true
  size: 100Gi
  storageClass: "longhorn"
  accessMode: ReadWriteOnce

environment:
  RUSTFS_ACCESS_KEY: "rustfsadmin"
  RUSTFS_SECRET_KEY: "rustfsadmin"
  RUSTFS_CONSOLE_ENABLE: "true"
  RUSTFS_OBS_LOGGER_LEVEL: "info"

resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "8Gi"
    cpu: "4000m"

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: rustfs
          topologyKey: kubernetes.io/hostname

ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: s3.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: rustfs-tls
      hosts:
        - s3.example.com

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    namespace: rustfs
```

### Upgrade and Uninstall

```bash
# Upgrade existing installation
helm upgrade rustfs rustfs/rustfs \
  --namespace rustfs \
  -f custom-values.yaml

# Uninstall
helm uninstall rustfs --namespace rustfs

# Remove namespace (after uninstall)
kubectl delete namespace rustfs
```

## Method 5: Nix Flake

### Prerequisites

- Nix 2.4+ with flakes enabled
- Enable flakes in `/etc/nix/nix.conf`:
  ```
  experimental-features = nix-command flakes
  ```

### Usage

```bash
# Run without installing (uses latest from GitHub)
nix run github:rustfs/rustfs

# Build binary locally
nix build github:rustfs/rustfs
./result/bin/rustfs --help

# Install to profile
nix profile install github:rustfs/rustfs

# From local checkout
cd rustfs
nix build
nix run

# Specific version
nix run github:rustfs/rustfs/1.0.0-alpha.93
```

### Custom Nix Expression

**flake.nix:**
```nix
{
  description = "RustFS development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    rustfs.url = "github:rustfs/rustfs/1.0.0-alpha.93";
  };

  outputs = { self, nixpkgs, rustfs }: {
    packages.x86_64-linux.rustfs = rustfs.packages.x86_64-linux.default;
    
    devShells.x86_64-linux.default = nixpkgs.lib.mkDefault nixpkgs.lib.genAttrs ["x86_64-linux"] (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in pkgs.mkShell {
        packages = [
          rustfs.packages.${system}.default
          pkgs.awscli2
          pkgs.minio-client
        ];
      });
  };
}
```

## Method 6: Binary Download

### Manual Installation

```bash
# Download binary
ARCH=$(uname -m)
case $ARCH in
  x86_64) ARCH_SUBSTR="x86_64-musl" ;;
  aarch64|arm64) ARCH_SUBSTR="aarch64-musl" ;;
  *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

TAG="1.0.0-alpha.93"
URL="https://api.github.com/repos/rustfs/rustfs/releases/tags/$TAG"

# Find and download the correct binary
BINARY_URL=$(curl -s "$URL" | \
  grep -o "\"browser_download_url\": \"[^\"]*${ARCH_SUBSTR}[^\"]*\\.zip\"" | \
  cut -d'"' -f4 | head -n 1)

curl -fL "$BINARY_URL" -o rustfs.zip
unzip rustfs.zip
chmod +x rustfs

# Move to PATH
sudo mv rustfs /usr/local/bin/

# Verify
rustfs --version
```

### Create Systemd Service

**/etc/systemd/system/rustfs.service:**
```ini
[Unit]
Description=RustFS Object Storage
After=network.target

[Service]
Type=simple
User=rustfs
Group=rustfs
ExecStart=/usr/local/bin/rustfs /var/lib/rustfs/{0..3}
Restart=always
RestartSec=5s
EnvironmentFile=-/etc/rustfs/rustfs.env

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/rustfs /var/log/rustfs

[Install]
WantedBy=multi-user.target
```

**/etc/rustfs/rustfs.env:**
```bash
RUSTFS_ADDRESS=:9000
RUSTFS_CONSOLE_ADDRESS=:9001
RUSTFS_CONSOLE_ENABLE=true
RUSTFS_ACCESS_KEY=rustfsadmin
RUSTFS_SECRET_KEY=rustfsadmin
RUSTFS_OBS_LOGGER_LEVEL=info
```

### Start Service

```bash
# Create user and directories
sudo useradd -r -s /bin/false -d /var/lib/rustfs rustfs
sudo mkdir -p /var/lib/rustfs/{0..3} /var/log/rustfs
sudo chown -R rustfs:rustfs /var/lib/rustfs /var/log/rustfs

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable rustfs
sudo systemctl start rustfs

# Check status
sudo systemctl status rustfs
```

## Development Setup

### Build from Source

```bash
# Clone repository
git clone https://github.com/rustfs/rustfs.git
cd rustfs
git checkout 1.0.0-alpha.93

# Build binary
cargo build --release

# Binary location
./target/release/rustfs

# Run directly
cargo run -- /tmp/rustfs/{0..3}
```

### Docker Development Environment

```bash
# Build development image
docker build -t rustfs/rustfs:devenv \
  --target dev \
  -f Dockerfile.source \
  .

# Run with source code mounted
docker run -it \
  -p 9010:9000 \
  -p 9011:9001 \
  -v $(pwd):/app \
  -v cargo_registry:/usr/local/cargo/registry \
  rustfs/rustfs:devenv
```

### Build Multi-Architecture Images

```bash
# Install buildx
docker buildx create --name rustfs-builder --use

# Build for multiple architectures
./docker-buildx.sh --build-arg RELEASE=1.0.0-alpha.93

# Build and push to registry
./docker-buildx.sh --push

# Custom registry
./docker-buildx.sh \
  --registry your-registry.com \
  --namespace yourname \
  --release v1.0.0 \
  --push
```

## Post-Installation Verification

### Health Checks

```bash
# S3 API health
curl -f http://localhost:9000/health

# Console health
curl -f http://localhost:9001/rustfs/console/health

# Info endpoint
curl http://localhost:9000/minio.health/live
```

### Test S3 Connectivity

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure for RustFS
aws s3api create-bucket \
  --bucket test-bucket \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# Upload test file
echo "test" > test.txt
aws s3 cp test.txt s3://test-bucket/test.txt \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin

# Verify
aws s3 cp s3://test-bucket/test.txt - \
  --endpoint-url http://localhost:9000 \
  --access-key rustfsadmin \
  --secret-access-key rustfsadmin
```

## Migration from Other Systems

### From MinIO

RustFS is designed to be MinIO-compatible. Most configurations can be directly migrated:

```bash
# MinIO environment variables work with RustFS
# Just change the image name in docker-compose.yml
# minio/minio:latest → rustfs/rustfs:1.0.0-alpha.93

# MC client works identically
mc alias set myminio http://localhost:9000 minioadmin minioadmin
# becomes
mc alias set myrustfs http://localhost:9000 rustfsadmin rustfsadmin
```

### From AWS S3

Update endpoint URL and credentials in your applications:

```python
# Before (AWS S3)
s3 = boto3.client('s3')

# After (RustFS)
s3 = boto3.client(
    's3',
    endpoint_url='http://rustfs:9000',
    aws_access_key_id='rustfsadmin',
    aws_secret_access_key='rustfsadmin'
)
```

## Troubleshooting Installation

See [`06-troubleshooting.md`](06-troubleshooting.md) for common issues and solutions.

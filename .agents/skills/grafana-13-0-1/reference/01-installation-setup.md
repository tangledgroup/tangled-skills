# Installation and Setup

## Contents
- Supported Operating Systems
- Hardware Requirements
- Installation Methods
- Configuration (grafana.ini)
- Docker Deployment

## Supported Operating Systems

Grafana supports:
- **Debian/Ubuntu** — via APT repository, `.deb` package, or binary tarball
- **RHEL/Fedora** — via YUM/DNF repository, `.rpm` package, or binary tarball
- **SUSE/openSUSE** — via binary tarball
- **macOS** — via Homebrew (`brew install grafana`) or binary download
- **Windows** — via MSI installer or binary zip

Installation on other OSes is possible but not supported.

## Hardware Requirements

| Resource | Minimum | Notes |
|----------|---------|-------|
| Memory | 512 MB | More needed for heavy dashboard use or many alert rules |
| CPU | 1 core | Alert evaluation and concurrent users drive CPU load |

Four factors drive resource needs:
1. **Concurrent users** — active browser sessions issuing queries; primary driver of CPU/memory
2. **Alert rules** — background evaluation load; high rule counts with short intervals saturate CPU
3. **Dashboard complexity** — panels with many queries or long time ranges increase load
4. **Data source latency** — slow backends hold connections longer

In Grafana OSS, the alert engine runs in the same process as the UI and data source proxy, so alert CPU saturation directly competes with dashboard query performance.

## Installation Methods

### Debian/Ubuntu (APT)

```bash
# Add Grafana APT repository
sudo apt-get install -y apt-transport-https software-properties-common
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /usr/share/keyrings/grafana.gpg > /dev/null
echo "deb [signed-with=/usr/share/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Install
sudo apt-get update
sudo apt-get install grafana

# Start service
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

Configuration file is at `/etc/grafana/grafana.ini`.

### RHEL/Fedora (YUM)

```bash
# Add Grafana YUM repository
sudo vim /etc/yum.repos.d/grafana.repo
```

Add:
```ini
[grafana]
name=grafana
baseurl=https://rpm.grafana.com
repo_gpgcheck=1
enabled=1
gpgkey=https://rpm.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
```

```bash
sudo yum install grafana
sudo systemctl enable --now grafana-server
```

### Binary Tarball (any Linux)

```bash
wget https://dl.grafana.com/oss/release/grafana-13.0.1-linux-amd64.tar.gz
tar -xzf grafana-13.0.1-linux-amd64.tar.gz
cd grafana-13.0.1/
./bin/grafana-server web
```

Configuration file is at `conf/custom.ini` (copy from `conf/sample.ini`).

## Configuration (grafana.ini)

The default configuration is in `<WORKING_DIR>/conf/defaults.ini`. Do not edit it. Create or edit `custom.ini` to override settings. On Debian/RHEL packages, use `/etc/grafana/grafana.ini` directly.

Key sections:

### [server]
```ini
http_port = 3000
domain = localhost
root_url = %(protocol)s://%(domain)s:%(http_port)s/
```

### [database]
```ini
type = sqlite3
path = grafana.db
# For MySQL:
# type = mysql
# host = 127.0.0.1:3306
# name = grafana
# user = root
# password = secret
# For PostgreSQL:
# type = postgres
# host = 127.0.0.1:5432
# name = grafana
# user = root
# password = secret
```

### [security]
```ini
admin_user = admin
admin_password = admin  # change immediately
secret_key = SwQ6wRn9Y51y
disable_gravatar = true
```

### [auth.anonymous]
```ini
enabled = false
org_role = Viewer
```

### [users]
```ini
allow_sign_up = false
auto_assign_org = true
auto_assign_org_role = Editor
```

Configuration can also be set via environment variables using the `GF_` prefix. For example, `GF_SERVER_HTTP_PORT=3000` maps to `[server] http_port`.

## Docker Deployment

Use the `grafana/grafana` image for OSS (starting v12.4.0, `grafana/grafana-oss` is deprecated).

### Basic Run

```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  -v grafana-data:/var/lib/grafana \
  grafana/grafana:13.0.1
```

### With Provisioning

```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v grafana-data:/var/lib/grafana \
  -v /path/to/provisioning:/etc/grafana/provisioning \
  -v /path/to/dashboards:/var/lib/grafana/dashboards \
  grafana/grafana:13.0.1
```

### Docker Compose

```yaml
services:
  grafana:
    image: grafana/grafana:13.0.1
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_INSTALL_PLUGINS: grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana-data:/var/lib/grafana
      - ./provisioning:/etc/grafana/provisioning

volumes:
  grafana-data:
```

### Environment Variable Configuration

All `grafana.ini` settings are available as environment variables with `GF_` prefix and uppercase section/key names:

```bash
GF_SERVER_HTTP_PORT=3000
GF_SERVER_ROOT_URL=http://localhost:3000/
GF_DATABASE_TYPE=sqlite3
GF_DATABASE_PATH=grafana.db
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin
```

### Alpine vs Ubuntu Variants

- **Alpine** (default): smaller image, uses musl libc. Recommended for most deployments.
- **Ubuntu**: use `grafana/grafana:13.0.1-ubuntu` tag if glibc is required.

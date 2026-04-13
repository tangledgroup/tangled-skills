# Troubleshooting Guide

Common issues, debugging techniques, and solutions for podman-compose.

## Container Name Resolution Issues

### Problem: Services Cannot Reach Each Other by Name

**Symptoms:**
```
Connection refused when connecting to http://service-name:port
getaddrinfo ENOTFOUND service-name
```

**Causes:**
1. Missing DNS resolution plugin (CNI networks)
2. Services on different networks
3. Pod not properly created

**Solutions:**

**Option 1: Install podman-dnsname plugin (for CNI networks)**
```bash
# Fedora/RHEL
sudo dnf install podman-dnsname

# Debian/Ubuntu
sudo apt install podman-dnsname

# Verify installation
ls /usr/lib/containers/libnetwork/cni/dnsname*
```

**Option 2: Switch to netavark backend (recommended)**
Netavark has built-in DNS resolution, no plugin needed:
```bash
# Check current network backend
podman info | grep -A 5 "host:"

# Switch to netavark
podman system connection edit default --set-option=network_backend=netavark

# Restart podman (if running as service)
systemctl --user restart podman.socket
```

**Option 3: Verify network configuration**
```bash
# Check if services are on same network
podman-compose ps
podman network ls

# Inspect container network settings
podman inspect <container-id> | grep -A 10 "NetworkSettings"
```

## Permission and SELinux Issues

### Problem: Permission Denied When Mounting Volumes

**Symptoms:**
```
Permission denied when mounting ./data:/app/data
SELinux policy prevents access
```

**Solutions:**

**Option 1: Add SELinux labels to mounts**
```yaml
volumes:
  - ./data:/app/data:Z      # Private unshared content
  - ./shared:/app/shared:z  # Shared content (multiple containers)
```

**Option 2: Disable SELinux for volume (not recommended)**
```bash
# Temporarily set SELinux to permissive
sudo setenforce 0

# Or add :Z flag and fix context
sudo chcon -Rt svirt_sandbox_file_t ./data
```

**Option 3: Use named volumes instead**
```yaml
volumes:
  - my-data:/app/data

volumes:
  my-data:
```

### Problem: Cannot Create Pods (Rootless Mode)

**Symptoms:**
```
Error: permission denied while trying to connect to the Podman socket
Error: cannot start pod: operation not permitted
```

**Solutions:**

**Check rootless mode:**
```bash
# Verify running as non-root user
id

# Check podman info
podman info | grep -i rootless
```

**Ensure cgroups are configured:**
```bash
# Check cgroup version
cat /proc/filesystems | grep cgroup

# For systemd-based systems, ensure user slice exists
systemctl --user status
```

**Fix user namespace configuration:**
```bash
# Create subgid/subuid entries if missing
sudo usermod -aG podman $USER
sudo systemctl --user restart podman.socket
```

## Network Issues

### Problem: Port Binding Fails

**Symptoms:**
```
Error: port 80 is already allocated
Bind: permission denied (ports < 1024)
```

**Solutions:**

**Check for conflicting bindings:**
```bash
# Find what's using the port
ss -tlnp | grep :80
lsof -i :80

# Check other podman containers
podman ps -a --format "{{.Ports}}"
```

**Use different host port:**
```yaml
ports:
  - "8080:80"    # Instead of "80:80"
```

**For privileged ports in rootless mode:**
```bash
# Enable port forwarding with socat or similar
sudo systemctl enable --now podman-port-forwarder.service

# Or use subuid mapping
echo "podman:10000:65536" | sudo tee -a /etc/subuid
```

### Problem: Container Cannot Access External Network

**Symptoms:**
```
Container cannot reach internet
DNS resolution fails for external domains
```

**Solutions:**

**Check DNS configuration:**
```bash
# Test DNS from inside container
podman-compose exec web nslookup google.com

# Check host DNS
cat /etc/resolv.conf
```

**Configure DNS in compose file:**
```yaml
services:
  web:
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

**Check firewall rules:**
```bash
# Check iptables/nftables rules
sudo iptables -L -n -v | grep podman

# For firewalld
sudo firewall-cmd --list-all
```

## Build Issues

### Problem: Image Build Fails

**Symptoms:**
```
Error during build: cannot find Dockerfile
Build context not found
Layer cache error
```

**Solutions:**

**Verify build context:**
```bash
# Check Dockerfile exists
ls -la ./api/Dockerfile

# Verify context directory has necessary files
find ./api -type f | head -20
```

**Clear build cache:**
```bash
podman-compose build --no-cache

# Or clear all podman build cache
podman builder prune -a
```

**Check Dockerfile syntax:**
```bash
# Validate Dockerfile manually
podman build -t test ./api

# Use multi-stage builds for complex applications
```

### Problem: Build Context Too Large

**Symptoms:**
```
Build timeout due to large context
Slow build times
```

**Solutions:**

**Use .dockerignore:**
```bash
# Create .dockerignore in build context
echo "node_modules
.git
*.md
__pycache__
.pytest_cache" > .dockerignore
```

**Optimize Dockerfile:**
```dockerfile
# Use multi-stage builds
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

## Dependency and Startup Issues

### Problem: Services Start in Wrong Order

**Symptoms:**
```
Connection errors during startup
Service fails because dependency not ready
```

**Solutions:**

**Use health checks for dependencies:**
```yaml
services:
  db:
    image: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 10
  
  api:
    depends_on:
      db:
        condition: service_healthy
```

**Add startup delays (not recommended):**
```yaml
services:
  api:
    command: >
      sh -c "sleep 10 && python app.py"
```

**Use wait-for-it pattern:**
```yaml
services:
  api:
    image: myapi
    depends_on:
      - db
    entrypoint: ["/usr/local/bin/wait-for-it.sh", "db:5432", "--", "python", "app.py"]
```

### Problem: Container Exits Immediately

**Symptoms:**
```
Container starts then stops
Exit code 1 or other non-zero codes
No logs visible
```

**Solutions:**

**Check container logs:**
```bash
podman-compose logs --tail 100 <service>
podman logs <container-id>
```

**Inspect container status:**
```bash
podman-compose ps -a
podman inspect <container-id> | grep -A 5 "State"
```

**Run in foreground to see errors:**
```bash
podman-compose up <service>
```

**Check if command is correct:**
```yaml
services:
  web:
    # Ensure CMD or command is valid
    command: ["python", "app.py"]
```

## Podman Integration Issues

### Problem: podman compose vs podman-compose Confusion

**Symptoms:**
```
Command not found: podman compose
Different behavior between podman compose and podman-compose
```

**Explanation:**
- `podman-compose`: Standalone Python script (works with all podman versions)
- `podman compose`: Podman subcommand (requires podman 4.0+, uses external provider)

**Solutions:**

**Use standalone command:**
```bash
# Install podman-compose
pip3 install podman-compose

# Use directly
podman-compose up -d
```

**Configure podman subcommand:**
```bash
# Set the compose provider
export PODMAN_COMPOSE_PROVIDER=/usr/local/bin/podman-compose

# Now use as subcommand
podman compose up -d
```

### Problem: External Command Warning

**Symptoms:**
```
WARN[0000] "podman compose" calls an external provider
```

**Solutions:**

**Disable warning via environment:**
```bash
export PODMAN_COMPOSE_WARNING_LOGS=false
```

**Disable warning in containers.conf:**
```bash
# Edit /etc/containers/containers.conf or ~/.config/containers/containers.conf
[engine]
compose_warning_logs = false
```

## Migration from Docker Compose

### Problem: docker-compose.yml Not Working

**Symptoms:**
```
Unsupported compose file version
Feature not implemented
Different behavior than docker-compose
```

**Solutions:**

**Check compose file version:**
```yaml
# Version is optional in modern compose files
version: "3.8"  # Remove or update to latest supported
```

**Replace Docker-specific features:**
```yaml
# Docker: cgroup parent (not needed in podman)
# Remove: cgroup_parent: ...

# Docker: privileged mode (use capabilities instead)
privileged: true  # Replace with:
cap_add:
  - NET_ADMIN
  - SYS_ADMIN
```

**Adjust volume mounts for rootless:**
```yaml
# Add :Z flag for SELinux systems
volumes:
  - ./data:/app/data:Z
```

### Common docker-compose to podman-compose Differences

| Docker Compose | Podman Compose | Notes |
|---------------|----------------|-------|
| Daemon required | Daemonless | Faster startup, no context transfer |
| root or rootless | Rootless by default | May need volume mount adjustments |
| Docker networks | Podman networks + pods | Pods provide additional isolation |
| `docker-compose up` | `podman-compose up` or `podman compose up` | Both work |
| Docker volumes | Podman volumes | Compatible, but stored in different location |

## Debugging and Diagnostics

### Enable Verbose Logging

```bash
# Verbose mode
podman-compose --verbose up

# Debug podman commands
export PODMAN_COMPOSE_DEBUG=1
podman-compose up
```

### Inspect Running Stack

```bash
# List all containers
podman-compose ps -a

# View pod details
podman pod ps
podman pod inspect <project>_pod

# Check network configuration
podman network ls
podman network inspect <project>_default

# View volume usage
podman volume ls
podman volume inspect <project>_<volume>
```

### Test Service Connectivity

```bash
# Execute command in container
podman-compose exec web curl http://api:3000/health

# Check DNS resolution
podman-compose exec web nslookup api

# Test port binding from host
curl http://localhost:8080
```

### Performance Issues

**Problem: Slow startup times**

**Solutions:**
```bash
# Use image caching
podman-compose pull  # Pull images before build

# Enable parallel builds
podman-compose build --parallel

# Use multi-stage Dockerfiles to reduce image size
```

**Problem: High resource usage**

**Solutions:**
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: "1"
          memory: 512M
        reservations:
          cpus: "0.5"
          memory: 256M
```

## Common Error Messages

### "Cannot connect to Podman socket"

```bash
# Start podman user service
systemctl --user start podman.socket

# Check socket status
systemctl --user status podman.socket

# Verify socket path
echo $XDG_RUNTIME_DIR/podman/podman.sock
```

### "Image not found"

```bash
# Pull image manually
podman pull nginx:alpine

# Check image exists
podman images | grep nginx

# Use --pull flag
podman-compose up --pull
```

### "Port already in use"

```bash
# Find process using port
lsof -i :8080
ss -tlnp | grep 8080

# Kill process or change port mapping
ports:
  - "8081:80"  # Use different host port
```

## Getting Help

### Useful Commands

```bash
# Show all available commands
podman-compose --help

# Show help for specific command
podman-compose up --help

# Check version
podman-compose version

# Validate compose file
podman-compose config --quiet
```

### Resources

- **Official Documentation:** https://docs.podman.io/
- **GitHub Repository:** https://github.com/containers/podman-compose
- **Compose Specification:** https://compose-spec.io/
- **Podman Documentation:** https://podman.io/docs/

### Reporting Issues

When reporting bugs, include:

1. podman-compose version
2. Podman version (`podman --version`)
3. Operating system and version
4. Compose file (if shareable)
5. Exact error message
6. Steps to reproduce

```bash
# Generate diagnostic info
echo "Podman Compose Version:"
podman-compose version

echo "Podman Version:"
podman --version

echo "Podman Info:"
podman info | grep -E "version|os|rootless"
```

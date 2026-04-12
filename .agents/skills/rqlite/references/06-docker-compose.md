# Docker Compose

Running rqlite clusters with Docker Compose for development and production.

## Overview

Docker Compose simplifies running multi-node rqlite clusters by managing containers, networking, and persistent storage in a single configuration file.

## Quick Start

### Single Node (Development)

```yaml
# docker-compose.yml
version: '3'
services:
  rqlite:
    image: rqlite/rqlite:latest
    container_name: rqlite
    ports:
      - "4001:4001"
    volumes:
      - rqlite-data:/rqlite

volumes:
  rqlite-data:
```

**Start the service:**
```bash
docker-compose up -d

# Verify it's running
curl localhost:4001/status

# Connect to shell
docker exec -it rqlite rqlite 127.0.0.1:4001
```

### 3-Node Cluster (Production-Like)

```yaml
# docker-compose.yml
version: '3'
services:
  rqlite1:
    image: rqlite/rqlite:latest
    container_name: rqlite1
    ports:
      - "4001:4001"
      - "4002:4002"
    command: 
      - "-node-id=1"
      - "-http-addr=0.0.0.0:4001"
      - "-raft-addr=0.0.0.0:4002"
    volumes:
      - rqlite1-data:/rqlite
    networks:
      - rqlite-net

  rqlite2:
    image: rqlite/rqlite:latest
    container_name: rqlite2
    ports:
      - "4003:4001"
      - "4004:4002"
    command:
      - "-node-id=2"
      - "-http-addr=0.0.0.0:4001"
      - "-raft-addr=0.0.0.0:4002"
      - "-join=rqlite1:4002"
    volumes:
      - rqlite2-data:/rqlite
    networks:
      - rqlite-net
    depends_on:
      - rqlite1

  rqlite3:
    image: rqlite/rqlite:latest
    container_name: rqlite3
    ports:
      - "4005:4001"
      - "4006:4002"
    command:
      - "-node-id=3"
      - "-http-addr=0.0.0.0:4001"
      - "-raft-addr=0.0.0.0:4002"
      - "-join=rqlite1:4002"
    volumes:
      - rqlite3-data:/rqlite
    networks:
      - rqlite-net
    depends_on:
      - rqlite1

volumes:
  rqlite1-data:
  rqlite2-data:
  rqlite3-data:

networks:
  rqlite-net:
    driver: bridge
```

**Start the cluster:**
```bash
docker-compose up -d

# Check cluster status
curl localhost:4001/status

# View all nodes
docker exec rqlite1 rqlite 127.0.0.1:4001 ".nodes"
```

## Production Configuration

### With Health Checks and Auto-Restart

```yaml
version: '3'
services:
  rqlite1:
    image: rqlite/rqlite:latest
    container_name: rqlite1
    restart: unless-stopped
    ports:
      - "4001:4001"
      - "4002:4002"
    command:
      - "-node-id=1"
      - "-http-addr=0.0.0.0:4001"
      - "-raft-addr=0.0.0.0:4002"
      - "-raft-badger"  # Use Badger for Raft storage (better performance)
    volumes:
      - rqlite1-data:/rqlite
    networks:
      - rqlite-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4001/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  rqlite2:
    image: rqlite/rqlite:latest
    container_name: rqlite2
    restart: unless-stopped
    ports:
      - "4003:4001"
      - "4004:4002"
    command:
      - "-node-id=2"
      - "-http-addr=0.0.0.0:4001"
      - "-raft-addr=0.0.0.0:4002"
      - "-join=rqlite1:4002"
      - "-raft-badger"
    volumes:
      - rqlite2-data:/rqlite
    networks:
      - rqlite-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4001/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  rqlite3:
    image: rqlite/rqlite:latest
    container_name: rqlite3
    restart: unless-stopped
    ports:
      - "4005:4001"
      - "4006:4002"
    command:
      - "-node-id=3"
      - "-http-addr=0.0.0.0:4001"
      - "-raft-addr=0.0.0.0:4002"
      - "-join=rqlite1:4002"
      - "-raft-badger"
    volumes:
      - rqlite3-data:/rqlite
    networks:
      - rqlite-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4001/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

volumes:
  rqlite1-data:
    driver: local
  rqlite2-data:
    driver: local
  rqlite3-data:
    driver: local

networks:
  rqlite-net:
    driver: bridge
```

### With TLS Encryption

```yaml
version: '3'
services:
  rqlite1:
    image: rqlite/rqlite:latest
    container_name: rqlite1
    ports:
      - "4001:4001"
      - "4002:4002"
    command:
      - "-node-id=1"
      - "-http-addr=0.0.0.0:4001"
      - "-raft-addr=0.0.0.0:4002"
      - "-cluster-cert=/certs/tls.crt"
      - "-cluster-key=/certs/tls.key"
      - "-cluster-ca-cert=/certs/ca.crt"
      - "-http-cert=/certs/tls.crt"
      - "-http-key=/certs/tls.key"
    volumes:
      - rqlite1-data:/rqlite
      - ./certs:/certs:ro
    networks:
      - rqlite-net

  rqlite2:
    image: rqlite/rqlite:latest
    container_name: rqlite2
    ports:
      - "4003:4001"
      - "4004:4002"
    command:
      - "-node-id=2"
      - "-http-addr=0.0.0.0:4001"
      - "-raft-addr=0.0.0.0:4002"
      - "-join=rqlite1:4002"
      - "-cluster-cert=/certs/tls.crt"
      - "-cluster-key=/certs/tls.key"
      - "-cluster-ca-cert=/certs/ca.crt"
      - "-http-cert=/certs/tls.crt"
      - "-http-key=/certs/tls.key"
    volumes:
      - rqlite2-data:/rqlite
      - ./certs:/certs:ro
    networks:
      - rqlite-net

volumes:
  rqlite1-data:
  rqlite2-data:

networks:
  rqlite-net:
```

### With Read-Only Nodes

```yaml
version: '3'
services:
  rqlite1:
    image: rqlite/rqlite:latest
    container_name: rqlite1
    ports:
      - "4001:4001"
      - "4002:4002"
    command: ["-node-id=1"]
    volumes:
      - rqlite1-data:/rqlite
    networks:
      - rqlite-net

  rqlite2:
    image: rqlite/rqlite:latest
    container_name: rqlite2
    ports:
      - "4003:4001"
      - "4004:4002"
    command: ["-node-id=2", "-join=rqlite1:4002"]
    volumes:
      - rqlite2-data:/rqlite
    networks:
      - rqlite-net

  rqlite3:
    image: rqlite/rqlite:latest
    container_name: rqlite3
    ports:
      - "4005:4001"
      - "4006:4002"
    command: ["-node-id=3", "-join=rqlite1:4002"]
    volumes:
      - rqlite3-data:/rqlite
    networks:
      - rqlite-net

  # Read-only node for scaling reads
  rqlite-ro1:
    image: rqlite/rqlite:latest
    container_name: rqlite-ro1
    ports:
      - "4007:4001"
      - "4008:4002"
    command:
      - "-node-id=ro1"
      - "-join=rqlite1:4002"
      - "-raft-voter=false"  # Read-only, doesn't vote
    volumes:
      - rqlite-ro1-data:/rqlite
    networks:
      - rqlite-net

volumes:
  rqlite1-data:
  rqlite2-data:
  rqlite3-data:
  rqlite-ro1-data:

networks:
  rqlite-net:
```

## Operations

### Start and Stop

```bash
# Start all services
docker-compose up -d

# Start specific node
docker-compose up -d rqlite1

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### View Logs

```bash
# All logs
docker-compose logs -f

# Specific node
docker-compose logs -f rqlite1

# Last 100 lines
docker-compose logs --tail=100 rqlite1
```

### Execute Commands

```bash
# Connect to shell in container
docker exec -it rqlite1 rqlite 127.0.0.1:4001

# Create backup
docker exec rqlite1 rqlite 127.0.0.1:4001 ".backup /rqlite/backup.sqlite3"

# Copy backup to host
docker cp rqlite1:/rqlite/backup.sqlite3 ./backup.sqlite3

# Check cluster status
docker exec rqlite1 curl localhost:4001/status
```

### Restart and Update

```bash
# Restart specific node
docker-compose restart rqlite1

# Update image and restart
docker-compose pull
docker-compose up -d

# Scale (for custom setups)
docker-compose up -d --scale rqlite=5
```

## Host-Bound Volumes

For better performance or integration with existing backup systems:

```yaml
version: '3'
services:
  rqlite1:
    image: rqlite/rqlite:latest
    container_name: rqlite1
    ports:
      - "4001:4001"
      - "4002:4002"
    command: ["-node-id=1"]
    volumes:
      - /var/lib/rqlite/node1:/rqlite  # Host directory

  rqlite2:
    image: rqlite/rqlite:latest
    container_name: rqlite2
    ports:
      - "4003:4001"
      - "4004:4002"
    command: ["-node-id=2", "-join=rqlite1:4002"]
    volumes:
      - /var/lib/rqlite/node2:/rqlite

  rqlite3:
    image: rqlite/rqlite:latest
    container_name: rqlite3
    ports:
      - "4005:4001"
      - "4006:4002"
    command: ["-node-id=3", "-join=rqlite1:4002"]
    volumes:
      - /var/lib/rqlite/node3:/rqlite

networks:
  rqlite-net:
```

## Multi-Host Deployment

For deploying across multiple physical/virtual hosts, use Docker Swarm or external orchestration. Each host runs one or more nodes with appropriate `-http-adv-addr` and `-raft-adv-addr` settings.

## Troubleshooting

### Node Won't Join

```bash
# Check network connectivity
docker exec rqlite2 ping rqlite1

# Verify ports are open
docker exec rqlite1 netstat -tlnp

# Check logs for errors
docker-compose logs rqlite2
```

### Cluster Has No Leader

```bash
# Check all node statuses
for i in 1 2 3; do
  echo "=== Node $i ==="
  docker exec rqlite$i curl localhost:4001/status
done
```

### Data Persistence Issues

```bash
# Verify volumes are mounted
docker inspect rqlite1 | grep Mounts -A 10

# Check volume size
docker volume ls
docker system df
```

## Next Steps

- Set up [backup automation](05-backup-restore.md)
- Configure [monitoring](10-monitoring.md) for production
- Enable [security](08-security.md) with TLS and authentication
- Deploy to [Kubernetes](https://rqlite.io/docs/guides/kubernetes/) for large-scale production

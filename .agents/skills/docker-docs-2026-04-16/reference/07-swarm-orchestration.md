# Swarm Orchestration

## Overview

Docker Swarm is Docker's native clustering and orchestration solution. It turns a group of Docker engines into a single virtual Docker engine, providing service discovery, load balancing, rolling updates, and high availability.

## Initializing a Swarm

```bash
# Initialize swarm on manager node
docker swarm init --advertise-addr <MANAGER-IP>

# Join worker node
docker swarm join --token <TOKEN> <MANAGER-IP>:2377

# Join manager node
docker swarm join-token manager  # Get manager join token
docker swarm join --token <TOKEN> <MANAGER-IP>:2377
```

## Node Management

```bash
docker node ls                    # List nodes
docker node inspect <node>        # Inspect node
docker node ps <node>             # Tasks on a node
docker node update --label-add key=val <node>
docker node demote <node>         # Demote manager to worker
docker node promote <node>        # Promote worker to manager
docker node drain <node>          # Drain tasks from node
docker node rm <node>             # Remove node
```

Node states: `ready`, `down`, `unreachable`
Node roles: `manager`, `worker`

## Services

Services are the core abstraction in Swarm mode, defining the desired state.

### Creating Services

```bash
# Replicated service (default)
docker service create --name web --replicas 3 -p 8080:80 nginx

# Global service (one per node)
docker service create --name monitor --mode global prom/node-exporter

# With resource constraints
docker service create --name app \
  --replicas 2 \
  --memory 512M \
  --cpus 0.5 \
  myapp:latest

# With environment and secrets
docker service create --name db \
  --env MYSQL_ROOT_PASSWORD=secret \
  --secret db_password \
  mysql:8

# Rolling update config
docker service create --name web \
  --replicas 3 \
  --update-parallelism 1 \
  --update-delay 10s \
  --update-order start-first \
  nginx:latest
```

### Service Management

```bash
docker service ls                           # List services
docker service inspect web                  # Inspect service
docker service ps web                       # Tasks for a service
docker service scale web=5                  # Scale replicas
docker service update --image nginx:1.25 web  # Rolling update
docker service rollback web                 # Rollback to previous
docker service logs -f web                  # Follow logs
docker service rm web                       # Remove service
```

### Service Discovery and Load Balancing

Swarm provides internal DNS-based service discovery. Services are reachable by service name within the overlay network:

```bash
# Any container on the swarm network can reach 'db' service by name
docker service create --name app --network mynet myapp
```

Each service gets a virtual IP (VIP) for load balancing across replicas. For direct routing to individual tasks, use `--endpoint-mode dnsrr`:

```bash
docker service create --name web \
  --endpoint-mode dnsrr \
  --replicas 3 \
  nginx
```

## Compose with Swarm

Deploy Compose files to Swarm:
```bash
docker stack deploy -c docker-compose.yml mystack
docker stack services mystack
docker stack ps mystack
docker stack rm mystack
```

Compose `deploy` section maps to Swarm service configuration:
```yaml
services:
  web:
    image: nginx
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      rollback_config:
        parallelism: 1
        order: stop-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 256M
      placement:
        constraints:
          - node.role == manager
          - node.labels.datacenter == us-east
        preferences:
          - spread: node.labels.rack
    ports:
      - "8080:80"
    networks:
      - frontend
```

## Secrets

Swarm-managed secrets are encrypted at rest and distributed securely to tasks:

```bash
# Create from file
docker secret create db_password ./password.txt

# Create from stdin
echo "mypassword" | docker secret create api_key -

# List and inspect
docker secret ls
docker secret inspect db_password

# Use in service
docker service create --secret db_password mysql:8
```

In Compose:
```yaml
services:
  db:
    image: mysql
    secrets:
      - db_password

secrets:
  db_password:
    file: ./password.txt
```

## Configs

Immutable configuration files distributed to tasks (not mounted as files, injected at runtime):

```bash
docker config create nginx_conf ./nginx.conf
docker service create --config src=nginx_conf,target=/etc/nginx/nginx.conf nginx
```

## Swarm Security

- Manager-worker communication encrypted via mutual TLS
- Raft consensus for cluster state
- Secrets encrypted at rest using node key
- Certificate rotation (automatic by default, 60-day period)
- Node authorization with join tokens

## High Availability

- Minimum 3 manager nodes recommended for production
- Raft quorum requires majority of managers
- Managers can be demoted/promoted dynamically
- Automatic leader election

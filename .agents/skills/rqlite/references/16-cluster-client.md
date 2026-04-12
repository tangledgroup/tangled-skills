# Cluster Client Connection Strategies

Strategies for connecting your application to an rqlite cluster.

## Overview

When running rqlite as a cluster, your application needs a strategy for connecting to the cluster's nodes. Since any node can accept both read and write requests (with transparent forwarding), you have several options.

## How rqlite Routes Requests

### Leader-Follower Architecture

- **Leader**: Handles all writes, some reads
- **Followers**: Handle reads, forward writes to leader
- **Transparent forwarding**: Clients don't need to know which node is leader

```
Client → Any Node → [If Follower: Forward to Leader] → Process → Response
```

### Request Forwarding

- Writes to follower → Automatically forwarded to leader
- Reads can be served by any node (depending on consistency level)
- Client sees uniform behavior regardless of which node it contacts

## Connection Strategies

### 1. Static List with Round-Robin

Configure client with fixed list of node addresses:

```python
nodes = [
    "http://node1:4001",
    "http://node2:4001", 
    "http://node3:4001"
]

# Round-robin through nodes
for i, node in enumerate(nodes):
    response = request(node + "/db/query?q=SELECT * FROM users")
    if response.ok:
        break
```

**Pros:**
- Simple to implement
- No extra infrastructure needed
- No special permissions required

**Cons:**
- Cannot auto-detect topology changes
- Must update list when nodes join/leave
- Works best with stable cluster membership

### 2. DNS-Based Discovery

Use DNS to resolve cluster nodes:

```python
# Client connects to single DNS name
import dns.resolver

answers = dns.resolver.resolve('rqlite.example.com', 'A')
nodes = [f"http://{answer.to_text()}:4001" for answer in answers]
```

**DNS Configuration:**
```
rqlite.example.com.  60  IN  A  10.0.1.1
rqlite.example.com.  60  IN  A  10.0.1.2
rqlite.example.com.  60  IN  A  10.0.1.3
```

**SRV Records (alternative):**
```
_rqlite._tcp.example.com.  60  IN  SRV  0 5 4001 node1.example.com.
_rqlite._tcp.example.com.  60  IN  SRV  0 5 4001 node2.example.com.
```

**Pros:**
- Single configuration value (DNS name)
- Easy to update as cluster changes
- No client-side logic needed
- Kubernetes headless services do this automatically

**Cons:**
- DNS TTL affects update propagation
- Requires DNS management
- Short TTL increases DNS query load

### 3. Load Balancer

Place load balancer in front of cluster:

```yaml
# HAProxy configuration
frontend rqlite_front
  bind *:4001
  default_backend rqlite_back

backend rqlite_back
  balance roundrobin
  option httpchk GET /ready
  server node1 10.0.1.1:4001 check
  server node2 10.0.1.2:4001 check
  server node3 10.0.1.3:4001 check
```

**Client configuration:**
```python
# Single endpoint
node = "http://loadbalancer:4001"
response = request(node + "/db/query?q=SELECT * FROM users")
```

**Pros:**
- Trivial client configuration (single endpoint)
- Automatic health checking via `/ready`
- Removes unhealthy nodes automatically
- Well-suited for cloud/Kubernetes environments

**Cons:**
- Additional infrastructure component
- Load balancer is single point of failure (mitigate with HA)
- Small latency overhead (extra hop)

### 4. Node Discovery via API

Use `/nodes` endpoint to discover cluster membership:

```python
import requests

# Connect to seed node
seed_node = "http://node1:4001"

# Discover all nodes
response = requests.get(f"{seed_node}/nodes?ver=2")
cluster = response.json()

# Extract API addresses
nodes = [info['api_addr'] for info in cluster.values() if info['reachable']]

# Use discovered nodes
for node in nodes:
    response = requests.get(f"{node}/db/query?q=SELECT * FROM users")
    break
```

**Response from `/nodes`:**
```json
{
  "node1": {
    "api_addr": "http://10.0.1.1:4001",
    "addr": "10.0.1.1:4002",
    "reachable": true,
    "leader": true,
    "voter": true
  },
  "node2": {
    "api_addr": "http://10.0.1.2:4001",
    "addr": "10.0.1.2:4002",
    "reachable": true,
    "leader": false,
    "voter": true
  }
}
```

**Pros:**
- Only one node address needed at startup
- Auto-adapts to topology changes
- Can route directly to leader (avoid forwarding latency)
- Used by official `gorqlite` client library

**Cons:**
- Requires `status` permission for `/nodes` endpoint
- More implementation complexity
- Must handle discovery failures
- Need to periodically refresh cluster view

## Strategy Comparison

| Strategy | Complexity | Auto-Discovery | Health Checks | Infrastructure |
|----------|-----------|----------------|---------------|----------------|
| Static List | Low | No | Manual | None |
| DNS | Low | Yes (TTL-limited) | Manual | DNS server |
| Load Balancer | Low | No | Automatic | LB instance(s) |
| API Discovery | Medium | Yes | Via `/nodes` | None |

## Choosing a Strategy

### Use Static List When:
- Cluster membership is stable
- Simple deployment environment
- No DNS or load balancer available
- Small team, infrequent changes

### Use DNS When:
- Running in Kubernetes (headless services)
- Have DNS infrastructure
- Want simple client configuration
- Can tolerate TTL-based delay in updates

### Use Load Balancer When:
- Running in cloud environment
- Want automatic health checking
- Need single endpoint for clients
- Platform provides managed load balancers

### Use API Discovery When:
- Cluster membership changes frequently
- Want optimal routing (direct to leader)
- Can grant `status` permission
- Building custom client library

## Implementation Examples

### Python Client with Static List

```python
import requests
from itertools import cycle

class RQLiteClient:
    def __init__(self, nodes):
        self.nodes = cycle(nodes)
        
    def query(self, q):
        for node in self.nodes:
            try:
                resp = requests.get(f"{node}/db/query", params={'q': q})
                if resp.status_code == 200:
                    return resp.json()
            except requests.RequestException:
                continue
        raise Exception("All nodes unreachable")

# Usage
client = RQLiteClient([
    "http://node1:4001",
    "http://node2:4001",
    "http://node3:4001"
])
result = client.query("SELECT * FROM users")
```

### Python Client with API Discovery

```python
import requests
from cachetools import TTLCache

class RQLiteClient:
    def __init__(self, seed_node):
        self.seed_node = seed_node
        self.node_cache = TTLCache(maxsize=1, ttl=60)
        
    def _discover_nodes(self):
        if 'nodes' in self.node_cache:
            return self.node_cache['nodes']
            
        resp = requests.get(f"{self.seed_node}/nodes?ver=2")
        cluster = resp.json()
        nodes = [info['api_addr'] for info in cluster.values() if info['reachable']]
        self.node_cache['nodes'] = nodes
        return nodes
    
    def query(self, q):
        nodes = self._discover_nodes()
        for node in nodes:
            try:
                resp = requests.get(f"{node}/db/query", params={'q': q})
                if resp.status_code == 200:
                    return resp.json()
            except requests.RequestException:
                continue
        raise Exception("All nodes unreachable")

# Usage
client = RQLiteClient("http://node1:4001")
result = client.query("SELECT * FROM users")
```

### Go Client (gorqlite)

```go
import "github.com/rqlite/gorqlite"

// Automatically uses API discovery
conn, err := gorqlite.Open("http://node1:4001")
if err != nil {
    log.Fatal(err)
}

// Query
rows, err := conn.Query("SELECT * FROM users", nil)
```

## Health Checks

All strategies benefit from health checking:

```bash
# Check if node is ready
curl -f http://node1:4001/ready

# Returns HTTP 200 if ready, 503 if not
```

Use `/ready` endpoint in:
- Load balancer health checks
- Client connection validation
- Monitoring systems

## Next Steps

- Set up [security](08-security.md) for client connections
- Configure [monitoring](10-monitoring.md) for connection health
- Use [client libraries](https://rqlite.io/docs/api/client-libraries/) for production
- Review [FAQ](18-faq.md) for common connection questions

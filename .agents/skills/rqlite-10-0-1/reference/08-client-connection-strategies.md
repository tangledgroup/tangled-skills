# Client Connection Strategies

When running rqlite as a cluster, your application needs a strategy for connecting to the cluster's nodes. Since any node can accept both read and write requests (thanks to [transparent request forwarding](reference/02-http-api-and-developer-guide.md#request-forwarding)), you have several options.

## How rqlite Handles Client Requests

rqlite uses Raft consensus, so the cluster always has one Leader and one or more Followers. All writes must be processed by the Leader, though reads can be handled by any node depending on [consistency level](reference/03-read-consistency.md). By default, reads are also sent to the Leader.

**You don't need to know which node is the Leader.** If a Follower receives a write request, it transparently forwards it to the Leader and returns the response. From the client's perspective, every node behaves the same way.

## Static List with Round-Robin

Configure your client with a fixed list of node addresses and cycle through them:

```
http://node1:4001
http://node2:4001
http://node3:4001
```

Requests are sent in round-robin order. If a node is unreachable, skip it and try the next. This is the approach used by [rqlite-go-http](https://github.com/rqlite/rqlite-go-http).

**Trade-offs:**

- Simple to implement. No extra infrastructure needed.
- No additional permissions required — only normal API calls.
- Cannot automatically detect new nodes joining or removed nodes.
- Works well when cluster membership is stable and known at deployment time.

## DNS-Based Discovery

Configure a DNS name that resolves to the IP addresses of your rqlite nodes:

### A Records with Multiple IPs

```
rqlite.example.com.  60  IN  A  10.0.1.1
rqlite.example.com.  60  IN  A  10.0.1.2
rqlite.example.com.  60  IN  A  10.0.1.3
```

In Kubernetes, a [headless Service](reference/13-kubernetes-and-docker-compose.md) does exactly this.

### SRV Records

SRV records encode both hostnames and port numbers. Some service discovery systems (Consul, etcd) can generate SRV records automatically.

**Trade-offs:**

- Single DNS name in client configuration, easy to manage.
- DNS updates can lag behind actual cluster changes (mitigate with short TTL).
- No additional client-side logic or permissions needed.

## Load Balancer

Place a load balancer in front of your rqlite nodes. Your client connects to a single stable endpoint:

```
frontend rqlite_front
    bind *:4001
    default_backend rqlite_back

backend rqlite_back
    balance roundrobin
    option httpchk GET /readyz
    server node1 10.0.1.1:4001 check
    server node2 10.0.1.2:4001 check
    server node3 10.0.1.3:4001 check
```

> rqlite provides a [`/readyz` endpoint](reference/12-monitoring.md#readiness-checks) that returns HTTP 200 when healthy. Use this as your health check.

Because rqlite transparently forwards requests to the Leader, any basic load-balancing strategy (round-robin, least-connections, random) works correctly. The load balancer doesn't need to be leader-aware.

**Trade-offs:**

- Client only needs a single endpoint.
- Load balancer health-checks nodes and removes unhealthy ones automatically.
- Introduces an additional infrastructure component.
- Adds a small amount of network latency (one extra hop).
- Well suited to cloud environments and Kubernetes.

## Node Discovery via API

Connect to one known node, query `/nodes` to discover the full cluster membership, then distribute requests across all discovered nodes:

```bash
curl -s localhost:4001/nodes?pretty&ver=2
```

Response:

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

This is the approach used by [gorqlite](https://github.com/rqlite/gorqlite):

```go
conn, err := gorqlite.Open("http://node1:4001")
```

If the Leader changes or a node becomes unreachable, gorqlite re-queries `/nodes` to discover the new topology.

**Trade-offs:**

- Only one node address needed at startup.
- Adapts to cluster membership changes without redeployment.
- Can route requests directly to the Leader, avoiding forwarding latency.
- Requires `status` [permission](reference/10-security.md#user-level-permissions) on the connecting user.
- Adds implementation complexity compared to a static list.

## Choosing a Strategy

- **Kubernetes or cloud platform:** Load balancer or DNS-based approach is often easiest since the platform provides the mechanism.
- **Stable, well-known set of nodes:** A static list may be all you need.
- **Automatic topology adaptation:** API-based discovery provides the most flexibility if you can grant the `status` permission.
- You can combine approaches — for example, DNS to discover an initial node, then API-based discovery for ongoing cluster awareness.

## Client Libraries

Client libraries are available in multiple languages:

**Go:**
- [rqlite-go-http](https://github.com/rqlite/rqlite-go-http) — thin client with minimal abstraction
- [gorqlite](https://github.com/rqlite/gorqlite) — richer client with node discovery
- [GORM driver](https://github.com/goki/rqlite)

**Python:**
- [pyrqlite](https://github.com/rqlite/pyrqlite)
- [sqlalchemy-rqlite](https://github.com/rqlite/sqlalchemy-rqlite)
- [tangled-pyrqlite](https://github.com/tangledgroup/tangled-pyrqlite)

**Java:**
- [rqlite-java-http](https://github.com/rqlite/rqlite-java-http) — thin client
- [rqlite-jdbc](https://github.com/rqlite/rqlite-jdbc) — fully featured Type 4 JDBC driver

**Rust:**
- [rqlite](https://docs.rs/rqlite/latest/rqlite)
- [rqlite_client](https://docs.rs/rqlite_client/)
- [sqlx-rqlite](https://github.com/HaHa421/sqlx-rqlite)

**TypeScript:**
- [knex-rqlite](https://github.com/rqlite/knex-rqlite)
- [tsrqdb](https://github.com/Tjstretchalot/tsrqdb)

**JavaScript:**
- [rqlite-js](https://github.com/rqlite/rqlite-js)
- [rqlink](https://github.com/ManwilBahaa/rqlink) — Prisma-like ORM style client

**C#:**
- [rqlite-dotnet](https://github.com/rqlite/rqlite-dotnet)
- [rqlite-net](https://github.com/sec/rqlite-net)

**PHP:**
- [rqlite-php](https://github.com/karlomikus/rqlite-php)

**Delphi (Pascal):**
- [rqliteclient4delphi](https://github.com/OwlHatSoftware/rqliteclient4delphi)

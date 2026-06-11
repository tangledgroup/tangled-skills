# DHT Network Details

## Contents
- Architecture Overview
- Peer Discovery
- Cache Propagation
- Performance Characteristics
- Installation and Configuration

## Architecture Overview

The DHT (Distributed Hash Table) network is an optional peer-to-peer layer that caches search results across participating nodes. It operates transparently — no code changes required beyond installing the `[dht]` extra.

### Components

- **Local cache** — Persistent on-disk cache for recent queries
- **Network node** — Full DHT participant using libp2p
- **API integration** — Automatic `/dht/*` endpoints when `ddgs api` runs
- **Search interceptor** — All search methods check DHT before hitting upstream engines

### How It Works

1. Node starts and joins the DHT network via libp2p peer discovery
2. Incoming search query triggers a DHT lookup first
3. If a cached result exists, it's returned immediately (~50ms)
4. If not found, normal search proceeds and result is published to DHT
5. Every new node makes the network faster for all participants

## Peer Discovery

Nodes discover each other through libp2p's Kademlia DHT protocol. No central bootstrap server — peers find each other organically through existing connections.

- New nodes connect to known peer addresses
- Existing nodes learn about new peers through gossip
- Connection table maintained via libp2p's connection manager
- No query visibility — all lookups are anonymous

## Cache Propagation

Results use **eventual consistency**:

- Cached results propagate to other nodes within 1–5 minutes
- TTL is based on the original search result's freshness
- Stale entries are evicted automatically
- Write-through: new results are published to DHT after successful search

### Cache Key Structure

Cache keys are derived from the full query parameters (query string, region, safesearch, timelimit, backend). Identical parameters produce identical cache hits.

## Performance Characteristics

| Network Size | Performance | Notes |
|-------------|-------------|-------|
| < 50 nodes | Marginal — expect timeouts | Limited peer availability |
| 50–200 nodes | Good — >95% success rate | Viable for most use cases |
| > 200 nodes | Excellent — near perfect | Full network benefits |

### Metrics

When running the API server, expose Prometheus metrics at `/dht/metrics`:

- Node count and peer list
- Cache hit/miss ratio
- Query latency distribution
- Network topology information

## Installation and Configuration

### Linux/macOS

```bash
pip install -U ddgs[dht]
pip install coincurve@git+https://github.com/ofek/coincurve.git@7829b29c08ebb1cc80386a1cdaf8c2243c4ef5c5
pip install libp2p@git+https://github.com/libp2p/py-libp2p.git@0e88584c89377086883c6f5b26cd1a8052399be7
```

### macOS Additional Step

```bash
brew install gmp
```

### Windows

Not supported due to libp2p dependency constraints. Use base `ddgs` package only.

### Usage with API Server

```bash
# Start API server — DHT activates automatically
ddgs api -d

# Or spawn from Python
from ddgs import DDGS
ddgs = DDGS(api_url="http://localhost:4479", spawn_api=True)
```

No code changes needed in existing scripts — `DDGS().text()`, `.images()`, etc. automatically use DHT cache when available.

## DHT API Endpoints

All require `ddgs[api]` running:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dht/cache` | GET | Retrieve cached result by query hash |
| `/dht/cache` | POST | Store new result in cache |
| `/dht/cache` | DELETE | Invalidate a cached entry |
| `/dht/status` | GET | Service status and operational metrics |
| `/dht/peers` | GET | List of connected peer addresses |
| `/dht/peers/detailed` | GET | Peer info with latency, location hints |
| `/dht/map` | GET | Network topology graph (JSON) |
| `/dht/metrics` | GET | Prometheus-format metrics |

## Beta Status

DHT is working beta software. All core functionality is implemented but network performance depends on user adoption. Report issues at https://github.com/deedy5/ddgs/issues.

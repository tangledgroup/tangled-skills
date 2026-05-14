# PROXY Protocol and Peers

## PROXY Protocol

The PROXY protocol safely transports connection information (client address, ports) across multiple layers of NAT or TCP proxies. It prepends a short header to each new connection, requiring minimal changes to existing components.

### Why PROXY Protocol

When a proxy relays TCP connections, the original connection parameters (source/destination addresses and ports) are lost. HTTP has `X-Forwarded-For` and `Forwarded` headers, but these require protocol-specific knowledge. The PROXY protocol works at the transport layer, making it protocol-agnostic — it works with HTTP, SMTP, FTP, SSH, RDP, or any TCP/UDP protocol.

### Version 1 (Human-Readable)

```
PROXY TCP4 192.168.0.1 192.168.0.11 56324 443\r\n
```

Format: `PROXY <protocol> <src_addr> <dst_addr> <src_port> <dst_port>\r\n`

- Protocol: `TCP4`, `TCP6`, or `UNKNOWN`
- Maximum line length: 107 characters including CRLF
- A 108-byte buffer is always sufficient

### Version 2 (Binary)

16-byte fixed header followed by address information:

```
Bytes 1-12:  Magic signature \x0D\x0A\x0D\x0A\x00\x0D\x0A\x51\x55\x49\x54\x0A
Byte 13:     Version (high nibble) + Command (low nibble)
Byte 14:     Address family (high nibble) + Protocol (low nibble)
Bytes 15-16: Length of address block (network byte order)
Bytes 17+:   Source/destination addresses and ports
```

Command values:
- `0x0` — LOCAL: connection initiated by the proxy itself (health checks)
- `0x1` — PROXY: relayed connection with original endpoints

Address family + protocol byte values:
- `0x00` — UNSPEC (unknown/unspecified)
- `0x11` — TCP over IPv4 (12 bytes of address data)
- `0x12` — UDP over IPv4 (12 bytes)
- `0x21` — TCP over IPv6 (36 bytes)
- `0x22` — UDP over IPv6 (36 bytes)
- `0x31` — UNIX stream (216 bytes)

Total header sizes:
- v2 TCP/IPv4: 16 + 12 = 28 bytes
- v2 TCP/IPv6: 16 + 36 = 52 bytes

### TLV (Type-Length-Value) Extensions

Version 2 supports optional TLV blocks after the address information:

- `0x01` — ALPN: negotiated application protocol
- `0x02` — AUTHORITY: SNI hostname (UTF-8 string)
- `0x03` — CRC32C: checksum of the PROXY header
- `0x04` — NOOP: padding/alignment
- `0x05` — UNIQUE_ID: opaque connection identifier (up to 128 bytes)
- `0x20` — SSL: SSL/TLS information with subtypes:
  - `0x21` — SSL version string
  - `0x22` — Client certificate Common Name
  - `0x23` — Cipher name (e.g., "ECDHE-RSA-AES128-GCM-SHA256")
  - `0x24` — Signature algorithm
  - `0x25` — Key algorithm (e.g., "RSA2048")
  - `0x26` — Key exchange group (e.g., "secp256r1")
  - `0x27` — Signature scheme (e.g., "rsa_pss_rsae_sha256")
- `0x30` — NETNS: network namespace name
- `0xE0-0xEF` — Reserved for application-specific data
- `0xF0-0xF7` — Reserved for experimental use

### Using PROXY Protocol in HAProxy

#### Accepting PROXY Protocol

```
frontend http-in
    bind *:443 ssl crt /etc/haproxy/certs/ accept-proxy-v2
```

Options:
- `accept-proxy` — accept PROXY protocol v1
- `accept-proxy-v2` — accept PROXY protocol v2
- `accept-proxy` also accepts v2 (backward compatible)

#### Sending PROXY Protocol

```
backend web-servers
    server web1 10.0.0.1:80 send-proxy-v2 check
    server web2 10.0.0.2:80 send-proxy check
```

Options:
- `send-proxy` — send PROXY protocol v1
- `send-proxy-v2` — send PROXY protocol v2
- `send-proxy-v2-sub` — send v2 with SSL TLV subtypes

#### Multi-Layer Proxy Chain

```
         Internet
          ,---.
         (  X  )
          `---'
            |
         +--+--+      +-----+
         | FW1 |------| PX1 |  <-- accepts from internet
         +--+--+      +-----+       | sends PROXY v2 to PX2
            |                       V
         +--+--+      +-----+
         | FW2 |------| PX2 |  <-- accepts PROXY v2
         +--+--+      +-----+       | sends PROXY v2 to SRV
            |                       V
         +--+--+
         | SRV |  <-- receives original client IP
         +-----+
```

PX1 configuration:
```
frontend fe-internet
    bind *:443 ssl crt /etc/haproxy/certs/
    default_backend be-px2

backend be-px2
    server px2 10.0.1.2:443 send-proxy-v2 ssl verify required
```

PX2 configuration:
```
frontend fe-px1
    bind *:443 ssl crt /etc/haproxy/certs/ accept-proxy-v2
    default_backend be-servers

backend be-servers
    server srv1 10.0.2.1:80 send-proxy-v2 check
```

### Security Considerations

- **Never auto-detect** PROXY protocol — always explicitly configure `accept-proxy`. Auto-detection allows clients to spoof their source address
- Only accept PROXY protocol from trusted sources (internal networks, known proxies)
- The v2 binary signature is designed to be rejected by common protocols (HTTP, SSL, SMTP, FTP, POP, LDAP, SSH, RDP) when presented unexpectedly
- Receiver must not start processing before receiving a complete and valid PROXY header

## Peers Protocol

The peers protocol replicates stick-table entries between HAProxy nodes in a multi-master fashion. This enables consistent rate limiting, DDoS protection, and session persistence across multiple load balancers.

### Configuration

```
peers mycluster
    localpeer $HAPROXY_LOCALPEER
    peer node1 10.0.0.1:10000
    peer node2 10.0.0.2:10000
    peer node3 10.0.0.3:10000
```

Or using command-line peer name:
```
peers mycluster
    peer node1 10.0.0.1:10000
    peer node2 10.0.0.2:10000
```

Started with: `haproxy -L node1 -f /etc/haproxy/haproxy.cfg`

### Protocol Details

**Handshake:**
1. Peer connects and sends "hello" message (3 lines):
   ```
   HAProxyS 2.1\n
   <remote-peer-name>\n
   <local-peer-name> <pid> <relative-pid>\n
   ```
2. Remote peer replies with status code:
   - `200` — handshake succeeded
   - `300` — try again later
   - `501` — protocol error
   - `502` — bad version
   - `503` — local peer identifier mismatch
   - `504` — remote peer identifier mismatch

**Connection Management:**
- Symmetrical — any peer can connect to any other
- Only one TCP session per peer pair (last connected wins)
- On simultaneous connection, the existing session is closed in favor of the new one
- Random reconnection delay (50ms to 2050ms) prevents simultaneous reconnect storms

**Heartbeat:**
- Heartbeat messages sent after 3 seconds of inactivity
- Peer considered dead after 5 seconds of silence (no heartbeat, no data)
- Dead peers are disconnected and reconnection is attempted

### Message Types

**Control Messages (class 0):**
- Type 0 — Synchronization request (full sync from remote)
- Type 1 — Synchronization finished
- Type 2 — Synchronization partial
- Type 3 — Synchronization confirmed
- Type 4 — Heartbeat

**Error Messages (class 1):**
- Type 0 — Protocol error
- Type 1 — Size limit error

**Stick-Table Updates (class 10, variable-length):**
- Type 128 — Entry update
- Type 129 — Incremental entry update
- Type 130 — Stick-table definition (sent before updates)
- Type 133 — Update acknowledgement

### Stick-Table Replication Flow

1. New HAProxy process starts and connects to peers
2. Sends synchronization request
3. Peers push their stick-table definitions and entries
4. After initial sync, incremental updates are exchanged in real-time
5. Updates are acknowledged by receiving peers

### Monitoring Peers

```bash
# Show peer status
echo "show peers" | socat stdio /var/run/haproxy.sock

# Output shows:
# - Peer connection status (NONE, CONN, ESTA)
# - Shared tables and their sync state
# - Last acknowledged/pushed update IDs
```

### Tuning

```
global
    # Max stick-table updates processed at once (default 200)
    tune.peers.max-updates-at-once 200
```

### Use Case: Distributed Rate Limiting

With peers replication, rate limiting works consistently across multiple HAProxy nodes:

```
peers ratelimit-cluster
    peer lb1 10.0.0.1:10000
    peer lb2 10.0.0.2:10000

frontend http-in
    bind *:80
    stick-table type ip size 200k expire 5m \
        store http_req_rate(10s) \
        peer ratelimit-cluster
    http-request track-sc0 src
    http-request deny if { sc_http_req_rate(0) gt 100 }
    default_backend web-servers
```

When a client hits lb1 and then lb2, the request rate is already tracked because stick-table entries are replicated in real-time. This prevents attackers from bypassing rate limits by hitting different load balancers.

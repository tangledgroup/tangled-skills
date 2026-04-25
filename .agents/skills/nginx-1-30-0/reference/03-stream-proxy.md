# Stream / TCP / UDP Proxy Reference

## ngx_stream_core_module — Stream Core

The stream module is available since version 1.9.0 and must be enabled with `--with-stream` at compile time. It provides generic proxying and load balancing for TCP/UDP protocols.

### Example Configuration

```nginx
worker_processes auto;
error_log /var/log/nginx/error.log info;

events {
    worker_connections 1024;
}

stream {
    upstream backend {
        hash $remote_addr consistent;
        server backend1.example.com:12345 weight=5;
        server 127.0.0.1:12345 max_fails=3 fail_timeout=30s;
        server unix:/tmp/backend3;
    }

    upstream dns {
        server 192.168.0.1:53535;
        server dns.example.com:53;
    }

    server {
        listen 12345;
        proxy_connect_timeout 1s;
        proxy_timeout 3s;
        proxy_pass backend;
    }

    server {
        listen 127.0.0.1:53 udp reuseport;
        proxy_timeout 20s;
        proxy_pass dns;
    }

    server {
        listen [::1]:12345;
        proxy_pass unix:/tmp/stream.socket;
    }
}
```

### `listen [ address : port ] [ parameters ]`

| Parameter | Description |
|-----------|-------------|
| `default_server` | Default server for this address:port (1.25.5) |
| `ssl` | Enable SSL mode |
| `udp` | Listen for datagrams (1.9.13); requires `reuseport` for same-session handling |
| `proxy_protocol` | Accept PROXY protocol headers (v2 since 1.13.11) |
| `reuseport` | Separate listening socket per worker (SO_REUSEPORT) |
| `backlog = number` | listen() backlog queue length |
| `rcvbuf = size` / `sndbuf = size` | Socket buffer sizes |
| `so_keepalive = on \| off \| [keepidle]:[keepintvl]:[keepcnt]` | TCP keepalive per-socket settings |
| `fastopen = number` | TCP Fast Open, limits SYN queue (1.21.0) |
| `setfib = number` | Routing table FIB (FreeBSD only, 1.25.5) |
| `ipv6only = on \| off` | IPv6-only socket |
| `multipath` | Multipath TCP (IPPROTO_MPTCP), Linux 5.6+ (1.29.7) |

Port ranges: `listen 12345-12399;`  
UNIX sockets: `listen unix:/var/run/nginx.sock;`

### `server { ... }`
Defines a virtual server in the stream context. Supports SNI-based routing (1.25.5).

### `server_name [ name ... ]`
Server names for SNI-based virtual server selection (since 1.25.5). Supports wildcards and regex.

```nginx
server {
    listen 443 ssl;
    server_name example.com www.example.com;
    proxy_pass secure_backend;
}
```

### `stream { ... }`
Configuration context for stream server directives. Resides in main context.

**Context:** `main`

### `tcp_nodelay [ on \| off ]`
Enables TCP_NODELAY option for both client and proxied connections.

**Default:** `on`  
**Context:** `stream`, `server`

### `proxy_protocol_timeout [ timeout ]`
Timeout for reading PROXY protocol header. Connection is closed if incomplete.

**Default:** `30s`  
**Context:** `stream`, `server`

### `preread_buffer_size [ size ]`
Buffer size for preread phase (used by SSL/SNI preread).

**Default:** `16k`  
**Context:** `stream`, `server`

### `preread_timeout [ timeout ]`
Timeout for the preread phase.

**Default:** `30s`  
**Context:** `stream`, `server`

### `resolver [ address ... ] [ valid=time ] [ ipv4=on\|off ] [ ipv6=on\|off ]`
DNS resolver for upstream name resolution in stream context.

```nginx
resolver 127.0.0.1 [::1]:5353 valid=30s;
```

### `resolver_timeout [ time ]`
Timeout for DNS name resolution.

**Default:** `30s`  
**Context:** `stream`, `server`

### `variables_hash_bucket_size [ size ]`
Bucket size for variables hash table.

**Default:** `64`  
**Context:** `stream`

### `variables_hash_max_size [ size ]`
Maximum size of variables hash table.

**Default:** `1024`  
**Context:** `stream`

## Stream Embedded Variables

| Variable | Description |
|----------|-------------|
| `$binary_remote_addr` | Client address in binary form (4 bytes IPv4, 16 bytes IPv6) |
| `$bytes_received` | Bytes received from client (1.11.4) |
| `$bytes_sent` | Bytes sent to client |
| `$connection` | Connection serial number |
| `$hostname` | Host name |
| `$msec` | Current time in seconds with ms resolution |
| `$nginx_version` | Nginx version string |
| `$pid` | Worker process PID |
| `$protocol` | Protocol: `TCP` or `UDP` (1.11.4) |
| `$proxy_protocol_addr` | Client from PROXY protocol header |
| `$proxy_protocol_port` | Client port from PROXY protocol header |
| `$remote_addr` | Client address |
| `$remote_port` | Client port |
| `$server_addr` | Server address that accepted the connection |
| `$server_port` | Port of accepting server |
| `$session_time` | Session duration in seconds with ms resolution (1.11.4) |
| `$status` | Session status: `200`, `400`, `403`, `500`, `502`, `503` (1.11.4) |
| `$time_iso8601` | Local time in ISO 8601 format |
| `$time_local` | Local time in Common Log Format |

## Stream Load Balancing

Stream module supports the same load balancing methods as HTTP upstream:

```nginx
stream {
    # Hash-based (consistent hashing)
    upstream consistent_backend {
        hash $remote_addr consistent;
        server backend1.example.com:80;
        server backend2.example.com:80;
    }

    # Round-robin with weights
    upstream weighted_backend {
        server backend1.example.com:80 weight=5;
        server backend2.example.com:80 weight=3;
        server backend3.example.com:80 backup;
    }

    # Least connections
    upstream least_conn_backend {
        least_conn;
        server backend1.example.com:80;
        server backend2.example.com:80;
    }

    server {
        listen 80;
        proxy_pass weighted_backend;
    }
}
```

## ngx_stream_ssl_module — SSL/TLS in Stream Context

### `ssl_certificate [ file ]`
SSL certificate for stream connections.

### `ssl_certificate_key [ file ]`
SSL private key for stream connections.

### `ssl_protocols [ SSLv2 \| SSLv3 \| TLSv1 \| TLSv1.1 \| TLSv1.2 \| TLSv1.3 ]`
Enabled protocols for stream SSL connections.

### `ssl_ciphers [ ciphers ]`
Cipher suite configuration for stream SSL.

### `ssl_prefer_server_ciphers [ on \| off ]`
Prefer server cipher order.

### `ssl_session_cache [ none \| builtin[:size] \| shared:name:size ]`
SSL session caching for stream connections.

## ngx_stream_ssl_preread_module — SNI Preread

Allows extracting SNI information from ClientHello without terminating SSL/TLS. Useful for routing based on server name in encrypted connections.

```nginx
stream {
    map $ssl_preread_server_name $upstream_backend {
        api.example.com     api_backend;
        www.example.com     www_backend;
        default             default_backend;
    }

    server {
        listen 443 ssl;
        proxy_pass $upstream_backend;
        ssl_preread on;
    }
}
```

Enable module: `--with-stream_ssl_preread_module`

## ngx_stream_geo_module — Geo Variables in Stream

Creates variables based on client IP address for stream context.

```nginx
stream {
    geo $remote_addr $is_internal {
        default 0;
        10.0.0.0/8 1;
        192.168.1.0/24 1;
    }

    server {
        listen 8080;
        allow 10.0.0.0/8;
        allow 192.168.1.0/24;
        deny all;
        proxy_pass internal_backend;
    }
}
```

## ngx_stream_geoip_module — GeoIP in Stream

Creates variables based on client IP using MaxMind databases.

```nginx
geoip_country /usr/share/GeoIP/GeoIP.dat;

stream {
    geo $remote_addr $country_code {
        default US;
        GB UK;
        DE DE;
    }

    server {
        listen 80;
        if ($country_code = CN) {
            return 403;
        }
        proxy_pass backend;
    }
}
```

## ngx_stream_access_module — Access Control in Stream

### `allow [ address \| CIDR \| all ]`
Allow access from specified addresses.

### `deny [ address \| all ]`
Deny access from specified addresses.

```nginx
stream {
    server {
        listen 22;
        allow 10.0.0.0/8;
        deny all;
        proxy_pass ssh_backend;
    }
}
```

## ngx_stream_limit_conn_module — Connection Limiting in Stream

### `limit_conn_zone [ variable ] zone=name:size`
Defines a zone for connection limiting.

```nginx
stream {
    limit_conn_zone $binary_remote_addr zone=addr:10m;

    server {
        listen 80;
        limit_conn addr 10;
        proxy_pass backend;
    }
}
```

## ngx_stream_log_module — Stream Logging

### `access_log [ path [ format ] ]`
Configure access logging for stream connections.

```nginx
log_format basic '$remote_addr [$time_local] $protocol '
                 '"$connection" "$connection_status"';

stream {
    access_log /var/log/nginx/stream-access.log basic;
}
```

### `map` — Variable Mapping in Stream

Maps values to other values for stream context.

```nginx
stream {
    map $ssl_preread_server_name $upstream {
        api.example.com     api_backend;
        *.example.com       default_backend;
        ~^www\d+\.example\.com$ www_backend;
    }
}
```

## ngx_stream_split_clients_module — A/B Testing in Stream

Creates variables for traffic splitting (A/B testing) in stream context.

```nginx
stream {
    split_clients "$remote_addr$request_method" $backend_variant {
        0.5     backend_v1;
        *       backend_v2;
    }

    server {
        listen 80;
        proxy_pass $backend_variant;
    }
}
```

## ngx_stream_return_module — Simple Return in Stream

Sends a specified value to the client and closes the connection. Useful for health checks or simple responses.

```nginx
stream {
    server {
        listen 8053 udp;
        return 127.0.0.1:53;  # DNS forwarding response
    }

    server {
        listen 8443;
        return "OK";
    }
}
```

## ngx_stream_keyval_module — Key-Value Storage in Stream

Stores and retrieves key-value pairs in shared memory for stream context. Useful for tracking client state across connections.

```nginx
stream {
    keyval_zone zone=my_state:1m;
    keyval $remote_addr $client_id zone=my_state;

    server {
        listen 80;
        proxy_pass backend;
    }
}
```

## ngx_stream_set_module — Variable Setting in Stream

Sets values for variables in stream context.

```nginx
stream {
    set $upstream_host "backend.example.com";
    set $upstream_port 8080;

    server {
        listen 80;
        proxy_pass $upstream_host:$upstream_port;
    }
}
```

## ngx_stream_proxy_module — Proxy Protocol in Stream

### `proxy_connect_timeout [ time ]`
Timeout for establishing connection with upstream.

**Default:** `60s`

### `proxy_timeout [ time ]`
Timeout for both client and upstream connections.

**Default:** `10m`

### `proxy_pass [ address ]`
Specifies the upstream server to proxy to.

```nginx
server {
    listen 80;
    proxy_pass backend_servers;
}
```

### `proxy_bind [ address ]`
Bind outgoing connection to a specific local address.

## ngx_stream_upstream_hc_module — Health Checks (Commercial)

Health check module for stream upstream servers (commercial subscription).

```nginx
upstream backend {
    zone upstream_dynamic 64k;
    server backend1.example.com:80;
    server backend2.example.com:80;
}

server {
    listen 80;
    proxy_pass backend;
    health_check;
}
```

## ngx_stream_zone_sync_module — Zone Synchronization (Commercial)

Synchronizes shared memory zones between nginx nodes for high availability (commercial subscription).

```nginx
zone_sync;
zone_sync_server 192.168.1.2:12345;
```

## ngx_stream_mqtt_preread_module — MQTT Pre-Read

MQTT CONNECT packet prereading module for routing based on client ID.

Enable with: `--with-stream_mqtt_preread_module`

```nginx
stream {
    map $mqtt_connect_client_id $upstream_backend {
        ~^device-\d+$     iot_backend;
        ~^admin-.*$       admin_backend;
        default           default_backend;
    }

    server {
        listen 1883;
        proxy_pass $upstream_backend;
    }
}
```

## ngx_stream_mqtt_filter_module — MQTT Filter

Basic MQTT packet filtering module for stream context.

Enable with: `--with-stream_mqtt_filter_module`

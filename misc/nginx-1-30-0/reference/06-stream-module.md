# Stream Module (TCP/UDP)

## Overview

The `ngx_stream_core_module` enables nginx to proxy TCP and UDP traffic. It requires the `--with-stream` configure flag (or dynamic module loading). The stream context is at the same level as `http` in the main configuration.

## Request Processing Phases

A TCP/UDP session is processed through successive phases:

1. **Post-accept** — initial phase after accepting connection (`ngx_stream_realip_module`)
2. **Pre-access** — preliminary access check (`ngx_stream_limit_conn_module`, `ngx_stream_set_module`)
3. **Access** — client access limitation (`ngx_stream_access_module`, `js_access`)
4. **SSL** — TLS/SSL termination (`ngx_stream_ssl_module`)
5. **Preread** — reading initial bytes for analysis (`ngx_stream_ssl_preread_module`, `js_preread`)
6. **Content** — data processing, usually proxying to upstream
7. **Log** — recording session results (`ngx_stream_log_module`)

## Basic Configuration

```nginx
stream {
    upstream backend {
        server backend1.example.com:12345 weight=5;
        server 127.0.0.1:12345 max_fails=3 fail_timeout=30s;
        server unix:/tmp/backend3;
    }

    server {
        listen 12345;
        proxy_pass backend;
    }
}
```

## UDP Support

```nginx
stream {
    upstream dns {
        server 192.168.0.1:5353;
        server dns.example.com:53;
    }

    server {
        listen 53 udp reuseport;
        proxy_pass dns;
    }
}
```

## Stream Proxy Directives

```nginx
proxy_connect_timeout 1s;
proxy_timeout 1s;
proxy_responses 1;
proxy_buffer_size 4k;
```

## SSL Termination for TCP

```nginx
stream {
    server {
        listen 443 ssl;
        proxy_pass backend;

        ssl_certificate     /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/cert.key;
    }
}
```

## SSL Preread

Route based on SNI without terminating SSL:

```nginx
stream {
    map $ssl_preread_server_name $backend {
        default default_backend;
        app1.example.com app1_backend;
        app2.example.com app2_backend;
    }

    server {
        listen 443;
        ssl_preread on;
        proxy_pass $backend;
    }
}
```

## Stream Access Control

```nginx
server {
    listen 3306;
    proxy_pass mysql_backend;

    allow 10.0.0.0/8;
    deny all;
}
```

## Log Format for Stream

```nginx
stream {
    log_format basic '$remote_addr [$time_local] '
                     '$protocol $status $bytes_sent $bytes_received '
                     '$session_time';

    access_log /var/log/nginx/stream.log basic;
}
```

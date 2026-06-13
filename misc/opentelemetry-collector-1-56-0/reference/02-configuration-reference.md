# Configuration Reference

## Configuration Location and Loading

By default, the Collector reads configuration from:

```
/etc/<otel-directory>/config.yaml
```

Where `<otel-directory>` is `otelcol`, `otelcol-contrib`, or another value
depending on the distribution. Override with the `--config` flag:

```bash
otelcol --config=custom-config.yaml
```

## Configuration Providers (Schemes)

The `--config` flag accepts URIs with scheme prefixes:

- **file** — read from a file path
  ```
  otelcol --config=file:/path/to/config.yaml
  ```
- **env** — read from an environment variable
  ```
  otelcol --config=env:MY_CONFIG_IN_AN_ENVVAR
  ```
- **yaml** — inline YAML string with `::` delimiter for nested keys
  ```
  otelcol --config="yaml:exporters::debug::verbosity: detailed"
  ```
- **http / https** — read from a URL
  ```
  otelcol --config=https://config-server.example.com/collector-config.yaml
  ```

Multiple configurations can be merged by passing multiple `--config` flags. Each
file can be a full or partial configuration, and files can reference components
from each other.

## Configuration File Inclusion

YAML files can include other files using the `${file:path}` syntax:

```yaml
# main-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

exporters:
  ${file:exporters.yaml}

service:
  extensions: []
  pipelines:
    traces:
      receivers: [otlp]
      processors: []
      exporters: [otp_grpc]
```

```yaml
# exporters.yaml
otlp_grpc:
  endpoint: otelcol.observability.svc.cluster.local:443
```

The Collector merges all included files into a single in-memory YAML
configuration at startup.

## Environment Variable Substitution

Configuration values can reference environment variables using the
`${ENV_VAR}` syntax. The Collector substitutes these values at load time:

```yaml
exporters:
  otlp:
    endpoint: ${OTEL_EXPORTER_ENDPOINT}
    authentication:
      credentials: ${OTEL_API_KEY}
```

## Proxy Support

The Collector respects standard proxy environment variables:

- `HTTP_PROXY` / `http_proxy` — proxy for HTTP connections
- `HTTPS_PROXY` / `https_proxy` — proxy for HTTPS connections
- `NO_PROXY` / `no_proxy` — hosts to exclude from proxying

Some exporters also support explicit proxy configuration in their settings.

## Authentication

Authentication can be configured at the receiver (server-side) and exporter
(client-side) level. Common approaches:

### Bearer Token Authentication

```yaml
exporters:
  otlp:
    endpoint: backend:4317
    auth:
      authenticator: bearer_token

extensions:
  bearer_token:
    token: "${BEARER_TOKEN}"
```

### API Key Authentication

```yaml
exporters:
  otlp:
    endpoint: backend:4317
    headers:
      X-API-Key: "${API_KEY}"
```

### Authenticator Extensions

Use authenticator extensions for more sophisticated authentication:

```yaml
extensions:
  bearer_token_auth:
    token: "${BEARER_TOKEN}"
  oauth2client:
    client_id: "${CLIENT_ID}"
    client_secret: "${CLIENT_SECRET}"
    token_url: https://auth.example.com/oauth2/token
    scopes: [otel.write]

exporters:
  otlp:
    endpoint: backend:4317
    auth:
      authenticator: oauth2client
```

## TLS Configuration

### Server-Side TLS (Receivers)

Configure TLS for receivers that accept incoming connections:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
        tls:
          cert_file: /etc/ssl/certs/collector-cert.pem
          key_file: /etc/ssl/private/collector-key.pem
      http:
        endpoint: 0.0.0.0:4318
        tls:
          cert_file: /etc/ssl/certs/collector-cert.pem
          key_file: /etc/ssl/private/collector-key.pem
```

### Client-Side TLS (Exporters)

Configure TLS for exporters that connect to backends:

```yaml
exporters:
  otlp:
    endpoint: backend:443
    tls:
      cert_file: /etc/ssl/certs/client-cert.pem
      key_file: /etc/ssl/private/client-key.pem
      ca_file: /etc/ssl/certs/ca-cert.pem
      insecure: false
      insecure_skip_verify: false
```

### Mutual TLS (mTLS)

For mTLS, configure both client and server certificates:

```yaml
# Server side
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
        tls:
          cert_file: /etc/ssl/certs/server-cert.pem
          key_file: /etc/ssl/private/server-key.pem
          ca_file: /etc/ssl/certs/ca-cert.pem

# Client side
exporters:
  otlp:
    endpoint: collector:4317
    tls:
      cert_file: /etc/ssl/certs/client-cert.pem
      key_file: /etc/ssl/private/client-key.pem
      ca_file: /etc/ssl/certs/ca-cert.pem
```

### Common TLS Settings

Both server and client TLS configurations support:

- `cert_file` — path to TLS certificate file
- `key_file` — path to TLS private key file
- `ca_file` — path to CA certificate file
- `insecure` — disable TLS (not recommended for production)
- `insecure_skip_verify` — skip server certificate verification
- `cipher_suites` — list of cipher suites to use
- `min_version` — minimum TLS version (e.g., "1.2", "1.3")
- `max_version` — maximum TLS version

## Configuration Validation

Validate a configuration file before deploying:

```bash
otelcol validate --config=config.yaml
```

This checks for syntax errors, missing required fields, and component
compatibility issues.

## Examining the Final Configuration

Use command-line flags to inspect the resolved configuration:

```bash
# Print final configuration in YAML
otelcol --config=config.yaml --print-config

# Print final configuration in JSON
otelcol --config=config.yaml --print-config --as-json

# Show sensitive fields (normally masked)
otelcol --config=config.yaml --print-config --show-sensitive
```

## Checking Available Components

List components available in a Collector distribution:

```bash
otelcol --components
```

This outputs all receivers, processors, exporters, connectors, and extensions
compiled into the binary.

## Configuration Override Settings

### Simple Property Override

Override individual settings:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: ${ENV_ENDPOINT:-0.0.0.0:4317}
```

### Complex Nested Keys

Use double colons `::` for nested key references in YAML provider paths:

```
yaml:receivers::docker_stats::metrics::container.cpu.utilization::enabled: false
```

### Array Values

Override array values:

```yaml
service:
  pipelines:
    traces:
      processors: [${PROCESSORS_LIST:-memory_limiter,batch}]
```

## Security Best Practices

- Bind endpoints to `localhost` when all clients are local
- Use TLS for all network communications
- Rotate certificates regularly
- Use environment variables or secret managers for credentials
- Enable the health_check extension for load balancer health probes
- Follow the Collector hosting best practices and configuration best practices
  documented in the OpenTelemetry security guidelines
- The Collector defaults to `0.0.0.0` for endpoints but this will change to
  `localhost` in future releases — explicitly set endpoints

## Sending Queue and Retry Configuration

Configure resilience for exporters:

```yaml
exporters:
  otlp:
    endpoint: backend:4317
    sending_queue:
      enabled: true
      num_consumers: 10
      queue_size: 5000
      storage:
        id: file_storage  # enables persistent WAL
    retry_on_failure:
      enabled: true
      initial_interval: 5s
      max_interval: 30s
      max_elapsed_time: 10m
```

Key parameters:

- `queue_size` — maximum number of batches in the queue (default: 1000)
- `num_consumers` — number of worker goroutines sending data
- `initial_interval` — initial retry wait time
- `max_interval` — maximum retry wait time (exponential backoff cap)
- `max_elapsed_time` — total retry duration before dropping data (default: 5m)

Enable sending queues for any exporter sending data over a network. Monitor
queue metrics (`otelcol_exporter_queue_size`, `otelcol_exporter_queue_capacity`)
to detect backpressure.

# Management and OpAMP

## Fleet Management Overview

Managing telemetry collection at scale requires structured approaches to handle:

- Querying agent information (version, OS, capabilities)
- Applying new configurations to agents
- Upgrading/downgrading agents and managing packages
- Health and performance monitoring (CPU, memory, backpressure metrics)
- Connection management (TLS certificate rotation, revocation)

Not every use case requires all management capabilities. The OpenTelemetry
project provides OpAMP as the open-source standard for agent fleet management.

## OpAMP Protocol

Open Agent Management Protocol (OpAMP) defines how to manage a fleet of
telemetry data agents. It is vendor-agnostic and supports mixed fleets from
different vendors.

### Architecture

```
Control Plane                          Data Plane
┌─────────────┐                        ┌──────────────┐
│  OpAMP      │◄──── WebSocket ───────►│  OpAMP Client │
│  Server     │   or HTTP/REST         │  (Collector)  │
│  (orchestrator)                      │  or           │
└─────────────┘                        │  Supervisor   │
                                       └──────────────┘
```

- **OpAMP Server** — part of the control plane, acts as orchestrator managing
  a fleet of agents
- **OpAMP Client** — part of the data plane, implemented either in-process
  (within the Collector) or out-of-process (via a Supervisor)

### Communication Channels

OpAMP supports two transport modes:

- **WebSocket** — persistent bidirectional connection for real-time updates
- **HTTP/REST** — polling-based communication for simpler setups

## OpAMP Client Modes

### In-Process Client

The Collector itself implements the OpAMP client. The Collector connects
directly to the OpAMP server and receives configuration updates, status reports,
and package updates.

### Out-of-Process (Supervisor)

The OpAMP Supervisor is a separate binary that manages the Collector on behalf
of the OpAMP server. It handles OpAMP communication and controls the Collector
process — applying configurations, restarting, and upgrading.

## Setting Up OpAMP with Supervisor

### Step 1: Start an OpAMP Server

Using the Go reference implementation:

```bash
git clone https://github.com/open-telemetry/opamp-go.git
cd opamp-go/internal/examples/server
go run .
# Output: OpAMP Server running...
```

### Step 2: Install the Collector Binary

Download the appropriate distribution for your platform from the
[releases page](https://github.com/open-telemetry/opentelemetry-collector-releases/releases).

### Step 3: Install the OpAMP Supervisor

Download the `opampsupervisor` binary matching your OS and architecture:

```bash
# Linux AMD64
curl --proto '=https' --tlsv1.2 -fL -o opampsupervisor \
  "https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/cmd%2Fopampsupervisor%2Fv0.150.0/opampsupervisor_0.150.0_linux_amd64"
chmod +x opampsupervisor

# Linux ARM64
curl --proto '=https' --tlsv1.2 -fL -o opampsupervisor \
  "https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/cmd%2Fopampsupervisor%2Fv0.150.0/opampsupervisor_0.150.0_linux_arm64"
chmod +x opampsupervisor

# macOS ARM64
curl --proto '=https' --tlsv1.2 -fL -o opampsupervisor \
  "https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/cmd%2Fopampsupervisor%2Fv0.150.0/opampsupervisor_0.150.0_darwin_arm64"
chmod +x opampsupervisor
```

### Step 4: Create Supervisor Configuration

Create `supervisor.yaml`:

```yaml
server:
  endpoint: ws://127.0.0.1:4320/v1/opamp
  tls:
    insecure_skip_verify: true

capabilities:
  accepts_remote_config: true
  reports_effective_config: true
  accepts_package_updates: true
  reports_packages: true
  accepts_connection_settings: true
  reports_health: true
  reports_status: true

agent:
  path: /path/to/otelcol
  config_file: /path/to/config.yaml
  log_file: /path/to/collector.log
```

### Step 5: Run the Supervisor

```bash
./opampsupervisor --config supervisor.yaml
```

The supervisor starts the Collector, connects to the OpAMP server, and begins
reporting status. The control plane can now remotely configure and manage the
Collector.

## OpAMP Capabilities

The Supervisor and Collector report capabilities to the server:

- **accepts_remote_config** — server can push configuration updates
- **reports_effective_config** — agent reports its current configuration
- **accepts_package_updates** — server can push binary updates
- **reports_packages** — agent reports installed package versions
- **accepts_connection_settings** — server can configure connection credentials
- **reports_health** — agent reports health status
- **reports_status** — agent reports operational status

## Remote Configuration

With OpAMP, the control plane can push configuration changes to agents without
manual intervention:

1. Server sends new configuration YAML to the agent
2. Supervisor validates the configuration
3. If valid, Supervisor restarts the Collector with new configuration
4. Agent reports new effective configuration back to server
5. If invalid, agent reports error and keeps current configuration

## Agent Health Monitoring

OpAMP enables health monitoring of the fleet:

- **Health status** — whether the Collector is running normally
- **Component statuses** — individual receiver/exporter/processor health
- **Last error** — most recent error message from the agent
- **Uptime** — how long the current instance has been running

## OpAMP Own Telemetry

The Collector can send its own telemetry (metrics, logs) through OpAMP:

```yaml
service:
  telemetry:
    metrics:
      level: normal
    own_metrics:
      enabled: true
    own_traces:
      enabled: false
```

This allows the control plane to monitor Collector performance through the same
OpAMP connection used for management.

## Connection Management

OpAMP handles TLS certificate rotation and connection settings:

- Server can push new connection settings (certificates, credentials)
- Agent applies settings and reconnects with new credentials
- Supports certificate revocation notification
- Handles connection re-establishment on network failures

## Scaling Considerations

For large fleets:

- Use WebSocket transport for efficient bidirectional communication
- Deploy multiple OpAMP servers behind a load balancer
- Monitor server-side connection counts and message throughput
- Use agent grouping for batch configuration updates
- Implement rate limiting for configuration push operations

## Alternative Management Approaches

OpAMP is the recommended open standard, but alternatives include:

- **Configuration management tools** — Ansible, Chef, Puppet for file-based config
- **Kubernetes ConfigMaps/Secrets** — for K8s deployments with hot reload
- **HashiCorp Consul/Vault** — dynamic configuration and secret management
- **Custom control planes** — proprietary solutions from observability vendors

## Security Considerations

- Use TLS for all OpAMP connections (wss:// instead of ws://)
- Authenticate agents to the OpAMP server
- Validate configurations before applying
- Audit configuration changes through OpAMP server logs
- Rotate connection credentials regularly
- Follow OpenTelemetry security best practices for collector hosting and
  configuration

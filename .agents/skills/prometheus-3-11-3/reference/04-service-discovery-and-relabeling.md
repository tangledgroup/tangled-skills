# Service Discovery and Relabeling

## Contents
- Service Discovery Overview
- Static Configuration
- File-Based Service Discovery
- Kubernetes Service Discovery
- Docker and Container SD
- Cloud Provider SD (AWS, Azure, GCP)
- Other SD Mechanisms
- Relabeling Configuration
- Relabel Actions
- Target Relabeling vs Metric Relabeling

## Service Discovery Overview

Service discovery (SD) dynamically finds targets to scrape. Each SD mechanism exposes metadata as `__meta_<sdname>_<key>` labels per target, plus `__address__` with the host:port. Users select and transform targets via relabeling.

**Design principle**: SDs expose all available metadata without filtering. Customization is handled via relabeling — no business logic in the SD itself.

## Static Configuration

Simplest form — hardcoded targets:

```yaml
scrape_configs:
  - job_name: "static-targets"
    static_configs:
      - targets: ["localhost:9090", "server1:9100", "server2:9100"]
        labels:
          env: "production"
          datacenter: "us-east"
```

Targets are fixed at config load time. No dynamic updates.

## File-Based Service Discovery

Reads targets from JSON or YAML files, with optional polling for changes:

```yaml
file_sd_configs:
  - files:
      - "/etc/prometheus/targets/*.json"
      - "/etc/prometheus/targets/*.yml"
    refresh_interval: 5m
```

**JSON format**:
```json
[
  {
    "targets": ["localhost:9090", "localhost:9091"],
    "labels": {"env": "production"}
  }
]
```

**YAML format**:
```yaml
- targets:
    - "localhost:9090"
    - "localhost:9091"
  labels:
    env: "production"
```

Commonly used with configuration management tools (Ansible, Chef, Puppet) that generate target files.

## Kubernetes Service Discovery

Most feature-rich SD mechanism. Supports multiple roles:

```yaml
kubernetes_sd_configs:
  - role: pod                    # pod, endpoint, endpointSlice, service, node, ingression, namespace, certificate, secret, crd, cluster
    api_server: "https://k8s-api:6443"
    basic_auth:
      username: "user"
      password: "pass"
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    namespaces:
      names:
        - monitoring
        - production
    selectors:
      - role: pod
        label: "app=my-app"
        field: "status.phase=Running"
```

**Key metadata labels by role**:

| Role | Key Labels |
|------|-----------|
| `pod` | `__meta_kubernetes_pod_name`, `__meta_kubernetes_pod_namespace`, `__meta_kubernetes_pod_ip`, `__meta_kubernetes_pod_label_<labelname>`, `__meta_kubernetes_pod_container_port_name`, `__meta_kubernetes_pod_node_name`, `__meta_kubernetes_pod_deployment_name`, `__meta_kubernetes_pod_cronjob_name`, `__meta_kubernetes_pod_job_name` |
| `endpoint` | `__meta_kubernetes_endpoint_node_name`, `__meta_kubernetes_endpoint_target_kind`, `__meta_kubernetes_endpoint_target_name` |
| `service` | `__meta_kubernetes_service_name`, `__meta_kubernetes_service_namespace`, `__meta_kubernetes_service_label_<labelname>`, `__meta_kubernetes_service_annotation_<annotation>` |
| `node` | `__meta_kubernetes_node_name`, `__meta_kubernetes_node_label_<labelname>`, `__meta_kubernetes_node_address_<address_type>` |

**v3.11.0 additions**:
- Pod-based labels for deployment, cronjob, and job controller names
- Node role selectors for pod roles

### Typical Kubernetes Scrape Config

```yaml
scrape_configs:
  - job_name: "kubernetes-pods"
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # Only scrape pods with prometheus.io/scrape=true annotation
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: "true"
      # Use custom port from annotation
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
        target_label: __address__
        replacement: "$1:${1}"
      # Use custom path from annotation
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        target_label: __metrics_path__
      # Add pod labels as scrape labels
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
```

## Docker and Container SD

### Docker Swarm

```yaml
docker_swarm_sd_configs:
  - host: "unix:///var/run/docker.sock"
    role: tasks               # tasks, services, nodes, containers
    refresh_interval: 30s
    basic_auth:
      username: "user"
      password: "pass"
```

### Docker (via file_sd or custom adapter)

Docker does not have a native SD in Prometheus. Use `file_sd_configs` with a script that queries the Docker API, or use cAdvisor for container metrics.

## Cloud Provider Service Discovery

### AWS

```yaml
# EC2
ec2_sd_configs:
  - region: us-east-1
    access_key: "AKIAIOSFODNN7EXAMPLE"
    secret_key: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    port: 9100
    refresh_interval: 2m
    filter:
      - name: tag:monitoring
        values: ["true"]

# ECS
ecs_sd_configs:
  - region: us-east-1
    access_key: "AKIAIOSFODNN7EXAMPLE"
    secret_key: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    account_id: "123456789012"

# Unified AWS SD (v3.8.0+) — covers EC2, Lightsail, ECS
aws_sd_configs:
  - region: us-east-1
    services: ["ec2", "ecs"]
```

**AWS v3.11.0 additions**: Elasticache Role, RDS Role.

### Azure

```yaml
azure_sd_configs:
  - environment: "PublicCloud"    # PublicCloud, ChineseCloud, GermanCloud, USGovernmentCloud
    tenant_id: "tenant-id"
    client_id: "client-id"
    client_secret: "client-secret"
    subscription_id: "subscription-id"
    refresh_interval: 2m
    port: 9100
```

**v3.11.0 addition**: Azure Workload Identity authentication method.

### GCP

```yaml
gce_sd_configs:
  - project: "my-project"
    zone: "us-central1-a"
    refresh_interval: 2m
    filter: "labels.monitoring = true"
    port: 9100
```

### Other Cloud Providers

- **DigitalOcean**: `digitalocean_sd_configs`
- **Hetzner**: `hetzner_sd_configs` (roles: `hcloud`, `robot`)
- **Linode**: `linode_sd_configs`
- **OVHcloud**: `ovhcloud_sd_configs`
- **Scaleway**: `scaleway_sd_configs`
- **Vultr**: `vultr_sd_configs`
- **IONOS Cloud**: `ionos_sd_configs`
- **Stackit**: `stackit_sd_configs`
- **Uyuni**: `uyuni_sd_configs`

### Other SD Mechanisms

```yaml
# Consul
consul_sd_configs:
  - server: "consul:8500"
    token: "secret-token"
    services: ["my-service"]    # Empty = discover all services
    tags: ["monitoring"]
    namespace: "default"        # Consul Enterprise

# DNS
dns_sd_configs:
  - names:
      - "myservice.mydomain.com"
    type: A                     # A, SRV, MX
    refresh_interval: 30s

# HTTP
http_sd_configs:
  - url: "http://sd-server/targets"
    refresh_interval: 30s
    basic_auth:
      username: "user"
      password: "pass"

# Eureka
eureka_server_configs:
  - server: "http://eureka-server:8761"
    refresh_interval: 10s

# Marathon
marathon_sd_configs:
  - servers:
      - "http://marathon:8080"
    refresh_interval: 30s

# Nomad
nomad_sd_configs:
  - server: "nomad:4646"
    token: "secret"
    allow_stale: true

# OpenStack
openstack_sd_configs:
  - identity_endpoint: "https://openstack:5000/v3"
    username: "admin"
    password: "secret"
    refresh_interval: 2m

# PuppetDB
puppetdb_sd_configs:
  - server: "https://puppetdb:8081"
    query: "inventory[{name = 'prometheus'}]"
    refresh_interval: 2m

# TRITON
tron_sd_configs:
  - account: "my-account"
    url: "https://us-east-1.lc.joyent.com"
    refresh_interval: 2m

# Zookeeper
zookeeper_sd_configs:
  - servers:
      - "zookeeper:2181"
    refresh_interval: 30s
```

## Relabeling Configuration

Relabeling transforms target labels before scraping. Applied in order, each step receives the output of the previous step.

### Relabel Config Fields

| Field | Description |
|-------|-------------|
| `source_labels` | List of labels to concatenate as input |
| `separator` | String between concatenated values (default: `;`) |
| `regex` | Regex to match against concatenated value (default: `(.*)`, fully anchored) |
| `modulus` | Modulo value for `hashmod` action |
| `target_label` | Label to write result to |
| `replacement` | Replacement pattern with capture group references (default: `$1`) |
| `action` | Relabeling action to perform |

### Relabel Actions

| Action | Description |
|--------|-------------|
| `replace` | Regex replacement on target label (default) |
| `keep` | Drop targets not matching regex |
| `drop` | Drop targets matching regex |
| `keepequal` | Drop targets where source labels don't match target label value |
| `dropequal` | Drop targets where source labels match target label value |
| `hashmod` | Set target label to hash of source labels mod modulus |
| `labelmap` | Copy labels matching regex to new label names |
| `labeldrop` | Drop labels matching regex |
| `labelkeep` | Drop labels not matching regex |
| `lowercase` | Convert input to lowercase |
| `uppercase` | Convert input to uppercase |

### Common Relabeling Patterns

**Change port**:
```yaml
- source_labels: [__address__]
  regex: "(.+):.*"
  target_label: __address__
  replacement: "${1}:9100"
  action: replace
```

**Extract label from address**:
```yaml
- source_labels: [__address__]
  regex: "(.+):(\\d+)"
  target_label: instance
  replacement: "${1}"
```

**Add environment label from hostname**:
```yaml
- source_labels: [__meta_kubernetes_pod_node_name]
  regex: "prod-(.*)"
  target_label: environment
  replacement: "production"
```

**Drop internal metrics**:
```yaml
- source_labels: [__name__]
  regex: "go_.*"
  action: drop
```

**Hash-mod for load balancing across multiple Prometheus instances**:
```yaml
- source_labels: [__address__]
  modulus: 3
  target_label: __tmp_hash
  action: hashmod
- source_labels: [__tmp_hash]
  regex: "0"    # This Prometheus instance number
  action: keep
```

**Label map — copy all `__meta_*` labels**:
```yaml
- regex: "__meta_kubernetes_pod_label_(.*)"
  replacement: "${1}"
  action: labelmap
```

## Target Relabeling vs Metric Relabeling

- **`relabel_configs`**: Applied to target metadata before scraping. Can modify scrape URL, path, and labels. Runs once per target discovery cycle.
- **`metric_relabel_configs`**: Applied to scraped metrics after the scrape. Can filter or transform individual metric series. Runs every scrape cycle.

Use target relabeling for discovery-level filtering. Use metric relabeling for per-metric filtering and transformation.

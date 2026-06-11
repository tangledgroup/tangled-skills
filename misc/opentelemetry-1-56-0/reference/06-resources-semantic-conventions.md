# Resources and Semantic Conventions

## Resource Data Model

A Resource represents the observed entity for which telemetry is produced. It identifies the source of telemetry, not the component that technically produces it (e.g., an auto-instrumentation agent).

### Clarification in 1.56.0

The specification now explicitly clarifies that a Resource describes the **observed entity**, not the component that technically emits telemetry. This distinction is important for auto-instrumentation scenarios where the instrumentation agent is separate from the application being observed.

### Structure

A resource is composed of:

- **Entities**: Structured identity information (Development status)
- **Attributes**: Raw key-value pairs identifying the resource

Example hierarchy for a process in Kubernetes:

```
Cloud Provider → Region → Account
  └── Kubernetes Cluster
      └── Namespace
          └── Deployment
              └── Pod
                  └── Container
                      └── Process (with runtime info)
```

### Identity

- The identity of a resource is the set of entities it contains
- Two resources are different if one contains an entity not found in the other
- Raw attributes are also considered identifying — different key-value pairs mean different resources
- Resources MUST NOT change during the lifetime of the resource

### Merging Resources

Merging joins together the context of observation, preserving existing identity while adding new details:

1. Construct a set of existing entities on the resource
2. For each new entity (highest priority first):
   - If an entity with the same type exists → perform Entity Data Model merge
   - Otherwise → add the new entity
3. Raw attributes from higher-priority sources take precedence

### Entities Merge Algorithm (Defined in 1.56.0)

The specification now formally defines the entities merge algorithm, providing deterministic behavior for combining entity data from multiple sources. This ensures consistent resource identity across distributed systems.

## Resource SDK

The SDK provides mechanisms for:

- Detecting resource information automatically (e.g., process, host, container)
- Merging detected resources with manually configured resources
- Associating the Resource with all telemetry produced by a Provider

### Environment Variable Configuration

```bash
# Set resource attributes via environment
export OTEL_RESOURCE_ATTRIBUTES="service.name=my-api,service.version=1.2.3,deployment.environment=production"

# Set service name directly
export OTEL_SERVICE_NAME="my-api-service"
```

### Declarative Configuration (1.56.0)

In-development guidance for exposing the effective `Resource` returned by `Create`. Spec changes must now consider the declarative configuration schema impact.

## Semantic Conventions

Semantic Conventions define standardized keys and values for commonly observed concepts, protocols, and operations. They are maintained in a separate repository: `https://github.com/open-telemetry/semantic-conventions`.

### Key Categories

- **Resource attributes**: Cloud provider, container, Kubernetes, host, OS, process, service
- **Span attributes**: HTTP, RPC (gRPC, Connect, Dubbo, JSON-RPC), database, messaging
- **Log attributes**: Event names, severity mappings
- **Metric attributes**: Runtime metrics (JVM, Go, .NET, Node.js, CPython), system metrics

### Common Resource Attributes

```
service.name              # Required for most services
service.version           # Service version string
service.instance.id       # Unique service instance identifier
cloud.provider            # aws, azure, gcp
cloud.region              # e.g., us-east-1
cloud.account.id          # Cloud account/subscription ID
container.name            # Container name
container.id              # Container runtime identifier
k8s.pod.name              # Kubernetes pod name
k8s.pod.uid               # Kubernetes pod UID
k8s.namespace.name        # Kubernetes namespace
k8s.deployment.name       # Kubernetes deployment name
host.name                 # Hostname
host.architecture         # e.g., x86_64, arm64
os.type                   # e.g., linux, windows
os.description            # Human-readable OS description
process.pid               # Process ID
process.runtime.name      # e.g., python, go, java
process.runtime.version   # Runtime version
```

### Attribute Naming Conventions

- Keys use lowercase letters, digits, hyphens, dots, and underscores
- Dot notation for hierarchical grouping: `http.method`, `db.system`
- Semantic convention groups use reverse domain style where appropriate

### Instrumentation Scope vs Resource

- **Instrumentation Scope**: Identifies the library/component producing telemetry (e.g., `io.opentelemetry.contrib.mongodb/2.3.0`)
- **Resource**: Identifies the entity being observed (e.g., a specific pod in a specific namespace)

## Attribute Data Types

Attributes use AnyValue which supports:

- **Primitives**: string, boolean, double (IEEE 754), signed 64-bit integer
- **Arrays**: Homogeneous arrays of primitive values or arrays of AnyValue
- **Maps**: `map<string, AnyValue>` with unique keys
- **Byte arrays**: Raw binary data
- **Empty values**: null/None/nil (language-dependent)

Arbitrary deep nesting is allowed for arrays and maps.

### Attribute Limits

Configurable to control memory usage:

- Maximum number of attributes per signal
- Maximum attribute value length
- Limits apply at SDK level, not API level

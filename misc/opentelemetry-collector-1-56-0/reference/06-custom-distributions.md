# Custom Distributions

## OpenTelemetry Collector Builder (ocb)

The OpenTelemetry Collector Builder (`ocb`) generates a custom Collector binary
based on a YAML manifest configuration. It allows you to include specific
components, create smaller binaries, or add custom components not available in
official distributions.

## Installation

### Docker Image (Recommended)

```bash
docker pull otel/opentelemetry-collector-builder:latest
```

Run with mounted configuration:

```bash
docker run \
  -v "$(pwd)/builder-config.yaml:/build/builder-config.yaml" \
  -v "$(pwd)/output:/build/otelcol-dev" \
  otel/opentelemetry-collector-builder:latest \
  --config=/build/builder-config.yaml
```

### Binary Download

Download from [releases](https://github.com/open-telemetry/opentelemetry-collector-releases/releases?q=cmd%2Fbuilder):

```bash
# Linux AMD64
curl --proto '=https' --tlsv1.2 -fL -o ocb \
  https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/cmd%2Fbuilder%2Fv0.150.0/ocb_0.150.0_linux_amd64
chmod +x ocb

# macOS ARM64
curl --proto '=https' --tlsv1.2 -fL -o ocb \
  https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/cmd%2Fbuilder%2Fv0.150.0/ocb_0.150.0_darwin_arm64
chmod +x ocb
```

### Go Install

```bash
go install go.opentelemetry.io/collector/cmd/builder@latest
```

## Manifest Configuration

The `ocb` manifest has two main sections: `dist` (distribution settings) and
module types (components to include).

### Basic Manifest

```yaml
dist:
  name: otelcol-custom
  description: "Custom OpenTelemetry Collector distribution"
  output_path: ./output
  go: ../go  # optional: path to Go installation

receivers:
  - gomod: go.opentelemetry.io/collector/receiver/otlpreceiver v0.150.0
  - gomod: github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver v0.150.0

processors:
  - gomod: go.opentelemetry.io/collector/processor/batchprocessor v0.150.0
  - gomod: go.opentelemetry.io/collector/processor/memorylimiterprocessor v0.150.0

exporters:
  - gomod: go.opentelemetry.io/collector/exporter/otlpexporter v0.150.0
  - gomod: go.opentelemetry.io/collector/exporter/debugexporter v0.150.0

extensions:
  - gomod: go.opentelemetry.io/collector/extension/healthcheckextension v0.150.0
  - gomod: go.opentelemetry.io/collector/extension/pprofextension v0.150.0

providers:
  - gomod: go.opentelemetry.io/collector/confmap/provider/envprovider v1.50.0
  - gomod: go.opentelemetry.io/collector/confmap/provider/fileprovider v1.50.0
  - gomod: go.opentelemetry.io/collector/confmap/provider/yamlprovider v1.50.0
```

### dist Section Options

- **module** — Go module name for the distribution (default:
  `go.opentelemetry.io/collector/cmd/builder`)
- **name** — binary name (default: `otelcol-custom`)
- **description** — description of the distribution
- **output_path** — where to write the built binary
- **version** — version string for the binary
- **replaces** — module replacement mappings for local development
- **work** — keep generated Go module directory after build (for debugging)

### Module Entry Format

Each component requires at minimum a `gomod` entry specifying the Go module path
and version:

```yaml
exporters:
  - gomod: github.com/open-telemetry/opentelemetry-collector-contrib/exporter/kafkaexporter v0.150.0
```

Optional fields:

- **import** — specific import path within the module (inferred from gomod if omitted)
- **name** — component name override (needed when multiple components share a name)

### Building

```bash
./ocb --config=builder-config.yaml
```

The output binary is written to the `output_path` directory specified in the manifest.

## Including Contrib Components

Contrib repository components use the GitHub module path:

```yaml
receivers:
  - gomod: github.com/open-telemetry/opentelemetry-collector-contrib/receiver/hostmetricsreceiver v0.150.0
  - gomod: github.com/open-telemetry/opentelemetry-collector-contrib/receiver/jaegerreceiver v0.150.0

exporters:
  - gomod: github.com/open-telemetry/opentelemetry-collector-contrib/exporter/prometheusremotewriteexporter v0.150.0
```

## Building Custom Components

### Setting Up a Custom Component

To develop a custom receiver, processor, exporter, connector, or extension:

1. Create a Go module for your component
2. Implement the required interfaces from the Collector SDK
3. Reference it in the ocb manifest using `replaces`

### Manifest with Local Component

```yaml
dist:
  name: otelcol-custom
  output_path: ./output
  replaces:
    - github.com/myorg/myreceiver=../myreceiver

receivers:
  - gomod: github.com/myorg/myreceiver v0.0.0

exporters:
  - gomod: go.opentelemetry.io/collector/exporter/debugexporter v0.150.0

providers:
  - gomod: go.opentelemetry.io/collector/confmap/provider/envprovider v1.50.0
  - gomod: go.opentelemetry.io/collector/confmap/provider/fileprovider v1.50.0
  - gomod: go.opentelemetry.io/collector/confmap/provider/yamlprovider v1.50.0
```

### Debugging Custom Components

Build with debug symbols for IDE debugging:

```bash
# Retain debug symbols
./ocb --ldflags="" --config=builder-config.yaml

# Full debug mode (disables inlining and optimizations)
./ocb --ldflags="" --gcflags="all=-N -l" --config=builder-config.yaml
```

Debug with Delve:

```bash
dlv --listen=:2345 --headless=true --api-version=2 \
  --accept-multiclient --log exec ./output/otelcol-custom \
  -- --config=config.yaml
```

## Containerizing Custom Distributions

Build a Docker image for your custom Collector:

```dockerfile
FROM alpine:3.19 AS alpine

FROM scratch
COPY --from=alpine /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY output/otelcol-custom /bin/otelcol-custom
ENTRYPOINT ["/bin/otelcol-custom"]
```

Build and run:

```bash
docker build -t otelcol-custom .
docker run -p 4317:4317 -p 4318:4318 otelcol-custom --config=/etc/otel/config.yaml
```

## Component Version Compatibility

When building custom distributions:

- Use compatible versions of core and contrib components
- Check the `manifest.yaml` in official distributions for known-good combinations
- Core components are versioned under `go.opentelemetry.io/collector/`
- Contrib components are versioned under `github.com/open-telemetry/opentelemetry-collector-contrib/`
- Configuration providers (env, file, yaml) have separate versioning from the Collector core

## Using ocb for Development Workflow

The recommended workflow for developing custom components:

1. Create a minimal manifest with your component and debug exporter
2. Use `replaces` to point to local source
3. Build with `--work` flag to keep the generated Go module
4. Run the Collector with `dlv` for debugging
5. Iterate on component code, rebuild, and test

```yaml
# Development manifest
dist:
  name: otelcol-dev
  output_path: ./bin
  work: true
  replaces:
    - github.com/myorg/myprocessor=../myprocessor

processors:
  - gomod: github.com/myorg/myprocessor v0.0.0
  - gomod: go.opentelemetry.io/collector/processor/memorylimiterprocessor v0.150.0

exporters:
  - gomod: go.opentelemetry.io/collector/exporter/debugexporter v0.150.0

receivers:
  - gomod: go.opentelemetry.io/collector/receiver/otlpreceiver v0.150.0

providers:
  - gomod: go.opentelemetry.io/collector/confmap/provider/envprovider v1.50.0
  - gomod: go.opentelemetry.io/collector/confmap/provider/fileprovider v1.50.0
  - gomod: go.opentelemetry.io/collector/confmap/provider/yamlprovider v1.50.0
```

## CLI Flags

The `ocb` command supports several flags that override manifest settings:

- `--config` — path to the manifest YAML file (required)
- `--set` — override a dist property (e.g., `--set version=1.0.0`)
- `--output` — override output path
- `--go` — path to Go binary
- `--ldflags` — custom linker flags
- `--gcflags` — custom compiler flags
- `--trimpath` — remove file system paths from binary (default: true)
- `--mod` — Go module mode

Run `ocb --help` for the complete list of available flags.

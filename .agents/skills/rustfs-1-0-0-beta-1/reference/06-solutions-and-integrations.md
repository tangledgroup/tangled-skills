# Solutions and Integrations

## Data Lake Architecture

RustFS serves as the storage layer for modern data lake architectures:

- **Apache Iceberg**: Table format with ACID transactions on S3-compatible storage
- **Apache Hudi**: Upsert and delete support for streaming data lakes
- **Delta Lake**: Open-source delta format for reliable data lakes
- **Presto/Trino**: SQL query engine accessing data directly from RustFS
- **Apache Spark**: Distributed computing with S3A connector

```python
# Spark example
spark.read \
    .format("iceberg") \
    .load("s3a://my-bucket/tables/events/") \
    .createOrReplaceTempView("events")

spark.sql("SELECT * FROM events WHERE date > '2025-01-01'").show()
```

## AI and Machine Learning

RustFS stores training datasets, model artifacts, and inference outputs:

- **PyTorch**: `torch.hub` with S3-compatible storage backends
- **TensorFlow**: TFRecord files on RustFS for distributed training
- **Hugging Face**: Model hub integration via S3 API
- **MLflow**: Experiment tracking with RustFS as artifact store

## Cloud Native

RustFS integrates with Kubernetes ecosystems:

- **Helm Chart**: Deploy via `charts.rustfs.com` (beta.1 fixes rollingUpdate rendering)
- **CSI Driver**: Persistent volume claims backed by RustFS buckets
- **Service Mesh**: Compatible with Istio, Linkerd for mTLS and traffic management

## Big Data Computing Storage Separation

Decouple compute from storage:

- Spin up ephemeral compute clusters (Spark, Presto) that read/write to persistent RustFS
- Scale compute independently of storage capacity
- Reduce costs by using spot/preemptible instances for compute while keeping data on reliable storage

## SQL Support

Query data directly from RustFS using SQL engines:

- **DuckDB**: `SELECT * FROM read_csv_auto('s3://bucket/data.csv')`
- **DuckDB HTTP Filesystem**: Access via REST API
- **Presto/Trino**: Full SQL support with S3 connectors

## Cold Archive Storage

Long-term data retention with lifecycle rules:

- Transition objects to cold storage tiers after configurable periods
- WORM compliance for regulatory requirements
- Cross-region replication for disaster recovery

## Observability Stack (beta.1)

The beta.1 release improves metrics coverage and dashboard performance:

- **Prometheus**: Built-in `/metrics` endpoint with comprehensive RustFS metrics
- **Grafana**: Pre-built dashboards for storage, network, and erasure coding health
- **Jaeger/Tempo**: Distributed tracing via OpenTelemetry integration
- **Profiling export**: Disabled by default in beta.1 (fixes Helm env name for profiling config)

Deploy the full observability stack with Docker Compose:

```bash
docker compose --profile observability up -d
```

This starts RustFS alongside Grafana, Prometheus, and Jaeger containers pre-configured for monitoring.

## SQL Server Integration

RustFS supports Azure Blob Storage-compatible APIs, enabling integration with Microsoft SQL Server external tables and polybase queries against object storage.

## Video Storage Solution

Optimized for video workflows:

- Range requests for streaming playback
- Multipart upload for large video files
- Lifecycle rules to archive completed productions
- Presigned URLs for secure client-side access

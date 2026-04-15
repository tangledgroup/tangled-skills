# Deployment with Text Embeddings Inference (TEI)

Production deployment of Qwen3 Embedding models using Hugging Face's Text Embeddings Inference for high-performance serving.

## What is TEI?

Text Embeddings Inference (TEI) is a production-ready inference server optimized for embedding models, providing:

- **High throughput**: 10x faster than naive implementations
- **Low latency**: Optimized for real-time applications
- **REST API**: Standard HTTP/JSON interface
- **Batching**: Automatic request batching
- **Quantization**: FP16 and INT8 support
- **Monitoring**: Built-in metrics and health checks

## Quick Start with Docker

### Basic Deployment

```bash
# Deploy Qwen3-Embedding-4B with TEI
docker run --gpus all --shm-size 1g -p 8080:80 \
  ghcr.io/huggingface/text-embeddings-inference/server-gpu:latest \
  --model-id Qwen/Qwen3-Embedding-4B \
  --max-concurrent-requests 16
```

### With Custom Settings

```bash
docker run --gpus all --shm-size 1g -p 8080:80 \
  ghcr.io/huggingface/text-embeddings-inference/server-gpu:latest \
  --model-id Qwen/Qwen3-Embedding-8B \
  --max-concurrent-requests 32 \
  --max-batch-tokens 4096 \
  --chunk-sizes 512,256,128 \
  --quantize fp16 \
  --api-key your-secret-key
```

### CPU-Only Deployment

```bash
docker run --shm-size 1g -p 8080:80 \
  ghcr.io/huggingface/text-embeddings-inference/server-cpu:latest \
  --model-id Qwen/Qwen3-Embedding-0.6B \
  --max-concurrent-requests 8
```

## API Usage

### Health Check

```bash
curl http://localhost:8080/health
# {"status":"ok"}
```

### Embedding Generation

```bash
# Single text
curl -X POST http://localhost:8080/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": "The cat sits on the mat."
  }'

# Response:
# {
#   "embeddings": [
#     {"embedding": [0.123, -0.456, ...], "text": "The cat sits on the mat.", "model_name": "Qwen/Qwen3-Embedding-4B"}
#   ]
# }

# Batch request
curl -X POST http://localhost:8080/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": [
      "First document to encode.",
      "Second document with different content.",
      "Third document for batch processing."
    ]
  }'
```

### With Authentication

```bash
curl -X POST http://localhost:8080/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-key" \
  -d '{"input": "Hello world"}'
```

## Python Client Integration

### Using requests

```python
import requests
import json

TEI_URL = "http://localhost:8080"

def encode_texts(texts, normalize=True):
    """Encode texts using TEI server"""
    if isinstance(texts, str):
        texts = [texts]
    
    response = requests.post(
        f"{TEI_URL}/embeddings",
        json={
            "input": texts,
            "normalize": normalize
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"TEI error: {response.text}")
    
    result = response.json()
    embeddings = [r["embedding"] for r in result["embeddings"]]
    
    return embeddings

# Usage
texts = ["Document one", "Document two", "Document three"]
embeddings = encode_texts(texts, normalize=True)
print(f"Encoded {len(embeddings)} texts with dimension {len(embeddings[0])}")
```

### Using httpx (Async)

```python
import httpx

async def encode_async(texts):
    """Async encoding for high-throughput applications"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8080/embeddings",
            json={"input": texts}
        )
        
        return response.json()["embeddings"]

# Usage in async application
import asyncio

texts = ["Query 1", "Query 2", "Query 3"]
embeddings = asyncio.run(encode_async(texts))
```

### Rate Limiting and Retries

```python
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def encode_with_retry(texts):
    """Encode with automatic retries on failure"""
    response = requests.post(
        "http://localhost:8080/embeddings",
        json={"input": texts},
        timeout=30  # 30 second timeout
    )
    
    response.raise_for_status()
    return response.json()["embeddings"]

# Usage
try:
    embeddings = encode_with_retry(["Important document"])
except Exception as e:
    print(f"Failed after retries: {e}")
```

## Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qwen3-embedding-tei
spec:
  replicas: 3
  selector:
    matchLabels:
      app: embedding-service
  template:
    metadata:
      labels:
        app: embedding-service
    spec:
      containers:
      - name: tei
        image: ghcr.io/huggingface/text-embeddings-inference/server-gpu:latest
        args:
          - --model-id
          - Qwen/Qwen3-Embedding-4B
          - --max-concurrent-requests
          - "32"
          - --port
          - "8080"
        ports:
        - containerPort: 8080
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            memory: "8Gi"
            cpu: "4"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: embedding-service
spec:
  selector:
    app: embedding-service
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: embedding-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: qwen3-embedding-tei
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Performance Tuning

### Model-Specific Settings

| Model | GPU Memory | Max Concurrent | Max Batch Tokens | Recommended Instance |
|-------|------------|----------------|------------------|---------------------|
| 0.6B | 2GB | 32 | 8192 | g4dn.xlarge (T4) |
| 4B | 8GB | 16 | 4096 | g5.xlarge (A10G) |
| 8B | 16GB | 8 | 2048 | g5.2xlarge (A10G) |

### Optimizing Throughput

```bash
# High-throughput configuration for batch processing
docker run --gpus all -p 8080:80 \
  ghcr.io/huggingface/text-embeddings-inference/server-gpu:latest \
  --model-id Qwen/Qwen3-Embedding-4B \
  --max-concurrent-requests 64 \
  --max-batch-tokens 8192 \
  --chunk-sizes 512,256 \
  --dtype float16
```

### Optimizing Latency

```bash
# Low-latency configuration for real-time applications
docker run --gpus all -p 8080:80 \
  ghcr.io/huggingface/text-embeddings-inference/server-gpu:latest \
  --model-id Qwen/Qwen3-Embedding-0.6B \
  --max-concurrent-requests 8 \
  --max-batch-tokens 2048 \
  --response-timeout 60
```

## Monitoring and Observability

### Prometheus Metrics

TEI exposes Prometheus metrics at `/metrics`:

```bash
curl http://localhost:8080/metrics | grep tei_
```

Key metrics:
- `tei_requests_total`: Total number of requests
- `tei_request_duration_seconds`: Request latency
- `tei_queue_size`: Current queue size
- `tei_model_load_time_seconds`: Model loading time

### Grafana Dashboard

Create a Prometheus data source and import dashboard with these panels:
- Request rate (requests/second)
- P50, P95, P99 latency
- Queue depth over time
- GPU utilization (if available)

### Health Monitoring

```python
import requests
import time

def monitor_health(base_url, interval=60):
    """Monitor TEI server health"""
    while True:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"{time.strftime('%H:%M:%S')} - Server healthy")
            else:
                print(f"{time.strftime('%H:%M:%S')} - Server unhealthy: {response.status_code}")
        except Exception as e:
            print(f"{time.strftime('%H:%M:%S')} - Server unreachable: {e}")
        
        time.sleep(interval)

# Usage
monitor_health("http://localhost:8080")
```

## Cost Optimization

### Spot Instances (AWS)

```yaml
# Use spot instances for cost savings
spec:
  template:
    spec:
      containers:
      - name: tei
        resources:
          limits:
            nvidia.com/gpu: 1
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: kubernetes.io/instance-category
                operator: In
                values:
                - spot
```

### Auto-Scaling to Zero

For intermittent workloads, use KEDA or similar tools to scale to zero when not in use.

## Security Considerations

### API Key Authentication

```bash
# Start server with authentication
docker run -p 8080:80 \
  -e HUGGING_FACE_HUB_TOKEN=your-token \
  ghcr.io/huggingface/text-embeddings-inference/server-gpu:latest \
  --model-id Qwen/Qwen3-Embedding-4B \
  --api-key your-secret-api-key
```

### Network Security

- Use TLS/HTTPS in production
- Restrict access via firewall rules
- Use VPC endpoints for cloud deployments
- Enable request rate limiting

## See Also

- [`references/10-optimization.md`](10-optimization.md) - Performance optimization
- [`references/01-model-variants.md`](01-model-variants.md) - Model selection guide
- TEI Documentation: https://github.com/huggingface/text-embeddings-inference

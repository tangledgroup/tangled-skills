# Podman Kubernetes Integration

This reference covers generating Kubernetes manifests from Podman containers/pods and playing Kubernetes manifests with Podman for local development and testing.

## Overview

Podman provides bidirectional Kubernetes integration:
- **Generate**: Convert running containers/pods to Kubernetes YAML manifests
- **Play**: Run containers/pods directly from Kubernetes YAML files

This enables:
- Local development with K8s manifests
- Testing K8s configurations before deployment
- Migration paths between Podman and Kubernetes
- Portable container definitions

## Generate Kubernetes Manifests

### From Single Container

```bash
# Generate Deployment manifest
podman generate kube mycontainer > deployment.yaml

# Generate with specific options
podman generate kube \
  --name=myapp \
  --latest-tag-image=false \
  mycontainer > deployment.yaml

# Include config maps and secrets
podman generate kube \
  --add-dockerfile \
  --cert-dir=/path/to/certs \
  mycontainer > deployment.yaml
```

### From Pod

```bash
# Generate pod manifest from Podman pod
podman generate kube mypod > pod.yaml

# Multiple containers in pod become K8s Pod spec
podman pod ps
podman generate kube mypod > multi-container-pod.yaml
```

### From Containerfile

```bash
# Build image first
podman build -t myapp:latest .

# Generate deployment from image
podman generate kube --image=myapp:latest > deployment.yaml
```

## Play Kubernetes Manifests

### Basic Usage

```bash
# Play a Deployment
podman play kube deployment.yaml

# Play a Pod
podman play kube pod.yaml

# Play with custom name prefix
podman play kube --name=myapp- deployment.yaml

# Detached mode (don't wait for completion)
podman play kube -d deployment.yaml
```

### Play Options

```bash
# Generate logs during play
podman play kube --log-level=debug deployment.yaml

# Use specific log driver
podman play kube --log-driver=journald deployment.yaml

# Specify storage opts
podman play kube --storage-opt=size=10G deployment.yaml

# Start containers immediately
podman play kube --start=true deployment.yaml
```

### Play and Stop

```bash
# Stop resources created by play kube
podman stop kube_<resource-name>

# Remove resources
podman rm kube_<resource-name>

# Clean up all kube resources
podman ps -a --filter label=io.kubernetes.pod.name | \
  awk 'NR>1 {print $1}' | xargs podman rm -f
```

## Supported Kubernetes Resources

### Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
    volumeMounts:
    - name: data
      mountPath: /usr/share/nginx/html
  volumes:
  - name: data
    hostPath:
      path: /data
```

Play with Podman:
```bash
podman play kube pod.yaml
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

Play with Podman:
```bash
# Creates pods based on replicas
podman play kube deployment.yaml
```

### Service (Limited Support)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

**Note:** Podman play kube has limited Service support. Port mapping is applied to containers directly.

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  config.json: |
    {"key": "value"}
  ENV_VAR: "production"
```

Used with Deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest
        envFrom:
        - configMapRef:
            name: app-config
        volumeMounts:
        - name: config-volume
          mountPath: /etc/config
      volumes:
      - name: config-volume
        configMap:
          name: app-config
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded "admin"
  password: c2VjcmV0  # base64 encoded "secret"
```

Create secret manually for Podman:
```bash
# Create secret for use with play kube
podman secret create db-user <(echo -n "admin")
podman secret create db-pass <(echo -n "secret")
```

## Generate Options and Customization

### Image Tag Handling

```bash
# Use latest tag (default behavior)
podman generate kube mycontainer > deployment.yaml
# Result: image: myregistry/myapp:latest

# Disable latest tag conversion
podman generate kube --latest-tag-image=false mycontainer > deployment.yaml
# Result: image: myregistry/myapp@sha256:<digest>
```

### Add Dockerfile

```bash
# Include Dockerfile in generated manifest
podman generate kube --add-dockerfile mycontainer > deployment-with-build.yaml

# Creates ConfigMap with Containerfile for building
```

### Certificate Handling

```bash
# Include certificates for registry authentication
podman generate kube \
  --cert-dir=/path/to/certs \
  mycontainer > deployment.yaml
```

### Name Customization

```bash
# Customize resource names in generated YAML
podman generate kube --name=custom-name mycontainer > deployment.yaml
```

## Common Patterns

### Development Workflow

```bash
# 1. Develop with Podman locally
podman run -it --rm \
  -v $(pwd):/app \
  -w /app \
  node:18-alpine npm run dev

# 2. Commit to image
podman build -t myapp:dev .

# 3. Generate K8s manifest for testing
podman generate kube --image=myapp:dev > deployment.yaml

# 4. Test with play kube
podman play kube deployment.yaml

# 5. Iterate and refine manifest
# Edit deployment.yaml, re-run play kube

# 6. Deploy to actual cluster when ready
kubectl apply -f deployment.yaml
```

### Multi-Container Application

```bash
# Create pod with multiple containers
podman pod create --name webapp-pod
podman run -d --pod webapp-pod --name web nginx
podman run -d --pod webapp-pod --name db postgres

# Generate K8s Pod manifest
podman generate kube webapp-pod > k8s-pod.yaml

# Test locally
podman play kube k8s-pod.yaml

# Deploy to cluster
kubectl apply -f k8s-pod.yaml
```

### Environment-Specific Configurations

```bash
# Generate base manifest
podman generate kube mycontainer > base-deployment.yaml

# Create environment-specific overrides
cat > dev-overrides.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: myapp
        env:
        - name: ENV
          value: development
        - name: DEBUG
          value: "true"
EOF

# Apply with kubectl --patch or use kustomize
```

### CI/CD Integration

```bash
# In CI pipeline:
# 1. Build and test image
podman build -t myapp:$CI_BUILD_NUMBER .

# 2. Generate K8s manifests
podman generate kube --image=myapp:$CI_BUILD_NUMBER > deployment.yaml

# 3. Validate manifest with play kube (dry run)
podman play kube -d deployment.yaml

# 4. Push image to registry
podman push myapp:$CI_BUILD_NUMBER registry.example.com/myapp:$CI_BUILD_NUMBER

# 5. Update manifest with registry path
sed -i 's|myapp:|registry.example.com/myapp:|' deployment.yaml

# 6. Deploy to cluster
kubectl apply -f deployment.yaml
```

## Compatibility Notes

### Supported Features

- ✅ Pod specs (containers, volumes, env vars)
- ✅ Deployment specs (replicas, selectors, templates)
- ✅ ConfigMaps (as environment variables and volume mounts)
- ✅ Secrets (with podman secret pre-creation)
- ✅ Resource limits and requests
- ✅ Volume mounts (hostPath, emptyDir, ConfigMap, Secret)
- ✅ Port mappings
- ✅ Health checks (livenessProbe, readinessProbe)

### Limited or Unsupported Features

- ⚠️ Services (port mapping applied directly to containers)
- ⚠️ Ingress resources (not supported)
- ❌ PersistentVolume/PersistentVolumeClaim (use hostPath instead)
- ❌ StatefulSets (use Deployment equivalent)
- ❌ DaemonSets (not supported)
- ❌ Jobs/CronJobs (not supported)
- ❌ NetworkPolicies (not enforced)

### Workarounds for Limitations

#### Persistent Volumes

```yaml
# Instead of PVC, use hostPath
volumes:
- name: data
  hostPath:
    path: /var/lib/podman/data
    type: DirectoryOrCreate
```

#### Service Discovery

```bash
# Use podman network for service discovery
podman network create app-network

podman play kube --network=app-network deployment.yaml

# Containers can resolve each other by name within network
```

#### Scaling

```bash
# Play kube creates containers based on replicas
podman play kube deployment.yaml  # Creates 3 containers if replicas: 3

# Or manually scale with podman
for i in {1..3}; do
  podman run -d --name myapp-$i myapp:latest
done
```

## Testing Kubernetes Manifests Locally

### Validate Manifest Syntax

```bash
# Play kube will fail if manifest is invalid
podman play kube deployment.yaml

# Check exit code
if [ $? -eq 0 ]; then
  echo "Manifest is valid"
else
  echo "Manifest has errors"
fi
```

### Test Health Checks

```bash
# Play deployment with health checks
podman play kube deployment.yaml

# Monitor container status
podman ps --filter label=io.kubernetes.pod.name

# Check logs for health check failures
podman logs kube_<container-name>
```

### Verify Resource Limits

```bash
# Play with resource constraints
podman play kube deployment.yaml

# Verify limits applied
podman inspect kube_<container-name> | grep -A5 HostConfig

# Monitor actual usage
podman stats --no-stream kube_<container-name>
```

## Migration from Docker to Kubernetes

### Step 1: Run with Podman

```bash
# Convert Docker commands to Podman
docker run -d -p 8080:80 --name myapp myimage:latest
# becomes:
podman run -d -p 8080:80 --name myapp myimage:latest
```

### Step 2: Generate Kubernetes Manifest

```bash
# Create deployment manifest
podman generate kube myapp > deployment.yaml
```

### Step 3: Refine for Production

```yaml
# Add production-ready configurations
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      containers:
      - name: myapp
        image: myregistry/myapp:v1.0.0
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Step 4: Test Locally

```bash
# Test with play kube
podman play kube deployment.yaml

# Verify functionality
curl http://localhost:8080/health

# Clean up
podman rm -f $(podman ps -aq --filter label=io.kubernetes.pod.name)
```

### Step 5: Deploy to Cluster

```bash
# Deploy to Kubernetes cluster
kubectl apply -f deployment.yaml

# Monitor rollout
kubectl rollout status deployment/myapp
```

## Troubleshooting

### Play Kube Fails

```bash
# Check manifest syntax
cat deployment.yaml | yq .  # Validate YAML

# Run with debug logging
podman play kube --log-level=debug deployment.yaml

# Verify image is available
podman pull nginx:1.21

# Check for port conflicts
sudo ss -tlnp | grep :80
```

### Generated Manifest Issues

```bash
# Inspect container before generating
podman inspect mycontainer

# Generate with verbose output
podman generate kube --log-level=debug mycontainer

# Compare generated manifest with expected
diff generated.yaml expected.yaml
```

### Resource Cleanup

```bash
# List all kube-created resources
podman ps -a --filter label=io.kubernetes.pod.name

# Remove all kube resources
podman rm -f $(podman ps -aq --filter label=io.kubernetes.pod.name)

# Clean up networks created by play kube
podman network ls --filter label=io.kubernetes.pod.name
podman network prune --filter label=io.kubernetes.pod.name
```

## Best Practices

1. **Use play kube for local testing** before deploying to cluster
2. **Pin image versions** with digests in production manifests
3. **Add resource limits** to prevent runaway containers
4. **Implement health checks** for reliable deployments
5. **Use ConfigMaps and Secrets** for configuration management
6. **Test manifests locally** with play kube in CI pipeline
7. **Document unsupported features** for team awareness

## See Also

- [Pod Management](03-pod-management.md) - Pod creation and orchestration
- [Image Management](02-image-management.md) - Image building and registry operations
- [Systemd Integration](05-systemd-quadlet.md) - Alternative declarative management

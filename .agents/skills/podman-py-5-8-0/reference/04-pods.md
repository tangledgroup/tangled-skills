# Pods

## Pod Lifecycle

### Creating Pods

```python
pod = client.pods.create(
    "my-pod",
    network="pod",
    port_bindings={"8080/tcp": [{"HostPort": "8080"}]},
)
```

See the [Podman API documentation](https://docs.podman.io/en/latest/_static/api.html#operation/CreatePod) for complete keyword list.

### Starting / Stopping Pods

```python
pod.start()
pod.stop(timeout=30)
pod.restart()
```

### Pause / Unpause

```python
pod.pause()
pod.unpause()
```

### Kill Pod

```python
pod.kill(signal="SIGTERM")  # or signal number
```

### Remove Pod

```python
pod.remove(force=True)
# or via manager:
client.pods.remove("my-pod", force=True)
```

Parameters:
- `force` (bool): Stop and delete all containers in pod first

## Listing Pods

```python
# List all pods
pods = client.pods.list()

# Filter by status
pods = client.pods.list(filters={"status": ["running"]})

# Filter by name
pods = client.pods.list(filters={"name": "my-pod"})

# Filter by container count
pods = client.pods.list(filters={"ctr-number": [2]})

# Filter by container status
pods = client.pods.list(filters={"ctr-status": ["running"]})
```

Available filters:
- `ctr-ids` (list[str]): Container IDs to filter by
- `ctr-names` (list[str]): Container names to filter by
- `ctr-number` (list[int]): Pods with given number of containers
- `ctr-status` (list[str]): Container states — `"created"`, `"running"`, `"paused"`, `"stopped"`, `"exited"`, `"unknown"`
- `id` (str): Pod ID
- `name` (str): Pod name
- `status` (list[str]): Pod states — same values as ctr-status
- `label` (list[str]): Labels
- `network` (list[str]): Network IDs (not names)

## Getting and Checking Pods

```python
pod = client.pods.get("my-pod")
exists = client.pods.exists("my-pod")
```

## Pod Statistics

```python
# Single snapshot for all running pods
stats = client.pods.stats(all=True, stream=False, decode=True)

# Stream statistics
for batch in client.pods.stats(stream=True, decode=True):
    for stat in batch:
        print(stat["Name"], stat["CPUUsage"])

# Specific pods
stats = client.pods.stats(name="my-pod", stream=False, decode=True)
```

Parameters:
- `all` (bool): Include all running pods
- `name` (str | list[str]): Specific pod names
- `stream` (bool): Stream until cancelled, default False
- `decode` (bool): Decode into dicts

## Pod Process List

```python
processes = pod.top()
# Returns dict with process information

# With ps arguments
processes = pod.top(ps_args="-aux")
```

## Pruning Pods

```python
result = client.pods.prune()
# Returns {"PodsDeleted": [...], "SpaceReclaimed": 0}
```

## Pod Properties

```python
print(pod.id)       # Pod ID
print(pod.name)     # Pod name
print(pod.short_id) # Truncated ID
```

# Kubernetes & Docker Compose

## Kubernetes

### Using Helm

[Helm Charts](https://github.com/rqlite/helm-charts) are available on [GitHub](https://github.com/rqlite/helm-charts) and [Artifact Hub](https://artifacthub.io/packages/helm/rqlite/rqlite).

### Manual Deployment

Deploy rqlite as a Kubernetes [StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/). Full source is available in the [rqlite Kubernetes Configuration repo](https://github.com/rqlite/kubernetes-configuration).

#### Create Services

Create two Kubernetes Services:

1. **`rqlite-svc-internal`** — Headless service for nodes to find each other and cluster automatically. Not for client use.
2. **`rqlite-svc`** — For clients to talk to the cluster. Gets a Cluster IP address with automatic load balancing. Only contains Pods that are ready to serve traffic.

```bash
curl -s https://raw.githubusercontent.com/rqlite/kubernetes-configuration/master/service.yaml -o rqlite-service.yaml
kubectl apply -f rqlite-service.yaml
```

#### Create a StatefulSet

```bash
curl -s https://raw.githubusercontent.com/rqlite/kubernetes-configuration/master/statefulset-3-node.yaml -o rqlite-3-nodes.yaml
kubectl apply -f rqlite-3-nodes.yaml
```

The StatefulSet args tell rqlite to use `dns` discovery mode and resolve `rqlite-svc-internal` to find other nodes. It waits until three nodes are available before forming a cluster.

#### Scaling the Cluster

Grow the cluster by setting the replica count:

```bash
kubectl scale statefulsets rqlite --replicas=9
```

> **Important:** Ensure the cluster is healthy and fully functional before scaling up. DNS must be working properly. If not, new nodes may become standalone single-node clusters.

Do **not** change `-bootstrap-expect` when scaling — it only needs to be set on the very first launch.

#### Shrinking the Cluster

```bash
kubectl scale statefulsets rqlite --replicas=1
```

**Warning:** From the remaining node's perspective, the other nodes have _failed_ — and a single node doesn't have quorum. The cluster becomes offline. Two ways to avoid this:

1. Remove one node at a time and [explicitly remove it](reference/05-clustering.md#removing-or-replacing-a-node) before reducing replicas
2. Enable `-raft-cluster-remove-shutdown=true` so nodes self-remove on graceful shutdown

#### Secrets Management

Use [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) to pass credentials (e.g., for [user-level permissions](reference/10-security.md)).

## Docker Compose

[Docker Compose](https://docs.docker.com/compose/) is an effective approach for development and deployment. Full documentation with scenarios is available in the [rqlite Docker Compose repo](https://github.com/rqlite/docker-compose):

- **Single-node database** — basic standalone rqlite instance
- **General clustering with 3 nodes** — manual three-node cluster configuration
- **Automatic clustering with 3 nodes** — demonstrates [automatic clustering](reference/06-automatic-clustering.md)

A typical single-node compose file:

```yaml
services:
  rqlite:
    image: rqlite/rqlite:latest
    ports:
      - "4001:4001"
    volumes:
      - rqlite-data:/rqlite/data

volumes:
  rqlite-data:
```
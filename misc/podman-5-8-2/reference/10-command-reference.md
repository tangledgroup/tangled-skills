# Command Reference

## Container Commands (`podman container`)

- `attach` — Attach to a running container
- `checkpoint` — Checkpoint a running container (requires root for CRIU)
- `cleanup` — Clean up container network and mountpoints
- `clone` — Create a copy of an existing container
- `commit` — Create a new image from a changed container
- `cp` — Copy files between container and filesystem
- `create` — Create a new container (without starting)
- `diff` — Inspect filesystem changes on a container
- `exec` — Execute a command in a running container
- `exists` — Check if a container exists
- `export` — Export container filesystem as tar archive
- `init` — Initialize a container
- `inspect` — Display container configuration
- `kill` — Kill the main process in containers
- `list` / `ls` — List containers (alias for `ps`)
- `logs` — Display container logs
- `mount` — Mount a container's root filesystem
- `pause` — Pause one or more containers
- `port` — List port mappings
- `prune` — Remove all stopped containers
- `ps` — Print information about containers
- `rename` — Rename an existing container
- `restart` — Restart containers
- `restore` — Restore a container from checkpoint (requires root)
- `rm` — Remove containers
- `run` — Run a command in a new container
- `runlabel` — Execute a command described by an image label
- `start` — Start containers
- `stats` — Live stream of resource usage
- `stop` — Stop running containers
- `top` — Display running processes
- `unmount` — Unmount a container's root filesystem
- `unpause` — Unpause containers
- `update` — Update cgroup configuration (resource limits, env vars)
- `wait` — Wait for containers to stop and print exit codes

## Image Commands (`podman image`)

- `build` — Build an image from a Containerfile/Dockerfile
- `diff` — Inspect filesystem changes on an image
- `exists` — Check if an image exists
- `history` — Show image build history
- `import` — Import a tarball as an image
- `inspect` — Display image configuration
- `list` / `ls` — List images (alias for `images`)
- `load` — Load an image from docker-archive
- `mount` — Mount an image's root filesystem
- `prune` — Remove unused images
- `pull` — Pull an image from a registry
- `push` — Push an image to a registry
- `rm` — Remove images (alias for `rmi`)
- `save` — Save an image to archive or OCI format
- `scp` — Securely copy an image between hosts
- `search` — Search a registry for images
- `sign` — Create a signature for an image
- `tag` — Add a name to a local image
- `tree` — Print layer hierarchy in tree format
- `trust` — Manage image trust policy
- `unmount` — Unmount an image's root filesystem
- `untag` — Remove names from a locally-stored image

## Pod Commands (`podman pod`)

- `clone` — Copy an existing pod
- `create` — Create a new pod
- `exists` — Check if a pod exists
- `inspect` — Display pod information
- `kill` — Kill processes in all pod containers
- `logs` — Display aggregated logs from pod containers
- `pause` — Pause all containers in pods
- `prune` — Remove stopped pods and their containers
- `ps` — Print information about pods
- `restart` — Restart pods
- `rm` — Remove stopped pods and containers
- `start` — Start pods
- `stats` — Live resource usage for pod containers
- `stop` — Stop pods
- `top` — Display processes in pod containers
- `unpause` — Unpause pods

## Network Commands (`podman network`)

- `connect` — Connect a container to a network
- `create` — Create a network
- `disconnect` — Disconnect a container from a network
- `exists` — Check if a network exists
- `inspect` — Display network configuration
- `ls` — List networks
- `prune` — Remove unused networks
- `reload` — Reload network configuration for containers
- `rm` — Remove networks
- `update` — Update an existing network

## Volume Commands (`podman volume`)

- `create` — Create a new volume
- `exists` — Check if a volume exists
- `export` — Export volume to tar
- `import` — Import tar into a volume
- `inspect` — Display volume information
- `ls` — List volumes
- `mount` — Mount a volume filesystem
- `prune` — Remove unused volumes
- `reload` — Reload volumes from plugins
- `rm` — Remove volumes
- `unmount` — Unmount a volume

## System Commands (`podman system`)

- `check` — Consistency checks on storage
- `connection` — Manage remote service connections
- `df` — Show disk usage
- `events` — Monitor Podman events
- `info` — Display system information
- `migrate` — Migrate containers to new version
- `prune` — Remove unused pods, containers, images, networks, volumes
- `renumber` — Migrate lock numbers
- `reset` — Reset storage to initial state
- `service` — Run the API service

## Machine Commands (`podman machine`)

- `cp` — Copy files between host and VM
- `info` — Display machine host info
- `init` — Initialize a new VM
- `inspect` — Inspect VM configuration
- `list` — List VMs
- `os` — Manage VM OS
- `reset` — Reset machines and environment
- `rm` — Remove a VM
- `set` — Set VM settings
- `ssh` — SSH into a VM
- `start` — Start a VM
- `stop` — Stop a VM

## Quadlet Commands (`podman quadlet`)

- `install` — Install a Quadlet file
- `list` / `ls` — List installed Quadlets
- `print` — Display Quadlet contents
- `rm` — Remove an installed Quadlet

## Kube Commands (`podman kube`)

- `apply` — Apply Kubernetes YAML to a cluster
- `down` — Remove containers/pods from Kubernetes YAML
- `generate` — Generate Kubernetes YAML from containers/pods
- `play` — Create containers/pods from Kubernetes YAML

## Artifact Commands (`podman artifact`)

- `add` — Add files to an artifact
- `extract` — Copy artifact contents to disk
- `inspect` — Inspect an artifact
- `ls` — List artifacts
- `pull` — Pull an artifact from a registry
- `push` — Push an artifact to a registry
- `rm` — Remove artifacts

## Other Commands

- `podman commit` — Create image from container changes
- `podman events` — Monitor Podman events (alias of system events)
- `podman generate` — Generate scripts or kube YAML
- `podman healthcheck` — Run healthchecks manually
- `podman history` — Show image history (alias of image history)
- `podman images` — List images (alias of image list)
- `podman import` — Import tarball as image (alias of image import)
- `podman info` — Display system info (alias of system info)
- `podman kill` — Kill container processes
- `podman load` — Load image from archive (alias of image load)
- `podman login` — Login to a registry
- `podman logout` — Logout from a registry
- `podman logs` — Display container logs
- `podman manifest` — Manage image manifests
- `podman mount` — Mount container filesystem (alias of container mount)
- `podman pause` — Pause containers
- `podman port` — List port mappings
- `podman ps` — List containers
- `podman pull` — Pull an image (alias of image pull)
- `podman push` — Push an image (alias of image push)
- `podman rename` — Rename a container
- `podman restart` — Restart containers
- `podman rm` — Remove containers
- `podman rmi` — Remove images (alias of image rm)
- `podman run` — Run a command in a new container
- `podman save` — Save an image (alias of image save)
- `podman search` — Search registry (alias of image search)
- `podman secret` — Manage secrets
- `podman start` — Start containers
- `podman stats` — Display resource usage
- `podman stop` — Stop containers
- `podman tag` — Tag an image (alias of image tag)
- `podman top` — Display running processes
- `podman unmount` — Unmount filesystem
- `podman unpause` — Unpause containers
- `podman untag` — Untag an image (alias of image untag)
- `podman update` — Update container configuration
- `podman unshare` — Run a command in the rootless user namespace
- `podman version` — Display Podman version
- `podman wait` — Wait for containers to stop

# WebAssembly Support

crun natively supports running WebAssembly/WASI workloads inside containers without a traditional Linux userspace. This enables lightweight, secure execution of wasm modules with minimal overhead.

## Supported Runtimes

crun can be built with one of the following WASI runtimes (only one at a time):

- **wasmedge** — supports wasi-nn plugin for AI/ML workloads
- **wasmer** — can compile `.wat` files on-the-fly
- **wasmtime** — production-grade runtime from Bytecode Alliance
- **wamr** — layered JIT architecture with tier-up during runtime

## Detection and Activation

crun detects wasm workloads through OCI annotations:

- `run.oci.handler=wasm` — explicit handler annotation
- `module.wasm.image/variant=compat` — OCI wasm compat image annotation

The entrypoint must point to a valid `.wasm` binary or `.wat` text file (wasmer-only).

For sidecar patterns with mixed workloads, use:
- `module.wasm.image/variant=compat-smart`
- `run.oci.handler=wasm-smart`

## Running wasm with Podman

```bash
podman run -it -p 8080:8080 --name=wasm-example \
  --platform=wasi/wasm32 michaelirwin244/wasm-example
```

## Building wasm Images

Compile a Rust program to wasm32-wasip1 target:

```bash
cargo new hello_wasm --bin
# Add your code to src/main.rs
cargo build --target wasm32-wasip1
```

Create a Containerfile:

```dockerfile
FROM scratch
COPY hello.wasm /
CMD ["/hello.wasm"]
```

Build and run with buildah and podman:

```bash
buildah build --platform=wasi/wasm -t mywasm-image .
podman run mywasm-image:latest
```

## Running Directly with crun

```bash
# Create OCI bundle with wasm handler annotation
crun run wasm-container
This is from a main function from a wasm module
```

## Kubernetes Integration

### CRI-O

As of version 1.31, CRI-O defaults to crun (though bundled crun may lack wasm support). CRI-O automatically propagates pod annotations to container spec:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-wasm-workload
  namespace: mynamespace
  annotations:
    module.wasm.image/variant: compat
spec:
  containers:
  - name: wasm-container
    image: myrepo/mywasmimage:latest
```

### containerd

Configure containerd to use crun and whitelist wasm annotations in `/etc/containerd/config.toml`:

```toml
pod_annotations = ["*.wasm.*", "wasm.*", "module.wasm.image/*", "*.module.wasm.image", "module.wasm.image/variant.*"]
```

Restart containerd:

```bash
systemctl restart containerd
```

## krun MicroVM Handler

The `krun` handler runs containers as microVMs using libkrun. Key features:

- External kernel support — bundle a kernel image with the container
- virtio-gpu — enabled when `/dev/dri` and `/usr/libexec/virgl_render_server` are present
- Nitro enclave support
- Up to 16 vCPUs
- passt-based networking via `krun.use_passt` annotation
- Configure via annotations: `krun.cpus`, `krun.ram_mib`, `krun.variant`

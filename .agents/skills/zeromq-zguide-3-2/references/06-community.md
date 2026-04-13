# ZeroMQ Community and Ecosystem

Overview of the ZeroMQ community, bindings, tools, and ecosystem resources from Chapter 6 of the ZGuide.

## Architecture of the ZeroMQ Community

The ZeroMQ project is organized as a collection of projects built around the core library.

### Project Structure

**Core Library (libzmq):**
- Written in C++ with low-level C API
- Highly optimized codebase
- Maintained by dozens of contributors
- Primary repository: https://github.com/zeromq/libzmq

**Bindings (~50+ languages):**
- Higher-level APIs for various programming languages
- Quality ranges from experimental to production-ready
- No "official" bindings - community-driven
- Example: PyZMQ (Python) is considered a model binding

**Reimplementations:**
- JeroMQ - Full Java translation of libzmq
- NetMQ - C# implementation based on JeroMQ
- Native stacks offering identical APIs
- Compatible with ZMTP protocol

**Outer Projects:**
- Frameworks using ZeroMQ
- Web servers (e.g., Mongrel2)
- Brokers (e.g., Majordomo)
- Enterprise tools (e.g., Apache Storm)

### Community Organization

The ZeroMQ GitHub organization hosts:
- libzmq core library
- Most language bindings
- Some outer projects

Governed by senior binding authors with self-managing structure.

## Language Bindings

### Official and Community Bindings

**C/C++ (Reference Implementation):**
```bash
# Install from source or package manager
sudo apt-get install libzmq3-dev  # Debian/Ubuntu
brew install zeromq              # macOS
```

**Python (PyZMQ):**
```bash
pip install pyzmq
```

Features:
- Complete API coverage
- Async support with asyncio
- DRAFT features available
- Documentation: https://pyzmq.readthedocs.io/

**Java:**
```xml
<!-- Maven dependency for JeroMQ -->
<dependency>
    <groupId>org.zeromq</groupId>
    <artifactIdjeromq</artifactId>
    <version>0.5.4</version>
</dependency>
```

Features:
- Pure Java implementation
- No native dependencies
- Compatible with libzmq protocol

**Go:**
```bash
go get github.com/pebbe/zmq4
# or
go get github.com/gomodule/redigo/redis  # For some use cases
```

**Node.js:**
```bash
npm install nanomsg
# or
npm install zeromq
```

**C#/.NET (NetMQ):**
```bash
Install-Package NetMQ
```

Features:
- Pure C# implementation
- No native dependencies
- Full API compatibility

**Erlang/Elixir:**
```erlang
% Erlang dependency
{zeromq, ">=0.3.5"}.
```

```elixir
# Elixir mix dependency
defp deps do
  [{:zeromq, "~> 0.4"}]
end
```

**Rust:**
```toml
# Cargo.toml
[dependencies]
zmq = "0.10"
# or async version
async-zmq = "0.4"
```

### Binding Quality Indicators

When evaluating bindings, look for:
- **Test coverage** - Comprehensive test suite
- **Documentation** - API docs and examples
- **Activity** - Recent commits and issue responses
- **Feature parity** - Support for latest ZeroMQ features
- **Community** - Active users and contributors

## Development Process (C4 Model)

ZeroMQ uses the C4 (Contributor Covenant v4) process for collaboration.

### Key Principles

1. **No designated maintainer** - Changes reviewed by community
2. **No branches** - All development on master/trunk
3. **Small patches** - Encourages review and integration
4. **Process over people** - Clear rules reduce conflict

### Patch Requirements

- Must follow coding standards
- Include tests for new functionality
- Document API changes
- Pass all existing tests
- Signed-off-by line in commit message

### Development Workflow

```bash
# 1. Fork the repository
git clone https://github.com/yourusername/libzmq.git
cd libzmq

# 2. Make changes
# ... edit code ...

# 3. Add tests
# ... add test cases ...

# 4. Run tests
./autogen.sh
./configure
make
make check

# 5. Submit pull request
git push origin master
# Create PR on GitHub
```

### Licensing

- **Core library**: LGPLv3
- **Bindings**: Varies by project (often same as language ecosystem)
- **Examples**: CC-BY-SA (Creative Commons)

LGPL chosen to:
- Encourage commercial use
- Require improvements to core be shared
- Allow proprietary extensions via dynamic linking

## Tools and Extensions

### Monitoring Tools

**zmq-monitor:**
```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.DEALER)

# Enable monitoring
monitor_socket = context.socket(zmq.PAIR)
socket.get_monitor_socket("inproc://monitor")

# Connect to monitor
monitor = context.socket(zmq.PAIR)
monitor.connect("inproc://monitor")

while True:
    event = monitor.recv_multipart()
    print(f"Monitor event: {event}")
```

**Event types:**
- ZMQ_EVENT_CONNECTED
- ZMQ_EVENT_CONNECT_DELAYED
- ZMQ_EVENT_CONNECT_RETRIED
- ZMQ_EVENT_LISTENING
- ZMQ_EVENT_BIND_FAILED
- ZMQ_EVENT_ACCEPTED
- ZMQ_EVENT_ACCEPT_FAILED
- ZMQ_EVENT_CLOSED
- ZMQ_EVENT_CLOSE_FAILED
- ZMQ_EVENT_CLOSED
- ZMQ_EVENT_DISCONNECTED

### Profiling Tools

**Performance Testing:**
```python
import zmq
import time

def benchmark_throughput():
    context = zmq.Context()
    
    # Create pipeline
    push = context.socket(zmq.PUSH)
    push.bind("inproc://test")
    
    pull = context.socket(zmq.PULL)
    pull.connect("inproc://test")
    
    # Warm up
    for _ in range(100):
        push.send(b"x" * 1024)
        pull.recv()
    
    # Benchmark
    start = time.time()
    iterations = 10000
    
    for _ in range(iterations):
        push.send(b"x" * 1024)
        pull.recv()
    
    elapsed = time.time() - start
    throughput = iterations / elapsed
    
    print(f"Throughput: {throughput:.0f} messages/sec")
    print(f"Latency: {(elapsed/iterations)*1000:.2f} ms")

benchmark_throughput()
```

### Security Tools

**CURVE Key Generation:**
```python
import zmq

# Generate key pair
public_key, secret_key = zmq.curve_keypair()

print(f"Public key:  {zmq.utils.z85_encode(public_key)}")
print(f"Secret key:  {zmq.utils.z85_encode(secret_key)}")
```

**Using CURVE Security:**
```python
import zmq

context = zmq.Context()

# Server setup
server = context.socket(zmq.ROUTER)
server.setsockopt(zmq.CURVE_SERVER, 1)
server.setsockopt(zmq.CERTIFICATE_PUBLIC, public_key)
server.setsockopt(zmq.CERTIFICATE_KEYPAIR, secret_key)
server.bind("tcp://*:5555")

# Client setup
client = context.socket(zmq.DEALER)
client.setsockopt(zmq.IDENTITY, b"Client1")
client.setsockopt(zmq.CURVE_PUBLIC, client_public)
client.setsockopt(zmq.CERTIFICATE_KEYPAIR, client_secret)
client.setsockopt(zmq.CURVE_SERVERKEY, server_public)
client.connect("tcp://localhost:5555")
```

## Community Resources

### Official Resources

**Websites:**
- Main site: https://zeromq.org/
- Documentation: https://zguide.zeromq.org/
- API Reference: https://api.zeromq.org/
- RFCs: https://rfc.zeromq.org/

**Communication:**
- Mailing list: zeromq-dev@lists.zeromq.org
- IRC: #zeromq on Freenode
- GitHub Discussions: https://github.com/zeromq/libzmq/discussions

**Code Repositories:**
- Core library: https://github.com/zeromq/libzmq
- Python binding: https://github.com/zeromq/pyzmq
- Java binding: https://github.com/zeromq/jeromq
- C# binding: https://github.com/zeromq/netmq

### Learning Resources

**Books:**
- "ZeroMQ: The Guide" (this document)
- "Building Mesos" (uses ZeroMQ extensively)

**Tutorials:**
- Official ZGuide chapters
- PyZMQ documentation and examples
- Language-specific binding docs

**Video Content:**
- ZeroMQ conference talks (YouTube)
- Pieter Hintjens presentations
- Community meetup recordings

### Third-Party Projects

**Frameworks:**
- **Majordomo**: Service-oriented architecture framework
- **Scuttlebutt**: Distributed hash table implementation
- **Cr0sh**: Load balancing framework

**Brokers:**
- **MQTT over ZeroMQ**: Message queue telemetry transport
- **AMQP bridges**: Advanced Message Queuing Protocol integration

**Monitoring:**
- **zmq-tools**: Collection of diagnostic utilities
- **zmon**: Real-time monitoring dashboard

## Best Practices for Community Participation

### Contributing Code

1. **Read the C4 process** - Understand contribution workflow
2. **Start small** - Fix bugs or add tests first
3. **Follow coding standards** - Match existing style
4. **Write tests** - Ensure changes don't break existing functionality
5. **Document changes** - Update docs for API modifications

### Asking for Help

1. **Search existing issues** - Problem may already be documented
2. **Provide minimal example** - Reproducible test case
3. **Include version info** - ZeroMQ and binding versions
4. **Be specific** - Clear description of expected vs actual behavior

### Reporting Issues

**Good issue report includes:**
- Clear title describing the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, ZeroMQ version, binding version)
- Minimal code example

### Code Review Guidelines

**When reviewing patches:**
- Check for memory leaks (C/C++)
- Verify thread safety
- Ensure proper error handling
- Confirm test coverage
- Validate documentation updates

## Common Tools and Utilities

### Development Utilities

**zmq-utils Package:**
```bash
# Install development utilities
sudo apt-get install libzmq3-dev zmq-utils
```

**Common commands:**
```bash
# Check ZeroMQ version
zmq --version

# Test basic connectivity
zmq-pub tcp://*:5555
zmq-sub tcp://localhost:5555
```

### Debugging Tools

**strace/ltrace for C programs:**
```bash
# Trace system calls
strace -f ./my_zmq_program

# Trace library calls
ltrace -f ./my_zmq_program
```

**Network debugging:**
```bash
# Monitor ZeroMQ traffic
tcpdump -i lo port 5555 -vv

# Check open ports
netstat -an | grep 5555
ss -tlnp | grep 5555
```

### Performance Tools

**Benchmarking suite:**
```bash
# Run ZeroMQ benchmarks
cd libzmq
./run_tests.sh
./performance/bench_hwm.sh
./performance/bench_lat.sh
./performance/bench_thr.sh
```

## Troubleshooting Common Issues

### Connection Problems

**Issue: Cannot connect to server**
- Check server is bound before client connects
- Verify firewall rules allow the port
- Confirm bind address is accessible (0.0.0.0 vs 127.0.0.1)

**Issue: Connection timeouts**
- Increase timeout settings
- Check network connectivity
- Verify server is running and responsive

### Message Delivery Issues

**Issue: Messages not received**
- Check subscription filters (PUB/SUB)
- Verify message format matches expectations
- Confirm socket types are compatible

**Issue: Lost messages**
- Implement reliability patterns (Lazy Pirate)
- Add acknowledgments for critical messages
- Use appropriate HWM (High Water Mark) settings

### Performance Issues

**Issue: Low throughput**
- Increase I/O thread count
- Tune message sizes
- Check for blocking operations
- Profile with benchmark tools

**Issue: High latency**
- Reduce message processing time
- Use inproc:// for same-process communication
- Minimize serialization overhead

## Next Steps

- [Advanced Architecture](07-advanced-architecture.md) - Large-scale patterns
- [Distributed Frameworks](08-distributed-framework.md) - Complete system design
- Official documentation: https://zguide.zeromq.org/

# Monitoring and CLI

## Socket Event Monitoring

aiozmq supports ZeroMQ socket monitoring, which reports lifecycle events (connect, disconnect, handshake, errors) for debugging and observability.

### Enabling Monitoring

```python
transport, protocol = await aiozmq.create_zmq_connection(
    MyProtocol(), zmq.DEALER, connect='tcp://127.0.0.1:5555'
)
await transport.enable_monitor()  # monitor all events
# or
await transport.enable_monitor(zmq.EVENT_CONNECTED | zmq.EVENT_DISCONNECTED)
```

Requires libzmq >= 4 and pyzmq >= 14.4. Raises `NotImplementedError` if unsupported.

### Receiving Events

Events are delivered via the protocol's `event_received(event)` callback:

```python
class MonitoredProtocol(aiozmq.ZmqProtocol):
    def event_received(self, event):
        # event is SocketEvent(event_code, value, endpoint)
        print(f"Event {event.event}: {event.value} on {event.endpoint}")

    def msg_received(self, data):
        # handle messages as usual
        pass
```

### Event Types

Common event codes (from pyzmq):

- `zmq.EVENT_CONNECTED` — Socket connected
- `zmq.EVENT_CONNECT_DELAYED` — Connection delayed
- `zmq.EVENT_CONNECT_RETRIED` — Connection retry
- `zmq.EVENT_LISTENING` — Socket listening on endpoint
- `zmq.EVENT_BIND_ERROR` — Bind failed
- `zmq.EVENT_ACCEPTED` — Incoming connection accepted
- `zmq.EVENT_ACCEPT_ERROR` — Accept failed
- `zmq.EVENT_CLOSED` — Socket closed
- `zmq.EVENT_CLOSE_ERROR` — Close failed
- `zmq.EVENT_DISCONNECTED` — Socket disconnected
- `zmq.EVENT_HANDSHAKE_SUCCEEDED` — Handshake OK
- `zmq.EVENT_HANDSHKE_FAILED` — Handshake failed
- `zmq.EVENT_ALL` — All events (default)

### Disabling Monitoring

```python
transport.disable_monitor()
```

## aiozmq CLI Proxy Tools

aiozmq includes command-line proxy tools for common ZeroMQ patterns.

### Queue Proxy (ROUTER/DEALER)

Creates a shared queue proxy that forwards messages between frontend and backend:

```bash
aiozmq-proxy queue \
    --front-bind tcp://*:5555 \
    --back-bind tcp://*:5556
```

### Forwarder Proxy (XSUB/XPUB)

Creates a message forwarding proxy for pub-sub fan-out:

```bash
aiozmq-proxy forwarder \
    --front-bind tcp://*:5555 \
    --back-bind tcp://*:5556
```

### Streamer Proxy (PULL/PUSH)

Creates a stream forwarding proxy for pipeline patterns:

```bash
aiozmq-proxy streamer \
    --front-bind tcp://*:5555 \
    --back-bind tcp://*:5556
```

### Monitor

Connect to a monitor socket and dump all traffic:

```bash
aiozmq-proxy monitor --bind tcp://*:5557
```

### Common Options

All proxy subcommands support:

- `--front-bind ADDR` — Bind frontend socket (repeatable)
- `--front-connect ADDR` — Connect frontend socket (repeatable)
- `--back-bind ADDR` — Bind backend socket (repeatable)
- `--back-connect ADDR` — Connect backend socket (repeatable)
- `--monitor-bind ADDR` — Create and bind monitor socket (repeatable)
- `--monitor-connect ADDR` — Connect monitor socket (repeatable)

## Version Info

```python
import aiozmq
print(aiozmq.version)       # "1.0.0 , Python 3.11.x ..."
print(aiozmq.version_info)  # VersionInfo(major=1, minor=0, micro=0, releaselevel='final', serial=0)
```

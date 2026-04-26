# Reliable Messaging

## Defining Reliability

Reliability means "keeping things working properly when code freezes or crashes." In ZeroMQ, the basic request-reply pattern scores low on failure handling — if the server crashes, the client hangs forever.

Common failure modes (in order of probability):
1. Application code crashes, freezes, runs too slowly, exhausts memory
2. System code (brokers) dies for same reasons
3. Message queues overflow and discard messages
4. Network failures (WiFi disconnects, etc.) — ZeroMQ auto-reconnects
5. Hardware failure
6. Exotic network failures (switch ports dying)
7. Data center disasters

## The Pirate Patterns

Three progressively robust patterns for reliable request-reply:

### Lazy Pirate Pattern (Client-Side Reliability)

The client polls for replies with a timeout, retries on failure, and abandons after N attempts:

```c
#define REQUEST_TIMEOUT 2500  //  msecs
#define REQUEST_RETRIES   3   //  Before we abandon

int retries_left = REQUEST_RETRIES;
while (retries_left) {
    zstr_send (client, request);
    bool expect_reply = true;
    while (expect_reply) {
        zmq_pollitem_t items [] = {{ client, 0, ZMQ_POLLIN, 0 }};
        int rc = zmq_poll (items, 1, REQUEST_TIMEOUT * ZMQ_POLL_MSEC);

        if (items [0].revents & ZMQ_POLLIN) {
            //  Got a valid reply
            char *reply = zstr_recv (client);
            expect_reply = false;
            retries_left = REQUEST_RETRIES;
            free (reply);
        } else {
            //  No reply — close and reopen REQ socket, retry
            if (--retries_left == 0) {
                printf ("E: server offline, abandoning\n");
                break;
            }
            zsock_destroy (&client);
            client = zsock_new_req (SERVER_ENDPOINT);
            zstr_send (client, request);
        }
    }
}
```

Key insight: REQ socket enforces strict send/receive. To resend after timeout, close and reopen the socket.

### Simple Pirate Pattern (Basic Reliable Queuing)

Server-side reliability using a load-balancing broker with DEALER sockets:

- Broker uses ROUTER on frontend (clients) and DEALER on backend (workers)
- Workers use DEALER for async communication
- Broker tracks worker liveness
- If worker doesn't reply in time, broker redistributes the request

### Paranoid Pirate Pattern (Robust Reliable Queuing)

Adds heartbeating to Simple Pirate:

- Broker sends periodic heartbeat messages to workers
- Workers must respond to heartbeats
- If no response within timeout, broker considers worker dead
- Uses a worker state machine: READY → WORKING → DEAD

```c
//  Heartbeat check in broker
if (zclock_now () - worker->hearthbeat > HEARTBEAT_LIVENESS) {
    //  Worker is dead — remove and redistribute
    printf ("W: heartbeat deadline, removing worker\n");
    ww_destroy (&worker);
}
```

## Heartbeating Strategies

### Shrugging It Off
Simply retry. If the peer doesn't respond, assume it's dead and move on. Works when message loss is acceptable.

### One-Way Heartbeats
Sender periodically sends heartbeat messages. Receiver tracks last heartbeat time. Simple but doesn't detect receiver failures.

### Ping-Pong Heartbeats
Both sides send heartbeats. Both track liveness. More robust but more complex.

### Heartbeating for Paranoid Pirate
Broker sends empty "heartbeat" frames to workers on the backend ROUTER socket. Workers must reply within HEARTBEAT_INTERVAL. If not, worker is marked dead and removed from the pool.

## Majordomo Protocol (MDP)

A service-oriented protocol for reliable request-reply with:

- **Service registration** — servers register with a broker
- **Service discovery** — clients request services by name
- **Request routing** — broker routes to registered servers
- **Heartbeating** — broker monitors server liveness
- **Clean shutdown** — servers unregister before exiting

### MDP Message Format

All messages use multipart frames:

```
Client → Broker: [MDPm] [0.1.0] [service name] [request body...]
Broker → Client: [MDPm] [0.1.0] [reply body...]
Server → Broker: [MDPm] [0.1.0] [empty] [registration]
```

The magic frame ("MDPm") identifies the protocol. Version frame ensures compatibility.

### Asynchronous Majordomo (ASM)

Extends MDP with async client support using DEALER sockets, allowing clients to send multiple requests without waiting for replies. Uses correlation IDs to match requests with replies.

## Service Discovery

In distributed systems, clients need to find available services:

- **Centralized directory** — a known registry service
- **Broadcast discovery** — UDP multicast to find peers
- **Majordomo broker** — built-in service registration and lookup

## Idempotent Services

For reliable systems, services should be idempotent — calling them multiple times with the same input produces the same result. This enables safe retries without side effects.

Use unique request IDs to detect duplicates:
```
Client sends: [request-id-12345] [payload]
Server checks: if request-id-12345 already processed, return cached result
```

## Titanic Pattern (Disconnected Reliability)

Disk-based message queuing for disconnected operation:

- Messages are persisted to disk before being sent
- On restart, unacked messages are replayed
- Uses a simple file-based queue
- Suitable for scenarios where network connectivity is intermittent

## Binary Star Pattern (High-Availability Pair)

Primary-backup server failover using two nodes that coordinate via PAIR socket:

- One node is primary (accepts client connections)
- Other node is backup (standby, monitors primary)
- Nodes exchange heartbeats over PAIR socket
- If primary fails, backup takes over
- Uses "split-brain" prevention with a tie-breaker (third party or file lock)

### Preventing Split-Brain

When network partition separates the two nodes, both might think they're primary. Prevention strategies:

- **Fencing** — use a shared resource (file lock, disk) as tie-breaker
- **Third-party arbiter** — a lightweight service that decides which node is primary
- **Priority-based** — one node has higher priority and always wins

## Freelance Pattern (Brokerless Reliability)

Direct client-to-server communication without an intermediary broker:

- Client maintains list of known servers
- On failure, client tries next server in list
- Servers register themselves via pub-sub or UDP broadcast
- Three models: simple retry/failover, shotgun (try all simultaneously), complex state machine

## Designing Reliability — Summary

Choose the right pattern for your topology:

| Topology | Pattern | Handles |
|----------|---------|---------|
| Multiple clients → single server | Lazy Pirate | Server crashes, network disconnects |
| Multiple clients → broker → multiple workers | Paranoid Pirate / Majordomo | Worker crashes, overload, queue failures |
| Multiple clients → multiple servers (no broker) | Freelance | Service crashes, overload, network issues |

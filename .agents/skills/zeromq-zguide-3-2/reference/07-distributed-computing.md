# Distributed Computing

## Design for the Real World

Building distributed applications requires solving:

- **Discovery** — how do nodes find each other?
- **Presence** — how to track when nodes come and go?
- **Connectivity** — how to actually connect nodes?
- **Point-to-point messaging** — direct node-to-node communication
- **Group messaging** — sending to groups without central coordination
- **Testing and simulation** — simulating large numbers of nodes
- **Distributed logging** — tracking what the cloud of nodes is doing
- **Content distribution** — sending content between nodes

## Discovery

### Service Discovery

Finding available services on the network. Approaches:
- Centralized directory service
- UDP broadcast/multicast beacons
- Majordomo broker registration

### Network Discovery (Beaconing)

ZeroMQ provides a beacon API for UDP-based discovery:

```c
//  Start broadcasting beacons
int interval = 1000;  //  msecs
zmq_beacon_t beacon;
zmq_beacon_init (&beacon, "Hello", 5);
zmq_beacon_set_interval (&beacon, interval);
zmq_beacon_publish (&beacon, "I'm here", 8);
zmq_beacon_bind (&beacon, "0.0.0.0", 5670);

//  In another process, subscribe to beacons
zmq_beacon_t beacon;
zmq_beacon_init (&beacon, "Hello", 5);
zmq_beacon_subscribe (&beacon, "I'm here");
zmq_beacon_bind (&beacon, "0.0.0.0", 5670);
```

Beacons use UDP broadcasts on a configurable port. They carry short key-value pairs for service identification.

## The Harmony Pattern (True Peer Connectivity)

In traditional client-server, one side binds and the other connects. The Harmony pattern lets peers connect symmetrically — either peer can be the "server":

- Each peer listens on a well-known port
- When two peers discover each other, they both try to connect
- One connection succeeds, the other fails gracefully
- The result: a symmetric peer-to-peer connection with no designated server

This is essential for mobile and proximity-based networking where there's no natural server.

## Zyre — Framework for Distributed Computing

Zyre is an open-source framework built on ZeroMQ for proximity-based peer-to-peer applications. It provides:

- **Node identity** — each node has a unique UUID
- **Discovery** — UDP beaconing to find nearby nodes
- **Presence tracking** — join/leave events with heartbeat monitoring
- **Point-to-point messaging** — send messages by node ID
- **Group messaging** — broadcast to all nodes in the cluster
- **Virtual clusters** — logical grouping of nodes
- **File transfer** — built on FileMQ

### Zyre API

```c
//  Create and start a Zyre node
zyre_t *self = zyre_new ("MyNode");
zyre_set_hello (self, hello_handler, NULL);
zyre_set_world (self, world_handler, NULL);
zyre_set_whisper (self, whisper_handler, NULL);
zyre_set_shout (self, shout_handler, NULL);
zyre_start (self);

//  Send point-to-point message (whisper)
zyre_whispers (self, target_node_id, "Hello peer!");

//  Send group message (shout)
zyre_shouts (self, "Hello everyone!");

//  Clean up
zyre_destroy (&self);
```

### Events

- **HELLO** — received when a new node joins
- **WHISPER** — point-to-point message from another node
- **SHOUT** — group message from another node
- **BYE** — node has left the cluster
- **WORLD** — complete list of known nodes (sent on join and after changes)

## WiFi Considerations for Distributed Apps

WiFi has significant limitations for distributed computing:

- **Inverse power law** — signal strength drops with square of distance
- **Slowest device bottleneck** — when AP talks to slowest device, whole network waits
- **Unicast overhead** — each recipient gets separate transmission
- **Multicast at low rate** — multicast/broadcast uses lowest common denominator rate
- **AP as bottleneck** — can't exceed half of advertised speed
- **Interference** — neighboring APs on same channel cause significant degradation
- **Battery life** — WiFi is power-hungry when idle

### Recommendations

- Use `inproc` or `ipc` for local communication when possible
- Set appropriate HWM to prevent memory exhaustion on slow links
- Implement heartbeat-based presence detection with generous timeouts
- Consider PGM multicast for high fan-out on enterprise networks
- Design for intermittent connectivity (disconnected operation)

## Testing and Simulation

For testing distributed systems:

- Use `inproc` transport for fast in-process simulation
- Create many simulated nodes as threads sharing a context
- Use assertions to validate protocol behavior
- Trace activity with pub-sub capture sockets
- Test with varying delays and failure injection

```c
//  Simulate N nodes in a single process
for (int i = 0; i < NUM_NODES; i++) {
    zthread_fork (ctx, node_thread, &node_config[i]);
}
```

## Distributed Logging

Every node can log to a central logger via pub-sub:

```c
//  Logger (subscriber)
void *logger = zmq_socket (context, ZMQ_SUB);
zmq_bind (logger, "tcp://*:5556");
zmq_setsockopt (logger, ZMQ_SUBSCRIBE, "", 0);  //  Subscribe to all

//  Application node (publisher)
void *logpipe = zmq_socket (context, ZMQ_PUB);
zmq_connect (logpipe, "tcp://localhost:5556");
zmq_send (logpipe, "[2024-01-01] Node started", 26, 0);
```

For binary logging protocols, use a compact format with fixed-length headers for efficient parsing.

## Content Distribution

Two approaches:
- **Server-centric** — FTP, HTTP (centralized, simple)
- **Decentralized** — FileMQ, BitTorrent (distributed, resilient)

FileMQ provides reliable file distribution with:
- Incremental sync (only changes transferred)
- Credit-based flow control
- Late joiner support
- Delivery confirmation

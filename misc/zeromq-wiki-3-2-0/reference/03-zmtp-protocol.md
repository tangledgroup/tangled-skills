# ZMTP Protocol

## Overview

The ZeroMQ Message Transport Protocol (ZMTP) is a transport layer protocol for exchanging messages between two peers over a connected transport layer such as TCP. ZMTP 3.0 is the current stable specification (RFC 23).

The major change in ZMTP 3.0 from 2.0 is the addition of security mechanisms and the removal of hard-coded connection metadata (socket type and identity) from the greeting.

## Goals

- Provide a standard protocol for ZeroMQ message transport over TCP and other connected transports
- Support security mechanisms (NULL, PLAIN, CURVE) pluggably
- Allow version negotiation between peers
- Maintain backward compatibility with ZMTP 2.0 and 1.0

## Overall Behavior

ZMTP operates as a stateful protocol running on top of TCP (or other connected transports). The connection lifecycle:

1. **Greeting exchange** — Both sides send a greeting frame containing version and mechanism
2. **Security handshake** — Depending on the mechanism (NULL, PLAIN, CURVE)
3. **Message framing** — Messages are exchanged using ZMTP frames

## Framing

ZMTP frames consist of:

1. **Length prefix** — 1 byte (for messages < 255 bytes) or 1 + 8 bytes (for larger messages). If the first byte is 255, the next 8 bytes contain the length as a big-endian 64-bit integer.
2. **Flags byte** — Indicates frame properties (more frames follow, etc.)
3. **Body** — The actual message data

The "more" flag (bit 0 of flags) indicates whether more frames follow in the same multipart message. This allows ZeroMQ's multipart messaging to work across ZMTP connections.

## Version Negotiation

Each greeting contains the major and minor version numbers. The protocol uses the lower of the two versions supported by both peers. ZMTP 3.0 can interoperate with ZMTP 2.0 and 1.0 through detection mechanisms:

- If the peer sends a ZMTP 3.0 greeting, use ZMTP 3.0
- If the peer sends a ZMTP 2.0 greeting (detectable by format), fall back to ZMTP 2.0
- If the peer sends raw socket data (no greeting prefix), it may be ZMTP 1.0 or pre-ZMTP

## Security Mechanisms

ZMTP 3.0 supports pluggable security mechanisms:

### NULL (RFC 24)

No authentication, no encryption. The simplest mechanism. After greeting exchange with mechanism set to NULL, messages flow directly. Used for trusted networks.

```
zmq_setsockopt (socket, ZMQ_MECHANISM, &ZMQ_NULL, sizeof (int));
```

### PLAIN (RFC 24)

Username/password authentication using SASL PLAIN mechanism. No encryption. The client sends credentials; the server authenticates against a policy. Uses the ZAP (ZeroMQ Authentication Protocol, RFC 27) for server-side authentication.

```
// Client side
zmq_setsockopt (socket, ZMQ_MECHANISM, &ZMQ_PLAIN, sizeof (int));
zmq_setsockopt (socket, ZMQ_PLAIN_USERNAME, username, strlen (username));
zmq_setsockopt (socket, ZMQ_PLAIN_PASSWORD, password, strlen (password));

// Server side
zmq_setsockopt (socket, ZMQ_MECHANISM, &ZMQ_PLAIN, sizeof (int));
```

### CURVE (RFC 25)

Elliptic curve encryption and authentication. Uses the CurveZMQ specification (RFC 26). Provides:

- Mutual authentication using long-term public/private key pairs
- Short-term session keys for encrypted message exchange
- Perfect forward secrecy — session keys are discarded after the connection ends

```
// Server side
zmq_setsockopt (socket, ZMQ_MECHANISM, &ZMQ_CURVE, sizeof (int));
zmq_setsockopt (socket, ZMQ_CURVE_SERVER, &server_flag, sizeof (int));
zmq_setsockopt (socket, ZMQ_CURVE_PUBLICKEY, server_public, 32);
zmq_setsockopt (socket, ZMQ_CURVE_SECRETKEY, server_secret, 32);
zmq_setsockopt (socket, ZMQ_CURVE_SERVERKEY, client_public, 32);

// Client side
zmq_setsockopt (socket, ZMQ_MECHANISM, &ZMQ_CURVE, sizeof (int));
zmq_setsockopt (socket, ZMQ_CURVE_PUBLICKEY, client_public, 32);
zmq_setsockopt (socket, ZMQ_CURVE_SECRETKEY, client_secret, 32);
zmq_setsockopt (socket, ZMQ_CURVE_SERVERKEY, server_public, 32);
```

Key sizes: CURVE uses 32-byte (256-bit) keys based on Ed25519 signatures and XSalsa20-Poly1305 encryption.

## Connection Metadata

In ZMTP 3.0, connection metadata (socket type, identity) is not hard-coded in the greeting. Instead, it is exchanged as part of the security mechanism handshake or through socket semantics defined by the pattern.

## Socket Semantics

ZMTP defines how each ZeroMQ socket type behaves over the protocol:

### Request-Reply Pattern (RFC 28)

REQ and REP sockets create reply envelopes. The envelope consists of zero or more reply addresses, followed by an empty delimiter frame, followed by the message body. DEALER and ROUTER sockets handle envelopes explicitly — DEALER strips/inserts identity frames, ROUTER reads/forwards them.

### Publish-Subscribe Pattern (RFC 29)

PUB sends each message to all connected SUB sockets. SUB can filter by topic prefix. Subscription messages flow from SUB to PUB (the only back-chatter in pub-sub). XPUB/XSUB provide raw versions that expose subscription events.

### Pipeline Pattern (RFC 30)

PUSH distributes messages in round-robin to multiple PULL sockets. PULL fair-queues from multiple PUSH inputs. No back-chatter — fire-and-forget semantics.

### Exclusive Pair Pattern (RFC 31)

PAIR connects two sockets exclusively. Both sides can send and receive freely. Used for inter-thread communication within a process.

## Error Handling

ZMTP handles errors through the underlying transport (TCP connection close). When a peer disconnects, the local side detects this at the TCP level and cleans up the ZMTP session. There is no explicit error frame in ZMTP 3.0 — errors are implicit through connection termination.

## Related Specifications

- RFC 23: ZMTP 3.0 (stable)
- RFC 24: ZMTP NULL and PLAIN mechanisms (stable)
- RFC 25: ZMTP CURVE mechanism (stable)
- RFC 26: CurveZMQ specification (stable)
- RFC 27: ZAP — ZeroMQ Authentication Protocol (stable)
- RFC 37: ZMTP (draft, newer version)
- RFC 38: ZMTP-GSSAPI (draft)

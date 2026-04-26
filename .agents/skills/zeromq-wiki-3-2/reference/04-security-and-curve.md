# Security and CURVE

## Overview

ZeroMQ provides three security mechanisms through ZMTP: NULL (no security), PLAIN (username/password authentication), and CURVE (elliptic curve encryption and authentication). CURVE is the recommended mechanism for production use.

## NULL Mechanism

No authentication, no encryption. Use only on trusted networks where all peers are known and the network cannot be intercepted.

```c
int mechanism = ZMQ_NULL;
zmq_setsockopt (socket, ZMQ_MECHANISM, &mechanism, sizeof (int));
```

## PLAIN Mechanism

Username/password authentication using SASL PLAIN. Provides authentication but no encryption — credentials and messages travel in cleartext after authentication. Requires a ZAP (ZeroMQ Authentication Protocol) handler on the server side.

### Client Configuration

```c
int mechanism = ZMQ_PLAIN;
zmq_setsockopt (client, ZMQ_MECHANISM, &mechanism, sizeof (int));
zmq_setsockopt (client, ZMQ_PLAIN_USERNAME, "admin", 5);
zmq_setsockopt (client, ZMQ_PLAIN_PASSWORD, "secret", 6);
```

### Server Configuration

```c
int mechanism = ZMQ_PLAIN;
zmq_setsockopt (server, ZMQ_MECHANISM, &mechanism, sizeof (int));
```

### ZAP Handler

The server needs a ZAP handler process that receives authentication requests on a special PAIR socket and responds with accept/deny:

```c
// ZAP handler (simplified)
void *zap = zmq_socket (context, ZMQ_PAIR);
zmq_bind (zap, "inproc://zeromq.zap.01");

// Receive ZAP request (6 frames: version, sequence, domain, address, identity, username)
// Respond with: version, sequence, status_code, status_text, principal, rights
```

## CURVE Mechanism

CURVE provides mutual authentication and encrypted message transport using elliptic curve cryptography. Based on the CurveZMQ specification (RFC 26).

### How CURVE Works

1. Each peer has a long-term public/private key pair
2. During connection setup, peers exchange short-term keys securely using their long-term keys
3. Messages are encrypted using the short-term session keys
4. When the session ends, both sides discard short-term keys — even if long-term keys are later captured, past messages remain unreadable (perfect forward secrecy)

### Key Generation

Keys are 32 bytes (256 bits). CURVE uses Ed25519 for signatures and XSalsa20-Poly1305 for encryption. The CZMQ library provides `zcert` API for key management:

```c
// Generate a new certificate (key pair)
zcert_t *cert = zcert_new ();
// cert now contains public key (32 bytes) and secret key (32 bytes)

// Save to file
zcert_save (cert, "/path/to/my-cert.txt");

// Load from file
zcert_t *loaded = zcert_load ("/path/to/my-cert.txt");
```

### Server Configuration

```c
int mechanism = ZMQ_CURVE;
zmq_setsockopt (server, ZMQ_MECHANISM, &mechanism, sizeof (int));
int server_flag = 1;
zmq_setsockopt (server, ZMQ_CURVE_SERVER, &server_flag, sizeof (int));

// Set server's own key pair
zmq_setsockopt (server, ZMQ_CURVE_PUBLICKEY, server_public_key, 32);
zmq_setsockopt (server, ZMQ_CURVE_SECRETKEY, server_secret_key, 32);

// Optionally restrict to a specific client
zmq_setsockopt (server, ZMQ_CURVE_SERVERKEY, expected_client_public, 32);
```

### Client Configuration

```c
int mechanism = ZMQ_CURVE;
zmq_setsockopt (client, ZMQ_MECHANISM, &mechanism, sizeof (int));

// Set client's own key pair
zmq_setsockopt (client, ZMQ_CURVE_PUBLICKEY, client_public_key, 32);
zmq_setsockopt (client, ZMQ_CURVE_SECRETKEY, client_secret_key, 32);

// Set server's public key (for authentication)
zmq_setsockopt (client, ZMQ_CURVE_SERVERKEY, server_public_key, 32);
```

### Certificate Management with CZMQ

CZMQ provides `zcert` and `zcertstore` APIs:

```c
// Create certificate store
zcertstore_t *store = zcertstore_new ();

// Load server cert and register it
zcert_t *server_cert = zcert_new ();
zcertstore_set (store, server_cert);

// Create a client cert signed by the server
zcert_t *client_cert = zcert_new ();
zcert_sign (server_cert, client_cert);  // Server signs client cert

// Save both certs
zcert_save (server_cert, "/etc/zmq/server.cert");
zcert_save (client_cert, "/etc/zmq/client.cert");

// Apply to sockets
zcert_apply (server_cert, server_socket);
zcert_apply (client_cert, client_socket);
```

### zauth — Automatic Authentication

CZMQ's `zauth` module provides automatic authentication for PLAIN and CURVE:

```c
// Start automatic authentication
zauth_t *auth = zauth_new (server_socket);

// Allow all connections (for testing)
zauth_allow (auth, "0.0.0.0/0");

// Or deny all by default, then allow specific IPs
zauth_configure (auth);  // Sets up ZAP handler
zauth_allow (auth, "192.168.1.0/24");
zauth_deny (auth, "0.0.0.0/0");
```

## GSSAPI Mechanism

ZMTP also supports GSSAPI (Generic Security Services Application Program Interface) for Kerberos-based authentication (RFC 38, draft status). This provides:

- Kerberos ticket-based authentication
- Mutual authentication
- Encrypted message transport
- Integration with enterprise identity infrastructure

```c
int mechanism = ZMQ_GSSAPI;
zmq_setsockopt (socket, ZMQ_MECHANISM, &mechanism, sizeof (int));

// Server or client role
int client_flag = 0;  // 0 = server, 1 = client
zmq_setsockopt (socket, ZMQ_GSSAPI_SERVER, &client_flag, sizeof (int));

// GSSAPI principal name
zmq_setsockopt (socket, ZMQ_GSSAPI_PRINCIPAL, principal, strlen(principal));
```

## Security Best Practices

- Always use CURVE in production environments
- Never transmit CURVE secret keys over the network
- Store certificates on disk with restricted permissions
- Use certificate signing to establish trust relationships
- Rotate keys periodically
- For PLAIN, always use it over a TLS-protected transport or internal network
- Validate ZAP responses carefully — a misconfigured ZAP handler can deny all connections

## libcurve Reference Implementation

The `libcurve` project (github.com/zeromq/libcurve) provides a reference implementation of CurveZMQ. It is primarily intended for:

- Facilitating CurveZMQ implementations in other languages
- Providing security for older versions of ZeroMQ
- End-to-end security over untrusted intermediaries
- Security over transports that fit the one-to-one model (not multicast)

Dependencies: libsodium, libzmq, libczmq.

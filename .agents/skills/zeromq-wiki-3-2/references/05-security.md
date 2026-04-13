# ZeroMQ Security

This reference covers authentication mechanisms, encryption, and security best practices for ZeroMQ applications.

## Security Overview

ZeroMQ provides multiple security mechanisms:

| Mechanism | RFC | Encryption | Authentication | Use Case |
|-----------|-----|------------|----------------|----------|
| None | - | No | No | Development only |
| ZMTP-PLAIN | 24 | No | Username/Password | Simple auth, trusted networks |
| ZMTP-CURVE | 25 | Yes (AES-128) | Public keys | Production, untrusted networks |
| ZMTP-GSSAPI | 38 | Optional | Kerberos | Enterprise environments |

## ZMTP-PLAIN Authentication

Simple username/password authentication over ZMTP.

### Server Configuration

```c
#include <czmq.h>

int main(void) {
    void *context = zmq_init(1);
    void *server = zmq_socket(context, ZMQ_REP);
    
    // Set allowed credentials
    zauth_t *auth = zauth_new();
    zauth_allow(auth, "127.0.0.1");  // Allow localhost
    zauth_password(auth, "user", "password");  // Username/password
    
    zmq_setsockopt(server, ZMQ_AUTH_PLAIN, auth, sizeof(auth));
    
    zmq_bind(server, "tcp://*:5555");
    
    // Handle requests...
    
    zauth_destroy(&auth);
    zmq_close(server);
    zmq_term(context);
    return 0;
}
```

### Client Configuration

```c
int main(void) {
    void *context = zmq_init(1);
    void *client = zmq_socket(context, ZMQ_REQ);
    
    // Set credentials
    zmq_setsockopt(client, ZMQ_PLAIN_USERNAME, "user", 4);
    zmq_setsockopt(client, ZMQ_PLAIN_PASSWORD, "password", 8);
    
    zmq_connect(client, "tcp://server:5555");
    
    // Send requests...
    
    zmq_close(client);
    zmq_term(context);
    return 0;
}
```

### Security Considerations

**Pros:**
- Simple to implement
- No key management required
- Works with existing user databases

**Cons:**
- No encryption (credentials sent in plaintext)
- Passwords must be managed securely
- Vulnerable to network sniffing
- No mutual authentication

**Recommendation**: Use only on trusted networks or with TLS wrapper.

---

## ZMTP-CURVE Authentication

Public-key cryptography with end-to-end encryption using Curve25519 and AES-128-CBC.

### Key Generation

```c
#include <czmq.h>

// Generate key pair
uint8_t secret_key[32];
uint8_t public_key[32];

zmq_curve_keypair(secret_key, public_key);

// Convert to Z85 for storage/logging
char secret_z85[41];
char public_z85[41];
zmq_z85_encode(secret_z85, secret_key, 32);
zmq_z85_encode(public_z85, public_key, 32);

printf("Secret key: %s\n", secret_z85);
printf("Public key: %s\n", public_z85);
```

**Important**: Never share or log secret keys! Store them securely.

### Server Configuration

```c
int main(void) {
    void *context = zmq_init(1);
    void *server = zmq_socket(context, ZMQ_REP);
    
    // Generate or load server key pair
    uint8_t server_secret[32];
    uint8_t server_public[32];
    
    // Load from file or generate new
    // zmq_z85_decode(server_secret, "SERVER_SECRET_Z85_STRING");
    // zmq_z85_decode(server_public, "SERVER_PUBLIC_Z85_STRING");
    zmq_curve_keypair(server_secret, server_public);
    
    // Configure CURVE on server
    zmq_curve_keypair(server, server_secret, server_public);
    
    // Enable server mode (required for accepting connections)
    int yes = 1;
    zmq_setsockopt(server, ZMQ_CURVE_SERVER, &yes, sizeof(yes));
    
    // Optional: Require authentication from all clients
    // (default behavior when ZMQ_CURVE_SERVER is set)
    
    zmq_bind(server, "tcp://*:5555");
    
    // Handle requests...
    
    zmq_close(server);
    zmq_term(context);
    return 0;
}
```

### Client Configuration

```c
int main(void) {
    void *context = zmq_init(1);
    void *client = zmq_socket(context, ZMQ_REQ);
    
    // Generate or load client key pair
    uint8_t client_secret[32];
    uint8_t client_public[32];
    
    // Load from file or generate new
    // zmq_z85_decode(client_secret, "CLIENT_SECRET_Z85_STRING");
    // zmq_z85_decode(client_public, "CLIENT_PUBLIC_Z85_STRING");
    zmq_curve_keypair(client_secret, client_public);
    
    // Load server's public key (must match server's key)
    uint8_t server_public[32];
    zmq_z85_decode(server_public, "SERVER_PUBLIC_Z85_STRING");
    
    // Configure CURVE on client
    zmq_curve_keypair(client, server_public, client_public, client_secret);
    
    zmq_connect(client, "tcp://server:5555");
    
    // Send requests...
    
    zmq_close(client);
    zmq_term(context);
    return 0;
}
```

### Key Management

**Generating Keys:**
```bash
# Using Python and pyzmq
python3 << 'EOF'
import zmq.context
from zmq.auth.cert import generate_cert

# Generate server keys
server_cert = generate_cert()
print("Server secret:", server_cert.key)
print("Server public:", server_cert.public_key)

# Generate client keys
client_cert = generate_cert()
print("Client secret:", client_cert.key)
print("Client public:", client_cert.public_key)
EOF
```

**Storing Keys:**
- Store in files with restricted permissions (`chmod 600`)
- Use environment variables for deployment
- Consider using a secrets manager (HashiCorp Vault, AWS Secrets Manager)
- Never commit keys to version control

### Security Features

**What CURVE provides:**
1. **Authentication**: Server verifies client identity via public key
2. **Encryption**: All messages encrypted with AES-128-CBC
3. **Key Exchange**: Curve25519 for secure session key derivation
4. **Replay Protection**: Nonces prevent message replay attacks

**What CURVE does NOT provide:**
1. **Forward Secrecy**: Compromised long-term keys decrypt past traffic
2. **Server Authentication to Client**: Client trusts server's public key
3. **Perfect Forward Secrecy**: Session keys derived from long-term keys

### Security Considerations

**Pros:**
- Strong encryption (AES-128-CBC)
- No shared secrets (public-key cryptography)
- Resistant to man-in-the-middle (if keys verified)
- Built into libzmq, no external dependencies

**Cons:**
- Key management complexity
- Performance overhead (~10-20% slower than plaintext)
- No forward secrecy
- Server public key must be distributed securely

**Recommendation**: Use CURVE for all production systems over untrusted networks.

---

## ZAP (ZeroMQ Authentication Protocol)

ZAP provides centralized authentication via external service.

### ZAP Handler Architecture

```
[Client] --> [Server Socket] --> [ZAP Handler]
                          |
                          +--> [Returns: Allow/Deny]
```

### ZAP Message Format

**Request from server to ZAP handler:**
```
[Version (1 frame)]
[Sequence Number (1 frame)]
[Connection Hostname (1 frame)]
[Credentials (N frames)]
```

**Response from ZAP handler to server:**
```
[Version (1 frame)]
[Sequence Number (1 frame)]
[Status Code (1 frame): "200" = allow, "400" = deny]
[Status Text (1 frame)]
[User ID (1 frame, optional)]
```

### ZAP Handler Example

```c
#include <czmq.h>

int main(void) {
    void *context = zmq_init(1);
    
    // ZAP socket must be REP and bind to inproc://zmq.auth.0
    void *zap_socket = zmq_socket(context, ZMQ_REP);
    int rc = zmq_bind(zap_socket, "inproc://zmq.auth.0");
    if (rc != 0) {
        printf("Failed to bind ZAP socket: %s\n", zmq_strerror(rc));
        return 1;
    }
    
    while (1) {
        zmsg_t *request = zmsg_recv(zap_socket);
        
        // Parse request
        const char *version = zmsg_popstr(request);
        const char *sequence = zmsg_popstr(request);
        const char *identity = zmsg_popstr(request);
        const char *address = zmsg_popstr(request);
        const char *mechanism = zmsg_popstr(request);
        const char *key = zmsg_popstr(request);  // For CURVE: client public key
        
        printf("ZAP request: mechanism=%s, key=%s\n", mechanism, key);
        
        // Determine allow/deny (implement your auth logic here)
        const char *status = "200";  // Allow
        const char *status_text = "OK";
        const char *user_id = "";
        
        // Check against whitelist of allowed keys
        // if (!is_allowed_key(key)) {
        //     status = "400";
        //     status_text = "Deny";
        // }
        
        // Build response
        zmsg_t *reply = zmsg_new();
        zmsg_addstr(reply, version);  // Echo version
        zmsg_addstr(reply, sequence);  // Echo sequence
        zmsg_addstr(reply, status);    // Allow or deny
        zmsg_addstr(reply, status_text);
        zmsg_addstr(reply, user_id);   // Optional user ID
        
        zmsg_send(&reply, zap_socket);
        
        zmsg_destroy(&request);
    }
    
    zmq_close(zap_socket);
    zmq_term(context);
    return 0;
}
```

### Enabling ZAP on Server

```c
void *server = zmq_socket(context, ZMQ_REP);

// Enable ZAP authentication
int zap = 1;
zmq_setsockopt(server, ZMQ_ZAP_DOMAIN, "global", 6);

zmq_bind(server, "tcp://*:5555");
```

### Security Considerations

**Pros:**
- Centralized authentication logic
- Can integrate with existing auth systems (LDAP, Active Directory)
- Supports multiple mechanisms from single handler
- User ID propagation to application

**Cons:**
- ZAP handler becomes single point of failure
- In-process communication only (ZAP handler must be in same process)
- Complex to implement correctly

**Recommendation**: Use ZAP when you need centralized auth or integration with existing systems.

---

## Security Best Practices

### Key Management

1. **Generate keys securely**: Use cryptographically secure random number generator
2. **Store keys safely**: File permissions 600, encrypted storage, secrets manager
3. **Rotate keys periodically**: Implement key rotation without downtime
4. **Revoke compromised keys**: Maintain allow/deny lists
5. **Never log secret keys**: Only log public keys or identifiers

### Network Security

1. **Use CURVE in production**: Always encrypt over untrusted networks
2. **Bind to specific interfaces**: Don't bind to `*` in production
   ```c
   zmq_bind(socket, "tcp://192.168.1.100:5555");  // Specific IP
   ```
3. **Use firewalls**: Restrict access to ZeroMQ ports
4. **Monitor connections**: Use socket monitoring to detect anomalies
5. **Limit connections**: Set `ZMQ_BACKLOG` to prevent DoS

### Application Security

1. **Validate all input**: Don't trust message content from peers
2. **Implement timeouts**: Use `zmq_poll()` with timeout to prevent hangs
3. **Set appropriate HWM**: Prevent memory exhaustion attacks
   ```c
   int hwm = 1000;
   zmq_setsockopt(socket, ZMQ_SNDHWM, &hwm, sizeof(hwm));
   zmq_setsockopt(socket, ZMQ_RCVHWM, &hwm, sizeof(hwm));
   ```
4. **Handle authentication failures**: Log and alert on failed auth attempts
5. **Principle of least privilege**: Run with minimal permissions

### Configuration Hardening

```c
// Set socket options for security
void harden_socket(void *socket) {
    // Limit reconnect attempts to prevent DoS
    int max_reconnect = 1000;
    zmq_setsockopt(socket, ZMQ_RECONNECT_IVL_MAX, &max_reconnect, sizeof(max_reconnect));
    
    // Set reasonable buffer limits
    int bufsize = 256 * 1024;  // 256KB max
    zmq_setsockopt(socket, ZMQ_SNDBUF, &bufsize, sizeof(bufsize));
    zmq_setsockopt(socket, ZMQ_RCVBUF, &bufsize, sizeof(bufsize));
    
    // Set HWM to prevent memory exhaustion
    int hwm = 1000;
    zmq_setsockopt(socket, ZMQ_SNDHWM, &hwm, sizeof(hwm));
    zmq_setsockopt(socket, ZMQ_RCVHWM, &hwm, sizeof(hwm));
    
    // Enable keepalive to detect dead peers
    int keepalive = 1;
    zmq_setsockopt(socket, ZMQ_TCP_KEEPALIVE, &keepalive, sizeof(keepalive));
    int keepalive_idle = 30;  // 30 seconds
    zmq_setsockopt(socket, ZMQ_TCP_KEEPALIVE_IDLE, &keepalive_idle, sizeof(keepalive_idle));
}
```

### Monitoring and Logging

```c
// Enable security event logging
zsys_set_log_level(ZLOG_LEVEL_INFO);
zsys_set_logfile("zeromq_security.log");

// Monitor authentication events
zmq_socket_monitor(socket, "inproc://monitor", 
    ZMQ_EVENT_CONNECTED | 
    ZMQ_EVENT_DISCONNECTED |
    ZMQ_EVENT_MONITOR_STOPPED);
```

### Common Vulnerabilities

1. **Credential leakage**: Logging passwords or secret keys
2. **Unauthenticated access**: Running without auth in production
3. **Denial of service**: No HWM limits, allowing memory exhaustion
4. **Information disclosure**: Logging sensitive message content
5. **Replay attacks**: Not using CURVE or not validating nonces

---

## See Also

- [Protocols](04-protocols.md) - ZMTP wire protocol details
- [RFC 24/ZMTP-PLAIN](http://rfc.zeromq.org/spec:24/) - PLAIN authentication spec
- [RFC 25/ZMTP-CURVE](http://rfc.zeromq.org/spec:25/) - CURVE authentication spec
- [RFC 27/ZAP](http://rfc.zeromq.org/spec:27/) - ZAP protocol spec

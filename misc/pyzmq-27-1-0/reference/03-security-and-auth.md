# Security and Authentication

## Security Levels

libzmq provides four levels of security:

1. **NULL** — No authentication (default). The Authenticator does not see NULL connections unless policies are added. All incoming NULL connections are allowed by default (classic ZeroMQ behavior).
2. **PLAIN** — Username/password authentication over the wire.
3. **CURVE** — Public-key cryptography using libsodium.
4. **GSSAPI** — Kerberos-based authentication (requires no configuration in pyzmq).

## The Authenticator

`zmq.auth.Authenticator` implements ZAP (ZeroMQ Authentication Protocol) for authenticating incoming connections. It creates and binds a ZAP socket that libzmq uses to perform authentication.

### Basic Setup

```python
import zmq.auth

auth = zmq.auth.Authenticator(context)
auth.allow("127.0.0.1")  # allow localhost
auth.start()
```

The Authenticator does not register with an event loop by default. You must manually handle ZAP messages:

```python
while True:
    await auth.handle_zap_message(auth.zap_socket.recv_multipart())
```

Or register `auth.zap_socket` with a Poller.

### Running in Background

For non-blocking operation, use the provided subclasses:

- **`zmq.auth.thread.Authenticator`** — runs ZAP in a background thread
- **`zmq.auth.asyncio.Authenticator`** — integrates with asyncio event loop
- **`zmq.auth.ioloop.Authenticator`** — integrates with Tornado IOLoop

```python
from zmq.auth.thread import ThreadAuthenticator

auth = ThreadAuthenticator(context)
auth.allow("127.0.0.1")
auth.start()
```

### Allow and Deny Policies

`allow()` and `deny()` are mutually exclusive — use one or the other:

```python
# Whitelist approach
auth.allow("127.0.0.1")
auth.allow("192.168.1.0/24")

# Blacklist approach
auth.deny("10.0.0.0/8")
```

Connections from addresses not explicitly allowed (when using `allow`) are rejected. Addresses not explicitly denied (when using `deny`) proceed to authentication.

Set `auth.allow_any = True` to allow all IP addresses to proceed with authentication.

## PLAIN Authentication

PLAIN uses username/password pairs:

```python
auth.configure_plain(
    domain="*",
    passwords={"alice": "secret123", "bob": "password456"}
)
```

The password dictionary is stored in `auth.passwords` and can be modified at runtime — it is reloaded automatically.

### Client Side

```python
sock = ctx.socket(zmq.DEALER)
sock.plain_username = "alice"
sock.plain_password = "secret123"
sock.connect("tcp://server:5555")
```

## CURVE Authentication

CURVE uses public-key cryptography. Each client has a certificate (public + secret key pair).

### Creating Certificates

```python
import zmq.auth

# Create certificates
metadata = {"name": "alice"}
pub_file, sec_file = zmq.auth.create_certificates("/path/to/certs", "alice", metadata)
```

Certificates are stored as text files in the specified directory. The public key file name is the z85-encoded public key.

### Loading Certificates

```python
# Load a single certificate
public_key, secret_key = zmq.auth.load_certificate(pub_file)

# Load all certificates from a directory
certs = zmq.auth.load_certificates("/path/to/certs")
```

### Server Configuration

```python
auth.configure_curve(domain="*", location="/path/to/certs")
```

This tells the authenticator to accept any client whose public key exists in the certificates directory. Call `configure_curve` again whenever certificates are added or removed.

To allow all CURVE clients without checking keys:

```python
auth.configure_curve(domain="*", location=zmq.CURVE_ALLOW_ANY)
```

### Callback-Based Validation

For database-backed credential checking:

```python
class CredentialsProvider:
    def callback(self, domain, key):
        # lookup key in database
        valid = check_db(domain, key)
        return valid

auth.configure_curve_callback(
    domain="*",
    credentials_provider=CredentialsProvider()
)
```

### Client Side

```python
public_key, secret_key = zmq.auth.load_certificate("/path/to/alice.cert.key")
sock.curve_publickey = public_key
sock.curve_secretkey = secret_key
sock.curve_serverkey = server_public_key  # server's public key
sock.connect("tcp://server:5555")
```

### User-Id Mapping

Override `auth.curve_user_id(client_public_key)` to map public keys to user IDs. Default implementation returns the z85-encoding of the public key:

```python
class CustomAuth(zmq.auth.Authenticator):
    def curve_user_id(self, client_public_key):
        return lookup_user_in_db(client_public_key)
```

## GSSAPI Authentication

GSSAPI (Kerberos) requires no pyzmq configuration:

```python
auth.configure_gssapi(domain="*")  # currently a no-op
```

Ensure Kerberos is properly configured on both client and server systems.

## Security Best Practices

- Always enable CURVE encryption when possible
- Never use `recv_pyobj` (pickle) on sockets that might receive untrusted messages
- Use IPC socket permissions for local communication
- Authenticate messages with HMAC digests or other signing mechanisms before deserializing
- Enable CURVE to prevent unauthorized messages at the transport level

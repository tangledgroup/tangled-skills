# Security

Configuring TLS, authentication, and access control for production rqlite deployments.

## Overview

rqlite supports comprehensive security features including TLS encryption for all communications and role-based access control (RBAC). Proper security configuration is essential for production deployments.

## TLS/SSL Encryption

### Why Use TLS?

- **Data in Transit**: Encrypts client-server and inter-node communication
- **Authentication**: Verifies node identity via certificates
- **Compliance**: Meets security requirements for regulated environments

### Generating Certificates

Using OpenSSL:

```bash
# Create directory for certificates
mkdir -p certs
cd certs

# Generate CA private key
openssl genrsa -out ca.key 4096

# Generate CA certificate
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "/CN=rqlite-ca/O=rqlite/C=US"

# Generate server private key
openssl genrsa -out server.key 2048

# Generate certificate signing request
openssl req -new -key server.key -out server.csr \
  -subj "/CN=rqlite-node/O=rqlite/C=US"

# Sign the certificate with CA
openssl x509 -req -days 1825 -in server.csr \
  -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out server.crt

# Generate client certificate (optional, for mutual TLS)
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr \
  -subj "/CN=rqlite-client/O=rqlite/C=US"
openssl x509 -req -days 1825 -in client.csr \
  -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out client.crt
```

### Starting rqlite with TLS

```bash
rqlited -node-id=1 \
  -http-cert=/path/to/server.crt \
  -http-key=/path/to/server.key \
  -cluster-cert=/path/to/server.crt \
  -cluster-key=/path/to/server.key \
  -cluster-ca-cert=/path/to/ca.crt \
  /var/lib/rqlite/node1
```

**Flags:**
- `-http-cert`, `-http-key`: TLS for HTTP API (client connections)
- `-cluster-cert`, `-cluster-key`: TLS for Raft cluster communication
- `-cluster-ca-cert`: CA certificate for verifying other nodes

### Connecting with TLS

```bash
# Via shell with CA verification
rqlite -H rqlite.example.com -s https -c /path/to/ca.crt

# Skip verification (development only)
rqlite -H rqlite.example.com -s https -i

# Via curl
curl -k https://localhost:4001/status  # -k skips verification
curl --cacert ca.crt https://localhost:4001/status  # Proper verification

# With client certificate (mutual TLS)
curl --cert client.crt --key client.key \
  --cacert ca.crt https://localhost:4001/status
```

### Docker with TLS

```yaml
version: '3'
services:
  rqlite1:
    image: rqlite/rqlite:latest
    ports:
      - "4001:4001"
    command:
      - "-node-id=1"
      - "-http-cert=/certs/server.crt"
      - "-http-key=/certs/server.key"
      - "-cluster-cert=/certs/server.crt"
      - "-cluster-key=/certs/server.key"
      - "-cluster-ca-cert=/certs/ca.crt"
    volumes:
      - ./data:/rqlite
      - ./certs:/certs:ro
```

## Authentication

### Basic Authentication

Enable username/password authentication:

```bash
rqlited -node-id=1 \
  -http-auth-users=admin:password123,readonly:user123 \
  /var/lib/rqlite/node1
```

**Multiple users:**
```bash
rqlited -http-auth-users="admin:pass1,readonly:pass2,analyst:pass3"
```

**Connect with authentication:**

```bash
# Via shell
rqlite -H localhost -u admin:password123

# Via curl
curl -u admin:password123 http://localhost:4001/status

# With TLS
curl -u admin:password123 --cacert ca.crt https://localhost:4001/status
```

### Authentication with Docker

```yaml
services:
  rqlite1:
    image: rqlite/rqlite:latest
    environment:
      - HTTP_AUTH_USERS=admin:${ADMIN_PASSWORD}
    command:
      - "-node-id=1"
      - "-http-auth-users=\$HTTP_AUTH_USERS"
```

## Role-Based Access Control (RBAC)

### Built-in Roles

rqlite supports role-based permissions:

| Role | Permissions |
|------|-------------|
| `admin` | Full read and write access |
| `readonly` | Read-only access (SELECT, PRAGMA) |
| Custom | Define custom roles with specific permissions |

### Configuring Roles

```bash
# Create users with specific roles
rqlited -http-auth-users="admin:pass1,readonly_user:pass2" \
  -http-admin-users=admin \
  /var/lib/rqlite/node1
```

**Flags:**
- `-http-auth-users`: Define users and passwords
- `-http-admin-users`: Users with admin role (comma-separated)
- Other users default to readonly role

### Testing Role Permissions

```bash
# Admin user - can write
rqlite -H localhost -u admin:pass1
CREATE TABLE test (id INTEGER)  # SUCCESS

# Readonly user - cannot write
rqlite -H localhost -u readonly_user:pass2
CREATE TABLE test (id INTEGER)  # ERROR: permission denied
SELECT * FROM users             # SUCCESS
```

## Security Best Practices

### Certificate Management

1. **Use strong keys**: 2048-bit minimum for RSA, prefer Ed25519
2. **Set appropriate expiration**: 1-5 years for server certs
3. **Rotate certificates**: Plan for renewal before expiration
4. **Secure private keys**: Use file permissions `600` or `400`
5. **Use separate CA**: Don't use server cert as CA

```bash
# Secure certificate files
chmod 600 server.key client.key ca.key
chmod 644 server.crt client.crt ca.crt
chown -R rqlite:rqlite certs/
```

### Password Security

1. **Use strong passwords**: Minimum 16 characters, mix of character types
2. **Store securely**: Use secrets management (Vault, AWS Secrets Manager)
3. **Rotate regularly**: Change passwords periodically
4. **Never commit to version control**: Use environment variables or secrets

```bash
# Generate strong password
openssl rand -base64 32

# Store in environment
export RQLITE_ADMIN_PASSWORD=$(openssl rand -base64 32)
```

### Network Security

1. **Firewall rules**: Restrict access to trusted IPs
2. **Use private networks**: Don't expose rqlite publicly
3. **Separate HTTP and Raft ports**: Different security policies
4. **Monitor connections**: Log and alert on unusual activity

```bash
# Example iptables rules
iptables -A INPUT -p tcp --dport 4001 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 4002 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 4001 -j REJECT
iptables -A INPUT -p tcp --dport 4002 -j REJECT
```

### Audit Logging

Enable request logging for security auditing:

```bash
rqlited -node-id=1 \
  -http-addr=:4001 \
  -log-level=info \
  /var/lib/rqlite/node1
```

Monitor logs for:
- Failed authentication attempts
- Unauthorized access attempts
- Unusual query patterns
- Connection from unknown IPs

## Secure Deployment Examples

### Production Cluster with Full Security

```bash
# Node 1 (bootstrap)
rqlited -node-id=1 \
  -http-addr=0.0.0.0:4001 \
  -raft-addr=0.0.0.0:4002 \
  -http-cert=/etc/rqlite/certs/server.crt \
  -http-key=/etc/rqlite/certs/server.key \
  -cluster-cert=/etc/rqlite/certs/server.crt \
  -cluster-key=/etc/rqlite/certs/server.key \
  -cluster-ca-cert=/etc/rqlite/certs/ca.crt \
  -http-auth-users="admin:\$ADMIN_PASS,app:\$APP_PASS,readonly:\$RO_PASS" \
  -http-admin-users=admin \
  /var/lib/rqlite/node1

# Node 2 (join)
rqlited -node-id=2 \
  -http-addr=0.0.0.0:4001 \
  -raft-addr=0.0.0.0:4002 \
  -join=node1.example.com:4002 \
  -http-cert=/etc/rqlite/certs/server.crt \
  -http-key=/etc/rqlite/certs/server.key \
  -cluster-cert=/etc/rqlite/certs/server.crt \
  -cluster-key=/etc/rqlite/certs/server.key \
  -cluster-ca-cert=/etc/rqlite/certs/ca.crt \
  -http-auth-users="admin:\$ADMIN_PASS,app:\$APP_PASS,readonly:\$RO_PASS" \
  -http-admin-users=admin \
  /var/lib/rqlite/node2
```

### Docker Compose with Security

```yaml
version: '3'
services:
  rqlite1:
    image: rqlite/rqlite:latest
    ports:
      - "4001:4001"
    environment:
      - HTTP_AUTH_USERS=${AUTH_USERS}
      - HTTP_ADMIN_USERS=${ADMIN_USERS}
    command:
      - "-node-id=1"
      - "-http-cert=/certs/server.crt"
      - "-http-key=/certs/server.key"
      - "-cluster-cert=/certs/server.crt"
      - "-cluster-key=/certs/server.key"
      - "-cluster-ca-cert=/certs/ca.crt"
      - "-http-auth-users=\$HTTP_AUTH_USERS"
      - "-http-admin-users=\$HTTP_ADMIN_USERS"
    volumes:
      - rqlite1-data:/rqlite
      - ./certs:/certs:ro
    networks:
      - rqlite-net

networks:
  rqlite-net:
    driver: bridge
```

## Troubleshooting Security Issues

### Certificate Errors

**Problem:** `x509: certificate signed by unknown authority`

**Solution:** Ensure CA certificate is correctly specified:
```bash
rqlited -cluster-ca-cert=/path/to/ca.crt ...
```

**Problem:** `x509: certificate has expired`

**Solution:** Generate new certificates with longer validity:
```bash
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt
```

### Authentication Errors

**Problem:** `401 Unauthorized`

**Solution:** Verify credentials and user configuration:
```bash
# Check user is configured
ps aux | grep rqlited | grep http-auth-users

# Test with correct credentials
curl -u admin:correct_password http://localhost:4001/status
```

### Permission Denied

**Problem:** Readonly user trying to write

**Solution:** Use admin user for write operations, or grant appropriate permissions.

## Next Steps

- Optimize [performance](09-performance.md) while maintaining security
- Set up [monitoring](10-monitoring.md) for security events
- Configure [backups](05-backup-restore.md) with encryption
- Implement [CDC](11-cdc.md) with secure streaming

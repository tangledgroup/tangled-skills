# Security and Encryption

## TLS Configuration

Configure TLS for secure access by setting `RUSTFS_TLS_PATH` to a directory containing `rustfs_cert.pem` and `rustfs_key.pem`.

### Linux (systemd)

```bash
# Edit /etc/default/rustfs
RUSTFS_TLS_PATH="/opt/tls"

# Restart
systemctl restart rustfs
```

Access via `https://your-host:9001`.

### Docker

```bash
docker run -d \
  --name rustfs \
  -e RUSTFS_TLS_PATH="/opt/tls/" \
  -v /path/to/certs:/opt/tls \
  -p 9000:9000 -p 9001:9001 \
  -v /data:/data \
  rustfs/rustfs:latest
```

Ensure certificate files are owned by UID 10001 (the `rustfs` container user).

TLS v1.2+ is supported between all cluster components with CPU-level optimizations for negligible performance overhead. SNI is supported for multiple certificates per domain.

## Server-Side Encryption

RustFS encrypts data at rest using industry-standard algorithms:
- **AES-256-GCM**: Authenticated encryption with SIMD acceleration
- **ChaCha20-Poly1305**: High-performance alternative
- **AES-CBC**: Legacy compatibility

### SSE-S3 (Server-Side Encryption with S3 Managed Keys)

Automatic bucket-level encryption. Each object encrypted with a unique key, multiple layers of additional encryption using dynamic keys derived from external KMS or client-provided keys.

### SSE-C (Server-Side Encryption with Customer-Provided Keys)

Client-driven encryption where applications specify the data key used to encrypt objects. The RustFS server performs all encryption operations including key rotation and re-encryption.

## Key Management Service Integration

RustFS supports multiple external KMS systems:
- AWS KMS
- HashiCorp Vault
- Google Secret Manager
- Azure Key Vault
- Thales CipherTrust (formerly Gemalto KeySecure)
- Fortanix

### RustFS Key Encryption Service (KES)

Built-in stateless distributed key management system. Acts as intermediary between RustFS clusters and external KMS, generating encryption keys on demand without being limited by KMS rate constraints.

Key features:
- Stateless design — auto-scales via Kubernetes HPA
- Handles majority of application requests independently
- Central KMS protects master keys as root of trust
- Applications request DEKs from KES servers
- Kubernetes Operator deploys/configures KES per tenant

## Identity and Access Management (IAM)

RustFS provides comprehensive IAM management:
- User management
- User group management
- Policy management (S3-compatible IAM policies)
- Bucket policies
- Access keys (AK/SK) management
- AWS Signature V4 authentication

### OIDC Integration

Supports OpenID Connect with configurable roles claim. For Microsoft Entra ID:

```bash
RUSTFS_IDENTITY_OPENID_ENABLE=on
RUSTFS_IDENTITY_OPENID_CONFIG_URL="https://login.microsoftonline.com/<tenant-id>/v2.0/.well-known/openid-configuration"
RUSTFS_IDENTITY_OPENID_CLIENT_ID="<client-id>"
RUSTFS_IDENTITY_OPENID_CLIENT_SECRET="<client-secret>"
RUSTFS_IDENTITY_OPENID_SCOPES="openid,profile,email"
RUSTFS_IDENTITY_OPENID_ROLES_CLAIM="roles"
```

Policy condition example using JWT roles:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["admin:*"],
    "Resource": ["arn:aws:s3:::*"],
    "Condition": {
      "ForAnyValue:StringEquals": {
        "jwt:roles": ["RustFS.ConsoleAdmin"]
      }
    }
  }]
}
```

## Object Locking (WORM)

Write-Once-Read-Many protection with three modes:

### Governance Mode

Prevents deletion by standard users. Users with `s3:BypassGovernanceRetention` permission can modify retention or delete objects.

### Compliance Mode

No one (including root user) can delete objects during the retention period.

### Legal Hold

Indefinite WORM protection without expiration date. Only authorized users can remove legal holds.

Retention can be set via:
- **Bucket default**: Duration in days/years, inherited by new objects
- **Explicit per-object**: "Retain until" date
- Explicit retention overrides bucket defaults
- Retention periods can be extended

RustFS meets Cohasset Associates standards for SEC Rule 17a-4(f), FINRA Rule 4511, and CFTC Regulation 1.31.

## Network Security

- TLS v1.2+ between all cluster components
- No weak links in encrypted traffic within or between clusters
- CPU-optimized TLS implementation with negligible overhead
- Trusted proxies management for reverse proxy deployments
- CORS configuration for cross-origin access control

## Data Sovereignty

RustFS has no telemetry and ensures full compliance with:
- GDPR (EU/UK)
- CCPA (US)
- APPI (Japan)

This guards against unauthorized cross-border data egress, making it suitable for regulated industries and government deployments.

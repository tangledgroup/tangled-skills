# Security and Encryption

## TLS Configuration

Set `RUSTFS_TLS_PATH` to a directory containing `rustfs_cert.pem` and `rustfs_key.pem`:

```bash
RUSTFS_TLS_PATH=/opt/tls
```

Certificates must be named exactly `rustfs_cert.pem` and `rustfs_key.pem`. For Docker:

```bash
docker run -d \
  -e RUSTFS_TLS_PATH="/opt/tls/" \
  -v /opt/tls:/opt/tls \
  -p 9000:9000 -p 9001:9001 \
  -v /data:/data \
  rustfs/rustfs:latest
```

Ensure certificate files are owned by the `rustfs` user (UID 10001) inside the container.

## Server-Side Encryption

- **SSE-S3**: RustFS generates and manages encryption keys automatically
- **SSE-C**: Client provides the encryption key with each request
- **KMS Integration**: External key management systems for enterprise deployments (under testing in beta.1)

Request SSE-S3 encryption:

```bash
mc cp file.txt myrustfs/bucket/ --encrypt
```

Request SSE-C encryption:

```bash
mc cp file.txt myrustfs/bucket/ --encrypt-key "my-secret-key"
```

## IAM Management

RustFS supports S3-compatible IAM with users, groups, and policies. The beta.1 release includes several IAM hardening fixes:

- **Cache miss handling**: IAM cache load failures are now properly propagated instead of silently failing
- **Portable IAM storage**: Derived authentication credentials are preserved across IAM store operations
- **Error mapping**: IAM not-found errors correctly return HTTP 404
- **Logging**: Walk failures in IAM listing paths are now logged for debugging

### Access Tokens

Generate short-lived access tokens via the console or API. Tokens inherit the parent user's permissions and can be revoked independently.

## WORM Object Locking

Write-Once-Read-Many (WORM) compliance supports regulatory requirements:

- **Retention periods**: Fixed or legal hold retention
- **Compliance mode**: Objects cannot be deleted before retention expires, even by admins
- **Governance mode**: Objects can be unlocked with special permissions

## OIDC Integration

RustFS supports OpenID Connect for identity federation:

```bash
RUSTFS_IDENTITY_OPENID_ENABLE=on
RUSTFS_IDENTITY_OPENID_CONFIG_URL="https://oidc-provider/.well-known/openid-configuration"
RUSTFS_IDENTITY_OPENID_CLIENT_ID="<client-id>"
RUSTFS_IDENTITY_OPENID_CLIENT_SECRET="<client-secret>"
RUSTFS_IDENTITY_OPENID_SCOPES="openid,profile,email"
RUSTFS_IDENTITY_OPENID_GROUPS_CLAIM="groups"
RUSTFS_IDENTITY_OPENID_ROLES_CLAIM="roles"
```

The `roles_claim` setting (beta.1) allows mapping OIDC role claims into the authorization pipeline alongside group claims, enabling Microsoft Entra ID app roles in both console admin checks and bucket IAM policies.

## Audit and Notify Modules (beta.1)

The beta.1 release adds console-managed switches for audit and notification modules. These can be toggled from the RustFS console without restarting the service, allowing runtime control over logging verbosity and alert delivery channels.

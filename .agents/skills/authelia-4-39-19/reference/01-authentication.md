# Authentication

## Contents
- First Factor (Authentication Backend)
  - LDAP Backend
  - File Backend
- Second Factor
  - Time-based One-Time Password (TOTP)
  - WebAuthn (Security Keys and Passkeys)
  - Duo / Mobile Push Notifications
- Password Policy
- Identity Validation
  - Elevated Session
  - Reset Password

## First Factor (Authentication Backend)

The first factor is username + password ("something you know"). Authelia supports two backends — choose one.

### LDAP Backend

Connect to an existing directory service for user authentication and group membership resolution.

```yaml
authentication_backend:
  ldap:
    address: 'ldap://127.0.0.1'
    implementation: 'custom'
    timeout: '5s'
    start_tls: false
    tls:
      server_name: 'ldap.example.com'
      skip_verify: false
      minimum_version: 'TLS1.2'
      maximum_version: 'TLS1.3'
      certificate_chain: |
        -----BEGIN CERTIFICATE-----
        ...
        -----END CERTIFICATE-----
    pooling:
      enable: true
      count: 0
      retries: 3
      timeout: '5s'
    base_dn: 'dc=example,dc=com'
    additional_users_dn: 'ou=users'
    users_filter: '(&({username_attribute}={input})(objectClass=person))'
    additional_groups_dn: 'ou=groups'
    groups_filter: '(|(member={dn})(memberUid={username}))'
    group_search_mode: 'filter'
    permit_referrals: false
    permit_unauthenticated_bind: false
    user: 'cn=read-only-admin,dc=example,dc=com'
    password: 'password'
    attributes:
      username: 'uid'
      mail: 'mail'
      display_name: 'cn'
      member_of: 'memberOf'
```

**Key options:**

- `implementation` — one of `custom`, `active_directory`, `freeipa`, `okd`, or `rlinux`. Authelia adjusts default filters and attributes per implementation.
- `users_filter` — Go template with `{input}` replaced by the username entered at login. Use `{username_attribute}` to reference the configured username attribute.
- `groups_filter` — Go template with `{dn}`, `{username}`, and `{mail}` available for group membership lookup.
- `group_search_mode` — `filter` (use groups_filter) or `dn` (extract from distinguished name).
- `attributes` — map LDAP attributes to Authelia's internal user model. Supports OIDC claims: `display_name`, `family_name`, `given_name`, `mail`, `member_of`, `group_name`, plus custom extra attributes with `name`, `value_type`, and `multi_valued`.
- `permit_unauthenticated_bind` — when true, Authelia performs anonymous search for the user's DN, then binds as that user. Required by some directory implementations.
- `refresh_interval` — how often group membership is re-fetched (duration string, default 1m).

**Password**: Use a secret file via environment variable instead of inline:

```yaml
authentication_backend:
  ldap:
    password: '{{ .AUTHELIA_LDAP_PASSWORD }}'
```

Set `AUTHELIA_LDAP_PASSWORD_FILE=/secrets/LDAP_PASSWORD` in the container.

### File Backend

Flat YAML file for small deployments or testing. Authelia generates this on first run if it does not exist.

```yaml
authentication_backend:
  file:
    path: '/config/users_database.yml'
    watch: true
    password:
      algorithm: 'argon2'
      argon2:
        variant: 'argon2id'
        iterations: 3
        memory: 65536
        parallelism: 4
        key_length: 32
        salt_length: 16
```

**Key options:**

- `path` — absolute path to the users database YAML file.
- `watch` — auto-reload when the file changes (useful for development).
- `password.algorithm` — `argon2` (recommended) or `bcrypt`.
- `password.argon2.*` — tuning parameters for Argon2id hashing. Higher memory and iterations increase security but slow authentication.

The users database format:

```yaml
---
users:
  authelia:
    disabled: false
    displayname: 'Authelia User'
    email: 'authelia@example.com'
    password: '$argon2id$v=19$m=65536,t=3,p=4$...'
    groups:
      - admins
      - dev
...
```

Generate passwords with the reference guide's password generation utilities. The default user is `authelia` with password `authelia` — change immediately.

## Second Factor

Second factor ("something you have") is optional per access control rule but required when policy is `two_factor`. Three methods available — enable one or more.

### Time-based One-Time Password (TOTP)

RFC 6234 compliant TOTP using SHA-1, SHA-256, or SHA-512.

```yaml
totp:
  disable: false
  algorithm: 'sha1'
  digits: 6
  period: 30
  skew: 1
  issuer: 'authelia.com'
  secret: '{{ .AUTHELIA_TOTP_SECRET }}'
```

- `algorithm` — `sha1`, `sha256`, or `sha512`. SHA-1 is the RFC default and most compatible.
- `digits` — 6 (standard) or 8.
- `period` — seconds between code rotations (default 30).
- `skew` — allows codes within ±N periods of current time (accounts for clock drift).
- `issuer` — displayed in authenticator apps to identify the account.
- `secret` — HMAC secret, use a secret file in production.

### WebAuthn (Security Keys and Passkeys)

FIDO2/WebAuthn support for hardware security keys and platform passkeys (Touch ID, Windows Hello, Android Face Unlock).

```yaml
webauthn:
  disable: false
  timeout: '60s'
  services:
    internal:
      acquire:
        credential_id: '{{ .AUTHELIA_WEBAUTHN_CREDENTIAL_ID }}'
```

- `timeout` — how long the WebAuthn ceremony waits for user interaction.
- Supports both cross-platform devices (YubiKey, SoloKey) and platform devices (Touch ID, Windows Hello).
- Passkeys enable passwordless authentication when combined with first-factor bypass policies.
- The Relying Party Identifier is derived from the session cookie domain configuration.

### Duo / Mobile Push Notifications

Duo Security integration for mobile push-based second factor.

```yaml
duo:
  disable: false
  hostname: 'api-xxxxxx.duosecurity.com'
  integration_key: 'XXXXXXXXXXXXXXXXX'
  secret_key: '{{ .AUTHELIA_DUO_SECRET_KEY }}'
```

- Requires a Duo Security account and application registration.
- `hostname`, `integration_key`, and `secret_key` from the Duo Admin Panel.
- Push notifications sent to user's registered mobile device.
- Always use secret files for `secret_key`.

## Password Policy

Enforce minimum password strength requirements during first-factor authentication.

```yaml
password:
  policy:
    enabled: true
    criteria:
      min_length: 8
      max_length: 0
      require_uppercase: true
      require_lowercase: true
      require_number: true
      require_special: true
    messages:
      too_short: 'Password must be at least {min} characters long'
      too_long: 'Password must be at most {max} characters long'
      no_uppercase: 'Password must contain an uppercase letter'
      no_lowercase: 'Password must contain a lowercase letter'
      no_number: 'Password must contain a number'
      no_special: 'Password must contain a special character'
```

- `min_length` / `max_length` — 0 for max means unlimited.
- Criteria are checked independently; all enabled criteria must pass.
- Messages support `{min}` and `{max}` template variables.
- Policy applies to password changes (reset password flow) and initial setup, not to existing passwords in LDAP backends.

## Identity Validation

### Elevated Session

When a user authenticates with only one factor but the resource requires two factors, Authelia creates an "elevated session" requiring the user to complete 2FA for that specific request while maintaining their 1FA session.

```yaml
identity_validation:
  password:
    reset_password:
      jwt_secret: '{{ .AUTHELIA_IDENTITY_VALIDATION_RESET_PASSWORD_JWT_SECRET }}'
      identity_validators:
        - name: 'emails'
          notifier_name: 'smtp'
          template_path: '/config/reset-password.html'
```

### Reset Password

Self-service password reset via email validation. Users receive an email with a signed JWT link to set a new password.

- `jwt_secret` — signs the reset password tokens. Must be a strong random string, use secret files.
- `identity_validators` — list of validators that send verification emails. Each references a notifier by name.
- `template_path` — path to the HTML email template (customizable).
- Works with both LDAP and file backends for password changes.
- For LDAP backends, Authelia binds as the configured service account to update user passwords.

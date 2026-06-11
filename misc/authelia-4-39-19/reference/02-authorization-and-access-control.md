# Authorization and Access Control

## Contents
- Access Control Rules
  - Rule Options
  - Policies
  - Rule Matching
  - Named Regex Groups
- Regulation (Brute-Force Protection)
- Trusted Header SSO

## Access Control Rules

Authelia uses sequential rule-based access control. Rules are evaluated in order; first match wins. Unmatched requests fall through to `default_policy`.

**Important**: Access control rules do not apply to OpenID Connect 1.0. OIDC has its own separate authorization policies configuration.

### Rule Options

```yaml
access_control:
  default_policy: 'deny'
  rules:
    - domain: 'private.example.com'
      domain_regex: '^(\d+\-)?priv-img\.example\.com$'
      policy: 'one_factor'
      networks:
        - 'internal'
        - '1.1.1.1'
      subject:
        - ['user:adam']
        - ['user:fred']
        - ['group:admins']
      methods:
        - 'GET'
        - 'HEAD'
      resources:
        - '^/api.*'
      query:
        - - operator: 'present'
            key: 'secure'
          - operator: 'absent'
            key: 'insecure'
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `domain` | list(string) | Yes (with domain_regex) | Exact domain or glob pattern (`*.example.com`). At least one of `domain` or `domain_regex` required. |
| `domain_regex` | string | Yes (with domain) | Regex for domain matching. Named capture groups extract values for use in other criteria. At least one of `domain` or `domain_regex` required. |
| `policy` | string | Yes | Policy applied when all criteria match: `deny`, `bypass`, `one_factor`, `two_factor`. |
| `subject` | list(list(string)) | No | User/group criteria. Each inner list is OR'd; outer list is AND'd. Format: `user:name` or `group:name`. |
| `methods` | list(string) | No | HTTP methods to match (e.g., `GET`, `POST`). |
| `networks` | list(string) | No | CIDR ranges, IPs, or named network groups from definitions. |
| `resources` | list(string) | No | Regex patterns matching the request path. |
| `query` | list(list(object)) | No | Query parameter conditions with operators: `present`, `absent`, `pattern`, `not pattern`. Inner list is AND'd, outer list is OR'd. |

### Policies

- **deny** — Access denied regardless of authentication state. Recommended as `default_policy`.
- **bypass** — No authentication required. Use for public endpoints or health checks.
- **one_factor** — User must be authenticated with 1FA (password).
- **two_factor** — User must complete both 1FA and 2FA.

### Rule Matching

Two critical concepts:

1. **Sequential Order**: Rules are evaluated top to bottom. The first rule where all criteria match determines the policy. Place specific rules before general ones.

2. **Subject Criteria Requires Authentication**: A rule with `subject` criteria cannot match an unauthenticated user. The user must already be logged in for their identity to be checked against subject conditions. To require authentication for a domain, use a rule without `subject`:

```yaml
# Correct: requires 1FA for all users on this domain
- domain: 'app.example.com'
  policy: one_factor

# Then: admins get 2FA, others keep their existing session level
- domain: 'app.example.com'
  subject: ['group:admins']
  policy: two_factor
```

### Named Regex Groups

Use named capture groups in `domain_regex` to reference matched values in other criteria:

```yaml
rules:
  - domain_regex: '^(?P<tenant>\w+)\.example\.com$'
    resources:
      - '^/api/(?P<tenant>\w+)/.*$'
    policy: one_factor
```

When `domain_regex` and `resources` both define a named group with the same name, the values must match for the rule to apply. This enables tenant-scoped access control where users can only access resources matching their tenant subdomain.

## Regulation (Brute-Force Protection)

Regulation prevents brute-force attacks by tracking failed authentication attempts and temporarily blocking users.

```yaml
regulation:
  max_retries: 3
  find_time: '2m'
  ban_time: '5m'
  implementation: 'default'
  temporary_ban_ttl: '15m'
  policy: 'reset'
  enable_control_header: true
```

| Option | Default | Description |
|--------|---------|-------------|
| `max_retries` | 3 | Failed attempts before ban triggers. |
| `find_time` | 2m | Time window for counting retries. |
| `ban_time` | 5m | Duration of the temporary ban. |
| `temporary_ban_ttl` | 15m | How long ban records are kept in storage. |
| `policy` | reset | `reset` clears retry count on success; `success_partial` reduces by one; `none` never resets. |
| `enable_control_header` | true | Adds `Retry-After` header to 403 responses. |

Regulation tracks per-user and per-IP failures. When max retries is exceeded within the find time window, the user receives a temporary ban. After ban time expires, they can attempt authentication again.

## Trusted Header SSO

When Authelia returns a 200 OK for an authorized request, it includes response headers that the reverse proxy can forward to backend applications for SSO:

| Header | Description |
|--------|-------------|
| `Remote-User` | The authenticated username |
| `Remote-Email` | The user's email address |
| `Remote-Name` | The user's display name |
| `Remote-Groups` | Comma-separated list of group memberships |

Configure the proxy to trust and forward these headers to backend applications. Applications that support trusted header authentication (e.g., Nextcloud, Gitea, Home Assistant) can use these headers for automatic login without separate credentials.

**Security**: Only enable trusted header SSO when the proxy is configured to strip these headers from incoming client requests. Otherwise, users could spoof their own identity by sending forged headers. See the Forwarded Headers documentation for hardening guidance.

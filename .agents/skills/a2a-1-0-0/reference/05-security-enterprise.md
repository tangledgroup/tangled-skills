# Security & Enterprise Features

## Transport Security

- Production deployments MUST use encrypted communication (HTTPS for HTTP-based bindings, TLS for gRPC)
- Implementations SHOULD use modern TLS configurations (TLS 1.3+ recommended)
- Agents SHOULD enforce HSTS headers when using HTTP-based bindings
- Implementations SHOULD disable deprecated SSL/TLS versions (SSLv3, TLS 1.0, TLS 1.1)
- Clients SHOULD verify the server's TLS certificate against trusted CAs during handshake

## Authentication

A2A delegates authentication to standard web mechanisms. Identity is handled at the transport/HTTP layer, not within A2A payloads.

### Process

1. **Discovery:** Client discovers server's authentication requirements via `securitySchemes` in Agent Card
2. **Credential Acquisition (Out-of-Band):** Client obtains credentials through processes external to A2A (OAuth flows, secure key distribution)
3. **Credential Transmission:** Client includes credentials in protocol-appropriate headers (e.g., `Authorization: Bearer <TOKEN>`)

### Server Responsibilities

- MUST authenticate every incoming request based on provided credentials
- SHOULD use binding-specific error codes for authentication challenges
- SHOULD provide relevant authentication challenge information with error responses
- Return HTTP 401 for missing/invalid credentials (with WWW-Authenticate header)
- Return HTTP 403 for valid credentials but insufficient permissions

### Supported Authentication Schemes

Agent Card declares schemes using OpenAPI-compatible structures:

- **HTTP Authentication:** Bearer, Basic, and other standard HTTP auth schemes
- **API Key:** API key in header, query parameter, or cookie
- **OAuth 2.0:** Authorization Code, Client Credentials, Device Code flows
- **OpenID Connect:** References OIDC discovery document URL
- **Mutual TLS (mTLS):** Client certificate authentication

### In-Task Authorization

Agents may need additional credentials during task execution (e.g., OAuth token for an API call). A2A provides `TASK_STATE_AUTH_REQUIRED` for this:

**Agent responsibilities:**
1. MUST use a Task to track the operation
2. MUST transition TaskState to `TASK_STATE_AUTH_REQUIRED`
3. MUST include a status message explaining required authorization (unless negotiated out-of-band)

**Client responsibilities:**
1. Upon receiving AUTH_REQUIRED, take action to resolve the authorization
2. May send response message to negotiate, correct, or reject
3. May contact another service to fulfill authorization
4. SHOULD subscribe to task stream or register webhook to avoid missing updates

**Security considerations for in-task auth:**
- Credentials SHOULD be received out-of-band via secure channel (HTTPS)
- In-band credential exchange may be negotiated via extensions
- Credentials SHOULD be bound to the originating agent
- Sensitive credentials SHOULD be encrypted

## Authorization

Once authenticated, the server authorizes requests based on identity and policies.

### Principles

- Servers MUST implement authorization checks on every A2A operation request
- Implementations MUST scope results to caller's authorized access boundaries
- Even without filter parameters, implementations MUST scope to authorized boundaries
- Authorization models are agent-defined (user-based, role-based, project-based, multi-tenant, custom)

### Operations Requiring Scope Limitation

- **ListTasks:** MUST only return tasks visible to the authenticated client
- **GetTask:** MUST verify client has access to the requested task
- **Task operations** (Cancel, Subscribe, Push Notification Config): MUST verify appropriate access rights

### Authorization Models

Agents may base authorization on:
- User identity (user-based)
- Organizational roles/groups (role-based)
- Project/workspace membership (project-based)
- Tenant boundaries (multi-tenant)
- Custom domain-specific logic

## Agent Card Signing

Agent Cards MAY be digitally signed using JSON Web Signature (JWS, RFC 7515).

### Canonicalization

Before signing, the Agent Card MUST be canonicalized using JSON Canonicalization Scheme (JCS, RFC 8785):

1. Respect Protocol Buffer field presence semantics
2. Omit optional fields not explicitly set
3. Include optional fields explicitly set to defaults
4. Always include REQUIRED fields
5. Apply RFC 8785 rules (lexicographic key ordering, consistent number/string representation)
6. Exclude the `signatures` field itself

### Signature Format

Uses JWS with three fields:
- `protected` (required): Base64url-encoded JWS Protected Header
- `signature` (required): Base64url-encoded signature value
- `header` (optional): Unprotected header as JSON object

Protected header MUST include:
- `alg`: Signing algorithm (e.g., "ES256", "RS256")
- `typ`: SHOULD be "JOSE"
- `kid`: Key ID for identifying the signing key

MAY include:
- `jku`: URL to JWKS containing the public key

### Verification Process

1. Extract signature from `signatures` array
2. Retrieve public key using `kid` and `jku` (or trusted key store)
3. Remove default values from received Agent Card
4. Exclude `signatures` field
5. Canonicalize using RFC 8785
6. Verify signature against canonicalized payload

Clients SHOULD verify at least one signature before trusting an Agent Card. Expired or revoked keys MUST NOT be used.

## Extended Agent Card

Agents MAY provide additional capabilities to authenticated clients via the GetExtendedAgentCard operation.

### Requirements

- Operation MUST require authentication using schemes declared in public Agent Card
- Agents MAY return different content based on client identity/authorization level
- Extended cards MAY include additional skills, rate limits, quotas, or organization-specific configuration
- Extended cards SHOULD NOT include sensitive exploitable information
- Clients SHOULD replace cached public Agent Card with extended version for session duration
- Available only if `capabilities.extendedAgentCard: true`

## Input Validation

- Agents MUST validate all input parameters before processing
- Agents SHOULD implement limits on message sizes, file sizes, and request complexity
- Agents SHOULD sanitize or validate file content types and reject unexpected media types

## Credential Management

- API keys, tokens, and credentials MUST be treated as secrets
- Credentials SHOULD be rotated periodically
- Credentials SHOULD be transmitted only over encrypted connections
- Agents SHOULD implement credential revocation mechanisms
- Agents SHOULD log authentication failures and implement rate limiting against brute-force

## Audit and Monitoring

- Agents SHOULD log security-relevant events (auth failures, authorization denials, suspicious requests)
- Agents SHOULD monitor for unusual patterns (rapid task creation, excessive cancellations)
- Agents SHOULD provide audit trails for sensitive operations
- Logs MUST NOT include sensitive information (credentials, personal data) unless required and protected

## Rate Limiting

- Agents SHOULD implement rate limiting on all operations
- Agents SHOULD return appropriate error responses when limits are exceeded
- Agents MAY implement different rate limits for different operations or user tiers

## Data Privacy

- Agents MUST comply with applicable data protection regulations (GDPR, CCPA, HIPAA)
- Agents SHOULD provide mechanisms for users to request data deletion
- Agents SHOULD implement appropriate data retention policies
- Agents SHOULD minimize logging of sensitive or personal information

## Observability and Tracing

- Clients and Servers SHOULD participate in distributed tracing systems
- Use OpenTelemetry to propagate trace context via W3C Trace Context headers
- Log details including taskId, sessionId, correlation IDs, and trace context
- Expose key operational metrics (request rates, error rates, latency, resource utilization)
- Audit significant events (task creation, critical state changes, sensitive operations)

## API Management

For externally exposed A2A servers:
- Centralized policy enforcement (authentication, authorization, rate limiting, quotas)
- Traffic management (load balancing, routing, mediation)
- Analytics and reporting (usage insights, performance trends)
- Developer portals for agent discovery and onboarding

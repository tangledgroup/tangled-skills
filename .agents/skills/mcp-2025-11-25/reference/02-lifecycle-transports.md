# Lifecycle and Transports

## Connection Lifecycle

MCP defines a rigorous lifecycle for client-server connections ensuring proper capability negotiation and state management.

### Phases

1. **Initialization**: Capability negotiation and protocol version agreement
2. **Operation**: Normal protocol communication
3. **Shutdown**: Graceful termination of the connection

### Initialization

The initialization phase MUST be the first interaction between client and server. During this phase, the client and server:

- Establish protocol version compatibility
- Exchange and negotiate capabilities
- Share implementation details

The client MUST initiate by sending an `initialize` request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {
      "roots": { "listChanged": true },
      "sampling": {},
      "elicitation": { "form": {}, "url": {} },
      "tasks": {
        "requests": {
          "elicitation": { "create": {} },
          "sampling": { "createMessage": {} }
        }
      }
    },
    "clientInfo": {
      "name": "ExampleClient",
      "title": "Example Client Display Name",
      "version": "1.0.0",
      "description": "An example MCP client application",
      "icons": [
        {
          "src": "https://example.com/icon.png",
          "mimeType": "image/png",
          "sizes": ["48x48"]
        }
      ],
      "websiteUrl": "https://example.com"
    }
  }
}
```

The server responds with its own capabilities and information:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-11-25",
    "capabilities": {
      "logging": {},
      "prompts": { "listChanged": true },
      "resources": { "subscribe": true, "listChanged": true },
      "tools": { "listChanged": true },
      "tasks": {
        "list": {},
        "cancel": {},
        "requests": {
          "tools": { "call": {} }
        }
      }
    },
    "serverInfo": {
      "name": "ExampleServer",
      "title": "Example Server Display Name",
      "version": "1.0.0",
      "description": "An example MCP server",
      "icons": [
        {
          "src": "https://example.com/server-icon.svg",
          "mimeType": "image/svg+xml",
          "sizes": ["any"]
        }
      ],
      "websiteUrl": "https://example.com/server"
    },
    "instructions": "Optional instructions for the client"
  }
}
```

After successful initialization, the client MUST send an `initialized` notification:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

- The client SHOULD NOT send requests other than pings before the server responds to `initialize`
- The server SHOULD NOT send requests other than pings and logging before receiving `initialized`

### Version Negotiation

In the `initialize` request, the client MUST send a protocol version it supports. This SHOULD be the *latest* version supported by the client. If the server supports the requested version, it MUST respond with the same version. Otherwise, it MUST respond with another version it supports (SHOULD be its latest). If the client does not support the server's response version, it SHOULD disconnect.

### Capability Negotiation

Key capabilities:

- **Client**: `roots`, `sampling`, `elicitation`, `tasks`, `experimental`
- **Server**: `prompts`, `resources`, `tools`, `logging`, `completions`, `tasks`, `experimental`

Capability objects can describe sub-capabilities like `listChanged` (list change notifications) and `subscribe` (individual item subscriptions, resources only).

### Operation

During the operation phase, both parties MUST respect the negotiated protocol version and only use capabilities that were successfully negotiated.

### Shutdown

No specific shutdown messages are defined. The underlying transport mechanism signals connection termination:

- **stdio**: Client closes input stream to server, waits for exit, sends SIGTERM if needed, then SIGKILL. Server MAY initiate by closing output and exiting.
- **HTTP**: Close the associated HTTP connection(s).

### Timeouts

Implementations SHOULD establish timeouts for all sent requests. When no response arrives within the timeout, the sender SHOULD issue a cancellation notification. SDKs SHOULD allow per-request timeout configuration. Implementations MAY reset the timeout clock on progress notifications but SHOULD always enforce a maximum timeout.

Example initialization error:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Unsupported protocol version",
    "data": {
      "supported": ["2024-11-05"],
      "requested": "1.0.0"
    }
  }
}
```

## Transports

MCP uses JSON-RPC to encode messages. Messages MUST be UTF-8 encoded. Two standard transports are defined:

### stdio

In the stdio transport:

- The client launches the MCP server as a subprocess
- Server reads JSON-RPC from stdin, writes to stdout
- Messages are delimited by newlines, MUST NOT contain embedded newlines
- Server MAY write UTF-8 strings to stderr for any logging (info, debug, error)
- Client MAY capture, forward, or ignore stderr; SHOULD NOT assume stderr indicates errors
- Server MUST NOT write anything to stdout that is not a valid MCP message
- Client MUST NOT write anything to stdin that is not a valid MCP message

### Streamable HTTP

The server operates as an independent process handling multiple client connections via HTTP POST and GET. The server provides a single HTTP endpoint (the **MCP endpoint**) supporting both POST and GET.

**Security Warning**: Servers MUST validate the `Origin` header on all incoming connections to prevent DNS rebinding attacks. Respond with HTTP 403 if the Origin is invalid. When running locally, bind only to localhost. Implement proper authentication.

#### Sending Messages to the Server

Every JSON-RPC message from the client MUST be a new HTTP POST to the MCP endpoint:

- Client MUST include `Accept` header listing both `application/json` and `text/event-stream`
- Body MUST be a single JSON-RPC request, notification, or response
- For responses/notifications: server returns 202 Accepted with no body on success
- For requests: server returns either `Content-Type: text/event-stream` (SSE) or `Content-Type: application/json`
- SSE streams SHOULD include an event ID to prime client reconnection
- Server MAY close the connection (without terminating the stream) and client SHOULD reconnect
- Server SHOULD send a `retry` field before closing for resumability

#### Listening for Messages from the Server

- Client MAY issue HTTP GET to open an SSE stream for server-to-client communication
- Server MUST return `Content-Type: text/event-stream` or HTTP 405 Method Not Allowed
- Server MAY send JSON-RPC requests and notifications on the stream
- Server MUST NOT send responses on the stream unless resuming a previous request

#### Multiple Connections

- Client MAY remain connected to multiple SSE streams simultaneously
- Server MUST send each message on only one stream (no broadcasting)

#### Resumability and Redelivery

- Servers MAY attach `id` fields to SSE events (globally unique within the session)
- Client SHOULD include `Last-Event-ID` header when resuming via HTTP GET
- Server MAY replay messages that would have been sent after the last event ID on the correct stream
- Resumption is always via HTTP GET with `Last-Event-ID`

#### Session Management

- Server MAY assign a session ID via `MCP-Session-Id` header on the InitializeResult response
- Session ID SHOULD be globally unique and cryptographically secure
- Session ID MUST only contain visible ASCII characters (0x21 to 0x7E)
- Client MUST include `MCP-Session-Id` on all subsequent requests
- Server MAY terminate sessions, responding with HTTP 404 to expired session IDs
- Client receiving 404 MUST start a new session with InitializeRequest
- Client SHOULD send HTTP DELETE to explicitly terminate sessions

#### Protocol Version Header

Client MUST include `MCP-Protocol-Version: <protocol-version>` on all HTTP requests (e.g., `MCP-Protocol-Version: 2025-11-25`). If the server receives an invalid or unsupported version, it MUST respond with 400 Bad Request.

#### Backwards Compatibility

For the deprecated HTTP+SSE transport (version 2024-11-05):

- Servers should continue hosting old SSE and POST endpoints alongside the new MCP endpoint
- Clients should attempt POST first; if 400/404/405, try GET to detect old transport

### Custom Transports

Clients and servers MAY implement additional custom transport mechanisms. They MUST preserve JSON-RPC message format and lifecycle requirements.

## Authorization

Authorization is OPTIONAL for MCP implementations. When supported, HTTP-based transports SHOULD conform to the OAuth 2.1 based authorization specification. STDIO transports SHOULD NOT follow this specification and instead retrieve credentials from the environment.

### Standards Compliance

Based on:

- OAuth 2.1 (draft-ietf-oauth-v2-1-13)
- OAuth 2.0 Authorization Server Metadata (RFC8414)
- OAuth 2.0 Dynamic Client Registration (RFC7591)
- OAuth 2.0 Protected Resource Metadata (RFC9728)
- OAuth Client ID Metadata Documents

### Roles

- **MCP server**: Acts as OAuth 2.1 resource server
- **MCP client**: Acts as OAuth 2.1 client
- **Authorization server**: Issues access tokens

### Authorization Server Discovery

MCP servers MUST implement OAuth 2.0 Protected Resource Metadata (RFC9728) to indicate authorization server locations. The metadata document MUST include the `authorization_servers` field.

Discovery mechanisms:

1. **WWW-Authenticate Header**: Include resource metadata URL in 401 responses
2. **Well-Known URI**: Serve at `.well-known/oauth-protected-resource` path

MCP clients MUST support both discovery mechanisms, using WWW-Authenticate when present, falling back to well-known URIs.

### Client Registration Approaches

Priority order:

1. Pre-registered client information if available
2. Client ID Metadata Documents (if server supports `client_id_metadata_document_supported`)
3. Dynamic Client Registration as fallback
4. Prompt user for client information

### Scope Selection Strategy

1. Use `scope` parameter from initial WWW-Authenticate 401 response if provided
2. If not available, use all scopes from `scopes_supported` in Protected Resource Metadata

### Resource Parameter

MCP clients MUST implement RFC 8707 Resource Indicators. The `resource` parameter:

- MUST be included in authorization and token requests
- MUST identify the MCP server (canonical URI)
- Examples: `https://mcp.example.com/mcp`, `https://mcp.example.com`

### Access Token Usage

- Client MUST use `Authorization: Bearer <access-token>` header on every request
- Tokens MUST NOT be included in URI query strings
- Server MUST validate tokens were issued specifically for itself as intended audience
- Invalid/expired tokens receive HTTP 401

### PKCE Requirements

MCP clients MUST implement PKCE per OAuth 2.1 Section 7.5.2 and MUST use `S256` code challenge method. Clients MUST verify PKCE support via authorization server metadata before proceeding.

### Token Audience Validation

- MCP servers MUST validate tokens were specifically issued for their use
- MCP servers MUST NOT pass through tokens to upstream APIs
- If the server makes requests to upstream APIs, it uses a separate token from the upstream authorization server

### Error Handling

| Status Code | Description |
|-------------|-------------|
| 401 | Authorization required or token invalid |
| 403 | Invalid scopes or insufficient permissions |
| 400 | Malformed authorization request |

For insufficient scope errors at runtime, servers SHOULD respond with HTTP 403 and WWW-Authenticate header including `error="insufficient_scope"` and the required scopes.

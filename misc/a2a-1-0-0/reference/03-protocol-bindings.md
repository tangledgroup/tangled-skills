# Protocol Bindings

A2A provides three standard protocol bindings. All must provide identical functionality, consistent behavior, equivalent authentication, and mapped error handling.

## Method Mapping Reference

| Operation | JSON-RPC Method | gRPC Method | REST Endpoint |
|---|---|---|---|
| Send message | `SendMessage` | `SendMessage` | `POST /message:send` |
| Send streaming message | `SendStreamingMessage` | `SendStreamingMessage` | `POST /message:stream` |
| Get task | `GetTask` | `GetTask` | `GET /tasks/{id}` |
| List tasks | `ListTasks` | `ListTasks` | `GET /tasks` |
| Cancel task | `CancelTask` | `CancelTask` | `POST /tasks/{id}:cancel` |
| Subscribe to task | `SubscribeToTask` | `SubscribeToTask` | `POST /tasks/{id}:subscribe` |
| Create push notification config | `CreateTaskPushNotificationConfig` | `CreateTaskPushNotificationConfig` | `POST /tasks/{id}/pushNotificationConfigs` |
| Get push notification config | `GetTaskPushNotificationConfig` | `GetTaskPushNotificationConfig` | `GET /tasks/{id}/pushNotificationConfigs/{configId}` |
| List push notification configs | `ListTaskPushNotificationConfigs` | `ListTaskPushNotificationConfigs` | `GET /tasks/{id}/pushNotificationConfigs` |
| Delete push notification config | `DeleteTaskPushNotificationConfig` | `DeleteTaskPushNotificationConfig` | `DELETE /tasks/{id}/pushNotificationConfigs/{configId}` |
| Get extended Agent Card | `GetExtendedAgentCard` | `GetExtendedAgentCard` | `GET /extendedAgentCard` |

## 1. JSON-RPC 2.0 Binding

### Requirements

- Protocol: JSON-RPC 2.0 over HTTP(S)
- Content-Type: `application/json`
- Method naming: PascalCase (e.g., `SendMessage`, `GetTask`)
- Streaming: Server-Sent Events (`text/event-stream`)

### Base Request Structure

```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "method": "MethodName",
  "params": { /* method-specific parameters */ }
}
```

### Service Parameters

Transmitted as HTTP headers:

```http
POST /rpc HTTP/1.1
Host: agent.example.com
Content-Type: application/json
Authorization: Bearer token
A2A-Version: 1.0
A2A-Extensions: https://example.com/extensions/geolocation/v1
```

### Core Methods

**SendMessage:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "SendMessage",
  "params": {
    "message": {
      "role": "ROLE_USER",
      "parts": [{"text": "What is the weather?"}],
      "messageId": "msg-uuid"
    }
  }
}
```

Response contains either `task` or `message` in the result.

**SendStreamingMessage:**

Same request as SendMessage. Response is HTTP 200 with `Content-Type: text/event-stream`:

```
data: {"jsonrpc": "2.0", "id": 1, "result": {"task": {...}}}

data: {"jsonrpc": "2.0", "id": 1, "result": {"statusUpdate": {...}}}
```

**GetTask:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "GetTask",
  "params": {
    "id": "task-uuid",
    "historyLength": 10
  }
}
```

**ListTasks:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "ListTasks",
  "params": {
    "contextId": "context-uuid",
    "status": "TASK_STATE_WORKING",
    "pageSize": 50,
    "pageToken": "cursor-token"
  }
}
```

**CancelTask:**

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "CancelTask",
  "params": {"id": "task-uuid"}
}
```

**SubscribeToTask:**

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "SubscribeToTask",
  "params": {"id": "task-uuid"}
}
```

Returns SSE stream. Returns `UnsupportedOperationError` for terminal tasks.

### Error Handling

Uses standard JSON-RPC 2.0 error structure:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32001,
    "message": "Task not found",
    "data": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "TASK_NOT_FOUND",
        "domain": "a2a-protocol.org",
        "metadata": {"taskId": "nonexistent-id"}
      }
    ]
  }
}
```

Standard JSON-RPC codes: `-32700` (parse), `-32600` (invalid request), `-32601` (method not found), `-32602` (invalid params), `-32603` (internal).

A2A-specific codes: `-32001` to `-32009` (see Error Code Mappings below).

## 2. gRPC Binding

### Requirements

- Protocol: gRPC over HTTP/2 with TLS
- Definition: Normative `a2a.proto` (Protocol Buffers v3)
- Service: Implement the `A2AService` gRPC service
- Serialization: Protocol Buffers

### Service Parameters

Transmitted as gRPC metadata (headers):

```go
md := metadata.Pairs(
    "authorization", "Bearer token",
    "a2a-version", "1.0",
    "a2a-extensions", "https://example.com/extensions/geolocation/v1",
)
ctx := metadata.NewOutgoingContext(context.Background(), md)
```

Metadata keys are case-insensitive and normalized to lowercase by gRPC.

### Streaming

Uses server streaming RPCs. `StreamResponse` message provides a oneof union of possible events: `task`, `message`, `statusUpdate`, `artifactUpdate`.

### Error Handling

Uses standard gRPC status with `google.rpc.Status`:

```proto
status {
  code: NOT_FOUND
  message: "Task with ID 'task-123' not found"
  details: [
    {
      type: "type.googleapis.com/google.rpc.ErrorInfo"
      reason: "TASK_NOT_FOUND"
      domain: "a2a-protocol.org"
      metadata: {
        task_id: "task-123"
        timestamp: "2025-11-09T10:30:00Z"
      }
    }
  ]
}
```

A2A-specific errors use `google.rpc.ErrorInfo` with reason in UPPER_SNAKE_CASE without "Error" suffix (e.g., `TASK_NOT_FOUND`).

## 3. HTTP+JSON/REST Binding

### Requirements

- Protocol: HTTP(S) with JSON payloads
- Content-Type: `application/a2a+json` (SHOULD be used)
- Methods: Standard HTTP verbs (GET, POST, DELETE)
- URL patterns: RESTful resource-based URLs
- Streaming: Server-Sent Events for real-time updates

### URL Patterns

**Message Operations:**
- `POST /message:send` — Send message
- `POST /message:stream` — Send message with streaming (SSE response)

**Task Operations:**
- `GET /tasks/{id}` — Get task status
- `GET /tasks` — List tasks (with query parameters)
- `POST /tasks/{id}:cancel` — Cancel task
- `POST /tasks/{id}:subscribe` — Subscribe to task updates (SSE)

**Push Notification Configuration:**
- `POST /tasks/{id}/pushNotificationConfigs` — Create
- `GET /tasks/{id}/pushNotificationConfigs/{configId}` — Get
- `GET /tasks/{id}/pushNotificationConfigs` — List
- `DELETE /tasks/{id}/pushNotificationConfigs/{configId}` — Delete

**Agent Card:**
- `GET /extendedAgentCard` — Get authenticated extended Agent Card

### Query Parameters

For GET/DELETE methods, request parameters use camelCase query parameters:

```http
GET /tasks?contextId=uuid&status=TASK_STATE_WORKING&pageSize=50&pageToken=cursor
GET /tasks/{id}?historyLength=10
```

Boolean values as lowercase strings (`true`, `false`). Enums as string values. Multiple values by repeating parameter name or comma-separated.

### Streaming (SSE)

```http
POST /message:stream
Content-Type: application/a2a+json

{ /* SendMessageRequest */ }
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream

data: { /* StreamResponse: task object */ }

data: { /* StreamResponse: statusUpdate or artifactUpdate */ }
```

### Error Handling

HTTP errors use `google.rpc.Status` JSON representation:

```http
HTTP/1.1 404 Not Found
Content-Type: application/a2a+json

{
  "error": {
    "code": 404,
    "status": "NOT_FOUND",
    "message": "The specified task ID does not exist or is not accessible",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "TASK_NOT_FOUND",
        "domain": "a2a-protocol.org",
        "metadata": {
          "taskId": "task-123",
          "timestamp": "2025-11-09T10:30:00.000Z"
        }
      }
    ]
  }
}
```

## Error Code Mappings

| A2A Error Type | JSON-RPC Code | gRPC Status | HTTP Status |
|---|---|---|---|
| TaskNotFoundError | -32001 | NOT_FOUND | 404 |
| TaskNotCancelableError | -32002 | FAILED_PRECONDITION | 400 |
| PushNotificationNotSupportedError | -32003 | FAILED_PRECONDITION | 400 |
| UnsupportedOperationError | -32004 | FAILED_PRECONDITION | 400 |
| ContentTypeNotSupportedError | -32005 | INVALID_ARGUMENT | 400 |
| InvalidAgentResponseError | -32006 | INTERNAL | 500 |
| ExtendedAgentCardNotConfiguredError | -32007 | FAILED_PRECONDITION | 400 |
| ExtensionSupportRequiredError | -32008 | FAILED_PRECONDITION | 400 |
| VersionNotSupportedError | -32009 | FAILED_PRECONDITION | 400 |

## Version Negotiation

Clients MUST send the `A2A-Version` header (or request parameter) with each request. Format is `Major.Minor` (e.g., `1.0`). Patch versions do not affect protocol compatibility and should not be used in requests.

- Empty value is interpreted as version 0.3
- If version is not supported, agent returns `VersionNotSupportedError`
- Agents can expose multiple interfaces with different versions under same or different URLs

## Protocol Selection

Clients MUST follow these rules when selecting a protocol:

1. Parse `supportedInterfaces` if present, and select the first supported transport
2. Prefer earlier entries in the ordered list when multiple options are supported
3. Use the correct URL for the selected transport

The first entry in `supportedInterfaces` represents the agent's preferred interface.

## Custom Bindings

Implementers MAY create custom protocol bindings (e.g., WebSocket, MQTT). Requirements:

1. Implement all core operations
2. Preserve data model equivalence
3. Maintain operation semantics
4. Document completely
5. Identify binding by URI in Agent Card's `supportedInterfaces`
6. Define error code mappings
7. Specify service parameter transmission mechanism
8. Document streaming support (if any)

**Key areas to specify for custom bindings:**

- **Data Type Mappings:** How each Protocol Buffer type is represented (binary encoding, enum representation, timestamp format)
- **Service Parameters:** Mechanism for carrying key-value context (headers, metadata fields), encoding/size constraints
- **Error Mapping:** Mapping table equivalent to the standard error code mappings
- **Streaming:** Stream mechanism, ordering guarantees, reconnection behavior, termination signaling
- **Authentication:** How credentials are transmitted over the custom transport

Example custom binding declaration:

```json
{
  "supportedInterfaces": [
    {
      "url": "wss://agent.example.com/a2a/websocket",
      "protocolBinding": "https://a2a-protocol.org/bindings/websocket",
      "protocolVersion": "1.0"
    }
  ]
}
```

Custom protocol bindings are a complementary but distinct concept to Extensions. Extensions modify the behavior of protocol interactions on top of an existing transport. Custom protocol bindings change the transport layer itself.

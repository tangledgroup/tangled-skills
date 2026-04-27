# Streaming & Asynchronous Operations

A2A provides three complementary mechanisms for task update delivery: polling, streaming (SSE), and push notifications (webhooks).

## Overview of Update Mechanisms

### Polling (GetTask)

- Client periodically calls GetTask to check task status
- Simple to implement, works with all protocol bindings
- Higher latency, potential for unnecessary requests
- Best for: Simple integrations, infrequent updates, clients behind restrictive firewalls

### Streaming (SSE)

- Real-time delivery of events as they occur
- Operations: SendStreamingMessage and SubscribeToTask
- Low latency, efficient for frequent updates
- Requires persistent connection support
- Best for: Interactive applications, real-time dashboards, live progress monitoring
- Requires `capabilities.streaming: true` in Agent Card

### Push Notifications (Webhooks)

- Agent sends HTTP POST to client-registered endpoints on state changes
- Client does not maintain persistent connection
- Asynchronous delivery, client must be reachable via HTTP
- Best for: Server-to-server integrations, long-running tasks, event-driven architectures
- Operations: Create/Get/List/Delete push notification configs
- Requires `capabilities.pushNotifications: true` in Agent Card
- Webhook calls always use plain HTTP with JSON payloads regardless of the agent's primary binding

## Streaming with SSE

### Initiation

Client uses `SendStreamingMessage` (or `POST /message:stream`) to send an initial message and subscribe to updates simultaneously.

### Stream Patterns

The stream MUST follow one of these patterns:

1. **Message-only stream:** If the agent returns a Message, the stream contains exactly one Message object and closes immediately. No task tracking or updates.

2. **Task lifecycle stream:** If the agent returns a Task, the stream begins with the Task object, followed by zero or more TaskStatusUpdateEvent or TaskArtifactUpdateEvent objects. The stream closes when the task reaches a terminal state (completed, failed, canceled, rejected) or an interrupted state (input-required, auth-required).

### Event Structure

Each SSE event's `data` field contains a StreamResponse:

```
data: {"task": {"id": "task-uuid", "status": {"state": "TASK_STATE_WORKING"}}}

data: {"artifactUpdate": {"taskId": "task-uuid", "artifact": {"parts": [{"text": "# Report\n\n"}]}}}

data: {"statusUpdate": {"taskId": "task-uuid", "status": {"state": "TASK_STATE_COMPLETED"}}}
```

### Event Ordering

Events MUST be delivered in the order they were generated. Events MUST NOT be reordered during transmission, regardless of protocol binding.

### Multiple Streams Per Task

An agent MAY serve multiple concurrent streams to one or more clients for the same task:

- Events are broadcast to all active streams
- Each stream receives the same events in the same order
- Closing one stream does not affect other active streams
- The task lifecycle is independent of any individual stream's lifecycle

### SubscribeToTask

Establishes a streaming connection to receive updates for an existing task:

- Returns Task object as the first event (current state at subscription time)
- Followed by status and artifact update events
- Stream terminates when task reaches terminal or interrupted state
- Returns `UnsupportedOperationError` for tasks already in terminal states

### Reconnection

If a client's SSE connection breaks while a task is still active, the client can reconnect using SubscribeToTask. The reconnected stream starts with the current Task state, preventing loss of information.

## Push Notifications

### Configuration

Client provides a PushNotificationConfig to the server either:
- Within the initial SendMessage request (via `configuration.pushNotificationConfig`)
- Separately via CreateTaskPushNotificationConfig for an existing task

```json
{
  "url": "https://client.example.com/webhook/a2a-notifications",
  "token": "secure-client-token-for-task-aaa",
  "authentication": {
    "schemes": ["Bearer"]
  }
}
```

### Notification Lifecycle

1. Client registers webhook URL in PushNotificationConfig
2. Agent processes task asynchronously
3. On significant state changes (terminal state, input-required, auth-required), agent sends HTTP POST to the webhook URL
4. Payload is a StreamResponse (same format as streaming events)
5. Client responds with HTTP 2xx to acknowledge receipt
6. Configuration persists until task completion or explicit deletion

### Notification Payload

```http
POST /webhook/a2a-notifications HTTP/1.1
Host: client.example.com
Authorization: Bearer server-generated-jwt
Content-Type: application/a2a+json
X-A2A-Notification-Token: secure-client-token-for-task-aaa

{
  "statusUpdate": {
    "taskId": "43667960-d455-4453-b0cf-1bae4955270d",
    "contextId": "c295ea44-7543-4f78-b524-7a38915ad6e4",
    "status": {
      "state": "TASK_STATE_COMPLETED",
      "timestamp": "2024-03-15T18:30:00Z"
    }
  }
}
```

### Client-Side Push Notification Service

The `url` in `PushNotificationConfig.url` points to a client-side Push Notification Service responsible for receiving HTTP POST notifications from the A2A Server. Its responsibilities include authenticating the incoming notification, validating its relevance, and relaying the notification or its content to the appropriate client application logic.

### Server Guarantees

- Agents MUST attempt delivery at least once for each configured webhook
- Agents MAY implement retry logic with exponential backoff for failed deliveries
- Agents SHOULD include reasonable timeout for webhook requests (recommended: 10-30 seconds)
- Agents MAY stop attempting delivery after configured consecutive failures

### Client Responsibilities

- Respond with HTTP 2xx status codes to acknowledge successful receipt
- Process notifications idempotently (duplicate deliveries may occur)
- Validate task ID matches an expected task
- Implement security measures to verify notification source

### Push Notification CRUD Operations

- **Create:** CreateTaskPushNotificationConfig / `POST /tasks/{id}/pushNotificationConfigs`
- **Get:** GetTaskPushNotificationConfig / `GET /tasks/{id}/pushNotificationConfigs/{configId}`
- **List:** ListTaskPushNotificationConfigs / `GET /tasks/{id}/pushNotificationConfigs`
- **Delete:** DeleteTaskPushNotificationConfig / `DELETE /tasks/{id}/pushNotificationConfigs/{configId}`

Delete is idempotent — multiple deletions of the same config have the same effect.

### Security Considerations

**Agent (Webhook Caller):**
- MUST include authentication credentials as specified in PushNotificationConfig.authentication
- SHOULD validate webhook URLs to prevent SSRF attacks:
  - Reject private IP ranges (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
  - Reject localhost and link-local addresses
  - Implement URL allowlists where appropriate

**Client (Webhook Receiver):**
- MUST validate webhook authenticity using provided authentication credentials
- SHOULD verify task ID matches an expected task
- SHOULD implement rate limiting to prevent webhook flooding
- SHOULD use HTTPS endpoints for webhook URLs
- Should reject notifications that are too old (timestamp validation)
- Should use unique identifiers (e.g., JWT `jti` claim) to prevent replay attacks

### Example Asymmetric Key Flow (JWT + JWKS)

1. Client creates PushNotificationConfig with `authentication.scheme: "Bearer"`
2. Agent generates JWT signed with its private key, including claims (iss, aud, iat, exp, jti, taskId)
3. Agent makes public keys available via JWKS endpoint
4. Client webhook extracts JWT, inspects kid, fetches public key from JWKS
5. Client verifies JWT signature and validates claims (iss, aud, iat, exp, jti)
6. Client checks PushNotificationConfig.token if provided

## Execution Mode

The `return_immediately` field in SendMessageConfiguration controls blocking behavior:

- **Blocking (default):** Operation waits until task reaches terminal or interrupted state before returning
- **Non-blocking (`return_immediately: true`):** Returns immediately after creating the task with in-progress state

This field has no effect when the operation returns a direct Message, for streaming operations (always real-time), or on push notification configurations.

## Complete Workflow Example

**Long-running task with push notifications:**

```http
POST /message:send HTTP/1.1
Host: agent.example.com
Content-Type: application/a2a+json
Authorization: Bearer token

{
  "message": {
    "role": "ROLE_USER",
    "parts": [{"text": "Generate the Q1 sales report"}],
    "messageId": "msg-001"
  },
  "configuration": {
    "pushNotificationConfig": {
      "url": "https://client.example.com/webhook/a2a-notifications",
      "token": "secure-token",
      "authentication": {"schemes": ["Bearer"]}
    }
  }
}
```

Response (task submitted):

```json
{
  "task": {
    "id": "task-001",
    "contextId": "ctx-001",
    "status": {
      "state": "TASK_STATE_SUBMITTED",
      "timestamp": "2024-03-15T11:00:00Z"
    }
  }
}
```

Later, server POSTs to webhook when task completes. Client then calls GetTask to retrieve full task with artifacts.

# Base Utilities

## Cancellation

MCP supports optional cancellation of in-progress requests through notification messages. Either side can send a cancellation notification to indicate that a previously-issued request should be terminated.

### Cancellation Flow

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/cancelled",
  "params": {
    "requestId": "123",
    "reason": "User requested cancellation"
  }
}
```

The notification contains the ID of the request to cancel and an optional reason string.

### Behavior Requirements

- Cancellation notifications MUST only reference requests previously issued in the same direction that are believed still in-progress
- The `initialize` request MUST NOT be cancelled by clients
- For task-augmented requests, the `tasks/cancel` request MUST be used instead
- Receivers SHOULD stop processing and free resources
- Receivers MAY ignore cancellations if the request is unknown, already completed, or cannot be cancelled
- Senders SHOULD ignore any response arriving after cancellation

### Timing Considerations

Due to network latency, cancellation notifications may arrive after processing has completed. Both parties MUST handle these race conditions gracefully.

## Ping

The ping mechanism allows either party to verify their counterpart is still responsive.

### Message Format

```json
{
  "jsonrpc": "2.0",
  "id": "123",
  "method": "ping"
}
```

The receiver MUST respond promptly with an empty response:

```json
{
  "jsonrpc": "2.0",
  "id": "123",
  "result": {}
}
```

If no response is received within a reasonable timeout, the sender MAY consider the connection stale and terminate it.

### Implementation Considerations

- Implementations SHOULD periodically issue pings to detect connection health
- Ping frequency SHOULD be configurable
- Timeouts SHOULD be appropriate for the network environment
- Excessive pinging SHOULD be avoided

## Progress Tracking

MCP supports optional progress tracking for long-running operations through notification messages.

### Progress Flow

When a party wants to receive progress updates, it includes a `progressToken` in the request metadata:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "some_method",
  "params": {
    "_meta": {
      "progressToken": "abc123"
    }
  }
}
```

The receiver MAY send progress notifications:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/progress",
  "params": {
    "progressToken": "abc123",
    "progress": 50,
    "total": 100,
    "message": "Reticulating splines..."
  }
}
```

- Progress tokens MUST be string or integer, unique across all active requests
- The `progress` value MUST increase with each notification
- `progress` and `total` MAY be floating point
- `message` SHOULD provide relevant human-readable progress information

### Behavior Requirements

- Progress notifications MUST only reference tokens from active requests
- Receivers MAY choose not to send any progress notifications
- For task-augmented requests, the same progressToken remains valid throughout the task's lifetime
- Progress notifications for tasks MUST stop after terminal status

## Tasks (Experimental)

Tasks were introduced in version 2025-11-25 and are currently experimental. They allow requestors to augment requests with durable state machines that carry execution state information, enabling polling and deferred result retrieval.

### Definitions

- **Requestor**: The sender of a task-augmented request (can be client or server)
- **Receiver**: The entity executing the task (can be client or server)

### Capabilities

Servers and clients that support tasks MUST declare a `tasks` capability:

**Server capabilities:**

```json
{
  "capabilities": {
    "tasks": {
      "list": {},
      "cancel": {},
      "requests": {
        "tools": { "call": {} }
      }
    }
  }
}
```

**Client capabilities:**

```json
{
  "capabilities": {
    "tasks": {
      "list": {},
      "cancel": {},
      "requests": {
        "sampling": { "createMessage": {} },
        "elicitation": { "create": {} }
      }
    }
  }
}
```

### Tool-Level Negotiation

Tools declare task support via `execution.taskSupport` in `tools/list` results:

- `"forbidden"` (default): Clients MUST NOT invoke as a task
- `"optional"`: Clients MAY invoke as a task or normal request
- `"required"`: Clients MUST invoke as a task

### Creating Tasks

Task-augmented requests follow a two-phase pattern. The server returns a `CreateTaskResult` immediately; the actual result becomes available later via `tasks/result`.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": { "city": "New York" },
    "task": { "ttl": 60000 }
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "task": {
      "taskId": "786512e2-9e0d-44bd-8f29-789f320fe840",
      "status": "working",
      "statusMessage": "The operation is now in progress.",
      "createdAt": "2025-11-25T10:30:00Z",
      "lastUpdatedAt": "2025-11-25T10:40:00Z",
      "ttl": 60000,
      "pollInterval": 5000
    }
  }
}
```

### Task Operations

**Get task status (`tasks/get`):**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tasks/get",
  "params": {
    "taskId": "786512e2-9e0d-44bd-8f29-789f320fe840"
  }
}
```

**Retrieve result (`tasks/result`):**

Blocks until terminal status. Returns exactly what the underlying request would have returned.

**List tasks (`tasks/list`):** Supports cursor-based pagination.

**Cancel task (`tasks/cancel`):**

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tasks/cancel",
  "params": {
    "taskId": "786512e2-9e0d-44bd-8f29-789f320fe840"
  }
}
```

### Task Status Lifecycle

Tasks transition through these states:

- `working`: Request is being processed
- `input_required`: Receiver needs input from requestor (requestor should call `tasks/result`)
- `completed`: Request completed successfully
- `failed`: Request did not complete successfully
- `cancelled`: Request was cancelled before completion

Valid transitions:

- From `working`: may move to `input_required`, `completed`, `failed`, or `cancelled`
- From `input_required`: may move to `working`, `completed`, `failed`, or `cancelled`
- Terminal states (`completed`, `failed`, `cancelled`) MUST NOT transition

### Task Status Notifications

Receivers MAY send `notifications/tasks/status` when task status changes. Requestors MUST NOT rely on receiving these notifications.

### Related Task Metadata

All requests, responses, and notifications associated with a task MUST include the `io.modelcontextprotocol/related-task` key in `_meta`:

```json
{
  "io.modelcontextprotocol/related-task": {
    "taskId": "786512e2-9e0d-44bd-8f29-789f320fe840"
  }
}
```

### TTL and Resource Management

- Receivers MUST include `createdAt` and `lastUpdatedAt` ISO 8601 timestamps
- Receivers MAY override the requested TTL
- After TTL elapses, receivers MAY delete the task and its results
- Receivers MAY include `pollInterval` to suggest polling frequency

### Error Handling

Protocol errors:

- Invalid/nonexistent taskId: `-32602` (Invalid params)
- Cancel task in terminal status: `-32602` (Invalid params)
- Internal errors: `-32603`
- Non-task-augmented request when required: `-32600`

### Security Considerations

- Task IDs are the primary access mechanism — without proper controls, any party with a task ID could access sensitive information
- When authorization context is provided, receivers MUST bind tasks to that context
- Without context-binding, receivers MUST generate cryptographically secure task IDs and consider shorter TTLs
- Receivers SHOULD implement rate limiting on task operations
- Receivers SHOULD enforce limits on concurrent tasks and maximum TTL durations

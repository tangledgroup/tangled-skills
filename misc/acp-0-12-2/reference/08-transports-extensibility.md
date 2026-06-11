# Transports and Extensibility

## stdio Transport (Primary)

The primary transport mechanism. The client launches the agent as a subprocess:

- Agent reads JSON-RPC messages from **stdin**
- Agent writes JSON-RPC messages to **stdout**
- Messages are individual JSON-RPC requests, notifications, or responses
- Messages are delimited by newlines (`\n`) and must not contain embedded newlines
- Agent may write UTF-8 strings to **stderr** for logging (clients may capture, forward, or ignore)
- Agent must not write anything to stdout that is not a valid ACP message
- Client must not write anything to stdin that is not a valid ACP message

```
Client → launches agent subprocess
  Client → writes JSON-RPC to agent stdin
  Agent  → writes JSON-RPC to stdout
  Agent  → optional logs on stderr
Client → closes stdin, terminates subprocess
```

## Streamable HTTP (Draft)

A draft proposal for HTTP-based transport is in discussion. Not yet finalized.

## Custom Transports

Agents and clients may implement additional custom transport mechanisms. The protocol is transport-agnostic and can be implemented over any channel supporting bidirectional message exchange.

Custom transports must:
- Preserve the JSON-RPC message format
- Follow lifecycle requirements defined by ACP
- Document their specific connection establishment and message exchange patterns

## Extensibility

### The `_meta` Field

All protocol types include a `_meta` field (`{ [key: string]: unknown }`) for attaching custom information — including requests, responses, notifications, content blocks, tool calls, plan entries, and capability objects.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "session/prompt",
  "params": {
    "sessionId": "sess_abc123",
    "prompt": [{"type": "text", "text": "Hello, world!"}],
    "_meta": {
      "traceparent": "00-80e1afed08e019fc1110464cfa66635c-7a085853722dc6d2-01",
      "zed.dev/debugMode": true
    }
  }
}
```

Root-level `_meta` keys reserved for W3C trace context (for OpenTelemetry interop):
- `traceparent`
- `tracestate`
- `baggage`

Implementations must not add custom fields at the root of a spec type — all possible names are reserved for future protocol versions. Custom data goes in `_meta`.

### Extension Methods

Method names starting with underscore (`_`) are reserved for custom extensions:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "_zed.dev/workspace/buffers",
  "params": { "language": "rust" }
}
```

Extension methods follow standard JSON-RPC 2.0 semantics:
- **Requests** — Include an `id` field and expect a response
- **Notifications** — Omit the `id` field and are one-way

If the receiving end doesn't recognize a custom method, it responds with "Method not found".

### Custom Capabilities

Implementations can advertise custom capabilities using the `_meta` field within capability objects to indicate support for protocol extensions.

# Server Features

## Tools

MCP allows servers to expose tools that can be invoked by language models. Tools enable models to interact with external systems such as querying databases, calling APIs, or performing computations.

### User Interaction Model

Tools are designed to be **model-controlled** — the language model discovers and invokes tools automatically based on contextual understanding. However, implementations are free to expose tools through any interface pattern. For trust and safety, there SHOULD always be a human in the loop with ability to deny tool invocations.

Applications SHOULD:

- Provide UI making clear which tools are exposed to the AI model
- Insert visual indicators when tools are invoked
- Present confirmation prompts to ensure a human is in the loop

### Capabilities

Servers that support tools MUST declare the `tools` capability:

```json
{
  "capabilities": {
    "tools": {
      "listChanged": true
    }
  }
}
```

`listChanged` indicates whether the server emits notifications when the tool list changes.

### Listing Tools

Clients send a `tools/list` request (supports pagination):

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {
    "cursor": "optional-cursor-value"
  }
}
```

Response includes tools with name, title, description, inputSchema, icons, and execution properties:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "title": "Weather Information Provider",
        "description": "Get current weather information for a location",
        "inputSchema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City name or zip code"
            }
          },
          "required": ["location"]
        },
        "icons": [
          {
            "src": "https://example.com/weather-icon.png",
            "mimeType": "image/png",
            "sizes": ["48x48"]
          }
        ],
        "execution": {
          "taskSupport": "optional"
        }
      }
    ],
    "nextCursor": "next-page-cursor"
  }
}
```

### Calling Tools

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "location": "New York"
    }
  }
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Current weather in New York:\nTemperature: 72\u00b0F\nConditions: Partly cloudy"
      }
    ],
    "isError": false
  }
}
```

### List Changed Notification

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed"
}
```

### Tool Definition

- `name`: Unique identifier (1-128 chars, case-sensitive, allowed: A-Z, a-z, 0-9, underscore, hyphen, dot)
- `title`: Optional human-readable display name
- `description`: Human-readable functionality description
- `icons`: Optional array of icons for UI display
- `inputSchema`: JSON Schema defining expected parameters (defaults to 2020-12 if no `$schema`)
- `outputSchema`: Optional JSON Schema defining output structure
- `annotations`: Optional behavior descriptions
- `execution`: Optional execution properties (`taskSupport`: `"forbidden"`, `"optional"`, or `"required"`)

For tools with no parameters:

```json
{ "type": "object", "additionalProperties": false }
```

### Tool Result Content Types

Tool results contain unstructured content in the `content` field or structured content in `structuredContent`:

**Text:**

```json
{ "type": "text", "text": "Tool result text" }
```

**Image:**

```json
{
  "type": "image",
  "data": "base64-encoded-data",
  "mimeType": "image/png"
}
```

**Audio:**

```json
{
  "type": "audio",
  "data": "base64-encoded-audio-data",
  "mimeType": "audio/wav"
}
```

**Resource Links:**

```json
{
  "type": "resource_link",
  "uri": "file:///project/src/main.rs",
  "name": "main.rs",
  "description": "Primary application entry point",
  "mimeType": "text/x-rust"
}
```

**Embedded Resources:**

```json
{
  "type": "resource",
  "resource": {
    "uri": "file:///project/src/main.rs",
    "mimeType": "text/x-rust",
    "text": "fn main() { println!(\"Hello world!\"); }"
  }
}
```

**Structured Content:**

```json
{
  "content": [
    { "type": "text", "text": "{\"temperature\": 22.5}" }
  ],
  "structuredContent": {
    "temperature": 22.5
  }
}
```

### Error Handling

Two error reporting mechanisms:

- **Protocol Errors**: Standard JSON-RPC errors for unknown tools, malformed requests, server errors
- **Tool Execution Errors**: Reported with `isError: true` in the result for API failures, validation errors, business logic errors

Clients SHOULD provide tool execution errors to language models to enable self-correction.

### Security Considerations

- Servers MUST validate all inputs, implement access controls, rate limit invocations, and sanitize outputs
- Clients SHOULD prompt for user confirmation on sensitive operations
- Clients SHOULD show tool inputs before calling the server
- Tool annotations should be considered untrusted unless from trusted servers

## Resources

MCP provides a standardized way for servers to expose resources to clients. Resources allow servers to share data providing context to language models, such as files, database schemas, or application-specific information. Each resource is uniquely identified by a URI.

### User Interaction Model

Resources are **application-driven**, with host applications determining how to incorporate context. Implementations could expose resources through UI elements, search interfaces, or automatic context inclusion.

### Capabilities

```json
{
  "capabilities": {
    "resources": {
      "subscribe": true,
      "listChanged": true
    }
  }
}
```

- `subscribe`: Client can subscribe to changes on individual resources
- `listChanged`: Server emits notifications when resource list changes

Both are optional — servers can support neither, either, or both.

### Listing Resources

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/list",
  "params": { "cursor": "optional-cursor-value" }
}
```

### Reading Resources

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "resources/read",
  "params": { "uri": "file:///project/src/main.rs" }
}
```

Response includes contents with either `text` or `blob` (base64-encoded binary).

### Resource Templates

Servers expose parameterized resources using URI templates (RFC 6570):

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "resources/templates/list"
}
```

Response includes `uriTemplate` (e.g., `file:///{path}`) with name, description, and mimeType.

### Subscriptions

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "resources/subscribe",
  "params": { "uri": "file:///project/src/main.rs" }
}
```

Server sends update notifications:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/resources/updated",
  "params": { "uri": "file:///project/src/main.rs" }
}
```

### Resource Definition

- `uri`: Unique identifier
- `name`: Resource name
- `title`: Optional human-readable display name
- `description`: Optional description
- `icons`: Optional array of icons
- `mimeType`: Optional MIME type
- `size`: Optional size in bytes

### Annotations

Resources support optional annotations:

- `audience`: Array of `"user"` and/or `"assistant"`
- `priority`: 0.0 (optional) to 1.0 (required)
- `lastModified`: ISO 8601 timestamp

### Common URI Schemes

- `https://`: Resources available on the web (client can fetch directly)
- `file://`: Filesystem-like resources (need not map to actual files)
- `git://`: Git version control integration
- Custom schemes: Must conform to RFC 3986

### Error Handling

- Resource not found: `-32002`
- Internal errors: `-32603`

## Prompts

MCP provides a standardized way for servers to expose prompt templates to clients. Prompts allow servers to provide structured messages and instructions for interacting with language models.

### User Interaction Model

Prompts are **user-controlled** — exposed from servers to clients for explicit user selection. Typically triggered through user-initiated commands (e.g., slash commands).

### Capabilities

```json
{
  "capabilities": {
    "prompts": {
      "listChanged": true
    }
  }
}
```

### Listing Prompts

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "prompts/list",
  "params": { "cursor": "optional-cursor-value" }
}
```

### Getting a Prompt

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "prompts/get",
  "params": {
    "name": "code_review",
    "arguments": {
      "code": "def hello():\n    print('world')"
    }
  }
}
```

Response includes messages with role ("user" or "assistant") and content (text, image, audio, or embedded resource).

### Prompt Definition

- `name`: Unique identifier
- `title`: Optional human-readable display name
- `description`: Optional description
- `icons`: Optional array of icons
- `arguments`: Optional list of argument definitions (name, description, required)

### Error Handling

- Invalid prompt name: `-32602`
- Missing required arguments: `-32602`
- Internal errors: `-32603`

## Server Utilities

### Completion

Servers offer autocompletion suggestions for prompt and resource template arguments.

**Capabilities:**

```json
{ "capabilities": { "completions": {} } }
```

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "completion/complete",
  "params": {
    "ref": { "type": "ref/prompt", "name": "code_review" },
    "argument": { "name": "language", "value": "py" }
  }
}
```

**Response:**

```json
{
  "result": {
    "completion": {
      "values": ["python", "pytorch", "pyside"],
      "total": 10,
      "hasMore": true
    }
  }
}
```

Reference types: `ref/prompt` (by name) or `ref/resource` (by URI).

### Logging

Servers send structured log messages to clients. Clients control verbosity by setting minimum log levels.

**Capabilities:**

```json
{ "capabilities": { "logging": {} } }
```

**Set log level:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "logging/setLevel",
  "params": { "level": "info" }
}
```

**Log message notification:**

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/message",
  "params": {
    "level": "error",
    "logger": "database",
    "data": { "error": "Connection failed" }
  }
}
```

Log levels follow RFC 5424 syslog severity: `debug`, `info`, `notice`, `warning`, `error`, `critical`, `alert`, `emergency`.

Log messages MUST NOT contain credentials, secrets, PII, or internal system details.

### Pagination

MCP uses cursor-based pagination for list operations.

- Cursor is an opaque string token
- Page size is determined by the server
- Clients MUST treat cursors as opaque tokens (don't parse, modify, or persist across sessions)
- Missing `nextCursor` means end of results

Operations supporting pagination:

- `resources/list`
- `resources/templates/list`
- `prompts/list`
- `tools/list`

**Response with cursor:**

```json
{
  "result": {
    "resources": [...],
    "nextCursor": "eyJwYWdlIjogM30="
  }
}
```

**Request with cursor:**

```json
{
  "params": { "cursor": "eyJwYWdlIjogMn0=" }
}
```

Invalid cursors SHOULD result in error code -32602.

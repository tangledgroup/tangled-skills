# Client Features

## Roots

MCP provides a standardized way for clients to expose filesystem "roots" to servers. Roots define the boundaries of where servers can operate within the filesystem.

### User Interaction Model

Roots are typically exposed through workspace or project configuration interfaces. Implementations could offer workspace/project pickers, combined with automatic detection from version control systems or project files.

### Capabilities

```json
{
  "capabilities": {
    "roots": {
      "listChanged": true
    }
  }
}
```

`listChanged` indicates whether the client emits notifications when roots change.

### Listing Roots

Servers send a `roots/list` request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "roots/list"
}
```

Response:

```json
{
  "result": {
    "roots": [
      {
        "uri": "file:///home/user/projects/myproject",
        "name": "My Project"
      }
    ]
  }
}
```

### Root List Changes

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/roots/list_changed"
}
```

### Root Definition

- `uri`: Unique identifier (MUST be a `file://` URI in current specification)
- `name`: Optional human-readable display name

### Error Handling

- Client does not support roots: `-32601`
- Internal errors: `-32603`

### Security Considerations

- Clients MUST only expose roots with appropriate permissions and validate URIs to prevent path traversal
- Servers SHOULD handle cases where roots become unavailable and respect root boundaries
- Clients SHOULD prompt users for consent before exposing roots

## Sampling

MCP provides a standardized way for servers to request LLM sampling ("completions" or "generations") from language models via clients. This enables servers to leverage AI capabilities without needing API keys.

### User Interaction Model

Sampling allows servers to implement agentic behaviors by enabling LLM calls nested inside other MCP server features. There SHOULD always be a human in the loop with ability to deny sampling requests.

Applications SHOULD:

- Provide UI making it easy to review sampling requests
- Allow users to view and edit prompts before sending
- Present generated responses for review before delivery

### Capabilities

**Basic sampling:**

```json
{ "capabilities": { "sampling": {} } }
```

**With tool use support:**

```json
{ "capabilities": { "sampling": { "tools": {} } } }
```

**With context inclusion (soft-deprecated):**

```json
{ "capabilities": { "sampling": { "context": {} } } }
```

The `includeContext` parameter values `"thisServer"` and `"allServers"` are soft-deprecated.

### Creating Messages

Servers send a `sampling/createMessage` request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "What is the capital of France?"
        }
      }
    ],
    "modelPreferences": {
      "hints": [{ "name": "claude-3-sonnet" }],
      "intelligencePriority": 0.8,
      "speedPriority": 0.5
    },
    "systemPrompt": "You are a helpful assistant.",
    "maxTokens": 100
  }
}
```

Response:

```json
{
  "result": {
    "role": "assistant",
    "content": {
      "type": "text",
      "text": "The capital of France is Paris."
    },
    "model": "claude-3-sonnet-20240307",
    "stopReason": "endTurn"
  }
}
```

### Sampling with Tools

Servers include `tools` and optionally `toolChoice` in the request:

```json
{
  "params": {
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "What's the weather in Paris?"
        }
      }
    ],
    "tools": [
      {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "inputSchema": {
          "type": "object",
          "properties": {
            "city": { "type": "string", "description": "City name" }
          },
          "required": ["city"]
        }
      }
    ],
    "toolChoice": { "mode": "auto" },
    "maxTokens": 1000
  }
}
```

Response with tool use:

```json
{
  "result": {
    "role": "assistant",
    "content": [
      {
        "type": "tool_use",
        "id": "call_abc123",
        "name": "get_weather",
        "input": { "city": "Paris" }
      }
    ],
    "model": "claude-3-sonnet-20240307",
    "stopReason": "toolUse"
  }
}
```

### Multi-turn Tool Loop

After receiving tool use requests, the server:

1. Executes the requested tool uses
2. Sends a new sampling request with tool results appended
3. Receives the LLM's response (which might contain new tool uses)
4. Repeats as needed

**Follow-up request with tool results:**

```json
{
  "params": {
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "What's the weather in Paris?"
        }
      },
      {
        "role": "assistant",
        "content": [
          {
            "type": "tool_use",
            "id": "call_abc123",
            "name": "get_weather",
            "input": { "city": "Paris" }
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "tool_result",
            "toolUseId": "call_abc123",
            "content": [
              { "type": "text", "text": "Weather in Paris: 18\u00b0C, partly cloudy" }
            ]
          }
        ]
      }
    ],
    "tools": [...],
    "maxTokens": 1000
  }
}
```

### Message Content Constraints

**Tool Result Messages**: When a user message contains tool results (type: "tool_result"), it MUST contain ONLY tool results. Mixing tool results with other content types is not allowed.

**Tool Use and Result Balance**: Every assistant message with `ToolUseContent` blocks MUST be followed by a user message consisting entirely of `ToolResultContent` blocks, with each tool use matched by a corresponding tool result.

### Tool Choice Modes

- `{mode: "auto"}`: Model decides whether to use tools (default)
- `{mode: "required"}`: Model MUST use at least one tool
- `{mode: "none"}`: Model MUST NOT use any tools

### Model Preferences

Servers express needs through normalized priority values (0-1):

- `costPriority`: How important is minimizing costs?
- `speedPriority`: How important is low latency?
- `intelligencePriority`: How important are advanced capabilities?

Model hints allow suggesting specific models or families:

```json
{
  "hints": [
    { "name": "claude-3-sonnet" },
    { "name": "claude" }
  ],
  "costPriority": 0.3,
  "speedPriority": 0.8,
  "intelligencePriority": 0.5
}
```

Hints are advisory — clients make final model selection and MAY map hints to equivalent models from different providers.

### Error Handling

- User rejected sampling request: `-1`
- Tool result missing in request: `-32602`
- Tool results mixed with other content: `-32602`

## Elicitation

MCP provides a standardized way for servers to request additional information from users through the client during interactions. Two modes are supported:

- **Form mode**: Structured data collection with optional JSON schema validation (data exposed to client)
- **URL mode**: Out-of-band interaction via URL navigation (data NOT exposed to client)

### User Interaction Model

Elicitation allows servers to implement interactive workflows nested inside other MCP server features.

Security requirements:

- Servers MUST NOT use form mode for sensitive information (passwords, API keys, tokens, payment credentials)
- Servers MUST use URL mode for interactions involving such sensitive information
- "Sensitive information" refers to secrets and credentials granting access or authorizing transactions

MCP clients MUST:

- Provide UI making clear which server is requesting information
- Respect user privacy with clear decline and cancel options
- For form mode, allow users to review and modify responses before sending
- For URL mode, clearly display the target domain/host and gather consent before navigation

### Capabilities

```json
{
  "capabilities": {
    "elicitation": {
      "form": {},
      "url": {}
    }
  }
}
```

For backwards compatibility, `{ "elicitation": {} }` is equivalent to `{ "elicitation": { "form": {} } }`.

### Elicitation Requests

All requests MUST include `mode` (string: `"form"` or `"url"`) and `message` (human-readable explanation).

#### Form Mode

Form mode requests MUST specify `mode: "form"` (or omit for backwards compat) and include `requestedSchema`:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "elicitation/create",
  "params": {
    "mode": "form",
    "message": "Please provide your GitHub username",
    "requestedSchema": {
      "type": "object",
      "properties": {
        "name": { "type": "string" }
      },
      "required": ["name"]
    }
  }
}
```

**Response:**

```json
{
  "result": {
    "action": "accept",
    "content": { "name": "octocat" }
  }
}
```

**Schema Restrictions**: Form mode schemas are limited to flat objects with primitive properties only:

- **String**: `type: "string"` with optional `title`, `description`, `minLength`, `maxLength`, `pattern`, `format` (email, uri, date, date-time), `default`
- **Number/Integer**: `type: "number"` or `"integer"` with optional `minimum`, `maximum`, `default`
- **Boolean**: `type: "boolean"` with optional `default`
- **Enum** (single-select): `type: "string"` with `enum` array
- **Enum** (with titles): `type: "string"` with `oneOf` of `{const, title}` pairs
- **Multi-select enum**: `type: "array"` with `items` containing `enum` or `anyOf`

Complex nested structures and arrays of objects beyond enums are not supported.

#### URL Mode

URL mode directs users to external URLs for out-of-band interactions:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "elicitation/create",
  "params": {
    "mode": "url",
    "elicitationId": "550e8400-e29b-41d4-a716-446655440000",
    "url": "https://mcp.example.com/ui/set_api_key",
    "message": "Please provide your API key to continue."
  }
}
```

**Response:**

```json
{
  "result": {
    "action": "accept"
  }
}
```

The `action: "accept"` indicates user consented to the interaction — it does not mean the interaction is complete.

### Completion Notifications (URL Mode)

Servers MAY send `notifications/elicitation/complete` when out-of-band interaction completes:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/elicitation/complete",
  "params": {
    "elicitationId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### URL Elicitation Required Error

When a request cannot be processed until elicitation completes, the server MAY return error code `-32042` (`URLElicitationRequiredError`):

```json
{
  "error": {
    "code": -32042,
    "message": "This request requires more information.",
    "data": {
      "elicitations": [
        {
          "mode": "url",
          "elicitationId": "550e8400-e29b-41d4-a716-446655440000",
          "url": "https://mcp.example.com/connect?elicitationId=...",
          "message": "Authorization is required."
        }
      ]
    }
  }
}
```

### Response Actions

Three-action model for both form and URL modes:

- **Accept** (`"accept"`): User approved and submitted. Form mode includes `content` with data; URL mode omits `content`.
- **Decline** (`"decline"`): User explicitly declined. `content` typically omitted.
- **Cancel** (`"cancel"`): User dismissed without explicit choice. `content` typically omitted.

### Security Considerations

#### Statefulness

Servers implementing elicitation MUST securely associate state with individual users:

- State MUST NOT be associated with session IDs alone
- For remote servers, user identification MUST be derived from credentials via MCP authorization (e.g., `sub` claim)

#### Safe URL Handling

Servers requesting elicitation:

- MUST NOT include sensitive user information in URLs
- MUST NOT provide pre-authenticated URLs
- SHOULD use HTTPS for non-development environments

Clients implementing URL mode:

- MUST NOT automatically pre-fetch the URL or open without explicit consent
- MUST show the full URL to the user before consent
- MUST open URLs securely (e.g., SFSafariViewController on iOS, not WKWebView)
- SHOULD highlight the domain to mitigate subdomain spoofing
- SHOULD warn for ambiguous/suspicious URIs (e.g., Punycode)

#### Phishing Prevention

For URL mode elicitation, servers MUST verify that the user who opens the URL is the same user who generated the elicitation request. Common approach: check session cookie against the `sub` claim from the MCP authorization server.

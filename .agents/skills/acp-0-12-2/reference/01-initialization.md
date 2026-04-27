# Initialization and Capabilities

## Purpose

The initialization phase allows clients and agents to negotiate protocol versions, capabilities, and authentication methods. This is the first exchange on every ACP connection.

## Flow

```
Client → Agent: initialize (negotiate version & capabilities)
Agent  → Client: initialize response (chosen version & capabilities)
[optional] Client → Agent: authenticate
```

Before any session can be created, clients **must** complete initialization.

## The Initialize Request

The client sends `initialize` with its latest supported protocol version and capabilities:

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "method": "initialize",
  "params": {
    "protocolVersion": 1,
    "clientCapabilities": {
      "fs": {
        "readTextFile": true,
        "writeTextFile": true
      },
      "terminal": true
    },
    "clientInfo": {
      "name": "my-client",
      "title": "My Client",
      "version": "1.0.0"
    }
  }
}
```

## The Initialize Response

The agent responds with the chosen protocol version and its capabilities:

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "protocolVersion": 1,
    "agentCapabilities": {
      "loadSession": true,
      "promptCapabilities": {
        "image": true,
        "audio": true,
        "embeddedContext": true
      },
      "mcpCapabilities": {
        "http": true,
        "sse": true
      },
      "sessionCapabilities": {
        "list": {}
      }
    },
    "agentInfo": {
      "name": "my-agent",
      "title": "My Agent",
      "version": "1.0.0"
    },
    "authMethods": []
  }
}
```

## Protocol Version Negotiation

Protocol versions are single integers identifying a **major** version. Only incremented for breaking changes.

- Client sends the latest version it supports
- If agent supports it, responds with the same version
- Otherwise, agent responds with the latest version it supports
- If client doesn't support the agent's response version, it should close the connection

Non-breaking features are introduced through **capabilities**, not version bumps. Unknown capabilities must be treated as unsupported.

## Client Capabilities

Clients advertise what they can provide to agents:

- **Filesystem** (`fs`) — `readTextFile` and `writeTextFile` boolean flags indicating whether the agent can call `fs/read_text_file` and `fs/write_text_file`
- **Terminal** (`terminal`) — Boolean flag for terminal command execution via `terminal/create`
- **Prompt capabilities** — What content types the client supports in prompts (image, audio, embedded context)

## Agent Capabilities

Agents advertise what features they support:

- **loadSession** — Whether the agent supports loading existing sessions via `session/load`
- **promptCapabilities** — What content types the agent accepts in user prompts (image, audio, embeddedContext)
- **mcpCapabilities** — MCP server transport types supported (http, sse)
- **sessionCapabilities.list** — Whether the agent supports `session/list` for discovering sessions

## Authentication

If the agent's initialize response includes `authMethods`, the client must authenticate before creating sessions:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "authenticate",
  "params": {
    "authMethod": "token",
    "token": "..."
  }
}
```

Authentication methods are negotiated during initialization. The agent specifies which methods it accepts in the `authMethods` array.

## Capability Design Principles

- All capabilities are optional — implementations should support all possible combinations of peer capabilities
- New capabilities are non-breaking — unknown capabilities must be ignored
- Capabilities may signal method availability, parameter subsets, or behavioral differences
- Custom capabilities can be advertised via the `_meta` field

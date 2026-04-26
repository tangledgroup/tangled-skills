# MCP Server

## Overview

Logfire provides a hosted remote MCP (Model Context Protocol) server that gives LLMs access to OpenTelemetry traces and metrics. This enables coding agents to query production telemetry data, analyze distributed traces, and perform custom SQL queries directly.

The local STDIO MCP server is deprecated — use the remote HTTP MCP server.

## Remote MCP Server (Recommended)

No local installation needed. Add configuration to your MCP client:

**US region**: `https://logfire-us.pydantic.dev/mcp`
**EU region**: `https://logfire-eu.pydantic.dev/mcp`
**Self-hosted**: `https://<your-logfire-hostname>/mcp`

Authentication is handled automatically through browser login on first connection.

## Configuration Examples

### Cursor

Create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "logfire": {
      "type": "http",
      "url": "https://logfire-us.pydantic.dev/mcp"
    }
  }
}
```

### Claude Code

```bash
claude mcp add logfire --transport http https://logfire-us.pydantic.dev/mcp
```

### Claude Desktop

Add to Claude settings:

```json
{
  "mcpServers": {
    "logfire": {
      "type": "http",
      "url": "https://logfire-us.pydantic.dev/mcp"
    }
  }
}
```

### VS Code

Create `.vscode/mcp.json`:

```json
{
  "servers": {
    "logfire": {
      "type": "http",
      "url": "https://logfire-us.pydantic.dev/mcp"
    }
  }
}
```

### Cline

Add to `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "logfire": {
      "type": "http",
      "url": "https://logfire-us.pydantic.dev/mcp"
    }
  }
}
```

### Zed

Create `.zed/settings.json`:

```json
{
  "context_servers": {
    "logfire": {
      "type": "http",
      "url": "https://logfire-us.pydantic.dev/mcp"
    }
  }
}
```

## Sandboxed Environments

When browser authentication is unavailable, use an API key with `project:read` scope as a Bearer token:

```json
{
  "mcpServers": {
    "logfire": {
      "type": "http",
      "url": "https://logfire-us.pydantic.dev/mcp",
      "headers": {
        "Authorization": "Bearer <your-logfire-api-key>"
      }
    }
  }
}
```

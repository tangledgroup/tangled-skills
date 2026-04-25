# Logfire MCP Server Reference

## Overview

The Model Context Protocol (MCP) server enables LLMs to query your application's OpenTelemetry traces and metrics through Logfire. See https://github.com/pydantic/logfire-mcp for details.

## Remote MCP Server (Recommended)

Hosted by Pydantic — no local installation needed. Handles authentication via browser.

### Region Endpoints

| Region | URL |
|--------|-----|
| US | `https://logfire-us.pydantic.dev/mcp` |
| EU | `https://logfire-eu.pydantic.dev/mcp` |

## Client Configuration Examples

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

Add to `~/.config/claude/settings.json`:
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

Ensure MCP support is enabled, then create `.vscode/mcp.json`:
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

Add to `.vscode/cline_mcp_settings.json`:
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

## Sandboxed Environments (API Key Auth)

When browser auth is unavailable, use an API key with `project:read` scope:

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

## Self-Hosted Logfire

Replace the URL with your self-hosted instance:
```json
{
  "mcpServers": {
    "logfire": {
      "type": "http",
      "url": "https://logfire.my-company.com/mcp"
    }
  }
}
```

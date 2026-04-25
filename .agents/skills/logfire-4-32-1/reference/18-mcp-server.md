# MCP Server

Allow LLMs to query your telemetry data via Model Context Protocol:

### Remote MCP Server (Recommended)

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

Supported clients: Cursor, Claude Code, Claude Desktop, Cline, VS Code, Zed. Use `logfire-eu.pydantic.dev` for EU region.

See [reference/10-mcp-server.md](reference/10-mcp-server.md).

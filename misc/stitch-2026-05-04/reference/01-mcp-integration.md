# MCP Integration

## Contents
- Available Tools
- Platform Configuration
- Authentication Methods
- Virtual Tools
- Common Issues

## Available Tools

The Stitch MCP server exposes tools that coding agents can call. Key tools:

- `create_project` — Create a new Stitch project
- `list_projects` — List all accessible projects
- `generate_screen_from_text` — Generate a screen from a text prompt within a project
- `edit_screens` — Edit existing screens with a text prompt
- `generate_variants` — Generate design variants of a screen
- `list_screens` — List screens in a project
- `get_screen` — Retrieve screen metadata
- `extract_design_context` — Extract design DNA (colors, fonts, layout patterns) from a screen
- `create_design_system` — Create a design system for a project
- `list_design_systems` — List design systems in a project

## Platform Configuration

### Claude Code

```bash
claude mcp add stitch "npx @_davideast/stitch-mcp proxy"
```

Verify: `claude mcp list`

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["@_davideast/stitch-mcp", "proxy"]
    }
  }
}
```

### Cursor / VS Code / Windsurf

Add to MCP settings JSON (`.vscode/mcp.json` or Settings > MCP):

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["@_davideast/stitch-mcp", "proxy"]
    }
  }
}
```

### Gemini CLI

```bash
gemini mcp add stitch "npx @_davideast/stitch-mcp proxy"
```

Or via extension. If gcloud is already configured, set:

```bash
export STITCH_USE_SYSTEM_GCLOUD=1
```

### Codex CLI

```bash
codex mcp add stitch "npx @_davideast/stitch-mcp proxy"
```

## Authentication Methods

### Automatic (recommended)

Run the init wizard. It handles gcloud check/install, Google login, project setup, and Stitch API activation:

```bash
npx @_davideast/stitch-mcp init
```

### API Key

Set `STITCH_API_KEY` environment variable to skip OAuth entirely:

```bash
export STITCH_API_KEY="your-api-key"
```

### Manual gcloud

If you already have gcloud configured:

```bash
gcloud auth application-default login
gcloud config set project <PROJECT_ID>
gcloud beta services mcp enable stitch.googleapis.com --project=<PROJECT_ID>
```

Then use `STITCH_USE_SYSTEM_GCLOUD=1` in your MCP config:

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["@_davideast/stitch-mcp", "proxy"],
      "env": {
        "STITCH_USE_SYSTEM_GCLOUD": "1"
      }
    }
  }
}
```

### Prerequisites

- Node.js 18+
- Google Cloud project with billing enabled
- At least one project on stitch.withgoogle.com

## Virtual Tools

The `@_davideast/stitch-mcp` proxy exposes additional virtual tools that combine multiple API calls:

### `build_site`

Builds a site from a project by mapping screens to routes. Returns HTML for each page.

```json
{
  "projectId": "string (required)",
  "routes": [
    {
      "screenId": "string (required)",
      "route": "string (required, e.g. \"/\" or \"/about\")"
    }
  ]
}
```

### `get_screen_code`

Retrieves a screen and downloads its HTML code content.

### `get_screen_image`

Retrieves a screen and downloads its screenshot as base64.

## Common Issues

### API keys don't work for MCP auth

The MCP proxy requires OAuth. Setting `STITCH_API_KEY` alone gives auth errors. Use `gcloud auth application-default login` or the init wizard instead. For direct SDK use (not MCP proxy), `STITCH_API_KEY` works fine.

### `.env` file conflicts

A `.env` file in your project directory can break the proxy with `invalid character 'd'` errors. Move or rename the `.env` file when running the Stitch MCP proxy.

### Permission errors

Check your Google Cloud project for:

- Billing enabled
- Stitch API enabled: `gcloud beta services mcp enable stitch.googleapis.com`
- Owner or Editor role on your account

### Full reset

When configuration is broken:

```bash
npx @_davideast/stitch-mcp logout
npx @_davideast/stitch-mcp init
```

### Health check

```bash
npx @_davideast/stitch-mcp doctor
```

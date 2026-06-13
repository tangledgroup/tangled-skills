# CLI Reference

## Contents
- Installation
- Commands
- Authentication
- Environment Variables

## Installation

Run directly with `npx` (no install needed):

```bash
npx @_davideast/stitch-mcp <command>
```

Or install globally:

```bash
npm install -g @_davideast/stitch-mcp
stitch-mcp <command>
```

Package: `@_davideast/stitch-mcp` (v0.5.5, Apache 2.0). Repository: `davideast/stitch-mcp`. Built on top of `@google/stitch-sdk`.

## Commands

### Setup

| Command | Description |
|---------|-------------|
| `init` | Set up auth, gcloud, and MCP client config (interactive wizard) |
| `doctor` | Verify configuration health |
| `logout` | Revoke credentials |

```bash
# First-time setup
npx @_davideast/stitch-mcp init

# Check everything is working
npx @_davideast/stitch-mcp doctor
```

### Development

| Command | Description |
|---------|-------------|
| `serve -p <id>` | Preview all project screens on a local Vite dev server |
| `screens -p <id>` | Browse screens in terminal (interactive) |
| `view` | Interactive resource browser for projects and screens |

```bash
# Serve all screens from a project
npx @_davideast/stitch-mcp serve -p 4044680601076201931

# Browse interactively
npx @_davideast/stitch-mcp view --projects
npx @_davideast/stitch-mcp view --project <id> --screen <screen-id>
```

In the `view` browser: arrow keys navigate, Enter drills into nested data, `c` copies selected value, `s` previews HTML in browser, `o` opens project in Stitch, `q` quits.

### Build

| Command | Description |
|---------|-------------|
| `site -p <id>` | Generate an Astro project from screens (maps screens to routes) |
| `snapshot` | Save screen state to file for testing |

```bash
# Build a complete site
npx @_davideast/stitch-mcp site -p <project-id>
```

### Integration

| Command | Description |
|---------|-------------|
| `tool [name]` | Invoke any MCP tool from CLI |
| `proxy` | Run MCP proxy server for coding agents |

```bash
# List all available tools
npx @_davideast/stitch-mcp tool

# See a tool's schema
npx @_davideast/stitch-mcp tool build_site -s

# Invoke a tool with JSON data
npx @_davideast/stitch-mcp tool build_site -d '{
  "projectId": "123456",
  "routes": [
    { "screenId": "abc", "route": "/" },
    { "screenId": "def", "route": "/about" }
  ]
}'
```

Run any command with `--help` for full options.

## Authentication

### Automatic (recommended)

The `init` wizard handles everything: gcloud installation, OAuth login, credentials, project setup, and MCP client configuration.

```bash
npx @_davideast/stitch-mcp init
```

### API Key

Set `STITCH_API_KEY` to skip OAuth:

```bash
export STITCH_API_KEY="your-api-key"
npx @_davideast/stitch-mcp serve -p <project-id>
```

### Manual gcloud

For existing gcloud setups:

```bash
gcloud auth application-default login
gcloud config set project <PROJECT_ID>
gcloud beta services mcp enable stitch.googleapis.com --project=<PROJECT_ID>
```

Then use `STITCH_USE_SYSTEM_GCLOUD=1` in MCP config or environment.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `STITCH_API_KEY` | API key for direct authentication (skips OAuth) |
| `STITCH_ACCESS_TOKEN` | Pre-existing OAuth access token |
| `STITCH_USE_SYSTEM_GCLOUD` | Use system gcloud config instead of isolated config |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID (with OAuth) |

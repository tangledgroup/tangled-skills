# Agent Integrations

Complete setup guides for integrating agentmemory with specific AI coding agents.

## Claude Code

### Plugin Installation (Recommended)

The Claude Code plugin provides 12 lifecycle hooks, 4 skills, and auto-wires the MCP server.

```bash
# Start the memory server in a separate terminal
npx @agentmemory/agentmemory

# In Claude Code:
/plugin marketplace add rohitg00/agentmemory
/plugin install agentmemory
```

The plugin automatically:
- Registers all 12 hooks for automatic capture
- Installs 4 skills (`/recall`, `/remember`, `/session-history`, `/forget`)
- Wires the `@agentmemory/mcp` stdio server via `.mcp.json`
- No manual MCP config needed

**Verify:**
```bash
curl http://localhost:3111/agentmemory/health
# {"status":"healthy"}
```

### Manual MCP Setup

If you prefer not to use the plugin:

```json
// Add to Claude Code MCP config
{
  "mcpServers": {
    "agentmemory": {
      "command": "npx",
      "args": ["-y", "@agentmemory/mcp"]
    }
  }
}
```

## Hermes Agent

### Option 1: MCP Server (Zero Code)

Start the server:
```bash
npx @agentmemory/agentmemory
```

Add to `~/.hermes/config.yaml`:
```yaml
mcp_servers:
  agentmemory:
    command: npx
    args: ["-y", "@agentmemory/mcp"]
```

### Option 2: Memory Provider Plugin (Deeper Integration)

Copy the plugin:
```bash
cp -r integrations/hermes ~/.hermes/plugins/memory/agentmemory
```

Start the server:
```bash
npx @agentmemory/agentmemory
```

The plugin provides 6 lifecycle hooks:
- `prefetch()`: Injects relevant memories before each LLM call
- `sync_turn()`: Captures every conversation turn in the background
- `on_session_end()`: Marks sessions complete for summarization
- `on_pre_compress()`: Re-injects context before compaction
- `on_memory_write()`: Mirrors MEMORY.md writes to agentmemory
- `system_prompt_block()`: Injects project profile at session start

**Configuration** (`~/.hermes/plugins/memory/agentmemory/config.yaml`):
```yaml
enabled: true
base_url: http://localhost:3111
token_budget: 2000
min_confidence: 0.5
```

### Paste This Prompt into Hermes

```text
Install agentmemory for Hermes. Run `npx @agentmemory/agentmemory` in a
separate terminal to start the memory server on localhost:3111. Then
add this to `~/.hermes/config.yaml` so Hermes can use agentmemory as
an MCP server with all 43 memory tools:

mcp_servers:
  agentmemory:
    command: npx
    args: ["-y", "@agentmemory/mcp"]

Verify it's working with
`curl http://localhost:3111/agentmemory/health` — it should return
{"status":"healthy"}. Open the real-time viewer at
http://localhost:3113 to watch memories being captured live.

If I want deeper integration — pre-LLM context injection, turn-level
capture, memory-write mirroring to MEMORY.md, and system prompt block
injection — copy `integrations/hermes` from the agentmemory repo to
`~/.hermes/plugins/memory/agentmemory` instead. That gives me the
6-hook memory provider plugin on top of the MCP server.
```

## OpenClaw

### Option 1: MCP Server (Zero Code)

Start the server:
```bash
npx @agentmemory/agentmemory
```

Add to your OpenClaw MCP config:
```json
{
  "mcpServers": {
    "agentmemory": {
      "command": "npx",
      "args": ["-y", "@agentmemory/mcp"]
    }
  }
}
```

### Option 2: Gateway Plugin (Deeper Integration)

Copy the plugin:
```bash
cp -r integrations/openclaw ~/.openclaw/plugins/memory/agentmemory
```

Start the server:
```bash
npx @agentmemory/agentmemory
```

The plugin provides 4 lifecycle hooks:
- `onSessionStart`: Starts new session, injects context
- `onPreLlmCall`: Injects token-budgeted memories before each LLM call
- `onPostToolUse`: Records every tool use, error, and decision
- `onSessionEnd`: Marks session complete for compression

**Configuration** (`~/.openclaw/plugins/memory/agentmemory/config.yaml`):
```yaml
enabled: true
base_url: http://localhost:3111
token_budget: 2000
min_confidence: 0.5
```

### Paste This Prompt into OpenClaw

```text
Install agentmemory for OpenClaw. Run `npx @agentmemory/agentmemory` in a
separate terminal to start the memory server on localhost:3111. Then add
this to my OpenClaw MCP config so agentmemory is available as an MCP
server with all 43 memory tools (memory_recall, memory_save,
memory_smart_search, memory_timeline, memory_profile, etc.):

{
  "mcpServers": {
    "agentmemory": {
      "command": "npx",
      "args": ["-y", "@agentmemory/mcp"]
    }
  }
}

Restart OpenClaw. Verify it's working with
`curl http://localhost:3111/agentmemory/health` — it should return
{"status":"healthy"}. Open the real-time viewer at
http://localhost:3113 to watch memories being captured live.

If I want deeper integration with pre-LLM context injection and
automatic tool-use capture, copy `integrations/openclaw` from the
agentmemory repo to `~/.openclaw/plugins/memory/agentmemory` — that
gives me the 4-hook gateway plugin instead of just the MCP server.
```

## Cursor

Add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "agentmemory": {
      "command": "npx",
      "args": ["-y", "@agentmemory/mcp"]
    }
  }
}
```

Restart Cursor. The server must be running separately:
```bash
npx @agentmemory/agentmemory
```

## Gemini CLI

```bash
gemini mcp add agentmemory -- npx -y @agentmemory/mcp
```

Start the server:
```bash
npx @agentmemory/agentmemory
```

## OpenCode

Add to `opencode.json`:
```json
{
  "mcp": {
    "agentmemory": {
      "type": "local",
      "command": ["npx", "-y", "@agentmemory/mcp"],
      "enabled": true
    }
  }
}
```

Start the server:
```bash
npx @agentmemory/agentmemory
```

## Codex CLI

Add to `.codex/config.yaml`:
```yaml
mcp_servers:
  agentmemory:
    command: npx
    args: ["-y", "@agentmemory/mcp"]
```

Start the server:
```bash
npx @agentmemory/agentmemory
```

## Cline, Goose, Kilo Code

Add MCP server in your agent's settings:
```json
{
  "mcpServers": {
    "agentmemory": {
      "command": "npx",
      "args": ["-y", "@agentmemory/mcp"]
    }
  }
}
```

## Claude Desktop

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "agentmemory": {
      "command": "npx",
      "args": ["-y", "@agentmemory/mcp"]
    }
  }
}
```

Restart Claude Desktop. Start the server:
```bash
npx @agentmemory/agentmemory
```

## Windsurf, Roo Code

Same MCP config pattern:
```json
{
  "mcpServers": {
    "agentmemory": {
      "command": "npx",
      "args": ["-y", "@agentmemory/mcp"]
    }
  }
}
```

## Aider (REST API)

Aider doesn't support MCP, but you can use the REST API directly:

```bash
# Start the server
npx @agentmemory/agentmemory

# Query memory from within your workflow
curl -X POST http://localhost:3111/agentmemory/smart-search \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication middleware", "budget": 2000}'
```

## Claude Agent SDK (TypeScript)

Use the `AgentSDKProvider` for programmatic integration:

```typescript
import { AgentSDKProvider } from '@agentmemory/agentmemory';

const provider = new AgentSDKProvider({
  baseURL: 'http://localhost:3111',
  secret: process.env.AGENTMEMORY_SECRET
});

// Inject into your agent's context
const context = await provider.getContext({
  sessionId: 'your-session-id',
  project: 'your-project-name',
  budget: 2000
});
```

## Standalone MCP (No Full Server)

If you only need MCP tools without the REST API, viewer, or cron jobs:

```bash
npx -y @agentmemory/agentmemory mcp
# or
npx -y @agentmemory/mcp
```

This provides 7 core tools without requiring iii-engine or Docker.

## Multi-Agent Setup

All agents can share the same memory server. Start one server instance:

```bash
npx @agentmemory/agentmemory
```

Then configure multiple agents to point to the same `localhost:3111`. Memories are automatically shared across all connected agents via MCP.

### Team Memory (Multi-User)

For team-wide memory with namespaced sharing:

```env
TEAM_ID=your-team-name
USER_ID=your-username
TEAM_MODE=private  # or 'shared'
```

Use `memory_team_share` and `memory_team_feed` MCP tools for explicit sharing.

## Environment Variables (All Integrations)

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENTMEMORY_URL` | `http://localhost:3111` | Server URL |
| `AGENTMEMORY_SECRET` | (none) | Auth token for protected instances |
| `TOKEN_BUDGET` | `2000` | Max tokens per context injection |
| `MIN_CONFIDENCE` | `0.5` | Minimum search confidence threshold |

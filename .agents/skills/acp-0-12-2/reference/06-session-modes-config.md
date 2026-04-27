# Session Modes and Config

## Overview

Session modes allow agents to operate in different modes that affect system prompts, tool availability, and permission behavior. The newer **Session Config Options** mechanism is the preferred approach — dedicated mode methods are deprecated but still supported for backwards compatibility.

## Session Modes (Legacy)

During session setup, the agent may return available modes:

```json
{
  "result": {
    "sessionId": "sess_abc123",
    "modes": {
      "currentModeId": "ask",
      "availableModes": [
        {
          "id": "ask",
          "name": "Ask",
          "description": "Request permission before making any changes"
        },
        {
          "id": "architect",
          "name": "Architect",
          "description": "Design and plan without implementation"
        },
        {
          "id": "code",
          "name": "Code",
          "description": "Write and modify code with full tool access"
        }
      ]
    }
  }
}
```

### Setting Mode from Client

The client changes mode via `session/set_mode`:

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "session/set_mode",
  "params": {
    "sessionId": "sess_abc123",
    "modeId": "code"
  }
}
```

Mode changes can occur at any point — whether the agent is idle or generating a response.

### Mode State Response

The agent may also push mode changes via `session/update` with `mode_update`:

```json
{
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123",
    "update": {
      "sessionUpdate": "mode_update",
      "currentModeId": "code"
    }
  }
}
```

## Session Config Options (Preferred)

Session config options replace dedicated mode methods with a more flexible key-value configuration system. Clients set configuration on sessions, and agents adjust behavior accordingly.

Config options are session-scoped and can be updated at any time during the session lifecycle.

## Slash Commands

Agents can advertise slash commands that users invoke for quick access to specific capabilities:

```json
{
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123",
    "update": {
      "sessionUpdate": "available_commands_update",
      "availableCommands": [
        {
          "name": "web",
          "description": "Search the web for information",
          "input": { "hint": "query to search for" }
        },
        {
          "name": "test",
          "description": "Run tests for the current project"
        },
        {
          "name": "plan",
          "description": "Create a detailed implementation plan",
          "input": { "hint": "description of what to plan" }
        }
      ]
    }
  }
}
```

Commands are included as regular user messages in prompt requests. The client includes the command text in the prompt when the user invokes a slash command.

Agents can dynamically update available commands at any time during the session by sending another `available_commands_update` notification.

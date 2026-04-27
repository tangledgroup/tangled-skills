# Tool Calls and Permissions

## Overview

Tool calls represent actions that LLMs request agents to perform during prompt turns — reading files, running commands, editing code, fetching data. Agents report tool calls through `session/update` notifications, allowing clients to display real-time progress and results.

## Tool Call Lifecycle

### 1. Creating a Tool Call

When the LLM requests a tool invocation, the agent reports it:

```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123def456",
    "update": {
      "sessionUpdate": "tool_call",
      "toolCallId": "call_001",
      "title": "Reading configuration file",
      "kind": "read",
      "status": "pending"
    }
  }
}
```

Fields:
- **toolCallId** — Unique identifier within the session (required)
- **title** — Human-readable description of what the tool is doing (required)
- **kind** — Category: `read`, `edit`, `delete`, `move`, `search`, `execute`, `think`, `fetch`, `other`
- **status** — Current execution status (defaults to `pending`)
- **content** — Content produced by the tool call
- **locations** — File locations affected by this tool call
- **rawInput** — Raw input parameters sent to the tool
- **rawOutput** — Raw output returned by the tool

### 2. Updating Tool Call Status

As tools execute, agents send updates:

```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123def456",
    "update": {
      "sessionUpdate": "tool_call_update",
      "toolCallId": "call_001",
      "status": "in_progress",
      "content": [
        {
          "type": "content",
          "content": {
            "type": "text",
            "text": "Found 3 configuration files..."
          }
        }
      ]
    }
  }
}
```

All fields except `toolCallId` are optional in updates — only changed fields need to be included.

### Status Progression

Tool calls progress through statuses:
- `pending` → awaiting execution or permission
- `in_progress` → actively executing
- `completed` → finished successfully
- `failed` → execution failed
- `cancelled` → user cancelled

## Permission Requests

Agents may request user authorization before executing tool calls via `session/request_permission`:

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "session/request_permission",
  "params": {
    "sessionId": "sess_abc123def456",
    "toolCall": {
      "toolCallId": "call_001",
      "title": "Writing to config.py",
      "kind": "edit"
    }
  }
}
```

The client displays an approval/denial UI and responds with the permission result. The agent proceeds or aborts based on the response.

## Tool Call Content

Tool calls can produce structured content:

```json
{
  "content": [
    {
      "type": "content",
      "content": { "type": "text", "text": "Result output..." }
    },
    {
      "type": "diff",
      "diff": {
        "uri": "file:///path/to/file.py",
        "unidiff": "--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new"
      }
    }
  ]
}
```

Content types include text, diffs, and other structured data.

## Tool Call Locations

Agents can report which files are affected by tool calls:

```json
{
  "locations": [
    {
      "uri": "file:///path/to/file.py",
      "range": { "startLine": 10, "endLine": 15 }
    }
  ]
}
```

This allows clients to navigate to relevant files and highlight affected ranges.

## Following the Agent

Clients can use tool call locations and content to provide a rich UX:
- Show file diffs inline in the editor
- Navigate to affected files
- Display progress indicators based on tool kind
- Stream output in real-time as it becomes available

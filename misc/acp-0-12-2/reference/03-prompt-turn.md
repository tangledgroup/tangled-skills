# Prompt Turn Protocol

## Overview

A prompt turn is the core interaction cycle between client and agent. It starts with a user message and continues until the agent completes its response, potentially involving multiple LLM exchanges and tool invocations.

Before sending prompts, clients must complete initialization and session setup.

## Lifecycle

```
Client → Agent: session/prompt (user message)
  Agent processes with LLM
  loop until completion:
    Agent → Client: session/update (plan entries)
    Agent → Client: session/update (agent_message_chunk)
    opt tool calls:
      Agent → Client: session/update (tool_call)
      opt permission required:
        Agent → Client: session/request_permission
        Client → Agent: permission response
      Agent → Client: session/update (tool_call status updates)
    opt user cancels:
      Client → Agent: session/cancel
  Agent → Client: session/prompt response (stopReason)
```

## 1. User Message

The turn begins when the client sends `session/prompt`:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "session/prompt",
  "params": {
    "sessionId": "sess_abc123def456",
    "prompt": [
      {
        "type": "text",
        "text": "Can you analyze this code for potential issues?"
      },
      {
        "type": "resource",
        "resource": {
          "uri": "file:///home/user/project/main.py",
          "mimeType": "text/x-python",
          "text": "def process_data(items):\n    for item in items:\n        print(item)"
        }
      }
    ]
  }
}
```

Parameters:
- **sessionId** — The session to send the message to
- **prompt** — Array of content blocks (text, image, audio, resource)

Clients must restrict content types according to prompt capabilities established during initialization.

## 2. Agent Processing

The agent sends the user message to the LLM, which may respond with text content, tool calls, or both. The agent processes these responses and reports progress to the client.

## 3. Agent Reports Output

The agent reports output via `session/update` notifications:

### Plan Entries

The agent may share its plan for accomplishing the task:

```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123def456",
    "update": {
      "sessionUpdate": "plan",
      "entries": [
        {
          "content": "Check for syntax errors",
          "priority": "high",
          "status": "pending"
        },
        {
          "content": "Run linter on changed files",
          "priority": "medium",
          "status": "pending"
        }
      ]
    }
  }
}
```

### Agent Message Chunks

Text output from the LLM is streamed as chunks:

```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123def456",
    "update": {
      "sessionUpdate": "agent_message_chunk",
      "chunk": "I found two potential issues in the code..."
    }
  }
}
```

### Turn Completion

The turn ends when the agent sends the `session/prompt` response with a stop reason:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "stopReason": "end_turn"
  }
}
```

Stop reasons indicate why the turn ended (e.g., `end_turn` for normal completion, `cancelled` if the user cancelled).

## Cancellation

Clients can cancel an ongoing prompt turn:

```json
{
  "jsonrpc": "2.0",
  "method": "session/cancel",
  "params": {
    "sessionId": "sess_abc123def456"
  }
}
```

This is a notification (no response expected). The agent should abort its operations and return the prompt response with `stopReason: "cancelled"`.

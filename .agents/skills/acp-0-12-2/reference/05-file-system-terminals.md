# File System and Terminals

## Overview

The filesystem and terminal methods allow agents to interact with the client's environment — reading/writing text files and executing shell commands. These are client-provided capabilities that agents discover during initialization.

## Checking Support

Before using any filesystem or terminal methods, agents must verify support in the initialize response:

```json
{
  "result": {
    "clientCapabilities": {
      "fs": {
        "readTextFile": true,
        "writeTextFile": true
      },
      "terminal": true
    }
  }
}
```

If a capability is `false` or absent, the agent must not attempt the corresponding method.

## File System

### Reading Files

The `fs/read_text_file` method reads text file contents, including unsaved editor state:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "fs/read_text_file",
  "params": {
    "sessionId": "sess_abc123def456",
    "path": "/home/user/project/src/main.py",
    "line": 10,
    "limit": 50
  }
}
```

Parameters:
- **sessionId** — Session ID (required)
- **path** — Absolute path to the file (required)
- **line** — Starting line number, 1-based (optional)
- **limit** — Maximum lines to read (optional)

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": "def hello_world():\n    print('Hello, world!')\n"
  }
}
```

### Writing Files

The `fs/write_text_file` method writes or updates text files:

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "fs/write_text_file",
  "params": {
    "sessionId": "sess_abc123def456",
    "path": "/home/user/project/src/main.py",
    "content": "def hello_world():\n    print('Hello, updated!')\n"
  }
}
```

Parameters:
- **sessionId** — Session ID (required)
- **path** — Absolute path to the file (required)
- **content** — New file contents (required)

## Terminals

### Executing Commands

The `terminal/create` method starts a command in a new terminal:

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "terminal/create",
  "params": {
    "sessionId": "sess_abc123def456",
    "command": "npm",
    "args": ["test", "--coverage"],
    "env": [
      { "name": "NODE_ENV", "value": "test" }
    ],
    "cwd": "/home/user/project",
    "outputByteLimit": 1048576
  }
}
```

Parameters:
- **sessionId** — Session ID (required)
- **command** — Command to execute (required)
- **args** — Command arguments array (optional)
- **env** — Environment variables as `{name, value}` pairs (optional)
- **cwd** — Working directory absolute path (optional)
- **outputByteLimit** — Maximum output bytes to retain; earlier output truncated when exceeded (optional)

### Terminal Output Streaming

The client streams terminal output in real-time through `session/update` notifications with terminal-related update types, allowing agents to monitor command progress and react to output.

### Process Control

Clients may support terminating running terminal processes, providing agents with the ability to cancel long-running commands.

## Design Notes

- Filesystem methods access the **client's** environment — agents read/write through the client, not directly
- This allows clients to track all file modifications made during agent execution
- Unsaved editor buffer state is accessible through `fs/read_text_file`
- Terminal commands run in the client's shell environment with access to installed tools

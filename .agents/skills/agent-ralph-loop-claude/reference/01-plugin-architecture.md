# Plugin Architecture

## Directory Structure

The Ralph Loop plugin follows the Claude Code plugin file convention:

```
ralph-loop/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── commands/
│   ├── ralph-loop.md         # /ralph-loop slash command
│   ├── cancel-ralph.md       # /cancel-ralph slash command
│   └── help.md               # /help slash command
├── hooks/
│   ├── hooks.json            # Hook registration manifest
│   └── stop-hook.sh          # Stop hook implementation
├── scripts/
│   └── setup-ralph-loop.sh   # Setup script (called by ralph-loop command)
├── LICENSE
└── README.md
```

## Plugin Manifest

`.claude-plugin/plugin.json` defines the plugin identity:

```json
{
  "name": "ralph-loop",
  "version": "1.0.0",
  "description": "Continuous self-referential AI loops for interactive iterative development, implementing the Ralph Wiggum technique. Run Claude in a while-true loop with the same prompt until task completion.",
  "author": {
    "name": "Anthropic",
    "email": "support@anthropic.com"
  }
}
```

## Commands

Claude Code plugins define slash commands as markdown files in the `commands/` directory. Each file has YAML frontmatter with metadata and a body that instructs Claude on what to do.

### ralph-loop.md

The main command. Frontmatter specifies allowed tools:

```yaml
---
description: "Start Ralph Loop in current session"
argument-hint: "PROMPT [--max-iterations N] [--completion-promise TEXT]"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/setup-ralph-loop.sh:*)"]
hide-from-slash-command-tool: "true"
---
```

The body instructs Claude to execute the setup script with user-provided arguments, then begin working on the task. It includes a critical rule: if a completion promise is set, Claude may only output it when the statement is completely and unequivocally true.

### cancel-ralph.md

Cancels an active Ralph loop by removing `.claude/ralph-loop.local.md`. Frontmatter restricts tools to checking/removing the state file:

```yaml
---
description: "Cancel active Ralph Loop"
allowed-tools: ["Bash(test -f .claude/ralph-loop.local.md:*)", "Bash(rm .claude/ralph-loop.local.md)", "Read(.claude/ralph-loop.local.md)"]
hide-from-slash-command-tool: "true"
---
```

Steps:
1. Check if `.claude/ralph-loop.local.md` exists
2. If not found, report no active loop
3. If found, read the iteration number from frontmatter, remove the file, and report cancellation

### help.md

Explain Ralph Loop to the user — covers what it is, available commands, key concepts (completion promises, self-reference mechanism), examples, when to use it, and links to learn more.

## Hook Registration

`hooks/hooks.json` registers the Stop hook with Claude Code:

```json
{
  "description": "Ralph Loop plugin stop hook for self-referential loops",
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh\""
          }
        ]
      }
    ]
  }
}
```

The `Stop` hook fires whenever Claude Code attempts to end a session. The hook receives JSON input via stdin containing session metadata and transcript path.

## Environment Variables

- `${CLAUDE_PLUGIN_ROOT}` — Root directory of the installed plugin (used by commands and hooks)
- `${CLAUDE_CODE_SESSION_ID}` — Unique session identifier (injected by Claude Code, used for session isolation)

# Extensions API

## Contents
- Extension Basics and Locations
- Available Imports
- Writing an Extension
- Event System Overview
- Session Events
- Agent Events
- Tool Events
- Input Events
- Model Events
- Custom Tools
- Custom UI
- Commands, Shortcuts, Flags
- ExtensionContext API
- ExtensionCommandContext API
- ExtensionAPI Methods
- Pi Packages

## Extension Basics and Locations

Extensions are TypeScript modules that extend pi with custom tools, commands, event handlers, keyboard shortcuts, and UI components. Loaded via jiti — TypeScript works without compilation.

### Auto-Discovery Locations

| Location | Scope |
|----------|-------|
| `~/.pi/agent/extensions/*.ts` | Global (all projects) |
| `~/.pi/agent/extensions/*/index.ts` | Global (subdirectory) |
| `.pi/extensions/*.ts` | Project-local |
| `.pi/extensions/*/index.ts` | Project-local (subdirectory) |

Place extensions in auto-discovered locations for hot-reload via `/reload`. Use `pi -e ./path.ts` only for quick tests.

### Quick Start

Create `~/.pi/agent/extensions/my-extension.ts`:
```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.notify("Extension loaded!", "info");
  });

  pi.registerTool({
    name: "greet",
    label: "Greet",
    description: "Greet someone by name",
    parameters: Type.Object({
      name: Type.String({ description: "Name to greet" }),
    }),
    async execute(_toolCallId, params) {
      return { content: [{ type: "text", text: `Hello, ${params.name}!` }], details: {} };
    },
  });

  pi.registerCommand("hello", {
    description: "Say hello",
    handler: async (args, ctx) => {
      ctx.ui.notify(`Hello ${args || "world"}!`, "info");
    },
  });
}
```

### Async Factory Functions

Use async factory for one-time startup work (fetching remote config, discovering models):
```typescript
export default async function (pi: ExtensionAPI) {
  const response = await fetch("http://localhost:1234/v1/models");
  const payload = (await response.json()) as { data: Array<{ id: string }> };
  pi.registerProvider("local-openai", {
    baseUrl: "http://localhost:1234/v1",
    apiKey: "LOCAL_OPENAI_API_KEY",
    api: "openai-completions",
    models: payload.data.map((m) => ({
      id: m.id, name: m.id, reasoning: false, input: ["text"],
      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
      contextWindow: 128000, maxTokens: 4096,
    })),
  });
}
```

Async factories complete before `session_start`, before `resources_discover`, and before provider registrations are flushed.

### Extension Styles

- **Single file** — `~/.pi/agent/extensions/my-extension.ts`
- **Directory with index.ts** — `my-extension/index.ts` entry point with helper modules
- **Package with dependencies** — Add `package.json`, run `npm install`, import from `node_modules/`

## Available Imports

| Package | Purpose |
|---------|---------|
| `@earendil-works/pi-coding-agent` | Extension types (`ExtensionAPI`, `ExtensionContext`, events) |
| `typebox` | Schema definitions for tool parameters |
| `@earendil-works/pi-ai` | AI utilities (`StringEnum` for Google-compatible enums) |
| `@earendil-works/pi-tui` | TUI components for custom rendering |

Node.js built-ins (`node:fs`, `node:path`, etc.) and npm dependencies work too.

## Event System Overview

### Lifecycle Flow

```
pi starts
├─► session_start { reason: "startup" }
└─► resources_discover { reason: "startup" }
│
▼ user sends prompt
├─► (extension commands checked first)
├─► input (can intercept, transform, or handle)
├─► (skill/template expansion if not handled)
├─► before_agent_start (inject message, modify system prompt)
├─► agent_start
│   ┌─── turn (repeats while LLM calls tools) ───┐
│   │ ├─► turn_start                              │
│   │ ├─► context (modify messages)               │
│   │ ├─► before_provider_request                 │
│   │ ├─► after_provider_response                 │
│   │ │                                           │
│   │ │ LLM responds, may call tools:             │
│   │ │ ├─► tool_execution_start                  │
│   │ │ ├─► tool_call (can block)                 │
│   │ │ ├─► tool_execution_update                 │
│   │ │ ├─► tool_result (can modify)              │
│   │ │ └─► tool_execution_end                    │
│   │ └─► turn_end                                │
│   └─────────────────────────────────────────────┘
└─► agent_end
```

### Resource Events

#### resources_discover
Fired after `session_start`. Extensions contribute additional skill, prompt, and theme paths.
```typescript
pi.on("resources_discover", async (event, _ctx) => {
  return {
    skillPaths: ["/path/to/skills"],
    promptPaths: ["/path/to/prompts"],
    themePaths: ["/path/to/themes"],
  };
});
```

## Session Events

#### session_start
Fired when a session starts, loads, or reloads. `reason`: `"startup" | "reload" | "new" | "resume" | "fork"`.

#### session_before_switch
Fired before `/new` or `/resume`. Return `{ cancel: true }` to prevent.

#### session_before_fork
Fired on `/fork` or `/clone`. `event.entryId`, `event.position` (`"before"` for fork, `"at"` for clone).

#### session_before_compact / session_compact
Fired on compaction. Cancel with `{ cancel: true }` or provide custom summary.

#### session_before_tree / session_tree
Fired on `/tree` navigation. Cancel with `{ cancel: true }` or provide custom summary.

#### session_shutdown
Fired before extension runtime tears down. `reason`: `"quit" | "reload" | "new" | "resume" | "fork"`.

## Agent Events

#### before_agent_start
After user submits prompt, before agent loop. Can inject message and/or modify system prompt:
```typescript
pi.on("before_agent_start", async (event, ctx) => {
  return {
    message: { customType: "my-extension", content: "Additional context", display: true },
    systemPrompt: event.systemPrompt + "\n\nExtra instructions...",
  };
});
```

`event.systemPromptOptions` exposes structured data Pi uses to build the system prompt: `.customPrompt`, `.selectedTools`, `.toolSnippets`, `.promptGuidelines`, `.contextFiles`, `.skills`.

#### agent_start / agent_end
Fired once per user prompt.

#### turn_start / turn_end
Fired for each turn (one LLM response + tool calls).

#### message_start / message_update / message_end
- `message_start` and `message_end` fire for user, assistant, and toolResult messages
- `message_update` fires for assistant streaming updates
- `message_end` handlers can return `{ message }` to replace the finalized message (must keep same role)

#### context
Before each LLM call. Modify messages non-destructively:
```typescript
pi.on("context", async (event, ctx) => {
  const filtered = event.messages.filter(m => !shouldPrune(m));
  return { messages: filtered };
});
```

#### before_provider_request
After provider payload is built, before request is sent. Can inspect or replace payload.

#### after_provider_response
After HTTP response received, before stream body consumed. Access `event.status` and `event.headers`.

## Tool Events

#### tool_call
Fired after `tool_execution_start`, before tool executes. **Can block.** `event.input` is mutable — mutate in place to patch arguments:
```typescript
import { isToolCallEventType } from "@earendil-works/pi-coding-agent";

pi.on("tool_call", async (event, ctx) => {
  if (isToolCallEventType("bash", event)) {
    event.input.command = `source ~/.profile\n${event.input.command}`;
    if (event.input.command.includes("rm -rf")) {
      return { block: true, reason: "Dangerous command" };
    }
  }
});
```

#### tool_result
After tool execution finishes. **Can modify result.** Handlers chain like middleware:
```typescript
pi.on("tool_result", async (event, ctx) => {
  const response = await fetch("https://example.com/summarize", {
    method: "POST",
    body: JSON.stringify({ content: event.content }),
    signal: ctx.signal,
  });
  return { content: [...], details: {...}, isError: false };
});
```

#### user_bash
Fired on `!` or `!!` commands. Can intercept with custom operations (SSH) or full replacement.

## Input Events

#### input
Fired after extension commands checked, before skill/template expansion. Processing order:
1. Extension commands (`/cmd`) — if found, handler runs and input event skipped
2. `input` event — can intercept, transform, or handle
3. Skill commands (`/skill:name`) expanded
4. Prompt templates (`/template`) expanded
5. Agent processing begins

```typescript
pi.on("input", async (event, ctx) => {
  if (event.text.startsWith("?quick "))
    return { action: "transform", text: `Respond briefly: ${event.text.slice(7)}` };
  if (event.text === "ping") {
    ctx.ui.notify("pong", "info");
    return { action: "handled" };
  }
});
```

Results: `continue` (default), `transform` (modify then continue), `handled` (skip agent entirely).

## Model Events

#### model_select
Fired when model changes via `/model`, `Ctrl+P`, or session restore. `event.source`: `"set" | "cycle" | "restore"`.

#### thinking_level_select
Fired when thinking level changes. Notification-only; handler return values ignored.

## Custom Tools

Register tools callable by the LLM:
```typescript
import { Type } from "typebox";
import { StringEnum } from "@earendil-works/pi-ai";

pi.registerTool({
  name: "my_tool",
  label: "My Tool",
  description: "What this tool does",
  promptSnippet: "Summarize or transform text according to action",
  promptGuidelines: ["Use my_tool when the user asks to summarize previously generated text."],
  parameters: Type.Object({
    action: StringEnum(["list", "add"] as const),
    text: Type.Optional(Type.String()),
  }),
  async execute(toolCallId, params, signal, onUpdate, ctx) {
    onUpdate?.({ content: [{ type: "text", text: "Working..." }] });
    return { content: [{ type: "text", text: "Done" }], details: {} };
  },
  // Optional custom rendering
  renderCall(args, theme, context) { ... },
  renderResult(result, options, theme, context) { ... },
});
```

- `promptSnippet` — One-line entry in "Available tools" section of system prompt
- `promptGuidelines` — Bullets appended to "Guidelines" section (must name the tool explicitly)
- `prepareArguments(args)` — Optional compatibility shim before schema validation
- Tools registered during load or after startup (inside `session_start`, command handlers, etc.)
- Use `pi.setActiveTools()` to enable/disable tools at runtime

## Custom UI

### ctx.ui Methods

| Method | Description |
|--------|-------------|
| `ctx.ui.notify(text, level)` | Show notification (`"info"`, `"success"`, `"error"`, `"warning"`) |
| `ctx.ui.confirm(title, message)` | Yes/no confirmation dialog |
| `ctx.ui.select(title, items)` | Selection list |
| `ctx.ui.input(title, placeholder)` | Text input |
| `ctx.ui.editor(title, initialText)` | Multi-line editor |
| `ctx.ui.setStatus(key, text)` | Footer status line |
| `ctx.ui.setWidget(key, lines)` | Widget above editor |
| `ctx.ui.setTitle(text)` | Window title |
| `ctx.ui.custom(component)` | Full TUI component with keyboard input |

### Custom Message Rendering

Register renderer for custom message types:
```typescript
pi.registerMessageRenderer("my-type", {
  render: (msg, width, theme) => {
    return [`> ${msg.content}`];
  },
});
```

## Commands, Shortcuts, Flags

### Commands

```typescript
pi.registerCommand("stats", {
  description: "Show session statistics",
  getArgumentCompletions: (prefix): AutocompleteItem[] | null => {
    const envs = ["dev", "staging", "prod"];
    return envs.filter(e => e.startsWith(prefix)).map(e => ({ value: e, label: e }));
  },
  handler: async (args, ctx) => {
    const count = ctx.sessionManager.getEntries().length;
    ctx.ui.notify(`${count} entries`, "info");
  },
});
```

If multiple extensions register the same command name, pi assigns numeric suffixes (`/review:1`, `/review:2`).

### Shortcuts

```typescript
pi.registerShortcut("ctrl+shift+p", {
  description: "Toggle plan mode",
  handler: async (ctx) => {
    ctx.ui.notify("Toggled!", "info");
  },
});
```

### Flags

```typescript
pi.registerFlag("plan", {
  description: "Start in plan mode",
  type: "boolean",
  default: false,
});
if (pi.getFlag("plan")) { /* Plan mode enabled */ }
```

## ExtensionContext API

| Property | Description |
|----------|-------------|
| `ctx.ui` | UI methods for user interaction |
| `ctx.hasUI` | `false` in print/JSON mode, `true` in interactive/RPC mode |
| `ctx.cwd` | Current working directory |
| `ctx.sessionManager` | Read-only session state access |
| `ctx.modelRegistry` / `ctx.model` | Access to models and API keys |
| `ctx.signal` | Abort signal for nested async work (defined during active turns) |
| `ctx.isIdle()` | Check if agent is idle |
| `ctx.abort()` | Abort current operation |
| `ctx.hasPendingMessages()` | Check for queued messages |
| `ctx.shutdown()` | Request graceful shutdown |
| `ctx.getContextUsage()` | Current context usage for active model |
| `ctx.compact(options)` | Trigger compaction without awaiting |
| `ctx.getSystemPrompt()` | Pi's current system prompt string |

## ExtensionCommandContext API

Session control methods available only in commands (can deadlock from event handlers):

| Method | Description |
|--------|-------------|
| `ctx.waitForIdle()` | Wait for agent to finish streaming |
| `ctx.newSession(options?)` | Create new session with optional setup and post-switch work |
| `ctx.fork(entryId, options?)` | Fork from specific entry (`position: "before"` or `"at"`) |
| `ctx.navigateTree(targetId, options?)` | Navigate to different point in session tree |
| `ctx.switchSession(sessionPath, options?)` | Switch to different session file |
| `ctx.reload()` | Run same reload flow as `/reload` |

### Session Replacement Lifecycle

`withSession` receives a fresh `ReplacedSessionContext`. Old extension instance may have already run shutdown cleanup. Do not use captured old `pi` / command `ctx` for session-bound work — use only the `ctx` passed to `withSession`.

Safe pattern:
```typescript
await ctx.newSession({
  withSession: async (ctx) => {
    await ctx.sendUserMessage("Continue from replacement session");
  },
});
```

## ExtensionAPI Methods

| Method | Description |
|--------|-------------|
| `pi.on(event, handler)` | Subscribe to events |
| `pi.registerTool(definition)` | Register custom tool |
| `pi.sendMessage(message, options?)` | Inject custom message into session |
| `pi.sendUserMessage(content, options?)` | Send user message (always triggers turn) |
| `pi.appendEntry(customType, data?)` | Persist extension state (not in LLM context) |
| `pi.setSessionName(name)` / `pi.getSessionName()` | Set/get session display name |
| `pi.setLabel(entryId, label)` | Set/clear label on entry for bookmarking |
| `pi.registerCommand(name, options)` | Register slash command |
| `pi.getCommands()` | Get available commands (extensions, templates, skills) |
| `pi.registerMessageRenderer(customType, renderer)` | Register custom TUI renderer |
| `pi.registerShortcut(shortcut, options)` | Register keyboard shortcut |
| `pi.registerFlag(name, options)` | Register CLI flag |
| `pi.exec(command, args, options?)` | Execute shell command |
| `pi.getActiveTools()` / `pi.getAllTools()` / `pi.setActiveTools(names)` | Manage active tools |
| `pi.setModel(model)` | Set current model (returns false if no API key) |
| `pi.getThinkingLevel()` / `pi.setThinkingLevel(level)` | Get/set thinking level |
| `pi.events` | Shared event bus for inter-extension communication |
| `pi.registerProvider(name, config)` | Register or override model provider dynamically |

## Pi Packages

Bundle and share extensions, skills, prompts, and themes via npm or git:
```bash
pi install npm:@foo/pi-tools
pi install git:github.com/user/repo
pi remove npm:@foo/pi-tools
pi list
pi update --extensions   # Update packages only
pi config                # Enable/disable package resources
```

Packages install to `~/.pi/agent/git/` (git) or global npm. Use `-l` for project-local installs.

Create a package by adding `pi` key to `package.json`:
```json
{
  "name": "my-pi-package",
  "keywords": ["pi-package"],
  "pi": {
    "extensions": ["./extensions"],
    "skills": ["./skills"],
    "prompts": ["./prompts"],
    "themes": ["./themes"]
  }
}
```

Without a `pi` manifest, pi auto-discovers from conventional directories. Runtime deps must be in `dependencies` (not `devDependencies`).

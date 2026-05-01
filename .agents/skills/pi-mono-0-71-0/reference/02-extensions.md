# Extensions System

Extensions are TypeScript modules that extend pi with custom tools, commands, keyboard shortcuts, event handlers, and UI components. The default export receives `ExtensionAPI` (`pi`) and can also be `async`.

## Extension Factory

```typescript
export default function (pi: ExtensionAPI) {
  pi.registerTool({ name: "my_tool", ... });
  pi.registerCommand("stats", { handler: async (args, ctx) => { ... } });
  pi.on("tool_call", async (event, ctx) => { ... });
}

// Async factory — pi waits before startup continues
export default async function (pi: ExtensionAPI) {
  const models = await fetchRemoteModels();
  pi.registerProvider("my-proxy", { baseUrl: "...", models });
}
```

## Loading Locations

Extensions load from (in priority order):

- Global: `~/.pi/agent/extensions/`
- Project: `.pi/extensions/`
- Packages: `extensions/` directories or `pi.extensions` in `package.json`
- Settings: `extensions` array
- CLI: `-e ./path.ts` (repeatable, temporary for current run)
- SDK: `DefaultResourceLoader` with `extensionFactories`

Disable discovery with `--no-extensions`.

## Registering Tools

Tools appear in the system prompt and can have custom rendering. Use `defineTool()` for standalone definitions or inline `pi.registerTool()`.

```typescript
import { Type } from "typebox";
import { StringEnum } from "@mariozechner/pi-ai";
import { defineTool, type ExtensionAPI } from "@mariozechner/pi-coding-agent";

pi.registerTool({
  name: "my_tool",
  label: "My Tool",
  description: "What this tool does (shown to LLM)",
  promptSnippet: "Short one-line entry for Available tools section",
  promptGuidelines: [
    "Use my_tool when the user asks about X.",
  ],
  parameters: Type.Object({
    action: StringEnum(["list", "add"] as const),
    text: Type.Optional(Type.String()),
  }),

  async execute(toolCallId, params, signal, onUpdate, ctx) {
    if (signal?.aborted) {
      return { content: [{ type: "text", text: "Cancelled" }] };
    }

    onUpdate?.({
      content: [{ type: "text", text: "Working..." }],
      details: { progress: 50 },
    });

    return {
      content: [{ type: "text", text: "Done" }],
      details: { data: "result" },
    };
  },

  // Optional custom rendering
  renderCall(args, theme, context) { ... },
  renderResult(result, options, theme, context) { ... },
});
```

### Key Tool Concepts

- **StringEnum**: Use `StringEnum` from `@mariozechner/pi-ai` for enums — `Type.Union`/`Type.Literal` doesn't work with Google's API
- **prepareArguments**: Transform args before schema validation (for backward compatibility with old session data)
- **terminate**: Return `terminate: true` to hint that automatic follow-up LLM call should be skipped (only when every tool in batch terminates)
- **Errors**: Throw from `execute()` to signal failure — returning a value never sets `isError: true`
- **@ prefix normalization**: Strip leading `@` from path arguments (some models include it)

### File Mutation Queue

If your custom tool mutates files, use `withFileMutationQueue()` to participate in the same per-file queue as built-in `edit` and `write`:

```typescript
import { withFileMutationQueue } from "@mariozechner/pi-coding-agent";

async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
  const absolutePath = resolve(ctx.cwd, params.path);
  return withFileMutationQueue(absolutePath, async () => {
    // read-modify-write logic here
    return { content: [{ type: "text", text: "Updated" }], details: {} };
  });
}
```

Pass the real absolute path. For existing files, it canonicalizes through `realpath()` so symlink aliases share one queue. Queue the entire mutation window, not just the write.

### Overriding Built-in Tools

Register a tool with the same name as a built-in (`read`, `bash`, `edit`, `write`, `grep`, `find`, `ls`) to override it. Rendering inherits per-slot — omit `renderCall` and the built-in renderer is used. `promptSnippet` and `promptGuidelines` are not inherited.

### Output Truncation

Tools MUST truncate output (default: 50KB / 2000 lines):

```typescript
import { truncateHead, DEFAULT_MAX_BYTES, DEFAULT_MAX_LINES, formatSize } from "@mariozechner/pi-coding-agent";

const truncation = truncateHead(output, { maxLines: DEFAULT_MAX_LINES, maxBytes: DEFAULT_MAX_BYTES });
if (truncation.truncated) {
  result += `\n[Output truncated: ${truncation.outputLines} of ${truncation.totalLines} lines]`;
}
```

Use `truncateHead` for content where the beginning matters (search results, file reads). Use `truncateTail` for logs and command output.

### Remote Execution

Built-in tools support pluggable operations for SSH, containers, etc.:

```typescript
import { createReadTool } from "@mariozechner/pi-coding-agent";

const remoteRead = createReadTool(cwd, {
  operations: {
    readFile: (path) => sshExec(remote, `cat ${path}`),
    access: (path) => sshExec(remote, `test -r ${path}`).then(() => {}),
  }
});
```

For bash, use a spawn hook to adjust command, cwd, or env before execution:

```typescript
import { createBashTool } from "@mariozechner/pi-coding-agent";

const bashTool = createBashTool(cwd, {
  spawnHook: ({ command, cwd, env }) => ({
    command: `source ~/.profile\n${command}`,
    cwd: `/mnt/sandbox${cwd}`,
    env: { ...env, CI: "1" },
  }),
});
```

## Registering Commands

```typescript
pi.registerCommand("stats", {
  description: "Show session statistics",
  handler: async (args, ctx) => {
    const count = ctx.sessionManager.getEntries().length;
    ctx.ui.notify(`${count} entries`, "info");
  },
});

// With argument completions
pi.registerCommand("deploy", {
  description: "Deploy to an environment",
  getArgumentCompletions: (prefix): AutocompleteItem[] | null => {
    return ["dev", "staging", "prod"]
      .filter(e => e.startsWith(prefix))
      .map(e => ({ value: e, label: e }));
  },
  handler: async (args, ctx) => { ... },
});
```

Multiple extensions can register the same command name — pi assigns numeric suffixes (`/review:1`, `/review:2`).

## Event Hooks

Subscribe to events via `pi.on()`. Key event types:

### Tool & Agent Events

- `tool_call` — Before tool execution. Return `{ block: true, reason }` to block.
- `before_agent_start` — Before agent starts processing. Modify system prompt options.
- `agent_start` / `agent_end` — Agent lifecycle
- `turn_start` / `turn_end` — Turn lifecycle (one LLM response + tool calls)

### Session Events

- `session_start` — Session loaded/created
- `session_shutdown` — Session ending
- `session_before_compact` — Before compaction. Cancel or provide custom summary.
- `session_before_tree` — Before tree navigation. Cancel or provide custom summary.
- `session_tree` — After tree navigation
- `session_before_switch` — Before session switch
- `session_before_fork` — Before fork

### Input & Model Events

- `input` — Transform user input before sending
- `model_select` — React to model changes
- `thinking_level_select` — Observe thinking level changes (new in 0.71.0)
- `before_provider_request` / `after_provider_response` — Inspect payloads and headers
- `message_start` / `message_update` / `message_end` — Message lifecycle; `message_end` results can replace finalized messages (new in 0.71.0)

```typescript
// Block dangerous bash commands
pi.on("tool_call", async (event, ctx) => {
  if (event.toolName !== "bash") return;
  const command = event.input.command as string;
  if (command.match(/\brm\s+-rf/)) {
    return { block: true, reason: "Dangerous command blocked" };
  }
});

// Custom compaction
pi.on("session_before_compact", async (event, ctx) => {
  const { preparation } = event;
  return { cancel: true }; // or provide custom summary
});

// Transform input
pi.on("input", async (event) => {
  return { message: event.message.replace(/trigger/, "replacement") };
});
```

## State Management

Store state in tool result `details` for proper branching support:

```typescript
let items: string[] = [];

pi.on("session_start", async (_event, ctx) => {
  items = [];
  for (const entry of ctx.sessionManager.getBranch()) {
    if (entry.type === "message" && entry.message.role === "toolResult") {
      if (entry.message.toolName === "my_tool") {
        items = entry.message.details?.items ?? [];
      }
    }
  }
});

pi.registerTool({
  name: "my_tool",
  // ...
  async execute(toolCallId, params, signal, onUpdate, ctx) {
    items.push("new item");
    return {
      content: [{ type: "text", text: "Added" }],
      details: { items: [...items] },
    };
  },
});
```

Persist extension state with `pi.appendEntry()`:

```typescript
pi.appendEntry("my-state", { count: 42 });

// Restore on reload
pi.on("session_start", async (_event, ctx) => {
  for (const entry of ctx.sessionManager.getEntries()) {
    if (entry.type === "custom" && entry.customType === "my-state") {
      // Reconstruct from entry.data
    }
  }
});
```

## Custom UI

### Dialogs

```typescript
const choice = await ctx.ui.select("Pick one:", ["A", "B", "C"]);
const ok = await ctx.ui.confirm("Delete?", "This cannot be undone");
const name = await ctx.ui.input("Name:", "placeholder");
const text = await ctx.ui.editor("Edit:", "prefilled text");
ctx.ui.notify("Done!", "info"); // "info" | "warning" | "error"
```

Timed dialogs with countdown:

```typescript
const confirmed = await ctx.ui.confirm("Title", "Message", { timeout: 5000 });
```

### Widgets, Status, Footer

```typescript
ctx.ui.setStatus("my-ext", "Processing...");
ctx.ui.setWidget("my-widget", ["Line 1", "Line 2"]);
ctx.ui.setWidget("my-widget", ["Line 1"], { placement: "belowEditor" });
ctx.ui.setFooter((tui, theme, footerData) => ({
  render(width) { return [theme.fg("dim", "Custom")]; },
  invalidate() {},
}));
```

### Custom Components

```typescript
const result = await ctx.ui.custom<boolean>((tui, theme, keybindings, done) => {
  const text = new Text("Press Enter to confirm", 1, 1);
  text.onKey = (key) => {
    if (key === "return") done(true);
    if (key === "escape") done(false);
    return true;
  };
  return text;
});
```

Overlay mode (experimental):

```typescript
const result = await ctx.ui.custom<string | null>(
  (tui, theme, keybindings, done) => new MyOverlay({ onClose: done }),
  { overlay: true, overlayOptions: { anchor: "top-right", width: "50%" } }
);
```

### Autocomplete Providers

```typescript
ctx.ui.addAutocompleteProvider((current) => ({
  async getSuggestions(lines, line, col, options) {
    const beforeCursor = (lines[line] ?? "").slice(0, col);
    const match = beforeCursor.match(/(?:^|[ \t])#([^\s#]*)$/);
    if (!match) return current.getSuggestions(lines, line, col, options);
    return {
      prefix: `#${match[1] ?? ""}`,
      items: [{ value: "#2983", label: "#2983", description: "Issue" }],
    };
  },
  applyCompletion(lines, line, col, item, prefix) {
    return current.applyCompletion(lines, line, col, item, prefix);
  },
}));
```

## Registering Providers

New in 0.71.0: `name` field for friendly display in `/login`, and `oauth` config.

```typescript
pi.registerProvider("my-proxy", {
  name: "My Proxy",           // Display name in /login (new in 0.71.0)
  baseUrl: "https://proxy.example.com",
  apiKey: "PROXY_API_KEY",
  api: "anthropic-messages",
  models: [{ id: "model-id", reasoning: false, input: ["text"], cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }, contextWindow: 200000, maxTokens: 16384 }],
});

// Override baseUrl only (keeps all models)
pi.registerProvider("anthropic", { baseUrl: "https://proxy.example.com" });

// With OAuth support for /login (new in 0.71.0)
pi.registerProvider("corporate-ai", {
  name: "Corporate AI (SSO)",
  baseUrl: "https://ai.corp.com",
  api: "openai-responses",
  models: [...],
  oauth: {
    name: "Corporate AI (SSO)",
    async login(callbacks) {
      callbacks.onAuth({ url: "https://sso.corp.com/..." });
      const code = await callbacks.onPrompt({ message: "Enter code:" });
      return { refresh: code, access: code, expires: Date.now() + 3600000 };
    },
    async refreshToken(credentials) { return credentials; },
    getApiKey(credentials) { return credentials.access; },
  },
});
```

## Utility APIs

- `pi.exec(command, args, options?)` — Execute shell command
- `pi.getActiveTools()` / `pi.getAllTools()` / `pi.setActiveTools(names)` — Manage active tools
- `pi.setModel(model)` — Switch model
- `pi.getThinkingLevel()` / `pi.setThinkingLevel(level)` — Thinking level
- `pi.sendMessage({ customType, content, display, details })` — Send extension messages
- `pi.sendUserMessage(content, options?)` — Inject user messages
- `pi.registerMessageRenderer(customType, renderer)` — Custom message rendering
- `pi.registerShortcut(shortcut, options)` — Keyboard shortcuts
- `pi.registerFlag(name, options)` — CLI flags
- `pi.setSessionName(name)` / `pi.getSessionName()` — Session display name
- `pi.setLabel(entryId, label)` — Bookmark entries for `/tree`
- `pi.events.on("my:event", handler)` / `pi.events.emit("my:event", data)` — Inter-extension event bus
- `pi.unregisterProvider(name)` — Remove a registered provider
- `pi.getCommands()` — Get slash commands available in current session (new in 0.71.0)
- `ctx.ui.getEditorComponent()` — Access currently configured custom editor factory (new in 0.71.0)
- `ctx.ui.pasteToEditor(content)` — Paste into editor with paste handling (new in 0.71.0)
- `ctx.ui.setWorkingVisible(bool)` — Show/hide built-in working loader row (new in 0.71.0)
- `ctx.ui.setWorkingIndicator(frames)` — Customize streaming working indicator (new in 0.71.0)
- `ctx.ui.getToolsExpanded()` / `ctx.ui.setToolsExpanded(bool)` — Tool output expansion state (new in 0.71.0)

## Mode Behavior

| Mode | UI Methods | Notes |
|------|-----------|-------|
| Interactive | Full TUI | Normal operation |
| RPC | JSON protocol | Host handles UI, dialogs via extension_ui_request |
| JSON | No-op | Event stream to stdout |
| Print | No-op | Extensions run but can't prompt |

Check `ctx.hasUI` before using UI methods in non-interactive modes.

# SDK and RPC

## SDK Overview

The SDK provides programmatic access to pi's agent capabilities via `@mariozechner/pi-coding-agent`. Use it to embed pi in other applications, build custom interfaces, or integrate with automated workflows.

### Quick Start

```typescript
import { AuthStorage, createAgentSession, ModelRegistry, SessionManager } from "@mariozechner/pi-coding-agent";

const authStorage = AuthStorage.create();
const modelRegistry = ModelRegistry.create(authStorage);

const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),
  authStorage,
  modelRegistry,
});

session.subscribe((event) => {
  if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
});

await session.prompt("What files are in the current directory?");
```

### createAgentSession()

The main factory function. Uses `DefaultResourceLoader` for extension/skill/prompt/theme/context-file discovery when no custom loader is provided.

```typescript
const { session } = await createAgentSession({
  model: myModel,
  thinkingLevel: "medium",
  tools: [readTool, bashTool],
  customTools: [myCustomTool],
  sessionManager: SessionManager.create(process.cwd()),
  resourceLoader: loader,
  settingsManager: SettingsManager.create(),
});
```

Returns `{ session, extensionsResult, modelFallbackMessage? }`.

### AgentSession

```typescript
interface AgentSession {
  prompt(text: string, options?: PromptOptions): Promise<void>;
  steer(text: string): Promise<void>;
  followUp(text: string): Promise<void>;
  subscribe(listener: (event: AgentSessionEvent) => void): () => void;
  setModel(model: Model): Promise<void>;
  setThinkingLevel(level: ThinkingLevel): void;
  navigateTree(targetId: string, options?): Promise<{ editorText?: string; cancelled: boolean }>;
  compact(customInstructions?: string): Promise<CompactionResult>;
  abort(): Promise<void>;
  dispose(): void;

  // State access
  agent: Agent;
  model: Model | undefined;
  thinkingLevel: ThinkingLevel;
  messages: AgentMessage[];
  isStreaming: boolean;
  sessionId: string;
  sessionFile: string | undefined;
}
```

### createAgentSessionRuntime()

Use the runtime API for session replacement (new, fork, clone, switch):

```typescript
const createRuntime: CreateAgentSessionRuntimeFactory = async ({ cwd, sessionManager, sessionStartEvent }) => {
  const services = await createAgentSessionServices({ cwd });
  return {
    ...(await createAgentSessionFromServices({ services, sessionManager, sessionStartEvent })),
    services,
    diagnostics: services.diagnostics,
  };
};

const runtime = await createAgentSessionRuntime(createRuntime, {
  cwd: process.cwd(),
  agentDir: getAgentDir(),
  sessionManager: SessionManager.create(process.cwd()),
});

await runtime.newSession();
await runtime.switchSession("/path/to/session.jsonl");
await runtime.fork("entry-id");
```

After replacement, `runtime.session` changes — re-subscribe to events and re-bind extensions.

### Prompting

```typescript
// Basic prompt
await session.prompt("What files are here?");

// With images
await session.prompt("What's in this image?", {
  images: [{ type: "image", source: { type: "base64", mediaType: "image/png", data: "..." } }]
});

// During streaming
await session.prompt("Stop and do this instead", { streamingBehavior: "steer" });
await session.prompt("After you're done, also check X", { streamingBehavior: "followUp" });

// Explicit queueing
await session.steer("New instruction");
await session.followUp("After you're done");
```

### Agent State Access

```typescript
const state = session.agent.state;
state.messages  // conversation history
state.model     // current model
state.thinkingLevel
state.systemPrompt
state.tools
state.streamingMessage?
state.errorMessage?

// Replace messages or tools
session.agent.state.messages = messages;
session.agent.state.tools = tools;

// Wait for agent to finish
await session.agent.waitForIdle();
```

### Events

```typescript
session.subscribe((event) => {
  switch (event.type) {
    case "message_update":
      if (event.assistantMessageEvent.type === "text_delta") {
        process.stdout.write(event.assistantMessageEvent.delta);
      }
      break;
    case "tool_execution_start":
      console.log(`Tool: ${event.toolName}`);
      break;
    case "tool_execution_end":
      console.log(`Result: ${event.isError ? "error" : "success"}`);
      break;
    case "agent_start": break;
    case "agent_end":
      // event.messages contains all new messages
      break;
    case "turn_start": break;
    case "turn_end":
      // event.message: assistant response
      // event.toolResults: tool results from this turn
      break;
    case "compaction_start":
    case "compaction_end":
    case "auto_retry_start":
    case "auto_retry_end":
      break;
  }
});
```

### Tools via SDK

```typescript
import { codingTools, readOnlyTools, readTool, bashTool, editTool, writeTool } from "@mariozechner/pi-coding-agent";

// Use built-in tool sets
const { session } = await createAgentSession({ tools: readOnlyTools });

// Custom cwd — use factory functions
const cwd = "/path/to/project";
const { session } = await createAgentSession({
  cwd,
  tools: createCodingTools(cwd),  // [read, bash, edit, write] for specific cwd
});

// Custom tool
import { defineTool } from "@mariozechner/pi-coding-agent";
import { Type } from "typebox";

const myTool = defineTool({
  name: "my_tool",
  label: "My Tool",
  description: "Does something useful",
  parameters: Type.Object({ input: Type.String() }),
  execute: async (_id, params) => ({
    content: [{ type: "text", text: `Result: ${params.input}` }],
    details: {},
  }),
});

const { session } = await createAgentSession({ customTools: [myTool] });
```

### Extensions via SDK

```typescript
import { DefaultResourceLoader } from "@mariozechner/pi-coding-agent";

const loader = new DefaultResourceLoader({
  additionalExtensionPaths: ["/path/to/my-extension.ts"],
  extensionFactories: [(pi) => { pi.on("agent_start", () => console.log("Starting")); }],
});
await loader.reload();
const { session } = await createAgentSession({ resourceLoader: loader });
```

### Skills via SDK

```typescript
const customSkill: Skill = {
  name: "my-skill",
  description: "Custom instructions",
  filePath: "/path/to/SKILL.md",
  baseDir: "/path/to",
  source: "custom",
};

const loader = new DefaultResourceLoader({
  skillsOverride: (current) => ({ skills: [...current.skills, customSkill], diagnostics: current.diagnostics }),
});
await loader.reload();
```

### Settings via SDK

```typescript
import { SettingsManager } from "@mariozechner/pi-coding-agent";

// From files (global + project merged)
const { session } = await createAgentSession({ settingsManager: SettingsManager.create() });

// With overrides
const sm = SettingsManager.create();
sm.applyOverrides({ compaction: { enabled: false } });

// In-memory (no file I/O)
const { session } = await createAgentSession({
  settingsManager: SettingsManager.inMemory({ compaction: { enabled: false } }),
  sessionManager: SessionManager.inMemory(),
});
```

### Auth & Models via SDK

```typescript
import { getModel } from "@mariozechner/pi-ai";
import { AuthStorage, ModelRegistry } from "@mariozechner/pi-coding-agent";

const authStorage = AuthStorage.create();
const modelRegistry = ModelRegistry.create(authStorage);

// Runtime API key override (not persisted)
authStorage.setRuntimeApiKey("anthropic", process.env.MY_KEY!);

// Find model
const opus = getModel("anthropic", "claude-opus-4-5");
const customModel = modelRegistry.find("my-provider", "my-model");
const available = await modelRegistry.getAvailable();

const { session } = await createAgentSession({
  model: opus,
  authStorage,
  modelRegistry,
});
```

### Run Modes

```typescript
// Interactive mode (full TUI)
import { InteractiveMode } from "@mariozechner/pi-coding-agent";
const mode = new InteractiveMode(runtime, { initialMessage: "Hello" });
await mode.run();

// Print mode (single-shot)
import { runPrintMode } from "@mariozechner/pi-coding-agent";
await runPrintMode(runtime, { mode: "text", initialMessage: "Hello" });

// RPC mode
import { runRpcMode } from "@mariozechner/pi-coding-agent";
await runRpcMode(runtime);
```

## RPC Mode

For non-Node.js integrations, use `pi --mode rpc`. JSON protocol over stdin/stdout with strict LF-delimited JSONL framing.

### Starting

```bash
pi --mode rpc --no-session
```

### Commands (stdin)

```json
{"type": "prompt", "message": "Hello!"}
{"type": "steer", "message": "New instruction"}
{"type": "follow_up", "message": "After you're done"}
{"type": "abort"}
{"type": "get_state"}
{"type": "get_messages"}
{"type": "set_model", "provider": "anthropic", "modelId": "claude-sonnet-4-20250514"}
{"type": "set_thinking_level", "level": "high"}
{"type": "compact"}
{"type": "new_session"}
{"type": "fork", "entryId": "abc123"}
{"type": "clone"}
{"type": "bash", "command": "ls -la"}
{"type": "get_session_stats"}
{"type": "get_commands"}
```

During streaming, `prompt` requires `streamingBehavior`: `"steer"` or `"followUp"`.

### Responses (stdout)

```json
{"type": "response", "command": "prompt", "success": true}
{"type": "response", "command": "get_state", "success": true, "data": {"model": {...}, "isStreaming": false}}
```

### Events (stdout)

Streamed as JSON lines: `agent_start`, `agent_end`, `turn_start`, `turn_end`, `message_start`, `message_update`, `message_end`, `tool_execution_start`, `tool_execution_update`, `tool_execution_end`, `queue_update`, `compaction_start`, `compaction_end`, `auto_retry_start`, `auto_retry_end`, `extension_error`.

### Extension UI Protocol

In RPC mode, extension dialogs become request/response on stdin/stdout:

```json
// Request (stdout)
{"type": "extension_ui_request", "id": "uuid-1", "method": "select", "title": "Allow?", "options": ["Yes", "No"]}

// Response (stdin)
{"type": "extension_ui_response", "id": "uuid-1", "value": "Yes"}
```

Fire-and-forget methods: `notify`, `setStatus`, `setWidget`, `setTitle`, `set_editor_text`.

### Python Client Example

```python
import subprocess, json

proc = subprocess.Popen(["pi", "--mode", "rpc", "--no-session"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

def send(cmd):
    proc.stdin.write(json.dumps(cmd) + "\n")
    proc.stdin.flush()

send({"type": "prompt", "message": "Hello!"})

for line in proc.stdout:
    event = json.loads(line)
    if event.get("type") == "message_update":
        delta = event.get("assistantMessageEvent", {})
        if delta.get("type") == "text_delta":
            print(delta["delta"], end="", flush=True)
    if event.get("type") == "agent_end":
        print()
        break
```

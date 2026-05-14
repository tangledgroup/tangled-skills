# SDK and Integration

## Contents
- createAgentSession()
- AgentSession API
- createAgentSessionRuntime()
- Prompting and Message Queueing
- Model Configuration
- API Keys and OAuth
- Tools (Built-in, Custom, Factory)
- Extensions via ResourceLoader
- Skills, Context Files, Prompt Templates
- Session Management
- Settings Management
- Run Modes (Interactive, Print, RPC)
- pi-web-ui Components

## createAgentSession()

Main factory for a single `AgentSession`. Uses `ResourceLoader` to supply extensions, skills, prompt templates, themes, and context files. Defaults to `DefaultResourceLoader` with standard discovery.

```typescript
import { AuthStorage, createAgentSession, ModelRegistry, SessionManager } from "@earendil-works/pi-coding-agent";

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

## AgentSession API

| Method | Description |
|--------|-------------|
| `prompt(text, options?)` | Send prompt and wait for completion |
| `steer(text)` | Queue steering message during streaming |
| `followUp(text)` | Queue follow-up message (delivered when agent stops) |
| `subscribe(listener)` | Subscribe to events (returns unsubscribe function) |
| `setModel(model)` | Change model |
| `setThinkingLevel(level)` | Change thinking level |
| `cycleModel()` | Cycle to next scoped model |
| `cycleThinkingLevel()` | Cycle to next thinking level |
| `navigateTree(targetId, options?)` | In-place tree navigation |
| `compact(customInstructions?)` | Trigger compaction |
| `abortCompaction()` | Abort in-progress compaction |
| `abort()` | Abort current operation |
| `dispose()` | Cleanup |

Properties: `sessionFile`, `sessionId`, `agent`, `model`, `thinkingLevel`, `messages`, `isStreaming`.

Session replacement APIs (new-session, resume, fork, import) live on `AgentSessionRuntime`, not `AgentSession`.

## createAgentSessionRuntime()

Use the runtime API when you need to replace the active session and rebuild cwd-bound runtime state. Same layer used by built-in interactive, print, and RPC modes.

```typescript
import {
  type CreateAgentSessionRuntimeFactory,
  createAgentSessionFromServices,
  createAgentSessionRuntime,
  createAgentSessionServices,
  getAgentDir,
  SessionManager,
} from "@earendil-works/pi-coding-agent";

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

// Replace active session
await runtime.newSession();
await runtime.switchSession("/path/to/session.jsonl");
await runtime.fork("entry-id");
await runtime.fork("entry-id", { position: "at" }); // clone
```

After replacement: `runtime.session` changes, re-subscribe to events, call `runtime.session.bindExtensions(...)` for extensions.

## Prompting and Message Queueing

```typescript
interface PromptOptions {
  expandPromptTemplates?: boolean;
  images?: ImageContent[];
  streamingBehavior?: "steer" | "followUp";
  source?: InputSource;
  preflightResult?: (success: boolean) => void;
}
```

- Extension commands (`/mycommand`): Execute immediately, even during streaming
- File-based prompt templates: Expanded to content before sending
- During streaming without `streamingBehavior`: Throws error. Use `steer()` or `followUp()` directly.

## Model Configuration

```typescript
import { getModel } from "@earendil-works/pi-ai";
import { AuthStorage, ModelRegistry } from "@earendil-works/pi-coding-agent";

const authStorage = AuthStorage.create();
const modelRegistry = ModelRegistry.create(authStorage);

// Find built-in model
const opus = getModel("anthropic", "claude-opus-4-5");

// Find custom model from models.json
const customModel = modelRegistry.find("my-provider", "my-model");

// Get only models with valid API keys
const available = await modelRegistry.getAvailable();

const { session } = await createAgentSession({
  model: opus,
  thinkingLevel: "medium",
  scopedModels: [
    { model: opus, thinkingLevel: "high" },
    { model: haiku, thinkingLevel: "off" },
  ],
  authStorage,
  modelRegistry,
});
```

If no model provided: tries session restore → settings default → first available.

## API Keys and OAuth

Resolution priority: runtime overrides → stored credentials (`auth.json`) → environment variables → fallback resolver.

```typescript
const authStorage = AuthStorage.create();
// Runtime override (not persisted)
authStorage.setRuntimeApiKey("anthropic", "sk-my-temp-key");

// Custom locations
const customAuth = AuthStorage.create("/my/app/auth.json");
const customRegistry = ModelRegistry.create(customAuth, "/my/app/models.json");
```

## Tools

### Built-in Tool Sets

```typescript
import {
  codingTools,    // read, bash, edit, write (default)
  readOnlyTools,  // read, grep, find, ls
  readTool, bashTool, editTool, writeTool,
  grepTool, findTool, lsTool,
} from "@earendil-works/pi-coding-agent";

const { session } = await createAgentSession({ tools: readOnlyTools });
```

### Tool Factories (for custom cwd)

Pre-built tool instances use `process.cwd()`. When specifying custom `cwd` AND explicit `tools`, use factory functions:

```typescript
import { createCodingTools, createReadTool, createBashTool } from "@earendil-works/pi-coding-agent";

const cwd = "/path/to/project";
const { session } = await createAgentSession({
  cwd,
  tools: createCodingTools(cwd),
});
```

### Custom Tools

```typescript
import { Type } from "typebox";
import { defineTool } from "@earendil-works/pi-coding-agent";

const myTool = defineTool({
  name: "my_tool",
  label: "My Tool",
  description: "Does something useful",
  parameters: Type.Object({
    input: Type.String({ description: "Input value" }),
  }),
  execute: async (_toolCallId, params) => ({
    content: [{ type: "text", text: `Result: ${params.input}` }],
    details: {},
  }),
});

const { session } = await createAgentSession({ customTools: [myTool] });
```

Use `defineTool()` for standalone definitions. Inline `pi.registerTool({...})` already infers parameter types correctly.

## Extensions via ResourceLoader

```typescript
import { createAgentSession, DefaultResourceLoader } from "@earendil-works/pi-coding-agent";

const loader = new DefaultResourceLoader({
  additionalExtensionPaths: ["/path/to/my-extension.ts"],
  extensionFactories: [
    (pi) => {
      pi.on("agent_start", () => console.log("[Inline Extension] Agent starting"));
    },
  ],
});
await loader.reload();
const { session } = await createAgentSession({ resourceLoader: loader });
```

### Event Bus (inter-extension communication)

```typescript
import { createEventBus, DefaultResourceLoader } from "@earendil-works/pi-coding-agent";

const eventBus = createEventBus();
const loader = new DefaultResourceLoader({ eventBus });
await loader.reload();
eventBus.on("my-extension:status", (data) => console.log(data));
```

## Skills, Context Files, Prompt Templates

### Skills

```typescript
import { createAgentSession, DefaultResourceLoader, type Skill } from "@earendil-works/pi-coding-agent";

const customSkill: Skill = {
  name: "my-skill",
  description: "Custom instructions",
  filePath: "/path/to/SKILL.md",
  baseDir: "/path/to",
  source: "custom",
};

const loader = new DefaultResourceLoader({
  skillsOverride: (current) => ({
    skills: [...current.skills, customSkill],
    diagnostics: current.diagnostics,
  }),
});
await loader.reload();
```

### Context Files

```typescript
const loader = new DefaultResourceLoader({
  agentsFilesOverride: (current) => ({
    agentsFiles: [
      ...current.agentsFiles,
      { path: "/virtual/AGENTS.md", content: "# Guidelines\n\n- Be concise" },
    ],
  }),
});
```

### Prompt Templates (Slash Commands)

```typescript
import { createAgentSession, DefaultResourceLoader, type PromptTemplate } from "@earendil-works/pi-coding-agent";

const customCommand: PromptTemplate = {
  name: "deploy",
  description: "Deploy the application",
  source: "(custom)",
  content: "# Deploy\n\n1. Build\n2. Test\n3. Deploy",
};

const loader = new DefaultResourceLoader({
  promptsOverride: (current) => ({
    prompts: [...current.prompts, customCommand],
    diagnostics: current.diagnostics,
  }),
});
```

## Session Management

### SessionManager Factories

| Factory | Description |
|---------|-------------|
| `SessionManager.inMemory()` | No persistence |
| `SessionManager.create(cwd)` | New persistent session |
| `SessionManager.continueRecent(cwd)` | Continue most recent |
| `SessionManager.open(path)` | Open specific file |

### Tree API

```typescript
const sm = SessionManager.open("/path/to/session.jsonl");
const entries = sm.getEntries();        // All entries (excludes header)
const tree = sm.getTree();              // Full tree structure
const path = sm.getPath();              // Path from root to current leaf
const leaf = sm.getLeafEntry();         // Current leaf entry
const children = sm.getChildren(id);    // Direct children
const label = sm.getLabel(id);          // Get label
sm.appendLabelChange(id, "checkpoint"); // Set label
sm.branch(entryId);                     // Move leaf to earlier entry
sm.branchWithSummary(id, "Summary..."); // Branch with context summary
```

### Session Listing

```typescript
const currentProjectSessions = await SessionManager.list(process.cwd());
const allSessions = await SessionManager.listAll(process.cwd());
```

## Settings Management

```typescript
import { createAgentSession, SettingsManager, SessionManager } from "@earendil-works/pi-coding-agent";

// Load from files (global + project merged)
const { session } = await createAgentSession({
  settingsManager: SettingsManager.create(),
});

// With overrides
const settingsManager = SettingsManager.create();
settingsManager.applyOverrides({
  compaction: { enabled: false },
  retry: { enabled: true, maxRetries: 5 },
});

// In-memory (no file I/O, for testing)
const { session } = await createAgentSession({
  settingsManager: SettingsManager.inMemory({ compaction: { enabled: false } }),
  sessionManager: SessionManager.inMemory(),
});

// Custom directories
const { session } = await createAgentSession({
  settingsManager: SettingsManager.create("/custom/cwd", "/custom/agent"),
});
```

Call `await settingsManager.flush()` for durability boundary. Use `settingsManager.drainErrors()` to check for I/O errors.

## Run Modes

### InteractiveMode

Full TUI with editor, chat history, and all built-in commands:
```typescript
import { InteractiveMode } from "@earendil-works/pi-coding-agent";
const mode = new InteractiveMode(runtime, {
  initialMessage: "Hello",
  initialImages: [],
  initialMessages: [],
});
await mode.run();
```

### runPrintMode

Single-shot: send prompts, output result, exit:
```typescript
import { runPrintMode } from "@earendil-works/pi-coding-agent";
await runPrintMode(runtime, {
  mode: "text",
  initialMessage: "Hello",
  messages: ["Follow up"],
});
```

### runRpcMode

JSON-RPC over stdin/stdout for subprocess integration:
```typescript
import { runRpcMode } from "@earendil-works/pi-coding-agent";
await runRpcMode(runtime);
```

CLI alternative: `pi --mode rpc --no-session`

## pi-web-ui Components

Reusable web UI components built on mini-lit web components and Tailwind CSS v4.

### Quick Start

```typescript
import { Agent } from '@earendil-works/pi-agent-core';
import { getModel } from '@earendil-works/pi-ai';
import {
  ChatPanel, AppStorage, IndexedDBStorageBackend,
  ProviderKeysStore, SessionsStore, SettingsStore,
  setAppStorage, defaultConvertToLlm, ApiKeyPromptDialog,
} from '@earendil-works/pi-web-ui';
import '@earendil-works/pi-web-ui/app.css';

// Set up storage
const backend = new IndexedDBStorageBackend({
  dbName: 'my-app', version: 1,
  stores: [
    new SettingsStore().getConfig(),
    new ProviderKeysStore().getConfig(),
    new SessionsStore().getConfig(),
    SessionsStore.getMetadataConfig(),
  ],
});

// Create agent
const agent = new Agent({
  initialState: {
    systemPrompt: 'You are a helpful assistant.',
    model: getModel('anthropic', 'claude-sonnet-4-5-20250929'),
    thinkingLevel: 'off', messages: [], tools: [],
  },
  convertToLlm: defaultConvertToLlm,
});

// Create chat panel
const chatPanel = new ChatPanel();
await chatPanel.setAgent(agent, {
  onApiKeyRequired: (provider) => ApiKeyPromptDialog.prompt(provider),
});
document.body.appendChild(chatPanel);
```

### Components

- **ChatPanel** — High-level chat interface with built-in artifacts panel
- **AgentInterface** — Lower-level chat interface for custom layouts
- **ArtifactsPanel** — Interactive HTML, SVG, Markdown with sandboxed execution
- **SettingsDialog**, **SessionListDialog**, **ModelSelector**, **ApiKeyPromptDialog**

### Storage

IndexedDB-backed: `AppStorage` wraps `SettingsStore`, `ProviderKeysStore`, `SessionsStore`, `CustomProvidersStore`.

### Attachments

Load and process files (PDF, DOCX, XLSX, PPTX, images, text):
```typescript
import { loadAttachment } from '@earendil-works/pi-web-ui';
const attachment = await loadAttachment(file); // From File input
const attachment = await loadAttachment('https://example.com/doc.pdf'); // From URL
```

### Tools

- **JavaScript REPL** — Execute JS in sandboxed browser environment
- **Extract Document** — Extract text from documents at URLs
- **Artifacts Tool** — Built into ArtifactsPanel, supports HTML, SVG, Markdown, images, PDF, DOCX, XLSX

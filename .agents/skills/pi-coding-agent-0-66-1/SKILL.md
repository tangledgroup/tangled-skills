---
name: pi-coding-agent-0-66-1
description: A skill for understanding and implementing the Pi Coding Agent 0.66.1 architecture, covering its minimal terminal-based coding harness design, extensible tool system via Skills/Extensions/Prompt Templates, session management with branching/compaction, multi-mode operation (interactive/print/RPC/SDK), and TUI-based user interface. Use when designing coding agent frameworks, implementing extensible CLI tools, building session-aware AI assistants, creating terminal-based developer tools, or understanding how to build minimal but highly customizable AI coding environments.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - coding-agent
  - cli-framework
  - tui-design
  - session-management
  - extensible-tools
  - developer-tools
  - terminal-ai
category: architecture
required_environment_variables: []
---

# Pi Coding Agent 0.66.1 Architecture and Implementation

Pi is a minimal terminal coding harness designed to be adapted to your workflows, not the other way around. It provides four built-in tools (read, write, edit, bash) with extensive extensibility through Skills, Extensions, Prompt Templates, Themes, and Pi Packages. Pi runs in four modes: Interactive (TUI), Print/JSON (batch), RPC (process integration), and SDK (embedding).

**Key architectural innovations:**
- **Minimal core, maximal extensibility**: Four tools + extension system vs feature-bloat
- **Session tree management**: In-place branching without file duplication
- **Context compaction**: Automatic summarization to handle long conversations
- **Multi-mode operation**: Same core logic across interactive, batch, RPC, and SDK modes
- **TUI-based interface**: Terminal UI with rich interactions (file references, images, commands)

## When to Use

- Designing minimal but extensible coding agent frameworks
- Implementing terminal-based AI developer tools
- Building session-aware conversation management systems
- Creating CLI tools with TUI interfaces
- Understanding extension architecture for AI agents
- Implementing context compaction for long conversations
- Building multi-mode applications (interactive + programmatic APIs)

## Quick Start

### Installation and Usage

```bash
# Install globally
npm install -g @mariozechner/pi-coding-agent

# Authenticate and start
export ANTHROPIC_API_KEY=sk-ant-...
pi

# Or use OAuth login
pi
/login  # Select provider
```

### Basic Interaction

```
User: Create a React component for a todo list
Assistant: I'll create a TodoList component...
[Tool: write] Creating src/TodoList.tsx
[Tool: read] Reading package.json to check dependencies
Assistant: Done! The component is ready at src/TodoList.tsx
```

### Programmatic Usage (SDK)

```typescript
import { createAgentSession } from "@mariozechner/pi-coding-agent";

const session = await createAgentSession({
  cwd: process.cwd(),
  model: getModel("anthropic", "claude-3-5-sonnet"),
  tools: [readTool, writeTool, editTool, bashTool]
});

session.on("turn_end", (event) => {
  console.log("Turn completed:", event.messages);
});

await session.prompt("Create a new file");
```

See [Usage Patterns](references/02-usage-patterns.md) for comprehensive examples.

## Core Architecture Overview

### Design Philosophy

Pi follows several key architectural principles:

1. **Minimal by default**: Ships with 4 tools, no sub-agents or plan mode
2. **Extensible everywhere**: Skills, Extensions, Prompt Templates, Themes, Packages
3. **Session-centric**: All work organized in branched session trees
4. **Mode-agnostic**: Same core works for interactive, batch, RPC, and SDK
5. **Terminal-first**: Rich TUI designed for developer workflows

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Mode Layer                            │
│  Interactive (TUI) | Print | JSON | RPC | SDK           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                 AgentSession Runtime                     │
│  - Event Bus (message flow coordination)                │
│  - Tool Execution (read/write/edit/bash + custom)       │
│  - Session Management (branching, compaction)           │
│  - Extension Runtime (load and coordinate extensions)   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Core Services                           │
│  - AgentSession (state machine, message processing)     │
│  - SessionManager (JSONL tree storage)                  │
│  - ModelRegistry (provider/model management)            │
│  - SettingsManager (global + project settings)          │
│  - SkillsLoader (skill discovery and formatting)        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Pi AI Layer                            │
│  streamSimple(model, context, options)                  │
│  → EventStream<AssistantMessageEvent>                   │
└─────────────────────────────────────────────────────────┘
```

See [Architecture Deep Dive](references/01-architecture-overview.md) for detailed component analysis.

## Key Implementation Patterns

### 1. Session Tree Pattern

**Problem**: How to support branching conversations without duplicating history files?

**Solution**: JSONL file with parent-child relationships:

```typescript
interface SessionEntry {
  id: string;           // UUID
  parentId?: string;    // Reference to parent entry
  type: "message" | "tool_call" | "tool_result" | "compact";
  timestamp: number;
  content: unknown;
}

// Single file contains entire tree
[
  { id: "1", type: "message", content: {...} },           // Root
  { id: "2", parentId: "1", type: "tool_call", ... },     // Child of 1
  { id: "3", parentId: "2", type: "tool_result", ... },   // Child of 2
  { id: "4", parentId: "1", type: "message", ... }        // Branch from 1
]
```

**Benefits:**
- No file duplication for branches
- Full history preserved in single file
- Efficient tree traversal with `/tree` command
- Fork creates new file only when explicitly requested

### 2. Extension Pattern

**Problem**: How to allow customization without forking internals?

**Solution**: Extension API with lifecycle hooks:

```typescript
interface Extension {
  name: string;
  version: string;
  
  // Lifecycle hooks
  onSessionStart?(context: ExtensionContext): void;
  beforeAgentStart?(event: BeforeAgentStartEvent): Promise<void>;
  onAgentEnd?(event: AgentEndEvent): void;
  
  // Custom tools
  tools?: ToolDefinition[];
  
  // Custom UI components
  widgets?: ExtensionWidgetOptions[];
  
  // Custom commands
  commands?: RegisteredCommand[];
}

// Load extensions
const extensions = await discoverAndLoadExtensions();
const runtime = createExtensionRuntime(extensions);
```

**Benefits:**
- No code modification needed for new features
- Extensions can add tools, UI, commands
- Hot-reload support via `/reload`
- Shareable via npm or git (Pi Packages)

### 3. Context Compaction Pattern

**Problem**: How to handle conversations that exceed context windows?

**Solution**: Automatic summarization with history preservation:

```typescript
// When context approaches limit
if (shouldCompact(session, settings)) {
  const result = await compact({
    session,
    cutPoint: await findCutPoint(session),
    summaryPrompt: settings.compaction.summaryPrompt
  });
  
  // Replace old entries with summary
  session.entries = [
    ...result.keepEntries,      // Recent messages kept as-is
    result.compactionEntry,     // Summary of older messages
    ...result.newEntries        // New messages since compaction
  ];
}
```

**Benefits:**
- Lossless (full history still in file)
- Configurable cut point strategy
- Custom summary prompts via extensions
- Revisit full history via `/tree`

### 4. Multi-Mode Pattern

**Problem**: How to support interactive CLI and programmatic SDK with same logic?

**Solution**: Mode layer on top of shared AgentSession:

```typescript
// Core session (mode-agnostic)
const session = await createAgentSession(options);

// Interactive mode adds TUI
InteractiveMode.run(session, { tuiOptions });

// Print mode streams to stdout
runPrintMode(session, { outputMode: "text" });

// RPC mode for process integration
runRpcMode(session, { port: 8080 });

// SDK mode for embedding
const sdkSession = session; // Use directly in your app
```

**Benefits:**
- Single code path for all modes
- Consistent behavior across interfaces
- Easy to add new modes
- SDK users get full feature set

### 5. Tool Registration Pattern

**Problem**: How to support both built-in and custom tools uniformly?

**Solution**: Tool definition interface with wrapper:

```typescript
interface ToolDefinition {
  name: string;
  description: string;
  parameters: TSchema;  // TypeBox schema
  handler: (input: unknown, context: ToolContext) => Promise<unknown>;
}

// Built-in tools
const readTool = createReadToolDefinition({ cwd });

// Custom tool via extension
const gitTool = defineTool({
  name: "git",
  description: "Run git commands",
  parameters: Type.Object({ command: Type.String() }),
  handler: async ({ command }) => {
    return await exec(`git ${command}`);
  }
});

// Register tools
const allTools = [...builtInTools, ...extensionTools];
```

**Benefits:**
- Uniform interface for all tools
- Type-safe parameters via TypeBox
- Easy to add custom tools
- Tools can be added/removed dynamically

## Session Management

### Tree Navigation

```typescript
// Navigate to any point in session tree
const tree = await buildSessionTree(session.entries);

// Find entry by ID
const entry = tree.find(entry => entry.id === "target-id");

// Build branch from entry
const branch = collectBranchEntries(tree, entry);

// Continue from branch point
session.setContext(branch);
await session.prompt("Continue from here");
```

### Forking Sessions

```typescript
// Fork creates new file with copied history
const newSession = await sessionManager.fork({
  sourcePath: "project/.pi/agent/sessions/main.jsonl",
  targetId: "entry-to-fork-from"
});

// New session has independent history
await newSession.prompt("Try different approach");
```

### Compaction Strategies

```typescript
// Find optimal cut point
const cutPoint = await findCutPoint(session, {
  strategy: "keep-last-n-turns",  // or "keep-recent-x-tokens"
  nTurns: 10
});

// Generate summary
const summary = await generateBranchSummary({
  entries: session.entries.slice(0, cutPoint),
  prompt: "Summarize this conversation for context..."
});

// Create compaction entry
const compactionEntry = {
  type: "compaction",
  summary,
  originalEntryCount: cutPoint,
  timestamp: Date.now()
};
```

## Extension System

### Creating an Extension

```typescript
// my-extension.ts
import type { Extension, ExtensionContext } from "@mariozechner/pi-coding-agent";

export default {
  name: "my-extension",
  version: "1.0.0",
  
  // Add custom tool
  tools: [
    {
      name: "deploy",
      description: "Deploy application",
      parameters: Type.Object({ environment: Type.String() }),
      handler: async ({ environment }) => {
        return await runDeployment(environment);
      }
    }
  ],
  
  // Add custom command
  commands: [
    {
      name: "deploy",
      description: "Deploy current project",
      handler: async (context) => {
        context.ui.showInput("Which environment?");
      }
    }
  ],
  
  // Lifecycle hooks
  onSessionStart: (context) => {
    console.log("Extension loaded!");
  }
} satisfies Extension;
```

### Loading Extensions

```typescript
// Discover extensions from node_modules and local dirs
const extensions = await discoverAndLoadExtensions({
  packages: ["@myorg/pi-extension"],
  directories: ["./extensions"]
});

// Create runtime with all extensions
const runtime = createExtensionRuntime(extensions, {
  cwd: process.cwd(),
  settings: settingsManager.get()
});

// Attach to agent session
session.attachExtensionRuntime(runtime);
```

## Reference Files

- [`references/01-architecture-overview.md`](references/01-architecture-overview.md) - High-level architecture, design philosophy, component interactions
- [`references/02-usage-patterns.md`](references/02-usage-patterns.md) - Interactive mode, SDK usage, extension development
- [`references/03-session-management.md`](references/03-session-management.md) - Session tree structure, branching, compaction implementation
- [`references/04-extension-system.md`](references/04-extension-system.md) - Extension API, tool registration, lifecycle hooks
- [`references/05-tool-implementation.md`](references/05-tool-implementation.md) - Built-in tools (read/write/edit/bash), custom tool creation
- [`references/06-tui-design.md`](references/06-tui-design.md) - TUI components, keyboard shortcuts, themes

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/pi-coding-agent-0-66-1/`). All paths are relative to this directory.

## Key Design Decisions

### Why Minimal Core?

1. **Focus**: 4 tools force thoughtful extension design
2. **Maintainability**: Smaller codebase, fewer bugs
3. **Flexibility**: Users build exactly what they need
4. **Learning**: Easier to understand and modify

### Why Session Trees?

1. **Efficiency**: No duplication for branches
2. **History**: Full conversation preserved
3. **Navigation**: Jump to any point with `/tree`
4. **Forking**: Explicit when you want independent history

### Why Extensions Over Features?

1. **Composability**: Mix and match functionality
2. **Upgradability**: Core updates don't break extensions
3. **Sharing**: Pi Packages on npm/git
4. **Customization**: Adapt to specific workflows

### Why Multi-Mode Design?

1. **Consistency**: Same behavior everywhere
2. **Testing**: Test SDK code in interactive mode
3. **Integration**: Embed in IDEs, CI/CD, custom tools
4. **Flexibility**: Choose interface that fits workflow

## Troubleshooting

### Common Issues

**Extension not loading:**
```bash
# Check extension discovery
pi /reload

# Verify extension path
ls ~/.pi/agent/extensions/
```

**Session corruption:**
```bash
# Restore from backup
cp ~/.pi/agent/sessions/*.jsonl.bak ~/.pi/agent/sessions/

# Or start fresh
pi --no-session
```

**Tool execution fails:**
```typescript
// Check tool permissions
const bashTool = createBashTool({
  allowedCommands: ["npm", "git"],  // Whitelist
  cwd: process.cwd()
});
```

## Additional Resources

- **GitHub Repository:** https://github.com/badlogic/pi-mono/tree/v0.66.1/packages/coding-agent
- **Documentation:** https://github.com/badlogic/pi-mono/tree/v0.66.1/packages/coding-agent/docs
- **Examples:** https://github.com/badlogic/pi-mono/tree/v0.66.1/packages/coding-agent/examples
- **Discord Community:** https://discord.com/invite/3cU7Bz4UPx

## Implementation Insights

Pi demonstrates several advanced patterns for building extensible developer tools:

1. **Minimal Viable Product**: Start small, extend as needed
2. **Tree-Based History**: Efficient branching without duplication
3. **Extension-First Design**: Core provides hooks, not features
4. **Mode Abstraction**: Same logic, different interfaces
5. **Context-Aware Tools**: Tools understand project structure

These patterns make Pi highly adaptable to different workflows while maintaining a small, maintainable codebase.

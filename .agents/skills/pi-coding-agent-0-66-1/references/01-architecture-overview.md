# Architecture Overview

## System Architecture

Pi Coding Agent 0.66.1 implements a layered architecture that separates mode-specific UI from core agent logic, enabling the same session management and tool execution across interactive, print, RPC, and SDK modes.

### Layer 1: Mode Layer (UI/Interface)

```typescript
// Four modes, same core
class InteractiveMode {
  async run(session: AgentSession): Promise<void> {
    // TUI with editor, messages, footer
    const tui = new ProcessTerminal();
    // Event loop for user input + agent responses
  }
}

function runPrintMode(session: AgentSession): void {
  // Stream to stdout, no TUI
}

function runRpcMode(session: AgentSession): void {
  // HTTP/JSON-RPC server
}

// SDK mode - just use AgentSession directly
const session = await createAgentSession(options);
```

**Design Decision:** Mode layer is thin wrapper around core logic.

### Layer 2: AgentSession Runtime

```typescript
class AgentSessionRuntime {
  private eventBus: EventBus;
  private tools: Map<string, ToolDefinition>;
  private extensions: ExtensionRuntime;
  
  async prompt(message: string): Promise<void> {
    // 1. Add user message to session
    // 2. Emit before_agent_start events
    // 3. Call LLM via Pi AI
    // 4. Process tool calls
    // 5. Execute tools (with extension hooks)
    // 6. Emit turn_end event
  }
}
```

**Design Decision:** Central runtime coordinates all agent activity.

### Layer 3: Core Services

```typescript
// Session management
class SessionManager {
  async load(path: string): Promise<SessionEntry[]>;
  async save(entries: SessionEntry[]): Promise<void>;
  async fork(source: string, targetId: string): Promise<string>;
}

// Model resolution
class ModelRegistry {
  async resolve(provider: string, model: string): Promise<Model>;
}

// Settings hierarchy
class SettingsManager {
  get(): Settings;  // Merges global + project settings
}
```

**Design Decision:** Services are pure, testable units.

### Layer 4: Pi AI Integration

Uses `streamSimple()` from Pi AI for LLM interactions.

**Design Decision:** Leverages existing, well-tested abstraction.

## Core Components

### AgentSession (State Machine)

```typescript
class AgentSession {
  state: "idle" | "prompting" | "executing_tools" | "compact";
  
  messages: SessionEntry[];
  currentTurn: TurnContext;
  
  async prompt(userMessage: string): Promise<void>;
  async executeToolCall(call: ToolCall): Promise<ToolResult>;
  async compact(): Promise<void>;
}
```

**Key Insight:** Session is a state machine with clear transitions.

### Event Bus (Message Coordination)

```typescript
interface EventBus {
  on<T extends EventType>(event: T, handler: EventHandler<T>): void;
  emit<T extends EventType>(event: T): Promise<void>;
}

// Events flow through bus
await bus.emit({ type: "before_agent_start" });
await bus.emit({ type: "tool_call", call: {...} });
await bus.emit({ type: "tool_result", result: {...} });
await bus.emit({ type: "turn_end" });
```

**Benefits:**
- Decouples components
- Extensions can observe/intercept
- Clear audit trail

### Session Tree (Branching Structure)

```typescript
interface SessionEntry {
  id: string;
  parentId?: string;  // Creates tree structure
  type: EntryType;
  timestamp: number;
  content: unknown;
}

// Build tree from flat array
function buildTree(entries: SessionEntry[]): TreeNode {
  const root = entries.find(e => !e.parentId);
  const children = entries.filter(e => e.parentId === root.id);
  
  return {
    entry: root,
    children: children.map(id => buildBranch(entries, id))
  };
}
```

### Extension Runtime (Plugin System)

```typescript
class ExtensionRuntime {
  extensions: Extension[];
  tools: Map<string, ToolDefinition>;
  commands: Map<string, CommandHandler>;
  
  async beforeAgentStart(context): Promise<void> {
    for (const ext of this.extensions) {
      if (ext.beforeAgentStart) {
        await ext.beforeAgentStart(context);
      }
    }
  }
}
```

## Component Interactions

### Prompt Flow

```
1. User types message in TUI
   ↓
2. InteractiveMode captures input
   ↓
3. AgentSession.prompt() called
   ↓
4. Event bus emits before_agent_start
   ↓
5. Extensions intercept/modify context
   ↓
6. Context built (messages + tools + skills)
   ↓
7. Pi AI streamSimple() called
   ↓
8. LLM streams response events
   ↓
9. Tool calls detected → executeToolCall()
   ↓
10. Extension hooks (before_tool_call)
    ↓
11. Tool executes (read/write/edit/bash)
    ↓
12. Extension hooks (after_tool_call)
    ↓
13. Tool result added to session
    ↓
14. Event bus emits turn_end
    ↓
15. TUI updates with response
```

### Session Persistence

```typescript
// Auto-save after each turn
session.on("turn_end", async () => {
  await sessionManager.save(session.entries);
});

// Load on startup
const entries = await sessionManager.load(sessionPath);
session.restore(entries);
```

## Extensibility Points

### Custom Tools

```typescript
// Via extension
export default {
  tools: [
    defineTool({
      name: "deploy",
      handler: async ({ env }) => await deploy(env)
    })
  ]
};
```

### Custom Commands

```typescript
// Register /command
export default {
  commands: [
    {
      name: "stats",
      handler: async (ctx) => {
        ctx.ui.showMessage(await getStats());
      }
    }
  ]
};
```

### Custom UI Components

```typescript
// Add widget to TUI
export default {
  widgets: [
    {
      placement: "above_editor",
      render: (ctx) => <StatusWidget />
    }
  ]
};
```

### Lifecycle Hooks

```typescript
export default {
  onSessionStart: (ctx) => { /* init */ },
  beforeAgentStart: (ctx) => { /* modify context */ },
  onAgentEnd: (ctx) => { /* cleanup */ },
  onToolCall: (ctx) => { /* intercept tool */ }
};
```

## Performance Considerations

### Memory Efficiency

- **Session entries**: Stored as flat array, tree built on-demand
- **Event bus**: Async handlers don't block event flow
- **TUI rendering**: Only dirty regions re-rendered

### CPU Efficiency

- **Tool execution**: Parallel when independent
- **Compaction**: Background process, non-blocking
- **Extension loading**: Lazy load on demand

### I/O Efficiency

- **Session saves**: Debounced (batch multiple changes)
- **File operations**: Cached where possible
- **LLM streaming**: Progressive rendering

## Security Considerations

### Tool Sandboxing

```typescript
// Bash tool with restrictions
const bashTool = createBashTool({
  allowedCommands: ["npm", "git", "node"],  // Whitelist
  cwd: projectRoot,                          // Restricted directory
  timeout: 30000                             // Max execution time
});
```

### Input Validation

- All tool parameters validated against TypeBox schemas
- File paths checked for directory traversal
- Shell commands sanitized before execution

### Extension Isolation

- Extensions run in same process but isolated contexts
- No direct access to file system except via tools
- Errors in extensions don't crash core

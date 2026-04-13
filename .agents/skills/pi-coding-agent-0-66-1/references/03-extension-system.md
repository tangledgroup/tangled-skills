# Extension System Architecture

This document covers the extension system in Pi Coding Agent, including extension lifecycle, API surface, tool registration, command handling, and UI component integration.

## Extension Architecture Overview

### Extension Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    Extension Discovery                       │
│   - Scan extensions/ directory                              │
│   - Load package.json metadata                              │
│   - Validate extension manifest                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Extension Loading                          │
│   - Dynamic import (jiti for TypeScript)                    │
│   - Create ExtensionRuntime instance                        │
│   - Call extension factory function                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Activation Phase                           │
│   - Call activate(context)                                  │
│   - Register tools, commands, keybindings                   │
│   - Subscribe to events                                     │
│   - Return shutdown handler                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Runtime Phase                               │
│   - Handle tool executions                                  │
│   - Process commands                                        │
│   - Emit/receive events                                     │
│   - Update UI components                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Shutdown Phase                             │
│   - Call shutdown handler                                   │
│   - Cleanup resources                                       │
│   - Unsubscribe from events                                 │
└─────────────────────────────────────────────────────────────┘
```

## Extension Definition

### Basic Extension Structure

```typescript
import type { ExtensionFactory, ExtensionContext } from "@mariozechner/pi-coding-agent";

export const myExtension: ExtensionFactory = () => {
  return {
    // Metadata (from package.json)
    name: "my-extension",
    version: "1.0.0",
    
    // Activation
    async activate(context: ExtensionContext) {
      // Register tools
      context.registerTool({
        name: "my_tool",
        label: "My Tool",
        description: "Does something useful",
        parameters: Type.Object({ input: Type.String() }),
        execute: async (toolCallId, params) => {
          return {
            content: [{ type: "text", text: `Result: ${params.input}` }],
            details: { input: params.input }
          };
        }
      });
      
      // Register commands
      context.registerCommand({
        name: "my-command",
        description: "My custom command",
        handler: async (ctx) => {
          console.log("Command executed");
        }
      });
      
      // Subscribe to events
      context.subscribe((event) => {
        if (event.type === "turn_end") {
          console.log("Turn completed");
        }
      });
      
      // Return shutdown handler
      return () => {
        console.log("Extension shutting down");
      };
    }
  };
};
```

### Extension Context API

The context provides the extension API surface:

```typescript
interface ExtensionContext {
  // Tool registration
  registerTool(tool: ToolDefinition): void;
  
  // Command registration
  registerCommand(command: RegisteredCommand): void;
  
  // Event subscription
  subscribe(listener: (event: ExtensionEvent) => void): () => void;
  
  // UI integration
  showDialog(options: ExtensionUIDialogOptions): Promise<string>;
  showWidget(options: ExtensionWidgetOptions): void;
  
  // Input handling
  requestInput(prompt: string): Promise<string>;
  
  // Error reporting
  reportError(error: ExtensionError): void;
  
  // Session info
  getSessionInfo(): SessionInfo;
  getCwd(): string;
}
```

## Tool Registration in Extensions

### Simple Tool Registration

```typescript
context.registerTool({
  name: "database_query",
  label: "Database Query",
  description: "Execute a database query",
  parameters: Type.Object({
    query: Type.String({ description: "SQL query" }),
    params: Type.Optional(Type.Array(Type.Any()))
  }),
  execute: async (toolCallId, params, signal, onUpdate) => {
    // Check for abort
    if (signal?.aborted) {
      throw new Error("Query cancelled");
    }
    
    // Execute query
    const result = await db.execute(params.query, params.params);
    
    // Stream progress for long queries
    onUpdate?.({
      content: [{ type: "text", text: `Processed ${result.rows.length} rows` }],
      details: { rows: result.rows.length }
    });
    
    return {
      content: [
        { type: "text", text: JSON.stringify(result.rows, null, 2) }
      ],
      details: {
        query: params.query,
        rows: result.rows.length,
        executionTime: result.executionTime
      }
    };
  }
});
```

### Tool with Authorization Hook

```typescript
context.registerTool({
  name: "deploy",
  label: "Deploy",
  description: "Deploy application to production",
  parameters: Type.Object({
    environment: StringEnum(["staging", "production"]),
    branch: Type.String()
  }),
  execute: async (toolCallId, params) => {
    // Tool logic
    await deployApp(params.environment, params.branch);
    
    return {
      content: [{ type: "text", text: `Deployed to ${params.environment}` }],
      details: { environment: params.environment, branch: params.branch }
    };
  }
});

// Before tool call hook for authorization
context.beforeToolCall(async ({ toolCall, args }) => {
  if (toolCall.name === "deploy" && args.environment === "production") {
    // Require confirmation for production deploys
    const confirmed = await context.requestInput(
      "Deploy to production? Type 'YES' to confirm:"
    );
    
    if (confirmed !== "YES") {
      return { 
        block: true, 
        reason: "Production deployment cancelled by user" 
      };
    }
  }
  
  return undefined; // Allow execution
});
```

## Command Registration

### Slash Commands

Register custom slash commands:

```typescript
context.registerCommand({
  name: "stats",
  description: "Show session statistics",
  handler: async (commandContext) => {
    const stats = commandContext.getSessionStats();
    
    commandContext.output(`
Session Statistics:
- Total turns: ${stats.turnCount}
- Tool calls: ${stats.toolCallCount}
- Tokens used: ${stats.tokenCount}
- Duration: ${formatDuration(stats.duration)}
    `);
  }
});

// Usage: /stats
```

### Command with Arguments

```typescript
context.registerCommand({
  name: "search",
  description: "Search codebase",
  handler: async (commandContext) => {
    const query = await commandContext.requestInput("Search for:");
    
    if (!query) {
      commandContext.output("No search query provided");
      return;
    }
    
    const results = await grepFiles(".", { pattern: query });
    
    commandContext.output(`Found ${results.length} matches:\n${results.join("\n")}`);
  }
});

// Usage: /search
```

### Command with UI Dialog

```typescript
context.registerCommand({
  name: "deploy",
  description: "Deploy application",
  handler: async (commandContext) => {
    const environment = await context.showDialog({
      type: "select",
      message: "Select deployment environment:",
      options: [
        { label: "Staging", value: "staging" },
        { label: "Production", value: "production" }
      ]
    });
    
    if (!environment) {
      commandContext.output("Deployment cancelled");
      return;
    }
    
    await deployApp(environment);
    commandContext.output(`Deployed to ${environment}`);
  }
});
```

## Event System

### Available Events

Extensions can subscribe to various events:

```typescript
context.subscribe((event) => {
  switch (event.type) {
    case "agent_start":
      console.log("Agent started");
      break;
      
    case "turn_start":
      console.log("New turn beginning");
      break;
      
    case "turn_end":
      console.log(`Turn ended with ${event.toolResults.length} tool results`);
      break;
      
    case "tool_execution_start":
      console.log(`Executing ${event.toolName}`);
      break;
      
    case "tool_execution_end":
      if (event.isError) {
        console.error(`Tool failed: ${event.result.content[0].text}`);
      }
      break;
      
    case "message_start":
    case "message_update":
    case "message_end":
      // Message lifecycle events
      break;
      
    case "session_compact":
      console.log("Session was compacted");
      break;
      
    case "agent_end":
      console.log("Agent session ended");
      break;
  }
});
```

### Event Filtering

Filter events by type:

```typescript
// Only listen to tool execution events
const unsubscribe = context.subscribe((event) => {
  if (event.type === "tool_execution_end") {
    logToolExecution(event);
  }
});

// Cleanup on shutdown
return () => {
  unsubscribe();
};
```

## UI Integration

### Custom Widgets

Add custom UI components:

```typescript
context.showWidget({
  title: "Database Status",
  placement: "footer",
  render: () => {
    const status = getDatabaseStatus();
    
    return h("div", { class: "db-status" }, [
      h("span", { class: status.connected ? "green" : "red" }, 
        status.connected ? "●" : "○"
      ),
      h("span", ` ${status.connections} connections`)
    ]);
  },
  refreshInterval: 5000 // Refresh every 5 seconds
});
```

### Dialogs and Prompts

Show interactive dialogs:

```typescript
// Text input
const filename = await context.requestInput(
  "Enter filename:",
  { placeholder: "example.txt" }
);

// Confirmation dialog
const confirmed = await context.showDialog({
  type: "confirm",
  message: "Are you sure you want to delete this file?",
  confirmText: "Delete",
  cancelText: "Cancel"
});

// Selection dialog
const model = await context.showDialog({
  type: "select",
  message: "Select a model:",
  options: [
    { label: "GPT-4o", value: "gpt-4o" },
    { label: "Claude 3.5", value: "claude-3-5-sonnet" }
  ]
});
```

## Keybinding Registration

### Custom Keybindings

Register custom keyboard shortcuts:

```typescript
context.registerKeybinding({
  key: "ctrl+k",
  command: "my-extension.show-help",
  context: "editor" // Optional context filter
});

context.registerKeybinding({
  key: "alt+s",
  command: "my-extension.save",
  description: "Save current work"
});
```

### Keybinding Commands

Implement keybinding handlers:

```typescript
context.registerCommand({
  name: "my-extension.show-help",
  handler: async (ctx) => {
    ctx.showWidget({
      title: "Help",
      placement: "overlay",
      render: () => h("div", [
        h("h2", "Available Commands:"),
        h("ul", [
          h("li", "/stats - Show statistics"),
          h("li", "/deploy - Deploy application")
        ])
      ])
    });
  }
});
```

## Extension Discovery and Loading

### Directory Structure

Extensions are discovered from:

```
~/.pi/extensions/
├── my-extension/
│   ├── package.json
│   └── index.ts
├── another-extension/
│   ├── package.json
│   └── index.ts
```

### Package.json Manifest

Each extension needs a manifest:

```json
{
  "name": "my-extension",
  "version": "1.0.0",
  "description": "My custom extension",
  "main": "index.ts",
  "piExtension": {
    "displayName": "My Extension",
    "author": "Your Name <email@example.com>",
    "license": "MIT",
    "dependencies": {
      "@mariozechner/pi-coding-agent": "^0.66.1"
    }
  }
}
```

### Dynamic Loading

Extensions are loaded with jiti for TypeScript support:

```typescript
async function loadExtension(extensionPath: string): Promise<Extension> {
  const jiti = createJiti(extensionPath);
  const module = await jiti.import(extensionPath + "/index.ts");
  
  const factory: ExtensionFactory = module.default || module;
  const extension = factory();
  
  return extension;
}
```

## Extension Runtime

### ExtensionRunner Class

Manages extension lifecycle:

```typescript
class ExtensionRunner {
  private extensions: Map<string, ExtensionRuntime> = new Map();
  
  async loadExtensions(paths: string[]): Promise<LoadExtensionsResult> {
    const results: LoadExtensionsResult = {
      loaded: [],
      errors: []
    };
    
    for (const path of paths) {
      try {
        const extension = await this.loadExtension(path);
        const runtime = new ExtensionRuntime(extension, this.context);
        
        const shutdown = await runtime.activate();
        runtime.shutdownHandler = shutdown;
        
        this.extensions.set(extension.name, runtime);
        results.loaded.push(extension.name);
      } catch (error) {
        results.errors.push({ path, error });
      }
    }
    
    return results;
  }
  
  async shutdown(): Promise<void> {
    for (const runtime of this.extensions.values()) {
      await runtime.shutdown();
    }
    this.extensions.clear();
  }
}
```

## Error Handling

### Extension Errors

Report errors from extensions:

```typescript
try {
  await someOperation();
} catch (error) {
  context.reportError({
    source: "my-extension",
    message: error.message,
    stack: error.stack
  });
}
```

### Graceful Degradation

Handle extension failures gracefully:

```typescript
async function safeActivate(extension: Extension): Promise<void> {
  try {
    const shutdown = await extension.activate(context);
    // Store shutdown handler
  } catch (error) {
    console.warn(`Extension ${extension.name} failed to activate:`, error);
    // Continue with other extensions
  }
}
```

## Best Practices

1. **Use unique names** - Prefix tools/commands with extension name
2. **Handle shutdown** - Always return cleanup function from activate()
3. **Subscribe selectively** - Only listen to relevant events
4. **Validate inputs** - Use TypeBox schemas for tool parameters
5. **Stream progress** - Use onUpdate callback for long operations
6. **Respect abort signals** - Check signal.aborted in async operations
7. **Log appropriately** - Use context.output() for user-visible messages
8. **Error gracefully** - Catch and report errors, don't crash

## Example: Complete Extension

```typescript
import type { ExtensionFactory } from "@mariozechner/pi-coding-agent";
import { Type } from "@sinclair/typebox";

export const gitExtension: ExtensionFactory = () => {
  return {
    name: "git-extension",
    version: "1.0.0",
    
    async activate(context) {
      // Register git status tool
      context.registerTool({
        name: "git_status",
        label: "Git Status",
        description: "Show current git repository status",
        parameters: Type.Object({}),
        execute: async () => {
          const status = await exec("git status --short");
          
          return {
            content: [{ type: "text", text: status || "Clean working directory" }],
            details: { output: status }
          };
        }
      });
      
      // Register /git-status command
      context.registerCommand({
        name: "git-status",
        description: "Show git status",
        handler: async (ctx) => {
          const status = await exec("git status");
          ctx.output(status);
        }
      });
      
      // Subscribe to turn end for auto-status
      context.subscribe((event) => {
        if (event.type === "turn_end") {
          // Log git status after each turn
          void exec("git status --short").then(s => {
            if (s) console.log("Git:", s);
          });
        }
      });
      
      return () => {
        console.log("Git extension shutting down");
      };
    }
  };
};
```

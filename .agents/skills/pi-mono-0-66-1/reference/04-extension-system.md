# Extension System - Deep Dive

This reference document explains how pi-coding-agent implements its extensibility architecture for adding custom tools, commands, UI components, and event handlers.

## Extension Philosophy

Pi's core is intentionally minimal - it ships with only four built-in tools (read, write, edit, bash). Everything else is added through extensions. This design:

**Benefits users**: Install only what you need, keeping the agent fast and focused.

**Benefits developers**: Extend without modifying core code, avoiding upgrade conflicts.

**Benefits community**: Share extensions as npm packages or git repositories.

## Extension Architecture

An extension is a TypeScript module that exports an extension factory function:

```typescript
export default function(context: ExtensionFactoryContext): Extension {
    return {
        id: "my-extension",
        name: "My Extension",
        version: "1.0.0",
        // ... hooks and capabilities
    };
}
```

The factory receives context for discovering resources and returns an extension object defining hooks and capabilities.

## Extension Object Structure

**Metadata**:
- `id`: Unique identifier (reverse-domain notation recommended)
- `name`: Display name for UI
- `version`: Semver version string

**Lifecycle hooks**: Functions called at specific points in the agent workflow

**Capability providers**: Functions that return tools, commands, UI components

**Event handlers**: Async functions that receive events and can modify behavior

## Lifecycle Hooks

Extensions can hook into the agent's lifecycle:

### Agent-Level Hooks

**onBeforeAgentStart**: Called before any processing begins. Use for initialization.

**onAgentStart**: Called after agent starts but before first turn. Use for setup that needs agent to be initialized.

**onAgentEnd**: Called when agent completes all work. Use for cleanup or final reporting.

### Turn-Level Hooks

**onTurnStart**: Called at the beginning of each turn (LLM call + tool execution cycle).

**onTurnEnd**: Called after a turn completes, with the assistant message and any tool results.

**Use case**: Track metrics per turn, inject context, log turn summaries.

### Message-Level Hooks

**onMessageStart**: Called when any message begins (user, assistant, tool result).

**onMessageUpdate**: Called during assistant message streaming with each chunk.

**onMessageEnd**: Called when a message completes.

**Use case**: Real-time message processing, analytics, custom rendering.

### Tool-Level Hooks

**onToolExecutionStart**: Called when a tool begins execution. Can return a result to block execution.

**onToolExecutionUpdate**: Called if the tool streams progress updates.

**onToolExecutionEnd**: Called after tool completes, before results are added to context.

**Use case**: Security checks, rate limiting, auditing, result modification.

## Tool Registration

Extensions can add custom tools:

```typescript
getTools(context): ToolDefinition[] {
    return [
        {
            name: "deploy",
            description: "Deploy the application",
            parameters: Type.Object({
                environment: Type.String(),
            }),
            execute: async (toolCallId, args, signal, onUpdate) => {
                // Implementation
                return {
                    content: [{ type: "text", text: "Deployed!" }],
                    details: { environment: args.environment }
                };
            }
        }
    ];
}
```

**Tool lifecycle**:
1. Extension registers tool via getTools()
2. Tool is added to agent's available tools list
3. LLM can call the tool like any built-in tool
4. Parameters are validated against schema
5. beforeToolCall hooks run (can block)
6. Tool executes
7. afterToolCall hooks run (can modify result)
8. Result added to conversation

**Streaming updates**: Tools can call onUpdate() to stream progress:
```typescript
execute: async (toolCallId, args, signal, onUpdate) => {
    onUpdate({ content: [{ type: "text", text: "Starting..." }] });
    await doWork();
    onUpdate({ content: [{ type: "text", text: "Completed!" }] });
    return { content: [{ type: "text", text: "Done" }] };
}
```

**Error handling**: Throw errors for failures. They become tool results with isError=true, allowing the LLM to recover.

## Command Registration

Extensions can add slash commands:

```typescript
getCommands(context): RegisteredCommand[] {
    return [
        {
            name: "deploy",
            description: "Deploy the application",
            handler: async (args, commandContext) => {
                // Implementation
                await deployApp(args);
            }
        }
    ];
}
```

**Command execution**:
1. User types `/deploy` in editor
2. Command handler runs with parsed arguments
3. Can access session state, agent, extension context
4. Can modify UI, trigger agent actions, show dialogs

**Command context** provides:
- Session access (messages, stats)
- Agent access (prompt, steer, followUp)
- UI manipulation (show overlays, add components)
- Input handling (prompt user for input)

## UI Component Registration

Extensions can add custom UI:

```typescript
getUI(uiContext): Component {
    return new MyCustomComponent();
}
```

**UI placement options**:
- Replace the editor entirely
- Add widgets above/below the editor
- Add a status line
- Add a custom footer
- Show overlays (dialogs, menus)

**UI context** provides:
- TUI instance for showing overlays
- Theme for consistent styling
- Terminal dimensions for responsive layouts

**Component lifecycle**:
1. getUI() called once, returns component
2. Component renders every frame
3. Component receives input when focused
4. Component invalidated and re-rendered when state changes

## Event Handling

Extensions receive events through their hooks:

**Event types**:
- Agent lifecycle (start, end)
- Turn lifecycle (start, end)
- Message events (start, update, end)
- Tool events (start, update, end)
- Custom events (bash execution, read file, etc.)

**Event data**: Each event type includes relevant data:
- Message events include the message content
- Tool events include tool call details and results
- Turn events include assistant message and tool results

**Async handling**: Hooks are async and awaited in order. This allows extensions to:
- Wait for external operations (database queries, API calls)
- Block execution by returning specific results
- Modify state before next hook runs

## Blocking Tool Execution

Extensions can block tools via the beforeToolCall hook:

```typescript
onToolExecutionStart(event): ToolCallEventResult | void {
    if (event.toolCall.name === "bash" && event.args.command.includes("rm -rf")) {
        return {
            block: true,
            reason: "Dangerous command blocked"
        };
    }
    // undefined = allow execution
}
```

**Blocking behavior**:
1. Tool execution is cancelled
2. Error result is added to conversation with the reason
3. LLM sees the error and can retry with different approach
4. onToolExecutionEnd still fires (with blocked result)

**Use cases**:
- Security policies (block dangerous commands)
- Rate limiting (throttle expensive operations)
- Environment checks (block if prerequisites not met)
- User approval (prompt before executing)

## Modifying Tool Results

Extensions can modify results via the afterToolCall hook:

```typescript
onToolExecutionEnd(event): void {
    if (!event.isError && event.result.content) {
        // Add metadata
        event.result.details = {
            ...event.result.details,
            processedBy: "my-extension",
            timestamp: Date.now()
        };
    }
}
```

**Modification limits**: Can modify the result object, but changes must be made before the hook returns. The modified result is what gets added to the conversation.

**Use cases**:
- Add audit metadata
- Transform output format
- Redact sensitive information
- Enrich with external data

## Extension Context

Extensions receive a context object providing access to pi's internals:

**Session access**:
- Current session ID and path
- Session messages and stats
- Session switching/branching

**Agent access**:
- Current agent state
- Prompt the agent
- Steer or follow-up
- Abort current operation

**Registration functions**:
- addTool(): Register additional tools dynamically
- addCommand(): Register commands dynamically
- addMessageRenderer(): Custom message rendering

**Utilities**:
- File system access
- Process execution
- Clipboard operations
- Configuration reading/writing

## Extension Loading

Extensions are loaded from directories:

**Discovery**:
1. Scan extension directories for packages
2. Read package.json for extension metadata
3. Import extension module
4. Call factory function with context
5. Register hooks and capabilities

**Loading order**: Extensions load in alphabetical order by ID. Hooks are called in loading order.

**Error handling**: If an extension fails to load, it's skipped with a warning. Other extensions continue loading.

**Hot reloading**: Extensions can be reloaded without restarting pi (useful for development).

## Extension Packages

Extensions can be packaged as npm packages:

**Package structure**:
```
my-extension/
├── package.json (with "pi-extension" field)
├── dist/
│   └── index.js (compiled extension)
└── README.md
```

**package.json fields**:
```json
{
    "name": "@user/my-extension",
    "version": "1.0.0",
    "pi-extension": {
        "id": "com.user.my-extension",
        "name": "My Extension",
        "description": "Does something useful"
    },
    "main": "dist/index.js"
}
```

**Installation**:
```bash
npm install -g @user/my-extension
# Or add to ~/.pi/agent/extensions/ directory
```

## Custom Message Types

Extensions can define custom message types via TypeScript declaration merging:

```typescript
// In extension code
declare module "@mariozechner/pi-coding-agent" {
    interface CustomAgentMessages {
        deployment: {
            role: "deployment";
            environment: string;
            status: "pending" | "success" | "failed";
            timestamp: number;
        };
    }
}
```

**How it works**:
1. Extension declares new message type
2. Agent accepts the type (TypeScript level)
3. Extension adds messages to session
4. UI can render them via custom message renderers
5. Messages are filtered out before LLM calls (LLMs don't see them)

**Use case**: Track internal state (deployments, builds, tests) without cluttering LLM context.

## Security Considerations

Extensions run with full access to the agent's internals. Security considerations:

**Trust model**: Only install extensions from trusted sources. They can:
- Read/write files
- Execute commands
- Access API keys
- Modify session data

**Sandboxing**: Pi doesn't sandbox extensions (they're TypeScript, not WASM). Trust is required.

**Code review**: Review extension code before installing, especially from unknown sources.

**Permissions**: Future versions might add permission scopes to limit extension capabilities.

## Debugging Extensions

**Logging**: Use console.log for debugging. Output appears in pi's logs.

**Error handling**: Wrap extension code in try/catch to prevent crashes:
```typescript
execute: async (...) => {
    try {
        return await riskyOperation();
    } catch (error) {
        console.error("Extension error:", error);
        throw new Error(`Operation failed: ${error.message}`);
    }
}
```

**State inspection**: Access agent.state to inspect current state in hooks.

**Event logging**: Log events in hooks to understand timing and data flow.

## Extension Examples

### Simple Tool Extension

Adds a single custom tool:
```typescript
export default function(context): Extension {
    return {
        id: "weather-tool",
        name: "Weather Tool",
        version: "1.0.0",
        getTools: () => [{
            name: "get_weather",
            description: "Get weather for a location",
            parameters: Type.Object({ city: Type.String() }),
            execute: async (_, args) => {
                const weather = await fetchWeather(args.city);
                return { content: [{ type: "text", text: weather }] };
            }
        }]
    };
}
```

### Security Extension

Blocks dangerous commands:
```typescript
export default function(context): Extension {
    return {
        id: "security-gate",
        name: "Security Gate",
        version: "1.0.0",
        onToolExecutionStart: (event) => {
            const dangerous = ["rm -rf", "dd if=", ":()"];
            if (dangerous.some(d => event.args.command.includes(d))) {
                return { block: true, reason: "Dangerous command blocked" };
            }
        }
    };
}
```

### UI Extension

Adds a status widget:
```typescript
export default function(context): Extension {
    let status = "Idle";
    
    return {
        id: "status-widget",
        name: "Status Widget",
        version: "1.0.0",
        onAgentStart: () => { status = "Working"; },
        onAgentEnd: () => { status = "Idle"; },
        getUI: (uiContext) => {
            return new Text(`Status: ${status}`);
        }
    };
}
```

### Command Extension

Adds a slash command:
```typescript
export default function(context): Extension {
    return {
        id: "deploy-command",
        name: "Deploy Command",
        version: "1.0.0",
        getCommands: () => [{
            name: "deploy",
            description: "Deploy to production",
            handler: async (args, cmdContext) => {
                await cmdContext.agent.prompt(
                    `Deploy the application to ${args.environment}`
                );
            }
        }]
    };
}
```

## Best Practices

**Single responsibility**: Each extension should do one thing well.

**Error handling**: Catch and handle errors gracefully, provide meaningful error messages.

**Performance**: Avoid heavy computation in hooks, especially onMessageUpdate (fires frequently).

**Cleanup**: Implement onAgentEnd for cleanup (close connections, cancel timers).

**Configuration**: Allow users to configure extension behavior via settings.

**Documentation**: Include README explaining what the extension does and how to configure it.

**Versioning**: Use semantic versioning, document breaking changes in changelog.

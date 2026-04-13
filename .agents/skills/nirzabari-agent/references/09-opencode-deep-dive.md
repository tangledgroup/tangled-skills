# OpenCode Deep Dive

Complete analysis of OpenCode's client-server architecture, TypeScript/Bun implementation, and design philosophy.

## Overview

**OpenCode** is an open-source AI coding agent with a client-server architecture. Built by neovim users and creators of terminal.shop, it pushes the limits of what's possible in the terminal while remaining provider-agnostic.

### Installation

```bash
# YOLO install
curl -fsSL https://opencode.ai/install | bash

# Package managers
npm i -g opencode-ai@latest        # or bun/pnpm/yarn
brew install anomalyco/tap/opencode # macOS and Linux (recommended)
scoop install opencode              # Windows
sudo pacman -S opencode             # Arch Linux

# Desktop app available for macOS, Windows, Linux
```

### Architecture Summary

- **Language**: TypeScript/Bun
- **Architecture**: Client-server with SSE event backbone
- **Server**: Event streaming and state management
- **Clients**: TUI (React/TSX), Web, Scripts
- **Tools**: Dynamic registry + model-aware tool swapping + plugins

## Core Architecture

### Client-Server Design

OpenCode explicitly has a server that streams events, with clients subscribing:

```
[TUI client]   [Web client]   [Scripts]
       \            |            /
        --> [Server /event SSE + APIs] --> tools/models/state
```

**Why this architecture**:
- Natural multi-client support (TUI, web, remote control)
- Event distribution built-in
- Server owns state, clients render
- Can run agent on one machine, control from another

### The Server

#### SSE Event Endpoint

```typescript
// packages/opencode/src/server/server.ts line 503

app.get(
  "/event",
  describeRoute({ operationId: "event.subscribe" }),
  async (c) => {
    const sessionId = c.req.query("session") || generateSessionId();
    
    return new Response(
      eventStream(sessionId, server.eventBus),
      {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
        },
      }
    );
  }
);

function* eventStream(sessionId: string, eventBus: EventBus): Generator<string> {
  const subscriber = eventBus.subscribe(sessionId);
  
  try {
    for await (const event of subscriber) {
      yield `data: ${JSON.stringify(event)}\n\n`;
    }
  } finally {
    eventBus.unsubscribe(sessionId);
  }
}
```

#### Event Bus

```typescript
class EventBus {
  private subscribers: Map<string, Set<EventCallback>> = new Map();
  
  subscribe(sessionId: string): EventStream {
    if (!this.subscribers.has(sessionId)) {
      this.subscribers.set(sessionId, new Set());
    }
    return new EventStream(sessionId, this);
  }
  
  async publish(event: ServerEvent): Promise<void> {
    for (const callbacks of this.subscribers.values()) {
      for (const callback of callbacks) {
        callback(event);
      }
    }
    
    // Also persist for replay
    await this.eventLogger.log(event);
  }
}
```

### The TUI Client

#### React/TSX Composition

OpenCode's TUI is composed like a web app using React:

```typescript
// packages/opencode/src/cli/cmd/tui/app.tsx

export default function TuiApp() {
  return (
    <ErrorBoundary>
      <ArgsProvider>
        <ExitProvider>
          <KVProvider>
            <ToastProvider>
              <RouteProvider>
                <TuiConfigProvider>
                  <SDKProvider>
                    <App />
                  </SDKProvider>
                </TuiConfigProvider>
              </RouteProvider>
            </ToastProvider>
          </KVProvider>
        </ExitProvider>
      </ArgsProvider>
    </ErrorBoundary>
  );
}
```

**Providers**:
- `ErrorBoundary` - Catch and display errors gracefully
- `ArgsProvider` - Command-line arguments context
- `ExitProvider` - Exit/cancellation handling
- `KVProvider` - Key-value storage for persistence
- `ToastProvider` - Notification system
- `RouteProvider` - Navigation/routing
- `TuiConfigProvider` - TUI configuration
- `SDKProvider` - Server SDK for event subscription

#### Event Subscription

```typescript
// packages/opencode/src/cli/cmd/tui/app.tsx line 676

function useSdkEvents() {
  const sdk = useSdk();
  
  useEffect(() => {
    // Subscribe to tool execution events
    const commandHandler = sdk.event.on(TuiEvent.CommandExecute.type, (evt) => {
      command.trigger(evt.properties.command);
    });
    
    // Subscribe to toast notifications
    const toastHandler = sdk.event.on(TuiEvent.ToastShow.type, (evt) => {
      toast.show({
        title: evt.properties.title,
        message: evt.properties.message,
        variant: evt.properties.variant,
        duration: evt.properties.duration,
      });
    });
    
    // Subscribe to routing events
    const routeHandler = sdk.event.on(TuiEvent.RouteChange.type, (evt) => {
      route.set(evt.properties.path);
    });
    
    return () => {
      commandHandler.dispose();
      toastHandler.dispose();
      routeHandler.dispose();
    };
  }, [sdk]);
}
```

**Key insight**: TUI subscribes to world via SDK events. Everything is reactive.

## Prompt System

### Runtime Selection

OpenCode selects prompt fragments at runtime using model-ID string matching:

```typescript
// packages/opencode/src/prompt/selector.ts

function selectPromptForModel(modelId: string): PromptParts {
  // Model-aware prompt selection
  if (modelId.includes("claude")) {
    return {
      system: readPrompt("prompts/claude-system.md"),
      tools: readPrompt("prompts/claude-tools.md"),
      constraints: readPrompt("prompts/constraints.md"),
    };
  } else if (modelId.includes("gpt-")) {
    return {
      system: readPrompt("prompts/gpt-system.md"),
      tools: readPrompt("prompts/gpt-tools.md"),
      constraints: readPrompt("prompts/constraints.md"),
    };
  } else {
    // Fallback to generic prompts
    return {
      system: readPrompt("prompts/default-system.md"),
      tools: readPrompt("prompts/default-tools.md"),
      constraints: readPrompt("prompts/constraints.md"),
    };
  }
}
```

### Environment Injection

OpenCode injects environment state into prompts:

```typescript
// packages/opencode/src/prompt/builder.ts

function buildSystemPrompt(modelId: string): string {
  const parts = selectPromptForModel(modelId);
  
  return `
${parts.system}

Today's date: ${new Date().toDateString()}
Current directory: ${process.cwd()}
Environment: ${getEnvironmentSummary()}

${parts.constraints}
  `.trim();
}

function getEnvironmentSummary(): string {
  return [
    `Shell: ${process.env.SHELL || 'unknown'}`,
    `User: ${process.env.USER || process.env.USERNAME || 'unknown'}`,
    `Platform: ${process.platform}`,
    `Node: ${process.version}`,
  ].join('\n');
}
```

**Implication**: Prompt bytes are time-dependent. Great for grounding, bad for reproducibility.

### Tool Descriptions as Prompts

OpenCode's tool descriptions do workflow steering:

```markdown
# bash Tool (from bash.txt)

Execute shell commands in a sandboxed environment.

## Usage Guidelines

1. **Think before executing**: Consider what the command does and potential side effects
2. **Use safe defaults**: Prefer `--dry-run`, `-n`, or similar safety flags when available
3. **Check results**: Always verify command output matches expectations
4. **Handle errors**: Check exit codes and error messages
5. **Be explicit**: Use full paths, avoid relying on current directory

## Command Patterns

### Safe exploration (no approval needed)
- `ls -la` to list files
- `cat file.txt` to read files  
- `grep -r "pattern" .` to search codebase

### Requires approval
- File modifications: `rm`, `mv`, `cp --remove-destination`
- Permission changes: `chmod`, `chown`
- Network operations: `curl -X DELETE`, `wget`

### Always blocked
- `sudo` commands
- Destructive operations: `rm -rf /`, `dd if=`
```

**Design choice**: "How to behave" lives close to the tool, not only in global system prompt.

## Tool System

### Dynamic Registry

```typescript
// packages/opencode/src/tool/registry.ts

class ToolRegistry {
  private tools: Map<string, ToolDefinition> = new Map();
  private modelTools: Map<string, string[]> = new Map();
  
  async initialize(): Promise<void> {
    // 1. Load built-in tools
    await this.loadBuiltInTools();
    
    // 2. Load custom tools from config dirs
    await this.loadCustomTools();
    
    // 3. Load plugin tools
    await this.loadPluginTools();
    
    // 4. Build model compatibility map
    this.buildModelCompatibility();
  }
  
  private async loadCustomTools(): Promise<void> {
    const configDirs = [
      '~/.opencode/tools',
      './.opencode/tools',
      './tools',
    ];
    
    const glob = new Bun.Glob("{tool,tools}/*.{js,ts}");
    
    for (const configDir of configDirs) {
      const expandedPath = expandTilde(configDir);
      if (!fs.existsSync(expandedPath)) continue;
      
      for (const match of glob.scanSync(expandedPath)) {
        const mod = await import(match);
        for (const [name, definition] of Object.entries(mod)) {
          if (isToolDefinition(definition)) {
            this.register(name, definition);
          }
        }
      }
    }
  }
  
  private async loadPluginTools(): Promise<void> {
    const plugins = await Plugin.list();
    
    for (const plugin of plugins) {
      for (const [id, def] of Object.entries(plugin.tool ?? {})) {
        const wrappedTool = fromPlugin(id, def);
        this.register(id, wrappedTool);
      }
    }
  }
  
  getToolsForModel(modelId: string): ToolDefinition[] {
    // Model-aware tool swapping
    const compatibleToolNames = this.modelTools.get(modelId) || [];
    return Array.from(this.tools.values())
      .filter(tool => compatibleToolNames.includes(tool.name));
  }
}
```

### Model-Aware Tool Swapping

Different models have different capabilities:

```typescript
// packages/opencode/src/tool/registry.ts

function buildModelCompatibility(): void {
  // GPT models may need simplified tool formats
  const gptTools = ['read', 'edit', 'bash', 'glob', 'ls'];
  modelTools.set('gpt-3.5-turbo', gptTools);
  modelTools.set('gpt-4', gptTools);
  
  // Claude models support full tool set
  const claudeTools = [...gptTools, 'patch', 'apply_patch', 'lsp'];
  modelTools.set('claude-3-sonnet', claudeTools);
  modelTools.set('claude-3.5-sonnet', claudeTools);
  
  // Local models have limited tool support
  const localTools = ['read', 'edit', 'bash'];
  modelTools.set('llama-3-8b', localTools);
}

// Example: Patch tool swapping
const usePatch = 
  model.modelID.includes("gpt-") &&
  !model.modelID.includes("oss") &&
  !model.modelID.includes("gpt-4");

if (usePatch) {
  // Use simplified patch format for GPT models
  registry.register('patch', patchToolSimplified);
} else {
  // Use full patch format for other models
  registry.register('patch', patchToolFull);
}
```

### Built-in Tools

```typescript
// packages/opencode/src/tool/bash.ts

export const bash: ToolDefinition = {
  name: 'bash',
  description: readFileSync('./prompts/tools/bash.txt', 'utf-8'),
  parameters: z.object({
    command: z.string().describe('Shell command to execute'),
    timeout: z.number().optional().describe('Timeout in milliseconds'),
    cwd: z.string().optional().describe('Working directory'),
  }),
  async handler({ command, timeout, cwd }, context) {
    // 1. Parse command with tree-sitter
    const tree = await parser().then(p => p.parse(command));
    const commands = extractCommands(tree);
    
    // 2. Analyze for safety
    const analysis = analyzeCommands(commands);
    
    // 3. Request permissions if needed
    if (analysis.directories.size > 0) {
      await context.ask({
        permission: 'external_directory',
        directories: Array.from(analysis.directories),
        command,
      });
    }
    
    if (analysis.patterns.size > 0) {
      await context.ask({
        permission: 'bash',
        patterns: Array.from(analysis.patterns),
        command,
      });
    }
    
    // 4. Execute with sandbox
    return executeSandboxed(command, { timeout, cwd });
  },
};
```

## Safety System

### AST Parsing for Bash

OpenCode parses bash commands with tree-sitter to understand what they do:

```typescript
// packages/opencode/src/tool/bash.ts line 84-164

async function analyzeCommand(command: string): CommandAnalysis {
  const parser = await getBashParser();
  const tree = parser.parse(command);
  
  const commands: ParsedCommand[] = [];
  const directories = new Set<string>();
  const patterns = new Set<string>();
  
  for (const node of tree.rootNode.descendantsOfType('command')) {
    const cmdNode = node.child(0);
    const args = node.children.slice(1).map(n => n.text.toString());
    
    const cmd: ParsedCommand = {
      command: cmdNode?.text.toString() || '',
      arguments: args,
      risky: isRiskyCommand(cmdNode?.text.toString(), args),
    };
    
    commands.push(cmd);
    
    // Extract paths from arguments
    const paths = extractPaths(args);
    for (const path of paths) {
      if (isDirectory(path)) {
        directories.add(resolvePath(path));
      } else {
        patterns.add(path);
      }
    }
  }
  
  return { commands, directories, patterns };
}

function isRiskyCommand(cmd: string, args: string[]): boolean {
  const dangerousCommands = ['rm', 'sudo', 'dd', 'mkfs', 'fdisk'];
  const dangerousArgs = ['-rf', '--force', '-y', '+y'];
  
  if (dangerousCommands.includes(cmd)) {
    return true;
  }
  
  if (args.some(arg => dangerousArgs.some(d => arg.includes(d)))) {
    return true;
  }
  
  return false;
}
```

### Permission Broker

```typescript
class PermissionBroker {
  async ask(request: PermissionRequest): Promise<boolean> {
    // Emit event for TUI to show approval dialog
    this.eventBus.publish({
      type: TuiEvent.PermissionRequest.type,
      properties: request,
    });
    
    // Wait for user response
    return await this.waitForResponse(request.id);
  }
  
  async checkPermission(permission: string, context: any): Promise<boolean> {
    // Check cached permissions
    const cached = this.cache.get(`${permission}:${JSON.stringify(context)}`);
    if (cached) {
      return cached.approved;
    }
    
    // Request permission
    const approved = await this.ask({
      type: permission,
      context,
    });
    
    // Cache result
    this.cache.set(`${permission}:${JSON.stringify(context)}`, {
      approved,
      timestamp: Date.now(),
    });
    
    return approved;
  }
}
```

## Agent System

### Built-in Agents

OpenCode includes two built-in agents:

```typescript
// packages/opencode/src/agent/registry.ts

const agents = {
  build: {
    name: 'build',
    description: 'Default, full-access agent for development work',
    permissions: ['read', 'write', 'execute'],
    systemPrompt: readPrompt('agents/build.md'),
  },
  plan: {
    name: 'plan',
    description: 'Read-only agent for analysis and code exploration',
    permissions: ['read'],
    systemPrompt: readPrompt('agents/plan.md'),
    constraints: [
      'Denies file edits by default',
      'Asks permission before running bash commands',
      'Ideal for exploring unfamiliar codebases or planning changes',
    ],
  },
};

// General subagent for complex searches
const generalSubagent = {
  name: 'general',
  description: 'Subagent for complex searches and multistep tasks',
  invokeWith: '@general',
};
```

### Agent Switching

```typescript
function useAgentSwitching() {
  const [currentAgent, setCurrentAgent] = useState('build');
  
  // Listen for Tab key to switch agents
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Tab' && e.ctrlKey) {
        e.preventDefault();
        const agentsList = Object.keys(agents);
        const currentIndex = agentsList.indexOf(currentAgent);
        const nextIndex = (currentIndex + 1) % agentsList.length;
        setCurrentAgent(agentsList[nextIndex]);
      }
    };
    
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [currentAgent]);
  
  return currentAgent;
}
```

## Extensibility

### Plugin System

```typescript
// packages/opencode/src/plugin/system.ts

export class Plugin {
  static async list(): Promise<PluginInstance[]> {
    const pluginDirs = ['~/.opencode/plugins', './.opencode/plugins'];
    const plugins: PluginInstance[] = [];
    
    for (const dir of pluginDirs) {
      const expandedPath = expandTilde(dir);
      if (!fs.existsSync(expandedPath)) continue;
      
      const entries = fs.readdirSync(expandedPath);
      for (const entry of entries) {
        if (entry.endsWith('.js') || entry.endsWith('.ts')) {
          const plugin = await import(path.join(expandedPath, entry));
          if (isPlugin(plugin.default)) {
            plugins.push(plugin.default);
          }
        }
      }
    }
    
    return plugins;
  }
}

interface PluginInstance {
  name: string;
  version: string;
  tool?: Record<string, ToolDefinition>;
  provider?: ProviderDefinition;
  middleware?: Middleware[];
}
```

### Example Plugin

```typescript
// ~/.opencode/plugins/github.ts

export default {
  name: 'github',
  version: '1.0.0',
  tool: {
    github_create_pr: {
      description: 'Create a pull request on GitHub',
      parameters: z.object({
        title: z.string(),
        body: z.string(),
        branch: z.string(),
        base: z.string().default('main'),
      }),
      async handler({ title, body, branch, base }, context) {
        const token = context.env.GITHUB_TOKEN;
        if (!token) {
          throw new Error('GITHUB_TOKEN environment variable required');
        }
        
        const response = await fetch('https://api.github.com/repos/.../pulls', {
          method: 'POST',
          headers: {
            'Authorization': `token ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ title, body, head: branch, base }),
        });
        
        return response.json();
      },
    },
  },
};
```

## Configuration

### Config File

```typescript
// ~/.opencode/config.json

{
  "models": {
    "default": "claude-3.5-sonnet",
    "providers": {
      "anthropic": {
        "apiKeyEnv": "ANTHROPIC_API_KEY"
      },
      "openai": {
        "apiKeyEnv": "OPENAI_API_KEY"
      }
    }
  },
  "agents": {
    "default": "build"
  },
  "tools": {
    "enabled": ["read", "edit", "bash", "glob", "ls"],
    "disabled": []
  },
  "safety": {
    "approvalPolicy": "dangerous",
    "allowedPaths": ["./src", "./test"],
    "deniedPaths": ["/etc", "~/.ssh"]
  },
  "plugins": {
    "enabled": ["github", "docker"]
  }
}
```

## Comparison with Alternatives

| Aspect | OpenCode | Codex | Claude Code |
|--------|----------|-------|-------------|
| **Architecture** | Client-server SSE | Single-process monolith | Proprietary |
| **Language** | TypeScript/Bun | Rust | Proprietary |
| **Prompts** | Runtime model-ID matching | Compiled + overlays | Proprietary |
| **Tools** | Dynamic registry + plugins | Compiled + MCP | Proprietary |
| **Safety** | AST parsing + permission broker | Orchestrator + sandbox | Proprietary |
| **Extensibility** | First-class plugins | MCP runtime component | Limited |
| **Clients** | TUI (React), Web, Scripts | TUI, VS Code, Desktop | CLI only |
| **Provider Support** | Any (Anthropic, OpenAI, Google, local) | Any (Responses API) | Anthropic only |

## Key Design Decisions

### 1. Client-Server Over Monolith

**Decision**: Server streams events, clients subscribe.

**Rationale**: Natural multi-client support, remote control, event distribution built-in.

**Trade-off**: Versioning, consistency, reconnect logic complexity.

### 2. Runtime Prompt Selection

**Decision**: Select prompts at runtime using model-ID matching.

**Rationale**: Flexible, supports any model without recompiling.

**Trade-off**: Harder to predict behavior, model IDs treated as truth.

### 3. Dynamic Tool Registry

**Decision**: Load tools from config dirs and plugins at runtime.

**Rationale**: Fast iteration, "ship behavior" as plugins, no recompiling.

**Trade-off**: Harder auditing, runtime composition is security surface.

### 4. AST Parsing for Safety

**Decision**: Parse bash commands to understand before executing.

**Rationale**: Pre-execution understanding enables better approvals.

**Trade-off**: Can miss edge cases, relies on parser quality.

### 5. React/TSX for TUI

**Decision**: Build TUI like web app with React components.

**Rationale**: Surface area and discoverability, routing, dialogs, toasts.

**Trade-off**: More overhead than terminal-native approach.

### 6. Provider-Agnostic Design

**Decision**: Support any LLM provider through pluggable providers.

**Rationale**: Not coupled to any provider, models evolve and pricing drops.

**Trade-off**: Need to handle different API shapes and capabilities.

## References

- **OpenCode GitHub**: https://github.com/anomalyco/opencode
- **Documentation**: https://opencode.ai/docs
- **Discord**: https://discord.gg/opencode
- **Contributing Guide**: https://github.com/anomalyco/opencode/blob/dev/CONTRIBUTING.md

## Key Takeaways

1. **Client-server architecture** - SSE event backbone enables multi-client support and remote control
2. **Runtime prompt selection** - Model-ID matching allows flexibility but harder to predict
3. **Dynamic tool registry** - Load tools from config dirs and plugins without recompiling
4. **Model-aware tool swapping** - Different tool sets for different model capabilities
5. **AST parsing for safety** - Understand commands before executing with tree-sitter
6. **Permission broker pattern** - Centralized approval system with caching
7. **React/TSX TUI** - Web-like composition for discoverability and surface area
8. **First-class plugins** - Tools, providers, middleware all pluggable
9. **Provider-agnostic design** - Support any LLM through pluggable provider system
10. **Built-in agent switching** - Build (full-access) vs Plan (read-only) agents

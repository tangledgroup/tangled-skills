# Tool Systems

How production agents implement tool registries, orchestration, and model-aware tool swapping.

## Core Concepts

### What Is a Tool?

A tool is any capability the agent can invoke: file operations, shell commands, API calls, database queries, or custom functions. Each tool should define:

1. **Name**: Unique identifier (e.g., `read_file`, `execute_bash`)
2. **Description**: What it does and when to use it
3. **Argument schema**: Typed parameters with validation
4. **Multi-modal support**: Images, videos, files as inputs/outputs
5. **Permissions**: What approvals are required

### Tool Registry Pattern

```typescript
interface ToolDefinition {
  name: string;
  description: string;
  parameters: z.ZodType; // Schema for validation
  handler: (args: any, context: ToolContext) => Promise<ToolResult>;
  requiresApproval?: boolean;
  modelCompatibility?: string[]; // Which models support this tool
}

const toolRegistry = new Map<string, ToolDefinition>();
```

## Codex: Centralized Orchestrator

### Architecture

Compiled tool handlers plus centrally routed runtime tools through single pipeline:

```rust
pub trait ToolHandler: Send + Sync {
    fn kind(&self) -> ToolKind;
    fn name(&self) -> ToolName;
    async fn handle(&self, request: &Request, context: &ToolCtx) -> ToolResult;
}

pub struct ToolOrchestrator {
    handlers: HashMap<ToolName, Box<dyn ToolHandler>>,
    approval_policy: ApprovalPolicy,
    sandbox_config: SandboxConfig,
}
```

**Source**: `codex-rs/core/src/tools/registry.rs`

### The Orchestrator Pattern

Single control point where policy is enforced for every tool call:

```rust
impl ToolOrchestrator {
    pub async fn run(
        &mut self,
        tool: &mut dyn ToolHandler,
        req: &Request,
        tool_ctx: &ToolCtx,
        turn_ctx: &TurnContext,
        approval_policy: AskForApproval,
    ) -> Result<Output, ToolError> {
        // 1. Validate request against schema
        self.validate(req)?;
        
        // 2. Check approval policy
        if self.requires_approval(tool, req) {
            self.request_approval(tool, req, approval_policy).await?;
        }
        
        // 3. Apply sandbox constraints
        let sandboxed_req = self.sandbox.apply(req);
        
        // 4. Execute tool
        let result = tool.handle(&sandboxed_req, tool_ctx).await;
        
        // 5. Log for replay
        self.event_log.log_tool_call(tool.name(), req, &result);
        
        Ok(result)
    }
}
```

**Source**: `codex-rs/core/src/tools/orchestrator.rs`

### Benefits

- **Fewer ways for behavior to differ**: Tools are compiled, typed, centrally routed
- **Single policy enforcement point**: All approvals and safety checks in one place
- **Easier auditing**: One code path to review for security
- **Consistent error handling**: Centralized error types and recovery

### Trade-offs

- **Less flexible**: Adding tools requires recompiling (for built-in tools)
- **Tighter coupling**: Tool system is part of core binary
- **Slower iteration**: New tools need release cycle (unless using MCP)

## OpenCode: Dynamic Registry

### Architecture

Intentionally composable at runtime with model-aware tool swapping:

```typescript
// packages/opencode/src/tool/registry.ts

class ToolRegistry {
  private tools: Map<string, ToolDefinition> = new Map();
  private modelTools: Map<string, string[]> = new Map(); // Model ID -> compatible tools
  
  async initialize() {
    // 1. Load built-in tools
    await this.loadBuiltInTools();
    
    // 2. Load custom tools from config dirs
    await this.loadCustomTools();
    
    // 3. Load plugin tools
    await this.loadPluginTools();
    
    // 4. Build model compatibility map
    this.buildModelCompatibility();
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

Different models have different capabilities. OpenCode swaps tools based on model:

```typescript
// Example: GPT models may not support certain tool formats
const usePatch = 
  model.modelID.includes("gpt-") &&
  !model.modelID.includes("oss") &&
  !model.modelID.includes("gpt-4");

if (usePatch) {
  // Use simplified patch format for GPT models
  registry.register(patchToolSimplified);
} else {
  // Use full patch format for other models
  registry.register(patchToolFull);
}
```

### Dynamic Tool Loading

```typescript
// Load tools dynamically from config dirs
const glob = new Bun.Glob("{tool,tools}/*.{js,ts}");
for (const match of glob.scanSync(configDirs)) {
  const mod = await import(match);
  for (const [name, definition] of Object.entries(mod)) {
    registry.register(name, definition);
  }
}

// Inject plugin tools into registry
const plugins = await Plugin.list();
for (const plugin of plugins) {
  for (const [id, def] of Object.entries(plugin.tool ?? {})) {
    const wrappedTool = fromPlugin(id, def);
    registry.register(id, wrappedTool);
  }
}
```

### Benefits

- **Faster iteration**: New tools without forking core or recompiling
- **Model optimization**: Different tool sets for different model capabilities
- **Plugin ecosystem**: "Ship behavior" as plugins
- **Runtime flexibility**: Tools can be added/removed without restart

### Trade-offs

- **Harder auditing**: "What tools exist?" becomes configuration-dependent
- **Security surface**: Runtime composition is potential entry point for malicious code
- **Versioning complexity**: Tools may break with model updates
- **Consistency challenges**: Different tool sets across models can confuse users

## Tool Categories

### File Operations

```typescript
const fileTools = {
  read_file: {
    description: "Read contents of a file",
    parameters: z.object({
      path: z.string().describe("File path to read"),
      offset: z.number().optional().describe("Line offset for large files"),
      limit: z.number().optional().describe("Max lines to read")
    })
  },
  edit_file: {
    description: "Edit a file with precise replacements",
    parameters: z.object({
      path: z.string(),
      edits: z.array(z.object({
        oldText: z.string(),
        newText: z.string()
      }))
    }),
    requiresApproval: true
  },
  write_file: {
    description: "Write content to a file",
    parameters: z.object({
      path: z.string(),
      content: z.string()
    }),
    requiresApproval: true
  }
};
```

### Shell Execution

```typescript
const bashTool = {
  name: "execute_bash",
  description: `Execute shell commands in a sandboxed environment.
  
Usage Guidelines:
1. Think before executing - consider side effects
2. Use safe defaults (--dry-run, -n flags)
3. Check results and exit codes
4. Be explicit with full paths

Safe operations: ls, cat, grep, find
Dangerous operations (require approval): rm, mv, sudo`,
  parameters: z.object({
    command: z.string(),
    timeout: z.number().optional(),
    cwd: z.string().optional()
  }),
  async handler({ command, timeout, cwd }, context) {
    // AST parsing for safety analysis
    const tree = await parser().then(p => p.parse(command));
    const commands = extractCommands(tree);
    
    // Permission checks
    const dangerousCommands = commands.filter(isDangerous);
    if (dangerousCommands.length > 0) {
      await context.ask({
        permission: "bash",
        commands: dangerousCommands
      });
    }
    
    // Execute with sandbox
    return executeSandboxed(command, { timeout, cwd });
  }
};
```

**Source**: Based on `packages/opencode/src/tool/bash.ts`

### Search and Discovery

```typescript
const searchTools = {
  grep: {
    description: "Search for patterns in files",
    parameters: z.object({
      pattern: z.string(),
      paths: z.array(z.string()).optional(),
      exclude: z.array(z.string()).optional()
    })
  },
  ripgrep: {
    description: "Fast code search using ripgrep",
    parameters: z.object({
      query: z.string(),
      glob: z.string().optional(),
      case_sensitive: z.boolean().optional()
    })
  },
  semantic_search: {
    description: "Find semantically similar code",
    parameters: z.object({
      query: z.string(),
      limit: z.number().default(10),
      threshold: z.number().default(0.7)
    })
  }
};
```

### MCP (Model Context Protocol)

MCP provides standardized tool connectivity across agents:

```typescript
// MCP server definition
const mcpServer = {
  name: "git-mcp",
  tools: [
    {
      name: "git_commit",
      description: "Commit changes with message",
      inputSchema: {
        type: "object",
        properties: {
          message: { type: "string" },
          files: { type: "array", items: { type: "string" } }
        }
      }
    }
  ]
};

// Agent discovers and uses MCP tools
const mcpClient = new MCPClient();
await mcpClient.connect(mcpServer);
const availableTools = await mcpClient.listTools();
```

**Codex approach**: MCP treated as runtime component with namespaced tools, routed through same handler model.

**OpenCode approach**: MCP servers merged into tool registry like any other plugin.

## Safety and Approvals

### Approval Patterns

```typescript
enum AskForApproval {
  NEVER,      // Always execute
  ALWAYS,     // Always ask
  DANGEROUS,  // Ask for dangerous operations
  CONFIGURED  // Based on policy configuration
}

interface ApprovalRequest {
  tool: string;
  arguments: any;
  riskLevel: "low" | "medium" | "high";
  description: string;
  consequences: string;
}

async function requestApproval(
  request: ApprovalRequest,
  policy: AskForApproval
): Promise<boolean> {
  if (policy === AskForApproval.NEVER) return true;
  if (policy === AskForApproval.ALWAYS) {
    return await ui.confirm(request);
  }
  
  if (policy === AskForApproval.DANGEROUS && request.riskLevel === "high") {
    return await ui.confirm(request);
  }
  
  return true;
}
```

### Risk Classification

```typescript
function classifyRisk(tool: string, args: any): "low" | "medium" | "high" {
  // File operations
  if (tool === "write_file" || tool === "edit_file") {
    return isCriticalPath(args.path) ? "high" : "medium";
  }
  
  // Shell commands
  if (tool === "execute_bash") {
    if (args.command.match(/rm\s+-rf|sudo|dd\b/)) {
      return "high";
    }
    if (args.command.match(/chmod\s+[7]|chown/)) {
      return "medium";
    }
  }
  
  return "low";
}
```

## Tool Call Streaming

Models must stream tool calls as they happen, not after everything is done. This makes agents feel responsive rather than frozen.

### Three-Phase Streaming Lifecycle

**Phase 1 - Tool call starting**: Model has decided to call a tool. Get tool name and call ID immediately.

```json
{
  "type": "content_block_start",
  "index": 1,
  "content_block": {
    "type": "tool_use",
    "id": "toolu_01T1x...",
    "name": "read_file",
    "input": {}
  }
}
```

UI can already show "Reading main.py..." while model is still generating.

**Phase 2 - Arguments streaming**: Model generates JSON arguments token by token.

```json
{
  "type": "content_block_delta",
  "index": 1,
  "delta": {
    "type": "input_json_delta",
    "partial_json": "{\"path\": \"src/m"
  }
}
{
  "type": "content_block_delta", 
  "index": 1,
  "delta": {
    "type": "input_json_delta",
    "partial_json": "ain.py\"}"
  }
}
```

**Phase 3 - Tool call complete**: Arguments finalized, harness can execute.

```json
{
  "type": "content_block_stop",
  "index": 1
}
```

See [Streaming APIs](06-streaming-apis.md) for complete implementation details.

## Best Practices

### 1. Typed Schemas

Always use typed schemas (Zod, Pydantic, Rust types) for tool arguments:

```typescript
// Good: Typed and validated
parameters: z.object({
  path: z.string().min(1),
  lines: z.number().int().positive()
})

// Bad: Untyped and error-prone
parameters: "object" // No validation
```

### 2. Clear Descriptions

Tool descriptions should include usage guidelines, not just technical specs:

```markdown
# read_file

Read contents of a file. Supports offset/limit for large files.

## When to use
- Understanding existing code before modifying
- Checking configuration values
- Reading documentation

## Tips
- Use offset/limit for large files to avoid context overflow
- Read related files together for better context
- Check file exists before reading (check_file tool)
```

### 3. Model Compatibility

Test tools with different models and adjust as needed:

```typescript
// Some models struggle with complex nested schemas
if (modelId.includes("gpt-3.5")) {
  // Simplify schema for older models
  return simplifiedSchema;
}
return fullSchema;
```

### 4. Error Handling

Tools should return structured errors:

```typescript
interface ToolError {
  code: string;         // "FILE_NOT_FOUND", "PERMISSION_DENIED"
  message: string;      // Human-readable description
  suggestions?: string[]; // How to fix the error
}

// Example error response
{
  error: {
    code: "FILE_NOT_FOUND",
    message: "File 'src/main.py' does not exist",
    suggestions: [
      "Check the path is correct",
      "List directory contents with ls tool",
      "Create the file if it should exist"
    ]
  }
}
```

### 5. Idempotency

Design tools to be idempotent when possible:

```typescript
// write_file is idempotent - same input = same result
await write_file({ path, content }); // Safe to retry

// execute_bash may not be idempotent
await execute_bash({ command: "npm install" }); // May have side effects
```

## Common Mistakes

### ❌ Overly Complex Tool Signatures

```typescript
// Bad: Too many parameters, hard for model to use
const complexTool = {
  parameters: z.object({
    path: z.string(),
    options: z.object({
      recursive: z.boolean(),
      followSymlinks: z.boolean(),
      excludeHidden: z.boolean(),
      maxDepth: z.number(),
      // ... 20 more options
    })
  })
};

// Good: Simple, with defaults
const simpleTool = {
  parameters: z.object({
    path: z.string(),
    recursive: z.boolean().default(false)
  })
};
```

### ❌ Insufficient Descriptions

```typescript
// Bad: Too brief
{
  name: "search",
  description: "Search for things"
}

// Good: Detailed with examples
{
  name: "search",
  description: `Search codebase for patterns using ripgrep.
  
Examples:
- Search for function: search({ query: "functionName", glob: "*.ts" })
- Case-insensitive: search({ query: "TODO", case_sensitive: false })
- Exclude dirs: search({ query: "password", exclude: ["node_modules", ".git"] })`
}
```

### ❌ No Approval for Dangerous Operations

```typescript
// Bad: No safety checks
const deleteFile = {
  parameters: z.object({ path: z.string() }),
  handler: async ({ path }) => fs.unlink(path)
};

// Good: Requires approval
const deleteFile = {
  parameters: z.object({ path: z.string() }),
  requiresApproval: true,
  riskLevel: "high",
  handler: async ({ path }, ctx) => {
    await ctx.ask({ permission: "delete_file", path });
    return fs.unlink(path);
  }
};
```

## References

- **Codex Tool Registry**: https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/registry.rs
- **OpenCode Tool System**: https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/tool/registry.ts
- **MCP Specification**: https://modelcontextprotocol.io
- **Anthropic Tool Use**: https://docs.anthropic.com/en/docs/tool-use

## Key Takeaways

1. **Centralized vs distributed orchestration** - Codex uses single orchestrator, OpenCode uses dynamic registry
2. **Model-aware tool swapping** - Different models may need different tool formats
3. **Typed schemas are essential** - Use Zod/Pydantic for validation
4. **Tool descriptions steer behavior** - They're prompts, not just specs
5. **Approvals based on risk** - Classify operations by danger level
6. **Streaming tool calls** - Model must stream tool decisions as they happen
7. **MCP for extensibility** - Standardized protocol for third-party tools
8. **Error handling matters** - Structured errors with suggestions help agents recover

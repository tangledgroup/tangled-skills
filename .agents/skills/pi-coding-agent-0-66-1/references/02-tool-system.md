# Tool System Architecture

This document covers the tool system implementation in Pi Coding Agent, including built-in tools (read, write, edit, bash, find, grep, ls), custom tool registration, and the extension-based tool framework.

## Tool Architecture Overview

### Three-Layer Tool System

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│   Agent tools (from @mariozechner/pi-agent-core)            │
│   - name, description, parameters (TypeBox schema)          │
│   - execute() function with streaming updates               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Tool Definition Wrapper Layer                   │
│   ToolDefinition (Pi Coding Agent specific)                 │
│   - Wraps AgentTool for TUI rendering                       │
│   - Adds label, icon, and rendering hints                   │
│   - Provides type guards for tool results                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Built-in Tool Implementation Layer              │
│   readTool, writeTool, editTool, bashTool, etc.             │
│   - File system operations                                   │
│   - Bash execution with spawn                                │
│   - Text search (find/grep)                                  │
│   - Directory listing (ls)                                   │
└─────────────────────────────────────────────────────────────┘
```

## Built-in Tools

### Read Tool

Reads file contents with offset/limit support for large files:

```typescript
const readToolDefinition = createReadToolDefinition({
  cwd: process.cwd(),
  maxLines: 2000,
  maxBytes: 50 * 1024, // 50KB limit
});

// Usage in agent
const readTool: AgentTool = {
  name: "read",
  label: "Read",
  description: "Read the contents of a file",
  parameters: Type.Object({
    path: Type.String({ description: "Path to file (relative or absolute)" }),
    offset: Type.Optional(Type.Number({ 
      description: "Line number to start reading from (1-indexed)" 
    })),
    limit: Type.Optional(Type.Number({ 
      description: "Maximum number of lines to read" 
    }))
  }),
  execute: async (toolCallId, params, signal, onUpdate) => {
    const content = await readFileWithTruncation(params.path, {
      offset: params.offset,
      limit: params.limit,
      maxLines: 2000,
      maxBytes: 50 * 1024
    });
    
    return {
      content: [{ type: "text", text: content }],
      details: {
        path: params.path,
        linesRead: countLines(content),
        truncated: content.includes("[truncated]")
      }
    };
  }
};
```

**Key Features:**
- Offset/limit for reading large files incrementally
- Automatic truncation with indicators
- Image file detection (jpg, png, gif, webp)
- Syntax highlighting support via photon-node

### Write Tool

Creates or overwrites files with parent directory creation:

```typescript
const writeToolDefinition = createWriteToolDefinition({
  cwd: process.cwd(),
});

const writeTool: AgentTool = {
  name: "write",
  label: "Write",
  description: "Write content to a file (creates if not exists, overwrites if does)",
  parameters: Type.Object({
    path: Type.String({ description: "Path to file" }),
    content: Type.String({ description: "Content to write" })
  }),
  execute: async (toolCallId, params, signal) => {
    // Ensure parent directory exists
    const dir = dirname(params.path);
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }
    
    // Write content
    writeFileSync(params.path, params.content, "utf-8");
    
    return {
      content: [{ 
        type: "text", 
        text: `Successfully wrote ${params.path} (${params.content.length} bytes)` 
      }],
      details: {
        path: params.path,
        bytesWritten: params.content.length,
        encoding: "utf-8"
      }
    };
  }
};
```

**Key Features:**
- Automatic parent directory creation
- Overwrites existing files
- UTF-8 encoding by default
- Byte count in result details

### Edit Tool

Precise text replacement with exact matching:

```typescript
const editToolDefinition = createEditToolDefinition({
  cwd: process.cwd(),
});

const editTool: AgentTool = {
  name: "edit",
  label: "Edit",
  description: "Edit a file using exact text replacement",
  parameters: Type.Object({
    path: Type.String({ description: "Path to file" }),
    edits: Type.Array(Type.Object({
      oldText: Type.String({ 
        description: "Exact text to replace (must match exactly)" 
      }),
      newText: Type.String({ 
        description: "Replacement text" 
      })
    }))
  }),
  execute: async (toolCallId, params, signal) => {
    const originalContent = readFileSync(params.path, "utf-8");
    let newContent = originalContent;
    
    // Apply each edit sequentially
    for (const edit of params.edits) {
      if (!newContent.includes(edit.oldText)) {
        throw new Error(
          `Edit failed: oldText not found in ${params.path}:\n${edit.oldText}`
        );
      }
      
      newContent = newContent.replace(edit.oldText, edit.newText);
    }
    
    // Write if changed
    if (newContent !== originalContent) {
      writeFileSync(params.path, newContent, "utf-8");
    }
    
    return {
      content: [{ 
        type: "text", 
        text: params.edits.length + 
              ` edit(s) applied to ${params.path}` 
      }],
      details: {
        path: params.path,
        editsApplied: params.edits.length,
        originalSize: originalContent.length,
        newSize: newContent.length
      }
    };
  }
};
```

**Key Features:**
- Exact text matching (no regex)
- Multiple disjoint edits in one call
- Atomic operation (all or nothing)
- No-op if content unchanged

### Bash Tool

Executes shell commands with timeout and output limits:

```typescript
const bashToolDefinition = createBashToolDefinition({
  cwd: process.cwd(),
  timeout: 60000, // 60 seconds
  maxOutputLines: 2000,
  maxOutputBytes: 50 * 1024,
});

const bashTool: AgentTool = {
  name: "bash",
  label: "Bash",
  description: "Execute a bash command",
  parameters: Type.Object({
    command: Type.String({ description: "Command to execute" }),
    timeout: Type.Optional(Type.Number({ 
      description: "Timeout in seconds (default: 60)" 
    }))
  }),
  execute: async (toolCallId, params, signal, onUpdate) => {
    const result = await executeBashWithOperations({
      command: params.command,
      cwd: process.cwd(),
      timeout: (params.timeout || 60) * 1000,
      maxOutputLines: 2000,
      maxOutputBytes: 50 * 1024,
      signal
    });
    
    return {
      content: [
        { type: "text", text: result.stdout || "" },
        { type: "text", text: result.stderr ? `STDERR:\n${result.stderr}` : "" }
      ].filter(c => c.text),
      details: {
        command: params.command,
        exitCode: result.exitCode,
        stdoutLength: result.stdout?.length || 0,
        stderrLength: result.stderr?.length || 0,
        timedOut: result.timedOut
      }
    };
  }
};
```

**Key Features:**
- Timeout protection (default 60s)
- Output truncation (2000 lines or 50KB)
- Exit code tracking
- Separate stdout/stderr handling
- Signal-based abort support

### Find Tool

Searches for files using glob patterns:

```typescript
const findToolDefinition = createFindToolDefinition({
  cwd: process.cwd(),
});

const findTool: AgentTool = {
  name: "find",
  label: "Find",
  description: "Find files matching a pattern",
  parameters: Type.Object({
    path: Type.String({ description: "Directory to search" }),
    pattern: Type.Optional(Type.String({ 
      description: "Glob pattern (e.g., '*.ts')" 
    })),
    maxResults: Type.Optional(Type.Number({ 
      description: "Maximum results (default: 100)" 
    }))
  }),
  execute: async (toolCallId, params) => {
    const files = await findFiles(params.path, {
      pattern: params.pattern,
      maxResults: params.maxResults || 100
    });
    
    return {
      content: [{ 
        type: "text", 
        text: files.join("\n") || "No files found" 
      }],
      details: {
        path: params.path,
        pattern: params.pattern,
        count: files.length
      }
    };
  }
};
```

### Grep Tool

Searches for patterns in file contents:

```typescript
const grepToolDefinition = createGrepToolDefinition({
  cwd: process.cwd(),
});

const grepTool: AgentTool = {
  name: "grep",
  label: "Grep",
  description: "Search for patterns in files",
  parameters: Type.Object({
    pattern: Type.String({ description: "Regex pattern to search" }),
    path: Type.String({ description: "File or directory to search" }),
    include: Type.Optional(Type.String({ 
      description: "Include files matching glob (e.g., '*.ts')" 
    })),
    exclude: Type.Optional(Type.String({ 
      description: "Exclude files matching glob" 
    }))
  }),
  execute: async (toolCallId, params) => {
    const results = await grepFiles(params.path, {
      pattern: params.pattern,
      include: params.include,
      exclude: params.exclude
    });
    
    return {
      content: [{ 
        type: "text", 
        text: formatGrepResults(results) 
      }],
      details: {
        pattern: params.pattern,
        matches: results.length
      }
    };
  }
};
```

### Ls Tool

Lists directory contents with optional filtering:

```typescript
const lsToolDefinition = createLsToolDefinition({
  cwd: process.cwd(),
});

const lsTool: AgentTool = {
  name: "ls",
  label: "Ls",
  description: "List directory contents",
  parameters: Type.Object({
    path: Type.String({ description: "Directory path" }),
    pattern: Type.Optional(Type.String({ 
      description: "Glob pattern to filter" 
    })),
    recursive: Type.Optional(Type.Boolean({ 
      description: "Recursively list subdirectories" 
    }))
  }),
  execute: async (toolCallId, params) => {
    const entries = await listDirectory(params.path, {
      pattern: params.pattern,
      recursive: params.recursive
    });
    
    return {
      content: [{ type: "text", text: entries.join("\n") }],
      details: {
        path: params.path,
        count: entries.length
      }
    };
  }
};
```

## Tool Registration System

### Creating Tool Definitions

Tool definitions wrap AgentTools with additional metadata:

```typescript
export function createReadToolDefinition(options: ReadToolOptions): ToolDefinition {
  return {
    name: "read",
    label: "Read File",
    icon: "📖",
    description: "Read the contents of a file",
    parameters: readSchema,
    execute: async (toolCallId, params, signal, onUpdate) => {
      // Implementation...
    }
  };
}

// Wrap for agent use
export function wrapToolDefinition(
  def: ToolDefinition
): AgentTool<any> {
  return {
    name: def.name,
    label: def.label,
    description: def.description,
    parameters: def.parameters,
    execute: def.execute
  };
}
```

### Built-in Tool Set

All built-in tools exported as a set:

```typescript
export const codingTools = [
  readToolDefinition,
  writeToolDefinition,
  editToolDefinition,
  bashToolDefinition,
  findToolDefinition,
  grepToolDefinition,
  lsToolDefinition
];

// Read-only variant (for safe modes)
export const readOnlyTools = [
  readToolDefinition,
  findToolDefinition,
  grepToolDefinition,
  lsToolDefinition
];
```

## Custom Tool Registration

### Via SDK

Register custom tools when creating agent session:

```typescript
import { createAgentSession } from "@mariozechner/pi-coding-agent";

const customTool: ToolDefinition = {
  name: "my_custom_tool",
  label: "My Custom Tool",
  description: "Does something custom",
  parameters: Type.Object({
    input: Type.String()
  }),
  execute: async (toolCallId, params, signal, onUpdate) => {
    // Custom logic
    return {
      content: [{ type: "text", text: `Processed: ${params.input}` }],
      details: { input: params.input }
    };
  }
};

const session = await createAgentSession({
  customTools: [customTool]
});
```

### Via Extensions

Extensions can register tools dynamically:

```typescript
export const myExtension: ExtensionFactory = () => {
  return {
    name: "my-extension",
    version: "1.0.0",
    
    async activate(context) {
      // Register custom tool
      context.registerTool({
        name: "extension_tool",
        label: "Extension Tool",
        description: "Tool from extension",
        parameters: Type.Object({ value: Type.Number() }),
        execute: async (toolCallId, params) => {
          return {
            content: [{ type: "text", text: `Value: ${params.value}` }],
            details: { value: params.value }
          };
        }
      });
    }
  };
};
```

## Tool Result Type Guards

Type-safe result checking:

```typescript
export function isReadToolResult(
  result: AgentToolResult<any>
): result is AgentToolResult<ReadToolDetails> {
  const details = result.details as ReadToolDetails | undefined;
  return details?.path !== undefined;
}

export function isWriteToolResult(
  result: AgentToolResult<any>
): result is AgentToolResult<WriteToolDetails> {
  const details = result.details as WriteToolDetails | undefined;
  return details?.bytesWritten !== undefined;
}

export function isBashToolResult(
  result: AgentToolResult<any>
): result is AgentToolResult<BashToolDetails> {
  const details = result.details as BashToolDetails | undefined;
  return details?.exitCode !== undefined;
}

// Usage
if (isReadToolResult(result)) {
  console.log(`Read ${result.details.linesRead} lines from ${result.details.path}`);
}
```

## Tool Execution Flow

### Complete Pipeline

```typescript
// 1. Model generates tool call
{
  type: "toolCall",
  id: "tool_123",
  name: "read_file",
  arguments: { path: "package.json" }
}

// 2. Agent validates arguments against TypeBox schema
const validatedArgs = validateToolArguments(tool, toolCall);

// 3. beforeToolCall hook (authorization)
if (beforeToolCall) {
  const result = await beforeToolCall({ toolCall, args: validatedArgs });
  if (result?.block) {
    return createErrorResult(result.reason);
  }
}

// 4. Execute tool
const result = await tool.execute(toolCall.id, validatedArgs, signal, onUpdate);

// 5. afterToolCall hook (transformation)
if (afterToolCall) {
  const override = await afterToolCall({ toolCall, result });
  if (override) {
    result = merge(result, override);
  }
}

// 6. Emit events and add to context
emit({ type: "tool_execution_end", result, isError: false });
context.messages.push(toolResultMessage);
```

## Truncation and Limits

### Output Truncation Strategies

Tools implement intelligent truncation:

```typescript
export function truncateHead(
  lines: string[],
  maxLines: number
): string[] {
  if (lines.length <= maxLines) return lines;
  
  const half = Math.floor(maxLines / 2);
  return [
    ...lines.slice(0, half),
    `... ${lines.length - maxLines} lines truncated ...`,
    ...lines.slice(-half)
  ];
}

export function truncateTail(
  lines: string[],
  maxLines: number
): string[] {
  if (lines.length <= maxLines) return lines;
  
  return [
    `... ${lines.length - maxLines} lines truncated ...`,
    ...lines.slice(-maxLines)
  ];
}

export function truncateLine(
  line: string,
  maxWidth: number
): string {
  if (line.length <= maxWidth) return line;
  
  return line.slice(0, maxWidth - 3) + "...";
}
```

### File Size Limits

Read operations enforce size limits:

```typescript
const DEFAULT_MAX_LINES = 2000;
const DEFAULT_MAX_BYTES = 50 * 1024; // 50KB

async function readFileWithTruncation(
  path: string,
  options: { offset?: number; limit?: number; maxLines?: number; maxBytes?: number }
): Promise<string> {
  const stats = await stat(path);
  
  // Check size before reading
  if (stats.size > options.maxBytes) {
    return `[File too large: ${(stats.size / 1024).toFixed(1)}KB > ${options.maxBytes / 1024}KB limit]`;
  }
  
  const content = await readFile(path, "utf-8");
  const lines = content.split("\n");
  
  // Apply offset/limit
  const start = options.offset || 0;
  const end = options.limit ? start + options.limit : undefined;
  const sliced = lines.slice(start, end);
  
  // Check line count
  if (sliced.length > options.maxLines) {
    const truncated = truncateHead(sliced, options.maxLines);
    return truncated.join("\n") + "\n[truncated]";
  }
  
  return sliced.join("\n");
}
```

## Best Practices

1. **Use exact matches for edit tool** - Not regex patterns
2. **Check file existence before write** - Use read first to verify path
3. **Set timeouts for bash commands** - Prevent hanging processes
4. **Use find/grep before bulk operations** - Verify files exist
5. **Handle truncation gracefully** - Check for `[truncated]` markers
6. **Use type guards for results** - Type-safe result handling
7. **Stream large outputs** - Use onUpdate callback for progress
8. **Respect abort signals** - Check signal.aborted in long operations

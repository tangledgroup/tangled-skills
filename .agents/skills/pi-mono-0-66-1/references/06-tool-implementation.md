# Tool Implementation - Deep Dive

This reference document explains how to implement custom tools in pi, including parameter validation, streaming updates, error handling, and integration with the agent's execution flow.

## Tool Fundamentals

A tool is a function the agent can call to interact with the external world. Tools enable the agent to:
- Read and write files
- Execute commands
- Query databases
- Call APIs
- Perform any computation or I/O operation

From the agent's perspective, all tools are equal - whether built-in (read, write, edit, bash) or custom (deploy, test, query_db).

## Tool Definition Structure

Every tool has three components:

### 1. Metadata

**name**: Unique identifier used by the LLM to call the tool. Use snake_case for readability (e.g., `get_weather`, `deploy_app`).

**description**: Natural language explanation of what the tool does. This is crucial - the LLM decides when to use the tool based on this description.

Good descriptions include:
- What the tool does
- When to use it
- What it returns
- Any limitations or side effects

Bad: "Gets weather"
Good: "Get current weather for a city. Returns temperature, conditions, and forecast. Use for weather queries, not historical data."

### 2. Parameters

Parameters are defined using TypeBox schemas, which provide:
- Type safety (TypeScript knows the parameter types)
- Validation (arguments are checked before execution)
- Documentation (descriptions help the LLM use parameters correctly)
- Serialization (schemas are JSON-serializable for transmission)

**Basic types**:
```typescript
Type.String()        // Text
Type.Number()        // Numbers
Type.Boolean()       // True/false
Type.Array(Type.String())  // Arrays
Type.Object({        // Objects
    field: Type.String()
})
```

**Parameter metadata**:
```typescript
Type.String({
    description: "City name (e.g., 'New York')",
    minLength: 1,
    examples: ["London", "Tokyo", "San Francisco"]
})
```

Descriptions help the LLM understand what values are appropriate. Examples show the expected format.

**Optional parameters**:
```typescript
Type.Object({
    city: Type.String(),
    units: Type.Optional(
        StringEnum(['celsius', 'fahrenheit'], {
            description: "Temperature units",
            default: 'celsius'
        })
    )
})
```

Optional parameters have defaults or can be omitted. The LLM learns from descriptions when to specify them.

### 3. Execute Function

The execute function implements the tool's logic:

```typescript
execute: async (toolCallId, args, signal, onUpdate) => {
    // Implementation
    return {
        content: [{ type: "text", text: "Result" }],
        details: { /* optional metadata */ }
    };
}
```

**Parameters**:
- `toolCallId`: Unique ID for this invocation (used for matching results to calls)
- `args`: Validated arguments from the LLM
- `signal`: AbortSignal for cancellation
- `onUpdate`: Callback for streaming progress updates

**Return value**:
- `content`: Array of content blocks (text, images)
- `details`: Optional metadata for UI or extensions

## Parameter Validation Flow

When the LLM calls a tool:

1. **Parse arguments**: JSON string parsed into object
2. **Validate against schema**: TypeBox checks types, constraints, required fields
3. **On validation failure**: Error returned to LLM as tool result with `isError=true`
4. **On validation success**: Execute function runs with typed arguments

**Validation example**:
```typescript
// Tool expects { city: string, year?: number }
LLM calls: { city: "London", year: "2024" }  // year is string, not number

// Validation fails, error returned to LLM:
{
    role: "toolResult",
    toolCallId: "abc123",
    toolName: "get_weather",
    content: [{
        type: "text",
        text: "Validation error: year must be a number, got string"
    }],
    isError: true
}

// LLM can retry with corrected arguments
```

This validation-then-execute pattern ensures tools receive well-formed arguments and the LLM learns from mistakes.

## Streaming Updates

Tools can stream progress updates during long-running operations:

```typescript
execute: async (toolCallId, args, signal, onUpdate) => {
    // Start operation
    onUpdate({ 
        content: [{ type: "text", text: "Starting deployment..." }],
        details: { phase: "init" }
    });
    
    // Check for cancellation
    if (signal.aborted) {
        throw new Error("Operation cancelled");
    }
    
    // Progress update
    await uploadFiles();
    onUpdate({ 
        content: [{ type: "text", text: "Files uploaded, deploying..." }],
        details: { phase: "deploy" }
    });
    
    // Check for cancellation again
    if (signal.aborted) {
        cleanup();
        throw new Error("Operation cancelled");
    }
    
    // Complete
    await deploy();
    return {
        content: [{ type: "text", text: "Deployment complete!" }],
        details: { url: "https://example.com" }
    };
}
```

**Benefits of streaming**:
- User sees progress instead of waiting silently
- Agent can react to intermediate results
- Cancellation checks prevent wasted work

**Update frequency**: Don't spam updates. Use them for meaningful milestones (phase changes, progress percentages, warnings).

## Error Handling

Tools should throw errors for failures, not return error messages as content:

```typescript
// WRONG: Returning error as content
execute: async (...) => {
    if (!fileExists(path)) {
        return { 
            content: [{ type: "text", text: "Error: File not found" }] 
        };
    }
}

// CORRECT: Throwing error
execute: async (...) => {
    if (!fileExists(path)) {
        throw new Error(`File not found: ${path}`);
    }
}
```

**Why throw instead of return?**
- Agent treats thrown errors differently (`isError=true`)
- LLM sees errors as failures to retry, not successful results
- Extensions can handle errors specially (alert user, log to monitoring)
- Consistent error format across all tools

**Error recovery**: When a tool throws:
1. Error caught by agent
2. Tool result created with `isError=true` and error message
3. Result added to conversation
4. LLM sees the error and can:
   - Retry with different arguments
   - Try alternative approach
   - Ask user for help

**Error types**:
- **Validation errors**: Caught before execute runs, returned to LLM
- **Runtime errors**: Thrown during execution, caught by agent
- **Cancellation errors**: Thrown when signal.aborted, cleanup performed

## Content Types

Tool results can include different content types:

### Text Content

Most common - plain text results:
```typescript
return {
    content: [{ type: "text", text: "File contains 42 lines" }]
};
```

### Image Content

Tools can return images (for vision-capable models):
```typescript
return {
    content: [
        { type: "text", text: "Here's the chart showing temperature trends" },
        { 
            type: "image", 
            data: base64EncodedImage,
            mimeType: "image/png"
        }
    ]
};
```

Images in tool results enable:
- Data visualization (charts, graphs)
- Screenshot tools
- Image processing tools
- Visual debugging

The LLM can analyze images if it has vision capabilities.

### Mixed Content

Combine text and images:
```typescript
return {
    content: [
        { type: "text", text: "Found 3 errors in the code:" },
        { type: "image", data: screenshot, mimeType: "image/png" },
        { type: "text", text: "Errors are highlighted in red." }
    ]
};
```

## Details Metadata

Tools can include metadata in the `details` field:

```typescript
return {
    content: [{ type: "text", text: "File written successfully" }],
    details: {
        path: "/path/to/file",
        bytesWritten: 1234,
        encoding: "utf-8"
    }
}
```

**Use cases for details**:
- UI enhancements (show file size, link to file)
- Extension data (audit logs, analytics)
- Tool-specific metadata (HTTP status codes, query execution time)

Details don't go to the LLM - they're for the UI and extensions only.

## Built-in Tool Examples

### Read Tool

Reads file contents with truncation:
```typescript
{
    name: "read",
    description: "Read file contents. Supports line limits and byte limits.",
    parameters: Type.Object({
        path: Type.String({ description: "Path to file" }),
        limit: Type.Optional(Type.Number({ description: "Max lines to read" })),
        offset: Type.Optional(Type.Number({ description: "Starting line number" }))
    }),
    execute: async (_, args) => {
        const content = await fs.readFile(args.path, "utf-8");
        const lines = content.split("\n");
        
        // Apply offset and limit
        const sliced = lines.slice(args.offset || 0, (args.offset || 0) + args.limit);
        const truncated = sliced.join("\n");
        
        return {
            content: [{ type: "text", text: truncated }],
            details: {
                path: args.path,
                totalLines: lines.length,
                returnedLines: sliced.length
            }
        };
    }
}
```

### Write Tool

Writes content to file:
```typescript
{
    name: "write",
    description: "Write content to a file. Creates parent directories if needed. Overwrites existing files.",
    parameters: Type.Object({
        path: Type.String({ description: "Path to file" }),
        content: Type.String({ description: "Content to write" })
    }),
    execute: async (_, args) => {
        // Ensure parent directory exists
        const dir = dirname(args.path);
        await mkdir(dir, { recursive: true });
        
        // Write file
        await fs.writeFile(args.path, args.content, "utf-8");
        
        return {
            content: [{ type: "text", text: `File written successfully` }],
            details: {
                path: args.path,
                bytesWritten: Buffer.byteLength(args.content, "utf-8")
            }
        };
    }
}
```

### Edit Tool

Edits files with precise replacements:
```typescript
{
    name: "edit",
    description: "Edit a file by replacing exact text matches. Each replacement must match uniquely in the file.",
    parameters: Type.Object({
        path: Type.String({ description: "Path to file" }),
        edits: Type.Array(Type.Object({
            oldText: Type.String({ description: "Exact text to find" }),
            newText: Type.String({ description: "Replacement text" })
        }))
    }),
    execute: async (_, args) => {
        let content = await fs.readFile(args.path, "utf-8");
        
        for (const edit of args.edits) {
            if (!content.includes(edit.oldText)) {
                throw new Error(`Text not found: ${edit.oldText.substring(0, 50)}...`);
            }
            
            // Replace first occurrence
            content = content.replace(edit.oldText, edit.newText);
        }
        
        await fs.writeFile(args.path, content, "utf-8");
        
        return {
            content: [{ type: "text", text: `File edited successfully` }],
            details: {
                path: args.path,
                editsApplied: args.edits.length
            }
        };
    }
}
```

### Bash Tool

Executes shell commands:
```typescript
{
    name: "bash",
    description: "Execute a shell command. Returns stdout, stderr, and exit code. Long output is truncated.",
    parameters: Type.Object({
        command: Type.String({ description: "Shell command to execute" }),
        timeout: Type.Optional(Type.Number({ description: "Timeout in seconds" }))
    }),
    execute: async (_, args, signal) => {
        const result = await exec(args.command, {
            timeout: args.timeout ? args.timeout * 1000 : undefined,
            signal: signal
        });
        
        return {
            content: [
                { type: "text", text: `Exit code: ${result.exitCode}\n\n` },
                { type: "text", text: result.stdout || "(no output)" },
                ...(result.stderr ? [{ type: "text", text: `\nErrors:\n${result.stderr}` }] : [])
            ],
            details: {
                command: args.command,
                exitCode: result.exitCode,
                duration: result.duration
            }
        };
    }
}
```

## Tool Best Practices

### Descriptions

**Be specific**: Describe exactly what the tool does, not just its name.

**Include limitations**: If the tool has constraints (file size limits, supported formats), mention them.

**Mention side effects**: If the tool modifies state (writes files, makes API calls), say so.

**Provide examples**: Show typical usage in the description.

### Parameters

**Use descriptive names**: `filePath` not `f`, `maxRetries` not `mr`.

**Add descriptions**: Every parameter should have a description explaining its purpose.

**Set constraints**: Use minLength, maxLength, minimum, maximum to prevent invalid values.

**Provide defaults**: Optional parameters should have sensible defaults.

### Error Messages

**Be actionable**: Tell the user what went wrong and how to fix it.

**Include context**: Show relevant values (paths, IDs) that help diagnose the issue.

**Avoid blame**: "File not found" not "You provided an invalid path".

### Performance

**Check abort signal**: Long-running tools should check `signal.aborted` periodically.

**Stream progress**: Use `onUpdate` for operations taking more than a second.

**Limit output**: Truncate large results to avoid overwhelming context.

**Cache when appropriate**: If a tool's result doesn't change frequently, cache it.

### Security

**Validate inputs**: Even with TypeBox validation, sanitize user input.

**Escape commands**: If building shell commands from parameters, escape special characters.

**Limit permissions**: Tools should use minimal required permissions.

**Log sensitive operations**: Audit log file writes, command executions, API calls.

## Testing Tools

Tools should be tested independently:

**Unit tests**: Test execute function with mock dependencies
```typescript
test("read tool returns file contents", async () => {
    const fsMock = { readFile: async () => "content" };
    const result = await readTool.execute("tool123", { path: "/test/file.txt" }, null, null);
    
    expect(result.content[0].text).toBe("content");
});
```

**Integration tests**: Test tool with real dependencies in isolated environment
```typescript
test("write tool creates file", async () => {
    const testDir = await mkdtemp();
    const path = join(testDir, "test.txt");
    
    await writeTool.execute("tool123", { path, content: "hello" }, null, null);
    
    expect(await fs.readFile(path, "utf-8")).toBe("hello");
});
```

**Validation tests**: Test that invalid arguments are rejected
```typescript
test("edit tool rejects missing oldText", async () => {
    try {
        await editTool.execute("tool123", { path: "/test.txt", edits: [{ newText: "x" }] }, null, null);
        fail("Should have thrown validation error");
    } catch (error) {
        expect(error.message).toContain("oldText is required");
    }
});
```

## Tool Discovery

The LLM learns about tools from their definitions in the system prompt:
```
Available tools:

- read: Read file contents. Supports line limits...
  Parameters: path (string), limit (number?), offset (number?)

- write: Write content to a file...
  Parameters: path (string), content (string)

- my_custom_tool: Does something useful...
  Parameters: ...
```

Tool names and descriptions are what the LLM sees. Parameter types are converted to natural language. Clear naming and descriptions help the LLM use tools correctly.

## Custom Tool Registration

Tools can be registered in multiple ways:

**Via extensions**: Most common - extension's getTools() returns tool definitions

**Via SDK**: Programmatic API for creating tools dynamically

**Via config**: JSON configuration file defining tools (less common)

All registration methods produce the same internal ToolDefinition format. The agent treats all tools equally regardless of source.

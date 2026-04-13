# Tool Execution Pipeline

This document covers the tool execution pipeline in Pi Agent, including preflight validation, execution strategies (parallel vs sequential), and post-processing hooks.

## Tool Definition Structure

### Basic Tool Definition

```typescript
import { Type } from "@sinclair/typebox";

const readFileTool: AgentTool = {
  // Core Tool interface (from pi-ai)
  name: "read_file",
  description: "Read the contents of a file",
  parameters: Type.Object({
    path: Type.String({ 
      description: "Path to the file to read" 
    })
  }),
  
  // Agent-specific additions
  label: "Read File",  // Human-readable name for UI
  
  // Execution function
  execute: async (
    toolCallId: string,
    params: { path: string },
    signal?: AbortSignal,
    onUpdate?: (partial: AgentToolResult) => void
  ): Promise<AgentToolResult> => {
    // Check for abort
    if (signal?.aborted) {
      throw new Error("Operation cancelled");
    }
    
    // Execute tool logic
    const content = await fs.readFile(params.path, "utf-8");
    
    // Stream progress update (optional)
    onUpdate?.({
      content: [{ type: "text", text: `Reading ${params.path}...` }],
      details: { path: params.path, status: "reading" }
    });
    
    // Return result
    return {
      content: [
        { 
          type: "text", 
          text: content,
          textSignature: shortHash(content)  // Optional signature
        }
      ],
      details: {
        path: params.path,
        size: content.length,
        encoding: "utf-8"
      }
    };
  }
};
```

### Tool with Image Results

```typescript
const generateChartTool: AgentTool = {
  name: "generate_chart",
  label: "Generate Chart",
  description: "Create a chart from data",
  parameters: Type.Object({
    type: StringEnum(["bar", "line", "pie"]),
    data: Type.Array(Type.Number()),
    labels: Type.Array(Type.String())
  }),
  
  execute: async (toolCallId: string, params) => {
    const chartBuffer = await generateChart(params);
    const base64Image = chartBuffer.toString("base64");
    
    return {
      content: [
        {
          type: "image",
          data: base64Image,
          mimeType: "image/png"
        },
        {
          type: "text",
          text: "Chart generated successfully"
        }
      ],
      details: {
        chartType: params.type,
        dataPoints: params.data.length
      }
    };
  }
};
```

## Execution Pipeline Overview

### Three-Phase Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                   Tool Call Detected                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
      ┌──────────────────────────────┐
      │  PHASE 1: Preparation        │
      │  - Find tool definition      │
      │  - Prepare arguments         │
      │  - Validate against schema   │
      │  - beforeToolCall hook       │
      └──────────────┬───────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    Blocked?              Allowed?
         │                       │
         ▼                       ▼
  Return error          ┌────────────────┐
  immediately           │ PHASE 2:       │
                        │ Execution      │
                        │ - Call tool    │
                        │ - Stream updates│
                        │ - Handle errors│
                        └───────┬────────┘
                                │
                                ▼
                        ┌────────────────┐
                        │ PHASE 3:       │
                        │ Finalization   │
                        │ - afterToolCall│
                        │ - Emit events  │
                        │ - Add to context│
                        └────────────────┘
```

## Phase 1: Preparation

### Tool Lookup and Argument Preparation

```typescript
async function prepareToolCall(
  currentContext: AgentContext,
  assistantMessage: AssistantMessage,
  toolCall: AgentToolCall,
  config: AgentLoopConfig,
  signal: AbortSignal | undefined
): Promise<PreparedToolCall | ImmediateToolCallOutcome> {
  
  // Step 1: Find tool definition
  const tool = currentContext.tools?.find(t => t.name === toolCall.name);
  
  if (!tool) {
    return {
      kind: "immediate",
      result: createErrorToolResult(`Tool ${toolCall.name} not found`),
      isError: true
    };
  }
  
  // Step 2: Prepare arguments (compatibility shim)
  const preparedToolCall = prepareToolCallArguments(tool, toolCall);
  
  // Step 3: Validate against TypeBox schema
  let validatedArgs: unknown;
  try {
    validatedArgs = validateToolArguments(tool, preparedToolCall);
  } catch (error) {
    return {
      kind: "immediate",
      result: createErrorToolResult(error.message),
      isError: true
    };
  }
  
  // Step 4: beforeToolCall hook (authorization/interception)
  if (config.beforeToolCall) {
    const beforeResult = await config.beforeToolCall(
      {
        assistantMessage,
        toolCall,
        args: validatedArgs,
        context: currentContext
      },
      signal
    );
    
    if (beforeResult?.block) {
      return {
        kind: "immediate",
        result: createErrorToolResult(
          beforeResult.reason || "Tool execution was blocked"
        ),
        isError: true
      };
    }
  }
  
  // All checks passed, return prepared tool call
  return {
    kind: "prepared",
    toolCall,
    tool,
    args: validatedArgs
  };
}
```

### Argument Preparation Shim

Some tools need to transform raw arguments before validation:

```typescript
const flexibleTool: AgentTool = {
  name: "search",
  label: "Search",
  description: "Search with flexible input format",
  parameters: Type.Object({
    query: Type.String(),
    limit: Type.Number(),
    filters: Type.Record(Type.String())
  }),
  
  // Transform raw args to match schema
  prepareArguments: (args: unknown): { 
    query: string; 
    limit: number; 
    filters: Record<string, string> 
  } => {
    if (typeof args === "string") {
      // Handle simple string input
      return {
        query: args,
        limit: 10,
        filters: {}
      };
    }
    
    if (typeof args === "object" && args !== null) {
      // Normalize limit (might be string "10")
      const limit = typeof args.limit === "string" 
        ? parseInt(args.limit, 10) 
        : args.limit || 10;
      
      return {
        query: String(args.query || ""),
        limit,
        filters: args.filters || {}
      };
    }
    
    // Default fallback
    return { query: "", limit: 10, filters: {} };
  },
  
  execute: async (toolCallId, params) => {
    // params is guaranteed to match schema
    const results = await searchDatabase(params);
    return {
      content: [{ type: "text", text: JSON.stringify(results) }],
      details: results
    };
  }
};
```

### beforeToolCall Hook Patterns

#### Authorization Check

```typescript
const agent = new Agent({
  beforeToolCall: async ({ toolCall, args, context }) => {
    // Block dangerous tools for untrusted users
    if (toolCall.name === "delete_file" && !isTrustedUser()) {
      return { 
        block: true, 
        reason: "Delete operations require trusted user status" 
      };
    }
    
    // Rate limit expensive tools
    if (toolCall.name === "generate_report") {
      const lastExecution = getLastExecutionTime(toolCall.name);
      if (Date.now() - lastExecution < 60000) {
        return { 
          block: true, 
          reason: "Please wait 60 seconds between report generations" 
        };
      }
    }
    
    return undefined; // Allow execution
  }
});
```

#### Argument Modification (via blocking + re-prompt)

```typescript
const agent = new Agent({
  beforeToolCall: async ({ toolCall, args }) => {
    // Enforce business rules
    if (toolCall.name === "create_user" && !args.email?.includes("@")) {
      return { 
        block: true, 
        reason: "Email must contain @ symbol. Please ask user for valid email." 
      };
    }
    
    // Prevent dangerous operations
    if (toolCall.name === "bash" && args.command.includes("rm -rf /")) {
      return { 
        block: true, 
        reason: "Dangerous command blocked. Use a safer alternative." 
      };
    }
  }
});
```

#### Context-Authorization

```typescript
const agent = new Agent({
  beforeToolCall: async ({ toolCall, args, context }) => {
    // Check if tool requires previous context
    if (toolCall.name === "write_file") {
      // Ensure we've read the file first
      const hasReadFile = context.messages.some(
        msg => msg.role === "toolResult" && 
               msg.toolName === "read_file" &&
               msg.toolCallId === args.path
      );
      
      if (!hasReadFile) {
        return {
          block: true,
          reason: "Please read the file before attempting to write it"
        };
      }
    }
  }
});
```

## Phase 2: Execution

### Sequential Execution

```typescript
async function executeToolCallsSequential(
  currentContext: AgentContext,
  assistantMessage: AssistantMessage,
  toolCalls: AgentToolCall[],
  config: AgentLoopConfig,
  signal: AbortSignal | undefined,
  emit: AgentEventSink
): Promise<ToolResultMessage[]> {
  const results: ToolResultMessage[] = [];
  
  for (const toolCall of toolCalls) {
    // Emit start event
    await emit({
      type: "tool_execution_start",
      toolCallId: toolCall.id,
      toolName: toolCall.name,
      args: toolCall.arguments
    });
    
    // Prepare tool call (Phase 1)
    const preparation = await prepareToolCall(
      currentContext, assistantMessage, toolCall, config, signal
    );
    
    if (preparation.kind === "immediate") {
      // Blocked or validation error - emit result immediately
      results.push(await emitToolCallOutcome(
        toolCall, preparation.result, preparation.isError, emit
      ));
    } else {
      // Execute tool (Phase 2)
      const executed = await executePreparedToolCall(
        preparation, signal, emit
      );
      
      // Finalize (Phase 3)
      results.push(await finalizeExecutedToolCall(
        currentContext, assistantMessage, preparation, 
        executed, config, signal, emit
      ));
    }
  }
  
  return results;
}
```

### Parallel Execution

```typescript
async function executeToolCallsParallel(
  currentContext: AgentContext,
  assistantMessage: AssistantMessage,
  toolCalls: AgentToolCall[],
  config: AgentLoopConfig,
  signal: AbortSignal | undefined,
  emit: AgentEventSink
): Promise<ToolResultMessage[]> {
  const results: ToolResultMessage[] = [];
  const runnableCalls: PreparedToolCall[] = [];
  
  // Phase 1: Prepare ALL tool calls sequentially
  for (const toolCall of toolCalls) {
    await emit({
      type: "tool_execution_start",
      toolCallId: toolCall.id,
      toolName: toolCall.name,
      args: toolCall.arguments
    });
    
    const preparation = await prepareToolCall(
      currentContext, assistantMessage, toolCall, config, signal
    );
    
    if (preparation.kind === "immediate") {
      // Blocked - emit immediately
      results.push(await emitToolCallOutcome(
        toolCall, preparation.result, preparation.isError, emit
      ));
    } else {
      // Queue for parallel execution
      runnableCalls.push(preparation);
    }
  }
  
  // Phase 2: Execute ALL allowed tools in parallel
  const runningCalls = runnableCalls.map((prepared) => ({
    prepared,
    execution: executePreparedToolCall(prepared, signal, emit)
  }));
  
  // Phase 3: Finalize results in original order
  for (const running of runningCalls) {
    const executed = await running.execution;
    results.push(await finalizeExecutedToolCall(
      currentContext, assistantMessage, running.prepared,
      executed, config, signal, emit
    ));
  }
  
  return results;
}
```

### Tool Execution with Streaming Updates

```typescript
const slowProcessingTool: AgentTool = {
  name: "process_large_dataset",
  label: "Process Large Dataset",
  description: "Process a large dataset with progress updates",
  parameters: Type.Object({
    filePath: Type.String(),
    batchSize: Type.Number()
  }),
  
  execute: async (
    toolCallId: string,
    params: { filePath: string; batchSize: number },
    signal?: AbortSignal,
    onUpdate?: (partial: AgentToolResult) => void
  ) => {
    const totalRecords = await countRecords(params.filePath);
    let processedCount = 0;
    
    for (let offset = 0; offset < totalRecords; offset += params.batchSize) {
      // Check for abort every batch
      if (signal?.aborted) {
        throw new Error("Processing cancelled by user");
      }
      
      // Process batch
      const batch = await readBatch(params.filePath, offset, params.batchSize);
      const results = await processBatch(batch);
      
      processedCount += batch.length;
      const progress = (processedCount / totalRecords) * 100;
      
      // Stream progress update
      onUpdate?.({
        content: [{ 
          type: "text", 
          text: `Processed ${processedCount}/${totalRecords} records (${progress.toFixed(1)}%)` 
        }],
        details: {
          processed: processedCount,
          total: totalRecords,
          progress,
          currentBatch: offset / params.batchSize + 1
        }
      });
    }
    
    return {
      content: [{ 
        type: "text", 
        text: `Successfully processed ${processedCount} records` 
      }],
      details: {
        totalProcessed: processedCount,
        duration: Date.now() - startTime
      }
    };
  }
};
```

## Phase 3: Finalization

### afterToolCall Hook

```typescript
async function finalizeExecutedToolCall(
  currentContext: AgentContext,
  assistantMessage: AssistantMessage,
  prepared: PreparedToolCall,
  executed: ExecutedToolCallOutcome,
  config: AgentLoopConfig,
  signal: AbortSignal | undefined,
  emit: AgentEventSink
): Promise<ToolResultMessage> {
  let result = executed.result;
  let isError = executed.isError;
  
  // Apply afterToolCall hook if configured
  if (config.afterToolCall) {
    const afterResult = await config.afterToolCall(
      {
        assistantMessage,
        toolCall: prepared.toolCall,
        args: prepared.args,
        result,
        isError,
        context: currentContext
      },
      signal
    );
    
    if (afterResult) {
      // Merge semantics - only override provided fields
      result = {
        content: afterResult.content ?? result.content,
        details: afterResult.details ?? result.details
      };
      isError = afterResult.isError ?? isError;
    }
  }
  
  // Emit final events and return tool result message
  return await emitToolCallOutcome(prepared.toolCall, result, isError, emit);
}
```

### afterToolCall Hook Patterns

#### Audit Logging

```typescript
const agent = new Agent({
  afterToolCall: async ({ toolCall, args, result, isError }) => {
    // Log all tool executions to audit trail
    await auditLog.write({
      timestamp: new Date().toISOString(),
      tool: toolCall.name,
      arguments: args,
      succeeded: !isError,
      resultSummary: summarizeResult(result)
    });
    
    // Add audit metadata to successful operations
    if (!isError && ["write_file", "delete_file"].includes(toolCall.name)) {
      return {
        details: {
          ...result.details,
          audited: true,
          auditId: await createAuditEntry(toolCall.name, args)
        }
      };
    }
  }
});
```

#### Result Enrichment

```typescript
const agent = new Agent({
  afterToolCall: async ({ toolCall, result }) => {
    // Add timestamps to file operations
    if (toolCall.name === "read_file") {
      return {
        details: {
          ...result.details,
          accessedAt: new Date().toISOString(),
          accessCount: await incrementAccessCount(toolCall.arguments.path)
        }
      };
    }
    
    // Add cache metadata to API calls
    if (toolCall.name === "fetch_api") {
      return {
        details: {
          ...result.details,
          cached: result.details.fromCache,
          cacheKey: result.details.cacheKey,
          ttl: 3600
        }
      };
    }
  }
});
```

#### Error Transformation

```typescript
const agent = new Agent({
  afterToolCall: async ({ toolCall, result, isError }) => {
    // Redact sensitive info from errors
    if (isError && result.content[0].type === "text") {
      const sanitized = redactSensitiveInfo(result.content[0].text);
      return {
        content: [{ type: "text", text: sanitized }]
      };
    }
    
    // Convert technical errors to user-friendly messages
    if (isError && toolCall.name === "database_query") {
      return {
        content: [{
          type: "text",
          text: "The database operation failed. Please check your query syntax and try again."
        }]
      };
    }
  }
});
```

## Execution Strategy Comparison

### Sequential vs Parallel

| Aspect | Sequential | Parallel |
|--------|-----------|----------|
| **Execution** | One tool at a time | All tools concurrently |
| **Preflight** | Per-tool | All tools first |
| **Speed** | Slower (additive) | Faster (concurrent) |
| **Memory** | Lower | Higher (all results in memory) |
| **Order** | Guaranteed | Results reordered to match original |
| **Use Case** | Dependent tools | Independent tools |

### When to Use Sequential

```typescript
const agent = new Agent({
  toolExecution: "sequential",
  
  // Good for dependent tool calls
  initialState: {
    tools: [
      { name: "read_file" },     // Step 1
      { name: "parse_content" },  // Step 2 (depends on step 1)
      { name: "transform_data" }  // Step 3 (depends on step 2)
    ]
  }
});
```

### When to Use Parallel

```typescript
const agent = new Agent({
  toolExecution: "parallel",  // Default
  
  // Good for independent tool calls
  initialState: {
    tools: [
      { name: "fetch_user_profile" },   // Independent
      { name: "fetch_user_settings" },  // Independent
      { name: "fetch_user_history" }    // Independent
    ]
  }
});
```

## Error Handling

### Tool Execution Errors

```typescript
const flakyTool: AgentTool = {
  name: "external_api",
  label: "External API",
  description: "Call external API (might fail)",
  parameters: Type.Object({ endpoint: Type.String() }),
  
  execute: async (toolCallId, params) => {
    try {
      const response = await fetch(params.endpoint);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      return {
        content: [{ type: "text", text: JSON.stringify(data) }],
        details: data
      };
    } catch (error) {
      // Don't throw - return error result
      return {
        content: [{ 
          type: "text", 
          text: `API call failed: ${error.message}` 
        }],
        details: { error: error.message, endpoint: params.endpoint }
      };
    }
  }
};
```

### Timeout Handling

```typescript
const slowTool: AgentTool = {
  name: "slow_operation",
  label: "Slow Operation",
  description: "Operation with timeout",
  parameters: Type.Object({ input: Type.String() }),
  
  execute: async (toolCallId, params, signal) => {
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error("Operation timed out after 30 seconds"));
      }, 30000);
    });
    
    const operationPromise = performSlowOperation(params);
    
    try {
      const result = await Promise.race([
        operationPromise,
        timeoutPromise
      ]);
      
      return {
        content: [{ type: "text", text: JSON.stringify(result) }],
        details: result
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: error.message }],
        details: { error: error.message }
      };
    }
  }
};
```

## Best Practices

1. **Validate early** - Use TypeBox schemas for argument validation
2. **Check abort signals** - Tools should honor `signal.aborted`
3. **Stream progress** - Use `onUpdate` for long-running operations
4. **Return structured details** - Include metadata in `result.details`
5. **Don't throw in execute** - Return error results instead
6. **Use prepareArguments** - For backward compatibility shims
7. **Block in beforeToolCall** - For authorization and safety checks
8. **Enrich in afterToolCall** - Add audit metadata, transform errors

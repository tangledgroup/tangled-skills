# Usage Patterns and Examples

This document covers common usage patterns, event handling strategies, and state management techniques in Pi Agent.

## Basic Agent Setup

### Minimal Agent

```typescript
import { Agent } from "@mariozechner/pi-agent-core";
import { getModel } from "@mariozechner/pi-ai";

const agent = new Agent({
  initialState: {
    systemPrompt: "You are a helpful assistant.",
    model: getModel("anthropic", "claude-3-5-sonnet")
  }
});

await agent.prompt("Hello, how can you help me?");
```

### Agent with Tools

```typescript
import { Type } from "@mariozechner/pi-ai";

const readFileTool = {
  name: "read_file",
  label: "Read File",
  description: "Read contents of a file",
  parameters: Type.Object({
    path: Type.String({ description: "File path to read" })
  }),
  execute: async (toolCallId: string, params: { path: string }) => {
    const content = await fs.readFile(params.path, "utf-8");
    return {
      content: [{ type: "text", text: content }],
      details: { path: params.path, size: content.length }
    };
  }
};

const agent = new Agent({
  initialState: {
    systemPrompt: "You are a coding assistant.",
    model: getModel("openai", "gpt-4o"),
    tools: [readFileTool]
  }
});

await agent.prompt("What's in package.json?");
```

## Event Subscription Patterns

### Basic Event Listening

```typescript
const agent = new Agent({ initialState });

const unsubscribe = agent.subscribe((event) => {
  console.log(`Event: ${event.type}`);
  
  if (event.type === "message_update") {
    console.log("Partial message:", event.message);
  }
});

await agent.prompt("Hello");

// Cleanup when done
unsubscribe();
```

### Async Event Processing

```typescript
const agent = new Agent({ initialState });

agent.subscribe(async (event) => {
  if (event.type === "tool_execution_end") {
    // Log to database asynchronously
    await logToolExecution(event.toolCallId, event.result);
    
    // Update analytics
    await trackToolUsage(event.toolName);
  }
  
  if (event.type === "agent_end") {
    // Save conversation state
    await saveConversation(agent.state.messages);
  }
});

// Note: prompt() waits for all async listeners to complete
await agent.prompt("Analyze this file");
```

### Conditional Event Handling

```typescript
const agent = new Agent({ initialState });

agent.subscribe((event) => {
  // Only handle text deltas during streaming
  if (event.type === "message_update" && 
      event.assistantMessageEvent?.type === "text_delta") {
    ui.appendText(event.assistantMessageEvent.delta);
  }
  
  // Show tool execution progress
  if (event.type === "tool_execution_start") {
    const progress = ui.showToolProgress(event.toolName);
    
    // Listen for updates
    if (event.type === "tool_execution_update") {
      progress.update(event.partialResult);
    }
  }
});
```

## Streaming UI Patterns

### Real-time Text Display

```typescript
const agent = new Agent({ initialState });

const outputDiv = document.getElementById("output");

agent.subscribe((event) => {
  if (event.type === "message_update") {
    const amEvent = event.assistantMessageEvent;
    
    if (amEvent?.type === "text_delta") {
      outputDiv.textContent += amEvent.delta;
      window.scrollTo(0, document.body.scrollHeight);
    }
    
    if (amEvent?.type === "thinking_delta") {
      thinkingDiv.textContent += amEvent.delta;
    }
  }
});

await agent.prompt("Explain quantum computing");
```

### Tool Execution UI

```typescript
const agent = new Agent({ initialState });

const toolPanel = document.getElementById("tool-panel");

agent.subscribe((event) => {
  switch (event.type) {
    case "tool_execution_start":
      const toolItem = createToolItem(event.toolName, event.args);
      toolPanel.appendChild(toolItem);
      break;
      
    case "tool_execution_update":
      updateToolItem(event.toolCallId, event.partialResult);
      break;
      
    case "tool_execution_end":
      finalizeToolItem(
        event.toolCallId, 
        event.result, 
        event.isError
      );
      break;
  }
});

function createToolItem(name: string, args: any) {
  const div = document.createElement("div");
  div.className = "tool-item executing";
  div.innerHTML = `
    <strong>${name}</strong>
    <pre>${JSON.stringify(args, null, 2)}</pre>
    <div class="spinner"></div>
  `;
  return div;
}
```

### Progress Indicators

```typescript
const agent = new Agent({ initialState });

let currentTurn = 0;
let pendingTools = new Set<string>();

agent.subscribe((event) => {
  switch (event.type) {
    case "turn_start":
      currentTurn++;
      ui.setTurnIndicator(currentTurn);
      ui.showLoading(true);
      break;
      
    case "tool_execution_start":
      pendingTools.add(event.toolCallId);
      ui.setPendingToolCount(pendingTools.size);
      break;
      
    case "tool_execution_end":
      pendingTools.delete(event.toolCallId);
      ui.setPendingToolCount(pendingTools.size);
      break;
      
    case "turn_end":
      ui.showLoading(false);
      ui.showTurnSummary(
        currentTurn, 
        event.toolResults.length
      );
      break;
  }
});
```

## State Management Patterns

### Reading Agent State

```typescript
const agent = new Agent({ initialState });

// Get current state snapshot
const state = agent.state;

console.log("Messages:", state.messages.length);
console.log("Current model:", state.model.id);
console.log("Thinking level:", state.thinkingLevel);
console.log("Is streaming:", state.isStreaming);

// During streaming, get partial message
if (state.isStreaming && state.streamingMessage) {
  const partialContent = state.streamingMessage.content;
  console.log("Generating:", partialContent);
}

// Check pending tool calls
if (state.pendingToolCalls.size > 0) {
  console.log("Executing tools:", [...state.pendingToolCalls]);
}
```

### Modifying Agent State

```typescript
const agent = new Agent({ initialState });

// Update system prompt (affects future turns)
agent.state.systemPrompt = "You are now a senior developer.";

// Change model mid-conversation
agent.state.model = getModel("anthropic", "claude-3-5-sonnet");

// Adjust thinking level
agent.state.thinkingLevel = "high";

// Update tools dynamically
agent.state.tools = [
  ...agent.state.tools, 
  newTool
];

// Clear message history
agent.state.messages = [];
```

### State Persistence

```typescript
const agent = new Agent({ initialState });

// Subscribe to save state after each turn
agent.subscribe(async (event) => {
  if (event.type === "turn_end") {
    const stateSnapshot = {
      systemPrompt: agent.state.systemPrompt,
      modelId: agent.state.model.id,
      thinkingLevel: agent.state.thinkingLevel,
      messages: agent.state.messages.slice(), // Copy array
      toolNames: agent.state.tools.map(t => t.name)
    };
    
    await localStorage.setItem(
      "conversation-state", 
      JSON.stringify(stateSnapshot)
    );
  }
});

// Restore state on page load
function restoreState() {
  const saved = localStorage.getItem("conversation-state");
  if (saved) {
    const state = JSON.parse(saved);
    return {
      systemPrompt: state.systemPrompt,
      model: getModel(state.modelProvider, state.modelId),
      thinkingLevel: state.thinkingLevel,
      messages: state.messages
    };
  }
}

const agent = new Agent({
  initialState: restoreState()
});
```

## Steering and Follow-up Patterns

### User Interruption (Steering)

```typescript
const agent = new Agent({ 
  initialState,
  steeringMode: "one-at-a-time"  // Process one steer per turn
});

// User can interrupt while agent is working
agent.subscribe((event) => {
  if (event.type === "message_update") {
    // Show partial response in UI
    ui.updateResponse(event.message);
  }
});

// Start long-running task
const taskPromise = agent.prompt("Analyze all files in the project");

// User realizes they want to change direction
setTimeout(() => {
  agent.steer("Actually, focus only on TypeScript files");
}, 2000);

await taskPromise;
```

### Batch Steering

```typescript
const agent = new Agent({ 
  initialState,
  steeringMode: "all"  // Process all steers at once
});

// Queue multiple steering messages
agent.steer("Check the database schema");
agent.steer("Also look at the API endpoints");
agent.steer("And review the test coverage");

// All three will be processed in next turn
await agent.prompt("Analyze the codebase");
```

### Follow-up Messages

```typescript
const agent = new Agent({ initialState });

// Start analysis
await agent.prompt("Review this pull request");

// Queue follow-ups for after current task completes
agent.followUp("Then suggest improvements");
agent.followUp("Finally, create a summary");

// Follow-ups will be processed automatically
// after the initial prompt completes
```

### Mixed Steering and Follow-up

```typescript
const agent = new Agent({ initialState });

const mainTask = agent.prompt("Build a REST API");

// User changes mind mid-execution
setTimeout(() => {
  agent.steer("Actually, make it a GraphQL API instead");
}, 1000);

// But also queue follow-ups for later
agent.followUp("Then write tests for it");
agent.followUp("Finally, document the API");

await mainTask;
// Result: steer processed first, then follow-ups
```

### Clearing Queues

```typescript
const agent = new Agent({ initialState });

// Queue some messages
agent.steer("Check database");
agent.followUp("Then summarize");

// User changes mind - clear all queued messages
agent.clearAllQueues();

// Or clear specific queue
agent.clearSteeringQueue();  // Keep follow-ups
agent.clearFollowUpQueue();  // Keep steers

// Check if queues have messages
if (agent.hasQueuedMessages()) {
  console.log("There are pending messages");
}
```

## Tool Usage Patterns

### Tool with Streaming Updates

```typescript
const slowTool = {
  name: "process_large_file",
  label: "Process Large File",
  description: "Process a large file with progress updates",
  parameters: Type.Object({
    path: Type.String(),
    chunks: Type.Number()
  }),
  execute: async (
    toolCallId: string, 
    params: { path: string; chunks: number },
    signal?: AbortSignal,
    onUpdate?: (partial: any) => void
  ) => {
    const totalLines = await countLines(params.path);
    let processed = 0;
    
    for (let i = 0; i < params.chunks; i++) {
      if (signal?.aborted) {
        throw new Error("Processing cancelled");
      }
      
      // Process chunk
      await processChunk(params.path, i, params.chunks);
      processed += totalLines / params.chunks;
      
      // Stream progress update
      onUpdate?.({
        content: [{ 
          type: "text", 
          text: `Processed ${Math.round(processed)} lines` 
        }],
        details: { 
          progress: (processed / totalLines) * 100,
          currentChunk: i + 1,
          totalChunks: params.chunks
        }
      });
    }
    
    return {
      content: [{ type: "text", text: "Processing complete" }],
      details: { totalLines, processed }
    };
  }
};

const agent = new Agent({ initialState: { tools: [slowTool] } });

// UI receives progress updates
agent.subscribe((event) => {
  if (event.type === "tool_execution_update") {
    ui.updateProgress(
      event.toolCallId, 
      event.partialResult.details.progress
    );
  }
});
```

### Tool Authorization

```typescript
const dangerousTool = {
  name: "delete_file",
  label: "Delete File",
  description: "Delete a file (requires authorization)",
  parameters: Type.Object({
    path: Type.String()
  }),
  execute: async (toolCallId: string, params: { path: string }) => {
    fs.unlinkSync(params.path);
    return {
      content: [{ type: "text", text: `Deleted ${params.path}` }],
      details: { path: params.path }
    };
  }
};

const agent = new Agent({
  initialState: { tools: [dangerousTool] },
  
  beforeToolCall: async ({ toolCall, args }) => {
    if (toolCall.name === "delete_file") {
      // Check user permissions
      if (!userHasPermission("file.delete")) {
        return { 
          block: true, 
          reason: "You don't have permission to delete files" 
        };
      }
      
      // Confirm dangerous operation
      if (!await confirmWithUser(`Delete ${args.path}?`)) {
        return { 
          block: true, 
          reason: "Operation cancelled by user" 
        };
      }
    }
    
    return undefined; // Allow execution
  }
});
```

### Tool Result Transformation

```typescript
const agent = new Agent({
  initialState: { tools: [readFileTool] },
  
  afterToolCall: async ({ toolCall, result, isError }) => {
    if (!isError && toolCall.name === "read_file") {
      // Add metadata to result
      return {
        details: {
          ...result.details,
          accessedAt: new Date().toISOString(),
          accessCount: await incrementAccessCount(toolCall.arguments.path)
        }
      };
    }
    
    // Redact sensitive info from errors
    if (isError && result.content[0].type === "text") {
      return {
        content: [{
          type: "text",
          text: redactSensitiveInfo(result.content[0].text)
        }]
      };
    }
  }
});
```

## Context Management Patterns

### Dynamic System Prompt

```typescript
const agent = new Agent({
  initialState: {
    systemPrompt: "You are a helpful assistant.",
    model: getModel("openai", "gpt-4o")
  }
});

// Change behavior mid-conversation
agent.state.systemPrompt = `You are a senior React developer. 
Focus on performance and accessibility.`;

await agent.prompt("How should I structure this component?");
```

### Model Switching

```typescript
const agent = new Agent({
  initialState: {
    systemPrompt: "You are an assistant.",
    model: getModel("openai", "gpt-4o-mini"), // Start with cheap model
    thinkingLevel: "off"
  }
});

await agent.prompt("What's 2 + 2?"); // Simple question, cheap model

// Switch to smarter model for complex task
agent.state.model = getModel("anthropic", "claude-3-5-sonnet");
agent.state.thinkingLevel = "high";

await agent.continue(); // Continues with new model
```

### Context Pruning

```typescript
const agent = new Agent({
  initialState,
  
  transformContext: async (messages) => {
    // Keep system prompt + last 20 messages
    if (messages.length > 21) {
      const [systemPrompt] = messages;
      const recentMessages = messages.slice(-20);
      return [systemPrompt, ...recentMessages];
    }
    
    return messages;
  }
});
```

### Context Injection

```typescript
const agent = new Agent({
  initialState,
  
  transformContext: async (messages) => {
    // Inject user context before each turn
    const userProfile = await fetchUserProfile();
    
    return [
      { 
        role: "user", 
        content: `User context: ${JSON.stringify(userProfile)}`,
        timestamp: Date.now()
      },
      ...messages
    ];
  }
});
```

## Error Handling Patterns

### Graceful Error Recovery

```typescript
const agent = new Agent({ initialState });

agent.subscribe((event) => {
  if (event.type === "turn_end" && event.message.errorMessage) {
    console.error("Turn failed:", event.message.errorMessage);
    
    // Auto-retry on transient errors
    if (isTransientError(event.message.errorMessage)) {
      setTimeout(() => agent.continue(), 1000);
    }
  }
});

try {
  await agent.prompt("Hello");
} catch (error) {
  console.error("Prompt failed:", error);
  // Handle catastrophic failure
}
```

### Abort Handling

```typescript
const agent = new Agent({ initialState });

// User clicks cancel button
const abortButton = document.getElementById("abort");
abortButton.addEventListener("click", () => {
  agent.abort();
  ui.showAbortedMessage();
});

agent.subscribe((event) => {
  if (event.type === "turn_end" && 
      event.message.stopReason === "aborted") {
    ui.showPartialResult(event.message.content);
  }
});

await agent.prompt("Analyze this large codebase");
```

### Tool Error Handling

```typescript
const flakyTool = {
  name: "unreliable_api",
  label: "Unreliable API",
  description: "This tool might fail",
  parameters: Type.Object({ query: Type.String() }),
  execute: async (toolCallId: string, params: { query: string }) => {
    try {
      const result = await fetchExternalApi(params.query);
      return {
        content: [{ type: "text", text: JSON.stringify(result) }],
        details: result
      };
    } catch (error) {
      // Don't throw - return error in content
      return {
        content: [{ 
          type: "text", 
          text: `API error: ${error.message}` 
        }],
        details: { error: error.message }
      };
    }
  }
};

const agent = new Agent({ initialState: { tools: [flakyTool] } });

agent.subscribe((event) => {
  if (event.type === "tool_execution_end" && event.isError) {
    console.log("Tool failed:", event.result);
    // Tool result still added to context, model can handle it
  }
});
```

## Advanced Patterns

### Multi-Agent Coordination

```typescript
const researcher = new Agent({
  initialState: {
    systemPrompt: "You are a research assistant.",
    model: getModel("openai", "gpt-4o"),
    tools: [searchTool, readTool]
  }
});

const writer = new Agent({
  initialState: {
    systemPrompt: "You are a technical writer.",
    model: getModel("anthropic", "claude-3-5-sonnet"),
    tools: [writeFileTool]
  }
});

// Research phase
await researcher.prompt("Research TypeScript performance");
const researchResults = researcher.state.messages;

// Writing phase - pass research to writer
writer.state.messages = researchResults;
await writer.prompt("Write a blog post about the findings");
```

### Conversation Branching

```typescript
const agent = new Agent({ initialState });

// Save state before branching
const branchPoint = {
  messages: agent.state.messages.slice(),
  systemPrompt: agent.state.systemPrompt,
  model: agent.state.model
};

await agent.prompt("What are the pros?");
const prosResponse = agent.state.messages.slice();

// Restore and explore alternative
agent.state.messages = branchPoint.messages;
await agent.prompt("What are the cons?");
const consResponse = agent.state.messages.slice();

// Compare branches
console.log("Pros:", prosResponse);
console.log("Cons:", consResponse);
```

### Rate Limiting

```typescript
let lastRequestTime = 0;
const RATE_LIMIT_MS = 1000; // 1 request per second

const agent = new Agent({
  initialState,
  
  transformContext: async (messages) => {
    const now = Date.now();
    const elapsed = now - lastRequestTime;
    
    if (elapsed < RATE_LIMIT_MS) {
      await sleep(RATE_LIMIT_MS - elapsed);
    }
    
    lastRequestTime = Date.now();
    return messages;
  }
});
```

## Best Practices

1. **Always subscribe before prompting** - Events emitted during prompt won't be caught if you subscribe after
2. **Use async listeners sparingly** - They block prompt resolution
3. **Copy state arrays** - Don't mutate `state.messages` directly
4. **Handle abort signals** - Tools should check `signal.aborted`
5. **Use steering for interruptions** - Not follow-ups
6. **Implement context pruning** - Prevent token limit errors
7. **Log tool executions** - For debugging and audit trails
8. **Test with faux provider** - Validate logic without API costs

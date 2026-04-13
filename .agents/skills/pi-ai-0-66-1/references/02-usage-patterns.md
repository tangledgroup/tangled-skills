# Usage Patterns

## Basic Patterns

### Streaming with Event Handling

```typescript
const s = stream(model, context);

for await (const event of s) {
  switch (event.type) {
    case 'text_delta':
      process.stdout.write(event.delta);
      break;
    case 'toolcall_end':
      const result = await executeTool(event.toolCall);
      // Handle tool result
      break;
    case 'done':
      console.log('Complete');
      break;
  }
}

const finalMessage = await s.result();
```

### Non-Streaming (Complete)

```typescript
const response = await complete(model, context);

for (const block of response.content) {
  if (block.type === 'text') {
    console.log(block.text);
  } else if (block.type === 'toolCall') {
    const result = await executeTool(block);
    // Add result to context and continue
  }
}
```

## Tool Definition Patterns

### Simple Tool

```typescript
const getTimeTool: Tool = {
  name: 'get_time',
  description: 'Get current time',
  parameters: Type.Object({
    timezone: Type.Optional(Type.String())
  })
};
```

### Tool with Validation

```typescript
const createUserTool: Tool = {
  name: 'create_user',
  description: 'Create a new user account',
  parameters: Type.Object({
    email: Type.String({ format: 'email', minLength: 5 }),
    age: Type.Integer({ minimum: 0, maximum: 150 }),
    role: StringEnum(['admin', 'user', 'guest'], { default: 'user' })
  })
};
```

### Tool with Nested Objects

```typescript
const createOrderTool: Tool = {
  name: 'create_order',
  description: 'Create a new order',
  parameters: Type.Object({
    items: Type.Array(Type.Object({
      productId: Type.String(),
      quantity: Type.Integer({ minimum: 1 })
    })),
    shipping: Type.Object({
      address: Type.String(),
      method: StringEnum(['standard', 'express'])
    }),
    metadata: Type.Optional(Type.Record(Type.String()))
  })
};
```

## Context Management Patterns

### Multi-Turn Conversation

```typescript
const context: Context = {
  systemPrompt: 'You are a coding assistant.',
  messages: [],
  tools: [readFileTool, writeFileTool]
};

// Turn 1
context.messages.push({ role: 'user', content: 'Read main.ts' });
const response1 = await complete(model, context);
context.messages.push(response1);

// Handle tool calls
for (const block of response1.content) {
  if (block.type === 'toolCall') {
    const result = await executeTool(block);
    context.messages.push({
      role: 'toolResult',
      toolCallId: block.id,
      toolName: block.name,
      content: [{ type: 'text', text: result }],
      isError: false,
      timestamp: Date.now()
    });
  }
}

// Turn 2
context.messages.push({ role: 'user', content: 'Now fix the bug' });
const response2 = await complete(model, context);
```

### Context Persistence

```typescript
// Save to database
const json = JSON.stringify(context);
await db.conversations.save({ id: '123', data: json });

// Load later
const saved = await db.conversations.find('123');
const context = JSON.parse(saved.data) as Context;

// Continue conversation
context.messages.push({ role: 'user', content: 'Where were we?' });
const response = await complete(model, context);
```

## Reasoning/Thinking Patterns

### Auto-Reasoning (Simple API)

```typescript
// Automatically adjusts based on model capabilities
const s = streamSimple(model, context, {
  reasoning: 'high'  // Model chooses appropriate tokens/effort
});
```

### Manual Reasoning Control

```typescript
// For models with explicit reasoning tokens
const s = stream(model, context, {
  reasoningEffort: 'high',  // OpenAI-specific
  maxTokens: 4096
});

// For Anthropic with thinking budget
const s = stream(model, context, {
  thinkingBudgets: {
    high: 2000  // Reserve 2000 tokens for reasoning
  }
});
```

### Streaming Thinking Content

```typescript
for await (const event of s) {
  if (event.type === 'thinking_delta') {
    process.stdout.write(`[Thinking] ${event.delta}`);
  } else if (event.type === 'text_delta') {
    process.stdout.write(event.delta);
  }
}
```

## Image Input Patterns

### Single Image

```typescript
const context: Context = {
  messages: [{
    role: 'user',
    content: [
      { type: 'text', text: 'What is in this image?' },
      {
        type: 'image',
        data: base64EncodedImage,
        mimeType: 'image/png'
      }
    ]
  }]
};
```

### Multiple Images

```typescript
const context: Context = {
  messages: [{
    role: 'user',
    content: [
      { type: 'text', text: 'Compare these diagrams' },
      { type: 'image', data: img1, mimeType: 'image/png' },
      { type: 'image', data: img2, mimeType: 'image/png' }
    ]
  }]
};
```

## Error Handling Patterns

### Try-Catch with Stream

```typescript
try {
  const s = stream(model, context);
  
  for await (const event of s) {
    if (event.type === 'error') {
      console.error('Stream error:', event.error);
      break;
    }
    // Handle other events...
  }
} catch (error) {
  console.error('Setup error:', error);
}
```

### Abort Handling

```typescript
const controller = new AbortController();

const s = stream(model, context, {
  signal: controller.signal
});

// Abort after 30 seconds
setTimeout(() => controller.abort(), 30000);

try {
  const result = await s.result();
} catch (error) {
  if (error.name === 'AbortError') {
    console.log('Request aborted by user');
  }
}
```

## Advanced Patterns

### Parallel Tool Execution

```typescript
const toolCalls = response.content.filter(b => b.type === 'toolCall');

// Execute all tools in parallel
const results = await Promise.all(
  toolCalls.map(async (call) => {
    const result = await executeTool(call);
    return { call, result };
  })
);

// Add all results to context
for (const { call, result } of results) {
  context.messages.push({
    role: 'toolResult',
    toolCallId: call.id,
    toolName: call.name,
    content: [{ type: 'text', text: result }],
    isError: false,
    timestamp: Date.now()
  });
}
```

### Model Fallback

```typescript
const providers = ['openai', 'anthropic', 'google'];
let lastError;

for (const provider of providers) {
  try {
    const model = getModel(provider, getPreferredModel(provider));
    const response = await complete(model, context);
    return response;
  } catch (error) {
    lastError = error;
    console.warn(`Provider ${provider} failed, trying next...`);
  }
}

throw lastError;
```

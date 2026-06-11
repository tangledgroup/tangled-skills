# pi-ai Package — Unified LLM API

## Contents
- Overview and Installation
- Quick Start
- Streaming API (stream)
- Simple API (streamSimple / completeSimple)
- Complete API (complete)
- Tool Definitions with TypeBox
- Handling Tool Calls
- Streaming Tool Calls with Partial JSON
- Validating Tool Arguments
- Event Reference
- Image Input
- Thinking/Reasoning
- Stop Reasons and Error Handling
- Aborting Requests
- Cross-Provider Handoffs
- Context Serialization
- Custom Models
- OpenAI Compatibility Settings

## Overview and Installation

`@earendil-works/pi-ai` is a unified LLM API with automatic model discovery, provider configuration, token and cost tracking, and context persistence with cross-provider handoffs. Only includes models that support tool calling (function calling).

```bash
npm install @earendil-works/pi-ai
```

TypeBox exports are re-exported: `Type`, `Static`, `TSchema`.

## Quick Start

```typescript
import { Type, getModel, stream, complete, Context, Tool } from '@earendil-works/pi-ai';

const model = getModel('openai', 'gpt-4o-mini');

const tools: Tool[] = [{
  name: 'get_time',
  description: 'Get the current time',
  parameters: Type.Object({
    timezone: Type.Optional(Type.String({ description: 'Optional timezone' }))
  })
}];

const context: Context = {
  systemPrompt: 'You are a helpful assistant.',
  messages: [{ role: 'user', content: 'What time is it?' }],
  tools,
};

// Streaming
const s = stream(model, context);
for await (const event of s) {
  if (event.type === 'text_delta') process.stdout.write(event.delta);
}
const finalMessage = await s.result();
context.messages.push(finalMessage);

// Complete (non-streaming)
const response = await complete(model, context);
console.log(response.content);
console.log(`Tokens: ${finalMessage.usage.input} in, ${finalMessage.usage.output} out`);
console.log(`Cost: $${finalMessage.usage.cost.total.toFixed(4)}`);
```

## Streaming API (stream)

Full event stream with all event types:

```typescript
const s = stream(model, context);
for await (const event of s) {
  switch (event.type) {
    case 'start':
      console.log(`Starting with ${event.partial.model}`);
      break;
    case 'text_delta':
      process.stdout.write(event.delta);
      break;
    case 'thinking_start':
      console.log('[Model is thinking...]');
      break;
    case 'thinking_delta':
      process.stdout.write(event.delta);
      break;
    case 'toolcall_end':
      console.log(`Tool: ${event.toolCall.name}`, event.toolCall.arguments);
      break;
    case 'done':
      console.log(`Finished: ${event.reason}`);
      break;
    case 'error':
      console.error(`Error: ${event.error}`);
      break;
  }
}
```

Streaming events for different content blocks are not guaranteed to be contiguous. Use `contentIndex` to associate each delta/end event with its block.

## Simple API (streamSimple / completeSimple)

Simplified interface with unified thinking option:

```typescript
import { getModel, streamSimple, completeSimple } from '@earendil-works/pi-ai';

const model = getModel('anthropic', 'claude-sonnet-4-20250514');

const response = await completeSimple(model, {
  messages: [{ role: 'user', content: 'Solve: 2x + 5 = 13' }]
}, { reasoning: 'medium' }); // 'minimal' | 'low' | 'medium' | 'high' | 'xhigh'

for (const block of response.content) {
  if (block.type === 'thinking') console.log('Thinking:', block.thinking);
  else if (block.type === 'text') console.log('Response:', block.text);
}
```

## Complete API (complete)

Get complete response without streaming:

```typescript
const response = await complete(model, context);
for (const block of response.content) {
  if (block.type === 'text') console.log(block.text);
  else if (block.type === 'toolCall')
    console.log(`Tool: ${block.name}(${JSON.stringify(block.arguments)})`);
}
```

Provider-specific options:
```typescript
// Anthropic
await complete(anthropicModel, context, { thinkingEnabled: true, thinkingBudgetTokens: 8192 });

// OpenAI
await complete(openaiModel, context, { reasoningEffort: 'medium', reasoningSummary: 'detailed' });

// Google
await complete(googleModel, context, { thinking: { enabled: true, budgetTokens: 8192 } });
```

## Tool Definitions with TypeBox

```typescript
import { Type, Tool, StringEnum } from '@earendil-works/pi-ai';

const weatherTool: Tool = {
  name: 'get_weather',
  description: 'Get current weather for a location',
  parameters: Type.Object({
    location: Type.String({ description: 'City name or coordinates' }),
    units: StringEnum(['celsius', 'fahrenheit'], { default: 'celsius' })
  })
};
```

Use `StringEnum` instead of `Type.Enum` for Google API compatibility.

## Handling Tool Calls

```typescript
const response = await complete(model, context);
for (const block of response.content) {
  if (block.type === 'toolCall') {
    const result = await executeWeatherApi(block.arguments);
    context.messages.push({
      role: 'toolResult',
      toolCallId: block.id,
      toolName: block.name,
      content: [{ type: 'text', text: JSON.stringify(result) }],
      isError: false,
      timestamp: Date.now(),
    });
  }
}

// Tool results can include images (for vision-capable models)
context.messages.push({
  role: 'toolResult',
  toolCallId: 'tool_xyz',
  toolName: 'generate_chart',
  content: [
    { type: 'text', text: 'Generated chart' },
    { type: 'image', data: imageBuffer.toString('base64'), mimeType: 'image/png' },
  ],
  isError: false,
  timestamp: Date.now(),
});

// Continue if there were tool calls
if (toolCalls.length > 0) {
  const continuation = await complete(model, context);
  context.messages.push(continuation);
}
```

## Streaming Tool Calls with Partial JSON

During streaming, tool arguments are progressively parsed:

```typescript
for await (const event of s) {
  if (event.type === 'toolcall_delta') {
    const toolCall = event.partial.content[event.contentIndex];
    // BE DEFENSIVE: arguments may be incomplete
    if (toolCall.type === 'toolCall' && toolCall.arguments) {
      if (toolCall.name === 'write_file' && toolCall.arguments.path) {
        console.log(`Writing to: ${toolCall.arguments.path}`);
      }
    }
  }
  if (event.type === 'toolcall_end') {
    const toolCall = event.toolCall;
    // Complete (but not yet validated)
    console.log(`Tool: ${toolCall.name}`, toolCall.arguments);
  }
}
```

During `toolcall_delta`: fields may be missing, strings truncated, arrays incomplete. `arguments` is always at minimum `{}`.

## Validating Tool Arguments

```typescript
import { stream, validateToolCall, Tool } from '@earendil-works/pi-ai';

const tools: Tool[] = [weatherTool];
const s = stream(model, { messages, tools });
for await (const event of s) {
  if (event.type === 'toolcall_end') {
    try {
      const validatedArgs = validateToolCall(tools, event.toolCall);
      const result = await executeMyTool(event.toolCall.name, validatedArgs);
      // Add tool result to context...
    } catch (error) {
      context.messages.push({
        role: 'toolResult',
        toolCallId: event.toolCall.id,
        toolName: event.toolCall.name,
        content: [{ type: 'text', text: error.message }],
        isError: true,
        timestamp: Date.now(),
      });
    }
  }
}
```

## Event Reference

| Event Type | Description | Key Properties |
|------------|-------------|----------------|
| `start` | Stream begins | `partial`: Initial assistant message |
| `text_start` | Text block starts | `contentIndex` |
| `text_delta` | Text chunk received | `delta`, `contentIndex` |
| `text_end` | Text block complete | `content`, `contentIndex` |
| `thinking_start` | Thinking block starts | `contentIndex` |
| `thinking_delta` | Thinking chunk received | `delta`, `contentIndex` |
| `thinking_end` | Thinking block complete | `content`, `contentIndex` |
| `toolcall_start` | Tool call begins | `contentIndex` |
| `toolcall_delta` | Tool args streaming | `delta`, `partial.content[contentIndex].arguments` |
| `toolcall_end` | Tool call complete | `toolCall`: `{ id, name, arguments }` |
| `done` | Stream complete | `reason`: `"stop"`, `"length"`, `"toolUse"` |
| `error` | Error occurred | `reason`: `"error"` or `"aborted"`, `error` |

## Image Input

```typescript
import { readFileSync } from 'fs';

const model = getModel('openai', 'gpt-4o-mini');
if (model.input.includes('image')) console.log('Model supports vision');

const imageBuffer = readFileSync('image.png');
const response = await complete(model, {
  messages: [{
    role: 'user',
    content: [
      { type: 'text', text: 'What is in this image?' },
      { type: 'image', data: imageBuffer.toString('base64'), mimeType: 'image/png' },
    ],
  }],
});
```

Images passed to non-vision models are silently ignored.

## Thinking/Reasoning

Check if model supports reasoning: `if (model.reasoning)`. If passed to non-reasoning model, silently ignored.

Streaming thinking content:
```typescript
const s = streamSimple(model, context, { reasoning: 'high' });
for await (const event of s) {
  if (event.type === 'thinking_delta') process.stdout.write(event.delta);
}
```

## Stop Reasons and Error Handling

`stopReason` values: `"stop"`, `"length"`, `"toolUse"`, `"error"`, `"aborted"`.

```typescript
const message = await stream.result();
if (message.stopReason === 'error' || message.stopReason === 'aborted') {
  console.error('Failed:', message.errorMessage);
  // message.content contains partial content
  // message.usage contains partial token counts and costs
}
```

## Aborting Requests

```typescript
const controller = new AbortController();
setTimeout(() => controller.abort(), 2000);

const s = stream(model, context, { signal: controller.signal });
for await (const event of s) {
  if (event.type === 'error') {
    console.log(`${event.reason === 'aborted' ? 'Aborted' : 'Error'}:`, event.error.errorMessage);
  }
}

// Aborted messages can be added to context and continued
const partial = await complete(model, context, { signal: controller.signal });
context.messages.push(partial);
context.messages.push({ role: 'user', content: 'Please continue' });
const continuation = await complete(model, context);
```

## Cross-Provider Handoffs

Seamless handoffs between different LLM providers within the same conversation:

```typescript
const claude = getModel('anthropic', 'claude-sonnet-4-20250514');
const gpt5 = getModel('openai', 'gpt-5-mini');
const gemini = getModel('google', 'gemini-2.5-flash');

const context: Context = { messages: [] };
context.messages.push({ role: 'user', content: 'What is 25 * 18?' });

const claudeResponse = await complete(claude, context, { thinkingEnabled: true });
context.messages.push(claudeResponse);

// Switch to GPT-5 — sees Claude's thinking as <thinking> tagged text
context.messages.push({ role: 'user', content: 'Is that correct?' });
const gptResponse = await complete(gpt5, context);
context.messages.push(gptResponse);

// Switch to Gemini
context.messages.push({ role: 'user', content: 'What was the original question?' });
const geminiResponse = await complete(gemini, context);
```

Transformation rules for cross-provider messages:
- User and tool result messages: passed through unchanged
- Assistant messages from same provider/API: preserved as-is
- Assistant messages from different providers: thinking blocks converted to text with `<thinking>` tags
- Tool calls and regular text: preserved unchanged

## Context Serialization

```typescript
const context: Context = {
  systemPrompt: 'You are a helpful assistant.',
  messages: [{ role: 'user', content: 'What is TypeScript?' }],
};

const response = await complete(model, context);
context.messages.push(response);

// Serialize
const serialized = JSON.stringify(context);
localStorage.setItem('conversation', serialized);

// Deserialize and continue
const restored: Context = JSON.parse(localStorage.getItem('conversation')!);
restored.messages.push({ role: 'user', content: 'Tell me more' });
const continuation = await complete(newModel, restored);
```

## Custom Models

```typescript
import { Model } from '@earendil-works/pi-ai';

const ollamaModel: Model<'openai-completions'> = {
  id: 'llama-3.1-8b',
  name: 'Llama 3.1 8B (Ollama)',
  api: 'openai-completions',
  provider: 'ollama',
  baseUrl: 'http://localhost:11434/v1',
  reasoning: false,
  input: ['text'],
  cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
  contextWindow: 128000,
  maxTokens: 32000,
};
```

### Faux Provider (for tests)

```typescript
import { complete, fauxAssistantMessage, fauxText, fauxToolCall, registerFauxProvider } from '@earendil-works/pi-ai';

const registration = registerFauxProvider({ tokensPerSecond: 50 });
const model = registration.getModel();
registration.setResponses([
  fauxAssistantMessage([
    fauxThinking('Need to inspect first.'),
    fauxToolCall('echo', { text: 'package.json' })
  ], { stopReason: 'toolUse' }),
]);

const first = await complete(model, context);
// ... handle tool result ...
registration.unregister();
```

## OpenAI Compatibility Settings

For custom proxies and unknown endpoints, use `compat` field on model definition:

```typescript
interface OpenAICompletionsCompat {
  supportsStore?: boolean;               // Default: true
  supportsDeveloperRole?: boolean;       // Default: true
  supportsReasoningEffort?: boolean;     // Default: true
  supportsUsageInStreaming?: boolean;    // Default: true
  supportsStrictMode?: boolean;          // Default: true
  sendSessionAffinityHeaders?: boolean;  // Default: false
  maxTokensField?: 'max_completion_tokens' | 'max_tokens';
  requiresToolResultName?: boolean;      // Default: false
  thinkingFormat?: 'openai' | 'deepseek' | 'zai' | 'qwen' | 'qwen-chat-template';
  cacheControlFormat?: 'anthropic';
  openRouterRouting?: OpenRouterRouting;
  vercelGatewayRouting?: VercelGatewayRouting;
}
```

Partial `compat` is supported — unspecified fields use detected defaults.

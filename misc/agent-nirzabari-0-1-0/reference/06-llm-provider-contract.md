# LLM Provider Contract

## Separating Model Capability from Product Engineering

Before diving into harness architecture, it's worth separating "model capability" from "product engineering." A reader should walk away knowing what to demand from any LLM provider — OpenAI, Anthropic, Google, and others.

## Streaming as Events, Not Just Text

For an agent, "streaming text" isn't enough. You need the model to tell you about tool calls *as they happen*, not after everything is done. This is what makes a coding agent feel responsive rather than frozen.

When you ask Cursor to "read main.py and fix the bug," the model doesn't just generate text. Behind the scenes, it decides to call a tool (like `read_file`), generates the arguments for that tool (`{"path": "src/main.py"}`), and then the harness executes it. **All of this happens over a streaming connection using SSE (Server-Sent Events) — a web standard that lets a server push data to a client over a single long-lived HTTP connection.**

### Three-Phase Tool Call Streaming

Both Anthropic and OpenAI expose a similar three-phase streaming lifecycle:

#### Phase 1: "A tool call is starting"

The model has decided to call a tool. You get the tool name and a unique call ID immediately, before the arguments are fully generated. The UI can already show "Reading main.py..." while the model is still generating.

In the **Anthropic Messages API**, this is a `content_block_start` event with `type: "tool_use"`:

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

In the **OpenAI Responses API**, this begins with `response.output_item.added`, which emits an in-progress function call item.

#### Phase 2: "Arguments are streaming in"

The model generates the JSON arguments token by token: first `{"path": "src/m`, then `ain.py"}`. You see the arguments building up incrementally in the UI, which makes the whole interaction feel more responsive.

In **Anthropic**, these arrive as `content_block_delta` events with `type: "input_json_delta"`:

```json
{ "type": "content_block_delta", "index": 1, "delta": { "type": "input_json_delta", "partial_json": "{\"path\": \"src/m" } }
{ "type": "content_block_delta", "index": 1, "delta": { "type": "input_json_delta", "partial_json": "ain.py\"}" } }
```

In **OpenAI**, these are `response.function_call_arguments.delta` events:

```json
{ "type": "response.function_call_arguments.delta", "item_id": "fc_001", "delta": "{\"path\": \"src/m" }
```

#### Phase 3: "Done, execute it"

The tool call is fully formed. Arguments are finalized, the harness can now actually execute the tool.

In **Anthropic**: `content_block_stop`. In **OpenAI**: `response.function_call_arguments.done`, which also includes the complete arguments and function name in one payload.

See [Anthropic's streaming docs](https://docs.anthropic.com/en/api/messages-streaming) and [OpenAI's streaming events reference](https://platform.openai.com/docs/api-reference/responses-streaming) for the full event schemas.

### Why This Matters for a Harness

Without these events, you'd have to wait for the entire model response to finish before you even know a tool call happened. With them, the product can:

- Show the user what's happening in real-time
- Start preparing the execution environment early (like spinning up a sandbox)
- Persist each event to the timeline for replay and debugging

Codex is built around consuming Responses API SSE streams and translating them into internal events for its own clients and surfaces.

### Latency Discipline

To register as instantaneous to users, the rough target is about 100ms end-to-end, which aligns with classic HCI guidance for perceived immediacy. The same principle applies to the harness: the streaming contract should give the UI enough granularity that the user always understands what the agent is doing. Cursor does this well; Codex and Claude Code have room to improve here.

## Tool Calling with Stable IDs

In practice, robust agent harnesses benefit from tool calls that are addressable (call IDs), typed (schemas), and paired (every call has an output). Systems like Codex additionally persist enough thread state and event history to reconstruct turns and resume sessions.

## Multi-Turn Thread State

Agents aren't "one request." They're threads that grow until they hit a context window, then require compaction or truncation strategies. This is one of the ways each coding agent product differs.

Context management is still one of the biggest issues that defines a good harness — context rot is a common problem, and larger windows (today mostly up to 1M tokens) increase your costs.

As OpenAI puts it: "generally, the cost of sampling the model dominates the cost of network traffic, making sampling the primary target of our efficiency efforts. This is why prompt caching is so important."

## Portability

Codex explicitly notes its endpoint is configurable and can work with any endpoint implementing the Responses API. This leads naturally to vendor-neutral standards like **Open Responses** (launched in January 2026), which defines items, semantic streaming, and tool invocation patterns for provider-agnostic agent APIs.

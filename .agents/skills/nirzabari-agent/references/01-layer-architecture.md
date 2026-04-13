# Layer Architecture Deep Dive

Complete breakdown of the 7-layer coding agent architecture with real implementation examples from Codex CLI and OpenCode.

## Overview

Every production coding agent implements these layers, though architectures differ significantly:

```
Layer 1: Agent Loop → "System Prompt" → user → model → tools → model → ...
Layer 2: Context Building → What data is available to answer the request
Layer 3: Tooling Systems → Registry of tools with schemas and handlers
Layer 4: Safety → Approvals, policies, sandboxes, undo
Layer 5: Replay/Persistence → Event logs for turns, tool calls, diffs
Layer 6: Client Surface → TUI, Web, or IDE interface
Layer 7: Extensibility → MCP, plugins, AGENTS.md conventions
```

## Layer 1: Agent Loop

The conversation runs in turns. Each turn can include hundreds of tool calls, but always ends with an assistant message signaling completion and returning control to the user.

### Codex: Single-Process Architecture

Codex's TUI **is** the runtime - one Tokio event loop multiplexing everything:

```rust
loop {
    tokio::select! {
        // 1) Internal app/UI commands
        Some(app_event) = app_event_rx.recv() => {
            control = app.handle_event(tui, app_event).await?;
        }
        // 2) Messages from active Codex thread
        Some(thread_event) = active_thread_rx.recv(),
            if active_thread_rx_enabled => {
            app.handle_active_thread_event(tui, thread_event).await?;
            control = Continue;
        }
        // 3) Terminal input + draw ticks
        Some(tui_event) = tui_events.next() => {
            control = app.handle_tui_event(tui, tui_event).await?;
        }
        // 4) New agent threads (multi-agent/collab)
        created = thread_created_rx.recv(),
            if listen_for_threads => {
            if let Ok(thread_id) = created {
                app.handle_thread_created(thread_id).await?;
            }
            control = Continue;
        }
    }
    if matches!(control, Exit(reason)) { break reason; }
}
```

**Source**: `codex-rs/tui/src/app.rs` line 1827

**Benefits**: Low latency, minimal moving parts, single owner of state and lifecycle.

**Trade-offs**: Multi-client support requires RPC layer; harder to attach remote clients.

### OpenCode: Client-Server Architecture

OpenCode has a server that streams events, with TUI/web clients subscribing:

```
[TUI client]   [Web client]   [Scripts]
       \            |            /
        --> [Server /event SSE + APIs] --> tools/models/state
```

**Server SSE endpoint**:
```typescript
.get(
  "/event",
  describeRoute({ operationId: "event.subscribe" }),
  async (c) => { ... }
)
```

**TUI subscribes reactively**:
```typescript
sdk.event.on(TuiEvent.CommandExecute.type, (evt) => {
    command.trigger(evt.properties.command)
})
sdk.event.on(TuiEvent.ToastShow.type, (evt) => {
    toast.show({
        title: evt.properties.title,
        message: evt.properties.message,
        variant: evt.properties.variant,
        duration: evt.properties.duration,
    })
})
```

**Source**: `opencode/src/cli/cmd/tui/app.tsx` line 676

**Benefits**: Natural multi-client support, remote orchestration, event distribution built-in.

**Trade-offs**: Versioning, consistency, reconnect logic, "who is source of truth?" bugs.

## Layer 2: Context Building

This layer decides what data the model sees and when. **Context engineering is UX engineering**.

### The AGENTS.md Pattern

OpenAI learned this the hard way: **give the agent a map, not a 1000-page instruction manual**.

**Failed approach**: One giant AGENTS.md file
- Crowds out task and code in context window
- Too much guidance becomes noise
- Rots quickly as repo changes
- Hard to verify mechanically

**Working approach**: AGENTS.md as table of contents (~100 lines)
- Repository knowledge base lives in structured `docs/` directory
- Short AGENTS.md injected into context with pointers to deeper sources
- From agent's perspective: anything not accessible in-context effectively doesn't exist

### Codex: Compiled Contract

Prompts are versioned, auditable contracts that ship with the binary:

```rust
// Default base instructions embedded at compile time
include_str!("prompts/base.md")
```

Then composed with:
- Model-specific instruction files
- Personality/model-message overlays

**Architecture choice**: Behavior tightly tied to releases. Switching models changes narrow slice of instruction surface while harness contract stays coherent.

### OpenCode: Runtime Routing

Prompt fragments selected at runtime using model-ID string matching:

```typescript
// Model-aware prompt selection
if (model.modelID.includes("claude")) {
    // Use Claude-specific prompt fragment
}
```

Also injects environment state:
```typescript
`Today's date: ${new Date().toDateString()}`
```

**Implication**: Prompt bytes are time-dependent. Great for grounding, bad for reproducibility.

### Tool Descriptions as Prompts

OpenCode's `bash.txt` does workflow steering that isn't about Bash at all - it gives the model instructions about how to behave.

**Design choice**: "How to behave" lives close to the tool, not only in global system prompt.
- If behavior lives in tool descriptions: global prompt can be smaller, but each tool description needs careful review
- If behavior lives in global prompt: tool descriptions stay tight, but base prompt becomes larger contract to maintain

## Layer 3: Tooling Systems

Product needs a tool registry: which tools are available, with argument schemas, multi-modal support, and parameters.

### Codex: Centralized Orchestrator

Compiled tool handlers plus centrally routed runtime tools through single pipeline:

```rust
pub trait ToolHandler: Send + Sync {
    fn kind(&self) -> ToolKind;
    fn name(&self) -> ToolName;
    async fn handle(&self, /* ... */) -> ToolResult;
}
```

**Source**: `codex-rs/core/src/tools/registry.rs` line 22-43

Orchestrator is single control point - one place where policy enforced for every tool call:

```rust
pub async fn run(
    &mut self,
    tool: &mut T,
    req: &Rq,
    tool_ctx: &ToolCtx<'_>,
    turn_ctx: &TurnContext,
    approval_policy: AskForApproval,
) -> Result<Out, ToolError>
```

**Source**: `codex-rs/core/src/tools/orchestrator.rs` line 35-42

**Benefit**: Fewer ways for behavior to differ across models and providers - tools are compiled, typed, centrally routed.

### OpenCode: Dynamic Registry

Intentionally composable at runtime:

```typescript
// Model-aware tool swapping
const usePatch =
    model.modelID.includes("gpt-") &&
    !model.modelID.includes("oss") &&
    !model.modelID.includes("gpt-4")

// Load tools dynamically from config dirs
const glob = new Bun.Glob("{tool,tools}/*.{js,ts}")
for (const match of glob.scanSync(/* ... */)) {
    const mod = await import(match)
}

// Inject plugin tools into registry
const plugins = await Plugin.list()
for (const plugin of plugins) {
    for (const [id, def] of Object.entries(plugin.tool ?? {})) {
        custom.push(fromPlugin(id, def))
    }
}
```

**Source**: `packages/opencode/src/tool/registry.ts`

**Benefit**: Faster tool/plugin iteration - new tools and providers without forking core. Can "ship behavior" as plugins.

**Trade-off**: Auditing is harder. Runtime composition means "what tools exist?" becomes configuration-dependent, potential entry point for malicious code.

## Layer 4: Safety

`sudo rm -rf /*`. Scary.

Harnesses support:
1. Allowlist and denylist for tools and commands
2. Sandboxing
3. Snapshotting and recovery

Safety isn't "add a warning." It's architecture - approvals, policies, sandboxes, and undo.

### Codex: Execution Containment

Tools execute through orchestrated pipeline that can require approvals and apply sandbox constraints. Execution funnels through `ToolOrchestrator::run(...)` with explicit approval policy as input.

**Approach**: Defense-in-depth with orchestrator + approvals + OS sandboxing.

### OpenCode: Pre-Execution Understanding

In the bash path: understand what command is, then run if permissions allow. Parses commands with tree-sitter:

```typescript
const tree = await parser().then((p) => p.parse(params.command))
for (const node of tree.rootNode.descendantsOfType("command")) {
    // extract command + args
}

// Permission checks before spawn
if (directories.size > 0) {
    await ctx.ask({ permission: "external_directory", /* ... */ })
}
if (patterns.size > 0) {
    await ctx.ask({ permission: "bash", /* ... */ })
}
```

**Source**: `packages/opencode/src/tool/bash.ts` line 84-164

**Trade-off**: Approval becomes main guardrail, while Codex invests more in execution containment.

## Layer 5: Replay / Persistence

Long-running agents are event systems, not just chat transcripts. Need to reconstruct what happened: turns, tool calls, approvals, outputs, and order.

### Codex: Local State

Internal event channels that drive app loop and thread updates also make session legible after the fact. Tool calls, thread events, UI state transitions all pass through single process with single owner of state.

**Benefit**: Local state easier to reason about - fewer components involved.

### OpenCode: Distributed Events

SSE event backbone and server-owned state make replay, connecting from another client, and multi-client synchronization more natural because system already designed around publishing/subscribing to structured events.

**Benefit**: Distributed replay more straightforward - event distribution is first-class concept.

## Layer 6: Client Surface (UX)

### Codex: High-Performance Terminal

One async loop, explicit rendering and event handling, minimal indirection. Produces fast responsiveness and fewer "UI framework" failure modes, but less discoverability unless you build command palettes, routing, rich toasts manually.

### OpenCode: Web-Like TUI

TUI composed like web app:

```typescript
render(() => (
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
))
```

Subscribes to world via SDK events. Optimizes for surface area and discoverability (routing, dialogs, toasts, remote control). Codex optimizes for tight feedback loops and minimal architecture.

## Layer 7: Extensibility

### Codex: MCP as Runtime Component

MCP treated as runtime-integrated tool source - namespaced tool kinds, routed through same handler model. Designed to remain tight, controlled harness that lets MCP expand reach without turning core into general plugin system.

### OpenCode: First-Class Plugins

Registry literally merges plugin-defined tools into tool list. Not "MCP-only" - "anything can be tool if it implements hook surface." Auth flows, tools, request/response shaping - all pluggable.

**Product implication**: OpenCode clearly designed to be more platform-like and hackable. Codex designed to remain tightly controlled.

## The Bottom Line

Neither approach is "better" in abstract. Different answers to: *"How do you turn a text generation model into a product that can safely act on its own?"*

- **Codex answer**: Contain execution (orchestrator + approvals + sandbox)
- **OpenCode answer**: Favor runtime composition and pre-execution understanding (AST parsing + permission broker + composable tooling)

## Key Takeaways

1. **Architecture determines trade-offs** - Monolith vs control-plane, compiled vs dynamic, local vs distributed
2. **Safety is architecture** - Not warnings, but approvals, policies, sandboxes, undo
3. **Context engineering is UX** - Product decides what model sees and when
4. **Tool descriptions are prompts too** - Behavior can live in global prompt or tool descriptions
5. **Event systems enable replay** - Turns, tool calls, approvals must be reconstructable
6. **Client surface matches architecture** - Terminal-native vs web-like TUI
7. **Extensibility is product decision** - Tight control vs platform-like hackability

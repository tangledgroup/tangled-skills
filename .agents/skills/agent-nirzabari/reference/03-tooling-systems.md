# Tooling Systems

## Tool Registry Requirements

The product needs a tool registry: which tools are available for the model to use. Each tool should define:

1. Argument schemas
2. Multi-modal support (images / videos)
3. Attachment / parameters

Example tools: shell, file edit, code search, browser automation, screenshot analysis.

## Codex: Compiled Tool Handlers

Codex is built around compiled tool handlers plus centrally routed runtime tools, all routed through a central "run tool" pipeline:

```rust
pub trait ToolHandler: Send + Sync {
    fn kind(&self) -> ToolKind;
    fn name(&self) -> ToolName;
    async fn handle(&self, /* ... */) -> ToolResult;
}
```

[Source: codex-rs/core/src/tools/registry.rs](https://github.com/openai/codex/blob/6638558b8807328e852b54580b010be7034699b7/codex-rs/core/src/tools/registry.rs#L22-L43)

The orchestrator is the single control point — one place where policy gets enforced for every tool call:

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

[Source: codex-rs/core/src/tools/orchestrator.rs](https://github.com/openai/codex/blob/6638558b8807328e852b54580b010be7034699b7/codex-rs/core/src/tools/orchestrator.rs#L35-L42)

**What this buys you:** Fewer ways for behavior to differ across models and providers, because tools are compiled, typed, and centrally routed.

## OpenCode: Dynamic Runtime Registry

OpenCode's registry is intentionally composable at runtime:

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

// Inject plugin tools into the registry
const plugins = await Plugin.list()
for (const plugin of plugins) {
    for (const [id, def] of Object.entries(plugin.tool ?? {})) {
        custom.push(fromPlugin(id, def))
    }
}
```

[Source: packages/opencode/src/tool/registry.ts](https://github.com/anomalyco/opencode/blob/6c7d968c4423a0cd6c85099c9377a6066313fa0a/packages/opencode/src/tool/registry.ts)

**What this buys you:** Faster tool and plugin iteration — new tools and providers without forking core, and the ability to "ship behavior" as plugins.

**The trade-off:** Auditing is harder. Runtime composition means "what tools exist?" becomes configuration-dependent, which could also be a point of entry for malicious code.

## Model-Aware Tool Swapping

Both systems adapt tool behavior based on the model being used. OpenCode does this explicitly with string matching on model IDs (e.g., `model.modelID.includes("gpt-")`). Codex does this through model-specific instruction files that are composed at runtime.

This is a practical necessity: different models have different capabilities, context windows, and tool-calling conventions. The harness must adapt its tool surface accordingly.

## Tool Descriptions and Behavior Steering

Tool descriptions serve dual purposes: they tell the model what a tool does, and they can steer how the model behaves. OpenCode's `bash.txt` includes workflow instructions that aren't about Bash at all — they guide the model's overall behavior.

This creates a design tension: should behavioral guidance live in tool descriptions or in the global system prompt? Each approach has trade-offs in maintainability, review surface, and prompt size.

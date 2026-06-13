# Safety and Persistence

## Safety Architecture

Safety isn't "add a warning." It's architecture — approvals, policies, sandboxes, and undo. Harnesses today support:

1. Allowlist and denylist for tools and commands
2. Sandboxing
3. Snapshotting and recovery

After all of that, you can't stop users from running dangerously.

### Codex: Execution Containment

Codex's safety approach: tools execute through an orchestrated pipeline that can require approvals and apply sandbox constraints. Execution funnels through `ToolOrchestrator::run(...)` and takes explicit approval policy as an input.

The orchestrator enforces defense-in-depth: exec policy + approvals enforced by orchestrator + OS sandboxing.

### OpenCode: Pre-Execution Understanding

OpenCode's safety approach, at least in the bash path, is: understand what the command is, then run it if permissions allow. The bash tool parses commands with [tree-sitter](https://tree-sitter.github.io/tree-sitter/):

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

[Source: packages/opencode/src/tool/bash.ts](https://github.com/anomalyco/opencode/blob/6c7d968c4423a0cd6c85099c9377a6066313fa0a/packages/opencode/src/tool/bash.ts#L84-L164)

In the cited OpenCode bash path, approval becomes the main guardrail, while Codex invests more heavily in execution containment.

## Replay and Persistence

Long-running agents are event systems, not just chat transcripts. You need to be able to reconstruct what happened: turns, tool calls, approvals, outputs, and the order they occurred in.

Forking chats and environments is crucial for debugging. These systems are made of turns, tool calls, diffs, approvals, and other events — so you need to be able to restore them.

### Codex: Local State

Codex keeps this close to the runtime. The same internal event channels that drive the app loop and active thread updates also make the session legible after the fact: tool calls, thread events, and UI state transitions all pass through a single process with a single owner of state.

### OpenCode: Distributed Events

OpenCode pushes persistence outward into the control plane. Its SSE event backbone and server-owned state make replay, connecting from another client, and multi-client synchronization more natural, because the system is already designed around publishing and subscribing to structured events.

### The Trade-Off

The trade-off matches the architecture split. Codex makes local state easier to reason about because fewer components are involved. OpenCode makes distributed replay more straightforward because event distribution is already a first-class concept.

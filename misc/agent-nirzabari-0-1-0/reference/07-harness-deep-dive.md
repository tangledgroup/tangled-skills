# Harness Deep Dive: Codex vs OpenCode

## Architecture Comparison

| Layer / Dimension | [Codex CLI (Rust)](https://github.com/openai/codex) | [OpenCode (TS/Bun)](https://github.com/anomalyco/opencode) |
| --- | --- | --- |
| **Layer 1: Agent Loop** | Single-process CLI/TUI runtime multiplexing input, thread events, and ticks via internal channels | Client-server architecture with `/event` SSE and clients subscribing to SDK events |
| **Layer 2: Context Building** | Default base instructions compiled into the binary, plus model-specific instruction files and personality/model-message overlays | Runtime-selected provider prompts via model-ID matching, plus runtime environment and instruction-file injection |
| **Layer 3: Tooling Systems** | Compiled built-ins plus centrally routed MCP/runtime tools through a central orchestrator pipeline | Dynamic registry + model-aware tool swapping + plugins/custom tools |
| **Layer 4: Safety** | Exec policy + approvals enforced by orchestrator + OS sandboxing (defense-in-depth) | Permission broker + AST parsing for bash command analysis (policy-first) |
| **Layer 5: Replay / Persistence** | Internal event channels and thread state make turns reconstructable inside one runtime | SSE event backbone and server-owned state make replay and multi-client synchronization natural |
| **Layer 6: Client Surface (UX)** | Fast terminal-native loop (Rust TUI patterns) | Terminal rendered like a web app (JSX/components), toasts/routing/events |
| **Layer 7: Extensibility** | MCP treated as a runtime component (namespaced tools, runtime discovery) | Plugins + custom tools are first-class; providers/auth are pluggable |

## Layer 1: Agent Loop (Monolith vs Control-Plane)

At this layer, "monolith vs control-plane" is really the question of where the agent loop lives and who owns its state.

### Codex: "One Binary Owns Everything"

Codex's TUI *is* the app runtime: it multiplexes user input, internal agent events, and background ticks inside a single [Tokio](https://tokio.rs) loop.

```text
[TUI Process]
  ├─ input (keys)
  ├─ agent events (thread rx)
  ├─ periodic ticks
  └─ tool execution / approvals / rendering
```

The event loop in Rust:

```rust
loop {
    tokio::select! {
        // 1) Internal app/UI commands
        Some(app_event) = app_event_rx.recv() => {
            control = app.handle_event(tui, app_event).await?;
        }
        // 2) Messages from the active Codex thread
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

[Source: codex-rs/tui/src/app.rs](https://github.com/openai/codex/blob/6638558b8807328e852b54580b010be7034699b7/codex-rs/tui/src/app.rs#L1827)

**Why this is a product choice:** Low latency, minimal moving parts, "what you see is what runs." This architecture assumes one UI owns the agent. If you want multiple clients (TUI + web), you need an RPC layer to multiplex control and broadcast updates. The monolith wins when latency matters, you want a single owner of state and lifecycle, and you want a self-contained artifact.

### OpenCode: Client-Server Control Plane

OpenCode explicitly has a server that streams events, and a TUI client that subscribes and reacts:

```text
[TUI client]   [Web client]   [Scripts]
       \            |            /
        --> [Server /event SSE + APIs] --> tools/models/state
```

The server SSE endpoint:

```typescript
.get(
  "/event",
  describeRoute({ operationId: "event.subscribe" }),
  async (c) => { ... }
)
```

[Source: opencode/src/server/server.ts](https://github.com/anomalyco/opencode/blob/6c7d968c4423a0cd6c85099c9377a6066313fa0a/packages/opencode/src/server/server.ts#L503)

The TUI subscribes to events reactively:

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

[Source: opencode/src/cli/cmd/tui/app.tsx](https://github.com/anomalyco/opencode/blob/6c7d968c4423a0cd6c85099c9377a6066313fa0a/packages/opencode/src/cli/cmd/tui/app.tsx#L676)

If Codex is more like a secure, single-process instrument panel (one engine, one cockpit), OpenCode is more like a control plane: a server that emits events, and any number of clients that can render them.

### What Each Architecture Makes Harder

The monolith makes multi-client attach and remote orchestration require an RPC-ish boundary. The control-plane introduces versioning, consistency, reconnect, and "who is the source of truth?" bugs.

## The Bottom Line

Neither approach is "better" in the abstract. They're different answers to the same question: *"How do you turn a text generation model into a product that can safely act on its own?"*

- **Codex answers:** contain execution (orchestrator + approvals + sandbox).
- **OpenCode answers:** favor runtime composition and, in its bash path, pre-execution understanding (AST parsing + permission broker + composable tooling), and more.

# Codex CLI Deep Dive

Complete analysis of OpenAI's Codex CLI architecture, Rust implementation details, and design decisions.

## Overview

**Codex CLI** is a coding agent from OpenAI that runs locally on your computer. It represents OpenAI's "harness engineering" - the system around the model that makes it useful.

### Installation

```bash
# npm
npm install -g @openai/codex

# Homebrew
brew install --cask codex

# Or download binary from GitHub releases
```

### Architecture Summary

- **Language**: Rust
- **Architecture**: Single-process CLI/TUI runtime
- **Event Loop**: Tokio async runtime multiplexing input, thread events, and ticks
- **Tools**: Compiled built-ins plus centrally routed MCP/runtime tools
- **Safety**: Exec policy + approvals enforced by orchestrator + OS sandboxing

## Core Architecture

### Single-Process Design

Codex's TUI **is** the app runtime. Everything runs in one Tokio event loop:

```
[TUI Process]
  ├─ input (keys)
  ├─ agent events (thread rx)
  ├─ periodic ticks
  └─ tool execution / approvals / rendering
```

This is a product choice: low latency, minimal moving parts, "what you see is what runs."

### The Event Loop

```rust
// codex-rs/tui/src/app.rs line 1827

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

**Key insight**: Four channels multiplexed in one loop:
1. App events (internal commands)
2. Thread events (agent messages)
3. TUI events (terminal input + rendering)
4. Thread creation (multi-agent support)

### Why Monolith?

**Benefits**:
- Low latency - no network overhead between components
- Minimal moving parts - fewer failure modes
- Single owner of state and lifecycle - easier reasoning about system behavior
- Self-contained artifact - one binary to distribute

**Trade-offs**:
- Multi-client attach requires RPC layer
- Remote orchestration needs additional infrastructure
- Harder to scale horizontally (one process = one session)

## Prompt Architecture

### Compiled Contract Approach

Codex treats prompts like versioned, auditable contracts that ship with the binary:

```rust
// Default base instructions embedded at compile time
const BASE_INSTRUCTIONS: &str = include_str!("prompts/base.md");

// Model-specific instructions
const CLAUDE_INSTRUCTIONS: &str = include_str!("prompts/claude.md");
const GPT_INSTRUCTIONS: &str = include_str!("prompts/gpt.md");

// Personality templates (optional)
const CAREFUL_PERSONALITY: &str = include_str!("promptoms/personalities/careful.md");
```

**Composition**:
1. Base prompt (always included)
2. Model-specific prompt (selected based on active model)
3. Personality template (optional, for specific behaviors)

### Why Compiled?

**Benefits**:
- Behavior tightly tied to releases - predictable, auditable
- Prompt families: base + model prompts + personalities
- Switching models changes narrow slice of instruction surface while harness contract stays coherent

**Trade-offs**:
- Runtime overrides still exist (AGENTS.md, user config)
- Less flexible than runtime-selected prompts
- Need to recompile for prompt changes (unless using overlays)

## Tool System

### Tool Handler Trait

```rust
// codex-rs/core/src/tools/registry.rs line 22-43

pub trait ToolHandler: Send + Sync {
    fn kind(&self) -> ToolKind;
    fn name(&self) -> ToolName;
    async fn handle(&self, request: &Request, context: &ToolCtx) -> ToolResult;
}

pub struct ToolRegistry {
    handlers: HashMap<ToolName, Box<dyn ToolHandler>>,
}
```

### Built-in Tools

Compiled into the binary:
- `edit` - File editing with precise replacements
- `read` - File reading with offset/limit for large files
- `bash` - Shell execution with sandboxing
- `glob` - File pattern matching
- `ls` - Directory listing

### MCP Integration

MCP (Model Context Protocol) tools treated as runtime component:

```rust
pub struct McpToolHandler {
    server: McpServer,
    tool_name: String,
}

impl ToolHandler for McpToolHandler {
    fn kind(&self) -> ToolKind {
        ToolKind::Mcp
    }
    
    fn name(&self) -> ToolName {
        format!("mcp/{}", self.tool_name).into()
    }
    
    async fn handle(&self, request: &Request, context: &ToolCtx) -> ToolResult {
        // Route to MCP server
        self.server.call_tool(&self.tool_name, request).await
    }
}
```

**Namespaced tools**: MCP tools get `mcp/` prefix to avoid conflicts with built-ins.

### Central Orchestrator

Single control point where policy enforced for every tool call:

```rust
// codex-rs/core/src/tools/orchestrator.rs line 35-42

pub struct ToolOrchestrator {
    approval_policy: ApprovalPolicy,
    sandbox_config: SandboxConfig,
    event_logger: EventLogger,
}

impl ToolOrchestrator {
    pub async fn run(
        &mut self,
        tool: &mut dyn ToolHandler,
        req: &Request,
        tool_ctx: &ToolCtx,
        turn_ctx: &TurnContext,
        approval_policy: AskForApproval,
    ) -> Result<Output, ToolError> {
        // 1. Validate request against schema
        self.validate(req)?;
        
        // 2. Check approval policy
        if self.requires_approval(tool, req) {
            self.request_approval(tool, req, approval_policy).await?;
        }
        
        // 3. Apply sandbox constraints
        let sandboxed_req = self.sandbox.apply(req);
        
        // 4. Execute tool
        let result = tool.handle(&sandboxed_req, tool_ctx).await;
        
        // 5. Log for replay
        self.event_logger.log_tool_call(tool.name(), req, &result);
        
        Ok(result)
    }
}
```

**Why centralized**:
- Fewer ways for behavior to differ across models and providers
- Tools are compiled, typed, centrally routed
- One place to audit for security

## Safety System

### Approval Policy

```rust
pub enum AskForApproval {
    Never,        // Always execute
    Always,       // Always ask
    Dangerous,    // Ask for dangerous operations
    Configured,   // Based on policy configuration
}

pub struct ApprovalPolicy {
    default: AskForApproval,
    tool_overrides: HashMap<ToolName, AskForApproval>,
    command_patterns: Vec<CommandPattern>,
}
```

### Sandbox Implementation

OS-level sandboxing for defense-in-depth:

```rust
// codex-rs/core/src/sandbox.rs

#[cfg(target_os = "linux")]
pub struct LinuxSandbox {
    namespace_config: NamespaceConfig,
    cgroup_config: CgroupConfig,
    seccomp_filter: SeccompFilter,
}

#[cfg(target_os = "macos")]
pub struct MacOSSandbox {
    sysctl_constraints: SysctlConstraints,
    launchd_profile: LaunchdProfile,
}

impl Sandbox for LinuxSandbox {
    async fn execute(&self, command: &str, cwd: &Path) -> Result<Output, Error> {
        // 1. Create user namespace
        unshare(UserNamespace::new())?;
        
        // 2. Apply cgroup limits
        self.cgroup_config.apply()?;
        
        // 3. Load seccomp filter
        load_seccomp_filter(&self.seccomp_filter)?;
        
        // 4. Execute command
        execute_command(command, cwd).await
    }
}
```

**Defense-in-depth**: Approvals + sandbox + approval policy = multiple layers of protection.

## Thread Management

### Thread State

```rust
pub struct Thread {
    id: ThreadId,
    messages: Vec<Message>,
    tool_calls: Vec<ToolCall>,
    context_window: ContextWindow,
    created_at: DateTime,
    updated_at: DateTime,
}

pub struct ContextWindow {
    max_tokens: usize,
    used_tokens: usize,
    cached_tokens: usize,
}
```

### Multi-Thread Support

Codex supports multiple concurrent threads (agents):

```rust
pub struct ThreadManager {
    threads: HashMap<ThreadId, Thread>,
    active_thread: Option<ThreadId>,
    thread_rx: mpsc::Receiver<ThreadEvent>,
}

impl ThreadManager {
    pub async fn create_thread(&mut self) -> ThreadId {
        let id = ThreadId::generate();
        let thread = Thread::new(id);
        self.threads.insert(id, thread);
        id
    }
    
    pub async fn switch_thread(&mut self, id: ThreadId) {
        self.active_thread = Some(id);
    }
    
    pub async fn get_active_thread(&self) -> Option<&Thread> {
        self.active_thread.and_then(|id| self.threads.get(&id))
    }
}
```

## Client Architecture

### App Server Concept

OpenAI uses "App Server" to expose the harness to multiple clients via stable protocol:

```
┌──────────────────────────────────────────┐
│              App Server                  │
│  - Core agent loop and execution logic   │
│  - Thread management                     │
│  - Tool orchestration                    │
│  - Event broadcasting                    │
└────────────────────┬─────────────────────┘
                     │ Stable protocol
         ┌───────────┼───────────┬──────────┐
         │           │           │          │
    ┌────▼────┐ ┌────▼────┐ ┌───▼───┐ ┌───▼────┐
    │  TUI    │ │ VS Code │ │ Desktop│ │ Partner│
    │ Client  │ │ Extension│ │ App   │ │ API    │
    └─────────┘ └──────────┘ └───────┘ └────────┘
```

**Benefits**:
- Single implementation of agent logic
- Multiple client types (TUI, IDE, desktop, web)
- Stable protocol for third-party integrations

### Protocol Design

```rust
pub enum AppEvent {
    UserMessage { thread_id: ThreadId, message: String },
    ToolApproval { call_id: CallId, approved: bool },
    ThreadSwitch { thread_id: ThreadId },
    ConfigUpdate { config: Config },
}

pub enum ServerEvent {
    AssistantMessage { thread_id: ThreadId, content: String },
    ToolCallStart { call_id: CallId, tool: String, args: Value },
    ToolCallComplete { call_id: CallId, result: ToolResult },
    ProgressUpdate { progress: f64, message: String },
}
```

## Performance Optimizations

### Prompt Caching

```rust
pub struct PromptCache {
    cached_sections: HashMap<String, CachedSection>,
    max_cache_size: usize,
}

impl PromptCache {
    pub fn add_section(&mut self, key: String, content: String) {
        if self.cached_sections.len() < self.max_cache_size {
            self.cached_sections.insert(key, CachedSection {
                content,
                token_count: count_tokens(&content),
                inserted_at: Instant::now(),
            });
        }
    }
    
    pub fn get_cached_prompt(&self, sections: &[&str]) -> String {
        sections.iter()
            .filter_map(|&key| self.cached_sections.get(key))
            .map(|section| &section.content)
            .collect::<Vec<_>>()
            .join("\n\n")
    }
}
```

### Token Counting

```rust
pub struct TokenCounter {
    encoder: Cl100kBase, // Tiktoken encoder
}

impl TokenCounter {
    pub fn count(&self, text: &str) -> usize {
        self.encoder.encode(text).len()
    }
    
    pub fn count_message(&self, message: &Message) -> usize {
        // Account for message structure tokens
        let mut count = 4; // Base message tokens
        count += self.count(&message.role);
        count += self.count(&message.content);
        count
    }
}
```

## Configuration

### Config File Structure

```toml
# ~/.config/codex/config.toml

[models]
default = "claude-3-5-sonnet"

[models.claude-3-5-sonnet]
api_key_env = "ANTHROPIC_API_KEY"
max_tokens = 4096

[models.gpt-4]
api_key_env = "OPENAI_API_KEY"
max_tokens = 4096

[safety]
approval_policy = "dangerous"
sandbox_enabled = true

[tools]
enabled = ["edit", "read", "bash", "glob", "ls"]
disabled = []

[mcp]
servers = [
    { name = "git", command = "mcp-git-server" },
    { name = "docker", command = "mcp-docker-server" }
]
```

## Comparison with Alternatives

| Aspect | Codex | OpenCode | Claude Code |
|--------|-------|----------|-------------|
| **Architecture** | Single-process monolith | Client-server | Proprietary |
| **Language** | Rust | TypeScript/Bun | Proprietary |
| **Prompts** | Compiled + overlays | Runtime-selected | Proprietary |
| **Tools** | Compiled + MCP | Dynamic registry + plugins | Proprietary |
| **Safety** | Orchestrator + sandbox | AST parsing + approvals | Proprietary |
| **Extensibility** | MCP as runtime component | First-class plugins | Limited |
| **Clients** | TUI, VS Code, Desktop | TUI, Web, Scripts | CLI only |

## Key Design Decisions

### 1. Monolith Over Microservices

**Decision**: Single process owns everything.

**Rationale**: Low latency, minimal moving parts, single owner of state.

**Trade-off**: Multi-client support requires RPC layer.

### 2. Compiled Prompts

**Decision**: Prompts embedded in binary at compile time.

**Rationale**: Versioned, auditable contract; behavior tied to releases.

**Trade-off**: Less flexible than runtime selection.

### 3. Centralized Tool Orchestrator

**Decision**: Single control point for all tool calls.

**Rationale**: Fewer ways for behavior to differ; easier auditing.

**Trade-off**: Potential bottleneck (mitigated by async).

### 4. OS-Level Sandboxing

**Decision**: Use OS namespaces and constraints for safety.

**Rationale**: Defense-in-depth; hard to escape even if model compromised.

**Trade-off**: Performance overhead, some operations can't be sandboxed.

### 5. App Server Pattern

**Decision**: Expose harness via stable protocol to multiple clients.

**Rationale**: Single implementation, multiple client types.

**Trade-off**: Protocol design and versioning complexity.

## References

- **Codex GitHub**: https://github.com/openai/codex
- **Codex Documentation**: https://developers.openai.com/codex
- **Contributing Guide**: https://github.com/openai/codex/blob/main/docs/contributing.md
- **Harness Engineering Post**: https://openai.com/index/harness-engineering/
- **Unrolling the Agent Loop**: https://openai.com/index/unrolling-the-codex-agent-loop/

## Key Takeaways

1. **Single-process architecture** - Tokio event loop multiplexes everything for low latency
2. **Compiled prompts** - Versioned, auditable contracts embedded in binary
3. **Centralized orchestrator** - Single control point for all tool calls and policy enforcement
4. **OS-level sandboxing** - Defense-in-depth with namespaces and cgroups
5. **MCP as runtime component** - Namespaced tools routed through same handler model
6. **App server pattern** - Stable protocol exposes harness to multiple client types
7. **Rust for performance** - Type safety and async runtime enable responsive TUI
8. **Thread management** - Support for multiple concurrent agent sessions
9. **Prompt caching** - Reduce costs by caching frequent context portions
10. **Defense-in-depth safety** - Approvals + sandbox + policy = multiple protection layers

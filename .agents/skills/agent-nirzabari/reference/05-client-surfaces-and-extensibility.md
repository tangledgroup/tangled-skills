# Client Surfaces and Extensibility

## Client Surface Architectures

Main players today:

- **TUI:** [OpenCode](https://github.com/anomalyco/opencode), [Claude Code](https://docs.anthropic.com/en/docs/claude-code), and [Codex](https://github.com/openai/codex)
- **IDE:** [Cursor](https://cursor.com), Google's [Antigravity](https://developers.googleblog.com/en/build-with-google-antigravity-our-new-agentic-development-platform/), and [Replit Agent](https://replit.com/products/agent), plus extensions like [GitHub Copilot](https://github.com/features/copilot)
- **Web:** [Bolt.new](https://bolt.new/), [v0](https://v0.app/), and [Lovable](https://www.lovable.dev/)

## Codex: Terminal-Native TUI

Codex reads like a high-performance terminal program: one async loop, explicit rendering and event handling, minimal indirection. This produces fast responsiveness and fewer "UI framework" failure modes, but less discoverability unless you build command palettes, routing, and rich toasts manually.

## OpenCode: Web-Style TUI

OpenCode's TUI is composed like a web app:

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
```

Because it's a client, it subscribes to the world via SDK events. OpenCode optimizes for surface area and discoverability (routing, dialogs, toasts, remote control); Codex optimizes for tight feedback loops and minimal architecture.

## Extensibility Ecosystem

The ecosystem is converging on shared boundaries:

- **MCP** ([Model Context Protocol](https://modelcontextprotocol.io)) — tool connectivity standard
- **Skills** ([Anthropic Skills](https://docs.anthropic.com/en/docs/claude-code/skills)) — Anthropic's convention for agent instructions
- **AGENTS.md** ([GitHub's guide](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)) — repo-specific instruction conventions
- **Open Responses** ([openresponses.org](https://www.openresponses.org/)) — provider-agnostic API shape

### Codex: MCP as Runtime Component

Codex treats MCP as a runtime-integrated tool source — namespaced tool kinds, routed through the same handler model. MCP expands its reach without turning the core into a general plugin system.

### OpenCode: First-Class Plugins

OpenCode's registry literally merges plugin-defined tools into the tool list. That's not "MCP-only" — it's "anything can be a tool if it implements the hook surface." Auth flows, tools, request/response shaping — all pluggable.

**Product implication:** OpenCode is clearly designed to be more platform-like and hackable. Codex is designed to remain a tight, tightly controlled harness.

Anthropic excels in the extensibility space overall — their Skills system and tight IDE integration make them the reference implementation for agent extensibility.

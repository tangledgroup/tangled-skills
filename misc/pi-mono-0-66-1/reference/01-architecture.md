# Architecture & Monorepo Structure

## Package Layout

```
pi-mono/
├── packages/
│   ├── ai/              # LLM provider abstraction
│   │   └── streaming, tool calls, cost tracking, model types
│   ├── agent/           # Agent loop and message types
│   │   └── Agent class, AgentMessage union, event types
│   ├── tui/             # Terminal UI components
│   │   └── Text, Box, Container, SelectList, Markdown, Image
│   └── coding-agent/    # CLI, interactive mode, extensions
│       ├── src/core/     # AgentSession, SessionManager, tools
│       ├── src/modes/    # Interactive, print, JSON, RPC modes
│       ├── docs/         # Documentation
│       └── examples/     # Extension and SDK examples
```

## Four Core Packages

### @mariozechner/pi-ai

LLM provider abstraction layer. Handles:

- Streaming via `AssistantMessageEventStream`
- Tool call parsing and streaming
- Cost calculation from usage
- Model definition types (`Model`, `ProviderConfig`)
- Built-in providers: Anthropic, OpenAI, Google, Azure, Bedrock, Mistral, Groq, etc.
- API types: `anthropic-messages`, `openai-completions`, `openai-responses`, `google-generative-ai`, `bedrock-converse-stream`, `mistral-conversations`

Key exports: `getModel()`, `createAssistantMessageEventStream()`, `calculateCost()`, `StringEnum()`

### @mariozechner/pi-agent-core

Agent loop and message types. Handles:

- `Agent` class — core LLM interaction loop
- `AgentMessage` union type (UserMessage, AssistantMessage, ToolResultMessage)
- `AgentEvent` types (agent_start, agent_end, turn_start/turn_end, message lifecycle, tool execution)
- State management (messages, model, thinkingLevel, systemPrompt, tools)

### @mariozechner/pi-tui

Terminal UI component library. Handles:

- Component interface: `{ render(width): string[], handleInput?(data), invalidate() }`
- Focusable interface for IME cursor positioning
- Built-in components: `Text`, `Box`, `Container`, `Spacer`, `Markdown`, `Image`, `SelectList`, `SettingsList`, `Input`
- Keyboard handling: `matchesKey()`, `Key.*` constants
- Text utilities: `visibleWidth()`, `truncateToWidth()`, `wrapTextWithAnsi()`
- ANSI styling with per-line reset (styles don't carry across lines)

### @mariozechner/pi-coding-agent

The main package — CLI, interactive mode, extension system. Handles:

- `createAgentSession()` — factory for AgentSession
- `createAgentSessionRuntime()` — session replacement layer (new, fork, clone, switch)
- Built-in tools: `read`, `bash`, `edit`, `write`, `grep`, `find`, `ls`
- Tool factories: `createReadTool(cwd)`, `createBashTool(cwd)`, etc.
- Extension system: `ExtensionAPI`, event hooks, tool/command registration
- Session management: JSONL tree format, branching, compaction
- Settings: global + project merge
- Resource loading: extensions, skills, prompts, themes discovery
- Run modes: InteractiveMode, runPrintMode, runRpcMode

## Design Philosophy

Pi is aggressively extensible. Features that other tools bake in are built with extensions or installed from third-party packages:

- **No MCP** — build CLI tools with READMEs (skills), or build an extension
- **No sub-agents** — spawn pi instances via tmux, or build your own
- **No permission popups** — run in a container, or build your own confirmation flow
- **No plan mode** — write plans to files, or build it with extensions
- **No built-in to-dos** — use TODO.md, or build your own
- **No background bash** — use tmux for full observability

## Run Modes

| Mode | Flag | Description |
|------|------|-------------|
| Interactive | (default) | Full TUI with editor, chat history, commands |
| Print | `-p` | Single-shot: send prompt, output result, exit |
| JSON | `--mode json` | All events as JSON lines to stdout |
| RPC | `--mode rpc` | JSON protocol over stdin/stdout for subprocess integration |
| SDK | N/A | Embed in Node.js apps via `createAgentSession()` |

## Development Setup

```bash
git clone https://github.com/badlogic/pi-mono
cd pi-mono
npm install
npm run build

# Run from source (keeps caller's cwd)
/path/to/pi-mono/pi-test.sh

# Testing
./test.sh                         # Non-LLM tests (no API keys needed)
npm test                          # All tests
```

For forking/rebranding, configure via `package.json`:

```json
{
  "piConfig": {
    "name": "my-agent",
    "configDir": ".my-agent"
  }
}
```

Always use `src/config.ts` (`getPackageDir()`, `getThemeDir()`) for package asset paths — never `__dirname` directly.

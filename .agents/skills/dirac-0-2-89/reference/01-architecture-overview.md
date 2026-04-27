# Architecture Overview

## Core Flow

Dirac follows a layered architecture:

```
Extension Entry (extension.ts)
  → Webview Manager (core/webview/)
    → Controller (core/controller/index.ts)
      → Task Runner (core/task/index.ts)
        → Tool Executor (core/task/tools/)
          → Individual Tool Handlers
```

The **controller** handles webview messages and task lifecycle. The **task runner** executes API requests, processes LLM responses, and dispatches tool operations. Each tool has a dedicated handler class implementing either `IToolHandler` or `IFullyManagedTool`.

## Codebase Modules

| Directory | Purpose |
|-----------|---------|
| `src/core/task/` | Task execution loop, state management, API conversation handling |
| `src/core/task/tools/` | Tool implementations (edit_file, read_file, execute_command, etc.) |
| `src/core/prompts/` | System and tool prompt templates for LLM instructions |
| `src/core/controller/` | High-level extension coordination, state management, gRPC handlers |
| `src/core/context/` | Context gathering — user instructions, skills, rule conditionals |
| `src/core/slash-commands/` | Slash command definitions and parsing |
| `src/integrations/` | Terminal, Browser, Editor API wrappers, checkpoints, diagnostics |
| `src/services/` | Shared services — Logging, Telemetry, Tree-sitter, Symbol Index |
| `src/shared/` | Cross-component types, utilities, tool registry, API provider configs |
| `webview-ui/` | React-based frontend for VS Code extension UI |
| `cli/` | TypeScript/React Ink CLI implementation |
| `proto/dirac/` | Protocol Buffer definitions for internal messaging |

## Key Files

- `src/extension.ts` — Extension entry point
- `src/core/task/index.ts` — Main task logic and execution loop
- `src/shared/tools.ts` — Tool registry (DiracDefaultTool enum)
- `src/core/api/index.ts` — API factory (`createHandlerForProvider`)
- `src/shared/api.ts` — Model metadata, pricing, capability flags
- `src/utils/AnchorStateManager.ts` — Hash anchor state management
- `src/utils/ASTAnchorBridge.ts` — AST-to-anchor bridge for skeleton/function extraction

## CLI Architecture

The CLI (`cli/src/`) is a standalone terminal application built with React Ink that shares the same core backend as the VS Code extension. Key components:

- `cli/src/index.ts` — CLI entry point, command parsing via Commander.js
- `cli/src/agent/DiracAgent.ts` — Agent session management for CLI
- `cli/src/controllers/CliWebviewProvider.ts` — Bridges CLI to the shared webview/controller layer
- `cli/src/vscode-shim.ts` — Shim layer that provides VS Code APIs to the core code running in CLI context
- `cli/src/components/` — React Ink UI components for terminal rendering
- `cli/src/context/` — CLI-specific context handling

The CLI uses a **vscode-shim** pattern: it implements the VS Code extension host API interfaces so that the core Dirac code (written for VS Code) runs unchanged in the terminal. This is why both CLI and extension share identical behavior and tool access.

## API Provider Architecture

Provider handlers live in `src/core/api/providers/` with individual implementations for Anthropic, OpenAI, Gemini, Bedrock, etc. Each implements the `ApiHandler` interface. The API factory (`createHandlerForProvider`) instantiates the correct handler based on user configuration. Stream handling in `src/core/api/transform/` normalizes various provider stream formats into Dirac's internal `ApiStream`.

## Protocol Buffers

Dirac uses Protocol Buffers (`proto/dirac/`) for structured internal messaging between components. Generated code lives in `src/generated/` and `src/shared/proto/`. Run `npm run protos` before building.

## Development Setup

```bash
npm run install:all   # Install all dependencies
npm run protos        # Generate protobuf code (required before build)
npm run build         # Build the project
npm test              # Run tests
npm run lint          # Lint with Biome
```

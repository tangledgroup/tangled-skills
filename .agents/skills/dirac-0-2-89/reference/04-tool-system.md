# Tool System

## Tool Registry

All tools are defined in `src/shared/tools.ts` as the `DiracDefaultTool` enum:

### Read-Only Tools

These tools do not modify workspace state and can run in parallel with checkpoint operations:

- `list_files` — List files in a directory or matching glob patterns
- `read_file` — Read file content (with hash anchors prepended)
- `search_files` — Search files using ripgrep
- `get_file_skeleton` — Extract AST definition lines with anchors
- `get_function` — Retrieve specific functions by name
- `find_symbol_references` — Find all references to a symbol
- `diagnostics_scan` — Run linter diagnostics on files
- `browser_action` — Headless browser navigation and interaction
- `ask_followup_question` — Ask the user a clarifying question
- `web_search` — Search the web
- `web_fetch` — Fetch and parse web content
- `use_skill` — Load and apply a skill definition
- `list_skills` — List available skills
- `use_subagents` — Spawn parallel subagent tasks

### Write Tools

These tools modify workspace state:

- `edit_file` — Hash-anchored file editing (insert_after, insert_before, replace)
- `write_to_file` — Create or overwrite a file
- `execute_command` — Run terminal commands
- `replace_symbol` — Replace all occurrences of a symbol
- `rename_symbol` — Rename a symbol with validation

### Task Management Tools

- `attempt_completion` — Signal task completion for review
- `new_task` — Start a new sub-task
- `plan_mode_respond` — Respond in plan mode (strategy before execution)
- `condense` — Condense conversation history to save tokens
- `summarize_task` — Generate a task summary
- `report_bug` — Create a GitHub issue for Dirac bugs
- `new_rule` — Create a new Dirac Rule from conversation context
- `generate_explanation` — Generate code explanations

## Handler Patterns

Tool handlers implement one of two interfaces:

### IToolHandler

Simple handler with an `execute(config, block)` method. Used for straightforward tools.

### IFullyManagedTool

Extended handler that also implements:
- `getDescription(block)` — Returns a human-readable description for the UI
- `handlePartialBlock(block, uiHelpers)` — Handles streaming/partial tool call blocks during LLM generation

`IFullyManagedTool` is used for complex tools like `edit_file` that need to show progress during generation and manage approval workflows.

## Approval Workflow

Dirac uses an approval-based workflow for sensitive actions:

1. **Auto-approved tools**: Read-only tools are auto-approved by default
2. **User approval**: Write tools prompt the user with a diff/summary before execution
3. **Path-scoped approval**: Auto-approval can be configured per file path pattern
4. **Yolo mode** (`-y` flag): Bypasses all approvals (use with caution)
5. **Auto-approve-all** (`--auto-approve-all`): Approves all actions but keeps UI visible

The `ToolValidator` class validates tool parameters before execution, incrementing `consecutiveMistakeCount` on validation failures. After too many consecutive mistakes, the task may be flagged for review.

## Tool Execution Pipeline

1. LLM generates tool use blocks in its response
2. `StreamResponseHandler` parses blocks as they stream in
3. `handlePartialBlock()` updates the UI with progress
4. On completion, `execute()` is called on the appropriate handler
5. Handler validates parameters via `ToolValidator`
6. For write tools: approval prompt → user confirmation
7. Tool executes and returns a `ToolResponse`
8. Response is formatted and sent back to the LLM
9. Telemetry captures tool usage metrics

## Dynamic Tools

Dirac supports dynamic tool registration via `setDynamicToolUseNames(namespace, names)`. This allows extensions or custom configurations to add tools beyond the built-in set. The `getToolUseNames()` function returns both static and dynamic tools.

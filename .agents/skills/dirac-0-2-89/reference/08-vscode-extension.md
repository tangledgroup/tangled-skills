# VS Code Extension

## Installation

1. Open VS Code
2. Go to Extensions view (`Ctrl+Shift+X`)
3. Search for **Dirac**
4. Click Install

Available on the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=dirac-run.dirac).

## Getting Started

### 1. Open the Dirac Sidebar

Click the Dirac icon (δ) in the Activity Bar (left side of VS Code) to open the Dirac panel.

### 2. Configure Your Provider

- Click the Settings icon in the Dirac panel
- Select your preferred provider (Anthropic, OpenAI, OpenRouter, Gemini, etc.)
- Enter your API Key
- Select the model you wish to use

### 3. Start Your First Task

Type a description of what you want to do in the chat box and press Enter:

```
Add a new 'Contact' page to this React app.
```

## Key Features

### Chat Interface

Watch Dirac think and execute tools in real-time with a full approval workflow for sensitive actions. Each tool call shows its progress, and write operations require explicit user approval (unless auto-approved).

### History

Access all past tasks and resume exactly where you left off in any previous session. Task history is persisted locally.

### Dirac Rules

Define custom instructions that the agent should always follow — either project-specific (stored in `.dirac/rules/`) or global. Rules can have conditional triggers based on file paths, symbol patterns, or other context.

- Use `/newrule` during a conversation to create a rule from the current context
- Rules are loaded automatically when relevant to the task

### Worktrees

Dirac can work in isolated git worktree environments, preventing interference with your uncommitted changes. Accessible through the worktree management UI in the sidebar.

## Slash Commands

| Command | Description |
|---------|-------------|
| `/newtask` | Start a new task while carrying over important context |
| `/smol` | Condense chat history to save tokens and improve performance |
| `/explain-changes` | Analyze and explain differences between git refs (branches, commits, or PRs) |
| `/newrule` | Create a new Dirac Rule based on the current conversation |
| `/reportbug` | Automatically create a GitHub issue for Dirac bugs |

## Settings

### Auto-Approval

Choose which tools Dirac can run without asking for permission. Configurable per-tool and per-path-pattern.

### Browser Settings

Configure how Dirac interacts with websites:
- Window size
- Headless mode toggle
- Browser binary path

### Model Configuration

Fine-tune model parameters:
- Temperature
- Max tokens
- Reasoning effort
- Thinking budget

### Theme

Toggle between light and dark modes, or follow your VS Code theme automatically.

## Autonomous Tools

Dirac's VS Code extension has access to a comprehensive tool suite:

- **File Operations**: Read, write, edit (hash-anchored), search, list files
- **Terminal Execution**: Run shell commands with approval workflow
- **Browser Navigation**: Headless browser for web testing and scraping
- **AST Manipulation**: File skeletons, function extraction, symbol operations
- **Diagnostics**: Linter integration for real-time error feedback
- **Web Tools**: Search and fetch web content
- **Subagents**: Spawn parallel tasks for complex workflows

## Webview Architecture

The VS Code extension UI is built with React in `webview-ui/`. It communicates with the extension host via VS Code's webview messaging API. The `CliWebviewProvider` bridges this to the shared controller layer, ensuring both CLI and extension use identical core logic.

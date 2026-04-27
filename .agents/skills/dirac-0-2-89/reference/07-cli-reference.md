# CLI Reference

## Installation

```bash
npm install -g dirac-cli
```

Or via installation script (macOS/Linux):

```bash
curl -fsSL https://raw.githubusercontent.com/dirac-run/dirac/master/scripts/install.sh | bash
```

Requires Node.js >= 20.0.0. Built with TypeScript, React Ink for TUI rendering, Commander.js for CLI parsing.

## Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `task <prompt>` | `t` | Start a new task with the given prompt |
| `history` | `h` | List task history, browse and resume past work |
| `config` | — | Display current Dirac configuration and environment status |
| `auth` | — | Interactive authentication and provider configuration |
| `update` | — | Check for updates and install if available |
| `version` | — | Show current version |
| `kanban` | — | Launch Kanban board for task management (requires npx) |

## Basic Usage

```bash
# Start a task with a prompt
dirac "Refactor the login logic to use JWT"

# Interactive mode (no prompt = chat session)
dirac

# Plan mode — see strategy before executing
dirac -p "Analyze the architecture of this project"

# Yolo mode — auto-approve all actions
dirac -y "Fix the linting errors"

# Pipe context from other commands
git diff | dirac "Review these changes for potential bugs"
cat logs.txt | dirac "Analyze these logs and find the root cause"
```

## Authentication

### Interactive Setup

```bash
dirac auth
```

Follow prompts to select a provider and enter your API key.

### Non-Interactive Setup

```bash
dirac auth --provider anthropic --apikey YOUR_API_KEY --modelid claude-3-5-sonnet-20241022
```

### Environment Variables

Dirac reads API keys from standard environment variables:

| Provider | Environment Variable |
|----------|---------------------|
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Azure OpenAI | `AZURE_OPENAI_API_KEY` |
| Google Gemini | `GEMINI_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| Mistral | `MISTRAL_API_KEY` |
| Groq | `GROQ_API_KEY` |
| x.ai (Grok) | `XAI_API_KEY` |
| HuggingFace | `HF_TOKEN` |

When using environment variables, you must still specify `--provider` and `--model` flags if not previously configured via `dirac auth`.

### Custom OpenAI-Compatible Providers

```bash
export OPENAI_COMPATIBLE_CUSTOM_KEY=your_api_key
dirac "Refactor this function" --provider https://api.your-provider.com/v1 --model your-model-name
```

## Flags

### Execution Modes

- `-p, --plan` — Plan mode: analyze and present strategy before execution
- `-a, --act` — Act mode (default): perform actions with approval prompts
- `-y, --yolo` — Yolo mode: auto-approve all tool actions
- `--auto-approve-all` — Auto-approve but keep interactive UI visible

### Model & Performance

- `-m, --model <model>` — Override default model for this task
- `--provider <provider>` — Specify API provider (requires `--model`)
- `--thinking [tokens]` — Enable extended thinking (default: 1024 tokens)
- `--subagents` — Enable subagent spawning for parallelizable tasks

### Other

- `--verbose` — Enable verbose console output
- `--cwd <path>` — Set working directory
- `--continue` — Continue a previous task
- `--config <path>` — Load configuration from file
- `--reasoning-effort <level>` — Set reasoning effort (low/medium/high)
- `--max-consecutive-mistakes <n>` — Max mistakes before task review
- `--double-check-completion` — Extra validation on task completion
- `--auto-condense` — Automatically condense conversation when needed
- `--timeout <seconds>` — Task timeout
- `--json` — Output in JSON format
- `--hooks-dir <path>` — Custom hooks directory

## Slash Commands (Interactive Mode)

| Command | Description |
|---------|-------------|
| `/help` | Show available commands and usage tips |
| `/models` | Switch AI model for current session |
| `/clear` | Clear conversation and start fresh |
| `/newtask` | Start a new task, preserving relevant context |
| `/smol` | Manually trigger context condensation to save tokens |
| `/exit` | Exit the interactive session |

## Piping Context

Dirac reads from stdin when piped:

```bash
git diff | dirac "Review these changes for potential bugs"
cat error.log | dirac "What caused this error?"
find . -name "*.ts" -exec grep -l "deprecated" {} \; | dirac "List these files and suggest replacements"
```

The piped content is automatically included as context for the task.

## Logging

CLI logs are written to `CLI_LOG_FILE` (path defined in `cli/src/vscode-shim.ts`). Use `--verbose` to see real-time console output.

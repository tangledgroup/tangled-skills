# Usage Examples

### Installation and Quick Start

```bash
# Install globally
npm install -g @mariozechner/pi-coding-agent

# Run with API key
export ANTHROPIC_API_KEY=sk-ant-...
pi

# Or use OAuth login
pi
/login  # Select provider, authenticate in browser
```

### Interactive Mode Commands

Type `/` in the editor to trigger commands:

| Command | Description |
|---------|-------------|
| `/login`, `/logout` | OAuth authentication |
| `/model` | Switch models (or Ctrl+L) |
| `/scoped-models` | Enable/disable models for Ctrl+P cycling |
| `/settings` | Thinking level, theme, message delivery, transport |
| `/resume` | Pick from previous sessions |
| `/new` | Start a new session |
| `/name <name>` | Set session display name |
| `/session` | Show session info (path, tokens, cost) |
| `/tree` | Jump to any point in the session and continue from there |
| `/fork` | Create a new session from the current branch |
| `/compact [prompt]` | Manually compact context, optional custom instructions |
| `/copy` | Copy last assistant message to clipboard |
| `/export [file]` | Export session to HTML file |
| `/share` | Upload as private GitHub gist with shareable HTML link |
| `/reload` | Reload keybindings, extensions, skills, prompts, and context files (themes hot-reload automatically) |
| `/hotkeys` | Show all keyboard shortcuts |
| `/changelog` | Display version history |
| `/quit` | Quit pi |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+C | Clear editor (twice to quit) |
| Escape | Cancel/abort (twice to open `/tree`) |
| Ctrl+L | Open model selector |
| Ctrl+P / Shift+Ctrl+P | Cycle scoped models forward/backward |
| Shift+Tab | Cycle thinking level |
| Ctrl+O | Collapse/expand tool output |
| Ctrl+T | Collapse/expand thinking blocks |
| @ | Fuzzy-search project files |
| Tab | Complete paths |
| Shift+Enter | Multi-line input (or Ctrl+Enter on Windows Terminal) |
| Ctrl+V | Paste images (Alt+V on Windows), or drag onto terminal |
| `!command` | Run bash and send output to LLM |
| `!!command` | Run bash without sending to LLM |

### Message Queue

Submit messages while the agent is working:
- **Enter**: Queues a *steering* message, delivered after current assistant turn finishes executing tool calls
- **Alt+Enter**: Queues a *follow-up* message, delivered only after agent finishes all work
- **Escape**: Aborts and restores queued messages to editor
- **Alt+Up**: Retrieves queued messages back to editor

Configure delivery in settings: `steeringMode` and `followUpMode` can be `"one-at-a-time"` (default) or `"all"`. `transport` selects provider preference (`"sse"`, `"websocket"`, or `"auto"`).

### Provider and Model Selection

Pi supports 15+ providers with hundreds of models. Switch mid-session with `/model` or Ctrl+L.

**Model selection patterns:**
```bash
# By provider and model
pi --provider anthropic --model claude-sonnet-4

# With provider prefix (no --provider needed)
pi --model openai/gpt-4o "Help me refactor"

# With thinking level shorthand
pi --model sonnet:high "Solve this complex problem"

# Limit model cycling to specific patterns
pi --models "claude-*,gpt-4o"
```

**Thinking levels:** `off`, `minimal`, `low`, `medium`, `high`, `xhigh` (set via `/settings` or Shift+Tab)

### Package Management

Install, remove, and update pi packages (extensions, skills, prompts, themes):

```bash
# Install from npm
pi install npm:@foo/pi-tools
pi install npm:@foo/pi-tools@1.2.3      # pinned version

# Install from git
pi install git:github.com/user/repo
pi install git:github.com/user/repo@v1  # tag or commit
pi install https://github.com/user/repo@v1

# Project-local install (-l flag)
pi install -l npm:@foo/pi-tools

# Manage packages
pi list          # List installed packages
pi update        # Update (skips pinned)
pi remove npm:@foo/pi-tools
pi config        # Enable/disable extensions, skills, prompts, themes
```

**Security:** Pi packages run with full system access. Review source code before installing third-party packages.

### CLI Reference

```bash
pi [options] [@files...] [messages...]
```

**Modes:**
- Default: Interactive mode
- `-p`, `--print`: Print response and exit
- `--mode json`: Output all events as JSON lines
- `--mode rpc`: RPC mode for process integration
- `--export <in> [out]`: Export session to HTML

**Session options:**
- `-c`, `--continue`: Continue most recent session
- `-r`, `--resume`: Browse and select session
- `--session <path>`: Use specific session file or partial UUID
- `--fork <path>`: Fork specific session file or partial UUID into new session
- `--no-session`: Ephemeral mode (don't save)

**Tool options:**
- `--tools <list>`: Enable specific built-in tools (default: `read,bash,edit,write`)
- `--no-tools`: Disable all built-in tools (extension tools still work)

**Resource options:**
- `-e`, `--extension <source>`: Load extension from path, npm, or git (repeatable)
- `--no-extensions`: Disable extension discovery
- `--skill <path>`: Load skill (repeatable)
- `--no-skills`: Disable skill discovery
- `--prompt-template <path>`: Load prompt template (repeatable)
- `--theme <path>`: Load theme (repeatable)

**File arguments:** Prefix files with `@` to include in the message:
```bash
pi @prompt.md "Answer this"
pi -p @screenshot.png "What's in this image?"
pi @code.ts @test.ts "Review these files"
```

### Piped Input

In print mode, pi reads piped stdin and merges it into the initial prompt:
```bash
cat README.md | pi -p "Summarize this text"
```

### Why Minimalism Works

**Benchmark results**: pi with Claude Opus 4.5 on Terminal-Bench 2.0 competed against Codex, Cursor, Windsurf, and other harnesses with native models. Results: https://github.com/laude-institute/terminal-bench (see leaderboard placement).

**Key insight**: Terminus 2 (Terminal-Bench team's own minimal agent) just gives the model a tmux session - no fancy tools, no file operations, raw terminal interaction. It holds its own against agents with sophisticated tooling. Evidence that minimal approach works.

**Why it works:**
1. **Models are RL-trained**: Frontier models inherently understand what coding agents are - they don't need 10,000 tokens of system prompt
2. **Training data**: Models trained on read/write/edit tools with similar schemas, know how to use bash
3. **Context efficiency**: ~1000 tokens for system prompt + tool definitions vs 7-9% context window waste from MCP servers
4. **Progressive disclosure**: CLI tools with READMEs only cost tokens when agent reads them (on-demand)
5. **Observability**: Full visibility into what agent does vs black-box sub-agents
6. **Workflow matters**: Context gathering in separate session → artifact → fresh session beats mid-session sub-agents

**Real-world validation**: Pi used exclusively for day-to-day work, hundreds of exchanges in single session without compaction issues. Terminal-Bench results prove contrarian design decisions work in practice.

### Understanding Provider Abstraction

When you call an LLM in pi, you don't directly invoke OpenAI or Anthropic APIs. Instead:

1. You select a model using `getModel("anthropic", "claude-sonnet-4")`
2. The model object contains metadata (API type, capabilities, pricing)
3. When you stream a response, pi looks up which provider implementation handles that API type
4. The provider is loaded lazily (only when first used)
5. The provider translates your request to its native format, calls the API, and converts responses back to pi's unified event format

This means you can switch models mid-conversation without changing your code. The agent can even hand off work between different providers - Claude's thinking output becomes tagged text that GPT-5 can read.

### Understanding the Agent Loop

The agent runs a continuous loop:

1. **Turn starts**: Collect all messages (user prompts, assistant responses, tool results)
2. **Send to LLM**: Convert messages to provider format, stream response
3. **Receive response**: Emit events for each chunk of text, thinking, or tool call
4. **Execute tools**: If the response includes tool calls, execute them (in parallel if independent)
5. **Add results**: Tool results become new messages in the conversation
6. **Check queues**: Process any steering (interrupt) or follow-up (queued) messages
7. **Repeat or end**: If tools were called or there are queued messages, go to step 1; otherwise finish

At every step, events are emitted so the UI can update and extensions can react. The loop handles errors gracefully - if a tool fails, the error becomes a tool result message that the LLM can see and recover from.

### Understanding Differential Rendering

Terminal UIs traditionally flicker because they clear the screen and redraw everything on each update. Pi uses three rendering strategies:

**First Render**: Just output all lines without clearing scrollback history.

**Width Changed**: When terminal resizes, clear screen and fully re-render (layouts need recalculation).

**Normal Update**: Find the first line that changed, move cursor there, clear to end of screen, render only changed lines.

All updates are wrapped in "synchronized output" mode (CSI 2026), which tells the terminal to batch all changes and display them atomically. This prevents users from seeing intermediate states during rendering.

### Understanding Session Branching

Sessions are trees, not linear histories. When you branch:

1. Pi copies all entries up to the branch point into a new session
2. If branching from an old point (not the latest), it generates a summary of what happened after that point
3. The new session is independent - changes don't affect the original
4. You can switch between branches anytime, or create branches from branches

This enables workflows like "try this risky refactoring in a branch, if it works merge it back, if not discard the branch."

### Understanding Compaction

LLMs have limited context windows. When a session grows too large:

1. Pi detects approaching the limit (with a safety buffer)
2. It finds a cut point - where to start summarizing from
3. It sends old messages to an LLM with instructions to summarize key decisions, changes, and context
4. The summary replaces the old messages, freeing up tokens
5. A compaction entry records what was removed and how many tokens were saved

Compaction preserves important information while discarding details no longer needed. You can also manually trigger compaction with custom instructions via `/compact "summarize focusing on X"`.

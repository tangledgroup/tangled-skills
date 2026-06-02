# Supported Agents

## Contents
- Integration Tiers Explained
- Agent Setup Reference
- Windows Support
- Graceful Degradation
- Per-Agent Details

## Integration Tiers Explained

| Tier | Mechanism | Guarantee | Examples |
|------|-----------|-----------|----------|
| **Shell hook** | Shell script or Rust binary intercepts via agent API | Guaranteed rewrite before agent sees output | Claude Code, Cursor, Gemini CLI, Copilot |
| **Plugin** | TypeScript/Python in agent's plugin system, in-place mutation | Transparent when agent allows mutation | OpenCode, Pi, Hermes, OpenClaw |
| **Rules file** | Prompt-level instructions written to project config | Guidance only — model must comply | Cline, Windsurf, Codex, Kilo Code, Antigravity |

Shell hooks guarantee rewriting. Rules files rely on the model following instructions. Plugin integrations use in-place mutation via the agent's TypeScript extension API.

## Agent Setup Reference

| Agent | Global Init | Local Init | Method |
|-------|------------|------------|--------|
| Claude Code | `rtk init --global` | `rtk init` | PreToolUse hook + settings.json |
| VS Code Copilot Chat | `rtk init --global --copilot` | — | PreToolUse hook |
| GitHub Copilot CLI | `rtk init --global --copilot` | — | PreToolUse deny-with-suggestion |
| Cursor | `rtk init --global --cursor` | — | preToolUse hook |
| Gemini CLI | `rtk init --global --gemini` | — | BeforeTool hook |
| Pi (global) | `rtk init --agent pi --global` | `rtk init --agent pi` | TypeScript extension |
| OpenCode | `rtk init --global --opencode` | — | TS plugin (`tool.execute.before`) |
| OpenClaw | `openclaw plugins install ./openclaw` | — | TS plugin (`before_tool_call`) |
| Hermes | `rtk init --agent hermes` | — | Python plugin (terminal mutation) |
| Cline / Roo Code | — | `rtk init --cline` | `.clinerules` rules file |
| Windsurf | — | `rtk init --windsurf` | `.windsurfrules` rules file |
| Codex CLI | — | `rtk init --codex` | Patches `AGENTS.md` |
| Kilo Code | — | `rtk init --agent kilocode` | `.kilocode/rules/rtk-rules.md` |
| Google Antigravity | — | `rtk init --agent antigravity` | `.agents/rules/antigravity-rtk-rules.md` |
| Mistral Vibe | — | — | Planned (blocked on upstream) |

## Per-Agent Details

### Claude Code
```bash
rtk init --global          # Hook + patches settings.json
rtk init --show            # Verify hook status
```
Installs hook to `~/.claude/hooks/rtk-rewrite.sh`, creates `~/.claude/RTK.md` (10 lines), adds `@RTK.md` reference to `~/.claude/CLAUDE.md`.

### Cursor
```bash
rtk init --global --cursor
```
Uses Cursor's `preToolUse` hook with `updated_input` format.

### Pi
```bash
rtk init --agent pi                    # Project-local: .pi/extensions/rtk.ts
rtk init --agent pi --global           # Global: ~/.pi/agent/extensions/rtk.ts
rtk init --uninstall --agent pi        # Remove local extension
rtk init --uninstall --agent pi --global  # Remove global extension
```
Pi auto-discovers extensions from both paths on startup.

### OpenCode
Creates `~/.config/opencode/plugins/rtk.ts` using the `tool.execute.before` hook.

### Hermes
Creates `~/.hermes/plugins/rtk-rewrite/`. The plugin fails open — if RTK is missing or errors, the original command runs unchanged. Source lives in `hooks/hermes/` in the repo.

### Cline / Roo Code
```bash
rtk init --cline    # creates .clinerules in current project
```
Cline reads `.clinerules` as custom instructions telling it to prefer `rtk <cmd>`.

### Windsurf
```bash
rtk init --windsurf    # creates .windsurfrules in current project
```

### Codex CLI
```bash
rtk init --codex    # creates AGENTS.md or patches existing one
```

### Kilo Code
```bash
rtk init --agent kilocode    # creates .kilocode/rules/rtk-rules.md
```

### Google Antigravity
```bash
rtk init --agent antigravity    # creates .agents/rules/antigravity-rtk-rules.md
```

## Windows Support

Shell hooks require a Unix shell. On native Windows:
- `rtk init -g` falls back to **CLAUDE.md injection mode** (prompt-level instructions)
- Filters work normally (`rtk cargo test`, `rtk git status`)
- Auto-rewrite does not work

For full hook support, use WSL where RTK works identically to Linux.

## Graceful Degradation

Hooks never block command execution:
- RTK binary not found → warning to stderr, exit 0 (raw command runs)
- Invalid JSON input → pass through unchanged
- RTK version too old → warning to stderr, exit 0
- Filter logic error → fallback to raw command output

## Override: Disable RTK for One Command

```bash
RTK_DISABLED=1 git status    # runs raw git status, no rewrite
```

Or exclude permanently in `~/.config/rtk/config.toml`:
```toml
[hooks]
exclude_commands = ["git rebase", "git cherry-pick"]
```

# Optional Features

## Telegram Notifications

Get progress updates via Telegram bot messages.

### Setup

1. Create a bot via `@BotFather` on Telegram — get the bot token
2. Start a conversation with your bot, then visit:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   Find your chat ID from the response
3. Set environment variables:
   ```bash
   export TG_BOT_TOKEN="your-bot-token-here"
   export TG_CHAT_ID="your-chat-id-here"
   ```

### Usage

```bash
# Enable telegram notifications (requires TG_BOT_TOKEN and TG_CHAT_ID)
./scripts/ralph-loop.sh

# Enable audio notifications (also requires CHUTES_API_KEY)
./scripts/ralph-loop.sh --telegram-audio

# Disable telegram
./scripts/ralph-loop.sh --no-telegram
```

### Notifications You Receive

- 🚀 Loop start notifications
- ✅ Spec completion notifications with mermaid diagrams
- ⚠️ Warnings for consecutive failures or stuck specs
- 🏁 Summary when loop finishes

### Audio Notifications

Requires a Chutes API key (`CHUTES_API_KEY`). Uses Kokoro TTS with multiple voice options (American/British male/female). Enable with `--telegram-audio` flag.

### Security

Never commit bot tokens or chat IDs to version control. Add `.env` to `.gitignore`.

## GitHub Issues Integration

Configure the constitution to work on GitHub issues in addition to spec files:

```markdown
## GitHub Issues

Work on issues from `owner/repo` in addition to specs. Use `gh` CLI:
  gh issue list --repo owner/repo --state open
  gh issue close <number> --repo owner/repo
```

The agent uses the `gh` CLI to list, work on, and close issues. You can restrict the agent to only work on issues approved by a specific person.

## Completion Logs

When enabled in the constitution, each spec completion creates entries in `completion_log/`:

- `YYYY-MM-DD--HH-MM-SS--spec-name.md` — Summary and mermaid code
- `YYYY-MM-DD--HH-MM-SS--spec-name.png` — Rendered mermaid diagram

These provide a visual history of what was built over time.

## History Tracking

After each spec completion, the agent:

1. Appends a 1-line summary to `history.md`
2. Creates `history/YYYY-MM-DD--spec-name.md` with lessons learned, decisions made, and issues encountered

The agent checks history before starting work on any spec to avoid repeating past mistakes.

## Alternative Agent Backends

Ralph Wiggum provides separate loop scripts for different AI agents:

- `scripts/ralph-loop.sh` — Claude Code (default)
- `scripts/ralph-loop-codex.sh` — OpenAI Codex
- `scripts/ralph-loop-gemini.sh` — Google Gemini
- `scripts/ralph-loop-copilot.sh` — GitHub Copilot

Each script follows the same loop pattern but invokes a different agent CLI. Usage is identical:

```bash
./scripts/ralph-loop-codex.sh plan    # Plan mode with Codex
./scripts/ralph-loop-codex.sh         # Build mode with Codex
./scripts/ralph-loop-codex.sh 20      # Max 20 iterations
```

## Compatible Platforms

Ralph Wiggum works with: Claude Code, Cursor, Codex, Windsurf, Amp, OpenCode, and any agent that can follow the prompts and execute shell commands.

# Constitution Reference

The constitution (`.specify/memory/constitution.md`) is the single source of truth for all agent behavior in a Ralph Wiggum project. The agent reads it every iteration.

## Full Template

```markdown
# {PROJECT_NAME} Constitution

> {PROJECT_VISION}

---

## Context Detection

**Ralph Loop Mode** (started by ralph-loop*.sh):
- Pick highest priority incomplete spec from `specs/`
- Implement, test, commit, push
- Output `<promise>DONE</promise>` only when 100% complete
- Output `<promise>ALL_DONE</promise>` when no work remains

**Interactive Mode** (normal conversation):
- Be helpful, guide decisions, create specs

---

## Core Principles

{List the user's principles, one per line}

---

## Technical Stack

{List or "Detected from codebase"}

---

## Autonomy

YOLO Mode: {ENABLED/DISABLED}
Git Autonomy: {ENABLED/DISABLED}

---

## Specs

Specs live in `specs/` as markdown files. Pick the highest priority incomplete spec (lower number = higher priority). A spec is incomplete if it lacks `## Status: COMPLETE`.

Spec template: https://raw.githubusercontent.com/github/spec-kit/refs/heads/main/templates/spec-template.md

When all specs are complete, re-verify a random one before signaling done.

---

## NR_OF_TRIES

Track attempts per spec via `<!-- NR_OF_TRIES: N -->` at the bottom of the spec file. Increment each attempt. At 10+, the spec is too hard — split it into smaller specs.

---

## History

Append a 1-line summary to `history.md` after each spec completion. For details, create `history/YYYY-MM-DD--spec-name.md` with lessons learned, decisions made, and issues encountered. Check history before starting work on any spec.

---

## Completion Signal

All acceptance criteria verified, tests pass, changes committed and pushed → output `<promise>DONE</promise>`. Never output this until truly complete.
```

## Optional Sections

Add these to the constitution only when the corresponding feature is enabled.

### Telegram Notifications

```markdown
---

## Telegram Notifications

Send progress via Telegram using env vars `TG_BOT_TOKEN` and `TG_CHAT_ID`.

After completing a spec:
  curl -s -X POST "https://api.telegram.org/bot$TG_BOT_TOKEN/sendMessage" \
    -d chat_id="$TG_CHAT_ID" -d parse_mode=Markdown \
    -d text="✅ *Completed:* {spec name}%0A{one-line summary}"

Also notify on: 3+ consecutive failures, stuck specs (NR_OF_TRIES >= 10).
```

### GitHub Issues Integration

```markdown
---

## GitHub Issues

Work on issues from `{OWNER/REPO}` in addition to specs. Use `gh` CLI:
  gh issue list --repo {OWNER/REPO} --state open
  gh issue close <number> --repo {OWNER/REPO}
```

### Completion Logs

```markdown
---

## Completion Logs

After each spec, create `completion_log/YYYY-MM-DD--HH-MM-SS--spec-name.md` with a brief summary.
```

## Key Configuration Points

**YOLO Mode**: When ENABLED, the agent executes commands, modifies files, and runs tests without asking for permission each time. This is recommended for autonomous operation.

**Git Autonomy**: When ENABLED, the agent commits and pushes automatically after each spec completion.

**Spec Sources**: During installation you can choose:
1. SpecKit Specs (default) — Markdown files in `specs/`
2. GitHub Issues — Fetch from a repository
3. Custom Source — Your own mechanism

The constitution adapts to whichever source is chosen.

## Best Practices

- Keep the constitution concise — it's read every iteration
- Make core principles actionable, not aspirational
- Set YOLO Mode and Git Autonomy to ENABLED for full autonomy
- Store optional feature configuration in the constitution, not baked into scripts
- Never put secrets (bot tokens, API keys) in the constitution — use environment variables

# Configuration & Loop Tuning

## ralph.config.cjs

After `wiggum init`, the main configuration file is `.ralph/ralph.config.cjs`. It contains stack detection results and loop settings:

```javascript
module.exports = {
  name: 'my-project',
  stack: {
    framework: {
      name: 'Next.js',
      version: '15.0',
      variant: 'App Router',
    },
    packageManager: 'pnpm',
    testing: {
      unit: 'Vitest',
      e2e: 'Playwright',
    },
    styling: 'Tailwind CSS',
  },
  commands: {
    dev: 'pnpm dev',
    build: 'pnpm build',
    test: 'pnpm test',
    lint: 'pnpm lint',
    typecheck: 'pnpm typecheck',
  },
  paths: {
    root: '.ralph',
    prompts: '.ralph/prompts',
    guides: '.ralph/guides',
    specs: '.ralph/specs',
    scripts: '.ralph/scripts',
    learnings: '.ralph/LEARNINGS.md',
    agents: '.ralph/AGENTS.md',
  },
  loop: {
    maxIterations: 10,
    maxE2eAttempts: 5,
    defaultModel: 'sonnet',    // Claude implementation/e2e default
    planningModel: 'opus',     // Claude planning/review default
    codexModel: 'gpt-5.3-codex', // Codex model default
    codingCli: 'claude',       // Implementation CLI: 'claude' | 'codex'
    reviewCli: 'claude',       // Review CLI: 'claude' | 'codex'
    reviewMode: 'manual',      // 'manual' | 'auto' | 'merge'
    claudePermissionMode: 'default',
    codexSandbox: 'workspace-write',
    codexApprovalPolicy: 'never',
    disableMcpInAutomatedRuns: true,
  },
};
```

## Model Selection

### Claude Models

- `defaultModel` — Used for implementation and E2E testing phases (default: `sonnet`)
- `planningModel` — Used for planning and review phases (default: `opus`)
- Override per run with `--model <model>` on the CLI

### Codex Models

- `codexModel` — Default model for all Codex phases (default: `gpt-5.3-codex`)
- Override per run with `--model <model>` on the CLI

### Mixed Agent Workflows

You can use different agents for implementation and review:

```bash
# Codex implements, Claude reviews
wiggum run feature --cli codex --review-cli claude
```

This is useful when you want to leverage Codex's speed for implementation but Claude's reasoning for review.

## Review Modes

Three levels of automation for the PR phase:

| Mode | Behavior |
|------|----------|
| `manual` | Loop stops at PR creation. Human reviews and merges. (default) |
| `auto` | Agent reviews the diff against spec. Does not merge. |
| `merge` | Agent reviews the diff against spec and auto-merges when checks pass. |

Set in config or override with `--review-mode`:

```bash
wiggum run feature --review-mode merge
```

## Git Worktree Isolation

The `--worktree` flag creates an isolated git worktree for each feature. This enables:

- Parallel feature development — multiple Ralph loops running simultaneously on different features
- Clean branch isolation — no cross-contamination between features
- Easy rollback — delete the worktree without affecting the main branch

```bash
wiggum run feature-a --worktree
wiggum run feature-b --worktree  # runs in parallel
```

## Claude Permission Modes

Control how Claude Code interacts with your filesystem:

| Mode | Description |
|------|-------------|
| `default` | Standard permission prompts |
| `auto` | Auto-approve safe operations |
| `dontAsk` | Never prompt, always proceed |
| `acceptEdits` | Accept file edits without prompting |
| `plan` | Read-only planning mode |
| `bypassPermissions` | Skip all permission checks |

Set in `loop.claudePermissionMode`. Use cautiously — `bypassPermissions` and `dontAsk` skip safety checks.

## Codex Sandbox Settings

Control Codex CLI's access level:

| Setting | Description |
|---------|-------------|
| `read-only` | Can read files, cannot modify |
| `workspace-write` | Can modify project files (default) |
| `danger-full-access` | Full filesystem access |

Set in `loop.codexSandbox`. Approval policy (`loop.codexApprovalPolicy`) controls when Codex asks for confirmation:

- `untrusted` — Ask before every command
- `on-failure` — Ask only when commands fail
- `on-request` — Ask when Codex explicitly requests
- `never` — Never ask (default)

## MCP Server Management

Wiggum detects MCP server configurations in your project and recommends servers based on your detected stack. During automated runs (`wiggum agent`, headless mode), MCP servers are disabled by default (`disableMcpInAutomatedRuns: true`) to prevent unexpected side effects. Set to `false` if your loop requires MCP tools.

## Prompt Templates

Wiggum generates prompt templates under `.ralph/prompts/`:

- `PROMPT.md` — Main implementation prompt
- `PROMPT_feature.md` — Feature planning prompt
- `PROMPT_e2e.md` — E2E testing prompt
- `PROMPT_verify.md` — Verification prompt
- `PROMPT_review_manual.md` — Manual review prompt (stop at PR)
- `PROMPT_review_auto.md` — Auto review prompt (review, no merge)
- `PROMPT_review_merge.md` — Merge review prompt (review + auto-merge)

These are tailored to your specific stack. You can edit them directly for fine-tuning. Recent versions have trimmed boilerplate from prompts to reduce token usage.

## Performance Tuning

### Token Reduction Strategies

- Merge verification phase into review phase to cut one full agent round
- Use `--resume` for implementation and E2E loop iterations 2+ (avoids re-sending context)
- Edit prompt templates to remove boilerplate the coding agent already knows
- Use smaller models for implementation (`sonnet`) and reserve larger models for planning/review (`opus`)

### Iteration Limits

Adjust `maxIterations` (default: 10) and `maxE2eAttempts` (default: 5) based on feature complexity. Simple features may need fewer iterations; complex integrations may need more.

## Context Refresh

When your project structure changes significantly (new dependencies, framework upgrades, directory reorganization), run:

```bash
wiggum sync
```

This re-scans the project and updates `.ralph/.context.json` with current stack information. Always sync before running new loops after major project changes.

# CLI Reference

## wiggum init

Scan the project, detect the tech stack, generate configuration.

```bash
wiggum init [options]
```

| Flag | Description |
|------|-------------|
| `--provider <name>` | AI provider: `anthropic`, `openai`, `openrouter` (default: `anthropic`) |
| `-i, --interactive` | Stay in interactive mode after init |
| `-y, --yes` | Accept defaults, skip confirmations |

What happens: Wiggum reads your `package.json`, config files, source tree, and directory structure. It runs a unified codebase analyzer that builds project context, commands, and implementation guidance from your actual codebase. MCP detection maps your detected stack to essential/recommended MCP server suggestions. All enriched context is saved under `.ralph/`.

Detection covers 80+ technologies across frameworks (Next.js, React, Vue, Svelte, Astro, Django, Rails), package managers (npm, yarn, pnpm, bun), testing tools (Jest, Vitest, Playwright, Cypress), databases (PostgreSQL, MySQL, MongoDB, Redis), ORMs (Prisma, Drizzle, TypeORM), styling (Tailwind, Sass, CSS Modules), auth (NextAuth, Clerk, Auth0), deployment targets (Vercel, Netlify, Docker, AWS), and more.

## wiggum new

Create a feature specification via AI-powered interview.

```bash
wiggum new <feature> [options]
```

| Flag | Description |
|------|-------------|
| `--provider <name>` | AI provider for spec generation |
| `--model <model>` | Model to use |
| `--issue <number\|url>` | Add GitHub issue as context (repeatable) |
| `--context <url\|path>` | Add URL/file context (repeatable) |
| `--auto` | Headless mode — skip TUI, generate spec without interaction |
| `--goals <description>` | Feature goals for `--auto` mode |
| `-e, --edit` | Open in editor after creation |
| `-f, --force` | Overwrite existing spec |

The interview follows four phases:

1. **Context** — Share reference URLs, docs, or files
2. **Goals** — Describe what you want to build
3. **Interview** — AI asks 3–5 clarifying questions grounded in your codebase
4. **Generation** — Produces a detailed feature spec in `.ralph/specs/`

Spec names are autocompleted from existing specs when using the TUI `/run` command. In headless mode (`--auto`), pass goals directly without interaction.

## wiggum run

Run the autonomous development loop.

```bash
wiggum run <feature> [options]
```

| Flag | Description |
|------|-------------|
| `--worktree` | Git worktree isolation (enables parallel feature development) |
| `--resume` | Resume an interrupted loop from last checkpoint |
| `--model <model>` | Model id override (applied per CLI; Codex defaults to `gpt-5.3-codex`) |
| `--cli <cli>` | Implementation CLI: `claude` or `codex` |
| `--review-cli <cli>` | Review CLI: `claude` or `codex` |
| `--max-iterations <n>` | Max iterations (default: 10) |
| `--max-e2e-attempts <n>` | Max E2E retries (default: 5) |
| `--review-mode <mode>` | `manual` (stop at PR), `auto` (review, no merge), or `merge` (review + auto-merge). Default: `manual` |

For loop models:
- Claude CLI phases use `defaultModel` / `planningModel` from config (defaults: `sonnet` / `opus`)
- Codex CLI phases default to `gpt-5.3-codex` across all phases

The run command hands the spec + prompts + project context to your coding agent and executes the Ralph loop: plan → implement → test → verify → PR. The TUI shows real-time progress with phase tracking, token usage, and an activity feed. Press `Esc` to background the run; use `/monitor` to re-enter.

## wiggum monitor

Track feature development progress in real-time.

```bash
wiggum monitor <feature> [options]
```

| Flag | Description |
|------|-------------|
| `--interval <seconds>` | Refresh interval (default: 5) |
| `--bash` | Use bash monitor script |
| `--stream` | Force headless streaming monitor output |

In interactive terminals, routes to the Ink TUI RunScreen with progress bars, token tracking, and live diffs.

## wiggum agent

Run the autonomous backlog executor — reads GitHub issues, generates specs, runs loops, reviews diffs, and auto-merges PRs.

```bash
wiggum agent [options]
```

| Flag | Description |
|------|-------------|
| `--model <model>` | Model override (defaults from `ralph.config.cjs`) |
| `--max-items <n>` | Max issues to process before stopping |
| `--max-steps <n>` | Max agent steps before stopping |
| `--labels <l1,l2>` | Only process issues matching these labels |
| `--issues <n1,n2,...>` | Only process specific issue numbers |
| `--review-mode <mode>` | `manual`, `auto`, or `merge` |
| `--dry-run` | Plan actions without executing |
| `--stream` | Stream output instead of waiting for final response |
| `--diagnose-gh` | Run GitHub connectivity diagnostics for agent flows |

Agent mode prioritizes issues by label (P0 > P1 > P2) and dependency order. It assesses feature state (fresh start, resume partial branch, or already shipped), generates specs from issue context, runs the full Ralph loop per issue, reviews diffs against the spec, and auto-merges when all checks pass — then moves to the next issue. Learns from outcomes and stores memory across iterations.

Run headless in CI: `wiggum agent --stream`.

## wiggum sync

Re-scan project and refresh saved context (`.ralph/.context.json`) using current provider/model settings. Useful when project structure changes or before running new loops to ensure context is current.

```bash
wiggum sync
```

## wiggum config

Manage API keys and loop settings.

```bash
wiggum config [options]
```

Accessed via `/config` or `/cfg` in the TUI. Manages provider selection, model configuration, and loop parameters.

## Spec Autocomplete

When running `/run` in the TUI, Wiggum pre-fills spec names from your `.ralph/specs/` directory using AI-generated suggestions grounded in your codebase context. Tab-complete to select.

## Action Inbox

During loop execution, the agent can request user input mid-execution without blocking. The loop pauses, you approve or redirect, it continues. This is implemented via IPC between the loop process and the TUI.

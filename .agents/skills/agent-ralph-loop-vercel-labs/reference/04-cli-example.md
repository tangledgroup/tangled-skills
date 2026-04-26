# CLI Example

The `examples/cli` directory in the repository contains a full-featured autonomous coding agent that demonstrates the Ralph Loop pattern with Vercel Sandbox, Playwright browser automation, and a Judge Agent for quality review.

## Architecture

```
Coding Agent (Claude Opus)  ──▶  Vercel Sandbox (Isolated Env)  ──▶  Judge Agent (Claude Opus)
     │                               │                                 │
     ▼                               ▼                                 ▼
 Writes code                   Runs commands                  Reviews work
 Takes screenshots             Dev server                     Approves/rejects
 Interacts with UI             Type-check/build               Visual verification
```

- **Coding Agent**: Uses `RalphLoopAgent` with Claude Opus. Writes code, runs commands, takes screenshots, interacts with the browser.
- **Vercel Sandbox**: Isolated environment with PostgreSQL, Redis, and Playwright pre-installed. Dev server accessible via a public URL.
- **Judge Agent**: Separate `generateText` call that reviews completed work using verification tools (run tests, type-check, build). Can approve or request changes.

## Usage

```bash
# Interactive Plan Mode
pnpm cli /path/to/project

# With an inline prompt
pnpm cli /path/to/project "Migrate from CommonJS to ESM"

# With a prompt file
pnpm cli /path/to/project ./my-task.md

# GitHub repo — clones, runs task, creates PR
pnpm cli https://github.com/owner/repo "Upgrade dependencies"
```

## Plan Mode

When no prompt is provided and no `PROMPT.md` exists, the CLI enters Plan Mode. The AI reads the codebase (read-only) to understand context, then generates a detailed plan with goals, steps, and completion criteria. The user can approve, refine, or cancel before execution begins.

## GitHub Repo Mode

When given a GitHub URL:

1. Clones to `tasks/[owner]/[repo]/[timestamp]/`
2. Runs Plan Mode or uses provided prompt
3. Executes the task in the sandbox
4. Creates a PR via `gh` CLI with branch name `ralph/<slug>-<short-hash>`

## Tools Available in the CLI

**File Operations:**

- `listFiles(pattern)` — Glob-based file listing
- `readFile(files[])` — Read one or more files, with optional `lineStart`/`lineEnd` for large files
- `writeFile(files[])` — Write one or more files (creates directories)
- `editFile(edits[])` — Batch search/replace editing (more token-efficient than full rewrites)
- `deleteFile(files[])` — Delete one or more files

**Environment:**

- `detectPackageManager()` — Detect npm/yarn/pnpm/bun from lock files
- `runCommand(command)` — Execute shell commands in the sandbox

**Web/Browser:**

- `startDevServer(command?)` — Start a dev server in background
- `curl(url, method?)` — Make HTTP requests to test the dev server
- `takeScreenshot(url?, fullPage?, analyze?, question?)` — Screenshot + AI vision analysis via Claude Sonnet
- `browserInteract(action, selector?, text?)` — Navigate, click, fill forms via Playwright
- `runPlaywrightTest(testFile)` — Run Playwright test files

**Completion:**

- `markComplete(summary, filesModified[])` — Signal task completion, triggers Judge Agent review

## Judge Agent

When the coding agent calls `markComplete`, the CLI invokes a separate judge agent that:

1. Runs verification commands (type-check, build, tests)
2. Reviews the work summary and modified files
3. Calls either `approveTask` or `requestChanges`
4. If changes are requested, feedback is injected back into the coding agent for another iteration

The judge uses its own tools (`runCommand`, `readFile`, `listFiles`, `approveTask`, `requestChanges`) and runs independently from the coding agent.

## Interrupt Handling

Press Ctrl+C during execution to see options:

- **Continue** — Resume the current task
- **Follow up** — Send a message to update the plan
- **Save & exit** — Copy files back from sandbox and exit
- **Quit** — Exit without saving changes

Press Ctrl+C twice quickly to force quit.

## Context Management in CLI

The CLI enables context management with generous budgets for long-running tasks:

```typescript
contextManagement: {
  maxContextTokens: 180_000,
  enableSummarization: true,
  recentIterationsToKeep: 2,
  maxFileChars: MAX_FILE_CHARS,
  changeLogBudget: 8_000,
  fileContextBudget: 60_000,
},
```

## Environment Variables

```bash
# Vercel Sandbox (required)
SANDBOX_VERCEL_TOKEN=your_vercel_token
SANDBOX_VERCEL_TEAM_ID=your_team_id
SANDBOX_VERCEL_PROJECT_ID=your_project_id

# Optional: GitHub CLI for PR creation
# Install with: brew install gh
# Authenticate with: gh auth login
```

## Key Design Patterns from the CLI

**1. Verify-then-execute loop:** The coding agent works, calls `markComplete`, the judge reviews, and if rejected, the agent iterates again with specific feedback.

**2. Context preservation on abort:** When interrupted, the agent's `preserveContext` flag allows resuming from the exact iteration count without losing accumulated conversation history.

**3. Plan-driven execution:** The initial plan (from Plan Mode or user prompt) defines completion criteria that feed into both the agent's instructions and the judge's evaluation.

**4. Visual verification:** Screenshots analyzed by a vision model let the agent "see" UI changes, enabling it to verify visual correctness without manual inspection.

**5. Efficient file operations:** `editFile` for surgical changes (search/replace) is preferred over `writeFile` for small modifications, saving tokens and preserving file structure.

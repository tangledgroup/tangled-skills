# Memory Systems

## The Memory Problem

Each Ralph iteration spawns a fresh AI instance with **zero internal memory** of previous iterations. The model doesn't remember what it did five minutes ago in the previous loop. This is by design — it keeps context windows clean and focused.

But Ralph needs memory to function. Without it, each iteration would start from scratch, potentially redoing work or making the same mistakes. Ralph solves this through **external memory systems** — files on disk that persist between iterations.

## Three Pillars of Memory

Ralph's memory system has three components:

1. **Git history** — Code changes committed by previous iterations
2. **progress.txt** — Append-only log of learnings and patterns
3. **prd.json** — Task list with completion status

These three files carry all necessary state between iterations. Everything else is derived from them.

## Git History as Memory

Git commits are Ralph's primary memory for code changes. Each iteration that successfully implements a story commits its changes:

```bash
git add -A
git commit -m "feat: [Story ID] - [Story Title]"
```

### Why Git Works as Memory

- **Immutable**: Commits cannot be silently changed
- **Searchable**: Ralph can use `git log`, `git show`, and ripgrep to find previous work
- **Context-rich**: Commit messages provide summaries of what was done
- **Verifiable**: Ralph can check out commits to verify behavior

### What Ralph Reads from Git

On each iteration, Ralph reads git history to understand:
- What code has been changed
- What patterns were used in previous implementations
- Whether related files were modified
- The evolution of the codebase

### Best Practices for Commits

- Commit after every completed story
- Use conventional commit format: `feat: [ID] - [Title]`
- Include all changes (code, tests, documentation) in one commit per story
- Never commit broken code — quality checks must pass first

## progress.txt: The Append-Only Log

`progress.txt` is Ralph's running journal. It records learnings, patterns, and context discovered during each iteration.

### Structure

```markdown
# Ralph Progress Log
Started: 2024-01-15

## Codebase Patterns
- Migrations: Use IF NOT EXISTS
- Types: Export from actions.ts
---

## 2024-01-15 14:32 - US-001
Thread: https://ampcode.com/threads/$AMP_CURRENT_THREAD_ID
- Added priority column to tasks table
- Files changed: db/schema.ts, migrations/001-add-priority.sql
- **Learnings for future iterations:**
  - Patterns discovered: This codebase uses Prisma for ORM
  - Gotchas encountered: Must run `npx prisma generate` after schema changes
  - Useful context: The settings panel is in component SettingsPanel.tsx
---

## 2024-01-15 14:45 - US-002
- Added priority badge component to task cards
- Files changed: components/PriorityBadge.tsx, components/TaskCard.tsx
- **Learnings for future iterations:**
  - Patterns discovered: Badge colors use CSS custom properties from :root
  - Gotchas encountered: Tailwind config needs updating for new color variants
---
```

### The Append-Only Rule

Ralph **never replaces** progress.txt — it always appends. This preserves the full history of learnings and creates a chronological record of the project's evolution.

```markdown
## Progress Report Format

APPEND to progress.txt (never replace, always append):
```

### Codebase Patterns Section

At the TOP of progress.txt, Ralph maintains a "Codebase Patterns" section that consolidates the most important reusable learnings:

```markdown
## Codebase Patterns
- Migrations: Always use `IF NOT EXISTS` for idempotency
- React: Use `useRef<Timeout | null>(null)` for timer refs
- API: Export types from actions.ts for UI components
- Testing: Mock external services in test setup
```

This section is updated by Ralph as it discovers new patterns. It serves as a quick reference for future iterations, avoiding the need to scan through the entire progress log.

### What to Include in Learnings

**Good learnings:**
- Patterns discovered ("this codebase uses X for Y")
- Gotchas encountered ("don't forget to update Z when changing W")
- Useful context ("the evaluation panel is in component X")
- Build/test commands that worked
- Environment-specific requirements

**Bad learnings (do not include):**
- Story-specific implementation details
- Temporary debugging notes
- Information already in progress.txt (no duplicates)

### Thread URLs (Amp)

When using Amp, each iteration's progress entry includes a thread URL:

```markdown
Thread: https://ampcode.com/threads/$AMP_CURRENT_THREAD_ID
```

This allows future iterations to use the `read_thread` tool to reference previous work if needed, providing access to the full conversation history of a specific iteration.

## AGENTS.md / CLAUDE.md Updates

Beyond progress.txt, Ralph updates project-level documentation files (AGENTS.md for Amp, CLAUDE.md for Claude Code) with reusable knowledge.

### When to Update

Before committing, Ralph checks if any edited files have learnings worth preserving in nearby documentation files:

1. **Identify directories with edited files** — Look at which directories were modified
2. **Check for existing documentation** — Look for AGENTS.md/CLAUDE.md in those directories or parent directories
3. **Add valuable learnings** — If something was discovered that future developers/agents should know

### Good Documentation Additions

- "When modifying X, also update Y to keep them in sync"
- "This module uses pattern Z for all API calls"
- "Tests require the dev server running on PORT 3000"
- "Field names must match the template exactly"
- "Build command: `cargo build --release` (takes ~2 minutes)"

### Bad Documentation Additions

- Story-specific implementation details
- Temporary debugging notes
- Information already in progress.txt

Only update documentation if there is **genuinely reusable knowledge** that would help future work in that directory.

### Why This Matters

AGENTS.md and CLAUDE.md files are automatically read by AI coding tools when they open a project. By updating these files, Ralph ensures that:

1. Future Ralph iterations benefit from discovered patterns
2. Human developers who later work on the codebase have context
3. New AI sessions (not part of Ralph) can understand the codebase

This creates a compounding knowledge effect — each iteration makes future iterations more effective.

## prd.json as State Machine

`prd.json` serves as Ralph's state machine. It tracks which stories are done and which remain:

```json
{
  "userStories": [
    { "id": "US-001", "passes": true },   // Done
    { "id": "US-002", "passes": true },   // Done
    { "id": "US-003", "passes": false },  // Next to implement
    { "id": "US-004", "passes": false }   // Pending
  ]
}
```

### State Transitions

Each iteration performs one state transition: `passes: false` → `passes: true` for exactly one story. The loop continues until all stories are `true`.

### Priority Ordering

Stories with lower `priority` values are implemented first. This ensures dependency ordering: database changes before backend logic, backend logic before UI components.

## Memory Compounding Effect

The memory system creates a compounding effect across iterations:

- **Iteration 1**: Ralph discovers the project uses Prisma for ORM. Records in progress.txt and AGENTS.md.
- **Iteration 2**: Ralph reads progress.txt, knows to use Prisma patterns. Discovers Tailwind is used for styling. Records this too.
- **Iteration 3**: Ralph reads both learnings, applies Prisma + Tailwind patterns correctly from the start.
- **Iteration 10**: By story 10, Ralph knows the project's patterns well enough to implement features with minimal errors.

This is why Ralph gets better over time — not because the model changes, but because its external memory grows richer and more specific to the codebase.

## Archiving and Memory Preservation

When starting a new feature (different `branchName`), Ralph archives previous runs:

```
archive/
└── 2024-01-15-task-priority/
    ├── prd.json        # Previous feature's task list
    └── progress.txt    # Previous feature's learnings
```

This preserves the memory of completed features while giving new features a clean progress.txt. The archived learnings are available for reference if needed.

## Memory Limitations and Workarounds

### Context Window Limits

Even with external memory, Ralph is limited by context windows. The prompt template, prd.json, and progress.txt all consume context space. As progress.txt grows, it may exceed practical context limits.

**Workaround**: The Codebase Patterns section at the top of progress.txt provides a condensed summary. Ralph reads this first and can skip older entries if context is tight.

### Git History Depth

For very long runs, git history becomes extensive. Ralph may not be able to read all commits within its context window.

**Workaround**: Recent commits are most relevant. Ralph focuses on the last few iterations' changes and uses progress.txt for broader context.

### Lost Context Between Tool Restarts

Since each iteration is a fresh process, Ralph cannot use in-memory caches or temporary state.

**Workaround**: Everything must be persisted to disk. If Ralph needs to remember something, it writes it to progress.txt, prd.json, or an AGENTS.md file.

## Design Philosophy

The memory system follows these principles:

1. **Explicit over implicit** — Memory is stored in plain text files, not hidden state
2. **Append-only where possible** — progress.txt never loses information
3. **Progressive disclosure** — Codebase Patterns at the top, detailed history below
4. **Human-readable** — All memory files are readable by humans for debugging and auditing
5. **Tool-agnostic** — Memory works the same regardless of which AI tool Ralph uses

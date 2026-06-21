# Core Concepts

## Rules

1. **Always use `plan.sh` — never write or edit PLAN.md directly.** The LLM should not generate PLAN.md content itself. All operations (create, add, update, remove, status changes) go through `plan.sh` commands. Scripts enforce status transitions, auto-derive emojis, detect dependency cycles, and maintain integrity via checksums. Direct edits bypass all safeguards and corrupt the plan.
2. **Smaller models especially must not hallucinate PLAN.md content.** When unsure of a command, read the Usage section or run `plan.sh --help`. Do not guess the file format.
3. **There can be multiple `PLAN.md` files** in different locations, forming a DAG via `Depends On` headers.
4. **Status emojis are derived automatically** by the script after every mutation. Prefer relying on auto-derivation. `set-plan-status` and `set-phase-status` exist for manual override (e.g., marking a plan as ❓ when scope is unclear), but `check --fix` will re-derive them from actual task states.

## File Format (for understanding only)

The structure below describes what `plan.sh` produces. Do not write it yourself.

- Title: `# [emoji] Plan ➖ Title`
- Header fields: `Depends On`, `Created`, `Updated`, `Current Phase`, `Current Task`
- Phases: `## [emoji] Phase N ➖ Title` with numbered tasks underneath
- Tasks: `- [emoji] Task X.Y ➖ Title ⚓ ...` (dependencies optional)
- Checksum comment at bottom for integrity verification

## When to Use

Use this skill when:
- Starting a project that requires structured phase-by-phase execution
- Tackling complex tasks with multiple dependent steps (implementation, testing, deployment)
- Coordinating work across multiple `PLAN.md` files with inter-plan dependencies
- Resuming interrupted work by tracking current phase and task state
- Validating plan consistency — run `plan.sh check PLAN.md --fix` to detect and repair issues
- Any workflow needing a single source of truth for progress

# Subagents, Worktrees & Checkpoints

## Subagents

The `use_subagents` tool enables the main agent to spawn parallel subagent instances for independent tasks. This is controlled by the `SubagentToolHandler` (`src/core/task/tools/handlers/SubagentToolHandler.ts`).

### How It Works

1. The LLM proposes up to 5 parallel prompts (`prompt_1` through `prompt_5`)
2. Each prompt spawns an independent Dirac agent instance
3. Subagents run in isolation with their own context and tool access
4. Results are aggregated and returned to the parent agent

### Configuration

- `subagentsEnabled` — Global setting to enable/disable subagent functionality
- `AgentConfigLoader` — Resolves configured subagent names for dynamic tool registration
- `SubagentRunner` — Manages the lifecycle of spawned subagent processes
- Subagents cannot spawn nested subagents (prevents infinite recursion)

### Parameters

- `timeout` — Maximum execution time per subagent (default: 300 seconds)
- `max_turns` — Maximum LLM turns per subagent
- `include_history` — Whether to include parent conversation history in subagent context

## Worktrees

Dirac supports **git worktrees** for isolated editing environments. This prevents interference with uncommitted changes in the main working directory.

### Worktree Operations

Implemented in `src/core/controller/worktree/`:

- `createWorktree.ts` — Create a new git worktree on a specific branch
- `switchWorktree.ts` — Switch between worktrees
- `mergeWorktree.ts` — Merge worktree changes back to the main branch
- `deleteWorktree.ts` — Clean up worktrees
- `listWorktrees.ts` — List available worktrees
- `checkoutBranch.ts` — Checkout a specific branch in a worktree
- `getAvailableBranches.ts` — List branches available for worktree creation
- `trackWorktreeViewOpened.ts` — UI state tracking

### Use Cases

- **Safe experimentation**: Test refactoring in an isolated branch without affecting the main working directory
- **Parallel tasks**: Run different tasks on different branches simultaneously
- **Rollback safety**: If a task goes wrong, simply discard the worktree

## Checkpoints

The checkpoint system (`src/integrations/checkpoints/`) provides git-based snapshots for safe editing with rollback capability.

### CheckpointTracker

The `CheckpointTracker` class manages:

1. **Automatic snapshots**: Git commits created at key points during task execution
2. **Diff tracking**: Compare current state against any checkpoint
3. **Multi-root support**: `MultiRootCheckpointManager` handles monorepo workspaces
4. **Lock management**: `CheckpointLockUtils` prevents concurrent checkpoint operations

### Checkpoint Lifecycle

1. Task starts → Initial checkpoint created
2. Before each tool execution → Pre-tool checkpoint (for read-only tools, parallel with initial commit)
3. After task completion → Completion checkpoint
4. User can view diffs between any two checkpoints via `showChangedFilesDiff()`

### Diff Operations

The `multifile-diff.ts` module provides:

- **Changes since snapshot**: Compare current state against the last checkpoint
- **New changes since last task completion**: Show incremental changes between task completions
- Uses `checkpointTracker.getDiffSet(hash1, hash2)` to compute file-level diffs

### Checkpoint Exclusions

`CheckpointExclusions.ts` defines files and patterns that should not be included in checkpoints (e.g., lock files, generated artifacts).

## Integration

These three systems work together:

- **Subagents** handle parallel independent tasks
- **Worktrees** provide isolated filesystem environments for each task
- **Checkpoints** provide rollback safety within each worktree

This combination allows Dirac to perform complex multi-file refactoring across large codebases with full auditability and rollback capability.

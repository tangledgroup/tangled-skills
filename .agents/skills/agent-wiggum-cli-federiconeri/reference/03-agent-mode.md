# Agent Mode & Backlog Automation

## Overview

Agent mode (`wiggum agent`) is the most autonomous feature of Wiggum. It reads your GitHub backlog, prioritizes issues, generates implementation specs, runs full Ralph loops, reviews diffs, and auto-merges PRs — then moves to the next issue. Zero human intervention required.

```
GitHub Issues → Prioritize → Assess State → Generate Spec →
  Run Ralph Loop → Review Diff vs Spec → Auto-Merge → Next Issue
```

## How It Works

### Issue Prioritization

Agent mode reads open issues from your GitHub repository and prioritizes them by label:

- **P0** — Critical, process first
- **P1** — High priority
- **P2** — Normal priority

Issues without priority labels are processed after labeled ones. You can filter with `--labels` to only process specific categories, or `--issues` to target specific issue numbers.

### Dependency Ordering

Agent mode respects dependency relationships between issues. If issue #42 depends on issue #38, it processes #38 first. This prevents implementing features that rely on unfinished foundations.

### Feature State Assessment

Before running a loop, agent mode assesses the current state of each feature:

- **Fresh start** — No existing branch or work; generate spec and begin
- **Resume** — Partial branch exists; continue from where it left off
- **Already shipped** — Branch merged or feature complete; skip

This prevents wasted effort on already-completed work and enables crash recovery for interrupted loops.

### Spec Generation from Issue Context

Agent mode pulls full issue context (title, body, labels) and uses it as input for spec generation. This is equivalent to running `wiggum new --issue #42` but fully automated. The generated spec includes tasks, test plans, and architectural decisions grounded in your codebase.

### Full Ralph Loop Execution

For each issue, agent mode runs the complete Ralph loop: plan → implement → test → verify → PR. Each phase has its own checkpoints and error handling. If a phase fails, it retries at that phase level rather than restarting the entire feature.

### Diff Review Against Spec

After the Ralph loop completes, agent mode reviews the generated diff against the original spec. It checks that every requirement was met and no unintended changes were introduced. Only when all checks pass does it proceed to merge.

### Auto-Merge

When review passes and all CI checks are green, agent mode auto-merges the PR. Then it moves to the next issue in the queue. This continues until `--max-items` is reached or the backlog is exhausted.

## Running Agent Mode

### Interactive

```bash
wiggum agent
```

Opens the agent loop monitor TUI showing issue progress, current phase, and token usage.

### Headless (CI)

```bash
wiggum agent --stream --max-items 5
```

Streams output without waiting for final response. Suitable for CI pipelines where you want to process a bounded number of issues per run.

### Dry Run

```bash
wiggum agent --dry-run
```

Plans all actions without executing anything. Shows which issues would be processed, in what order, and what specs would be generated. Useful for reviewing the automation plan before committing.

### Targeted Execution

```bash
# Only process P1 bugs
wiggum agent --labels bug,P1

# Process specific issues
wiggum agent --issues 42,57,89

# Limit to 3 items
wiggum agent --max-items 3
```

## Memory and Learning

Agent mode stores memory across iterations. Outcomes from previous loops (what worked, what didn't) are recorded in `.ralph/LEARNINGS.md`. This means the system improves over time — it learns which patterns produce good results and adjusts future specs accordingly.

## GitHub Issue Integration

Beyond agent mode, Wiggum provides several ways to integrate with GitHub issues:

### TUI Issue Picker

Run `/issue` in the Wiggum TUI to browse your GitHub issues in a navigable table picker with columns for issue number, title, state, and labels. Select an issue and Wiggum takes you straight into the AI interview with full issue context pre-loaded.

### CLI Issue Flag

Pass `--issue #42` directly to `wiggum new` to include issue context in spec generation:

```bash
wiggum new feature-name --issue #42 --issue #57
```

Multiple issues can be referenced (flag is repeatable).

### GitHub CLI Dependency

Agent mode and `/issue` require the GitHub CLI (`gh`) to be installed and authenticated. Run `wiggum agent --diagnose-gh` to check connectivity.

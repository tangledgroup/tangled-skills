# Scaling Case Study: Anthropic's C Compiler

## Overview

Anthropic published a [case study](https://www.anthropic.com/engineering/building-c-compiler) about building a C compiler with a team of parallel Claude agents. It's the best public example of what harness engineering looks like at scale.

## Architecture

The architecture was simple: each Docker container mounted a shared bare git repo at `/upstream`, cloned a local workspace, and coordinated through lock files in `current_tasks/` — pick a task by creating a lock file, do the work, pull, merge, push, remove the lock. Simple git-based synchronization enabled parallelization without complex orchestration.

```bash
#!/bin/bash
while true; do
    COMMIT=$(git rev-parse --short=6 HEAD)
    LOGFILE="agent_logs/agent_${COMMIT}.log"
    claude --dangerously-skip-permissions \
           -p "$(cat AGENT_PROMPT.md)" \
           --model claude-opus-4-6-20260131 &> "$LOGFILE"
done
```

## Lessons Learned About Harness Design

### Continuous Task Loops Beat Interactive Sessions

The agent needs to immediately pick up the next task without waiting for human input. The `while true` loop is essential — the agent should never idle.

### High-Quality Test Harnesses Are Critical

The tests define what the agent solves. Tests should print minimal output and log details to files — context window rotting is a real problem. They added `--fast` modes that run deterministic subsamples so agents don't spend hours on full test runs.

### Extensive READMEs and Progress Files Are Essential

Each fresh container starts with zero context. The agent needs to know what's been done, what remains, and how to proceed — all from files it can read.

### Parallelization Works Best with Independent Tasks

Parallelization worked great with independent failing tests, but monolithic tasks caused all agents to hit the same bugs. The solution was to use GCC as a known-good oracle to narrow the failure-inducing file subsets, letting different agents make progress on different bugs.

### Agent Specialization

They used agent specialization — dedicated agents for code consolidation, performance optimization, documentation, and design critique. Different agents with different prompts and responsibilities.

## Hard Limits

**Code quality degrades as complexity grows.** New features frequently broke existing functionality even with CI. Generated code efficiency was poor (worse than `gcc -O0`).

**Cost vs quality.** The total cost was just under $20k for roughly 100k lines, which is cost-effective vs. human teams, but passing tests still doesn't guarantee quality without human verification.

## Key Takeaway

OpenAI puts the lesson well in its [harness engineering post](https://openai.com/index/harness-engineering/):

> "When something failed, the fix was almost never 'try harder.' Human engineers always stepped into the task and asked: 'what capability is missing, and how do we make it both legible and enforceable for the agent?'"

The bottleneck shifts from "can the model code?" to "can we run it reliably, cheaply, and at scale?" Building software still demands discipline — it just shows up more in the scaffolding than in the code.

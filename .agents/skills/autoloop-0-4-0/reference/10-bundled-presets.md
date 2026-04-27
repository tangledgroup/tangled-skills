# Bundled Preset Family

Autoloop ships a family of `auto*` preset workflows. Each one is a self-contained agentic loop with a distinct behavioral center, topology, and shared-state contract.

Across the family, the intended posture is **fail-closed** rather than rubber-stamp: verifier, checker, judge, reporter, and final-gate roles should prefer explicit evidence, surface uncertainty, and reject weak proof instead of quietly approving work.

## Preset Catalog

### autocode — Code Implementation Loop

Plan, build, review, and commit code changes. Takes a task description, breaks it into slices, builds each slice, reviews, and gates completion. The critic is expected to independently smoke-test the builder's changed code path whenever a practical executable surface exists.

- **Shape:** planner → builder → critic → finalizer
- **Shared state:** `.autoloop/context.md`, `.autoloop/plan.md`, `.autoloop/progress.md`, `.autoloop/logs/`
- **Required event:** `review.passed`

### autospec — Specification Loop

Turn a rough idea into a durable RFC + `.code-task.md` pair. Clarifies scope first, inspects repo conventions and adjacent code/docs, drafts the design doc, drafts the implementation task, and adversarially checks that the pair is aligned and executable.

- **Shape:** clarifier → researcher → designer → planner → critic
- **Shared state:** `.autoloop/spec-brief.md`, `.autoloop/spec-research.md`, `.autoloop/progress.md`
- **Required events:** `research.ready`, `design.ready`, `spec.ready`

### autosimplify — Post-Implementation Cleanup

Focus on recently modified code, identify safe opportunities to improve reuse, clarity, and obvious efficiency, apply behavior-preserving simplifications, and independently verify that the result is actually cleaner.

- **Shape:** scoper → reviewer → simplifier → verifier
- **Shared state:** `.autoloop/simplify-context.md`, `.autoloop/simplify-plan.md`, `.autoloop/progress.md`
- **Required event:** `simplification.verified`

### autoideas — Repository Survey and Improvement Report

Scan a target repo for areas worth improving, deep-dives each area, validates suggestion quality, and compiles an actionable report.

- **Shape:** scanner → analyst → reviewer → synthesizer
- **Shared state:** `.autoloop/scan-areas.md`, `.autoloop/progress.md`, `.autoloop/ideas-report.md`
- **Required event:** `analysis.validated`

### autoresearch — Autonomous Experiment Loop

Hypothesize, implement, measure, keep or discard. Supports LLM-as-judge for semantic evaluation when hard metrics are insufficient.

- **Shape:** strategist → implementer → benchmarker → evaluator
- **Shared state:** `.autoloop/autoresearch.md`, `.autoloop/experiments.jsonl`, `.autoloop/progress.md`
- **Required event:** `experiment.measured`

### autoqa — Native Validation Orchestration

Inspect the target repo, infer its domain, select the idiomatic validation surface, write a validation plan, and execute it — all without installing external test frameworks. Uses native/manual validation surfaces that already exist in the repo (build system, type checker, linter, REPL, CLI invocation, existing test suite).

- **Shape:** inspector → planner → executor → reporter
- **Shared state:** `.autoloop/qa-plan.md`, `.autoloop/qa-report.md`, `.autoloop/progress.md`
- **Required event:** `surfaces.identified`

### autotest — Formal Test Creation

Survey the codebase for coverage gaps, write new tests using the repo's existing framework and conventions, run them, and assess quality improvement. Distinct from autoqa: autotest writes new formal tests; autoqa validates what exists.

- **Shape:** surveyor → writer → runner → assessor
- **Shared state:** `.autoloop/test-plan.md`, `.autoloop/test-report.md`, `.autoloop/progress.md`
- **Required event:** `tests.passed`

### autofix — Bug Diagnosis and Repair

Narrower than autocode — starts from a bug report or failing test rather than a feature request. Reproduces the issue, traces the root cause, implements a minimal fix, and verifies with regression checks.

- **Shape:** diagnoser → fixer → verifier → closer
- **Shared state:** `.autoloop/bug-report.md`, `.autoloop/fix-log.md`, `.autoloop/progress.md`
- **Required event:** `fix.verified`

### autoreview — Code Review Loop

Read a PR diff or set of changes, check for correctness, security, style, performance, and maintainability issues, propose concrete fixes, and produce structured review feedback with a clear verdict.

- **Shape:** reader → checker → suggester → summarizer
- **Shared state:** `.autoloop/review-context.md`, `.autoloop/review-findings.md`, `.autoloop/progress.md`
- **Required event:** `review.checked`

### autodoc — Documentation Generation and Maintenance

Audit existing docs against the codebase, identify gaps and staleness, write or update documentation, and adversarially verify accuracy against the actual code before publishing.

- **Shape:** auditor → writer → checker → publisher
- **Shared state:** `.autoloop/doc-plan.md`, `.autoloop/doc-report.md`, `.autoloop/progress.md`
- **Required event:** `doc.checked`

### autosec — Security Audit and Hardening

Scan for OWASP top-10 vulnerabilities, dependency issues, secret leaks, and configuration weaknesses. Each finding is confirmed or dismissed with evidence, then fixed with standard security patterns.

- **Shape:** scanner → analyst → hardener → reporter
- **Shared state:** `.autoloop/sec-findings.md`, `.autoloop/sec-report.md`, `.autoloop/progress.md`
- **Required event:** `findings.reported`

### autoperf — Performance Profiling and Optimization

Identify hot paths, establish baselines, implement targeted optimizations, measure results, and keep or discard changes — similar to autoresearch but scoped to performance.

- **Shape:** profiler → optimizer → measurer → judge
- **Shared state:** `.autoloop/perf-profile.md`, `.autoloop/perf-log.jsonl`, `.autoloop/progress.md`
- **Required event:** `perf.measured`

### automerge — Worktree Merge

Merge a completed worktree branch back into its base branch. Planning category (read-only from the perspective of the main checkout).

### autopr — Pull Request Generation

Turn the current branch into a reviewable pull request.

## Naming Guidance

- `autoimprove` is an umbrella concept, not a preset. It describes composing `autoideas` → `autocode`: survey a repo for improvements, then implement them.
- `autoresearch` stays — it is the only experiment/hypothesis loop in the family
- All presets use the `auto` prefix followed by a single lowercase word that describes the behavioral center

## Choosing a Preset

- Turn a rough idea into an RFC + implementation task → `autospec`
- Implement a feature or task → `autocode`
- Clean up a recent diff without changing behavior → `autosimplify`
- Survey a repo for improvement ideas → `autoideas`
- Run experiments and measure results → `autoresearch`
- Validate that things work without writing new tests → `autoqa`
- Write or improve formal tests → `autotest`
- Fix a specific bug → `autofix`
- Review code changes → `autoreview`
- Generate or update documentation → `autodoc`
- Audit for security issues → `autosec`
- Profile and optimize performance → `autoperf`

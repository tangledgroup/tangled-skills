# Prompt Engineering

## The Prompt Template

Ralph uses a prompt template (`prompt.md` for Amp, `CLAUDE.md` for Claude Code) that is piped into the AI tool on every iteration. This template defines what the agent should do during its single iteration.

The prompt is not static — it evolves through observation and tuning. There is no "perfect prompt." The prompt adapts to your codebase, your failure modes, and your project's specific needs.

## Default Prompt Structure

Both `prompt.md` and `CLAUDE.md` follow the same structure with minor tool-specific differences:

### Section 1: Task Definition

```markdown
# Ralph Agent Instructions

You are an autonomous coding agent working on a software project.

## Your Task

1. Read the PRD at `prd.json` (in the same directory as this file)
2. Read the progress log at `progress.txt` (check Codebase Patterns section first)
3. Check you're on the correct branch from PRD `branchName`. If not, check it out or create from main.
4. Pick the **highest priority** user story where `passes: false`
5. Implement that single user story
6. Run quality checks (e.g., typecheck, lint, test)
7. Update AGENTS.md/CLAUDE.md files if you discover reusable patterns
8. If checks pass, commit ALL changes with message: `feat: [Story ID] - [Story Title]`
9. Update the PRD to set `passes: true` for the completed story
10. Append your progress to `progress.txt`
```

### Section 2: Progress Report Format

```markdown
## Progress Report Format

APPEND to progress.txt (never replace, always append):
```

The format specifies exactly how learnings should be recorded, including a thread URL reference (for Amp) so future iterations can use the `read_thread` tool.

### Section 3: Pattern Consolidation

```markdown
## Consolidate Patterns

If you discover a **reusable pattern** that future iterations should know, add it to the `## Codebase Patterns` section at the TOP of progress.txt.
```

This creates a living knowledge base that grows with each iteration.

### Section 4: AGENTS.md/CLAUDE.md Updates

```markdown
## Update AGENTS.md Files

Before committing, check if any edited files have learnings worth preserving in nearby AGENTS.md files.
```

Instructions for identifying directories with edited files, checking for existing documentation, and adding valuable learnings.

### Section 5: Quality Requirements

```markdown
## Quality Requirements

- ALL commits must pass your project's quality checks (typecheck, lint, test)
- Do NOT commit broken code
- Keep changes focused and minimal
- Follow existing code patterns
```

### Section 6: Browser Testing

```markdown
## Browser Testing (Required for Frontend Stories)

For any story that changes UI, you MUST verify it works in the browser.
```

### Section 7: Stop Condition

```markdown
## Stop Condition

After completing a user story, check if ALL stories have `passes: true`.

If ALL stories are complete and passing, reply with:
<promise>COMPLETE</promise>

If there are still stories with `passes: false`, end your response normally.
```

## Customizing the Prompt

After copying the prompt template to your project, customize it:

- Add project-specific quality check commands
- Include codebase conventions
- Add common gotchas for your stack
- Specify testing frameworks and commands

### Tool-Specific Differences

**prompt.md (Amp)**: References AGENTS.md, includes thread URL in progress format, requires browser verification.

**CLAUDE.md (Claude Code)**: References CLAUDE.md instead of AGENTS.md, omits thread URL (no Amp threads), browser testing is conditional ("if available").

## Signposting: The Core Tuning Mechanism

Signposting is the primary method for tuning Ralph. It involves adding explicit instructions ("signs") to the prompt that address observed failure patterns.

### The Signposting Process

1. **Observe**: Run Ralph and watch its behavior
2. **Identify**: Find patterns of bad behavior or mistakes
3. **Add a sign**: Insert an explicit instruction in the prompt
4. **Repeat**: Run more loops and observe improvement

### Common Signs

**Preventing placeholder implementations:**
```markdown
DO NOT IMPLEMENT PLACEHOLDER OR SIMPLE IMPLEMENTATIONS. WE WANT FULL IMPLEMENTATIONS.
```

**Preventing incorrect assumptions about existing code:**
```markdown
Before making changes search codebase (don't assume not implemented) using subagents. Think hard.
```

**Enforcing test documentation:**
```markdown
When authoring documentation, capture the why — explain what tests are trying to verify and why the backing implementation is important.
```

**Preventing context window waste:**
```markdown
Only add patterns that are general and reusable, not story-specific details.
```

### When Signs Work

Signs work because LLMs attend to explicit, prominently placed instructions. By adding signs that directly address failure modes, you steer the model away from its default behaviors (minimal implementations, assumptions, vague documentation).

Do not be dismayed if Ralph initially ignores a sign. The models have been trained to chase their reward function, and the reward function often favors compiling code over correctness. You may need multiple iterations for Ralph to internalize a new constraint.

## Geoffrey Huntley's Advanced Prompt Patterns

For complex projects (like building a compiler), the prompt evolves into a multi-layered instruction set:

### The Numbered Priority System

Geoffrey uses numbered sections with increasing numbers to create priority ordering:

```markdown
0a. study specs/* to learn about the compiler specifications
0b. The source code of the compiler is in src/
0c. study fix_plan.md.

1. Your task is to implement missing stdlib...
2. After implementing functionality, run tests...
3. When the tests pass, update fix_plan.md and commit...

999. Important: When authoring documentation, capture the why...
9999. Important: We want single sources of truth...
999999. As soon as there are no build or test errors, create a git tag.
```

The increasing numbers serve as emphasis markers — higher numbers indicate more critical, non-negotiable instructions.

### The Anti-Placeholder Directive

```markdown
9999999999999999999999999999. DO NOT IMPLEMENT PLACEHOLDER OR SIMPLE IMPLEMENTATIONS.
WE WANT FULL IMPLEMENTATIONS. DO IT OR I WILL YELL AT YOU
```

This extreme directive addresses Claude's inherent bias toward minimal and placeholder implementations. The夸张 language is intentional — it signals maximum importance to the model.

### The Self-Improvement Loop

```markdown
When you learn something new about how to run the compiler or examples, make sure you update AGENT.md using a subagent but keep it brief.
```

This instruction enables Ralph to improve its own documentation over time, creating a self-reinforcing learning loop.

### Bug Resolution Mandate

```markdown
For any bugs you notice, it's important to resolve them or document them in fix_plan.md to be resolved using a subagent even if it is unrelated to the current piece of work.
```

This prevents Ralph from ignoring discovered bugs — they must either be fixed or tracked.

## Prompt Evolution Through Observation

The prompt is not designed once and forgotten. It evolves through a continuous feedback loop:

1. Run Ralph on your project
2. Watch the stream of output
3. Identify patterns where Ralph makes mistakes
4. Add explicit instructions to address those patterns
5. Run more loops
6. Observe improvement or identify new failure modes
7. Repeat

### What to Watch For

- **Placeholder implementations**: Ralph creates stub functions instead of real logic
- **Assumption errors**: Ralph assumes code doesn't exist when it does (or vice versa)
- **Scope creep**: Ralph tries to do more than one story per iteration
- **Missing tests**: Ralph implements features without corresponding tests
- **Documentation gaps**: Ralph doesn't record learnings in progress.txt
- **Broken commits**: Ralph commits code that fails quality checks

### Tuning Strategy

Start with the default prompt. Add signs only when you observe specific failure patterns. Don't preemptively add instructions for problems that haven't occurred — each instruction consumes context window space and may dilute the impact of other instructions.

## Planning vs. Building Prompts

For large projects, Geoffrey uses separate prompts for planning and building:

### Planning Prompt

```markdown
study specs/* to learn about the compiler specifications and fix_plan.md to understand plan so far.

First task is to study existing source code and compare it against the compiler specifications.
From that create/update a fix_plan.md which is a bullet point list sorted in priority of items yet to be implemented.
```

### Building Prompt

```markdown
Your task is to implement missing stdlib and compiler functionality.
Follow the fix_plan.md and choose the most important thing.
```

This separation allows Ralph to first understand the full scope before starting implementation, preventing wasted effort on already-implemented features.

## Key Principles

1. **Be explicit** — Don't assume Ralph knows your codebase conventions
2. **Add signs surgically** — Only add instructions for observed failure patterns
3. **Trust the process** — Ralph needs multiple iterations to internalize new constraints
4. **Keep it focused** — One thing per loop, always
5. **Document everything** — progress.txt and AGENTS.md are Ralph's memory
6. **Verify, don't assume** — Always include quality checks and browser verification
7. **Evolve the prompt** — There is no perfect prompt, only continuously improved ones

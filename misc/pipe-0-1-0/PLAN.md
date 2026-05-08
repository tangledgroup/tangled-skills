# ☑ Plan: pipe - Unix Pipe Meta-Skill for LLMs

**Depends On:** NONE
**Created:** 2026-05-08T12:00:00Z
**Updated:** 2026-05-08T12:30:00Z
**Current Phase:** ☐ Phase 1 Research & Analysis
**Current Task:** ☐ Task 1.1 Study existing skills for pipe-compatible patterns

## ☑ Phase 1 Research & Analysis

- ☑ Task 1.1 Study existing skills for pipe-compatible patterns
  - Study `scrapling-0-4-7` and `duckduckgo-2026-05-08` as example stages
  - Identify how skills produce output that could be consumed by another skill
  - Map out data flow: skill invocation → output capture → injection into next stage

- ☑ Task 1.2 Study agent-agnostic skill patterns (depends on: Task 1.1)
  - Review `sman` skill for cross-platform skill conventions (pi, opencode, Claude Code, Codex)
  - Understand how skills instruct agents behaviorally without platform-specific code
  - Study `plan` skill as a meta-skill reference for instruction-only patterns

- ☑ Task 1.3 Define pipe semantics and grammar (depends on: Task 1.1 , Task 1.2)
  - Formalize the `| stage1 | stage2 | stage3` syntax
  - Define what a "stage" is: skill invocation, tool call, MCP tool, user request, or raw instruction
  - Determine how `|` separates stages and how output flows between them
  - Decide on error handling semantics (fail-fast vs continue-with-empty)

## ☑ Phase 2 Design & Specification

- ☑ Task 2.1 Design the pipe execution model (depends on: Task 1.3)
  - Sequential execution: each stage runs to completion before next begins
  - Output of stage N becomes context/prompt for stage N+1
  - Define how output is captured (tool result, bash stdout, LLM response, skill output)
  - Design the "pipe buffer" — how much context passes between stages (full output, truncated, summarized)

- ☑ Task 2.2 Design stage resolution logic (depends on: Task 1.3 , Task 2.1)
  - How the agent resolves a stage: skill name match, tool name, MCP tool, or raw instruction
  - If stage references a known skill → load that skill's context + user's instruction
  - If stage references a tool → invoke tool with piped input as argument
  - If stage is a bare string → treat as direct instruction/prompt
  - Fallback behavior for unresolvable stages

- ☑ Task 2.3 Design cross-platform compatibility (depends on: Task 1.2 , Task 2.1)
  - Ensure instructions work on any agent that loads SKILL.md (no platform-specific commands)
  - Avoid references to pi-only features (extensions, registerCommand, TUI)
  - Use universal concepts: skills, tools, bash, user input
  - Define how the skill instructs the agent to behave, not how to implement programmatically

- ☑ Task 2.4 Define error handling and output conventions (depends on: Task 2.1)
  - Per-stage error reporting with stage number and name
  - Fail-fast mode as default
  - How to display intermediate results vs final output
  - Pipe buffer size limits and truncation rules

## ☑ Phase 3 Implementation — Core Skill (SKILL.md)

- ☑ Task 3.1 Write SKILL.md YAML header and Overview (depends on: Task 2.4)
  - name: `pipe-0-1-0`
  - description with WHAT + WHEN formula (agent-agnostic, no platform references)
  - tags, category, version fields

- ☑ Task 3.2 Write When to Use section of SKILL.md (depends on: Task 3.1)
  - Specific scenarios where pipe composition is valuable
  - Contrast with normal sequential prompting
  - Examples of when NOT to use pipes

- ☑ Task 3.3 Write Core Concepts section of SKILL.md (depends on: Task 2.4 , Task 3.2)
  - Define pipe grammar and syntax rules
  - Explain stage types: skill-ref, tool-invocation, mcp-tool, raw-instruction
  - Explain output flow between stages
  - Explain the pipe buffer concept

- ☑ Task 3.4 Write Usage Examples section of SKILL.md (depends on: Task 3.3)
  - Example: `| duckduckgo search for tangled group | scrapling get first result`
  - Example: Multi-stage with raw instructions mixed in
  - Example: Using tools as pipe stages (bash, read)
  - Example: Error case showing fail-fast behavior

## ☑ Phase 4 Implementation — Reference Files

- ☑ Task 4.1 Create reference/01-pipe-semantics.md (depends on: Task 3.4)
  - Detailed grammar specification for `|` syntax
  - Stage resolution algorithm step by step
  - Output capture and injection mechanics
  - Pipe buffer rules (size limits, truncation, summarization triggers)

- ☑ Task 4.2 Create reference/02-stage-patterns.md (depends on: Task 3.4)
  - Common stage composition patterns (search→scrape→summarize, extract→transform→load)
  - Anti-patterns to avoid (too many stages, unbounded output, circular deps)
  - Performance considerations and token budgeting
  - Stage-specific tips (when to use skill vs tool vs raw instruction)

- ☑ Task 4.3 Create reference/03-error-handling.md (depends on: Task 3.4)
  - Fail-fast semantics and when to override
  - Error recovery patterns (retry, skip, substitute)
  - Debugging multi-stage pipes (identifying which stage failed)
  - Partial output handling when pipe breaks mid-chain

## ☑ Phase 5 Validation & Polish

- ☑ Task 5.1 Run structural validator against SKILL.md (depends on: Task 4.3)
  - `bash scripts/validate-skill.sh .agents/skills/pipe-0-1-0`
  - Fix any YAML header, naming, or structure issues

- ☑ Task 5.2 LLM judgment review of content (depends on: Task 5.1)
  - Check description follows WHAT + WHEN formula
  - Verify no platform-specific references (no pi extensions, no TypeScript)
  - Confirm agent-agnostic language throughout
  - Verify consistent terminology
  - Check examples are copy-pasteable and correct

- ☑ Task 5.3 Regenerate README.md skills table (depends on: Task 5.2)
  - `bash scripts/gen-skills-table.sh`

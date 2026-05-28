# ☐ Plan: Create "add-two-numbers" Skill

**Depends On:** NONE

**Created:** 2026-05-26T00:00:00Z

**Updated:** 2026-05-26T00:00:00Z

**Current Phase:** ☐ Phase 1

**Current Task:** ☐ Task 1.1

## ☐ Phase 1 Analyze Requirements

- ☐ Task 1.1 Clarify scope and approach for "add two random numbers" skill
  - Determine target platforms (pi, opencode, Claude Code, etc.)
  - Decide whether to use Python inline, bash `$RANDOM`, or another language
  - Determine if skill needs scripts/assets or is markdown-only

## ☐ Phase 2 Design Skill Structure

- ☐ Task 2.1 Choose output structure (simple vs complex) and draft SKILL.md outline
  - (depends on: Task 1.1)
  - Simple skill likely sufficient — single cohesive topic
  - Draft YAML header fields (name, description, tags, category)

## ☐ Phase 3 Write SKILL.md

- ☐ Task 3.1 Write the SKILL.md file
  - (depends on: Task 2.1)
  - Include YAML header with proper metadata
  - Overview section explaining what the skill does
  - "When to Use" section with specific scenarios
  - Core Concepts or Usage Examples as appropriate

## ☐ Phase 4 Validate and Report

- ☐ Task 4.1 Run structural validator against the skill
  - (depends on: Task 3.1)
  - `bash .agents/skills/skman/scripts/validate-skill.sh .agents/skills/add-two-numbers`
- ☐ Task 4.2 Regenerate README.md skills table
  - (depends on: Task 4.1)
  - `bash .agents/skills/skman/scripts/gen-skills-table.sh`

# ☑ Plan: Create vega-embed 7.1.0 Skill

**Depends On:** NONE

**Created:** 2026-06-02T00:00:00Z

**Updated:** 2026-06-02T00:00:00Z

<!-- [emoji-of-phase] Phase X Phase Title -->
**Current Phase:** ☑ Phase 4

<!-- [emoji-of-phase] Phase X - [emoji-of-task] Task X.Y -->
**Current Task:** ☑ Task 4.3

## Phases and Tasks

## ☑ Phase 1 Planning

- ☑ Task 1.1 Analyze sources and determine skill structure (simple vs complex)
  - Review npm page, GitHub README, source code (embed.ts, types.ts, container.ts, index.ts), CHANGELOG
  - Identify distinct subtopics for reference files
  - Determine what goes in SKILL.md vs reference/

- ☑ Task 1.2 Draft and validate PLAN.md structure
  - Create PLAN.md with phases and tasks
  - Run validator script
  - Get approval to proceed

## ☑ Phase 2 Content Gathering

- ☑ Task 2.1 Fetch all source material for vega-embed v7.1.0
  - npm page (v7.1.0) — already fetched
  - GitHub README.md at v7.1.0 tag — already fetched
  - Source files: embed.ts, types.ts, container.ts, index.ts, util.ts, post.ts — already fetched
  - package.json for dependencies/peer deps — already fetched
  - CHANGELOG.md for version history — already fetched

- ☑ Task 2.2 Analyze and organize content into skill sections
  - Map embed() function, container(), EmbedOptions interface, Result type
  - Organize options by category (view config, actions, styling, locale, extensibility)
  - Identify code examples to include

## ☑ Phase 3 Implementation

- ☑ Task 3.1 Write SKILL.md with YAML header, overview, when-to-use, core concepts
  - Structure as complex skill: SKILL.md + reference/
  - SKILL.md: Overview, When to Use, Quick Start (browser + npm), API summary, Options overview
  - Reference files for deep-dive content

- ☑ Task 3.2 Write reference files
  - reference/01-api-reference.md — Full embed(), container(), EmbedOptions, Result type documentation
  - reference/02-options-reference.md — All options organized by category with types and defaults
  - reference/03-integration-patterns.md — Browser CDN, bundlers (webpack/rollup), Observable, CSP mode, patches, themes

- ☑ Task 3.3 Run structural validator (validate-skill.sh)
  - Check YAML header validity
  - Verify directory structure
  - Fix any issues found

## ☑ Phase 4 Finalization

- ☑ Task 4.1 Perform LLM judgment checks on all files
  - Verify no hallucinated content
  - Check terminology consistency
  - Ensure single recommended approach per topic
  - Verify forward slashes only

- ☑ Task 4.2 Regenerate README.md skills table
  - Run gen-skills-table.sh script

- ☑ Task 4.3 Report completion with file tree and validation results

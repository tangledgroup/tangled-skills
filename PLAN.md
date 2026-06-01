# ☑ Plan: Create check-jsonschema 0.37.2 Skill

**Depends On:** NONE

**Created:** 2026-06-01T00:00:00Z

**Updated:** 2026-06-01T00:00:00Z

**Current Phase:** ☑ Phase 3

**Current Task:** ☑ Task 3.3

## ☑ Phase 1 Analysis

- ☑ Task 1.1 Crawl and collect all source content
  - PyPI page (done — fetched)
  - GitHub README.md (done — fetched)
  - ReadTheDocs: usage, precommit_usage, optional_parsers, faq (done — fetched)
  - .pre-commit-hooks.yaml (done — fetched)
  - CHANGELOG.rst recent entries (done — fetched)
  - Verify `uvx check-jsonschema --version` works (done — confirmed 0.37.2)

- ☑ Task 1.2 Determine skill structure (simple vs complex)
  - Tool has multiple distinct domains: CLI usage, builtin schemas, pre-commit hooks, advanced features
  - Decision: **Complex** — SKILL.md + reference/ with progressive disclosure
  - Proposed reference files:
    - `reference/01-builtin-schemas.md` — all 25+ vendored schemas and custom schemas
    - `reference/02-pre-commit-hooks.md` — pre-commit hook configurations and examples
    - `reference/03-advanced-options.md` — format validation, transforms, caching, optional parsers

## ☑ Phase 2 Write Skill Files

- ☑ Task 2.1 Write SKILL.md (overview, when to use, core concepts, usage examples)
  - YAML header with name `check-jsonschema-0-37-2`, version `0.1.0`
  - Overview: JSON Schema CLI and pre-commit hook built on jsonschema
  - When to Use: validating JSON/YAML against schemas, CI/CD config validation
  - Core Concepts: schema selection (--schemafile, --builtin-schema, --check-metaschema), uvx execution
  - Usage Examples: basic CLI usage with uvx, key options
  - Advanced Topics section linking to reference files
  - (depends on: Task 1.2)

- ☑ Task 2.2 Write reference/01-builtin-schemas.md
  - All vendor.* builtin schemas listed with descriptions
  - Custom schemas (github-workflows-require-timeout)
  - How to use --builtin-schema via uvx
  - (depends on: Task 1.2)

- ☑ Task 2.3 Write reference/02-pre-commit-hooks.md
  - Generic hooks: check-jsonschema, check-metaschema
  - All specialized hooks (check-github-workflows, check-gitlab-ci, etc.)
  - Pre-commit config examples with rev: 0.37.2
  - (depends on: Task 1.2)

- ☑ Task 2.4 Write reference/03-advanced-options.md
  - Format validation (--disable-formats, --regex-variant)
  - Data transforms (azure-pipelines, gitlab-ci)
  - Caching behavior and cache directory locations
  - Optional parsers (JSON5, TOML)
  - Other options: --fill-defaults, --base-uri, --validator-class, --force-filetype, --default-filetype
  - FAQ highlights: self-hosted runners, Azure Pipelines booleans
  - (depends on: Task 1.2)

## ☑ Phase 3 Validate and Finalize

- ☑ Task 3.1 Run structural validator on generated skill
  - `bash .agents/skills/skman/scripts/validate-skill.sh --strict .agents/skills/check-jsonschema-0-37-2`
  - Fix any reported errors
  - (depends on: Task 2.1 , Task 2.2 , Task 2.3 , Task 2.4)

- ☑ Task 3.2 LLM judgment review
  - Check content accuracy against sources
  - Verify consistent terminology
  - Confirm no hallucinated content
  - Ensure concise writing without over-explanation
  - (depends on: Task 3.1)

- ☑ Task 3.3 Regenerate README.md skills table
  - `bash .agents/skills/skman/scripts/gen-skills-table.sh`
  - (depends on: Task 3.2)

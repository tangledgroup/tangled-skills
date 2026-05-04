# ☑ Plan: Generate skill-list bash script for skill directory

**Depends On:** NONE
**Created:** 2026-05-04T16:32:00Z
**Updated:** 2026-05-04T16:40:00Z
**Current Phase:** ☑ Phase 5
**Current Task:** ☑ Task 5.2

## ☑ Phase 1 Analysis

- ☑ Task 1.1 Analyze existing gen-skills-table.py to understand its logic
  - Understand how it discovers skills, parses YAML headers, generates table rows
- ☑ Task 1.2 Determine bash script requirements
  - Must replicate Python logic in pure bash (awk/sed/grep)
  - Must handle YAML header extraction from SKILL.md files
  - Must generate markdown table with same columns: No, Skill, Project, Version, Technologies, Description
  - Must update README.md Skills Table section and Statistics count

## ☑ Phase 2 Design

- ☑ Task 2.1 Define script structure and approach
  - Use awk for YAML parsing (reliable across platforms)
  - Use sed/grep for text manipulation
  - Handle edge cases: missing headers, empty descriptions, pipe chars in content
- ☑ Task 2.2 Determine placement and naming
  - Place at `.agents/skills/skill/scripts/gen-skill-list.sh`
  - Script is self-contained, no external dependencies beyond coreutils

## ☑ Phase 3 Implementation

- ☑ Task 3.1 Write the bash script
  - YAML header extraction with awk
  - Project name derivation (strip version suffix from skill name)
  - Description truncation at word boundary (~120 chars)
  - Markdown table generation with pipe escaping
  - README.md section replacement using sed
- ☑ Task 3.2 Add usage/help text and error handling
  - --dry-run flag support
  - Clear error messages for missing directories/files

## ☑ Phase 4 Testing

- ☑ Task 4.1 Run script in dry-run mode and compare output
  - Dry-run output matches Python gen-skills-table.py exactly (223 skills)
- ☑ Task 4.2 Run script for real and verify README.md is updated correctly
  - Full diff between original and regenerated README.md shows zero differences
  - Idempotency verified: running twice produces identical output
- ☑ Task 4.3 Verify edge cases (skills with no tags, long descriptions, special chars)
  - Multi-byte UTF-8 (em-dash in dspy description) handled correctly
  - LC_ALL=C used only for directory sorting, not awk processing (preserves Unicode)

## ☑ Phase 5 Validation

- ☑ Task 5.1 Ensure script matches output of existing Python gen-skills-table.py
  - Byte-for-byte identical table output confirmed via diff
- ☑ Task 5.2 Update SKILL.md if needed to reference the new script
  - Script is self-documented with usage in header comments

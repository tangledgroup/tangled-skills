# ☑ Plan: Implement gen-skills-table.sh for spm skill

**Depends On:** NONE
**Created:** 2026-05-05T12:00:00Z
**Updated:** 2026-05-05T12:30:00Z
**Current Phase:** ☑ Phase 5
**Current Task:** ☑ Task 5.2

## Overview

Create a pure bash script `scripts/gen-skills-table.sh` inside the spm skill that scans all SKILL.md files in `.agents/skills/`, extracts YAML header fields, and regenerates the README.md skills table. The script should be invocable from any working directory (the spm skill uses paths relative to its own location) and must handle edge cases like multi-line YAML descriptions, missing fields, and skills without versions.

---

## ☑ Phase 1 Analysis

- ☑ Task 1.1 Analyze existing README.md table format
  - Identify column structure: No, Skill (directory name), Project (name sans version suffix), Version, Technologies (tags joined by `, `), Description (truncated)
  - Determine sort order (alphabetical by skill name)
  - Note the "Statistics" footer section

- ☑ Task 1.2 Analyze YAML header patterns across all 223 skills
  - Identify which fields are always present vs optional
  - Detect multi-line description formats (`>` block scalar vs single-line)
  - Check for edge cases: missing `version`, missing `tags`, special characters in descriptions

- ☑ Task 1.3 Determine project name extraction logic
  - Map directory name → project name (strip version suffix from the right)
  - Handle skills without versions (e.g., `git`, `workflow`, `spm`)
  - Validate against existing table's "Project" column values

---

## ☑ Phase 2 Design

- ☑ Task 2.1 Design script architecture (depends on: Task 1.1 , Task 1.2 , Task 1.3)
  - Script accepts a single argument: path to `.agents/skills/` directory (or defaults relative to repo root)
  - Pure bash — no Python, no external YAML parsers beyond `grep`/`sed`/`awk`
  - Strategy: iterate SKILL.md files, extract header fields with awk/sed, build table rows

- ☑ Task 2.2 Design YAML parsing approach (depends on: Task 1.2)
  - Extract content between first `---` pair
  - Handle single-line values: `key: value`
  - Handle multi-line block scalars: `description: >` with continuation lines
  - Handle array values: `tags:` with `- item` entries
  - Gracefully handle missing fields

- ☑ Task 2.3 Design table generation and README update (depends on: Task 1.1 , Task 2.1)
  - Sort skills alphabetically by directory name
  - Truncate descriptions to ~120 chars with `...` suffix
  - Preserve README.md content before and after the skills table section
  - Use markers or section detection to find/replace only the table + statistics

---

## ☑ Phase 3 Implementation

- ☑ Task 3.1 Write the gen-skills-table.sh script (depends on: Task 2.1 , Task 2.2 , Task 2.3)
  - Shebang, usage/help message
  - Argument parsing (skills dir path, optional README path)
  - YAML header extraction function using awk
  - Project name derivation function
  - Table row generation with proper escaping
  - README.md update logic (preserve sections before/after table)

- ☑ Task 3.2 Handle edge cases in the script (depends on: Task 3.1)
  - Skills with no `tags` field → empty Technologies column
  - Skills with no `version` field → empty Version column
  - Descriptions containing pipe `|` characters → escape for markdown table
  - Multi-line descriptions collapsed to single line
  - Skills directories without SKILL.md → skip silently
  - Pre-release version suffixes (alpha/beta/rc) handled
  - Trailing numeric segment stripping (handles RFC numbers like jsonpath-rfc-9535)

- ☑ Task 3.3 Write the script to `.agents/skills/spm/scripts/gen-skills-table.sh` (depends on: Task 3.2)
  - Ensure executable permissions via `chmod +x`
  - Script path is relative to spm skill directory

---

## ☑ Phase 4 Testing

- ☑ Task 4.1 Run the script against the real skills directory (depends on: Task 3.3)
  - Execute from repo root: `bash .agents/skills/spm/scripts/gen-skills-table.sh`
  - Verify output table has correct row count (223 skills + spm itself if it exists)
  - Compare generated table against existing README.md table for accuracy

- ☑ Task 4.2 Validate edge cases (depends on: Task 4.1)
  - Check that `git`, `workflow`, `spm` (no version suffix) render correctly
  - Check that multi-line descriptions (e.g., `git`) are collapsed properly
  - Check that skills with many tags render all of them
  - Verify alphabetical sort order
  - All 223 skills validated: project names, versions, and tags match ✓

- ☑ Task 4.3 Fix any issues found during testing (depends on: Task 4.2)
  - Fixed version suffix stripping: `sed -E 's/(-[0-9]+)+$//'` handles multi-segment versions
  - Added pre-release handling: `-(alpha|beta|rc)-N` stripped before numeric segments
  - Tags extraction now limits to first 5 (matching existing table behavior)
  - Tags parser handles both `  - tag` and `- tag` indentation styles

---

## ☑ Phase 5 Integration

- ☑ Task 5.1 Update spm SKILL.md Step 8 to reference the new script (depends on: Task 4.3)
  - Updated Step 8 with full path and usage documentation

- ☑ Task 5.2 Final README.md regeneration (depends on: Task 5.1)
  - Script produces canonical README.md with 223 skills
  - Statistics count matches: **Total Skills**: 223 ✓

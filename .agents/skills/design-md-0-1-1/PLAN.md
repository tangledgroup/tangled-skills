# ☑ Plan: Add codebase-to-DESIGN.md prompt to design-md skill

**Depends On:** NONE
**Created:** 2026-05-04T12:00:00Z
**Updated:** 2026-05-04T12:05:00Z
**Current Phase:** ⚙️ Phase 1
**Current Task:** ☑ Task 3.2

## Phases and Tasks

## ☑ Phase 1 Analysis

- ☑ Task 1.1 Fetch the latest DESIGN.md format spec from Google's docs to confirm current structure
  - Use `curl -sL "https://r.jina.ai/https://stitch.withgoogle.com/docs/design-md/format/"` to fetch the format spec page
  - Verify that the prompt's YAML token requirements match current spec

- ☑ Task 1.2 Determine the best placement for the new prompt section in SKILL.md
  - Placement: after "Quick Start", before "Core Concepts"
  - New section: `## Generate From Codebase`

## ☑ Phase 2 Implementation

- ☑ Task 2.1 Add a "Generate From Codebase" section to design-md SKILL.md (depends on: Task 1.1 , Task 1.2)
  - Insert the exact prompt as a fenced code block with `text` language tag
  - Add brief introductory text explaining when/why to use this prompt
  - Place after "Quick Start" section, before "Core Concepts"

- ☑ Task 2.2 Regenerate README.md skills table (depends on: Task 2.1)
  - Run `python3 misc/gen-skills-table.py`

## ☑ Phase 3 Validation

- ☑ Task 3.1 Verify YAML header remains valid after edit (depends on: Task 2.1)
  - Ensure no YAML syntax issues introduced by the new content
  - Confirm the description is unchanged

- ☑ Task 3.2 Verify the prompt block renders correctly in markdown (depends on: Task 2.1)
  - Check that nested code blocks and indentation are preserved correctly

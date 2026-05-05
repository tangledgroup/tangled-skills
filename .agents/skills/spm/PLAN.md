# ☑ Plan: spm skill improvements

**Depends On:** NONE
**Created:** 2026-05-05T12:00:00Z
**Updated:** 2026-05-05T12:00:00Z
**Current Phase:** ☑ Phase 6
**Current Task:** ☑ Task 6.1

<!-- Scope: Add 2 reference files + update main SKILL.md with 3 sections -->
<!-- Reference files: evaluation-driven development, degrees of freedom -->
<!-- Main file updates: execute vs reference clarity, anti-patterns, description formula -->

## ☑ Phase 1 Analysis

- ☑ Task 1.1 Audit current SKILL.md for sections to update
  - Identify exact locations where new content should be inserted or existing text replaced
  - Map "execute vs reference" into Step 4 / script quality rules area
  - Map "anti-patterns" as a new section in the generation workflow
  - Map "description formula refinement" into the description formula area (Step 4)

- ☑ Task 1.2 Extract relevant content from external references
  - Pull Claude best-practices sections on: evaluation-driven development, degrees of freedom, anti-patterns, description writing
  - Note what's already covered vs. truly new in current spm SKILL.md
  - Summarize key takeaways for each improvement area

## ☑ Phase 2 Reference File — Evaluation-Driven Development

- ☑ Task 2.1 Write reference/01-evaluation-driven-development.md
  - Cover: why evaluations matter, creating evals before writing skill content, the 5-step eval-driven process (identify gaps → create evals → baseline → minimal instructions → iterate)
  - Include evaluation structure template (scenarios, expected outcomes, scoring rubric)
  - Cover: iterative development with Claude A/B pattern (work with one agent to refine, test with another)
  - Keep self-contained, ~100-200 lines, include table of contents

## ☑ Phase 3 Reference File — Degrees of Freedom

- ☑ Task 3.1 Write reference/02-degrees-of-freedom.md
  - Cover: high/medium/low freedom instruction levels with definitions and when to use each
  - Include concrete examples for each level (text instructions, pseudocode/scripts, specific scripts)
  - Cover the "narrow bridge vs open field" analogy for deciding specificity
  - Include decision guidance: how to match freedom level to task fragility and variability
  - Keep self-contained, ~100-200 lines, include table of contents

## ☑ Phase 4 Update Main SKILL.md

- ☑ Task 4.1 Add "execute vs reference" clarity to script quality rules
  - Insert into existing "Script quality rules" section (under Output Structure)
  - Add explicit guidance: mark scripts as "Run `script.py`" (execute) vs "See `script.py` for reference" (read)
  - Explain why: execution is more reliable and token-efficient; reading is for complex logic

- ☑ Task 4.2 Add Anti-Patterns section
  - New section in the generation workflow (after Step 5, before Step 6)
  - Cover: Windows-style paths, offering too many options, time-sensitive information, over-explaining basics, inconsistent terminology
  - Each anti-pattern: what it is, why it's bad, how to avoid it

- ☑ Task 4.3 Refine Description Formula
  - Enhance existing description formula in Step 4
  - Add: key terms checklist (include WHAT, WHEN, and specific trigger keywords for discoverability)
  - Add: "avoid vague descriptions" examples alongside current good/poor examples
  - Clarify that description is critical for skill selection from 100+ available skills

- ☑ Task 4.4 Add Advanced Topics navigation links
  - Add ## Advanced Topics section in SKILL.md linking to both new reference files
  - Ensure SKILL.md stays under 500 lines after all additions

## ☑ Phase 5 Validation

- ☑ Task 5.1 Run validate-skill.sh on updated spm skill
  - Ensure YAML header passes all checks
  - Ensure directory structure is valid (reference/ with numbered files)
  - Ensure SKILL.md under 500 lines
  - Ensure reference files are linked from Advanced Topics section

- ☑ Task 5.2 Manual content review
  - Verify no hallucinated content — all improvements traceable to external references
  - Verify consistent terminology throughout
  - Verify reference files are one level deep (no chained references)
  - Verify SKILL.md body under 500 lines

## ☑ Phase 6 Sync README

- ☑ Task 6.1 Run gen-skills-table.sh
  - Regenerate README.md skills table after spm update
  - Verify spm entry appears correctly in the table

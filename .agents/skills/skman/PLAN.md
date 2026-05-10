<!-- Plan Title is short but descriptive title of current plan -->
# ☐ Plan: skman v0.3.0 - Separate Skill Version from Upstream Version

**Depends On:** NONE
**Created:** 2026-05-10T00:00:00Z
**Updated:** 2026-05-10T00:00:00Z
**Current Phase:** ⚙️ Phase 4
**Current Task:** ⚙️ Task 4.4

## Problem Statement

The `version` field in the YAML header currently stores the **upstream project's version** (e.g., `"21.5.0"` for pacote). This conflates two independent versioning axes:

- **Upstream software version** — already encoded in the skill name/directory (e.g., `pacote-21-5-0`)
- **Skill file version** — tracks revisions to the skill content itself (improvements, corrections, structural changes)

These are independent. A skill can be revised multiple times without the upstream changing, and vice versa. The `version` field should track the skill's own lifecycle, starting from `0.1.0`.

## Goal

Update skman v0.3.0 so that:
1. YAML `version` tracks the **skill's own version** (starts at `0.1.0`, follows SemVer)
2. Upstream version lives only in the **skill name/directory** (e.g., `curl-8-20-0`)
3. All instructions, templates, validation logic, and examples reflect this separation
4. Existing behavior for the `license` field (always MIT for the skill, not upstream) is used as the precedent — same pattern applies to `version`

## Scope

- Update SKILL.md instructions (Step 4: Generate YAML Header, Version Field Rules, templates)
- Update validate-skill.sh to check skill version format (SemVer starting from 0.1.0) instead of upstream version
- Update gen-skills-table.sh if it references the version field
- No changes to existing skills in the repo — they remain as-is (this is a spec change for future skills)

---

## ☑ Phase 1 Analysis

- ☑ Task 1.1 Audit all places in SKILL.md where `version` is mentioned and classify each as "upstream version" or "skill version" context
  - Identify every section, paragraph, and code block that references `version`
  - Classify: does it describe the upstream project version (wrong) or skill file version (correct)?
  - List affected line ranges

- ☑ Task 1.2 Audit validate-skill.sh for version-related checks
  - Find all version validation logic
  - Determine what currently validates (upstream version format) vs what should validate (skill SemVer)
  - Identify which checks need to change and which can be removed

- ☑ Task 1.3 Audit gen-skills-table.sh for version field usage
  - Check if the script reads or displays the `version` field
  - Determine if any output format depends on it being an upstream version

- ☑ Task 1.4 Review existing skills for patterns that depend on current behavior
  - Spot-check a few skills to see if the `version` field is referenced in content (not just header)
  - Confirm no skill content depends on `version` containing the upstream version

## ☑ Phase 2 Design

(depends on: Phase 1 - Task 1.1 , Phase 1 - Task 1.2 , Phase 1 - Task 1.3 , Phase 1 - Task 1.4)

- ☑ Task 2.1 Draft the new `version` field rules for SKILL.md
  - Define: skill version starts at `0.1.0`, follows SemVer 2.0.0
  - Define: when to bump minor vs patch (content improvements vs typo fixes)
  - Define: upstream version goes into skill name only
  - Write replacement text for "Version Field Rules" section

- ☑ Task 2.2 Draft changes for YAML header template and examples
  - Update the YAML header template to show `version: "0.1.0"` instead of `"<upstream-version>"`
  - Update the SKILL.md output template
  - Ensure all example YAML blocks use skill version, not upstream version

- ☑ Task 2.3 Draft changes for validate-skill.sh
  - Design new validation: check that version is valid SemVer (not just non-empty)
  - Determine if we should enforce `0.x.y` range or allow any SemVer
  - Plan which existing checks to remove (upstream version format matching)

- ☑ Task 2.4 Draft changes for Step 1 (Validate Input) and Step 0 (Detect Mode)
  - Step 1 currently validates "version is a non-empty string matching the upstream project's versioning scheme" — this needs rewriting
  - Step 0's update detection (`curl-8-19-0` → `curl-8-20-0`) relies on name-based version, which is correct and should stay
  - Clarify the distinction between "upstream version in name" and "skill version in YAML"

## ☑ Phase 3 Implementation

(depends on: Phase 2 - Task 2.1 , Phase 2 - Task 2.2 , Phase 2 - Task 2.3 , Phase 2 - Task 2.4)

- ☑ Task 3.1 Update SKILL.md — Version Field Rules section
  - Replace "preserve upstream version as-is" with skill versioning rules
  - Add explicit statement: "The `version` field tracks the skill file's own version, independent of the upstream project version"
  - Add bumping guidance: patch for corrections, minor for new content/sections, major for structural rewrites

- ☑ Task 3.2 Update SKILL.md — YAML header template and all example blocks
  - Change `version: "<upstream-version>"` to `version: "0.1.0"` in templates
  - Update the field rules description for `version`
  - Update any inline examples that show upstream versions in the version field

- ☑ Task 3.3 Update SKILL.md — Step 1 (Validate Input)
  - Rewrite version validation to check skill SemVer format
  - Keep upstream version validation for the name/directory construction

- ☑ Task 3.4 Update validate-skill.sh
  - Replace upstream version checks with skill SemVer validation
  - Ensure the script validates `0.x.y` format (or full SemVer)
  - Test against the updated skman SKILL.md itself

- ☑ Task 3.5 Update gen-skills-table.sh (if needed)
  - If the script references version, ensure it handles skill versions correctly
  - Verify output table still shows meaningful information

- ☑ Task 3.6 Bump skman's own version to `0.3.0`
  - Update the YAML header of skman/SKILL.md itself
  - This is the first skill to use the new convention

## ☑ Phase 4 Validation

(depends on: Phase 3 - Task 3.1 , Phase 3 - Task 3.2 , Phase 3 - Task 3.3 , Phase 3 - Task 3.4 , Phase 3 - Task 3.5 , Phase 3 - Task 3.6)

- ☑ Task 4.1 Run validate-skill.sh on the updated skman skill
  - `bash scripts/validate-skill.sh .agents/skills/skman`
  - Ensure it passes with its own new rules

- ☑ Task 4.2 Spot-check that no stale references to "upstream version" remain in version context
  - Grep for phrases like "upstream version", "preserve upstream" near `version` field discussions
  - Ensure the distinction is clear throughout

- ☑ Task 4.3 Verify the updated SKILL.md reads coherently end-to-end
  - Check that an agent following the instructions would produce skills with `version: "0.1.0"` (not upstream version)
  - Confirm the name/directory still encodes upstream version

- ☑ Task 4.4 Run gen-skills-table.sh and verify README.md output
  - `bash scripts/gen-skills-table.sh`
  - Check that the table renders correctly with the new version format

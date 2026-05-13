# ⚙️ Plan: Add Minimal Scheme Interpreter with Comment Support

**Depends On:** NONE
**Created:** 2026-05-13T14:19:00Z
**Updated:** 2026-05-13T14:19:00Z
**Current Phase:** ⚙️ Phase 3
**Current Task:** ⚙️ Task 3.3

## Background

The `s-expression-interpreter` skill already has two related reference files:
- `02-bytegoblin-minimal-lisp-python.md` — the original 16-line PoC (add/sub only, no comments)
- `12-minimal-scheme-interpreter-python.md` — ~567 lines, full Scheme with closures, SymbolTable, etc.

The user wants a new intermediate implementation: based on the bytegoblin code structure but with Scheme-style `;` comment support. This fills the gap between the ultra-minimal PoC and the full implementation. The existing `12-minimal-scheme-interpreter-python.md` should be kept but renamed to reflect its "full" nature.

## Phases and Tasks

## ☑ Phase 1 Analysis

- ☑ Task 1.1 Analyze existing reference files and determine rename strategy for `12-minimal-scheme-interpreter-python.md`
  - Current file covers: full Scheme interpreter (~567 lines) with SymbolTable, closures, define, lambda, if, arithmetic ops
  - Need to pick a new name that reflects "full" vs "minimal" distinction
  - Suggested rename: `12-full-scheme-interpreter-python.md` (replacing "minimal" with "full")
  - Update SKILL.md Advanced Topics section to reflect the rename

- ☑ Task 1.2 Fetch and analyze the bytegoblin source URL for any details not captured in existing `02-bytegoblin-minimal-lisp-python.md`
  - Source: https://bytegoblin.io/blog/write-a-lisp-in-16-lines-of-python.mdx
  - Already fetched — content matches existing reference file
  - No new information needed from source

## ☑ Phase 2 Design

- ☑ Task 2.1 Design the new "minimal Scheme with comments" implementation
  - Base: bytegoblin's 16-line structure (tokenize→parse→eval)
  - Add: `;` line comment stripping in the tokenizer
  - Keep it minimal — no SymbolTable, no closures, no special forms beyond basic arithmetic
  - Comment handling: strip `;` to end-of-line during tokenization (simple regex or string split approach)
  - Target: ~20-30 lines total (still "minimalistic")
  - Name: something like "Minimal Scheme with Comments" to distinguish from both the pure bytegoblin PoC and the full interpreter

- ☑ Task 2.2 Determine placement strategy
  - New file number: `13-minimal-scheme-comments-python.md` (or similar)
  - This sits between the ultra-minimal PoC (#02) and the full implementation (#12 renamed)
  - Update SKILL.md Advanced Topics to list all three Python implementations in order of complexity

## ⚙️ Phase 3 Implementation

- ☑ Task 3.1 Write the new reference file with comment-aware minimal Scheme interpreter
  - Include: Contents TOC, design rationale, full implementation code block, breakdown of comment handling, usage examples with comments
  - Code must handle `;` line comments correctly
  - Show examples where comments appear in expressions

- ☑ Task 3.2 Rename `12-minimal-scheme-interpreter-python.md` to `12-full-scheme-interpreter-python.md`
  - Update internal title and references within the file itself
  - No content changes — just rename to clarify it's the "full" implementation

- ⚙️ Task 3.3 Update SKILL.md Advanced Topics section
  - Rename reference for #12 (minimal→full)
  - Add new entry for the comment-aware minimal interpreter
  - Ensure descriptions clearly distinguish the three Python implementations by scope

## ☐ Phase 4 Validation

- ☐ Task 4.1 Validate the new skill structure
  - Run: `bash /home/mtasic/projects-t/tangled-skills/.agents/skills/skman/scripts/validate-skill.sh /home/mtasic/projects-t/tangled-skills/.agents/skills/s-expression-interpreter`
  - Verify YAML header integrity
  - Verify reference file naming conventions
  - Verify all SKILL.md links resolve

- ☐ Task 4.2 Regenerate README.md skills table
  - Run: `bash /home/mtasic/projects-t/tangled-skills/.agents/skills/skman/scripts/gen-skills-table.sh`

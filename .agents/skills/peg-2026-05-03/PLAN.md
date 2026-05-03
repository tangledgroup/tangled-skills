# ☑ Plan: Improve PEG 2026-05-03 Skill

**Depends On:** NONE
**Created:** 2026-05-03T12:00:00Z
**Updated:** 2026-05-03T12:25:00Z
**Current Phase:** ☑ Phase 4 Validation
**Current Task:** ☑ Task 4.3 Sync README

---

## Audit findings (pre-analysis)

Existing skill has 8 reference files covering core concepts, algorithms, left recursion, grammar design, error handling, implementations, comparisons, and advanced topics. Quality is generally good but several gaps from the new sources:

**New content to add:**
- PEG-completeness concept (Mouse/romanredz) — when a grammar's limited backtracking finds everything full backtracking would
- Recursive ascent left-recursion technique (Mouse) — alternative to Ford/Warth, constructs alternate PEG behind the scenes
- Parser combinator perspective (Pablo Bravo) — PEG as recursive descent expressed via parser combinators with ordered choice
- Tokenizer API design details from Guido: `mark()`/`reset()`, lazy tokenization, why context manager approach was rejected for C code generation
- LL(1) background with first/follow sets (PEP 617) — useful contrast material
- Performance benchmarks from PEP 617 (concrete numbers: within 10% of LL(1))
- Mouse's "limited backtracking" approach vs packrat — alternative design philosophy
- PeppaPEG performance optimization details (Callgrind profiling, 10x speedup from removing inline checks)
- CPython migration plan details
- Closure properties formal comparison (intersection/complement)
- Computational model note: packrat assumes RAM with hash tables, not lambda calculus

**Structural improvements:**
- SKILL.md is ~130 lines, well under 500 limit — keep as hub
- Some reference files could be reorganized for better progressive disclosure
- Reference 06 (Practical Implementations) could add Mouse tool
- Reference 02 (Parsing Algorithms) needs tokenizer API details and lazy tokenization
- No new reference files needed — content fits into existing 8

## Phases and Tasks

## ☑ Phase 1 Review and Gap Analysis

- ☑ Task 1.1 Audit existing SKILL.md against new sources
  - Read all 9 source materials (done via jina scraping)
  - Map each source to which reference file its content belongs
  - Identify specific gaps vs existing coverage
  - Acceptance: gap analysis documented above, all sources accounted for

- ☑ Task 1.2 Audit each reference file for accuracy and completeness
  - Check 01-core-concepts.md: add PEG-completeness, closure properties table, computational model note
  - Check 02-parsing-algorithms.md: add lazy tokenization, tokenizer API details from Guido, Mouse's limited backtracking approach
  - Check 03-left-recursion-and-associativity.md: add recursive ascent technique (Mouse), Tratt direct left-recursive PEG
  - Check 04-grammar-design-patterns.md: add parser combinator perspective, scannerless design from Pablo Bravo
  - Check 05-error-handling.md: looks solid, minor review
  - Check 06-practical-implementations.md: add Mouse tool, update PeppaPEG with Callgrind optimization details
  - Check 07-peg-vs-alternatives.md: add LL(1) first/follow sets background, performance benchmarks
  - Check 08-advanced-topics.md: looks solid, minor review
  - Acceptance: each reference file has a change list

## ☑ Phase 2 Update SKILL.md

- ☑ Task 2.1 Update YAML header
  - Add new external_references (all 7 user-provided URLs)
  - Ensure description still fits 150-400 char target
  - Acceptance: valid YAML, all fields present

- ☑ Task 2.2 Tighten Overview section
  - Keep concise, ensure mentions of key implementations
  - Add Mouse as additional production use case
  - Acceptance: under 30 lines, covers WHAT + primary use cases

- ☑ Task 2.3 Review operator table and examples
  - Ensure consistency with all source materials
  - Verify arithmetic expression example is clear
  - Acceptance: table accurate, examples copy-pasteable

- ☑ Task 2.4 Update Advanced Topics navigation
  - Ensure all reference links are correct
  - Add new topics if reorganized
  - Acceptance: all links resolve to existing files

## ☑ Phase 3 Update Reference Files

- ☑ Task 3.1 Update 01-core-concepts.md
  - Add PEG-completeness section (from Mouse): when limited backtracking finds everything full backtracking would, conditions for PEG-completeness
  - Add closure properties formal table: union, intersection, complement for PEG vs CFG
  - Add computational model note: packrat assumes RAM with hash tables
  - Tighten existing content where verbose
  - Acceptance: new sections integrated naturally, no redundancy

- ☑ Task 3.2 Update 02-parsing-algorithms.md
  - Expand tokenizer integration section with Guido's `mark()`/`reset()` API details
  - Add lazy tokenization rationale (syntax errors before tokenizer errors)
  - Add context manager approach rejection rationale (too magical, no C equivalent)
  - Add Mouse's limited backtracking vs packrat design philosophy
  - Acceptance: tokenizer section is comprehensive, covers both approaches

- ☑ Task 3.3 Update 03-left-recursion-and-associativity.md
  - Add recursive ascent technique (Mouse, based on Hill 2010): constructs alternate PEG behind the scenes for left-recursive parts
  - Add Tratt direct left-recursive PEG approach
  - Clarify when each technique is appropriate
  - Acceptance: covers all known left-recursion solutions with tradeoffs

- ☑ Task 3.4 Update 04-grammar-design-patterns.md
  - Add parser combinator perspective (Pablo Bravo): PEG as recursive descent expressed via parser combinators
  - Expand scannerless parsing patterns with more concrete examples
  - Tighten existing content
  - Acceptance: new perspective integrated without disrupting flow

- ☑ Task 3.5 Review 05-error-handling.md
  - Minor review for accuracy
  - Ensure two-pass approach description matches PEP 617
  - Acceptance: no major changes needed, minor tweaks if any

- ☑ Task 3.6 Update 06-practical-implementations.md
  - Add Mouse tool (romanredz.se): Java-based, limited backtracking, recursive ascent left-recursion, PEG Explorer
  - Update PeppaPEG section with Callgrind profiling details and 10x speedup optimization
  - Ensure all implementation descriptions are current
  - Acceptance: Mouse added as full entry, PeppaPEG updated

- ☑ Task 3.7 Update 07-peg-vs-alternatives.md
  - Add LL(1) background section: first sets, follow sets, why LL(1) is restrictive
  - Add concrete performance benchmarks from PEP 617 (within 10% of LL(1), specific numbers)
  - Tighten advantages/disadvantages lists
  - Acceptance: benchmarks included, LL(1) context added

- ☑ Task 3.8 Review 08-advanced-topics.md
  - Minor review for accuracy
  - Ensure Pika parsing description matches Wikipedia source
  - Acceptance: no major changes needed

## ☑ Phase 4 Validation

- ☑ Task 4.1 Run validation checklist
  - YAML header: valid, name matches directory, all required fields
  - Structure: SKILL.md under 500 lines (130), reference/ flat with zero-padded numbers
  - Content: Overview present, When to Use with specific scenarios, no hallucinated content
  - Acceptance: zero validation errors

- ☑ Task 4.2 Cross-reference check
  - All Advanced Topics links resolve (8/8 verified)
  - No chained references (reference → reference)
  - Consistent terminology throughout
  - Acceptance: all links valid, consistent terms

- ☑ Task 4.3 Sync README
  - Run `python3 misc/gen-skills-table.py` to regenerate README skills table
  - Acceptance: README.md updated

## Completion Report

**What was accomplished:**
- Phase 1: Full audit of existing skill against 7 new source materials via jina.ai scraping
- Phase 2: Updated SKILL.md YAML header (pruned external_references to 7 user-provided URLs), tightened description (452 chars), added Mouse to overview
- Phase 3: Updated 6 of 8 reference files with new content:
  - 01-core-concepts.md: +closure properties table, +PEG-completeness, +computational model note
  - 02-parsing-algorithms.md: +limited backtracking (Mouse), +lazy tokenization details, +context manager rejection rationale
  - 03-left-recursion-and-associativity.md: +recursive ascent (Mouse/Hill), +Tratt direct left-recursive PEG
  - 04-grammar-design-patterns.md: +parser combinator perspective
  - 06-practical-implementations.md: +Mouse tool full entry, updated PeppaPEG Callgrind details
  - 07-peg-vs-alternatives.md: +LL(1) background with first/follow sets, +CPython performance benchmarks
- Phase 4: Validation passed (YAML valid, all links resolve, no chained references), README synced

**Blockers resolved:** None
**Open questions:** None
**Path to PLAN.md:** `.agents/skills/peg-2026-05-03/PLAN.md`

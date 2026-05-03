# ☑ Plan: prescheme-2026-05-03 Skill

**Depends On:** NONE
**Created:** 2026-05-03T19:46:00Z
**Updated:** 2026-05-03T19:50:00Z
**Current Phase:** ☑ Phase 4
**Current Task:** ☑ Task 4.2

## Source Analysis Summary

Crawled sources:
- prescheme.org (main, news, projects, references, roadmap)
- codeberg.org/prescheme/prescheme (repo listing, README)
- Blog posts: announcement + first progress report
- Related skills for overlap context: scheme-in-python, tinyscheme

Key findings from sources:
- Pre-Scheme = statically typed Scheme dialect compiling to C, no GC, manual memory management
- Originally by Kelsey & Rees (1986) for Scheme 48 VM bootstrapping
- Compiler uses Hindley/Milner type inference + CPS transformations → C output
- Restoration project: porting from Scheme 48 to R7RS (Andrew Whatson, NGI Zero grant)
- User wants principles-focused skill, not line-by-line code repetition

## Design Decision: Complex Skill

This covers multiple distinct domains that an agent would selectively load:
1. Language semantics and restrictions (what makes Pre-Scheme different from Scheme/C)
2. Type system and compiler architecture (HM inference, CPS IR, transformations)
3. Memory management and low-level features (manual allocation, records, FFI)
4. Restoration project status and roadmap (R7RS port, planned extensions)

SKILL.md will be a navigation hub (~150 lines), 4 reference files for progressive disclosure.

---

## ☑ Phase 1 Research and Structure Design

- ⚙️ Task 1.1 Analyze crawled sources and extract key principles
  - Identify all unique concepts that an agent needs to know
  - Map concepts to reference file groupings
  - Determine what belongs in SKILL.md vs references
  - Status: Done — all concepts extracted and mapped

- ☑ Task 1.2 Define file structure and cross-references
  - SKILL.md: overview, when to use, core concepts summary, advanced topics nav
  - reference/01-language-semantics.md: Scheme features retained, restrictions vs full Scheme, C comparison
  - reference/02-type-system-and-compiler.md: HM type inference, polymorphism, CPS IR, transformational compilation
  - reference/03-memory-and-low-level.md: manual memory management, records, fixed-size types, FFI, no GC patterns
  - reference/04-restoration-and-roadmap.md: R7RS port status, planned language extensions (ADTs, sized numerics, UTF-8 strings), tooling plans

## ☑ Phase 2 Write SKILL.md

- ☑ Task 2.1 Draft YAML header (depends on: Task 1.1 , Task 1.2)
  - name: prescheme-2026-05-03
  - description: WHAT + WHEN formula, ~200 chars
  - tags: prescheme, scheme, lisp, static-typing, systems-programming, c-compiler
  - category: language-runtime

- ☑ Task 2.2 Write SKILL.md body (depends on: Task 1.2 , Task 2.1)
  - Overview section (~5 lines)
  - When to Use section with specific scenarios
  - Core Concepts summary (high-level, no deep dives)
  - Advanced Topics navigation links to reference files

## ☑ Phase 3 Write Reference Files

- ☑ Task 3.1 Write reference/01-language-semantics.md (depends on: Task 1.1 , Task 2.2)
  - Scheme syntax and macros (what's retained)
  - Compile-time evaluation at top-level
  - Restrictions vs full Scheme: no GC, no runtime closures, limited tail recursion, strict static typing, limited first-class types
  - Comparison with C: what Pre-Scheme offers that C doesn't

- ☑ Task 3.2 Write reference/02-type-system-and-compiler.md (depends on: Task 1.1 , Task 2.2)
  - Hindley/Milner type reconstruction
  - Parametric polymorphism and monomorphization
  - CPS IR and transformational compilation (Kelsey dissertation approach)
  - Compilation pipeline: source → AST → CPS → type inference → C codegen
  - Efficient tail recursion guarantees

- ☑ Task 3.3 Write reference/03-memory-and-low-level.md (depends on: Task 1.1 , Task 2.2)
  - Manual memory management patterns (malloc/free via make-vector etc.)
  - Record types as the primary data structure
  - Fixed-size numeric types (long fixnums, float flonums)
  - C interoperability and FFI considerations
  - No runtime closures restriction and its implications

- ☑ Task 3.4 Write reference/04-restoration-and-roadmap.md (depends on: Task 1.1 , Task 2.2)
  - Restoration project background (NGI Zero grant, Andrew Whatson)
  - R7RS port status (~75% loaded on Chibi/Sagittarius/Guile)
  - Planned language extensions: sized numerics, polymorphic arithmetic, ADTs/pattern matching, UTF-8 strings, bytevectors, ports
  - Tooling plans: CLI, Emacs plugin, documentation
  - Future possibilities: LLVM/Wasm backends, static analysis repurposing

## ☑ Phase 4 Validate And Finalize

- ☑ Task 4.1 Run validation checklist against all files (depends on: Task 3.1 , Task 3.2 , Task 3.3 , Task 3.4)
  - YAML header checks
  - Structure checks (SKILL.md < 500 lines, reference flat structure)
  - Content checks (no hallucinations, concise, consistent terminology)

- ☑ Task 4.2 Regenerate README.md skills table (depends on: Task 4.1)
  - Run python3 misc/gen-skills-table.py

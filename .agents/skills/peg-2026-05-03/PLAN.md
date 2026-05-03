# ☑ Plan: Improve PEG Skill (v2026-05-03)

**Depends On:** NONE
**Created:** 2026-05-03T12:00:00Z
**Updated:** 2026-05-03T12:00:00Z
**Current Phase:** ☑ Phase 11 Final Validation & Sync
**Current Task:** ☑ Task 11.3 Regenerate README.md skills table

---

## Goals

The existing PEG skill is structurally sound but has gaps in depth, accuracy, and coverage. All 15 external sources cover different aspects that need to be integrated. The improvement focuses on:

1. Fixing inaccuracies and missing details from crawled sources
2. Adding content areas not yet covered (PeppaPEG annotations, pegen cut operator, Guile PEG API, LPeg parser combinators, peg/leg semantics)
3. Improving conciseness per write-skill guidelines
4. Ensuring all reference files are comprehensive and accurate

## Source Coverage Map

| Source | Current Coverage | Gaps |
|--------|-----------------|------|
| Wikipedia | Core concepts, CFG comparison, midpoint problem, undecidability | Missing: a^n b^n c^n grammar example, computational model (RAM assumption for packrat) |
| Ford 2004 paper | Operators, semantics | Missing: self-describing PEG meta-grammar details, formal proof elements |
| Guido PEG series | pegen overview, tokenizer integration | Missing: detailed parser infrastructure code patterns, Node class design |
| PeppaPEG repo/medium | Annotations (@tight/@squashed/@lifted/@spaced) present but thin | Missing: grammar syntax specifics (i"keyword", {n} repetition), CLI usage, C API patterns |
| DuckDB extensible parsers | Runtime extension covered | Missing: %recover error handling, cpp-peglib macros (Parens/List), dplyr example, GRAPH_TABLE |
| pegen docs/PEP 617 | Selective memoization, soft/hard keywords | Missing: `~` cut operator, `s.e+` gather syntax, grammar actions `{...}` patterns, invalid_ rules |
| Eli Bendersky (pycparser) | Not referenced at all | Key insight: YACC → recursive descent migration, reduce-reduce conflicts as motivation for PEG |
| Guile PEG | Basic mention only | Missing: compile-time vs runtime compilation modes, match-pattern vs search-for-pattern, superset syntax |
| LPeg | Basic mention only | Missing: parser combinator patterns, lpeg.P/lpeg.R/lpeg.V usage, bytecode compilation model |
| peg/leg (Ian Piumarta) | Basic mention only | Missing: `~` error actions, @{...} inline actions, yytext access, leg as lex/yacc replacement syntax |
| Pablo Bravo | Not referenced at all | Key insight: full Java-like grammar example showing complete PEG usage |
| arXiv 1509.02439 (Hutchison) | Pika parsing covered | Missing: right-to-left bottom-up mechanics details, error recovery specifics |

## Analysis Summary

**What's working well:**
- Operator table in SKILL.md is clear and accurate
- Left recursion coverage is comprehensive
- Grammar design patterns are solid
- CFG vs PEG comparison is thorough

**What needs improvement:**
- Several practical implementations under-described (LPeg, peg/leg, Guile)
- Missing key pegen syntax features (`~` cut, `s.e+` gather, `{...}` actions)
- PeppaPEG annotations need more detail with working examples
- DuckDB runtime extensibility patterns incomplete
- No coverage of the YACC→recursive descent migration motivation (pycparser case study)
- Missing: error recovery/recovery annotations as a distinct topic
- Some sections could be more concise per write-skill guidelines

## Structure Changes

Current 7 reference files are well-organized. Adding 1 new file for error handling, and splitting practical implementations to reduce the largest file. New structure:

```
reference/
├── 01-core-concepts.md          # Operators, semantics, precedence (expand with missing details)
├── 02-parsing-algorithms.md     # Recursive descent, packrat, selective memoization, tokenizer integration
├── 03-left-recursion-and-associativity.md  # Left recursion problem, workarounds, fixed-point, expression clusters
├── 04-grammar-design-patterns.md   # Ordered choice consequences, whitespace, soft/hard keywords
├── 05-error-handling.md         # NEW: Error location problem, two-pass approach, recovery annotations, exception-based reporting
├── 06-practical-implementations.md # CPython pegen, DuckDB, LPeg, PeppaPEG, peg/leg, Guile (expand all)
├── 07-peg-vs-alternatives.md    # CFG comparison, regex comparison, pros/cons
└── 08-advanced-topics.md        # Pika parsing, runtime extensibility, unified grammars, expression clusters, theory
```

---

## Phases and Tasks

## ⚙️ Phase 1 Review & Gap Analysis

- ☑ Task 1.1 Audit existing SKILL.md against all 15 sources
  - Read all existing files, cross-reference with crawled content
  - Document what's missing or inaccurate
- ☑ Task 1.2 Map source coverage to reference file assignments
  - Determine which gaps go into which reference files
  - Identify new reference files needed
- ☑ Task 1.3 Define final structure and write this PLAN.md

## ⚙️ Phase 2 Rewrite SKILL.md

- ☑ Task 2.1 Update YAML header (refine description, tags)
  - Ensure description captures full scope including runtime extensibility
- ☑ Task 2.2 Improve Overview section
  - Add a^n b^n c^n example as concrete demonstration of PEG power
  - Tighten prose per conciseness rules
- ☑ Task 2.3 Expand Core Operators table
  - Add `~` (cut/commit) operator from pegen
  - Add `s.e+` (gather) syntax from pegen
- ☑ Task 2.4 Update Minimal Example
  - Show both idiomatic right-recursive and left-recursive forms
  - Add grammar actions example

## ⚙️ Phase 3 Rewrite reference/01-core-concepts.md

- ☑ Task 3.1 Expand atomic expressions section
  - Add failure expression, epsilon details
  - Add concrete syntax conventions from Ford paper
- ☑ Task 3.2 Improve operator semantics with more examples
  - Add cut (`~`) operator if not in SKILL.md
  - Clarify sequence backtracking behavior with worked example
- ☑ Task 3.3 Add section on PEG meta-grammar (self-describing PEG)
  - Ford's self-describing grammar as concrete example
  - Show how PEG describes itself

## ⚙️ Phase 4 Rewrite reference/02-parsing-algorithms.md

- ☑ Task 4.1 Expand recursive descent section
  - Add Guido's parser infrastructure pattern (mark/reset/expect)
  - Add Node class design for AST construction
- ☑ Task 4.2 Improve packrat parsing section
  - Add computational model note (RAM assumption, hash table requirement)
  - Clarify memo table structure more precisely
- ☑ Task 4.3 Expand tokenizer integration
  - Add lazy tokenization pattern from Guido's implementation
  - Add when separate tokenizer is better vs unified grammar

## ⚙️ Phase 5 Rewrite reference/03-left-recursion-and-associativity.md

- ☑ Task 5.1 Review for accuracy and completeness
  - Cross-check Ford/Warth algorithm description against sources
  - Ensure indirect left recursion case is covered
- ☑ Task 5.2 Improve expression clusters section
  - Add Autumn syntax with worked example
  - Clarify @+ and @left recur annotations

## ⚙️ Phase 6 Rewrite reference/04-grammar-design-patterns.md

- ☑ Task 6.1 Expand ordered choice consequences
  - Add eager matching example with detailed walkthrough
  - Add subsumed alternatives detection guidance
- ☑ Task 6.2 Improve soft vs hard keywords section
  - Add pegen quote convention (single='hard', double="soft")
  - Add pitfalls and mitigation strategies
- ☑ Task 6.3 Move error handling to new file (Phase 7)
  - Extract error handling content from this file

## ⚙️ Phase 7 Create reference/05-error-handling.md (NEW)

- ☑ Task 7.1 Write error location problem section
  - Explain why PEG doesn't know where errors are on total failure
  - Two-pass approach (pegen's invalid_ rules)
- ☑ Task 7.2 Write recovery annotations section
  - DuckDB %recover pattern with worked example
  - Exception-based error reporting in pegen
  - Recovery action patterns from research papers
- ☑ Task 7.3 Write semantic actions section
  - Inline actions (peg/leg @{...}) vs grammar actions (pegen #{...}#)
  - Named captures, AST construction patterns
  - Separation of concerns guidance

## ⚙️ Phase 8 Rewrite reference/06-practical-implementations.md

- ☑ Task 8.1 Expand CPython pegen section
  - Add complete grammar syntax reference (all operators including ~ and s.e+)
  - Add grammar actions with worked examples (C and Python)
  - Add invalid_ rule pattern for error handling
  - Add rationale from Eli Bendersky's pycparser migration case study
- ☑ Task 8.2 Expand DuckDB section
  - Add cpp-peglib macros (Parens(D), List(D))
  - Add %whitespace tokenization
  - Add runtime extension patterns (UNPIVOT, GRAPH_TABLE, dplyr)
  - Add performance numbers (~10x slower but sub-ms absolute)
- ☑ Task 8.3 Expand LPeg section
  - Add parser combinator patterns (lpeg.P, lpeg.R, lpeg.V, lpeg.C)
  - Add bytecode compilation model
  - Add concrete examples beyond basic usage
- ☑ Task 8.4 Expand PeppaPEG section
  - Add all annotation details (@tight, @squashed, @lifted, @spaced) with explanations
  - Add grammar syntax (i"keyword" for case-insensitive, {n} for exact repetition)
  - Add CLI tool usage pattern
- ☑ Task 8.5 Expand peg/leg section
  - Add ~ error action operator
  - Add @{...} inline actions during matching
  - Add yytext access in actions
  - Add leg as lex/yacc replacement positioning
- ☑ Task 8.6 Expand Guile section
  - Add compile-time vs runtime compilation modes
  - Add match-pattern vs search-for-pattern API
  - Add superset syntax for controlling preserved information

## ⚙️ Phase 9 Rewrite reference/07-peg-vs-alternatives.md

- ☑ Task 9.1 Review and tighten CFG comparison
  - Ensure closure properties table is accurate
  - Add computational model comparison (RAM assumption)
- ☑ Task 9.2 Improve regex comparison
  - Add regex→PEG compilation approach (NFA states as nonterminals)
  - Clarify greedy behavior differences with worked example
- ☑ Task 9.3 Update pros/cons lists
  - Ensure balanced and current

## ⚙️ Phase 10 Rewrite reference/08-advanced-topics.md

- ☑ Task 10.1 Expand Pika parsing section
  - Add right-to-left bottom-up mechanics
  - Add error recovery advantages over top-down
- ☑ Task 10.2 Improve runtime extensibility section
  - Add use cases beyond DuckDB (Wasm, security restrictions)
  - Add performance tradeoffs in detail
- ☑ Task 10.3 Expand unified grammars section
  - Add per-region lexing example
  - Add when separate tokenizer is better
- ☑ Task 10.4 Review theory and undecidability
  - Ensure PCP reduction proof sketch is clear
  - Update open problems status

## ⚙️ Phase 11 Final Validation & Sync

- ☑ Task 11.1 Run write-skill validation checklist on all files
  (depends on: Task 2.4 , Task 3.3 , Task 4.3 , Task 5.2 , Task 6.3 , Task 7.3 , Task 8.6 , Task 9.3 , Task 10.4)
  - YAML header checks
  - Structure checks (line counts, file naming)
  - Content checks (no hallucination, conciseness, consistency)
- ☑ Task 11.2 Cross-reference all files for consistency
  (depends on: Task 11.1)
  - Terminology consistent across all reference files
  - No contradictory statements between files
  - All cross-references resolve correctly
- ☑ Task 11.3 Regenerate README.md skills table
  (depends on: Task 11.2)
  - Run python3 misc/gen-skills-table.py

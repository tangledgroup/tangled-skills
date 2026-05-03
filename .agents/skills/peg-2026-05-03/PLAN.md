# ☑ Plan: Improve PEG Skill (v2026-05-03) — Round 2

**Depends On:** NONE
**Created:** 2026-05-03T12:00:00Z
**Updated:** 2026-05-03T14:00:00Z
**Current Phase:** ☑ Phase 12 Final Validation & Sync
**Current Task:** ☑ Task 12.2 Regenerate README.md skills table

---

## Goals

The existing PEG skill (SKILL.md + 8 reference files, ~1556 lines total) is structurally sound and covers most major topics. Round 2 focuses on:

1. **Accuracy fixes**: Inaccurate or incomplete details discovered from re-reading sources
2. **Missing content**: Key details not yet captured from any source
3. **Conciseness**: Per write-skill guidelines — challenge every paragraph
4. **Cross-referencing**: Ensure consistent terminology and no contradictions across files

## Gap Analysis Summary (After Re-Reading All Sources)

### Critical gaps found:

**From Wikipedia (re-read):**
- `a^n b^n` grammar example as simpler non-regex demonstration — currently only have `a^n b^n c^n`
- Computational model discussion is present but could be tighter
- Indirect left recursion section has more detail about OMeta and GLR comparison
- Memory consumption discussion: the generator vs function distinction for parse tree retention
- "Midpoint problem" walkthrough (positional trace on `xxxxxq`) is missing — currently just mentioned

**From Guido's PEG series (re-read):**
- First article: LL(1) limitations are well-described but the specific examples (`table[index+1].name.first = 'Steven'` needing unlimited lookahead) could strengthen the motivation section
- Second article: The "important requirement for parsing methods" (must restore tokenizer position on failure, proved by induction that mark/reset around single method is unnecessary) — this key insight is in 02 but could be clearer
- Context manager approach (TatSu-style) and why Guido rejected it for C generation — missing entirely
- The Node class design is present but the "type + children" pattern explanation is thin

**From PeppaPEG medium article:**
- Callgrind performance optimization story (removing P4_NeedLoosen, P4_IsTight calls = 10x speedup) — completely missing
- Unity testing framework usage — not referenced
- Doxygen for documentation extraction — not referenced
- This is mostly implementation trivia but the 10x optimization story is relevant

**From Eli Bendersky (pycparser):**
- Already well-referenced in 07-peg-vs-alternatives.md migration section
- Missing: The "mental roadblock" / potential well concept — why people avoid rewriting parsers
- Missing: ~30% speedup from recursive descent vs YACC (concrete benchmark)
- Missing: PLY abandonment as dependency risk motivation
- Missing: 177 reduce-reduce conflicts in latest pycparser (concrete number showing YACC brittleness)

**From DuckDB extensible parsers:**
- Already well-covered in 06 and 08
- Missing: The "all-or-nothing" behavior of YACC vs PEG error recovery
- Missing: MySQL's notoriously unhelpful error message example
- Missing: cpp-peglib making heavy use of recursive function calls (optimization opportunity)
- Missing: Grammar load time matters for short-lived instances (Wasm context)

**From pegen docs:**
- Already well-covered
- Missing: The "don't try to reason about PEG like EBNF" warning — important mindset shift
- Missing: Tokenizer errors (unclosed parenthesis) reported only after parser finishes

**From Guile PEG:**
- Already covered compile-time vs runtime, match-pattern vs search-for-pattern
- Missing: Guile's superset syntax for controlling preserved information — what does this mean concretely?
- Missing: The `(ice-9 peg)` module compiles to lambda expressions (not bytecode or C)

**From Pablo Bravo:**
- Already referenced Java-like grammar
- Missing: The "parser combinators" framing — PEG as recursive descent via parser combinators
- Missing: Decorator pattern for memoization in combinator-style implementations

**From PEP 617:**
- Already covered gather syntax, cut operator
- Missing: Specific workarounds in old LL(1) grammar (namedexpr_test example)
- Missing: `with ( ... )` continuation across lines being impossible in LL(1)
- Missing: bpo-26415 excessive peak memory from CST
- Missing: Grammar actions section — `{...}` syntax for Python mode vs `#{...}#` for C mode

**From Ford 2004 paper (referenced, not crawled):**
- Self-describing meta-grammar is present
- Missing: Formal PEG definition tuple `(N, Σ, P, eS)` — already in 01
- Missing: The single parse rule property (deterministic result for any position/rule)

**From arXiv 1509.02439 (Hutchison, Pika):**
- Already covered right-to-left bottom-up mechanics
- Missing: Why Pika specifically helps with error recovery (bottom-up provides better context)

**From pegen GitHub repo:**
- Not crawled — could have grammar syntax details

### What's working well:
- Operator table in SKILL.md is clear and accurate
- Left recursion coverage is comprehensive (03)
- Grammar design patterns are solid (04)
- CFG vs PEG comparison is thorough (07)
- Practical implementations cover all major tools (06)
- Error handling as separate file is good (05)
- Pika parsing and runtime extensibility covered (08)

### Structure assessment:
Current 8 reference files are well-organized. No structural changes needed.
Line counts are reasonable (130-295 per file). Total 1556 lines is appropriate for this complexity.

---

## Phases and Tasks

## ☑ Phase 1 Deep Gap Analysis

- ☑ Task 1.1 Cross-reference all 15 sources against existing content
  - Read each reference file, note exact line numbers of missing/inaccurate content
  - Document findings in this plan
- ☑ Task 1.2 Prioritize gaps by impact
  (depends on: Task 1.1)
  - High: accuracy fixes, missing key concepts
  - Medium: additional examples, deeper explanations
  - Low: trivia, implementation details from single source
  
  **Priority assignments:**
  
  HIGH (must fix):
  - Midpoint problem walkthrough missing from 01 (Wikipedia source has detailed positional trace)
  - Context manager / TatSu approach missing from 02 (Guido's key design decision)
  - Python mode `{...}` vs C mode `#{...}#` grammar actions distinction unclear in 05/06
  - pycparser migration numbers (~30% speedup, 177 conflicts) missing from 07
  - Pika error recovery advantages under-explained in 08
  - "Don't reason like EBNF" mindset warning missing from 04
  
  MEDIUM (should add):
  - `a^n b^n` simpler example alongside `a^n b^n c^n`
  - Generator vs function memory distinction in packrat
  - Tokenizer error timing (unclosed paren after parser finishes)
  - OMeta comparison in left recursion section
  - MySQL unhelpful error as contrast
  - cpp-peglib recursive call optimization note
  
  LOW (nice to have):
  - PeppaPEG Callgrind optimization story
  - Unity testing framework mention
  - Doxygen documentation extraction
  - Parser combinator framing from Pablo Bravo
  - Guile superset syntax details

## ☑ Phase 2 SKILL.md Improvements

- ☑ Task 2.1 Tighten Overview section
  - Add `a^n b^n` as simpler non-regex example alongside `a^n b^n c^n`
  - Ensure production users list is current (CPython, DuckDB v1.5, jq)
- ☑ Task 2.2 Review operator table for completeness
  - Verify all operators from Ford paper + pegen + PeppaPEG are represented
  - Check precedence values match sources
- ☑ Task 2.3 Improve minimal example
  - Ensure both right-recursive and left-recursive forms shown
  - Grammar actions example is clear

## ☑ Phase 3 reference/01-core-concepts.md Improvements

- ☑ Task 3.1 Add midpoint problem walkthrough
  (depends on: Task 1.2)
  - Positional trace showing how `S ← 'x' S 'x' / 'x'` fails on odd-length strings
  - Explain greedy matching consequence with worked example
- ☑ Task 3.2 Tighten atomic expressions
  - Add failure expression (`_` or `failure`) with usage context
  - Ensure end-of-input pattern (`!.`) is clearly explained
- ☑ Task 3.3 Review self-describing meta-grammar
  - Verify Ford's grammar matches the paper exactly
  - Ensure lexical vs syntactic separation is clear

## ☑ Phase 4 reference/02-parsing-algorithms.md Improvements

- ☑ Task 4.1 Add context manager approach discussion
  (depends on: Task 1.2)
  - TatSu-style `with self.alt()` pattern
  - Why Guido rejected it for C code generation
  - Exception-based control flow tradeoffs
- ☑ Task 4.2 Tighten packrat parsing section
  - Add generator vs function distinction for memory analysis
  - Clarify when LR and packrat have same worst-case (LISP example)
- ☑ Task 4.3 Improve tokenizer integration
  - Add tokenizer error reporting timing (unclosed paren after parser finishes)
  - Clarify lazy tokenization rationale (syntax errors before tokenizer errors)

## ☑ Phase 5 reference/03-left-recursion-and-associativity.md Improvements

- ☑ Task 5.1 Review Ford/Warth algorithm description
  (depends on: Task 1.2)
  - Ensure indirect left recursion case is clearly explained
  - Add OMeta comparison (supports full direct+indirect, loses linear time)
- ☑ Task 5.2 Tighten expression clusters section
  - Verify Autumn syntax annotations are accurate
  - Ensure @+ and @left recur semantics are clear

## ☑ Phase 6 reference/04-grammar-design-patterns.md Improvements

- ☑ Task 6.1 Add "don't reason like EBNF" warning
  (depends on: Task 1.2)
  - Key mindset shift from pegen docs
  - Ordered choice consequences are deeper than CFG intuition suggests
- ☑ Task 6.2 Tighten soft keyword section
  - Add concrete pitfalls with examples
  - Ensure pegen quote convention is clear

## ☑ Phase 7 reference/05-error-handling.md Improvements

- ☑ Task 7.1 Expand error location problem
  (depends on: Task 1.2)
  - Add Pika's bottom-up advantage for error recovery
  - MySQL unhelpful error example as contrast
- ☑ Task 7.2 Tighten semantic actions section
  - Clarify Python mode `{...}` vs C mode `#{...}#` syntax
  - Add return behavior rules (single name → auto-return, no action → dummy)
- ☑ Task 7.3 Review recovery annotations
  - Ensure DuckDB %recover pattern is clear
  - Exception-based reporting in pegen is accurate

## ☑ Phase 8 reference/06-practical-implementations.md Improvements

- ☑ Task 8.1 Expand CPython pegen section
  (depends on: Task 1.2)
  - Add specific LL(1) workarounds eliminated (namedexpr_test, with-statement continuation)
  - Add bpo-26415 memory savings from eliminating CST
  - Grammar actions: Python mode `{...}` vs C mode `#{...}#` with examples
- ☑ Task 8.2 Expand DuckDB section
  - Add "all-or-nothing" YACC behavior contrast
  - Add cpp-peglib recursive call optimization note
  - Clarify Wasm context for grammar load time
- ☑ Task 8.3 Expand LPeg section
  - Add parser combinator framing (patterns as first-class values)
  - Bytecode compilation model explained more clearly
- ☑ Task 8.4 Expand PeppaPEG section
  - Add Callgrind optimization story (10x speedup from removing inline checks)
  - Ensure all annotations (@tight/@squashed/@lifted/@spaced) have clear examples
- ☑ Task 8.5 Expand peg/leg section
  - Verify ~ error action vs @{...} inline action distinction
  - yytext access pattern is clear
- ☑ Task 8.6 Expand Guile section
  (depends on: Task 1.2)
  - Clarify superset syntax for controlling preserved information
  - Compile to lambda expressions (not bytecode/C) — emphasize this difference

## ☑ Phase 9 reference/07-peg-vs-alternatives.md Improvements

- ☑ Task 9.1 Add concrete migration numbers
  (depends on: Task 1.2)
  - pycparser: ~30% speedup, 177 reduce-reduce conflicts eliminated
  - CPython: bpo-26415 memory savings
- ☑ Task 9.2 Tighten regex comparison
  - Ensure NFA→PEG compilation approach is clear
  - Greedy behavior difference with worked example
- ☑ Task 9.3 Review pros/cons lists
  - Add parser combinator framing to advantages
  - Ensure disadvantages are balanced and current

## ☑ Phase 10 reference/08-advanced-topics.md Improvements

- ☑ Task 10.1 Expand Pika parsing section
  (depends on: Task 1.2)
  - Add error recovery advantages (bottom-up provides better context)
  - Why right-to-left naturally handles left recursion
- ☑ Task 10.2 Tighten runtime extensibility
  - Add security restriction use case (dynamically restrict grammar subsets)
  - Performance tradeoffs clearly stated
- ☑ Task 10.3 Review theory section
  - Ensure PCP reduction proof sketch is accurate
  - Open problems status current

## ☑ Phase 11 Conciseness Pass

- ☑ Task 11.1 Apply write-skill conciseness rules across all files
  (depends on: Task 3.3 , Task 4.3 , Task 5.2 , Task 6.2 , Task 7.3 , Task 8.6 , Task 9.3 , Task 10.3)
  - Challenge each paragraph: "Does the agent really need this?"
  - Remove over-explained basics (what parsers are, what ASTs are)
  - Ensure consistent terminology (one term per concept)
- ☑ Task 11.2 Cross-reference consistency check
  (depends on: Task 11.1)
  - No contradictory statements between files
  - All cross-references resolve correctly
  - Terminology consistent (e.g., always "ordered choice" not sometimes "choice operator")

## ☑ Phase 12 Final Validation & Sync

- ☑ Task 12.1 Run write-skill validation checklist
  (depends on: Task 11.2)
  - YAML header checks on SKILL.md
  - Structure checks (line counts, file naming, no chained references)
  - Content checks (no hallucination, conciseness, single recommended approach)
- ☑ Task 12.2 Regenerate README.md skills table
  (depends on: Task 12.1)
  - Run python3 misc/gen-skills-table.py

# ☑ Plan: Fix skill quality issues from re-evaluation

**Depends On:** NONE
**Created:** 2026-05-10T00:00:00Z
**Updated:** 2026-05-10T14:11:10Z
**Current Phase:** ☑ Phase 3
**Current Task:** ☑ Phase 3 - ☑ Task 3.4

## ☑ Phase 1 Fix descriptions missing "Use when" trigger (7 skills)

- ☑ Task 1.1 Fix agentmemory-0-8-9 description — add "Use when..." clause for persistent memory / semantic recall scenarios
  - Current: "Persistent memory engine for AI coding agents providing automatic cross-session context capture..."
  - Add WHEN trigger matching the skill's actual use cases
- ☑ Task 1.2 Fix changelog-1-1-0 description — add "Use when..." clause for changelog creation/maintenance scenarios
  - Current: "A skill for creating and maintaining changelogs following the Keep a Changelog specification..."
  - Add WHEN trigger
- ☑ Task 1.3 Fix esbuild-0-28-0 description — add "Use when..." clause for bundling/transformation workflows
  - Current: "Complete toolkit for esbuild v0.28 JavaScript bundler providing CLI, JavaScript API, and Go API..."
  - Add WHEN trigger
- ☑ Task 1.4 Fix mem0-1-0-11 description — add "Use when..." clause for LLM memory scenarios
  - Current: "A skill for using Mem0 v1.0.11, a universal self-improving memory layer..."
  - Add WHEN trigger
- ☑ Task 1.5 Fix mem0-2-0-1 description — add "Use when..." clause for LLM agent memory scenarios
  - Current: "A skill for using Mem0 v2.0.1, a self-improving memory layer for LLM agents..."
  - Add WHEN trigger
- ☑ Task 1.6 Fix pacote-21-5-0 description — add "Use when..." clause for npm package inspection scenarios
  - Current: "Use pacote 21.5 via npx to inspect, download, and extract npm packages..."
  - Already starts with action verb but lacks explicit "Use when" pattern
- ☑ Task 1.7 Fix sentence-transformers-5-4-1 description — add "Use when..." clause for embedding/reranking scenarios
  - Current: "Comprehensive toolkit for computing text embeddings, semantic search, and reranking..."
  - Add WHEN trigger

## ☑ Phase 2 Split oversized skills into reference files (5 skills)

- ☑ Task 2.1 Split aiohttp-sse-2-2-0 (488 lines, no refs) — create reference/ with SSE patterns, streaming examples, and advanced topics
  - Target: SKILL.md under 300 lines, move detailed API docs and examples to reference/
- ☑ Task 2.2 Split tailwindcss-browser-4-2-4 (461 lines, no refs) — create reference/ with browser build patterns, migration guide, and advanced config
  - Target: SKILL.md under 300 lines
- ☑ Task 2.3 Split tailwindcss-browser-4-2-0 (452 lines, no refs) — same split pattern as 4.2.4
  - Target: SKILL.md under 300 lines
- ☑ Task 2.4 Split aiohttp-security-0-5-0 (446 lines, no refs) — create reference/ with identity policies, authorization patterns, and JWT integration
  - Target: SKILL.md under 300 lines
- ☑ Task 2.5 Split solid-meta-0-29-0 (437 lines, no refs) — create reference/ with component API details, SSR patterns, and SEO optimization
  - Target: SKILL.md under 300 lines

## ☑ Phase 3 Validate all fixes

- ☑ Task 3.1 Run validate-all-skills.sh to confirm zero errors and warnings unchanged (depends on: Phase 1 - Task 1.7 , Phase 2 - Task 2.5)
  - Verify no new structural issues introduced by edits
- ☑ Task 3.2 Re-run description quality check to confirm all 7 descriptions now include "Use when" trigger
- ☑ Task 3.3 Re-run line-count check to confirm all 5 split skills have SKILL.md under 300 lines with reference/ directories
- ☑ Task 3.4 Regenerate README.md skills table via gen-skills-table.sh

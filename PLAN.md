# PLAN: tzip skill

## Goal
Create a minimal skill that minimizes token usage while preserving semantic meaning. Compresses input/output prose (~75% reduction) AND constrains code-generation behavior to prevent speculative, bloated output.

## Source Analysis

| Source | Key Idea | What We Keep |
|--------|----------|-------------|
| caveman `ultra` | Abbreviate, strip conjunctions, arrows for causality, one word = one word enough | Compression mechanics (drop articles/filler, use →, abbreviations) |
| Karpathy CLAUDE.md | 4 behavioral rules: Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution | **Proactive token savings** — prevent speculative code, unnecessary abstractions, and back-and-forth loops at the source. These are NOT about prose compression; they're about not generating excess tokens in the first place. |
| SPR system.md | LLM latent space priming with sparse associations | Theory: "compress to concepts, not sentences" |
| SPR unpack.md | Decompress SPR back to full prose | Symmetric decompression mechanism |

## Design Decisions

1. **Name**: `tzip` — short for "zip tokens", no version suffix (meta-pattern, not a library)
2. **Structure**: Simple skill (< 500 lines), single SKILL.md
3. **Dual-mode**: Auto-detects compression vs decompression from context
4. **Two-layer token savings**:
   - **Layer 1 (prose)**: Compress output text — drop filler, abbreviate, fragments
   - **Layer 2 (code generation)**: Prevent speculative bloat — no unrequested features, surgical diffs, verify before moving on
5. **Length target**: ~200-250 lines max

## Layer 1: Prose Compression Rules

- Drop articles (a/an/the), filler words, hedging
- Abbreviate common terms: DB/auth/config/req/res/fn/impl/state/etc.
- Strip conjunctions; use `→` for causality
- One word when one word suffices
- Technical terms exact — never abbreviate domain terminology
- Code blocks, commands, diffs: unchanged
- Fragments OK
- Pattern: `[thing] [action] [reason]. [next step].`

## Layer 2: Code Generation Constraints (from Karpathy CLAUDE.md)

**Core principle: Don't generate tokens you don't need.** Four behavioral rules that prevent speculative output at the source:

### 1. Think Before Coding
- State assumptions explicitly. If uncertain, ask.
- Surface tradeoffs — don't pick silently among multiple interpretations.
- If a simpler approach exists, say so. Push back when warranted.
- Name what's confusing before implementing.

*Token savings*: Prevents wasted commits from misinterpreting requirements. One clarifying question saves 200+ lines of wrong code.

### 2. Simplicity First
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

*Token savings*: Direct — fewer lines generated. Ask: "Would a senior engineer say this is overcomplicated?"

### 3. Surgical Changes
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- When your changes create orphans: remove only what YOUR changes made unused.
- Test: Every changed line should trace directly to the user's request.

*Token savings*: Smaller diffs, less context for follow-up turns. No "while I'm here" refactoring.

### 4. Goal-Driven Execution
- Transform tasks into verifiable goals: "Add validation" → "Write tests for invalid inputs, then make them pass"
- For multi-step tasks, state a brief plan with verification steps.
- Strong success criteria let you loop independently.

*Token savings*: Prevents back-and-forth clarification loops. Self-contained execution = fewer turns.

## Safety

Drop tzip mode for: security warnings, irreversible actions, multi-step sequences where fragments risk misread. Resume tzip after clear part done.

Example — destructive op:
> **Warning:** This will permanently delete all rows in the `users` table and cannot be undone.
> ```sql
> DROP TABLE users;
> ```
> Tzip resume. Verify backup exist first.

## Decompression Rules

- Expand abbreviations back to full terms
- Restore grammar and connectors
- Preserve all technical substance
- Output matches original intent/meaning

## File Structure

```
.agents/skills/tzip/
└── SKILL.md    # ~200 lines
```

## YAML Header (no source references in body)

```yaml
---
name: tzip
description: >
  Ultra-compressed communication mode (~75% token reduction). Compresses input/output
  while preserving full technical semantics. Includes code-generation constraints to
  prevent speculative, bloated output. Use when user requests token efficiency,
  brevity, compression, or "tzip" mode.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.2.0"
tags:
  - token-compression
  - sparse-representation
  - efficiency
category: communication
---
```

## Validation Checklist

- [x] Name `tzip` matches regex `^[a-z0-9]+(-[a-z0-9]+)*$` ✓
- [x] Description 1-1024 chars, third person, includes WHAT and WHEN
- [x] Simple skill structure (no references/)
- [ ] Line count under 500
- [ ] YAML header valid
- [ ] Bash validation passes
- [ ] Body contains zero source attributions (caveman, SPR, Karpathy names absent)

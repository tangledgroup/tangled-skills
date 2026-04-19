# PLAN: tzip skill

## Goal
Create a minimal skill that compresses LLM input/output tokens ~75% while preserving full technical semantic meaning. Acts as both SPR writer (compress) and unpacker (expand).

## Source Analysis

| Source | Key Idea | What We Keep |
|--------|----------|-------------|
| caveman `ultra` | Abbreviate, strip conjunctions, arrows for causality, one word = one word enough | Compression mechanics (drop articles/filler, use →, abbreviations) |
| Karpathy CLAUDE.md | Behavioral guidelines — simplicity, surgical changes, goal-driven execution | Code-generation token savings: no speculation, surgical diffs, verify before moving on |
| SPR system.md | LLM latent space priming with sparse associations | Theory: "compress to concepts, not sentences" |
| SPR unpack.md | Decompress SPR back to full prose | Symmetric decompression mechanism |

## Design Decisions

1. **Name**: `tzip` — short for "zip tokens", no version suffix needed (it's a meta-pattern, not a library)
2. **Structure**: Simple skill (< 500 lines), single SKILL.md
3. **Dual-mode**: Both compression and decompression in one skill (the LLM auto-detects mode from context)
4. **Code behavior layer**: Karpathy guidelines as code-generation token saver — simplicity, surgical changes, goal-driven
5. **Length target**: ~200-250 lines max

## Compression Rules

- Drop articles (a/an/the), filler words, hedging
- Abbreviate: DB/auth/config/req/res/fn/impl/state/etc.
- Strip conjunctions; use `→` for causality
- One word when one word suffices
- Technical terms exact — never abbreviate domain terminology
- Code blocks, commands, diffs: unchanged
- Fragments OK
- Pattern: `[thing] [action] [reason]. [next step].`

## Decompression Rules

- Expand abbreviations back to full terms
- Restore grammar and connectors
- Preserve all technical substance
- Output matches original intent/meaning

## Safety

Drop tzip mode for: security warnings, irreversible actions, multi-step sequences where fragments risk misread.

## Code Generation Guidelines

When tzip mode is active AND code is being generated:
- **Simplicity first** — minimum code, no speculation, push back on overengineering
- **Surgical changes** — touch only what's requested, don't refactor unrelated code
- **Goal-driven** — state success criteria, verify before moving to next step
- **No features beyond ask** — if it could be 50 lines, don't write 200

## File Structure

```
.tangled-skills/.agents/skills/tzip/
└── SKILL.md          # ~150 lines
```

## YAML Header (no source references)

```yaml
---
name: tzip
description: >
  Ultra-compressed communication mode (~75% token reduction). Compresses input/output
  while preserving full technical semantics. Use when user requests token efficiency,
  brevity, compression, or "tzip" mode. Supports compress/decompress modes automatically.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.1"
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

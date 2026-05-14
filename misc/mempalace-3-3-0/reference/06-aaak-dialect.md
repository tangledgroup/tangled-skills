# AAAK Dialect

## Overview

AAAK is a lossy abbreviation system for packing repeated entities and relationships into fewer tokens at scale. It is **readable by any LLM that reads text** (Claude, GPT, Gemini, Llama, Mistral) without a decoder — no special parsing library needed.

**Important:** AAAK is NOT the storage default. The MemPalace storage format is raw verbatim text in ChromaDB. AAAK is a separate compression layer for context loading and index summaries. It currently regresses LongMemEval vs raw mode (84.2% R@5 vs 96.6%).

## Honest Status

- **AAAK is lossy, not lossless.** It uses regex-based abbreviation, not reversible compression.
- **It does not save tokens at small scales.** Short text already tokenizes efficiently. AAAK overhead (codes, separators) costs more than it saves on a few sentences.
- **It can save tokens at scale** — in scenarios with many repeated entities (a team mentioned hundreds of times, the same project across thousands of sessions), entity codes amortize.
- **The original text cannot be reconstructed from AAAK output.** The "decode" method is just string splitting back into a dict.

## Format

```
FILE_NUM|PRIMARY_ENTITY|DATE|TITLE
ZID:ENTITIES|topic_keywords|"key_quote"|WEIGHT|EMOTIONS|FLAGS
T:ZID<->ZID|label
ARC:emotion->emotion->emotion
```

**Entity codes:** 3-letter uppercase. `ALC=Alice`, `JOR=Jordan`, `MAX=Max`.

**Emotion markers:** Abbreviated codes in asterisks. `*warm*=joy`, `*fierce*=determined`, `*raw*=vulnerable`, `*bloom*=tenderness`.

**Structure:** Pipe-separated fields. `FAM:` family | `PROJ:` projects | `⚠:` warnings/reminders.

**Importance:** Star scale `★` to `★★★★★` (1-5).

## Emotion Codes

Universal emotion codes detected by keyword matching:

- `vul` — vulnerability
- `joy` — joy
- `fear` — fear
- `trust` — trust
- `grief` — grief
- `wonder` — wonder
- `rage` — anger/anger
- `love` — love/devotion
- `hope` — hope
- `despair` — despair/hopelessness
- `peace` — peace
- `relief` — relief
- `humor` — humor/dark humor
- `tender` — tenderness
- `raw` — raw honesty/brutal honesty
- `doubt` — self-doubt
- `anx` — anxiety
- `exhaust` — exhaustion
- `convict` — conviction
- `passion` — quiet passion
- `warmth`, `curious`, `grat` (gratitude), `frust` (frustration), `confuse`, `satis` (satisfaction), `excite`, `determ` (determination), `surprise`

## Flags

Flags signal special content types detected by keyword patterns:

- `ORIGIN` — origin moment (birth of something)
- `CORE` — core belief or identity pillar
- `SENSITIVE` — handle with absolute care
- `PIVOT` — emotional turning point
- `GENESIS` — led directly to something existing
- `DECISION` — explicit decision or choice
- `TECHNICAL` — technical architecture or implementation detail

## How AAAK Generation Works

The `dialect.py` module is entirely deterministic (no LLM):

1. **Entity detection:** Known name-to-code mappings, or first 3 characters of capitalized words
2. **Topic extraction:** Word frequency + proper noun boosting, top 3 topics
3. **Key sentence selection:** Decision-keyword scoring, truncated at 55 chars
4. **Emotion detection:** Keyword → abbreviated emotion code lookup
5. **Flag detection:** Keyword → flag label

Stop words are stripped from topic extraction. Code lines are stripped before scoring.

## Example

```
FAM: ALC→♡JOR | 2D(kids): RIL(18,sports) MAX(11,chess+swimming) | BEN(contributor)
PROJ: ORION|auth-migration|"switched to Clerk over Auth0"|convict|DECISION
```

When reading AAAK: expand codes mentally, treat `*markers*` as emotional context.

## Token Counting

The dialect uses `len(text) // 3` as a heuristic for token estimation — not real tokenization. Actual token counts will vary by model. The "~30x compression" claim from early documentation was based on this approximation and has been corrected.

## When to Use AAAK

- Context loading where entity repetition is high (same names across many sessions)
- Diary entries for specialist agents
- Compact summaries where approximate content is acceptable
- Token-constrained system prompts

## When Not to Use AAAK

- When verbatim accuracy matters (use raw drawers instead)
- Short text (AAAK overhead costs more than it saves)
- Retrieval-critical indexing (raw mode scores 96.6% vs AAAK's 84.2%)

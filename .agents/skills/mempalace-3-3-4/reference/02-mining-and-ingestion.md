# Mining and Ingestion

## Overview

MemPalace ingests data through two primary modes: **project mining** (code, docs, notes) and **conversation mining** (Claude, ChatGPT, Slack exports). Both produce verbatim drawers in the palace.

## Project Mining

```bash
mempalace mine ~/projects/my_app
```

Walks the directory recursively. Room assignment uses a 4-priority cascade:

1. Folder path segment matches a room name
2. Filename stem matches a room name
3. Keyword frequency scoring in first 2000 chars
4. Fallback to `general`

Chunking: 800 chars per chunk, 100 char overlap, paragraph-then-line boundary splitting. Chunks under 50 chars are discarded.

Supported extensions: `.txt`, `.md`, `.markdown`, `.py`, `.js`, `.ts`, `.html`, `.rst`, `.adoc`, `.yaml`, `.yml`, `.json`, `.toml`, `.ini`, `.cfg`, `.sh`, `.bash`, `.c`, `.h`, `.cpp`, `.rs`, `.go`.

Skipped: Binary files, hidden files/directories (unless explicitly requested), `.git/` and other version control directories.

Deduplication: File-level only — if any drawer exists with the same `source_file`, the entire file is skipped. Re-mining modified files purges old drawers first.

Options:

- `--wing <name>` — override wing detection
- `--agent <name>` — tag drawers as added by a specialist agent
- `--limit N` — max files to process
- `--dry-run` — preview without writing
- `--no-gitignore` — include `.gitignore`d files
- `--include-ignored a,b,c` — comma-separated paths to include despite gitignore

## Conversation Mining

```bash
mempalace mine ~/chats/claude-sessions --mode convos
mempalace mine ~/exports/slack/ --mode convos --wing driftwood
```

Detects transcript format automatically (Claude Code JSONL, ChatGPT export, Slack export, Claude.ai privacy export). Creates day-based rooms for conversation transcripts.

Before mining mega-files that concatenate multiple sessions into one file, split them first:

```bash
mempalace split ~/chats/                    # split into per-session files
mempalace split ~/chats/ --dry-run          # preview first
mempalace split ~/chats/ --min-sessions 3   # only split files with 3+ sessions
```

General extraction mode classifies content into categories:

```bash
mempalace mine ~/chats/ --mode convos --extract general
```

Categories: decisions, milestones, problems, preferences, emotional context. Uses regex-based scoring — no LLM required.

## Sweeper (v3.3.2+)

A message-level, timestamp-coordinated, idempotent safety net that catches anything the primary miner missed:

```bash
mempalace sweep ~/chats/claude-sessions/    # run sweeper on transcript directory
mempalace sweep ~/chats/session.jsonl       # run sweeper on single file
```

## Entity Detection

The `init` command auto-detects people and projects from file content:

```bash
mempalace init ~/projects/myapp
```

Two-pass process:

1. Scan files for entity mentions (names, project identifiers)
2. Detect rooms from folder structure

Detected entities are saved to `<project>/entities.json` for the miner to use. Use `--yes` to skip interactive confirmation.

Canonical project names come from package manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`) and real people from git commit authors. Union-find dedup across name/email aliases with bot filtering.

### LLM-Assisted Refinement (v3.3.3+)

Optional `--llm` flag for LLM-assisted entity classification. Defaults to local Ollama (zero-API); also supports OpenAI-compatible endpoints and Anthropic Messages API. Runs interactively with progress indicator; Ctrl-C cancels cleanly with partial results. Useful for prose-heavy folders where regex detector struggles.

**v3.3.4:** LLM-assisted refinement now runs by default during `init`. Graceful fallback to heuristic-only if no LLM provider is reachable. Use `--no-llm` to explicitly opt out.

### Multi-Language Entity Detection (v3.3.1+)

Lexical patterns live in locale JSON under `mempalace/i18n/<lang>.json`. Supported locales: en, pt-br, ru, it, hi, id, be, de, es, fr, zh-hans, zh-hant. Configure via `MEMPALACE_ENTITY_LANGUAGES` env var, `MempalaceConfig.entity_languages`, or `mempalace init --lang en,pt-br`.

## Context-Aware Corpus Detection (v3.3.4)

Pass 0 runs before entity detection during `init`, answering: *is this corpus an AI-dialogue record, and if so, which platform and what persona names has the user assigned to the agents?*

- **Tier 1:** Free regex heuristic (AI brand terms + turn-marker patterns, with co-occurrence rules to suppress ambiguous terms)
- **Tier 2:** LLM call (~$0.01 Anthropic Haiku, free with local Ollama) extracts `user_name` and `agent_persona_names`

Result persists to `<palace>/.mempalace/origin.json` with `schema_version: 1`. Agent personas route to a new `agent_personas` bucket instead of `people`, preventing misclassification.

Re-run detection on grown corpora:

```bash
mempalace mine --redetect-origin ~/projects/myapp
```

## Auto-Mine On Init (v3.3.4)

After entity confirmation, room detection, and gitignore guard, `mempalace init` shows a scope estimate then asks `Mine this directory now? [Y/n]`. Declining prints the exact `mempalace mine <dir>` command for later.

For non-interactive paths:

```bash
mempalace init --auto-mine ~/projects/myapp   # skips prompt, mines directly
mempalace init --yes --auto-mine ~/projects/myapp  # fully non-interactive
```

## Cross-Wing Topic Tunnels (v3.3.4)

When two wings share confirmed `TOPIC` labels (from LLM-refine), the miner creates symmetric tunnels at mine time. Configurable via `MEMPALACE_TOPIC_TUNNEL_MIN_COUNT` env var or `topic_tunnel_min_count` in `~/.mempalace/config.json` (default 1). Tunnels are tagged `kind: "topic"` and stored under synthetic `topic:<name>` rooms to avoid collision with literal folder-derived rooms.

## Noise Stripping

Before filing drawers, MemPalace strips system tags, hook output, and Claude UI chrome from content. The `strip_noise` function is scoped to Claude Code JSONL only — other formats are stored verbatim.

## Re-mining

When a file is re-mined (content changed or `NORMALIZE_VERSION` bumped), the miner:

1. Purges every closet for that source file (`purge_file_closets`)
2. Writes a fresh set of drawers and closets

Stale topics from the prior mine are removed. Closets are always a snapshot of current content, never an accumulation across runs.

## File-Level Locking

A `mine_lock` prevents duplicate drawers when agents mine the same file concurrently. PID file guard prevents process stacking that bloats HNSW. Cross-platform PID liveness check included.

## Graceful Interrupt (v3.3.4)

Ctrl-C during `mempalace mine` prints progress summary (`files_processed: N/M`, `drawers_filed: K`, `last_file:`) and exits with code 130. Already-filed drawers are upserted idempotently on re-mine via deterministic IDs.

## Diary Ingest

Specialist agents write to their own diary (day-based rooms) in the palace:

```python
mempalace_diary_write("reviewer",
    "PR#42|auth.bypass.found|missing.middleware.check|pattern:3rd.time.this.quarter|★★★★")

mempalace_diary_read("reviewer", last_n=10)
```

Each agent has its own wing and diary — not shared. Diary entries use microsecond timestamps and full content hash to prevent ID collisions. Per-project wing derivation from Claude Code transcript path supported since v3.3.3.

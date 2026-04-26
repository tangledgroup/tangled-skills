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

## Entity Detection

The `init` command auto-detects people and projects from file content:

```bash
mempalace init ~/projects/myapp
```

Two-pass process:

1. Scan files for entity mentions (names, project identifiers)
2. Detect rooms from folder structure

Detected entities are saved to `<project>/entities.json` for the miner to use. Use `--yes` to skip interactive confirmation.

## Noise Stripping

Before filing drawers, MemPalace strips system tags, hook output, and Claude UI chrome from content. The `strip_noise` function is scoped to Claude Code JSONL only — other formats are stored verbatim.

## Re-mining

When a file is re-mined (content changed or `NORMALIZE_VERSION` bumped), the miner:

1. Purges every closet for that source file (`purge_file_closets`)
2. Writes a fresh set of drawers and closets

Stale topics from the prior mine are removed. Closets are always a snapshot of current content, never an accumulation across runs.

## File-Level Locking

A `mine_lock` prevents duplicate drawers when agents mine the same file concurrently. Critical sections are serialized.

## Diary Ingest

Specialist agents write to their own diary (day-based rooms) in the palace:

```python
mempalace_diary_write("reviewer",
    "PR#42|auth.bypass.found|missing.middleware.check|pattern:3rd.time.this.quarter|★★★★")

mempalace_diary_read("reviewer", last_n=10)
```

Each agent has its own wing and diary — not shared. Diary entries use microsecond timestamps and full content hash to prevent ID collisions.

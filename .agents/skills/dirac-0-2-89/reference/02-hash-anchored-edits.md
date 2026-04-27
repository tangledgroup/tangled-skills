# Hash-Anchored Edits

## The Problem With Search-and-Replace

Traditional coding agents use search-and-replace or unified diff for edits. Claude's `replace_in_file` requires the model to emit the full old text (`S`) plus new text (`R`), giving O(S+R) output token complexity. OpenAI's `apply_patch` similarly requires both sides of the diff. The larger the unchanged search block, the higher the probability of the model making a single-character mistake that causes the entire tool call to fail — forcing a complete regeneration.

Dirac reduces output complexity to O(R) by using **stable anchors** that pinpoint lines without requiring the model to repeat their content.

## How It Works

### The § Delimiter

Dirac uses `§` (U+00A7, section sign) as the delimiter between anchor and code content:

```
Moderator§def complex_payment_processor(transaction_data):
Qualifier§    logger.info("Starting processing")
...
Ripple§    logger.info("Payment successful")
Corona§    return {"status": "success"}
```

The model reads files with these anchors prepended to each line. When proposing an edit, it references only the anchor name and the line content:

```json
{
  "edit_type": "replace",
  "anchor": "Moderator§def complex_payment_processor(transaction_data):",
  "end_anchor": "Corona§    return {\"status\": \"success\"}",
  "text": "def complex_payment_processor(transaction_data, strict_mode=True):\n    ...\n    return {\"status\": \"success\", \"strict\": True}"
}
```

### Three Edit Types

- **`insert_after`** — Insert new text after the anchored line (requires `anchor` only)
- **`insert_before`** — Insert new text before the anchored line (requires `anchor` only)
- **`replace`** — Replace a range from `anchor` to `end_anchor` with new text

### EditExecutor Validation

The `EditExecutor.resolveAnchor()` method performs four checks:

1. **Format check**: Anchor name must match `/^[A-Z][a-zA-Z]*$/` (capital letter start, letters only)
2. **Existence check**: Anchor name must exist in the file's current anchor list
3. **No newlines**: The provided code line must be a single line
4. **Content match**: The provided code line must exactly match the file's actual content at that anchor's position

If any check fails, the edit is rejected with a diagnostic message explaining what went wrong.

## AnchorStateManager — The State Machine

The `AnchorStateManager` in `src/utils/AnchorStateManager.ts` is the heart of the system. It maintains task-scoped maps of every file that has been read, tracking which anchor word corresponds to which line.

### Key Properties

- **MAX_TRACKED_LINES**: 50,000 lines per file (files exceeding this fall back to `L1`, `L2`, ... line numbers)
- **MAX_TRACKED_FILES**: 1,024 files per task
- **MAX_TRACKED_TASKS**: 50 tasks (LRU eviction)

### Anchor Dictionary

Dirac ships with ~1,700 single-word, single-token anchors derived from `tiktoken.get_encoding("o200k_base")`. These are stored in `.hash_anchors` and loaded lazily. Examples: `Apple`, `Brave`, `Cider`, `Bison`, `Fox`, `Moderator`, `Qualifier`, `Ripple`, `Corona`.

When the single-word pool is exhausted, the state manager generates two-word combinations (e.g., `AppleBrave`) and, in extreme cases, three-word combinations. All anchors are guaranteed unique within a file's scope.

### Reconciliation via Myers Diff

The `reconcile()` method is called every time a file is read or after edits are applied:

1. **Fast path**: Compute FNV-1a hashes for all current lines. If identical to the tracked state, return existing anchors immediately — no work needed.

2. **First-time files**: Assign unique random words from the dictionary pool to every line.

3. **Changed files**: Run Myers Diff on the **integer hash arrays** (not strings) between old and new content:
   - **Unchanged lines**: Carry over the exact same word anchor
   - **Added lines**: Get fresh unique words from the pool
   - **Deleted lines**: Advance the old index, anchors become available for reuse

This means a 5-line change at the top of a 2,000-line file only requires re-anchoring those 5 lines — the remaining 1,995 lines keep their original anchors. This is the key advantage over line-number-based systems where any insertion shifts all subsequent line numbers.

### FNV-1a Hashing

Content hashing uses the FNV-1a algorithm for high performance:

```typescript
let h = 2166136261  // FNV-1a offset basis
for each char:
    h = Math.imul(h ^ charCode, 16777619)  // FNV-1a prime
return (h >>> 0).toString(16).padStart(8, "0")
```

Hashes are stored as `Uint32Array` for memory efficiency and compared as integers in the Myers Diff.

## BatchProcessor — Multi-File Edit Pipeline

The `BatchProcessor` in `src/core/task/tools/handlers/edit-file/BatchProcessor.ts` orchestrates multi-file edits:

1. **Group blocks by path**: All `edit_file` tool calls in a single LLM turn are grouped by target file
2. **Validate and prepare**: Read each file, reconcile anchors, resolve edit anchors to line indices
3. **Apply in memory**: Sort edits by line index (descending) and splice replacements
4. **Generate diff**: Unified diff format for the approval UI
5. **Request approval**: Combined approval prompt showing all files and edits
6. **Capture pre-save diagnostics**: Run linters before saving to detect existing issues
7. **Apply and save**: Sequentially save each file (to avoid UI conflicts), capturing auto-formatting changes
8. **Run post-save diagnostics**: Parallel linting across all successfully saved files
9. **Format results**: Return updated anchors with diagnostic feedback

## Token Efficiency Results

| Metric | Search-and-Replace | Hash-Anchored |
|--------|-------------------|---------------|
| Output complexity | O(S+R) | O(R) |
| Anchor overhead per line | None (full text repeated) | ~2 tokens (anchor + §) |
| Cascading invalidation | Every edit shifts positions | Only changed lines re-anchored |
| Avg cost per task | $0.49 (across agents) | $0.18 (Dirac) |

The 64.8% cost reduction comes primarily from eliminating the need to repeat unchanged code in output tokens, which are 5-6x more expensive than input tokens and 50-60x more expensive than cached read tokens.

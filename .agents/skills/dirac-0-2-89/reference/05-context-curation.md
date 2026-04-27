# Context Curation

## The Core Philosophy

Dirac's fundamental premise: **model reasoning ability degrades with context length**. By keeping context tightly curated — only what the LLM actually needs — Dirac improves both accuracy and cost while making larger changes tractable in single tasks.

Output tokens cost 5-6x more than input tokens, and 50-60x more than cached read tokens. Therefore, minimizing both input context and output repetition is the primary optimization target.

## ContextLoader

The `ContextLoader` (`src/core/task/ContextLoader.ts`) extracts contextual information from user prompts to auto-enrich the conversation:

### Extraction Pipeline

1. **Scrub code fences and URLs** — Prevent false positives in path/symbol matching
2. **Strip mentions** — Remove `@file`, `@symbol` style mentions (handled separately)
3. **Strip slash commands** — Remove `/newtask`, `/smol` etc. from the text being analyzed
4. **Extract file paths** — Regex matches against workspace files, validates existence via `fs.stat`
5. **Extract directory paths** — Same regex, checks for directories
6. **Extract symbol names** — Identifies function/class/method names that might refer to code symbols

### Auto-Symbol Enrichment

When the user mentions a symbol name (e.g., "fix the `DynamicCache.update` method"), Dirac:

1. Queries the `SymbolIndexService` for matching definitions
2. If ≤ 3 matches found and total lines ≤ 20, auto-includes them in context
3. Uses `ASTAnchorBridge.getFunctions()` to retrieve the function with anchors

Thresholds are configurable:
- `MAX_AUTO_SYMBOL_MATCHES`: 3
- `MAX_AUTO_SYMBOL_TOTAL_LINES`: 20
- `MAX_AUTO_SYMBOL_LINE_LENGTH_BYTES`: 200

## Context Condensation

### The condense Tool

When conversation history grows too large, Dirac can proactively suggest condensing the context. The `CondenseHandler` (`src/core/task/tools/handlers/CondenseHandler.ts`):

1. LLM generates a `condense` tool call with a summary context
2. User is shown the proposed summary and can provide feedback
3. If accepted, conversation history is truncated using the `ContextManager.getNextTruncationRange()` method
4. Truncation strategy: `"lastTwo"` if a summary was already appended, `"none"` otherwise

### The /smol Slash Command

Users can manually trigger context condensation with `/smol`. This is useful when the conversation has grown long and the user wants to save tokens without waiting for the LLM to suggest it.

## File Skeletons vs Full Reads

Dirac prefers file skeletons over full file reads whenever possible:

- **File skeleton** (`get_file_skeleton`): Returns only AST definition lines with anchors — typically 5-20 lines for a 500-line file. ~2 tokens per anchor prefix.
- **Full read** (`read_file`): Returns all lines with anchors — necessary when the LLM needs to see implementation details.

The system prompt guides the LLM to use skeletons first, then full reads only when needed for specific sections.

## Conversation History Management

Dirac tracks `conversationHistoryDeletedRange` to know which parts of the API conversation history have been truncated. This ensures the LLM doesn't reference deleted context and allows proper message indexing across condensation events.

The `ApiConversationManager` handles:
- Message state persistence
- Truncation range tracking
- History reconstruction after condensation
- Checkpoint-based message timestamps

## Skills and Rules Context

Dirac loads contextual instructions from:

- **Skills**: `.agents/skills/` directories with `SKILL.md` files — discovered via `getOrDiscoverSkills()`
- **Dirac Rules**: User-defined project-specific or global rules — loaded from `.dirac/rules/`
- **Rule conditionals**: Rules can have conditions (file paths, symbol patterns) that control when they apply

The `extractSymbolLikeStrings()` function in `rule-conditionals.ts` identifies code-relevant strings in user prompts for conditional rule matching.

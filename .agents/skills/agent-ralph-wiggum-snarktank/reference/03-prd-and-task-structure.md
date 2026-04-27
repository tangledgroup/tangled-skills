# PRD and Task Structure

## Product Requirements Documents (PRDs)

The PRD is the specification that drives Ralph. It defines what to build, broken into small, verifiable user stories. The PRD goes through two formats: first a Markdown document (created interactively), then a JSON file (`prd.json`) for machine consumption by Ralph.

## Creating a PRD

Ralph ships with a PRD generation skill that guides you through creating a structured requirements document.

### The Process

1. Invoke the PRD skill in Amp or Claude Code:
   ```
   Load the prd skill and create a PRD for [your feature description]
   ```
2. Answer 3-5 clarifying questions (presented with lettered options)
3. The skill generates a structured Markdown PRD
4. Save to `tasks/prd-[feature-name].md`

### Clarifying Questions

The skill asks focused questions to resolve ambiguity:

```
1. What is the primary goal of this feature?
   A. Improve user onboarding experience
   B. Increase user retention
   C. Reduce support burden
   D. Other: [please specify]

2. Who is the target user?
   A. New users only
   B. Existing users only
   C. All users
   D. Admin users only
```

Users respond with shorthand: "1A, 2C, 3B" for quick iteration.

### PRD Structure

The generated Markdown PRD includes:

1. **Introduction/Overview** — Brief description of the feature and problem it solves
2. **Goals** — Specific, measurable objectives
3. **User Stories** — Each with title, description, and acceptance criteria
4. **Functional Requirements** — Numbered list (FR-1, FR-2, etc.)
5. **Non-Goals** — What the feature will NOT include (critical for scope management)
6. **Design Considerations** — UI/UX requirements, existing components to reuse
7. **Technical Considerations** — Known constraints, integration points
8. **Success Metrics** — How success will be measured
9. **Open Questions** — Remaining areas needing clarification

### Writing for Junior Developers

The PRD reader may be a junior developer or AI agent. Therefore:

- Be explicit and unambiguous
- Avoid jargon or explain it
- Provide enough detail to understand purpose and core logic
- Number requirements for easy reference
- Use concrete examples where helpful

## Converting PRD to prd.json

After creating the Markdown PRD, convert it to Ralph's JSON format:

```
Load the ralph skill and convert tasks/prd-[feature-name].md to prd.json
```

This creates `prd.json` in the Ralph scripts directory with user stories structured for autonomous execution.

## prd.json Format

```json
{
  "project": "MyApp",
  "branchName": "ralph/task-priority",
  "description": "Task Priority System - Add priority levels to tasks",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add priority field to database",
      "description": "As a developer, I need to store task priority so it persists across sessions.",
      "acceptanceCriteria": [
        "Add priority column to tasks table: 'high' | 'medium' | 'low' (default 'medium')",
        "Generate and run migration successfully",
        "Typecheck passes"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

### Top-Level Fields

- `project` — Project name (used for context)
- `branchName` — Git branch to create/use for this feature (prefixed with `ralph/`)
- `description` — Feature description derived from PRD title/intro

### User Story Fields

- `id` — Sequential identifier (US-001, US-002, etc.)
- `title` — Short descriptive name for the story
- `description` — "As a [user], I want [feature] so that [benefit]"
- `acceptanceCriteria` — Array of verifiable conditions
- `priority` — Execution order (lower number = executed first)
- `passes` — Boolean flag; `false` initially, set to `true` when Ralph completes the story
- `notes` — Free-form notes (empty initially, may be populated during execution)

## Story Sizing: The Number One Rule

**Each story must be completable in ONE Ralph iteration (one context window).**

This is the most critical rule. Ralph spawns a fresh AI instance per iteration with no memory of previous work. If a story is too big, the LLM runs out of context before finishing and produces broken code.

### Right-Sized Stories

These fit comfortably in one context window:

- Add a database column and migration
- Add a UI component to an existing page
- Update a server action with new logic
- Add a filter dropdown to a list
- Implement a single API endpoint

### Too Big (Split These)

- "Build the entire dashboard" — Split into: schema, queries, UI components, filters
- "Add authentication" — Split into: schema, middleware, login UI, session handling
- "Refactor the API" — Split into one story per endpoint or pattern

**Rule of thumb:** If you cannot describe the change in 2-3 sentences, it is too big.

### Example: Splitting a Large Feature

**Original (too big):**
> "Add user notification system"

**Split into:**
1. US-001: Add notifications table to database
2. US-002: Create notification service for sending notifications
3. US-003: Add notification bell icon to header
4. US-004: Create notification dropdown panel
5. US-005: Add mark-as-read functionality
6. US-006: Add notification preferences page

Each is one focused change that can be completed and verified independently.

## Story Ordering: Dependencies First

Stories execute in priority order. Earlier stories must not depend on later ones.

### Correct Dependency Order

1. Schema/database changes (migrations)
2. Server actions / backend logic
3. UI components that use the backend
4. Dashboard/summary views that aggregate data

### Wrong Order

1. UI component (depends on schema that doesn't exist yet)
2. Schema change

The Ralph converter skill enforces this ordering when converting from Markdown PRD to JSON.

## Acceptance Criteria: Must Be Verifiable

Each criterion must be something Ralph can **check**, not something vague. Ralph needs binary pass/fail conditions.

### Good Criteria (Verifiable)

- "Add `status` column to tasks table with default 'pending'"
- "Filter dropdown has options: All, Active, Completed"
- "Clicking delete shows confirmation dialog"
- "Typecheck passes"
- "Tests pass"
- "Verify in browser using dev-browser skill"

### Bad Criteria (Vague)

- "Works correctly"
- "User can do X easily"
- "Good UX"
- "Handles edge cases"

### Mandatory Criteria

Always include as the final criterion:

```
"Typecheck passes"
```

For stories with testable logic, also include:

```
"Tests pass"
```

For stories that change UI, always include:

```
"Verify in browser using dev-browser skill"
```

Frontend stories are NOT complete until visually verified. Ralph uses the dev-browser skill to navigate to the page, interact with the UI, and confirm changes work.

### Explicit Criteria Examples

**Vague:**
> "Users can log in"

**Explicit:**
- Email/password fields present on login page
- Validates email format before submission
- Shows error message on authentication failure
- Redirects to dashboard on success
- Typecheck passes
- Verify at localhost:$PORT/login (PORT defaults to 3000)

## Conversion Rules

When converting a Markdown PRD to prd.json:

1. Each user story becomes one JSON entry
2. IDs are sequential (US-001, US-002, etc.)
3. Priority is based on dependency order, then document order
4. All stories start with `passes: false` and empty `notes`
5. `branchName` is derived from feature name, kebab-case, prefixed with `ralph/`
6. Always add "Typecheck passes" to every story's acceptance criteria

## Archiving Previous Runs

Before writing a new prd.json, check if there is an existing one from a different feature:

1. Read the current `prd.json` if it exists
2. Check if `branchName` differs from the new feature's branch name
3. If different AND `progress.txt` has content beyond the header:
   - Create archive folder: `archive/YYYY-MM-DD-feature-name/`
   - Copy current `prd.json` and `progress.txt` to archive
   - Reset `progress.txt` with fresh header

The ralph.sh script handles this automatically when you run it, but if manually updating prd.json between runs, archive first.

## Validation Checklist

Before saving prd.json:

- Previous run archived (if prd.json exists with different branchName)
- Each story is completable in one iteration (small enough)
- Stories are ordered by dependency (schema → backend → UI)
- Every story has "Typecheck passes" as criterion
- UI stories have "Verify in browser using dev-browser skill" as criterion
- Acceptance criteria are verifiable (not vague)
- No story depends on a later story

## Complete Example

Feature: Task Priority System

```json
{
  "project": "TaskApp",
  "branchName": "ralph/task-priority",
  "description": "Task Priority System - Add priority levels to tasks",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add priority field to database",
      "description": "As a developer, I need to store task priority so it persists across sessions.",
      "acceptanceCriteria": [
        "Add priority column to tasks table: 'high' | 'medium' | 'low' (default 'medium')",
        "Generate and run migration successfully",
        "Typecheck passes"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-002",
      "title": "Display priority indicator on task cards",
      "description": "As a user, I want to see task priority at a glance.",
      "acceptanceCriteria": [
        "Each task card shows colored priority badge (red=high, yellow=medium, gray=low)",
        "Priority visible without hovering or clicking",
        "Typecheck passes",
        "Verify in browser using dev-browser skill"
      ],
      "priority": 2,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-003",
      "title": "Add priority selector to task edit",
      "description": "As a user, I want to change a task's priority when editing it.",
      "acceptanceCriteria": [
        "Priority dropdown in task edit modal",
        "Shows current priority as selected",
        "Saves immediately on selection change",
        "Typecheck passes",
        "Verify in browser using dev-browser skill"
      ],
      "priority": 3,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-004",
      "title": "Filter tasks by priority",
      "description": "As a user, I want to filter the task list to see only high-priority items.",
      "acceptanceCriteria": [
        "Filter dropdown with options: All | High | Medium | Low",
        "Filter persists in URL params",
        "Empty state message when no tasks match filter",
        "Typecheck passes",
        "Verify in browser using dev-browser skill"
      ],
      "priority": 4,
      "passes": false,
      "notes": ""
    }
  ]
}
```

This example demonstrates proper dependency ordering (database first, then UI), right-sized stories, verifiable criteria, and browser verification for frontend changes.

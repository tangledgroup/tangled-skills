# The Ralph Loop Methodology

Core concepts, workflow mechanics, and completion verification for autonomous AI development.

## Core Principles

### 1. Iterative Self-Correction

Each loop iteration:
1. Picks ONE task/spec to work on
2. Implements it completely
3. Verifies acceptance criteria
4. Commits and pushes changes
5. Outputs `<promise>DONE</promise>` only when 100% complete

### 2. Fresh Context Each Loop

Every iteration starts with a **clean context window**. This prevents:
- Context overflow from previous iterations
- Confusion from accumulated conversation history
- Degraded performance over time

Shared state persists via files on disk (specs, IMPLEMENTATION_PLAN.md, constitution).

### 3. Spec-Driven Development

Professional specifications with:
- Clear feature requirements
- **Testable acceptance criteria** (not "works correctly" but specific verifiable conditions)
- Completion signal section with checklist

### 4. Magic Phrase Verification

The agent outputs `<promise>DONE</promise>` **ONLY** when:
- All acceptance criteria are verified
- Tests pass
- Changes are committed and pushed

The bash loop checks for this phrase. If not found, it retries the iteration.

## Work Sources (Priority Order)

Ralph picks work from these sources in order:

### 1. IMPLEMENTATION_PLAN.md (If Exists)

A detailed task breakdown created by planning mode. Ralph picks the highest priority incomplete task.

**When to use:** Complex projects needing detailed breakdown before implementation.

### 2. specs/ Folder (Default)

Ralph picks the highest priority incomplete spec directly from the `specs/` folder.

**Priority:** Lower number = higher priority (001- before 100-)

**Status detection:** A spec is complete if it contains:
```markdown
Status: COMPLETE
## Status: COMPLETE
**Status**: COMPLETE
```

Any other status (Draft, TODO, In Progress, or missing) means INCOMPLETE.

**When to use:** Most projects work fine directly from specs without planning mode.

## The Ralph Loop Workflow

### Phase 1: Orientation

1. Read `.specify/memory/constitution.md` - Core principles and workflow instructions
2. Check for `IMPLEMENTATION_PLAN.md` or scan `specs/` folder
3. Identify highest priority incomplete work item
4. Read the spec/task details and acceptance criteria

### Phase 2: Implementation

1. Implement the feature according to spec requirements
2. Follow constitution principles (YOLO mode, git autonomy)
3. Use available tools (MCP servers, git, testing frameworks)
4. Make incremental progress with meaningful commits

### Phase 3: Verification

1. Run all tests specified in acceptance criteria
2. Verify each checklist item in Completion Signal section
3. Check for console errors, visual issues, functionality gaps
4. Ensure changes meet all requirements

### Phase 4: Commit and Push

1. Commit changes with meaningful message
2. Push to remote repository
3. Update history.md with one-line summary (if required)
4. Create detailed history file in `history/YYYY-MM-DD--spec-name.md`

### Phase 5: Completion Signal

**ONLY if all verification passes:**
```
<promise>DONE</promise>
```

**If ALL specs are complete:**
```
<promise>ALL_DONE</promise>
```

The bash loop detects these signals and either continues to next iteration or stops.

## Two Modes

### Build Mode (Default)

**Purpose:** Pick spec/task, implement, test, commit, push

**Commands:**
```bash
./scripts/ralph-loop.sh           # Unlimited iterations
./scripts/ralph-loop.sh 20        # Max 20 iterations
./scripts/ralph-loop-codex.sh     # Use Codex CLI
./scripts/ralph-loop-gemini.sh    # Use Gemini CLI
./scripts/ralph-loop-copilot.sh   # Use Copilot CLI
```

**What happens:**
1. Loop starts, reads constitution
2. Picks highest priority incomplete spec
3. Agent implements, tests, verifies
4. If `<promise>DONE</promise>` detected: next iteration (fresh context)
5. If no signal: retry same task
6. Stops when all specs complete or max iterations reached

### Planning Mode (Optional)

**Purpose:** Create detailed task breakdown from specs

**Command:**
```bash
./scripts/ralph-loop.sh plan
```

**What happens:**
1. Agent studies all specs in `specs/`
2. Performs gap analysis against current codebase
3. Creates or updates `IMPLEMENTATION_PLAN.md` with prioritized tasks
4. Does NOT implement anything
5. Outputs `<promise>DONE</promise>` when plan is complete

**After planning:**
- Run `./scripts/ralph-loop.sh` to start building from the plan
- Or delete `IMPLEMENTATION_PLAN.md` to work directly from specs

## NR_OF_TRIES Tracking

Each spec tracks attempt count to detect stuck tasks:

### How It Works

```bash
# Counter stored as comment in spec file
<!-- NR_OF_TRIES: 5 -->
```

### Checking Stuck Specs

```bash
source scripts/lib/nr_of_tries.sh
print_stuck_specs_summary
```

Output:
```
⚠️ Stuck Specs (>= 10 attempts):
  - specs/004-dashboard/spec.md (12 attempts)
  - specs/007-payments/spec.md (11 attempts)

Consider splitting these specs into smaller, more achievable tasks.
```

### Actions for Stuck Specs

After 10+ attempts:
1. **Split the spec** - Break into smaller, more focused specs
2. **Clarify acceptance criteria** - Make them more specific and testable
3. **Fix blocking issues** - Manual intervention may be needed
4. **Reset counter** - After fixing: `reset_nr_of_tries "specs/NNN-feature/spec.md"`

## Circuit Breaker

Prevents runaway loops by detecting stagnation.

### States

| State | Meaning | Action |
|-------|---------|--------|
| CLOSED | Normal operation | Continue execution |
| HALF_OPEN | Monitoring mode | Watching for progress |
| OPEN | Failure detected | Halt execution |

### Triggers

Circuit opens after:
- 5 consecutive loops with no file changes
- 3 consecutive loops with same error

### Circuit Breaker Commands

```bash
# Check status
show_circuit_status

# Reset manually (after fixing issues)
reset_circuit_breaker "Fixed blocking issue"

# Continue with reset flag
./scripts/ralph-loop.sh --reset-circuit
```

### When Circuit Opens

The loop halts and displays:
```
🚨 CIRCUIT BREAKER OPENED: No progress in 5 consecutive loops

Possible reasons:
  • Task may be complete
  • Agent may be stuck on an error
  • Prompt needs clarification

To continue:
  1. Review logs
  2. Fix any issues
  3. Reset circuit breaker: --reset-circuit
```

## Autonomy Settings

### YOLO Mode

**ENABLED (Recommended):** Execute commands, modify files, run tests without asking each time.

**DISABLED:** Agent asks for approval before executing commands.

Set in constitution:
```markdown
YOLO Mode: ENABLED
```

The loop script auto-detects this setting and adds `--dangerously-skip-permissions` flag accordingly.

### Git Autonomy

**ENABLED (Recommended):** Commit and push automatically after each spec completion.

**DISABLED:** Agent creates commits but doesn't push; manual push required.

Set in constitution:
```markdown
Git Autonomy: ENABLED
```

## Completion Signals

### Single Spec Complete

When all acceptance criteria verified, tests pass, changes committed/pushed:
```
<promise>DONE</promise>
```

Bash loop detects this and starts next iteration with fresh context.

### All Work Complete

When no incomplete specs remain:
```
<promise>ALL_DONE</promise>
```

Loop stops gracefully.

### Important Rules

1. **Never output DONE prematurely** - Only when 100% verified
2. **Re-verify random completed spec** - Before signaling ALL_DONE
3. **Acceptance criteria must be specific** - Not "works correctly" but testable conditions
4. **Tests must pass** - Unit, integration, browser tests as specified in spec

## Example Iteration Flow

```
Iteration 1: specs/001-user-auth/spec.md
├─ Agent reads constitution and spec
├─ Implements OAuth login flow
├─ Runs tests (all pass)
├─ Commits and pushes
└─ Outputs <promise>DONE</promise>
   └─ Loop detects signal, starts Iteration 2

Iteration 2: specs/002-user-profile/spec.md
├─ Agent reads constitution and spec
├─ Implements profile page
├─ Runs tests (one fails)
├─ Fixes failing test
├─ Re-runs tests (all pass)
└─ Outputs <promise>DONE</promise>
   └─ Loop detects signal, starts Iteration 3

...

Iteration N: No incomplete specs remain
├─ Agent re-verifies specs/001-user-auth (random check)
├─ Confirms all specs have "Status: COMPLETE"
└─ Outputs <promise>ALL_DONE</promise>
   └─ Loop stops gracefully
```

## Best Practices

### For Specifications

1. **Write testable acceptance criteria** - Specific, verifiable conditions
2. **Include testing requirements** - Unit tests, integration tests, browser checks
3. **Set realistic scope** - One spec should complete in 1-5 iterations ideally
4. **Add completion checklist** - Clear items to verify before DONE

### For Running Loops

1. **Start with limited iterations** - `./scripts/ralph-loop.sh 10` for first runs
2. **Monitor logs** - Check `logs/` directory for issues
3. **Enable Telegram notifications** - Get progress updates remotely
4. **Review stuck specs early** - Don't wait until 10 attempts

### For Constitution

1. **Be specific about principles** - Guide decision-making across sessions
2. **Set appropriate autonomy** - YOLO mode recommended for most projects
3. **Document tech stack** - Helps agent make informed choices
4. **Keep it concise** - Single source of truth, not exhaustive documentation

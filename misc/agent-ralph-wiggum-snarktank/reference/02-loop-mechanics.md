# Loop Mechanics

## The Ralph Script

The `ralph.sh` script is the engine of the Ralph system. It is a Bash script that implements the iterative loop, spawning fresh AI instances for each iteration until all tasks are complete or the maximum iteration count is reached.

### Command-Line Interface

```bash
./scripts/ralph/ralph.sh [max_iterations]
./scripts/ralph/ralph.sh --tool amp [max_iterations]
./scripts/ralph/ralph.sh --tool claude [max_iterations]
./scripts/ralph/ralph.sh --tool=claude 25
```

Arguments:

- `--tool amp` or `--tool claude` — Select the AI coding tool (default: `amp`)
- `[max_iterations]` — Maximum number of loop iterations (default: `10`)
- Positional numeric arguments are treated as max_iterations for backward compatibility

### Argument Parsing

The script uses a while loop with case matching to parse arguments:

```bash
TOOL="amp"  # Default to amp
MAX_ITERATIONS=10

while [[ $# -gt 0 ]]; do
  case $1 in
    --tool)
      TOOL="$2"
      shift 2
      ;;
    --tool=*)
      TOOL="${1#*=}"
      shift
      ;;
    *)
      if [[ "$1" =~ ^[0-9]+$ ]]; then
        MAX_ITERATIONS="$1"
      fi
      shift
      ;;
  esac
done
```

Tool choice is validated — only `amp` or `claude` are accepted.

### Directory Structure

The script operates relative to its own location (`SCRIPT_DIR`):

```
scripts/ralph/
├── ralph.sh          # The loop script
├── prompt.md         # Prompt template for Amp
├── CLAUDE.md         # Prompt template for Claude Code
├── prd.json          # User stories with pass/fail status
├── progress.txt      # Append-only learnings log
├── .last-branch      # Tracks last run's branch name
└── archive/          # Archived previous runs
    └── YYYY-MM-DD-feature-name/
```

Key file paths resolved at runtime:

- `PRD_FILE="$SCRIPT_DIR/prd.json"`
- `PROGRESS_FILE="$SCRIPT_DIR/progress.txt"`
- `ARCHIVE_DIR="$SCRIPT_DIR/archive"`
- `LAST_BRANCH_FILE="$SCRIPT_DIR/.last-branch"`

### Initialization

Before entering the loop, the script performs setup:

1. **Archive detection**: If a previous run exists with a different `branchName`, archive it to `archive/YYYY-MM-DD-feature-name/`
2. **Progress file initialization**: Creates `progress.txt` with a header if it doesn't exist
3. **Branch tracking**: Records current branch name in `.last-branch`

The archiving process:

```bash
if [ "$CURRENT_BRANCH" != "$LAST_BRANCH" ]; then
    DATE=$(date +%Y-%m-%d)
    FOLDER_NAME=$(echo "$LAST_BRANCH" | sed 's|^ralph/||')
    ARCHIVE_FOLDER="$ARCHIVE_DIR/$DATE-$FOLDER_NAME"
    
    mkdir -p "$ARCHIVE_FOLDER"
    cp "$PRD_FILE" "$ARCHIVE_FOLDER/"
    cp "$PROGRESS_FILE" "$ARCHIVE_FOLDER/"
    
    # Reset progress for new run
    echo "# Ralph Progress Log" > "$PROGRESS_FILE"
    echo "Started: $(date)" >> "$PROGRESS_FILE"
    echo "---" >> "$PROGRESS_FILE"
fi
```

### The Main Loop

```bash
for i in $(seq 1 $MAX_ITERATIONS); do
  echo "═══ Iteration $i of $MAX_ITERATIONS ($TOOL) ═══"
  
  # Run the selected tool with the ralph prompt
  if [[ "$TOOL" == "amp" ]]; then
    OUTPUT=$(cat "$SCRIPT_DIR/prompt.md" | amp --dangerously-allow-all 2>&1 | tee /dev/stderr) || true
  else
    OUTPUT=$(claude --dangerously-skip-permissions --print < "$SCRIPT_DIR/CLAUDE.md" 2>&1 | tee /dev/stderr) || true
  fi
  
  # Check for completion signal
  if echo "$OUTPUT" | grep -q "<promise>COMPLETE</promise>"; then
    echo "Ralph completed all tasks!"
    exit 0
  fi
  
  sleep 2
done

echo "Ralph reached max iterations without completing all tasks."
exit 1
```

### Tool Invocation Differences

**Amp**: Prompt is piped via stdin with `--dangerously-allow-all`:

```bash
cat "$SCRIPT_DIR/prompt.md" | amp --dangerously-allow-all
```

**Claude Code**: Prompt is passed via stdin with `--dangerously-skip-permissions --print`:

```bash
claude --dangerously-skip-permissions --print < "$SCRIPT_DIR/CLAUDE.md"
```

Both use flags that skip permission prompts, enabling fully autonomous operation. The `|| true` ensures the loop continues even if a single iteration fails (non-zero exit code).

### Completion Detection

The loop checks each iteration's output for the completion signal:

```bash
if echo "$OUTPUT" | grep -q "<promise>COMPLETE</promise>"; then
    echo "Ralph completed all tasks!"
    exit 0
fi
```

The `<promise>COMPLETE</promise>` tag is emitted by the AI agent when all stories in `prd.json` have `passes: true`. This is the only way the loop exits successfully.

### Exit Codes

- `0` — All tasks completed (detected `<promise>COMPLETE</promise>`)
- `1` — Max iterations reached without completion

### Iteration Timing

A 2-second sleep between iterations provides:
- Brief cooldown between AI tool invocations
- Time for file system operations to settle
- Separation in log output for readability

### Output Handling

Each iteration's output is captured and displayed:

```bash
OUTPUT=$(... | tee /dev/stderr) || true
```

The `tee /dev/stderr` ensures output is both captured (in `$OUTPUT` for completion detection) and displayed (to stderr for visibility). This allows operators to watch Ralph's progress in real-time.

### What Happens Inside Each Iteration

From the AI agent's perspective, each iteration follows this sequence:

1. **Read state**: Load `prd.json` and `progress.txt`
2. **Check branch**: Verify or create the feature branch from `branchName`
3. **Select story**: Pick highest priority story where `passes: false`
4. **Implement**: Code the single user story
5. **Quality checks**: Run typecheck, lint, tests
6. **Update documentation**: Modify AGENTS.md/CLAUDE.md with learned patterns
7. **Commit**: If checks pass, commit with message `feat: [Story ID] - [Story Title]`
8. **Update PRD**: Set `passes: true` for the completed story
9. **Log progress**: Append learnings to `progress.txt`
10. **Check completion**: If all stories pass, emit `<promise>COMPLETE</promise>`

### Fresh Context Guarantee

Each iteration spawns a **completely new process** of the AI tool. There is no shared state between iterations except what persists on disk:

- Git commits (code changes from previous iterations)
- `prd.json` (which stories are done, which remain)
- `progress.txt` (learnings and patterns discovered)
- Modified source files (committed or uncommitted)
- Updated AGENTS.md/CLAUDE.md files

The AI tool does not retain conversation history, tool call results, or any internal state from previous iterations. This is a feature, not a bug — it prevents context bloat and keeps each iteration focused.

### Archiving Previous Runs

When starting a new feature (different `branchName`), Ralph automatically archives the previous run:

1. Detects branch name change by comparing `prd.json`'s `branchName` with `.last-branch`
2. Creates archive directory: `archive/YYYY-MM-DD-feature-name/`
3. Copies `prd.json` and `progress.txt` to archive
4. Resets `progress.txt` with fresh header

This preserves history from previous features while giving the new feature a clean slate.

### Debugging Failed Runs

When Ralph reaches max iterations without completing:

```bash
# Check which stories are still pending
cat scripts/ralph/prd.json | jq '.userStories[] | select(.passes == false) | {id, title}'

# Review learnings to understand what went wrong
cat scripts/ralph/progress.txt

# Check git log for commits made during the run
git log --oneline -20

# Check for uncommitted changes (Ralph may have failed before committing)
git status
```

Common failure modes:
- Story was too large for one context window
- Acceptance criteria were vague or unverifiable
- Quality checks were not configured (no typecheck/tests)
- Dependencies between stories were not properly ordered

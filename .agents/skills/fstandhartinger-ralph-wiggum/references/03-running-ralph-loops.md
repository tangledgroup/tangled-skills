# Running Ralph Loops

Complete guide to executing Ralph loops, monitoring progress, and managing iterations.

## Basic Commands

### Build Mode (Default)

```bash
# Unlimited iterations
./scripts/ralph-loop.sh

# Maximum 20 iterations
./scripts/ralph-loop.sh 20

# Use different AI providers
./scripts/ralph-loop-codex.sh      # OpenAI Codex CLI
./scripts/ralph-loop-gemini.sh     # Google Gemini CLI
./scripts/ralph-loop-copilot.sh    # GitHub Copilot CLI
```

### Planning Mode (Optional)

```bash
# Create IMPLEMENTATION_PLAN.md from specs
./scripts/ralph-loop.sh plan

# With iteration limit
./scripts/ralph-loop.sh plan 5
```

### Help

```bash
./scripts/ralph-loop.sh --help
./scripts/ralph-loop.sh -h
```

## Command-Line Options

### Iteration Limits

```bash
# No limit (runs until all specs complete)
./scripts/ralph-loop.sh

# Stop after 10 iterations
./scripts/ralph-loop.sh 10

# Stop after 50 iterations
./scripts/ralph-loop.sh 50
```

### Disable Telegram Notifications

```bash
./scripts/ralph-loop.sh --no-telegram
```

### Enable Audio Notifications

```bash
./scripts/ralph-loop.sh --telegram-audio
```

Requires `CHUTES_API_KEY` environment variable.

### Reset Circuit Breaker

```bash
./scripts/ralph-loop.sh --reset-circuit
```

## Understanding the Output

### Startup Display

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
              RALPH LOOP (Claude Code) STARTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mode:     build
Prompt:   PROMPT_build.md
Branch:   main
YOLO:     ENABLED
Log:      logs/ralph_build_session_20240115_143022.log
Max:      20 iterations

Work source:
  ○ IMPLEMENTATION_PLAN.md (not found, that's OK)
  ✓ specs/ folder (5 specs, 3 incomplete)
    Next incomplete: specs/003-user-dashboard/spec.md

The loop checks for <promise>DONE</promise> in each iteration.
Agent must verify acceptance criteria before outputting it.

Press Ctrl+C to stop the loop
```

### Iteration Display

```
════════════════════ LOOP 1 ════════════════════
[2024-01-15 14:30:25] Starting iteration 1

✓ Claude execution completed
✓ Completion signal detected: <promise>DONE</promise>
✓ Task completed successfully!

Waiting 2s before next iteration...
```

### Failure Display

```
════════════════════ LOOP 3 ════════════════════
[2024-01-15 14:35:12] Starting iteration 3

✓ Claude execution completed
⚠ No completion signal found
  Agent did not output <promise>DONE</promise> or <promise>ALL_DONE</promise>
  This means acceptance criteria were not met.
  Retrying in next iteration...

Latest Claude output (last 5 lines):
  ... implementing user profile page
  ... need to add validation for email field
  ... will fix in next attempt

⚠ 3 consecutive iterations without completion.
  The agent may be stuck. Consider:
  - Checking the logs in logs/
  - Simplifying the current spec
  - Manually fixing blocking issues
```

## Logging

### Log File Structure

All output is captured to log files in `logs/`:

| File Pattern | Contents |
|--------------|----------|
| `logs/ralph_*_session_YYYYMMDD_HHMMSS.log` | Entire session (all iterations) |
| `logs/ralph_*_iter_N_YYYYMMDD_HHMMSS.log` | Individual iteration output |
| `logs/ralph_codex_output_iter_N_*.txt` | Last message from Codex (if using Codex) |

### Finding Logs

```bash
# List all session logs
ls -la logs/ralph_*_session_*.log

# Find latest iteration log
ls -t logs/ralph_*_iter_*_*.log | head -1

# View specific iteration
cat logs/ralph_build_iter_5_20240115_143522.log
```

### Real-Time Monitoring

The loop displays rolling output every 10 seconds showing the last 5 lines of agent output. This helps monitor progress without scrolling through logs.

## Monitoring Progress

### Check Current Status

```bash
# Count total specs
find specs -maxdepth 1 -name "*.md" | wc -l

# Count incomplete specs
source scripts/lib/spec_queue.sh
count_incomplete_root_specs "specs"

# Get next spec to work on
get_first_incomplete_root_spec "specs"
```

### Check Stuck Specs

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

### Check Circuit Breaker

```bash
source scripts/lib/circuit_breaker.sh
show_circuit_status
```

Output:
```
Circuit Breaker Status
  State: CLOSED
  Reason: Normal operation
  Loops without progress: 0
  Current loop: 15
```

## Telegram Notifications

### What You Get

1. **Loop Start** - When Ralph begins running
2. **Spec Completed** - Each time a spec finishes
3. **Consecutive Failures** - After 3+ failures without completion
4. **Stuck Specs** - When NR_OF_TRIES reaches 10
5. **Loop Finished** - Summary when loop ends

### Example Messages

```
🚀 Ralph Loop Started
Mode: build
Branch: main
Specs: 5
```

```
✅ Spec Completed: 003-user-dashboard
Iteration: 3
Summary: Implemented user dashboard with stats widgets
```

```
⚠️ Ralph Loop Warning: 3 consecutive failures on spec 004-analytics
```

```
🏁 Ralph Loop Finished
Iterations: 12
Completed: 4 specs
```

### Setup Required

See [Advanced Features](05-advanced-features.md) for Telegram setup instructions.

## Completion Logs

If enabled in constitution, each completed spec creates a log entry:

```
completion_log/
├── 2024-01-15--14-30-22--001-user-auth.md
├── 2024-01-15--14-30-22--001-user-auth.png
├── 2024-01-15--14-35-45--002-user-profile.md
└── 2024-01-15--14-35-45--002-user-profile.png
```

Each log includes:
- Timestamp
- Spec name
- Summary of changes
- Mermaid diagram (as markdown and PNG)

## History Tracking

### history.md

After each spec completion, append a one-line summary:

```markdown
# Project History

- 2024-01-15: Implemented user authentication with OAuth (001-user-auth)
- 2024-01-15: Added user profile page with edit functionality (002-user-profile)
- 2024-01-15: Created dashboard with stats widgets (003-user-dashboard)
```

### Detailed History Files

For each spec, create `history/YYYY-MM-DD--spec-name.md`:

```markdown
# 2024-01-15 -- 001-user-auth

## Summary

Implemented OAuth authentication flow using Passport.js with Google and GitHub providers.

## Decisions Made

- Chose Passport.js over custom implementation for security best practices
- Used JWT tokens for session management
- Stored refresh tokens encrypted in database

## Issues Encountered

- Initial OAuth callback URL mismatch - fixed by updating redirect URI in console
- Token expiration handling needed retry logic

## Lessons Learned

- Always test OAuth flow in staging environment first
- Document redirect URIs clearly for team members
```

## Stopping the Loop

### Graceful Stop

Press `Ctrl+C` to stop the loop. Current iteration completes, then loop exits.

### Force Stop

Press `Ctrl+C` twice for immediate termination.

### Automatic Stop Conditions

1. All specs complete (outputs `<promise>ALL_DONE</promise>`)
2. Max iterations reached
3. Circuit breaker opens
4. No incomplete specs found

## Common Scenarios

### Running Overnight

```bash
# Limit to reasonable number of iterations
./scripts/ralph-loop.sh 50

# Enable Telegram notifications for progress updates
export TG_BOT_TOKEN="your-token"
export TG_CHAT_ID="your-chat-id"
./scripts/ralph-loop.sh 100
```

### Quick Test Run

```bash
# Just 3 iterations to verify setup
./scripts/ralph-loop.sh 3
```

### Focus on Specific Spec

Temporarily move other specs out of `specs/` folder:

```bash
# Backup all except target spec
mkdir specs/_backup
mv specs/001-* specs/_backup/
mv specs/002-* specs/_backup/
# Keep specs/003-target-spec/

# Run loop
./scripts/ralph-loop.sh

# Restore other specs
mv specs/_backup/* specs/
rmdir specs/_backup
```

### Debug Stuck Iteration

```bash
# Check the iteration log
cat logs/ralph_build_iter_8_20240115_144522.log

# Look for error patterns
grep -i "error\|fail\|exception" logs/ralph_build_iter_8_*.log

# Check NR_OF_TRIES count
grep "NR_OF_TRIES" specs/003-stuck-spec/spec.md

# Review acceptance criteria
cat specs/003-stuck-spec/spec.md | grep -A 20 "Acceptance Criteria"
```

## Performance Tips

### Optimize Iteration Count

1. **Write focused specs** - Each spec should complete in 1-5 iterations
2. **Clear acceptance criteria** - Reduce back-and-forth clarification
3. **Enable YOLO mode** - Faster execution without approval prompts
4. **Use completion logs** - Track progress and identify patterns

### Monitor Resource Usage

```bash
# Check log file sizes
du -sh logs/

# Clean old logs (older than 7 days)
find logs -name "*.log" -mtime +7 -delete
```

## Troubleshooting Loop Issues

### Loop Not Starting

**Symptom:** Script exits immediately

**Check:**
```bash
# Verify Claude CLI installed
which claude

# Check constitution exists
ls -la .specify/memory/constitution.md

# Verify specs exist
ls specs/
```

### Agent Not Outputting DONE

**Symptom:** Loop retries same task repeatedly

**Causes:**
1. Acceptance criteria not met
2. Tests failing
3. Ambiguous requirements

**Fix:**
- Review iteration logs for what's blocking completion
- Clarify acceptance criteria in spec
- Check if tests are actually passing
- Consider splitting spec into smaller pieces

### Circuit Breaker Opens Frequently

**Symptom:** Loop halts after few iterations

**Causes:**
1. Spec too complex
2. Blocking external dependency
3. Agent stuck on error

**Fix:**
```bash
# Check circuit status
show_circuit_status

# Review what changed (or didn't)
git status
git diff

# Reset and continue after fixing issue
reset_circuit_breaker "Fixed blocking issue"
./scripts/ralph-loop.sh
```

### No Progress After Multiple Iterations

**Symptom:** NR_OF_TRIES increasing but no completion

**Action:**
1. Check stuck specs summary
2. Review iteration logs for patterns
3. Consider manual intervention
4. Split spec into smaller pieces
5. Reset counter after fixing: `reset_nr_of_tries "specs/NNN/spec.md"`

## Next Steps

After running loops:
- Review [Creating Specifications](04-creating-specifications.md) for writing better specs
- Explore [Advanced Features](05-advanced-features.md) for Telegram, GitHub issues, audio notifications
- Consult [Troubleshooting](06-troubleshooting.md) for common issues

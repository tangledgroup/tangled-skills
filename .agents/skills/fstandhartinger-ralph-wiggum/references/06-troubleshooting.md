# Troubleshooting

Common issues, debugging techniques, and solutions for Ralph Wiggum problems.

## Common Issues

### Loop Not Starting

**Symptom:** Script exits immediately or shows error

#### Check Constitution Exists

```bash
ls -la .specify/memory/constitution.md
```

If missing, create it (see [Setup and Configuration](01-setup-configuration.md)).

#### Check AI CLI Installation

```bash
# For Claude Code
which claude
claude --version

# For Codex
which codex
codex --version
```

Install the required CLI if missing.

#### Verify Specs Directory

```bash
ls specs/
```

If empty, create at least one spec file.

#### Check Script Permissions

```bash
chmod +x scripts/ralph-loop.sh
chmod +x scripts/lib/*.sh
```

### Agent Not Outputting DONE

**Symptom:** Loop retries same task repeatedly without completion

#### Check Acceptance Criteria

Review the spec's acceptance criteria:
```bash
cat specs/003-current-spec/spec.md | grep -A 50 "Acceptance Criteria"
```

**Common problems:**
- Criteria too vague ("works correctly")
- Missing verification steps
- Impossible requirements
- Conflicting criteria

**Fix:** Rewrite criteria to be specific and testable with clear verification commands.

#### Review Iteration Logs

```bash
# Find latest iteration log
ls -t logs/ralph_*_iter_*_*.log | head -1

# Read the log
cat logs/ralph_build_iter_8_20240115_144522.log

# Look for errors
grep -i "error\|fail\|exception" logs/ralph_build_iter_8_*.log
```

**What to look for:**
- Tests failing and not being fixed
- Agent stuck on same error
- Missing dependencies
- Environment configuration issues

#### Check Test Results

```bash
# If agent ran tests, find output in logs
grep -A 10 "npm test\|yarn test\|pytest" logs/ralph_build_iter_8_*.log
```

If tests are failing, the agent won't output DONE. Either:
- Fix the tests manually
- Clarify what tests should pass
- Split spec into smaller pieces

### Stuck Specs (NR_OF_TRIES >= 10)

**Symptom:** Spec has been attempted 10+ times without completion

#### Identify Stuck Specs

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

#### Solutions

**Option 1: Split the Spec**

Break large spec into smaller, focused specs:

```bash
# Original: 004-dashboard (too complex)
# Split into:
# - 004-dashboard-layout (basic page structure)
# - 005-dashboard-widgets (stats components)
# - 006-dashboard-charts (chart integrations)
# - 007-dashboard-realtime (WebSocket updates)

# Move original to backup
mv specs/004-dashboard specs/004-dashboard-ORIGINAL

# Create new smaller specs
mkdir specs/004-dashboard-layout specs/005-dashboard-widgets
# Write focused specs for each
```

**Option 2: Clarify Acceptance Criteria**

Make criteria more specific and achievable:

**Before (vague):**
```markdown
### Criterion: Dashboard loads correctly
Dashboard should display user data
```

**After (specific):**
```markdown
### Criterion: Dashboard displays welcome message

**Given** authenticated user "John Doe"
**When** visiting /dashboard
**Then** page shows "Welcome back, John Doe" in h1 element

**Verification:**
```bash
# Using Playwright
await expect(page.locator('h1')).toContainText('Welcome back, John Doe')
```
```

**Option 3: Manual Intervention**

Fix blocking issues manually:
```bash
# Check what's blocking
git status
git diff

# Fix the issue (e.g., missing dependency)
npm install missing-package

# Reset counter and continue
reset_nr_of_tries "specs/004-dashboard/spec.md"
./scripts/ralph-loop.sh
```

**Option 4: Delete and Rewrite**

If spec is fundamentally flawed:
```bash
# Backup original
cp specs/004-dashboard/spec.md specs/004-dashboard/spec.md.backup

# Rewrite with clearer requirements
nano specs/004-dashboard/spec.md

# Reset counter
reset_nr_of_tries "specs/004-dashboard/spec.md"
```

### Circuit Breaker Opens Frequently

**Symptom:** Loop halts after few iterations due to circuit breaker

#### Check Circuit Status

```bash
source scripts/lib/circuit_breaker.sh
show_circuit_status
```

Output:
```
Circuit Breaker Status
  State: OPEN
  Reason: No progress in 5 consecutive loops
  Loops without progress: 5
  Current loop: 12
```

#### Understand Why It Opened

**No Progress (no file changes):**
- Agent not implementing anything
- Spec may be complete already
- Agent confused about what to do

**Same Error Repeated:**
- Blocking issue preventing progress
- Missing dependency or configuration
- Test failures not being addressed

#### Check What Changed (or Didn't)

```bash
# See if any files were modified
git status

# View recent changes
git diff HEAD~5

# Check iteration logs for patterns
ls -t logs/ralph_*_iter_*_*.log | head -5 | while read f; do
  echo "=== $f ==="
  tail -20 "$f"
done
```

#### Reset and Continue

After fixing the issue:

```bash
# Reset circuit breaker
reset_circuit_breaker "Fixed missing dependency"

# Or run with reset flag
./scripts/ralph-loop.sh --reset-circuit
```

#### Adjust Thresholds (If Needed)

For complex specs that need more iterations:

Edit `scripts/lib/circuit_breaker.sh`:
```bash
# Increase from 5 to 10
CB_NO_PROGRESS_THRESHOLD=10

# Increase from 3 to 5
CB_SAME_ERROR_THRESHOLD=5
```

### Telegram Notifications Not Working

**Symptom:** No messages received in Telegram

#### Verify Bot Token

```bash
curl -s "https://api.telegram.org/bot${TG_BOT_TOKEN}/getMe"
```

Should return bot info. If error, token is invalid.

#### Verify Chat ID

```bash
# Send test message to bot first, then:
curl -s "https://api.telegram.org/bot${TG_BOT_TOKEN}/getUpdates" | jq '.result[-1].message.chat.id'
```

Use this ID as `TG_CHAT_ID`.

#### Test Manual Message

```bash
curl -s -X POST "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TG_CHAT_ID}" \
  -d text="Test message from Ralph"
```

If this works but loop notifications don't, check:
- `TELEGRAM_ENABLED` flag in script
- Constitution has Telegram section
- Environment variables are set before running loop

### Audio Notifications Failing

**Symptom:** Text messages work, audio doesn't

#### Check Chutes API Key

```bash
echo $CHUTES_API_KEY
# Should start with "cpk_"
```

#### Test TTS Directly

```bash
curl -X POST "https://chutes-kokoro.chutes.ai/speak" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CHUTES_API_KEY" \
  -d '{"text": "Test audio", "voice": "am_michael"}' \
  --output test.wav

# Check file created
ls -lh test.wav

# Play it (if on macOS/Linux with player)
afplay test.wav  # macOS
aplay test.wav   # Linux
```

#### Enable Audio Flag

Make sure to pass the flag:
```bash
./scripts/ralph-loop.sh --telegram-audio
```

### GitHub Issues Not Working

**Symptom:** Ralph ignores GitHub issues

#### Verify gh CLI Authentication

```bash
gh auth status
```

Should show authenticated. If not:
```bash
gh auth login
```

#### Test Issue Listing

```bash
gh issue list --repo your-org/your-repo --state open
```

Should return issues. Check:
- Repository name is correct
- You have access permissions
- Token has required scopes

#### Check Constitution

Ensure constitution has GitHub Issues section:
```markdown
## GitHub Issues

Work on issues from `your-org/your-repo` in addition to specs.
```

### Logs Too Large

**Symptom:** Log files consuming too much disk space

#### Check Size

```bash
du -sh logs/
# Might show: 2.5G logs/
```

#### Clean Old Logs

```bash
# Delete logs older than 7 days
find logs -name "*.log" -mtime +7 -delete

# Compress logs older than 3 days
find logs -name "*.log" -mtime +3 -exec gzip {} \;
```

#### Set Up Automatic Rotation

Add to crontab:
```bash
# Daily at 2 AM: delete logs older than 7 days
0 2 * * * find /path/to/project/logs -name "*.log" -mtime +7 -delete
```

### Agent Making No Progress

**Symptom:** Loop runs but no files change

#### Check YOLO Mode

```bash
grep "YOLO Mode" .specify/memory/constitution.md
```

Should be `ENABLED`. If `DISABLED`, agent may be waiting for approval.

Change to:
```markdown
YOLO Mode: ENABLED
```

#### Review Constitution Principles

Ensure principles guide the agent effectively:
```markdown
## Core Principles

1. Build exactly what's specified, nothing more
2. Test everything before marking complete
3. Commit often with meaningful messages
4. Don't wait for approval when YOLO mode is enabled
```

#### Check Spec Clarity

Vague specs lead to confusion. Review:
- Are acceptance criteria specific?
- Is technical approach clear?
- Are dependencies listed?
- Is completion checklist comprehensive?

### Git Push Failing

**Symptom:** Agent commits but can't push

#### Check Remote Configuration

```bash
git remote -v
git branch --show-current
```

#### Verify Authentication

```bash
# Test push manually
git push origin main
```

If fails, configure git authentication:
- SSH keys
- Git credential helper
- Personal access token

#### Check Branch Name

Ensure branch exists on remote:
```bash
# If branch doesn't exist remotely
git push -u origin main
```

### Dependency Installation Failing

**Symptom:** Agent can't install required packages

#### Check Node/npm Version

```bash
node --version
npm --version
```

#### Verify Package Exists

```bash
npm view package-name
```

#### Check Network/Proxy

```bash
# Test npm registry
curl https://registry.npmjs.org/

# If behind proxy, configure npm
npm config set proxy http://proxy:port
npm config set https-proxy http://proxy:port
```

### Database Migration Failing

**Symptom:** Spec requires database changes but migrations fail

#### Check Database Connection

```bash
# Test connection
psql -h localhost -U postgres -d mydb

# Or for MySQL
mysql -u root -p mydb
```

#### Review Migration Script

```bash
cat migrations/001-create-table.sql
```

Check for:
- Syntax errors
- Missing dependencies
- Incorrect data types
- Constraint conflicts

#### Run Migration Manually

```bash
# Test migration
psql -d mydb -f migrations/001-create-table.sql
```

Fix errors, then continue loop.

## Debugging Techniques

### Analyze Iteration Patterns

```bash
# Count iterations per spec
for spec in specs/*/spec.md; do
  tries=$(grep -o "NR_OF_TRIES: [0-9]*" "$spec" | tail -1)
  echo "$spec: $tries"
done
```

### Find Common Errors

```bash
# Extract all errors from logs
grep -rh "Error\|Exception\|Failed" logs/ralph_*_iter_*_*.log | \
  sort | uniq -c | sort -rn | head -20
```

### Track File Changes Over Time

```bash
# See which files agent modifies most
git log --name-only --oneline | \
  grep -v "commit\|^$" | \
  sort | uniq -c | sort -rn | head -20
```

### Monitor Loop Performance

```bash
# Time each iteration (add to loop script)
START=$(date +%s)
# ... run iteration ...
END=$(date +%s)
echo "Iteration took $((END - START)) seconds"
```

### Check Agent's Last Thoughts

```bash
# See what agent was doing before stopping
tail -50 logs/ralph_build_iter_8_20240115_144522.log
```

Look for:
- What task it was working on
- What errors it encountered
- Whether it attempted to fix issues
- If it reached completion checklist

## Prevention Strategies

### Write Better Specs

1. **Specific acceptance criteria** - Given/When/Then format with verification steps
2. **Focused scope** - One feature per spec, achievable in 1-5 iterations
3. **Clear technical approach** - Dependencies, architecture, database changes
4. **Comprehensive testing** - Unit, integration, browser tests listed explicitly
5. **Realistic completion checklist** - All items verifiable

### Monitor Proactively

```bash
# Check stuck specs daily
source scripts/lib/nr_of_tries.sh
print_stuck_specs_summary

# Review circuit breaker status
source scripts/lib/circuit_breaker.sh
show_circuit_status

# Clean old logs weekly
find logs -name "*.log" -mtime +7 -delete
```

### Set Up Alerts

Enable Telegram notifications for:
- Spec completions
- Consecutive failures (3+)
- Stuck specs (NR_OF_TRIES >= 10)
- Circuit breaker opens

### Regular Maintenance

```bash
# Weekly: Review completion logs
ls -la completion_log/

# Monthly: Archive old history
tar czf history_archive_$(date +%Y%m).tar.gz history/*.md

# As needed: Update constitution with lessons learned
nano .specify/memory/constitution.md
```

## Getting Help

### Check Documentation

- [Ralph Loop Methodology](02-ralph-loop-methodology.md) - Core concepts
- [Running Ralph Loops](03-running-ralph-loops.md) - Execution details
- [Creating Specifications](04-creating-specifications.md) - Spec best practices
- [Advanced Features](05-advanced-features.md) - Notifications and integrations

### Review Original Repository

https://github.com/fstandhartinger/ralph-wiggum

Check:
- Issues tab for known problems
- README for latest updates
- Scripts for implementation details

### Community Resources

- Geoffrey Huntley's original methodology: https://github.com/ghuntley/how-to-ralph-wiggum
- SpecKit specifications: https://github.com/github/spec-kit

## When All Else Fails

### Manual Recovery

```bash
# Stop the loop (Ctrl+C)

# Review what was accomplished
git status
git diff

# Commit any good work
git add -A
git commit -m "WIP: Progress on 004-dashboard before manual intervention"
git push

# Fix blocking issues manually
# ... make fixes ...

# Reset and continue
reset_circuit_breaker "Manual fix applied"
reset_nr_of_tries "specs/004-dashboard/spec.md"
./scripts/ralph-loop.sh
```

### Start Fresh

If loop is too stuck:

```bash
# Backup current state
cp -r specs specs-backup-$(date +%Y%m%d)
cp -r logs logs-backup-$(date +%Y%m%d)

# Reset tracking
find specs -name "spec.md" -exec sed -i 's/NR_OF_TRIES: [0-9]*/NR_OF_TRIES: 0/g' {} \;

# Remove circuit breaker
rm .circuit_breaker_state

# Start fresh with limited iterations
./scripts/ralph-loop.sh 10
```

## Summary

Most issues stem from:
1. **Vague acceptance criteria** - Make them specific and testable
2. **Specs too large** - Split into smaller, focused specs
3. **Blocking dependencies** - Install missing packages, fix configuration
4. **Circuit breaker sensitivity** - Adjust thresholds or reset after fixes

Key commands to remember:
```bash
# Check stuck specs
print_stuck_specs_summary

# Reset circuit breaker
reset_circuit_breaker "Fixed issue"

# View iteration logs
tail -100 logs/ralph_*_iter_*_*.log

# Reset spec counter
reset_nr_of_tries "specs/NNN-feature/spec.md"
```

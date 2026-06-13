# Analytics & Telemetry

## Contents
- Token Savings Analytics (`rtk gain`)
- Discover Missed Savings (`rtk discover`)
- Session Adoption (`rtk session`)
- Telemetry Data Collection
- Managing Telemetry
- Environment Overrides

## Token Savings Analytics (`rtk gain`)

`rtk gain` shows how many tokens RTK has saved across all commands, with temporal breakdowns.

### Quick Reference

```bash
rtk gain                  # Default summary
rtk gain --graph          # ASCII graph (last 30 days)
rtk gain --history        # Recent command history
rtk gain --daily          # Day-by-day breakdown
rtk gain --weekly         # Weekly aggregation
rtk gain --all --format json   # JSON export for dashboards
```

### Example Output

```
Total commands : 12
Input tokens   : 45,230
Output tokens  : 4,890
Saved          : 40,340  (89.2%)
```

### Typical Savings by Command

| Command | Typical Savings |
|---------|----------------|
| `git add/commit/push` | ~92% |
| `cargo test`, `pytest`, `go test` | ~90% |
| `ls`, `tree`, `grep` | ~80% |
| `cat`, `read` | ~70% |
| `git diff` | ~75% |

### How Token Estimation Works

RTK estimates token counts based on character-to-token ratios, comparing raw output against filtered output. Actual savings vary by project size and command type.

### Database

Token history is stored in an SQLite database at `~/.local/share/rtk/history.db` (configurable via `[tracking].database_path`). History retention is 90 days by default (`[tracking].history_days`). Auto-cleanup removes old entries.

## Discover Missed Savings (`rtk discover`)

Analyzes AI assistant command history to identify commands that ran without RTK filtering and calculates lost tokens.

```bash
rtk discover                    # Current project
rtk discover --all              # All projects
rtk discover --all --since 7    # Last 7 days, all projects
```

Example output:
```
Missed savings analysis (last 7 days)

Command         Count   Est. lost
git status      45      ~27,000
cargo test      12      ~24,000
```

## Session Adoption (`rtk session`)

Shows RTK adoption rate across recent AI assistant sessions.

```bash
rtk session
```

## Telemetry Data Collection

RTK can collect **anonymous, aggregate usage metrics** once per day. Telemetry is **disabled by default** and requires **explicit opt-in consent** (GDPR Art. 6, 7).

### What Is Collected

| Category | Data | Why |
|----------|------|-----|
| Identity | Salted device hash (SHA-256) | Count unique installations |
| Environment | RTK version, OS, architecture, install method | Platform support prioritization |
| Usage volume | Command count (24h), total commands, tokens saved (24h/30d/total) | Measure adoption and value |
| Quality | Top 5 passthrough commands, parse failures | Identify weak filters |
| Ecosystem | Command category distribution (git, cargo, js, etc.) | Prioritize filter development |
| Retention | Days since first use, active days in last 30 | Understand engagement |
| Adoption | AI agent hook type, custom TOML filter count | Track integration coverage |
| Configuration | config.toml existence, excluded commands count | Understand user maturity |
| Features | Usage counts for meta-commands (gain, discover, proxy) | Value assessment |
| Economics | Estimated USD savings | Quantify value delivered |

All data is aggregate counts or anonymized command names (first 3 words, no arguments). Top commands report only tool names (e.g. "git", "cargo"), never full command lines.

### What Is NOT Collected

Source code, file paths, command arguments, secrets, environment variables, personal data, or repository contents.

### Managing Telemetry

```bash
rtk telemetry status      # Check current consent state
rtk telemetry enable      # Give consent (interactive prompt)
rtk telemetry disable     # Withdraw consent — stops immediately
rtk telemetry forget      # Withdraw + delete local data + server-side erasure
```

## Environment Overrides

| Variable | Description |
|----------|-------------|
| `RTK_TELEMETRY_DISABLED=1` | Blocks telemetry regardless of consent |
| `RTK_DISABLED=1` | Disable RTK for a single command |
| `RTK_TEE_DIR` | Override tee directory |
| `RTK_HOOK_AUDIT=1` | Enable hook audit logging |

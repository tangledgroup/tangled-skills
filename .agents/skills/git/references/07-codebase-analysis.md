# Codebase Analysis Commands

Before reading code in an unfamiliar repository, run these diagnostic git commands to understand where the codebase "hurts" and identify risk areas. These commands reveal churn hotspots, bus factor issues, bug clusters, and crisis patterns.

## Overview

These five git commands provide a diagnostic picture of a project before opening any files:
- Who built it and who maintains it now
- Where problems cluster
- Whether the team is shipping with confidence or avoiding certain areas
- Which files are high-risk to modify

## Command 1: What Changes the Most

```bash
git log --format=format: --name-only --since="1 year ago" | sort | uniq -c | sort -nr | head -20
```

**Purpose:** Shows the 20 most-changed files in the last year.

**What to look for:**
- The file at the top is often the one team members warn about: "Everyone's afraid to touch it"
- High churn doesn't always mean bad code (could be active development)
- High churn on a file nobody wants to own = clearest signal of codebase drag
- These files often have unpredictable blast radius for small edits
- Team members pad estimates because they know these files "fight back"

**Why it matters:** A [2005 Microsoft Research study](https://www.microsoft.com/en-us/research/publication/use-of-relative-code-churn-measures-to-predict-system-defect-density/) found that churn-based metrics predict defects more reliably than complexity metrics alone.

**Cross-reference strategy:** Take the top 5 files from this list and compare against the bug hotspot command (Command 3). A file that's high-churn **and** high-bug is your single biggest risk.

## Command 2: Who Built This

```bash
git shortlog -sn --no-merges
```

**Purpose:** Ranks every contributor by commit count.

**What to look for:**
- If one person accounts for 60% or more of commits, that's your **bus factor risk**
- If the top contributor left six months ago, it's a crisis
- Compare overall shortlog with recent activity: `git shortlog -sn --no-merges --since="6 months ago"`
- If the top contributor from overall history doesn't appear in the 6-month window, flag this immediately
- Look at the tail: 30 contributors but only 3 active in the last year means the people who built the system aren't maintaining it

**Caveat:** Squash-merge workflows compress authorship. If the team squashes every PR into a single commit, this output reflects who **merged**, not who wrote. Ask about merge strategy before drawing conclusions.

## Command 3: Where Do Bugs Cluster

```bash
git log -i -E --grep="fix|bug|broken" --name-only --format='' | sort | uniq -c | sort -nr | head -20
```

**Purpose:** Same shape as the churn command, but filtered to commits with bug-related keywords.

**What to look for:**
- Compare this list against the churn hotspots (Command 1)
- Files appearing on both lists = highest-risk code
- These files keep breaking and getting patched but never properly fixed
- Indicates technical debt that needs refactoring, not more patches

**Caveat:** Depends on commit message discipline. If the team writes "update stuff" for every commit, you'll get nothing useful. Even a rough map of bug density is better than no map.

**Variations for different commit conventions:**
```bash
# For teams using Conventional Commits (fix: prefix)
git log --grep="^fix:" --name-only --format='' | sort | uniq -c | sort -nr | head -20

# For broader bug-related keywords
git log -i --grep="bug\|fix\|broken\|patch\|workaround" --name-only --format='' | sort | uniq -c | sort -nr | head -20

# Case-insensitive with extended regex
git log -i -E --grep="fix|bug|broken|patch|workaround|hotfix" --name-only --format='' | sort | uniq -c | sort -nr | head -20
```

## Command 4: Is This Project Accelerating or Dying

```bash
git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c
```

**Purpose:** Shows commit count by month for the entire repository history.

**What to look for:**
- **Steady rhythm** = healthy project
- **Count drops by half in a single month** = usually someone left
- **Declining curve over 6-12 months** = team losing momentum
- **Periodic spikes followed by quiet months** = team batches work into releases instead of continuous shipping

**Why it matters:** This is **team data, not code data**. Showing this chart to stakeholders often reveals insights they hadn't connected before. Example: A CTO recognized "that's when we lost our second senior engineer" after seeing the velocity chart.

**Time range variations:**
```bash
# Last 6 months only
git log --format='%ad' --date=format:'%Y-%m' --since="6 months ago" | sort | uniq -c

# Last year with better formatting
git log --format='%ad' --date=format:'%Y-%m' --since="1 year ago" | sort | uniq -c | sort -r

# Visual histogram (if gnuplot available)
git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c | gnuplot -e "set style data histograms; plot '-' using 1:titlenew('Commits per month')"
```

## Command 5: How Often Is the Team Firefighting

```bash
git log --oneline --since="1 year ago" | grep -iE 'revert|hotfix|emergency|rollback'
```

**Purpose:** Shows revert and hotfix frequency.

**What to look for:**
- **A handful over a year** = normal
- **Reverts every couple of weeks** = team doesn't trust deploy process
- **Zero results** = either the team is stable, or nobody writes descriptive commit messages (check other commands to determine which)

**Why it matters:** Frequent reverts are evidence of deeper issues:
- Unreliable tests
- Missing staging environment
- Deploy pipeline that makes rollbacks harder than they should be
- Lack of confidence in deployment process

**Crisis patterns are easy to read** - either they're there or they're not.

**Variations:**
```bash
# Count by month
git log --oneline --since="1 year ago" | grep -iE 'revert|hotfix|emergency|rollback' | cut -d' ' -f2 | sort | uniq -c

# For Conventional Commits (revert: type)
git log --grep="^revert:" --oneline --since="1 year ago"

# Include more crisis keywords
git log --oneline --since="1 year ago" | grep -iE 'revert|hotfix|emergency|rollback|urgent|critical|p0'
```

## Combined Analysis Workflow

Run these commands in sequence for a complete diagnostic:

```bash
#!/bin/bash
# Codebase diagnostic script

echo "=== 1. Most Changed Files (Last Year) ==="
git log --format=format: --name-only --since="1 year ago" | sort | uniq -c | sort -nr | head -20

echo -e "\n=== 2. Contributors by Commit Count ==="
git shortlog -sn --no-merges

echo -e "\n=== 3. Recent Contributors (Last 6 Months) ==="
git shortlog -sn --no-merges --since="6 months ago"

echo -e "\n=== 4. Bug Hotspots ==="
git log -i -E --grep="fix|bug|broken" --name-only --format='' | sort | uniq -c | sort -nr | head -20

echo -e "\n=== 5. Commit Velocity by Month ==="
git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c | sort -r | head -24

echo -e "\n=== 6. Firefighting Frequency (Last Year) ==="
git log --oneline --since="1 year ago" | grep -iE 'revert|hotfix|emergency|rollback' | wc -l
```

## Interpreting Results

### High-Risk Indicators

| Pattern | Risk Level | Action |
|---------|------------|--------|
| Top 5 churn files overlap with top 5 bug files | **Critical** | Prioritize refactoring these files |
| Single contributor >60% of commits, left 6+ months ago | **Critical** | Document knowledge transfer needs immediately |
| Reverts every 2 weeks or more | **High** | Audit deploy process and test coverage |
| Commit count declining 6+ months | **High** | Investigate team morale and resource allocation |
| 30+ contributors, only 3 active last year | **Medium** | Plan knowledge transfer from original authors |

### Healthy Indicators

| Pattern | Signal |
|---------|--------|
| Steady commit rhythm month-over-month | Team has sustainable pace |
| Top contributor still active in recent window | Knowledge retention |
| Few reverts (<5 per year) | Confident deploy process |
| Churn distributed across many files | No single point of failure |
| Bug fixes concentrated in new features | Old code is stable |

## Integration with Conventional Commits

If the team uses [Conventional Commits](https://www.conventionalcommits.org/), these commands become more accurate:

```bash
# Bug hotspots using conventional commit types
git log --grep="^fix:" --name-only --format='' | sort | uniq -c | sort -nr | head -20

# Breaking changes frequency
git log --grep="BREAKING CHANGE" --oneline --since="1 year ago"

# Feature velocity by scope
git log --grep="^feat(" --oneline --since="1 year ago" | grep -oP 'feat\(\K[^)]+' | sort | uniq -c | sort -nr

# Revert frequency (conventional format)
git log --grep="^revert:" --oneline --since="1 year ago"
```

## Time Range Quick Reference

| Time Range | Parameter | Use Case |
|------------|-----------|----------|
| Last week | `--since="1 week ago"` | Recent activity check |
| Last month | `--since="1 month ago"` | Sprint/iteration analysis |
| Last quarter | `--since="3 months ago"` | Quarterly review |
| Last 6 months | `--since="6 months ago"` | Bus factor assessment |
| Last year | `--since="1 year ago"` | Annual trend analysis |
| All time | (no parameter) | Complete history |

## Advanced Analysis Techniques

### Cross-Reference Churn and Bugs

The most powerful insight comes from comparing Command 1 (churn) with Command 3 (bugs):

```bash
# Save both lists for comparison
git log --format=format: --name-only --since="1 year ago" | sort | uniq -c | sort -nr | head -20 > /tmp/churn.txt
git log -i -E --grep="fix|bug|broken" --name-only --format='' | sort | uniq -c | sort -nr | head -20 > /tmp/bugs.txt

# Find files that appear in both (highest risk)
comm -12 <(cut -d' ' -f2- /tmp/churn.txt | sort) <(cut -d' ' -f2- /tmp/bugs.txt | sort)
```

Files appearing on both lists are your **highest-risk code**: they keep breaking and keep getting patched, but never get properly fixed. These need refactoring, not more patches.

### Bus Factor Deep Dive

```bash
# Overall contributor distribution
git shortlog -sn --no-merges | head -10

# Recent activity (last 6 months)
git shortlog -sn --no-merges --since="6 months ago" | head -10

# Calculate bus factor: what % does top contributor represent?
git shortlog -sn --no-merges | awk 'NR==1 {top=$1} END {total=0} {total+=$1} END {printf "Top contributor: %.1f%%\n", (top/total)*100}'
```

**Interpretation:**
- **>60% by one person**: Critical bus factor risk
- **>40% by one person**: High risk if they leave
- **<30% distributed**: Healthy knowledge distribution

### Detect Team Turnover

```bash
# See when contributors last committed
git log --format='%an %ad' --date=format:'%Y-%m' | sort -u | grep -v '^$'

# Find contributors who haven't committed in 6+ months
git log --since="6 months ago" --format='%an' | sort -u > /tmp/recent_authors.txt
git log --format='%an' | sort -u > /tmp/all_authors.txt
comm -23 /tmp/all_authors.txt /tmp/recent_authors.txt
```

This reveals the "ghost contributors" - people who built the system but aren't maintaining it anymore.

### Crisis Pattern Detection

```bash
# Count emergency commits by month
git log --oneline --since="1 year ago" | grep -iE 'revert|hotfix|emergency|rollback' | cut -d' ' -f2 | sort | uniq -c | sort -r

# Find longest streak without emergencies (stability periods)
git log --format='%ad %s' --date=format:'%Y-%m-%d' --since="1 year ago" | \
  grep -ivE 'revert|hotfix|emergency|rollback' | \
  awk '{print $1}' | sort | uniq
```

## Automation and Reporting

### Create a Diagnostic Script

Save this as `scripts/codebase-health.sh`:

```bash
#!/bin/bash
# Codebase Health Diagnostic Script
# Run from repository root

echo "========================================"
echo "CODEBASE HEALTH DIAGNOSTIC"
echo "Generated: $(date)"
echo "Repository: $(git remote get-url origin 2>/dev/null || echo 'local')"
echo "========================================\n"

echo "1. CHURN HOTSPOTS (Top 10 most-changed files)"
echo "----------------------------------------------"
git log --format=format: --name-only --since="1 year ago" | sort | uniq -c | sort -nr | head -10

echo -e "\n2. BUS FACTOR ANALYSIS"
echo "----------------------------------------------"
echo "Overall contributors:"
git shortlog -sn --no-merges | head -5
echo -e "\nRecent (last 6 months):"
git shortlog -sn --no-merges --since="6 months ago" | head -5

echo -e "\n3. BUG HOTSPOTS (Top 10)"
echo "----------------------------------------------"
git log -i -E --grep="fix|bug|broken" --name-only --format='' | sort | uniq -c | sort -nr | head -10

echo -e "\n4. COMMIT VELOCITY (Last 12 months)"
echo "----------------------------------------------"
git log --format='%ad' --date=format:'%Y-%m' --since="1 year ago" | sort | uniq -c | sort -r

echo -e "\n5. FIREFIGHTING FREQUENCY"
echo "----------------------------------------------"
echo "Emergency commits in last year:"
git log --oneline --since="1 year ago" | grep -iE 'revert|hotfix|emergency|rollback' | wc -l
echo -e "\nDetails:"
git log --oneline --since="1 year ago" | grep -iE 'revert|hotfix|emergency|rollback'

echo -e "\n========================================"
echo "ANALYSIS COMPLETE"
echo "========================================"
```

Make it executable: `chmod +x scripts/codebase-health.sh`

## When to Use These Commands

### Before Starting on a New Codebase
- Run all 5 commands in the first hour
- Identify which files to read first (churn hotspots)
- Understand team structure and knowledge distribution
- Spot technical debt that needs addressing

### During Code Review
- Check if the file being reviewed is a known hotspot
- Consider extra testing for high-churn files
- Flag files that appear in both churn and bug lists

### When Investigating Recurring Issues
- Use Command 3 to see if bugs cluster in specific areas
- Cross-reference with Command 1 to understand maintenance burden
- Check Command 5 to see if team is in "firefighting mode"

### For Team Planning
- Use Command 4 to identify momentum shifts
- Command 2 helps plan knowledge transfer sessions
- Command 5 informs capacity planning (how much time goes to fixes vs features)

## Related Resources

- [Original article by Ally Piechowski](https://piechowski.io/post/git-commands-before-reading-code/)
- [Microsoft Research: Code Churn and Defect Prediction](https://www.microsoft.com/en-us/research/publication/use-of-relative-code-churn-measures-to-predict-system-defect-density/)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [How I Audit a Legacy Rails Codebase in the First Week](https://piechowski.io/post/how-i-audit-a-legacy-rails-codebase/)

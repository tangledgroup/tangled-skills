# Codebase Analysis with Git

This reference covers Git archaeology and codebase health diagnostics — using git commands to understand a project's history, identify risk areas, and assess team dynamics before reading any source code.

## Why Analyze Before Reading?

The first thing you should do when picking up a new codebase isn't opening the code — it's opening a terminal and running a handful of git commands. Within minutes, you'll know:
- Which files to read first
- Where problems cluster
- Whether the team is shipping with confidence or tiptoeing around landmines

## 1. What Changes the Most (Churn Hotspots)

Identify the most frequently modified files — these are often where everyone's afraid to make changes.

```bash
git log --format=format: --name-only --since="1 year ago" \
  | sort | uniq -c | sort -nr | head -20
```

**Interpretation:** The file at the top is almost always the one people warn you about. "Oh yeah, that file. Everyone's afraid to touch it."

High churn on a file doesn't mean it's bad — sometimes it's just active development. But high churn on a file that nobody wants to own is the clearest signal of codebase drag: every change is a patch on a patch, and the blast radius of a small edit is unpredictable.

**A 2005 Microsoft Research study found churn-based metrics predicted defects more reliably than complexity metrics alone.** Cross-reference with the bug hotspot command below — a file that's high-churn AND high-bug is your single biggest risk.

## 2. Who Built This (Bus Factor)

Rank every contributor by commit count to identify knowledge concentration.

```bash
git shortlog -sn --no-merges
```

**Interpretation:** If one person accounts for 60% or more, that's your bus factor risk. If they left six months ago, it's a crisis. Check the tail of the list — thirty contributors but only three active in the last year means the people who built this system aren't the people maintaining it.

**Caveat:** Squash-merge workflows compress authorship. If the team squashes every PR into a single commit, this output reflects who merged, not who wrote. Ask about the merge strategy before drawing conclusions.

### Check Recent Activity

```bash
git shortlog -sn --no-merges --since="6 months ago"
```

If the top contributor from the overall list doesn't appear in a 6-month window, flag that immediately.

## 3. Where Do Bugs Cluster (Bug Density)

Map commits with bug-related keywords to identify files that keep breaking.

```bash
git log -i -E --grep="fix|bug|broken" --name-only --format='' \
  | sort | uniq -c | sort -nr | head -20
```

**Interpretation:** Compare this list against the churn hotspots. Files that appear on **both** lists are your highest-risk code: they keep breaking and keep getting patched, but never get properly fixed.

**Caveat:** This depends on commit message discipline. If the team writes "update stuff" for every commit, you'll get nothing. But even a rough map of bug density is better than no map.

## 4. Is the Project Accelerating or Dying (Velocity)

View commit count by month to see the project's activity timeline.

```bash
git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c
```

**Interpretation — scan for shapes:**
- **Steady rhythm** = healthy, consistent development
- **Count drops by half in a single month** = someone left
- **Declining curve over 6–12 months** = team is losing momentum
- **Periodic spikes followed by quiet months** = the team batches work into releases instead of shipping continuously

This is team data, not code data. A declining velocity chart once revealed to a CTO that their dip corresponded exactly with "when we lost our second senior engineer" — they hadn't connected the timeline before.

## 5. How Often Is the Team Firefighting (Revert/Hotfix Frequency)

Count emergency commits that signal an unreliable deploy process.

```bash
git log --oneline --since="1 year ago" \
  | grep -iE 'revert|hotfix|emergency|rollback'
```

**Interpretation:**
- **A handful over a year** = normal
- **Reverts every couple of weeks** = the team doesn't trust its deploy process; evidence of unreliable tests, missing staging, or a pipeline that makes rollbacks harder than they should be
- **Zero results** = either the team is stable, or nobody writes descriptive commit messages

Crisis patterns are easy to read. Either they're there or they're not.

## Code Archaeology Commands

Beyond the five diagnostic commands above, these Git commands help you explore any codebase:

```bash
git log main                                    # Show commits on a branch
git log --graph main                            # Graph view of branch history
git log --oneline                               # Compact one-line-per-commit view
git log <file>                                  # Every commit that modified a file
git log --follow <file>                         # Track file across renames
git log -G banana                               # Commits that added/removed text matching pattern
git blame <file>                                # Who last changed each line of a file
```

## Putting It All Together — The First-Minute Audit

Run these commands in order when starting work on a new codebase:

```bash
# 1. What changes the most? (churn)
git log --format=format: --name-only --since="1 year ago" | sort | uniq -c | sort -nr | head -20

# 2. Who built this? (bus factor)
git shortlog -sn --no-merges

# 3. Where do bugs cluster? (bug density)
git log -i -E --grep="fix|bug|broken" --name-only --format='' | sort | uniq -c | sort -nr | head -20

# 4. Is the project accelerating or dying? (velocity)
git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c

# 5. How often is the team firefighting? (reverts/hotfixes)
git log --oneline --since="1 year ago" | grep -iE 'revert|hotfix|emergency|rollback'
```

These five commands take a couple minutes to run. They won't tell you everything, but you'll know which code to read first and what to look for when you get there. That's the difference between spending your first day reading methodically versus wandering.

**Source:** Inspired by [The Git Commands I Run Before Reading Any Code](https://piechowski.io/post/git-commands-before-reading-code/) by Ally Piechowski.

See [Core Git Commands](../01-core-git-commands.md) for detailed command syntax and options.
See [History Rewriting](../06-history-rewriting.md) for understanding and manipulating the history you're analyzing.

# Codebase Diagnostics

Before reading code in a new project, run these five commands:

## What Changes the Most (Code Churn Hotspots)

```bash
git log --format=format: --name-only --since="1 year ago" | sort | uniq -c | sort -nr | head -20
```

## Who Built This (Bus Factor)

```bash
git shortlog -sn --no-merges
```

## Where Do Bugs Cluster

```bash
git log -i -E --grep="fix|bug|broken" --name-only --format='' | sort | uniq -c | sort -nr | head -20
```

## Project Velocity Over Time

```bash
git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c
```

## How Often Is the Team Firefighting

```bash
git log --oneline --since="1 year ago" | grep -iE 'revert|hotfix|emergency|rollback'
```

Cross-reference churn hotspots with bug clusters: files on both lists are highest-risk code.

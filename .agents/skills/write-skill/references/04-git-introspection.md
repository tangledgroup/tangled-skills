# Git Introspection for Codebase Enhancement

This reference covers git-based project introspection techniques to enhance codebase understanding after initial directory analysis. Based on [Git Commands Before Reading Code](https://piechowski.io/post/git-commands-before-reading-code/).

**Purpose**: Use git metadata to validate and refine skill content by understanding file importance, activity patterns, and key contributors. This provides context that helps prioritize which files to read deeply and which areas are most critical.

## When to Use

Run git introspection **after** initial directory scanning when:
- Analyzing a codebase for skill generation
- Needing to validate discovered patterns against actual usage
- Working with existing git repositories
- Wanting to identify active vs stable areas
- Determining key contributors and ownership patterns
- Refining skill content based on file importance

**Skip if**: Project is not a git repository (directory analysis provides sufficient information)

## Quick Start Workflow

After initial directory scanning, run these git commands to **enhance understanding**:

```bash
# Step 1: Check if it's a git repository
git status 2>/dev/null || echo "Not a git repository"

# Step 2: Get high-level project overview
git log --oneline | head -20              # Recent commits
git branch -a                             # All branches
git tag                                   # Version tags

# Step 3: Understand file importance
git log --all --oneline --name-only | \
  awk '{print $NF}' | sort | uniq -c | \
  sort -rn | head -30                    # Most modified files

# Step 4: Identify active areas
git log --all --since="6 months ago" \
  --oneline --name-only | awk '{print $NF}' | \
  sort | uniq -c | sort -rn | head -20   # Recently touched files

# Step 5: Find key contributors
git shortlog -sn --all                   # Commits by author
```

See [Detailed Commands](#detailed-git-commands) below for complete command reference.

## Detailed Git Commands

### Repository Status and Branches

```bash
# Basic repository info
git status
git remote -v                           # Remote URLs
git branch -a                           # All branches (local + remote)
git tag -l                              # All tags

# Current branch context
git branch --show-current
git log --oneline -10                   # Last 10 commits on current branch
```

### Commit History Analysis

```bash
# Recent activity
git log --oneline | head -30            # Simple commit list
git log --graph --oneline --all | head -50  # Visual branch history

# Time-based analysis
git log --since="1 year ago" --oneline  # Last year
git log --since="6 months ago" --oneline  # Last 6 months
git log --since="3 months ago" --oneline  # Last 3 months
git log --since="1 month ago" --oneline   # Last month

# Commit patterns
git log --format="%ai %s" | head -20    # Date + message
git log --format="%an %s" | head -20    # Author + message
git log --all --oneline --grep="feat:"  # Feature commits
git log --all --oneline --grep="fix:"   # Bug fixes

# Commit frequency
git shortlog -sn --all                  # Total commits per author
git log --all --author="name" --oneline # Commits by specific author
```

### File Importance Discovery

**Most critical**: Identify files that change frequently (likely core logic):

```bash
# All-time most modified files
git log --all --oneline --name-only | \
  awk '{print $NF}' | sort | uniq -c | \
  sort -rn | head -30

# Most modified in last 6 months
git log --all --since="6 months ago" \
  --oneline --name-only | awk '{print $NF}' | \
  sort | uniq -c | sort -rn | head -20

# Most modified in last year (find stable vs active areas)
git log --all --since="1 year ago" \
  --oneline --name-only | awk '{print $NF}' | \
  sort | uniq -c | sort -rn | head -30

# Filter by file type
git log --all --oneline --name-only \
  -- "*.py" | awk '{print $NF}' | sort | uniq -c | sort -rn | head -20
git log --all --oneline --name-only \
  -- "*.js" | awk '{print $NF}' | sort | uniq -c | sort -rn | head -20
git log --all --oneline --name-only \
  -- "*.go" | awk '{print $NF}' | sort | uniq -c | sort -rn | head -20
```

### Directory Activity Analysis

```bash
# Most active directories
git log --all --oneline --name-only | \
  awk -F'/' '{print $1}' | sort | uniq -c | \
  sort -rn | head -20

# Top-level directory breakdown
git log --all --oneline --name-only | \
  awk -F'/' 'NF>0 {print $1}' | sort | uniq -c | \
  sort -rn | head -15

# Recent directory activity (last 3 months)
git log --all --since="3 months ago" \
  --oneline --name-only | awk -F'/' '{print $1"/"$2}' | \
  sort | uniq -c | sort -rn | head -20
```

### File Type Distribution

```bash
# Count files by extension (from git history)
git log --all --oneline --name-only | \
  awk '{print $NF}' | grep '\.' | \
  sed 's/.*\.//' | sort | uniq -c | \
  sort -rn | head -20

# Count by extension in recent commits
git log --all --since="6 months ago" \
  --oneline --name-only | awk '{print $NF}' | \
  grep '\.' | sed 's/.*\.//' | sort | uniq -c | \
  sort -rn | head -15
```

### Author and Contributor Analysis

```bash
# Top contributors by commit count
git shortlog -sn --all                  # All time
git shortlog -sn --since="1 year ago"   # Last year
git shortlog -sn --since="6 months ago" # Last 6 months

# Contributors to specific directories
git log --all --oneline -- "src/" | \
  awk '{print $3}' | sort | uniq -c | sort -rn

# Author email distribution
git log --all --format="%ae" | sort | uniq -c | sort -rn | head -10
```

### Code Changes Analysis

```bash
# Lines added/removed by file (all time)
git log --all --numstat --oneline | \
  awk 'NF==3 {added[$3]+=$1; removed[$3]+=$2} 
       END {for (f in added) print added[f], removed[f], f}' | \
  sort -rn | head -20

# Files with most churn (additions + deletions)
git log --all --numstat --oneline | \
  awk 'NF==3 {total[$3]+=$1+$2} 
       END {for (f in total) print total[f], f}' | \
  sort -rn | head -20

# Recent changes (last month)
git log --all --since="1 month ago" \
  --numstat --oneline | awk 'NF==3 {total[$3]+=$1+$2} 
                             END {for (f in total) print total[f], f}' | \
  sort -rn | head -15
```

### Branch-Specific Analysis

```bash
# Compare branches
git log main..feature-branch --oneline    # Commits in feature not in main
git diff --stat main feature-branch       # Stats between branches

# Files changed on specific branch
git log --all --oneline --name-only \
  main..feature-branch | awk '{print $NF}' | sort | uniq -c

# Active development branches (recent commits)
git for-each-ref --sort=-committerdate --format='%(refname:short) %(committerdate:short)' refs/heads/ | head -10
```

### Tag and Release Analysis

```bash
# All tags with dates
git tag -l --sort=-creatordate | head -20

# Commits between tags
git log v1.0..v2.0 --oneline              # Changes between versions
git diff --stat v1.0..v2.0                # Stats between versions

# Latest tag on current branch
git describe --tags --abbrev=0 2>/dev/null

# Tag frequency
git tag -l | awk -F'.' '{print $1"."$2}' | sort | uniq -c | sort -rn
```

### Search in Commit History

```bash
# Find commits by message content
git log --all --oneline --grep="authentication"
git log --all --oneline --grep="API" --grep="endpoint"
git log --all --oneline --grep="refactor"

# Find who last modified a file
git log -1 --format="%an %ae %s" -- path/to/file.py

# Find when a file was added
git log --all --diff-filter=A --follow --name-only -- path/to/file | tail -5

# Blame analysis (who wrote each line)
git blame path/to/important-file.py | head -30
```

### Repository Statistics

```bash
# Total commits and contributors
git log --all --shortstat | tail -1       # Summary stats
git log --all --format="%an" | sort | uniq | wc -l  # Unique authors

# Lines of code by extension (approximate)
git log --all --numstat | \
  awk 'NF==3 {ext=split($3,a,"."); ext=a[length(a); total[ext]+=$1+$2} 
       END {for (e in total) print e, total[e]}' | sort -rn

# Repository age
git log --all --reverse --format="%ai" | head -1   # First commit date
git log --all --format="%ai" | tail -1             # Last commit date
```

## Interpreting Results for Skill Generation

### File Importance Patterns

| Pattern | Interpretation | Action in Skill |
|---------|----------------|-----------------|
| High modification count | Core logic, frequently changed | Read these files first, document prominently |
| Recent activity (last 3 months) | Active development area | Highlight as current/focus areas |
| Stable files (no recent changes) | Mature, tested code | Reference as stable patterns |
| Files touched by many authors | Collaborative areas, critical paths | Note team collaboration points |

### Directory Patterns

| Pattern | Interpretation | Action in Skill |
|---------|----------------|-----------------|
| `src/` or `lib/` most active | Core implementation | Focus skill on these patterns |
| `test/` or `__tests__/` large | Well-tested codebase | Include testing patterns in skill |
| `docs/` frequently updated | Documentation-focused project | Extract docs for reference files |
| `scripts/` or `tools/` active | Automation-heavy workflow | Document helper scripts and automation |

### Commit Message Patterns

| Pattern | Interpretation | Action in Skill |
|---------|----------------|-----------------|
| Many `feat:` commits | Feature-rich, active development | Document feature set comprehensively |
| Many `fix:` commits | Bug-prone areas or legacy code | Note troubleshooting and edge cases |
| Many `refactor:` commits | Code quality focus | Document architectural decisions |
| Many `docs:` commits | Documentation-first culture | Prioritize documentation extraction |

### Author Patterns

| Pattern | Interpretation | Action in Skill |
|---------|----------------|-----------------|
| Single dominant author | Personal project or maintainer-driven | Note ownership and decision patterns |
| Many equal contributors | Team project, distributed ownership | Document collaboration workflows |
| Recent new authors | Active onboarding or team growth | Note contribution guidelines importance |

## Workflow Integration

### After Initial Directory Scanning

1. **Run directory analysis first** - Discover configs, scripts, env vars
2. **Extract initial patterns** - Identify workflows from content
3. **Run git introspection** (5-10 minutes of commands) - Validate and enhance understanding
4. **Identify top 10 most modified files** - Read these deeply for critical patterns
5. **Find active directories** - Focus on recent activity areas
6. **Check commit messages** - Understand project goals and evolution
7. **Identify key contributors** - Know who to reference for context
8. **Refine skill content** - Prioritize based on file importance

### After Directory Analysis, Before Deep Reading

```bash
# Create a reading priority list
echo "=== PRIORITY FILES TO READ ==="
git log --all --since="6 months ago" \
  --oneline --name-only | awk '{print $NF}' | \
  sort | uniq -c | sort -rn | head -10

echo ""
echo "=== RECENT COMMIT MESSAGES (context) ==="
git log --all --oneline -20

echo ""
echo "=== KEY CONTRIBUTORS ==="
git shortlog -sn --since="6 months ago" | head -5
```

### Generate Skill Structure Based on Git Data

```bash
# Determine if skill should be simple or complex
FILE_COUNT=$(git ls-files | wc -l)
COMMIT_COUNT=$(git log --all --oneline | wc -l)

if [ $FILE_COUNT -gt 100 ] || [ $COMMIT_COUNT -gt 500 ]; then
  echo "Recommendation: Complex skill with references/"
else
  echo "Recommendation: Simple single-file skill"
fi
```

## Comparison: Git vs Directory Analysis

| Aspect | Git Introspection | Directory Scanning (05-directory-analysis.md) |
|--------|-------------------|-----------------------------------------------|
| **Speed** | Very fast (metadata only) | Slower (reads file contents) |
| **Context** | Historical patterns, importance | Current state, configurations |
| **Best for** | Validating and prioritizing content | Extracting actual content and patterns |
| **Use when** | After initial directory scan | First step in codebase analysis |
| **Requires** | Git repository access | File system access only |

## Combined Workflow

For comprehensive skill generation:

1. **Directory analysis first** - Scan structure, discover configs, extract patterns
2. **Initial skill draft** - Generate basic skill from discovered content
3. **Git introspection** (if repository) - Validate and enhance understanding
4. **Read priority files** - Focus on top modified files for critical patterns
5. **Pattern refinement** - Cross-reference git importance with directory findings
6. **Generate final skill** - Use combined information

```bash
# Complete workflow example
echo "=== STEP 1: DIRECTORY ANALYSIS ==="
find . -name "*.yaml" -o -name "*.json" -o -name "Dockerfile*" | head -20
grep -r "process\.env\|os\.environ" --include="*.js" --include="*.py" | head -30

echo ""
echo "=== STEP 2: INITIAL PATTERN EXTRACTION ==="
# Extract configs, env vars, dependencies from discovered files

echo ""
echo "=== STEP 3: GIT INTROSPECTION (if repo) ==="
git log --all --oneline --name-only | \
  awk '{print $NF}' | sort | uniq -c | sort -rn | head -20

echo ""
echo "=== STEP 4: READ PRIORITY FILES ==="
# Read files identified from git history for deep understanding

echo ""
echo "=== STEP 5: REFINE AND GENERATE SKILL ==="
# Combine directory patterns with git importance data
```

## Limitations

- **Requires git repository** - Won't work on non-git codebases
- **No content analysis** - Only metadata, not actual code understanding
- **History-dependent** - New repos have limited data
- **Private repos** - May need authentication for remote info
- **Shallow clones** - Limited history if `--depth` was used

## Summary

- **Run after directory analysis** - Use git to enhance initial findings
- **Focus on frequency** - Most modified files = most important
- **Check recency** - Recent activity shows current focus areas
- **Understand contributors** - Know who maintains what
- **Validate patterns** - Cross-reference git history with discovered content
- **Refine skill content** - Prioritize based on combined information

This approach validates and enhances directory analysis by understanding which files are most critical through git history, ensuring the generated skill focuses on the most important aspects of the codebase.

See [Directory Analysis](05-directory-analysis.md) for the initial scanning step.

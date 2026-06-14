# GitGraph Diagrams

Pictorial representation of git commits and branch operations. Useful for visualizing branching strategies (Git Flow, GitHub Flow, etc.).

## Commands

| Command | Description |
| --- | --- |
| `commit` | New commit on current branch |
| `branch <name>` | Create and switch to new branch |
| `checkout <name>` | Switch to existing branch (`switch` is alias) |
| `merge <name>` | Merge branch into current branch (creates merge commit) |
| `cherry-pick id: "<id>"` | Cherry-pick commit from another branch |

## Commit attributes

```
commit id: "Alpha"
commit type: HIGHLIGHT
commit tag: "v1.0.0"
commit id: "RC_1" type: REVERSE tag: "Release Candidate"
```

### Commit types

| Type | Rendering |
| --- | --- |
| `NORMAL` (default) | Solid circle |
| `REVERSE` | Crossed solid circle |
| `HIGHLIGHT` | Filled rectangle |

## Merge attributes

```
merge develop id: "customID" tag: "customTag" type: REVERSE
```

Same attributes as commits (`id`, `type`, `tag`). Merge commits render as filled double circles by default.

## Cherry-pick

```
cherry-pick id: "MERGE" parent: "B"
```

Rules:
- Must specify `id` of existing commit from a different branch
- Current branch must have at least one commit
- For merge commits, `parent` attribute is mandatory (must be an immediate parent)

## Branch ordering

```
branch test1 order: 3
branch test2 order: 2
branch test3 order: 1
```

Ordering precedence: main branch first (default order 0), then branches without `order` in appearance order, then branches with explicit `order` ascending. Use `mainBranchOrder` config to change main's position.

## Orientation

```
gitGraph LR:    %% Left-to-right (default)
gitGraph TB:    %% Top-to-bottom
gitGraph BT:    %% Bottom-to-top (v11.0.0+)
```

## Configuration

```yaml
---
config:
  gitGraph:
    showBranches: true         %% Show/hide branch names and lines
    showCommitLabel: true      %% Show/hide commit labels
    mainBranchName: "main"     %% Default root branch name
    mainBranchOrder: 0         %% Position of main branch
    parallelCommits: false     %% true: commits at same level regardless of order
    rotateCommitLabel: true    %% true: 45-degree rotated labels (default)
---
```

## Theme variables

| Variable | Description |
| --- | --- |
| `git0`–`git7` | Branch colors (up to 8, then cycle) |
| `gitBranchLabel0`–`gitBranchLabel7` | Branch label colors (up to 8, then cycle) |
| `commitLabelColor` | Commit label text color |
| `commitLabelBackground` | Commit label background |
| `commitLabelFontSize` | Commit label font size |
| `tagLabelFontSize` | Tag label font size |

```yaml
---
config:
  themeVariables:
    git0: "#ff0000"
    git1: "#00ff00"
    commitLabelColor: "#ffffff"
    commitLabelBackground: "#333333"
---
```

> Branch styling cycles after 8 branches (9th uses `git0`, etc.).

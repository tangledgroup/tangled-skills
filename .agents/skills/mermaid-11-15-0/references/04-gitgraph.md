# GitGraph Reference

## Description

GitGraph diagrams visualize git commits and branch operations. Helpful for documenting branching strategies (git flow, trunk-based, etc.) and explaining commit history.

> **Note:** `checkout` and `switch` are interchangeable keywords.

## Basic Syntax

```mermaid
gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
    commit
```

## Commands

### commit

Create a new commit on the current branch.

```mermaid
gitGraph
    commit
    commit msg: "Initial commit"
    commit tag: "v1.0.0"
    commit type: HIGHLIGHT
    commit strokefmt: "#00ff00"
```

#### Commit Options

| Option | Description | Example |
|--------|-------------|---------|
| `msg` | Commit message | `commit msg: "Fix bug"` |
| `tag` | Tag on commit | `commit tag: "v1.0.0"` |
| `type` | Commit style | `HIGHLIGHT`, `REVERSE`, `NORMAL` |
| `strokefmt` | Custom stroke color | `strokefmt: "#ff0000"` |

### branch

Create and switch to a new branch.

```mermaid
gitGraph
    commit
    branch develop
    commit
```

### checkout / switch

Switch to an existing branch.

```mermaid
gitGraph
    branch develop
    checkout main
    commit
```

### merge

Merge a branch into the current branch.

```mermaid
gitGraph
    branch feature
    checkout feature
    commit
    checkout main
    merge feature
```

#### Merge Options

| Option | Description | Example |
|--------|-------------|---------|
| `msg` | Merge message | `merge feature msg: "Merge PR #42"` |
| `type` | Merge style | `NORMAL`, `REVERSE`, `HIGHLIGHT` |

### cherry-pick

Cherry-pick commits from another branch.

```mermaid
gitGraph
    branch feature
    checkout feature
    commit id: "A"
    commit id: "B"
    checkout main
    cherry-pick develop
```

### reset

Reset the current branch.

```mermaid
gitGraph
    commit
    branch feature
    checkout feature
    commit
    reset
    checkout main
```

#### Reset Types

| Type | Description |
|------|-------------|
| `soft` | Keep changes staged |
| `mixed` | Keep changes unstaged (default) |
| `hard` | Discard all changes |

## Branch Styling

```mermaid
gitGraph
    commit
    branch develop
    checkout develop
    commit
    branch feature-1
    checkout feature-1
    commit
    checkout main
    merge feature-1
```

### Custom Colors

```mermaid
gitGraph
    commit
    branch develop
    checkout develop
    commit type: HIGHLIGHT
    checkout main
    commit type: REVERSE
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `showBranches` | Show branch labels | `true` |
| `mainBranchName` | Name of default branch | `"main"` |
| `direction` | Layout direction: `LR`, `TB` | `LR` |
| `nodeLargest` | Node size | `30` |
| `commitSpacing` | Space between commits | `250` |
| `diagramPadding` | Padding around diagram | `10` |
| `parallelCommitGap` | Gap for parallel commits | `50` |
| `showCommitLabel` | Show commit messages | `true` |

## Examples

### Git Flow Strategy

```mermaid
gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    commit
    branch release
    checkout release
    commit tag: "v1.0.0"
    checkout main
    merge release
    checkout develop
    merge release
    branch feature-1
    checkout feature-1
    commit
    commit
    checkout develop
    merge feature-1
```

### Hotfix Workflow

```mermaid
gitGraph
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    commit
    branch hotfix
    checkout hotfix
    commit
    checkout main
    merge hotfix tag: "v1.0.1"
    checkout develop
    merge hotfix
```

### Cherry-Pick Example

```mermaid
gitGraph
    commit id: "A"
    commit id: "B"
    branch feature
    checkout feature
    commit id: "C"
    commit id: "D"
    commit id: "E"
    checkout main
    cherry-pick feature
```

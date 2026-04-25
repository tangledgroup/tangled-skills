# Issues & Pull Requests

> **Source:** https://gitea.com/gitea/tea/src/branch/main/docs/CLI.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## issues, issue, i

List, create and update issues.

### Common flags

- `--state` — Filter by state (`all|open|closed`)
- `--fields, -f` — Comma-separated fields: `index,state,kind,author,author-id,url,title,body,created,updated,deadline,assignees,milestone,labels,comments,owner,repo`
- `--output, -o` — Output format: `simple|table|csv|tsv|yaml|json`
- `--limit, --lm` — Items per page (default: 30)
- `--page, -p` — Page number (default: 1)
- `--keyword, -k` — Search string filter
- `--labels, -L` — Comma-separated labels to match
- `--milestones, -m` — Comma-separated milestones to match
- `--assignee, -a` / `--author, -A` / `--mentions, -M` / `--owner, --org` — Filter by user
- `--kind, -K` — Return `issues`, `pulls`, or `all`
- `--from, -F` / `--until, -u` — Filter by activity date range
- `--comments` — Display comments (prompts interactively if omitted)

### list, ls

```bash
tea issues list
tea issue ls --state open --labels bug,critical
tea issue ls --keyword "memory leak" --from 2025-01-01
```

### create, c

```bash
tea issue create --title "Fix crash on startup" \
  --description "App crashes when..." \
  --labels bug,high-priority \
  --assignees alice,bob \
  --milestone "v1.0"
```

Flags: `--title, -t`, `--description, -d`, `--labels, -L`, `--assignees, -a`, `--milestone, -m`, `--deadline, -D`, `--referenced-version, -v`

### edit, e

```bash
tea issue edit 42 --title "Updated title" --add-labels urgent
```

Flags: `--title, -t`, `--description, -d`, `--add-labels, -L`, `--remove-labels`, `--add-assignees, -a`, `--milestone, -m`, `--deadline, -D`, `--referenced-version, -v`

### reopen, open / close

```bash
tea issue reopen 42
tea issue close 42,43,44
```

## pulls, pull, pr

Manage and checkout pull requests.

### Common flags

Same as issues, plus PR-specific fields: `mergeable,base,base-commit,head,diff,patch,ci`

Default fields: `index,title,state,author,milestone,updated,labels`

### list, ls

```bash
tea pr ls
tea pull list --state open --fields index,title,ci,mergeable
```

### create, c

Create a pull request. Defaults to current branch as head and repo default branch as base.

```bash
tea pr create --title "Add feature X" \
  --description "Implements..." \
  --base main --head feature-x \
  --labels enhancement \
  --assignees reviewer1
```

Flags: `--title, -t`, `--description, -d`, `--base, -b`, `--head`, `--labels, -L`, `--assignees, -a`, `--milestone, -m`, `--deadline, -D`, `--referenced-version, -v`

Special: `--agit` for agit-flow PRs, `--topic` for agit topic name, `--allow-maintainer-edits, --edits`

### checkout, co

Locally check out a PR. Creates a local branch if `--branch, -b` is set.

```bash
tea pr checkout 42
tea pr co 42 --branch
```

### clean

Delete local and remote feature branches for closed PRs.

```bash
tea pr clean 42
tea pr clean 42 --ignore-sha   # match by name instead of commit hash
```

### edit, e

Edit PR properties (added in v0.13.0).

```bash
tea pr edit 42 --title "Updated" --add-labels needs-review
```

Flags: `--title, -t`, `--description, -d`, `--add-labels, -L`, `--remove-labels`, `--add-assignees, -a`, `--add-reviewers, -r`, `--remove-reviewers`, `--milestone, -m`, `--deadline, -D`, `--referenced-version, -v`

### reopen, open / close

```bash
tea pr reopen 42
tea pr close 42
```

### review

Interactively review a pull request. Walks through the diff and prompts for approval or changes requested.

```bash
tea pr review 42
```

### approve, lgtm, a

Approve a pull request (add LGTM).

```bash
tea pr approve 42
tea pr lgtm 42
```

### reject

Request changes on a pull request.

```bash
tea pr reject 42 "Please fix the test coverage"
```

### merge, m

Merge a pull request with specified style.

```bash
tea pr merge 42 --style squash
tea pr merge 42 --style rebase --title "My merge message" --message "Detailed body"
```

Merge styles: `merge` (default), `rebase`, `squash`, `rebase-merge`

### review-comments, rc

List review comments on a PR.

```bash
tea pr review-comments 42
tea pr rc 42 --fields id,path,line,body,reviewer
```

Available fields: `id,body,reviewer,path,line,resolver,created,updated,url`

### resolve / unresolve

Mark a review comment as resolved or unresolved (added in v0.14.0).

```bash
tea pr resolve 42 <comment-id>
tea pr unresolve 42 <comment-id>
```

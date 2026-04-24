# Actions, Webhooks, Notifications

> **Source:** https://gitea.com/gitea/tea/src/branch/main/docs/CLI.md, https://gitea.com/gitea/tea/src/branch/main/docs/example-workflows.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## actions, action

Manage repository CI/CD actions.

### secrets, secret

Manage encrypted action secrets.

```bash
tea actions secrets list
tea actions secrets create API_KEY           # prompts for value
tea actions secrets create API_KEY --stdin   # read from stdin
tea actions secrets create API_KEY --file .env  # read from file
tea actions secrets delete API_KEY --confirm
```

### variables, variable, vars, var

Manage action variables (non-secret).

```bash
tea actions variables list
tea actions variables list --name DEPLOY_ENV   # specific variable
tea actions variables set DEPLOY_ENV staging
tea actions variables set URL https://api.example.com --stdin
tea actions variables delete DEPLOY_ENV --confirm
```

### runs, run

Manage workflow runs.

#### list, ls

```bash
tea actions runs list
tea actions runs list --status failure
tea actions runs list --branch main --event push
tea actions runs list --since 24h --actor alice
```

Flags: `--status` (`success|failure|pending|queued|in_progress|skipped|canceled`), `--branch`, `--event`, `--actor`, `--since`, `--until`

#### view, show, get

```bash
tea actions runs view <run-id>
tea actions runs view <run-id> --jobs   # show jobs table
```

#### logs, log

```bash
tea actions runs logs <run-id>
tea actions runs logs <run-id> --job 12345     # specific job
tea actions runs logs <run-id> --follow        # tail -f style
```

#### delete, remove, rm, cancel

```bash
tea actions runs delete <run-id> --confirm
```

### workflows, workflow

Manage repository workflows.

#### list, ls

```bash
tea actions workflows list
```

#### view, show, get

```bash
tea actions workflows view deploy.yml
```

#### dispatch, trigger, run

Trigger a `workflow_dispatch` event (added in v0.14.0).

```bash
tea actions workflows dispatch deploy.yml
tea actions workflows dispatch deploy.yml --ref main
tea actions workflows dispatch deploy.yml --ref main \
  --input env=production --input version=2.0.0
tea actions workflows dispatch ci.yml --follow   # stream logs after dispatch
```

Flags: `--ref, -r` (branch or tag, default: current branch), `--input, -i` (key=value, repeatable), `--follow, -f`

#### enable / disable

```bash
tea actions workflows enable deploy.yml
tea actions workflows disable deploy.yml --confirm
```

## webhooks, webhook, hooks, hook

Manage repository, organization, and global webhooks.

### list, ls

```bash
tea webhooks list
tea webhooks list --org myorg        # org-level webhooks
tea webhooks list --global           # global webhooks
```

### create, c

```bash
tea webhook create https://example.com/hook \
  --events push,pull_request \
  --type gitea \
  --secret my-secret \
  --active
```

Flags: `--events` (comma-separated, default: `push`), `--type` (`gitea|gogs|slack|discord|dingtalk|telegram|msteams|feishu|wechatwork|packagist`), `--secret`, `--active`, `--branch-filter`, `--authorization-header`

Scope flags: `--org` (organization), `--global`

### update, edit, u

```bash
tea webhook update <id> --url https://new-url.com/hook
tea webhook update <id> --events push,push,pull_request --inactive
```

Flags: `--url`, `--events`, `--secret`, `--active`, `--inactive`, `--branch-filter`, `--authorization-header`

### delete, rm

```bash
tea webhook delete <id> --confirm
```

## notifications, notification, n

Show and manage notifications.

### list, ls

```bash
tea notifications
tea n --mine                           # across all your repos
tea n --states unread,pinned           # filter by state
tea n --types issue,pull               # filter by type
tea n --fields id,status,index,type,state,title
```

Flags: `--mine, -m` (all repos), `--states, -s` (`pinned|unread|read`, default: `unread,pinned`), `--types, -t` (`issue|pull|repository|commit`), `--fields, -f`

### read, r / unread, u

```bash
tea notifications read                 # mark filtered as read
tea notifications read 42              # mark specific notification
tea n unread 42                        # mark as unread
```

### pin, p / unpin

```bash
tea notifications pin 42
tea notifications unpin 42
```

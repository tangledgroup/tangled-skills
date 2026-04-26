# Command Reference

## Setup Commands

### login / logins

Manage Gitea server logins. Configuration is stored in `$XDG_CONFIG_HOME/tea/config.yml`.

```bash
tea login list                    # list saved logins
tea login add                     # interactive login wizard
tea login add --token <token>     # login with application token
tea login add --oauth             # interactive OAuth2 flow (Gitea 0.10+)
tea login add --ssh-agent-key     # login via SSH agent
tea login edit                    # edit a login
tea login delete                  # remove a login
tea login default                 # get or set default login
```

Flags for `login add`:

- `--url` / `-u` — server URL (default: `https://gitea.com`)
- `--token` / `-t` — access token
- `--user` — username for basic auth
- `--password` / `--pwd` — password for basic auth
- `--oauth` / `-o` — use OAuth2 flow
- `--client-id` — OAuth client ID
- `--redirect-url` — OAuth redirect URL
- `--scopes` — comma-separated token scopes
- `--ssh-agent-key` / `-a` — SSH key fingerprint from agent
- `--ssh-key` / `-s` — path to SSH key file
- `--insecure` / `-i` — disable TLS verification
- `--otp` — OTP token for MFA
- `--name` / `-n` — login name alias
- `--no-version-check` / `--nv` — skip version check
- `--helper` / `-j` — add helper

### logout

```bash
tea logout                        # log out from a Gitea server
```

### whoami

```bash
tea whoami                        # show current logged-in user
```

## Issues (`issues`, `issue`, `i`)

List, create, and update issues.

```bash
tea issues list                   # list issues (default action)
tea issues create                 # create an issue
tea issues edit 42                # edit issue #42
tea issues close 42               # close issue #42
tea issues reopen 42              # reopen issue #42
```

List filters:

- `--state` — filter by state (`all`, `open`, `closed`)
- `--assignee` / `-a` — filter by assignee
- `--author` / `-A` — filter by author
- `--labels` / `-L` — comma-separated labels to match
- `--milestones` / `-m` — comma-separated milestones to match
- `--keyword` / `-k` — search string
- `--from` / `-F` — activity after this date
- `--until` / `-u` — activity before this date
- `--mentions` / `-M` — issues mentioning user
- `--kind` / `-K` — return `issues`, `pulls`, or `all`
- `--owner` / `--org` — filter by owner
- `--comments` — display comments

Create flags:

- `--title` / `-t` — issue title
- `--description` / `-d` — issue body
- `--assignees` / `-a` — comma-separated usernames
- `--labels` / `-L` — comma-separated labels
- `--milestone` / `-m` — milestone to assign
- `--deadline` / `-D` — deadline timestamp
- `--referenced-version` / `-v` — commit hash or tag

Edit flags:

- `--add-assignees` / `-a` — add assignees
- `--add-labels` / `-L` — add labels (takes precedence over remove)
- `--remove-labels` — remove labels
- `--title` / `-t` — new title
- `--description` / `-d` — new body
- `--milestone` / `-m` — change milestone
- `--deadline` / `-D` — change deadline
- `--referenced-version` / `-v` — commit hash or tag

## Pull Requests (`pulls`, `pull`, `pr`)

Manage and checkout pull requests.

```bash
tea pr list                       # list open PRs
tea pr create                     # create a PR
tea pr edit 42                    # edit PR #42
tea pr checkout 42                # locally check out PR #42
tea pr clean                      # delete closed PR branches
tea pr close 42                   # close PR #42
tea pr reopen 42                  # reopen PR #42
tea pr review 42                  # interactive review
tea pr approve 42                 # approve (alias: lgtm, a)
tea pr reject 42                  # request changes
tea pr merge 42                   # merge PR #42
tea pr review-comments 42         # list review comments
tea pr resolve 42                 # resolve a review comment
tea pr unresolve 42               # unresolve a review comment
```

Create flags:

- `--title` / `-t` — PR title
- `--description` / `-d` — PR body
- `--base` / `-b` — target branch
- `--head` — source branch (use `<user>:<branch>` for different repo)
- `--assignees` / `-a` — assignees
- `--labels` / `-L` — labels
- `--milestone` / `-m` — milestone
- `--deadline` / `-D` — deadline
- `--referenced-version` / `-v` — commit hash or tag
- `--agit` — create agit flow PR
- `--topic` — topic name for agit flow
- `--allow-maintainer-edits` / `--edits` — allow maintainer push

Merge flags:

- `--style` / `-s` — merge kind: `merge`, `rebase`, `squash`, `rebase-merge`
- `--message` / `-m` — commit message
- `--title` / `-t` — commit title

Edit flags (v0.13+):

- `--add-assignees` / `-a` — add assignees
- `--add-labels` / `-L` — add labels
- `--remove-labels` — remove labels
- `--add-reviewers` / `-r` — add reviewers
- `--remove-reviewers` — remove reviewers
- `--title` / `-t` — change title
- `--description` / `-d` — change body
- `--milestone` / `-m` — change milestone
- `--deadline` / `-D` — change deadline
- `--referenced-version` / `-v` — commit hash or tag

## Labels (`labels`, `label`)

```bash
tea labels list                   # list labels
tea labels create                 # create a label
tea labels update                 # update a label
tea labels delete                 # delete a label
```

Create flags:

- `--name` — label name
- `--color` — label color value
- `--description` — label description
- `--file` — load labels from file

Update flags:

- `--id` — label ID
- `--name` — new name
- `--color` — new color
- `--description` — new description

List flag:

- `--save` / `-s` — save all labels to a file

## Milestones (`milestones`, `milestone`, `ms`)

```bash
tea milestones list               # list milestones
tea milestones create             # create a milestone
tea milestones close              # close milestone
tea milestones reopen             # reopen milestone
tea milestones delete             # delete milestone
tea milestones issues             # manage issues/pulls in milestone
tea milestones issues add         # add issue/PR to milestone
tea milestones issues remove      # remove issue/PR from milestone
```

Create flags:

- `--title` / `-t` — milestone title
- `--description` / `-d` — description
- `--deadline` / `--expires` / `-x` — due date
- `--state` — state (default: open)

## Releases (`releases`, `release`, `r`)

```bash
tea releases list                 # list releases
tea releases create               # create a release
tea releases edit                 # edit a release
tea releases delete               # delete a release
tea releases assets list          # list release attachments
tea releases assets create        # add attachment to release
tea releases assets delete        # delete attachment
```

Create flags:

- `--tag` — tag name (created if not exists)
- `--title` / `-t` — release title
- `--note` / `-n` — release notes
- `--note-file` / `-f` — notes from file
- `--target` — target branch or commit hash
- `--draft` / `-d` — mark as draft
- `--prerelease` / `-p` — mark as pre-release
- `--asset` / `-a` — file attachment path (repeatable)

Delete flags:

- `--confirm` / `-y` — required confirmation
- `--delete-tag` — also delete the git tag

## Time Tracking (`times`, `time`, `t`)

```bash
tea times list                    # list tracked times
tea times add <issue> <duration>  # track time on issue
tea times delete <issue> <id>     # delete a time entry
tea times reset <issue>           # reset all time on issue
```

List flags:

- `--mine` / `-m` — show your times across all repos
- `--from` / `-f` — after this date
- `--until` / `-u` — before this date
- `--total` / `-t` — print total duration at end
- `--fields` — comma-separated: `id`, `created`, `repo`, `issue`, `user`, `duration`

## Repositories (`repos`, `repo`)

```bash
tea repos list                    # list accessible repos
tea repos search                  # find repos on instance
tea repos create                  # create a repository
tea repos create-from-template    # create from template
tea repos fork                    # fork a repository
tea repos migrate                 # migrate from another service
tea repos delete                  # delete a repository
tea repos edit                    # edit repository properties (v0.13+)
```

List flags:

- `--owner` / `-O` — filter by owner
- `--starred` / `-s` — list starred repos
- `--watched` / `-w` — list watched repos
- `--type` / `-T` — filter: `fork`, `mirror`, `source`
- `--fields` / `-f` — fields: `description`, `forks`, `id`, `name`, `owner`, `stars`, `ssh`, `updated`, `url`, `permission`, `type`

Create flags:

- `--name` / `-` — repo name
- `--owner` / `-O` — owner
- `--private` — make private
- `--description` / `--desc` — description
- `--init` — initialize repo
- `--branch` — custom default branch (needs --init)
- `--gitignores` / `--git` — gitignore template (needs --init)
- `--license` — license template (needs --init)
- `--readme` — readme template (needs --init)
- `--labels` — label set to add
- `--template` — make a template repo
- `--object-format` — git object format (`sha1`, `sha256`)
- `--trustmodel` — trust model (`committer`, `collaborator`, `collaborator+committer`)

Create-from-template flags:

- `--template` / `-t` — source template
- `--name` / `-n` — new repo name
- `--owner` / `-O` — owner
- `--content` — copy git content
- `--avatar` — copy avatar
- `--githooks` — copy hooks
- `--labels` — copy labels
- `--topics` — copy topics
- `--webhooks` — copy webhooks
- `--private` — make private

Migrate flags:

- `--clone-url` — source clone URL
- `--service` — source service (`git`, `gitea`, `gitlab`, `gogs`)
- `--auth-user` / `--auth-password` / `--auth-token` — migration auth
- `--issues` / `--pull-requests` / `--releases` / `--milestones` — copy metadata
- `--labels` — copy labels
- `--wiki` — copy wiki
- `--lfs` — copy LFS objects
- `--mirror` — set as mirror
- `--mirror-interval` — mirror interval

Edit flags (v0.13+):

- `--name` — new name
- `--description` / `--desc` — new description
- `--private` — set private (`true`/`false`)
- `--archived` — set archived (`true`/`false`)
- `--template` — set template (`true`/`false`)
- `--default-branch` — set default branch
- `--website` — new website URL

## Branches (`branches`, `branch`, `b`)

```bash
tea branches list                 # list branches
tea branches protect              # protect a branch
tea branches unprotect            # unprotect a branch
tea branches rename               # rename a branch (v0.14+)
```

List fields: `name`, `protected`, `user-can-merge`, `user-can-push`, `protection`

## Actions (`actions`, `action`)

Manage repository CI/CD actions (v0.12+).

### Secrets

```bash
tea actions secrets list          # list action secrets
tea actions secrets create        # create a secret
tea actions secrets delete        # delete a secret
```

Secret create flags:

- `--file` — read value from file
- `--stdin` — read value from stdin

### Variables

```bash
tea actions variables list        # list action variables
tea actions variables set         # set/update a variable
tea actions variables delete      # delete a variable
```

Variable flags:

- `--name` — filter by name (list)
- `--file` — read value from file
- `--stdin` — read value from stdin

### Workflow Runs (`runs`, `run`)

```bash
tea actions runs list             # list workflow runs
tea actions runs view             # view run details
tea actions runs logs             # view run logs
tea actions runs delete           # cancel/delete a run
```

Run list filters:

- `--actor` — filter by actor
- `--branch` — filter by branch
- `--event` — filter by event type
- `--status` — filter: `success`, `failure`, `pending`, `queued`, `in_progress`, `skipped`, `canceled`
- `--since` — runs after this time (e.g., `24h`, `2024-01-01`)
- `--until` — runs before this time

View flags:

- `--jobs` — show jobs table

Log flags:

- `--follow` / `-f` — follow output (like `tail -f`)
- `--job` — specific job ID

### Workflows (`workflows`, `workflow`) (v0.14+)

```bash
tea actions workflows list        # list workflows
tea actions workflows view        # view workflow details
tea actions workflows dispatch    # trigger a workflow
tea actions workflows enable      # enable a workflow
tea actions workflows disable     # disable a workflow
```

Dispatch flags:

- `--ref` / `-r` — branch or tag (default: current)
- `--input` / `-i` — key=value input (repeatable)
- `--follow` / `-f` — follow log output after dispatch
- `--confirm` / `-y` — confirm without prompting (disable)

## Webhooks (`webhooks`, `webhook`, `hooks`, `hook`)

```bash
tea webhooks list                 # list webhooks
tea webhooks create               # create a webhook
tea webhooks update               # update a webhook
tea webhooks delete               # delete a webhook
```

Create flags:

- `--type` — webhook type (`gitea`, `gogs`, `slack`, `discord`, `dingtalk`, `telegram`, `msteams`, `feishu`, `wechatwork`, `packagist`)
- `--events` — comma-separated events (default: `push`)
- `--secret` — webhook secret
- `--active` — webhook is active
- `--branch-filter` — branch filter for push events
- `--authorization-header` — auth header

Scope flags:

- `--org` — operate on organization webhooks
- `--global` — operate on global webhooks

## Comment (`comment`, `c`)

Add a comment to an issue or PR:

```bash
tea comment 42                    # add comment to issue/PR #42
```

## Open (`open`, `o`)

Open repository entity in browser:

```bash
tea open 42                       # open issue/PR #42 in browser
tea open milestones               # open milestones page
```

## Notifications (`notifications`, `notification`, `n`)

```bash
tea notifications                 # show unread/pinned notifications
tea notifications read            # mark as read
tea notifications unread          # mark as unread
tea notifications pin             # pin notification
tea notifications unpin           # unpin notification
```

Flags:

- `--mine` / `-m` — notifications across all repos
- `--states` / `-s` — filter: `pinned`, `unread`, `read`
- `--types` / `-t` — filter: `issue`, `pull`, `repository`, `commit`
- `--fields` / `-f` — fields: `id`, `status`, `updated`, `index`, `type`, `state`, `title`, `repository`

## Clone (`clone`, `C`)

```bash
tea clone gitea.com/user/repo     # clone a Gitea repository
tea clone --depth 1 gitea.com/user/repo  # shallow clone
```

## API (`api`) (v0.12+)

Make arbitrary authenticated API requests:

```bash
tea api /api/v1/repos/user/repo/issues
tea api -X POST /api/v1/repos/user/repo/issues -F title="Bug" -F body="Details"
tea api -H "Accept: application/json" /api/v1/user/repos
```

Flags:

- `--method` / `-X` — HTTP method (default: `GET`)
- `--data` / `-d` — raw JSON body (`@file` or `@-` for stdin)
- `--field` / `-f` — string field `key=value`
- `--Field` / `-F` — typed field (`key=value`, `@file`, `@-`)
- `--header` / `-H` — custom header `key:value`
- `--include` / `-i` — include HTTP status/headers in output
- `--output` / `-o` — write response to file (`-` for stdout)

## Organizations (`organizations`, `organization`, `org`)

```bash
tea orgs list                     # list organizations
tea orgs create                   # create an organization
tea orgs delete                   # delete an organization
```

Create flags:

- `--name` / `-n` — org name
- `--description` / `-d` — description
- `--location` / `-L` — location
- `--website` / `-w` — website
- `--visibility` / `-v` — visibility
- `--repo-admins-can-change-team-access`

## Admin (`admin`, `a`)

Operations requiring admin access:

```bash
tea admin users list              # list registered users
```

User list fields: `id`, `login`, `full_name`, `email`, `avatar_url`, `language`, `is_admin`, `restricted`, `prohibit_login`, `location`, `website`, `description`, `visibility`, `activated`, `lastlogin_at`, `created_at`

## Global Flags

All commands support these global flags:

- `--debug` / `--vvv` — enable debug mode
- `--help` / `-h` — show help
- `--version` / `-v` — print version
- `--repo` / `-r` — override repository (path or `owner/repo` slug)
- `--login` / `-l` — use a different Gitea login
- `--remote` / `-R` — discover login from git remote name
- `--output` / `-o` — output format (`simple`, `table`, `csv`, `tsv`, `yaml`, `json`)

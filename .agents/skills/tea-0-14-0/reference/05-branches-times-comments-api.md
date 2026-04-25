# Branches, Times, Comments, API

> **Source:** https://gitea.com/gitea/tea/src/branch/main/docs/CLI.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## branches, branch, b

Consult repository branches.

### list, ls

```bash
tea branches list
tea branch ls --fields name,protected,user-can-merge,user-can-push
```

Available fields: `name,protected,user-can-merge,user-can-push,protection`

### protect, P / unprotect, U

```bash
tea branch protect main
tea branch unprotect feature-experiment
```

### rename, rn (added in v0.14.0)

```bash
tea branch rename old-name new-name
```

## times, time, t

Operate on tracked times of issues and pull requests.

### list, ls

```bash
tea times list
tea time ls --total          # show total duration
tea time ls --mine           # all your times across repos
tea time ls --from 2025-01-01 --until 2025-06-01
```

Available fields: `id,created,repo,issue,user,duration`

Flags: `--from, -f`, `--until, -u`, `--mine, -m`, `--total, -t`

### add, a

Track time spent on an issue.

```bash
tea times add 42 2h30m
tea time add 42 1h
```

### delete, rm

Delete a specific tracked time entry.

```bash
tea times delete 42 <time-id>
```

### reset

Reset all tracked time on an issue.

```bash
tea times reset 42
```

## comment, c

Add a comment to an issue or pull request.

```bash
tea comment 42 "This looks good, please merge."
tea c 42 --description "Detailed feedback..."
```

## open, o

Open repository resources in the web browser.

```bash
tea open 42                    # open issue/PR 42
tea open milestones            # open milestones page
tea open pulls                 # open PR list
```

## clone, C

Clone a Gitea repository locally.

```bash
tea clone gitea.com/gitea/tea
tea clone gitea.com/gitea/tea --depth 10
```

Flags: `--depth, -d` (number of commits, default: all)

## admin, a

Operations requiring admin access on the Gitea instance.

### users, u

Manage registered users.

```bash
tea admin users list
tea admin u ls --fields id,login,full_name,email,activated,is_admin
```

Available fields: `id,login,full_name,email,avatar_url,language,is_admin,restricted,prohibit_login,location,website,description,visibility,activated,lastlogin_at,created_at`

Default fields: `id,login,full_name,email,activated`

## api

Make authenticated API requests to Gitea (similar to `curl` but with tea's auth context).

```bash
# GET request
tea api repos/gitea/tea

# POST with JSON body
tea api users --method POST -d '{"login":"alice","email":"alice@example.com"}'

# With custom headers
tea api repos/gitea/tea/issues -H "X-Custom-Header:value"

# Include response headers
tea api repos/gitea/tea --include

# Write to file
tea api repos/gitea/tea --output repo.json

# Form fields
tea api actions/secrets --method POST --field name=API_KEY
```

Flags: `--method, -X` (GET/POST/PUT/PATCH/DELETE), `--data, -d` (raw JSON, `@file` or `@-` for stdin), `--field, -f` (string field key=value), `--Field, -F` (typed field, `@file` or `@-`), `--header, -H` (key:value), `--include, -i`, `--output, -o`

## logins, login

Manage Gitea server logins.

### add

```bash
tea login add                                    # interactive
tea login add --url https://gitea.com --token <token>
tea login add --oauth                            # OAuth2 flow
tea login add --ssh-agent-key                    # SSH key via agent
tea login add --user alice --password secret     # basic auth → creates token
```

Flags: `--url, -u` (default: `https://gitea.com`), `--token, -t`, `--oauth, -o`, `--user`, `--password/--pwd`, `--ssh-key, -s`, `--ssh-agent-key, -a`, `--ssh-agent-principal, -c`, `--client-id`, `--redirect-url`, `--scopes`, `--otp`, `--insecure, -i`, `--name, -n`, `--helper, -j`, `--no-version-check, --nv`

### list, ls / edit, e / delete, rm

```bash
tea login list
tea login edit gitea.com
tea login delete old-instance
```

### default

```bash
tea login default           # show current default
tea login default gitea.com # set default
```

### oauth-refresh

Refresh an OAuth token.

```bash
tea login oauth-refresh
```

## whoami

Show the currently logged-in user.

```bash
tea whoami
```

## logout

Log out from a Gitea server.

```bash
tea logout
```

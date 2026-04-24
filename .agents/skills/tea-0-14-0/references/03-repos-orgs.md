# Repositories & Organizations

> **Source:** https://gitea.com/gitea/tea/src/branch/main/docs/CLI.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## repos, repo

Manage repositories.

### Common flags

- `--fields, -f` — Fields: `description,forks,id,name,owner,stars,ssh,updated,url,permission,type`
- Default fields: `owner,name,type,ssh`
- `--output, -o` — Output format
- `--limit, --lm` / `--page, -p` — Pagination

### list, ls

```bash
tea repos list
tea repo ls --starred        # your starred repos
tea repo ls --watched        # your watched repos
tea repo ls --owner myorg    # repos owned by an org or user
tea repo ls --type fork      # filter: fork, mirror, source
```

### search, s

Search any repository on a Gitea instance.

```bash
tea repo search "gitea"
tea repo search "api" --topic                     # search in topics instead of name
tea repo search "tool" --private false --archived false
```

Flags: `--owner, -O`, `--type, -T` (`fork|mirror|source`), `--private` (true/false), `--archived` (true/false), `--topic, -t`

### create, c

```bash
tea repo create --name my-project --description "My project"
tea repo create --name my-project --private --init --license mit --readme default
```

Flags: `--name, -`, `--owner, -O`, `--description/--desc`, `--private`, `--template`, `--init`, `--branch`, `--gitignores/--git`, `--labels`, `--license`, `--readme`, `--object-format` (`sha1|sha256`), `--trustmodel` (`committer|collaborator|collaborator+committer`)

### create-from-template, ct

Create a repository from an existing template repo.

```bash
tea repo create-from-template --name new-repo \
  --template owner/template-repo \
  --content --labels --topics
```

Flags: `--name, -n`, `--owner, -O`, `--template, -t`, `--content`, `--avatar`, `--labels`, `--topics`, `--webhooks`, `--githooks`, `--private`, `--description/--desc`

### fork, f

```bash
tea repo fork
tea repo fork --owner my-org
```

Flags: `--owner, -O` (defaults to current user)

### migrate, m

Migrate a repository from another service.

```bash
tea repo migrate \
  --clone-url https://github.com/user/repo.git \
  --service github \
  --name imported-repo \
  --issues --milestones --pull-requests --releases --labels --wiki --lfs
```

Flags: `--clone-url`, `--service` (`git|gitea|gitlab|gogs`), `--name`, `--owner`, `--private`, `--template`, `--issues`, `--labels`, `--milestones`, `--pull-requests`, `--releases`, `--wiki`, `--lfs`, `--mirror`, `--mirror-interval`, `--auth-user`, `--auth-password`, `--auth-token`, `--lfs-endpoint`

### delete, rm

```bash
tea repo delete --name my-repo --owner myorg --force
```

Flags: `--name, -`, `--owner, -O`, `--force, -f` (skip confirmation)

### edit, e

Edit repository properties (added in v0.13.0).

```bash
tea repo edit --description "Updated description"
tea repo edit --name new-name --private true
tea repo edit --archived false
```

Flags: `--name`, `--description/--desc`, `--private` (true/false), `--archived` (true/false), `--template` (true/false), `--default-branch`, `--website`

## organizations, organization, org

List, create, delete organizations.

### list, ls

```bash
tea orgs list
```

### create, c

```bash
tea org create --name my-team --description "Engineering team" --visibility public
```

Flags: `--name, -n`, `--description, -d`, `--visibility, -v`, `--location, -L`, `--website, -w`, `--repo-admins-can-change-team-access`

### delete, rm

```bash
tea org delete my-team
```

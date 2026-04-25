# Releases, Milestones, Labels

> **Source:** https://gitea.com/gitea/tea/src/branch/main/docs/CLI.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## releases, release, r

Manage releases.

### list, ls

```bash
tea releases list
tea release ls --page 1 --limit 50
```

### create, c

Create a release. If the tag does not exist, Gitea creates it.

```bash
tea release create \
  --tag v1.0.0 \
  --title "Version 1.0.0" \
  --note "Stable release" \
  --target main

# With asset attachments
tea release create --tag v1.0.0 --title "v1.0.0" \
  --asset dist/app.tar.gz --asset dist/app.zip
```

Flags: `--tag`, `--title, -t`, `--note, -n`, `--note-file, -f` (ignore `--note` if set), `--target` (branch or commit hash), `--asset, -a` (repeatable), `--draft, -d`, `--prerelease, -p`

### edit, e

```bash
tea release edit v1.0.0 --title "Updated title" --note "Revised notes"
tea release edit v1.0.0 --draft true
```

Flags: `--title, -t`, `--note, -n`, `--tag`, `--target`, `--draft, -d` (true/false), `--prerelease, -p` (true/false)

### delete, rm

```bash
tea release delete v1.0.0 --confirm
tea release delete v1.0.0 --confirm --delete-tag   # also remove the git tag
```

### assets, asset, a

Manage release attachments.

```bash
tea release assets list v1.0.0
tea release assets create v1.0.0 path/to/file.tar.gz
tea release assets delete v1.0.0 <asset-id> --confirm
```

## milestones, milestone, ms

List and create milestones.

### Common flags

- `--state` — Filter by state (`all|open|closed`)
- `--fields, -f` — Fields: `title,state,items_open,items_closed,items,duedate,description,created,updated,closed,id`
- Default fields: `title,items,duedate`

### list, ls

```bash
tea milestones list
tea milestone ls --state open
```

### create, c

```bash
tea milestone create --title "v2.0" --description "Major release" --deadline 2026-06-01
```

Flags: `--title, -t`, `--description, -d`, `--deadline/--expires, -x`, `--state`

### close / reopen, open

```bash
tea milestone close "v1.0"
tea milestone reopen "v1.0"
```

### delete, rm

```bash
tea milestone delete "v1.0"
```

### issues, i

Manage issues/pulls within a milestone.

```bash
tea ms issues "v2.0" --kind pull --state open
tea ms issues "v2.0" add 42          # add issue/PR 42 to milestone
tea ms issues "v2.0" remove 42       # remove from milestone
```

Flags: `--kind` (`issue|pull`), `--state`, `--fields, -f`

## labels, label

Manage issue labels.

### list, ls

```bash
tea labels list
tea label ls --save   # save all labels to a file
```

### create, c

```bash
tea label create --name "bug" --color ee0701 --description "Something isn't working"
```

Flags: `--name`, `--color`, `--description`, `--file` (load from label file)

### update

```bash
tea label update --id 5 --name "Bug (Critical)" --color cc0000
```

Flags: `--id`, `--name`, `--color`, `--description`

### delete, rm

```bash
tea label delete --id 5
```

# Filter Rules and Pattern Matching

## Overview

Rsync's filter system controls which files are included in or excluded from transfers. Filters work on two sides: the **sender** (hiding/showing files in the file list) and the **receiver** (protecting/risking files during deletion).

## Basic Exclude/Include

The simplest form uses `--exclude` and `--include`:

```bash
# Exclude .o files and directories named build
rsync -av --exclude='*.o' --exclude='build/' src/ dest/

# Include only .c and .h files
rsync -av --include='*/' --include='*.[ch]' --exclude='*' src/ dest/
```

These are shorthand for filter rules: `--exclude='PATTERN'` is equivalent to `-f'- PATTERN'` and `--include='PATTERN'` is equivalent to `-f'+ PATTERN'`.

Read patterns from files:

```bash
rsync -av --exclude-from=/path/to/excludes.txt src/ dest/
```

The exclude-from file has one pattern per line. Blank lines are ignored, as are lines starting with `#` or `;`. Lines beginning with `- ` (dash space) are excludes, `+ ` (plus space) are includes. A line containing only `!` clears all current rules.

## Filter Rule Syntax

Full filter rules use `-f` or `--filter`:

```
RULE [PATTERN_OR_FILENAME]
RULE,MODIFIERS [PATTERN_OR_FILENAME]
```

The RULE and PATTERN are separated by a space (or underscore `_`). Available rule prefixes:

**Rule types:**
- `exclude`, `-` — exclude pattern (default: both hide + protect)
- `include`, `+` — include pattern (default: both show + risk)
- `merge`, `.` — merge-file on the client side for more rules
- `dir-merge`, `:` — per-directory merge-file
- `hide`, `H` — hide files from transfer (sender-only exclude, same as `-s`)
- `show`, `S` — show files (sender-only include, same as `+s`)
- `protect`, `P` — protect files from deletion (receiver-only exclude, same as `-r`)
- `risk`, `R` — risk files for deletion (receiver-only include, same as `+r`)
- `clear`, `!` — clear current include/exclude list (takes no arg)

**Examples:**

```bash
# Exclude all .o files
rsync -av -f'- *.o' src/ dest/

# Exclude a file at the transfer root
rsync -av -f'- /foo' src/ dest/

# Exclude any directory named foo
rsync -av -f'- foo/' src/ dest/

# Exclude bar two levels below foo
rsync -av -f'- foo/*/bar' src/ dest/

# Exclude bar anywhere under top-level foo (but not /foo/bar directly)
rsync -av -f'- /foo/**/bar' src/ dest/

# Include all directories and .c files, exclude everything else
rsync -av -f'+ */' -f'+ *.c' -f'- *' src/ dest/

# Include only foo directory and foo/bar.c
rsync -av -f'+ foo/' -f'+ foo/bar.c' -f'- *' src/ dest/
```

## Pattern Matching Rules

**Path matching:**
- If a pattern contains `/` (not counting trailing slash) or `**`, it matches against the full pathname within the transfer
- Otherwise, it matches only against the final component of the filename
- A trailing `/` matches only directories
- A leading `/` anchors to the start of the transfer path

**Wildcard characters:**
- `?` — matches any single character except `/`
- `*` — matches zero or more non-slash characters
- `**` — matches zero or more characters, including slashes
- `[abc]` — character class matching
- `***` — shorthand to match a directory and all its contents (e.g., `dir_name/***`)
- Backslash escapes wildcards, but only if at least one wildcard is present in the pattern

## Filter Rule Modifiers

Modifiers follow the rule type (after a comma for long names):

- `/` — match against absolute pathname
- `!` — negated match (take effect if pattern fails to match)
- `C` — insert all global CVS-exclude rules
- `s` — sender side only (affects file list building)
- `r` — receiver side only (affects deletion protection)
- `p` — perishable: ignored in directories being deleted
- `x` — affects xattr names, not file/dir names

**Examples:**

```bash
# Exclude all non-directories
rsync -av -f'-! */' src/ dest/

# Exclude foo only when under subdir (absolute path match)
rsync -av -f'-/ subdir/foo' src/ dest/

# Sender-side exclude (doesn't protect from deletion)
rsync -av --del -f'-s *.o' src/ dest/

# Receiver-side protect (doesn't hide from transfer)
rsync -av --del -f'P *.log' src/ dest/
```

## Merge-File Filter Rules

Merge files incorporate rules from external files:

```bash
# Single-instance merge file
rsync -av --filter='. /etc/rsync/default.rules' src/ dest/

# Per-directory merge file
rsync -av --filter=': .per-dir-filter' src/ dest/

# Shorthand with -F
rsync -aFv src/ dest/  # Looks for .rsync-filter in each directory
```

**Merge-file modifiers:**
- `-` — file contains only exclude patterns
- `+` — file contains only include patterns
- `C` — CVS-compatible parsing (turns on `n`, `w`, `-`)
- `e` — exclude the merge-file itself from transfer
- `n` — rules are not inherited by subdirectories
- `w` — word-split on whitespace instead of line-splitting

**Example filter file** (specified via `--filter='. file'`):

```
merge /home/user/.global-filter
- *.gz
dir-merge .rules
+ *.[ch]
- *.o
- foo*
```

Per-directory rules are inherited by subdirectories unless `n` is used. Each subdirectory's rules prefix the inherited rules (newer rules have higher priority).

## The `-F` Option

The `-F` option provides shorthand for per-directory filter files:

- First `-F`: `--filter='dir-merge /.rsync-filter'`
- Second `-F`: `--filter='- .rsync-filter'` (excludes the filter files themselves)

```bash
# Use .rsync-filter files and exclude them from transfer
rsync -aFFv src/ dest/
```

## CVS Exclude Mode (`-C`)

The `--cvs-exclude` option auto-excludes common build artifacts:

Default excludes include: `RCS`, `SCCS`, `CVS`, `.svn/`, `.git/`, `.hg/`, `.bzr/`, `*.o`, `*.obj`, `*.so`, `*.exe`, `*.bak`, `*.old`, `core`, and many more.

Additionally reads:
- `$HOME/.cvsignore`
- `$CVSIGNORE` environment variable
- Per-directory `.cvsignore` files

When combining `-C` with custom filter rules, CVS excludes are appended at the end (lower priority). To control placement, omit `-C` and use `--filter=:C` (for per-directory .cvsignore) and `--filter=-C` (for default CVS excludes) at your desired position in the rule list.

## Filter Rules When Deleting

By default, include/exclude rules affect both sender and receiver:

- **Sender side**: exclude "hides" files from the file list; include "shows" them
- **Receiver side**: exclude "protects" files from deletion; include "risks" them

When `--delete` is active, excluded files are protected from deletion unless you use `--delete-excluded` or mark rules as sender-side only (`-s` or `H`).

**Example — skip copying .o files but don't delete existing .o on receiver:**

```bash
rsync -ai --del -f'- *.o' -f'- cmd' src host:/dest/
```

**Better — use perishable modifier so deleted dirs aren't protected:**

```bash
rsync -ai --del -f'-p *.o' src host:/dest/
```

**Use `--delete-excluded` to make unqualified rules sender-side only:**

```bash
rsync -ai --del --delete-excluded -f'- *.o' src host:/dest/
```

## Transfer Rules vs. Filter Rules

Transfer rules affect which files the generator decides need transferring, without the side effects of exclude filters. They don't affect deletions:

- Default "quick check" (size & mod-time comparison)
- `--update` (`-u`)
- `--max-size`
- `--min-size`
- `--ignore-non-existing`
- `--ignore-existing`

A file omitted by a transfer rule still appears in the sender's file list, so it won't be deleted on the receiver even if its data wasn't transferred.

## Anchoring Include/Exclude Patterns

Global patterns with leading `/` are anchored at the "root of the transfer" — where the tree starts being duplicated in the destination. The trailing slash on the source and use of `--relative` affect this root:

```bash
# Transfer root is /home/me and /home/you
rsync -a /home/me /home/you /dest
# Pattern /me/foo/bar matches /home/me/foo/bar

# Transfer root strips me/ and you/
rsync -a /home/me/ /home/you/ /dest
# Pattern /foo/bar matches (no "me" prefix needed)

# --relative preserves full path
rsync -a --relative /home/me/ /home/you /dest
# Pattern /home/me/foo/bar matches
```

The easiest way to determine the correct pattern is to run with `--verbose` and `--dry-run`, then put a `/` in front of the name you see.

## Per-Directory Rules and Delete

Without `--delete`, per-directory rules only matter on the sending side. With `--delete`, the receiver needs to know about exclude rules too:

**Easiest approach — include merge files in transfer with `--delete-after`:**

```bash
rsync -avF --delete-after host:src/dir /dest
```

**Use local merge files for receiver-side protection:**

```bash
rsync -av --filter=':e /.rsync-filter' --delete host:src/dir /dest
```

The `e` modifier excludes the merge file from transfer. With `-FF`, both sender and receiver use their own `.rsync-filter` files.

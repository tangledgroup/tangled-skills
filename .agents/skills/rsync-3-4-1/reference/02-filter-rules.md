# Filter Rules Reference

## Overview

Filter rules control which files are transferred, which are protected from deletion, and which extended attributes are copied. Rules are evaluated in order — the first matching rule wins.

## Rule Syntax

```
RULE [PATTERN_OR_FILENAME]
RULE,MODIFIERS [PATTERN_OR_FILENAME]
```

Short and long rule names are interchangeable. The comma separating RULE from MODIFIERS is optional.

## Available Rule Types

| Rule | Prefix | Description |
|------|--------|-------------|
| `exclude` | `-` | Exclude pattern (hide + protect by default) |
| `include` | `+` | Include pattern (show + risk by default) |
| `merge` | `.` | Read more rules from a file |
| `dir-merge` | `:` | Per-directory merge file |
| `hide` | `H` | Hide from transfer (sender-only exclude) |
| `show` | `S` | Don't hide (sender-only include) |
| `protect` | `P` | Protect from deletion (receiver-only exclude) |
| `risk` | `R` | Don't protect (receiver-only include) |
| `clear` | `!` | Clear current include/exclude list |

## Simple Include/Exclude Examples

```bash
# Exclude all .o files
rsync -av --exclude='*.o' /src/ /dest/

# Multiple excludes
rsync -av \
  --exclude={'*.o','*.swp','.git','__pycache__'} \
  /src/ /dest/

# Include only .c and .h files, exclude everything else
rsync -av -f'+ *.c' -f'+ *.h' -f'- *' /src/ /dest/

# Exclude a specific directory
rsync -av --exclude='node_modules/' /src/ /dest/

# Include a file deep in the tree (must include parent dirs too!)
rsync -av -f'+ foo/bar/baz.txt' -f'- *' /src/ /dest/
```

## Pattern Matching Rules

### Wildcard Characters
- `*` — matches zero or more non-slash characters
- `?` — matches any single character except `/`
- `[...]` — character class (e.g., `[a-z]`, `[[:alpha:]]`)
- `**` — matches zero or more characters, including slashes
- `***` — shorthand to match a directory and all its contents

### Pattern Scope
- **No `/` in pattern**: matched against the final path component only
  - `'*.o'` matches any file ending in `.o` anywhere
- **Contains `/`**: matched against full pathname
  - `'/foo/bar'` matches foo/bar at root of transfer
- **Ends with `/`**: matches directories only
  - `'node_modules/'` excludes the directory itself
- **Starts with `/`**: anchored to transfer root
  - `'/tmp/*'` matches /tmp/ files but not /src/tmp/

### Examples
```bash
# Match any file named "foo" at the transfer root
-f'-/foo'

# Match any directory named "foo" anywhere
-f'- foo/'

# Match bar that is exactly 2 levels below a top-level "foo"
-f'- foo/*/bar'

# Match bar that is 2+ levels below a top-level "foo"
-f'- /foo/**/bar'

# Exclude a directory and all its contents
-f'- dir_name/***'
```

## Filter Rule Modifiers

| Modifier | Meaning |
|----------|---------|
| `/` | Match against absolute pathname |
| `!` | Apply if pattern FAILS to match (negation) |
| `C` | Insert all CVS-exclude rules at this point |
| `s` | Affects sending side only |
| `r` | Affects receiving side only |

### Examples
```bash
# Exclude all non-directories
-f'-! */'

# Exclude /etc/passwd when transferring from /etc
-f'-/ /etc/passwd'

# Sender-only exclude (hide)
-f'H *.secret'

# Receiver-only protect
-f'P important/'
```

## Per-Directory Filters (.rsync-filter)

Create `.rsync-filter` files in directories to apply local rules:

```bash
# In /src/.rsync-filter:
+ *.txt
- *

# Use with -F flag (equivalent to --filter='dir-merge /.rsync-filter')
rsync -av -F /src/ /dest/
```

Multiple `-F` flags add both the dir-merge rule and exclude for `.rsync-filter` itself.

## CVS Ignore Mode

```bash
# Auto-ignore files that CVS would ignore
rsync -avC /src/ /dest/

# Or set environment variable
CVSIGNORE="*.bak *.tmp" rsync -av /src/ /dest/
```

Default CVS excludes:
```
RCS,v,RCS,SCCS,rcs,vcs,sccs,SCCS,.git,.svn,.hg,.bzr,_darcs,{arch},*.o,*.so,*.a,*.lib,*.pyc,*.class
```

## Debugging Filters

```bash
# Show why each file is included/excluded
rsync -avv --debug=FILTER /src/ /dest/

# Pull-side filter debugging
rsync -avv -M--debug=FILTER /src/ /dest/
```

## Important Notes

1. **Order matters** — first matching rule wins
2. **Directory exclusion excludes all contents** — the sender doesn't even scan excluded directories
3. **Parent directories must be included** — to include a deep file, all parent dirs must pass through
4. **Trailing whitespace in patterns** — rsync 3.2.4+ warns about trailing spaces (a pattern `'foo '` won't match `foo`)
5. **`-f` takes one rule per invocation** — repeat for multiple rules, or use merge files

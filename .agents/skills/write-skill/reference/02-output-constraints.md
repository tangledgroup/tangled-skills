# Output Constraints

## Contents
- Markdown-Only Default
- Opt-In Scripts and Assets
- Script Invocation Rules
- Tool Preference Hierarchy
- Inline Bash Examples
- Inline Python Examples

## Markdown-Only Default

By default, generated skills contain only Markdown files:
- `SKILL.md` (always)
- `reference/*.md` (optional, for complex skills)

Do **not** generate `scripts/` or `assets/` directories on your own initiative.

## Opt-In Scripts and Assets

Only create `scripts/` or `assets/` when the user explicitly requests them (e.g., "include a validation script", "add example config files"). If you think they would be useful, suggest it to the user first and wait for confirmation — never generate them proactively.

Even when scripts or assets are requested, generated skills must never instruct installing packages (`pip`, `npm`, `cargo`, etc.). Use only tools already available on the system.

## Script Invocation Rules

When a skill includes scripts, the SKILL.md must show how to execute them using bash. Scripts are run from the skill directory, so paths are relative to the skill root:

```
## Utility scripts

**validate.py**: Check configuration for errors

```bash
python scripts/validate.py config.yaml
# Returns: "OK" or lists specific errors with line numbers
```

**analyze.py**: Extract metadata from input files

```bash
python scripts/analyze.py input.pdf > metadata.json
```
```

- Always use forward slashes in paths (`scripts/helper.py`), never backslashes
- State clearly whether the agent should **execute** the script or **read it as reference**
- Show expected output format so the agent knows what to expect
- Scripts must handle errors explicitly — never bare `except:` or unhandled exceptions
- Document all magic numbers/constants with justification comments

## Tool Preference Hierarchy

1. **Bash first** — file manipulation, validation, parsing, YAML checks, directory operations, URL fetching with `curl`, text processing with `sed`/`awk`/`grep`
2. **Python stdlib only** — use when Bash is awkward (JSON parsing, complex string manipulation, version validation). Only standard library modules: `json`, `pathlib`, `urllib`, `re`, `hashlib`, etc.
3. **Python via `uvx`** — ephemeral venv for one-off tools not in stdlib (e.g., `uvx ruff check file.py`, `uvx yamlfix file.yaml`)
4. **Python via `uv run --with`** — scripts needing dependencies, run with inline dependency declaration (e.g., `uv run --with pyyaml scripts/parse.py`)
5. **System tools** — `pandoc` for HTML→Markdown conversion, `pdftotext`/`gs` for PDFs, `jq` for JSON processing

**No-install rule:** Never instruct installing programs (`pip install`, `npm install`, `cargo install`, `apt install`, etc.). Use only what is already on the system. If the user explicitly says a program needs to be installed, then and only then, install it.

## Inline Bash Examples

Bash scripts are preferred for validation and file operations. Write them inline where the skill needs to perform checks. Scripts execute via bash — they are not loaded into context, only their output consumes tokens.

To validate a YAML header:
```bash
yaml_block=$(sed -n '1,/^---$/p' SKILL.md | sed '1d;$d')

if [ -z "$yaml_block" ]; then
    echo "✗ Invalid (no YAML block)"
else
    echo "✓ Valid"
fi
```

To count lines in a skill:
```bash
wc -l SKILL.md | awk '{print $1}'
```

To execute a skill script (when scripts are requested):
```bash
python scripts/validate.py input.pdf
# Output: "OK" or specific error messages with line numbers
```

**Key principle:** Scripts should solve problems, not punt to the agent. Handle errors explicitly and provide specific, actionable error messages.

## Inline Python Examples

Use Python stdlib only when Bash is impractical:

```python
import json, pathlib

# Read and parse JSON data
with open("data.json") as f:
    data = json.load(f)

# List all .md files in a directory
for p in pathlib.Path(".").rglob("*.md"):
    print(p)
```

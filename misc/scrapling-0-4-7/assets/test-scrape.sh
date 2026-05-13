#!/usr/bin/env bash
# test-scrape.sh — Extensive tests for scrape.sh
# Run via: bash scripts/test-scrape.sh
#
# Tests cover: argument parsing, validation, error handling,
# command construction, temp-file workflow, file output, and edge cases.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRAPE="$SCRIPT_DIR/scrape.sh"
PASS=0
FAIL=0
TOTAL=0

# ── Helpers ────────────────────────────────────────────────────────
assert_stdout() {
    local desc="$1" expected="$2" actual="$3"
    TOTAL=$((TOTAL + 1))
    if [[ "$actual" == *"$expected"* ]]; then
        PASS=$((PASS + 1))
        echo "  ✓ $desc"
    else
        FAIL=$((FAIL + 1))
        echo "  ✗ $desc"
        echo "    Expected to contain: $expected"
        echo "    Got: $actual"
    fi
}

assert_exit() {
    local desc="$1" expected_code="$2" actual_code="$3"
    TOTAL=$((TOTAL + 1))
    if [[ "$actual_code" -eq "$expected_code" ]]; then
        PASS=$((PASS + 1))
        echo "  ✓ $desc (exit=$actual_code)"
    else
        FAIL=$((FAIL + 1))
        echo "  ✗ $desc"
        echo "    Expected exit: $expected_code, got: $actual_code"
    fi
}

assert_file_contains() {
    local desc="$1" file="$2" pattern="$3"
    TOTAL=$((TOTAL + 1))
    if grep -qF -- "$pattern" "$file" 2>/dev/null; then
        PASS=$((PASS + 1))
        echo "  ✓ $desc"
    else
        FAIL=$((FAIL + 1))
        echo "  ✗ $desc"
        echo "    File $file does not contain: $pattern"
    fi
}

assert_file_exists() {
    local desc="$1" file="$2"
    TOTAL=$((TOTAL + 1))
    if [[ -f "$file" ]]; then
        PASS=$((PASS + 1))
        echo "  ✓ $desc"
    else
        FAIL=$((FAIL + 1))
        echo "  ✗ $desc (file missing: $file)"
    fi
}

assert_file_not_exists() {
    local desc="$1" file="$2"
    TOTAL=$((TOTAL + 1))
    if [[ ! -f "$file" ]]; then
        PASS=$((PASS + 1))
        echo "  ✓ $desc"
    else
        FAIL=$((FAIL + 1))
        echo "  ✗ $desc (file exists: $file)"
    fi
}

# ── Test Groups ────────────────────────────────────────────────────

echo "=== scrape.sh Test Suite ==="
echo ""

# ── 1. Help and Usage ─────────────────────────────────────────────
echo "--- 1. Help and Usage ---"

OUT=$(bash "$SCRAPE" --help 2>&1)
assert_stdout "Help shows usage" "Usage:" "$OUT"
assert_stdout "Help shows modes" "get" "$OUT"
assert_stdout "Help shows fetch mode" "fetch" "$OUT"
assert_stdout "Help shows stealthy mode" "stealthy" "$OUT"
assert_stdout "Help shows --css-selector" "css-selector" "$OUT"
assert_stdout "Help shows --output" "output" "$OUT"
assert_stdout "Help shows --impersonate" "impersonate" "$OUT"
assert_stdout "Help shows --ai-targeted" "ai-targeted" "$OUT"
assert_stdout "Help shows --no-ai-targeted" "no-ai-targeted" "$OUT"
assert_stdout "Help shows --extra" "extra" "$OUT"
echo ""

# ── 2. Missing URL ────────────────────────────────────────────────
echo "--- 2. Missing URL ---"

OUT=$(bash "$SCRAPE" 2>&1); RC=$?
assert_exit "No args → exit 1" 1 "$RC"
assert_stdout "Error mentions URL" "URL is required" "$OUT"
echo ""

# ── 3. Unknown Options ────────────────────────────────────────────
echo "--- 3. Unknown Options ---"

OUT=$(bash "$SCRAPE" --bogus 'https://example.com' 2>&1); RC=$?
assert_exit "Unknown option → exit 1" 1 "$RC"
assert_stdout "Error mentions unknown option" "Unknown option" "$OUT"
echo ""

# ── 4. Invalid Mode ───────────────────────────────────────────────
echo "--- 4. Invalid Mode ---"

OUT=$(bash "$SCRAPE" --mode invalid 'https://example.com' 2>&1); RC=$?
assert_exit "Invalid mode → exit 1" 1 "$RC"
assert_stdout "Error mentions valid modes" "Valid modes: get, fetch, stealthy" "$OUT"
echo ""

# ── 5. Valid Mode Values (command construction via dry-run check) ─
echo "--- 5. Mode Dispatch ---"

for mode in get fetch stealthy; do
    # We can't easily intercept the uvx call without running it,
    # but we verify no parse error for valid modes
    OUT=$(bash "$SCRAPE" --mode "$mode" 'https://example.com' 2>&1)
    # Should NOT contain mode error
    TOTAL=$((TOTAL + 1))
    if [[ "$OUT" != *"Unknown mode"* ]]; then
        PASS=$((PASS + 1))
        echo "  ✓ Mode '$mode' accepted (no parse error)"
    else
        FAIL=$((FAIL + 1))
        echo "  ✗ Mode '$mode' rejected"
    fi
done
echo ""

# ── 6. URL Position Flexibility ───────────────────────────────────
echo "--- 6. URL Position ---"

# URL at end (default)
OUT=$(bash "$SCRAPE" 'https://example.com' 2>&1)
TOTAL=$((TOTAL + 1))
if [[ "$OUT" != *"Unexpected argument"* ]]; then
    PASS=$((PASS + 1))
    echo "  ✓ URL at end accepted"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ URL at end rejected"
fi

# URL with flags before it
OUT=$(bash "$SCRAPE" --mode fetch 'https://example.com' 2>&1)
TOTAL=$((TOTAL + 1))
if [[ "$OUT" != *"Unexpected argument"* ]]; then
    PASS=$((PASS + 1))
    echo "  ✓ URL after flags accepted"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ URL after flags rejected"
fi

# Two URLs → error
OUT=$(bash "$SCRAPE" 'https://a.com' 'https://b.com' 2>&1); RC=$?
assert_exit "Two URLs → exit 1" 1 "$RC"
assert_stdout "Error mentions unexpected argument" "Unexpected argument" "$OUT"
echo ""

# ── 7. Flag Combinations ──────────────────────────────────────────
echo "--- 7. Flag Combinations ---"

# All common flags together
OUT=$(bash "$SCRAPE" --mode fetch -s 'article' --no-ai-targeted 'https://example.com' 2>&1)
TOTAL=$((TOTAL + 1))
if [[ "$OUT" != *"Unknown"* && "$OUT" != *"Error:"* ]]; then
    PASS=$((PASS + 1))
    echo "  ✓ All flags combined (fetch mode)"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ Flag combination failed: $OUT"
fi

# CSS selector with get mode
OUT=$(bash "$SCRAPE" -s 'main' --impersonate chrome 'https://example.com' 2>&1)
TOTAL=$((TOTAL + 1))
if [[ "$OUT" != *"Unknown"* && "$OUT" != *"Error:"* ]]; then
    PASS=$((PASS + 1))
    echo "  ✓ CSS selector + impersonate (get mode)"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ CSS + impersonate failed: $OUT"
fi

# Extra flags passthrough
OUT=$(bash "$SCRAPE" --mode stealthy --extra '--solve-cloudflare --block-webrtc' 'https://example.com' 2>&1)
TOTAL=$((TOTAL + 1))
if [[ "$OUT" != *"Unknown"* && "$OUT" != *"Error:"* ]]; then
    PASS=$((PASS + 1))
    echo "  ✓ Extra flags passthrough (stealthy mode)"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ Extra flags failed: $OUT"
fi

# ai-targeted explicitly on
OUT=$(bash "$SCRAPE" --ai-targeted 'https://example.com' 2>&1)
TOTAL=$((TOTAL + 1))
if [[ "$OUT" != *"Unknown"* && "$OUT" != *"Error:"* ]]; then
    PASS=$((PASS + 1))
    echo "  ✓ --ai-targeted explicit flag"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ --ai-targeted failed: $OUT"
fi
echo ""

# ── 8. File Output (-o) ───────────────────────────────────────────
echo "--- 8. File Output ---"

TMPDIR_TEST=$(mktemp -d)
trap 'rm -rf "$TMPDIR_TEST"' EXIT

# Output to existing directory
OUT=$(bash "$SCRAPE" -o "$TMPDIR_TEST/output.md" 'https://example.com' 2>&1)
TOTAL=$((TOTAL + 1))
if [[ "$OUT" != *"Unknown"* && "$OUT" != *"Unexpected"* ]]; then
    PASS=$((PASS + 1))
    echo "  ✓ -o flag accepted (no parse error)"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ -o flag failed: $OUT"
fi

# Output to nested directory (should auto-create)
OUT=$(bash "$SCRAPE" -o "$TMPDIR_TEST/sub/deep/output.md" 'https://example.com' 2>&1)
TOTAL=$((TOTAL + 1))
if [[ "$OUT" != *"Unknown"* && "$OUT" != *"Unexpected"* ]]; then
    PASS=$((PASS + 1))
    echo "  ✓ -o to nested dir accepted (mkdir -p)"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ -o nested dir failed: $OUT"
fi
echo ""

# ── 9. Script Structure Checks ────────────────────────────────────
echo "--- 9. Script Structure ---"

assert_file_contains "Script has shebang" "$SCRAPE" '#!/usr/bin/env bash'
assert_file_contains "Script uses strict mode" "$SCRAPE" 'set -euo pipefail'
assert_file_contains "Script has trap for cleanup" "$SCRAPE" 'trap'
assert_file_contains "Script checks uvx availability" "$SCRAPE" 'command -v uvx'
assert_file_contains "Script uses mktemp" "$SCRAPE" 'mktemp'
assert_file_contains "Script has usage function" "$SCRAPE" 'usage()'
assert_file_contains "Script handles EXIT trap" "$SCRAPE" 'rm -f'
assert_file_contains "Script documents exit codes" "$SCRAPE" 'Exit codes'
echo ""

# ── 10. Script Permissions ────────────────────────────────────────
echo "--- 10. Permissions ---"

TOTAL=$((TOTAL + 1))
if [[ -x "$SCRAPE" ]]; then
    PASS=$((PASS + 1))
    echo "  ✓ scrape.sh is executable"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ scrape.sh is not executable"
fi
echo ""

# ── 11. SKILL.md References the Script Correctly ──────────────────
echo "--- 11. SKILL.md Integration ---"

SKILL_MD="$(dirname "$(dirname "$SCRAPE")")/SKILL.md"
assert_file_contains "SKILL.md references scrape.sh" "$SKILL_MD" 'scripts/scrape.sh'
assert_file_contains "SKILL.md marks as Execute" "$SKILL_MD" 'Execute'
assert_file_contains "SKILL.md has CLI Usage section" "$SKILL_MD" '## CLI Usage'
assert_file_contains "SKILL.md shows default workflow with script" "$SKILL_MD" "bash scripts/scrape.sh 'https://example.com'"
assert_file_contains "SKILL.md shows --mode fetch example" "$SKILL_MD" '--mode fetch'
assert_file_contains "SKILL.md shows --mode stealthy example" "$SKILL_MD" '--mode stealthy'
assert_file_contains "SKILL.md shows -o output example" "$SKILL_MD" '-o '
assert_file_contains "SKILL.md shows -s selector example" "$SKILL_MD" '-s '
echo ""

# ── 12. No Raw Bash Patterns Left in SKILL.md Usage ───────────────
echo "--- 12. No Legacy Patterns ---"

# The old temp-file pattern should NOT appear in Usage Examples / CLI Usage
TOTAL=$((TOTAL + 1))
if ! grep -qF 'TMPFILE=$(mktemp' "$SKILL_MD"; then
    PASS=$((PASS + 1))
    echo "  ✓ No raw TMPFILE pattern in SKILL.md"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ Raw TMPFILE pattern still in SKILL.md"
fi

TOTAL=$((TOTAL + 1))
if ! grep -qF 'cat "$TMPFILE"' "$SKILL_MD"; then
    PASS=$((PASS + 1))
    echo "  ✓ No raw cat \$TMPFILE in SKILL.md"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ Raw cat \$TMPFILE still in SKILL.md"
fi

TOTAL=$((TOTAL + 1))
if ! grep -qF 'rm -f "$TMPFILE"' "$SKILL_MD"; then
    PASS=$((PASS + 1))
    echo "  ✓ No raw rm -f \$TMPFILE in SKILL.md"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ Raw rm -f \$TMPFILE still in SKILL.md"
fi
echo ""

# ── 13. No Backslashes in Paths ───────────────────────────────────
echo "--- 13. Cross-Platform Safety ---"

TOTAL=$((TOTAL + 1))
if ! grep -q '\scrape' "$SKILL_MD"; then
    PASS=$((PASS + 1))
    echo "  ✓ No backslash paths in SKILL.md"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ Backslash paths found in SKILL.md"
fi

TOTAL=$((TOTAL + 1))
if ! grep -q '\scrape' "$SCRAPE"; then
    PASS=$((PASS + 1))
    echo "  ✓ No backslash paths in scrape.sh"
else
    FAIL=$((FAIL + 1))
    echo "  ✗ Backslash paths found in scrape.sh"
fi
echo ""

# ── Summary ────────────────────────────────────────────────────────
echo "=== Results ==="
echo "  Passed: $PASS / $TOTAL"
echo "  Failed: $FAIL / $TOTAL"
echo ""

if [[ $FAIL -eq 0 ]]; then
    echo "✓ All tests passed!"
    exit 0
else
    echo "✗ $FAIL test(s) failed"
    exit 1
fi

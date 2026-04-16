# Directory Structure and Comprehensive Validation

This reference provides **on-the-fly bash scripts** for comprehensive skill validation covering three critical aspects:

1. **Directory structure** - Ensure `references/` is used (not `refs/` or `ref/`)
2. **Reference file numbering** - Validate sequential prefixes (`01-`, `02-`, `03-`)
3. **YAML header validity** - Verify required fields, format, and length

**Important:** All bash scripts are generated and executed on-the-fly during skill creation. No separate `.sh` files are created or stored.

## Validation Overview

| Aspect | What It Checks | Why It Matters |
|--------|----------------|----------------|
| **Directory Structure** | Wrong dirs (`refs/`, `ref/`) ❌<br>Correct dir exists with files ✅ | Prevents structural errors that break skill loading |
| **Reference Numbering** | Sequential prefixes (`01-`, `02-`, `03-`) ✅<br>No gaps or invalid formats | Ensures consistent ordering and platform compatibility |
| **YAML Header** | Required fields present ✅<br>Format valid (`name` regex) ✅<br>Length valid (`description` 1-1024) ✅ | Prevents skills from failing to load on platforms |

## Complete On-the-Fly Validation Script

This comprehensive script validates all three aspects in one execution. Replace `<skill-name>` with the actual skill name before running.

```bash
#!/bin/bash
# Comprehensive Skill Validation - Generated On-the-Fly
# Usage: Copy this script, replace <skill-name>, and execute
# Exit codes: 0 = all validations passed, 1 = validation failed

SKILL_NAME="<skill-name>"
SKILL_DIR=".agents/skills/$SKILL_NAME"
SKILL_FILE="$SKILL_DIR/SKILL.md"

echo "========================================="
echo "  Comprehensive Skill Validation"
echo "========================================="
echo "Skill: $SKILL_NAME"
echo "Path:  $SKILL_DIR"
echo ""

validation_failed=0

# ============================================
# VALIDATION 1: Directory Structure
# ============================================
echo "[1/3] Checking directory structure..."

# Check for incorrect directories (refs/, ref/)
if [ -d "$SKILL_DIR/refs" ]; then
    echo "✗ ERROR: Found 'refs/' directory (should be 'references/')"
    file_count=$(find "$SKILL_DIR/refs" -maxdepth 1 -name "*.md" | wc -l)
    echo "  Contains $file_count markdown files"
    validation_failed=1
fi

if [ -d "$SKILL_DIR/ref" ]; then
    echo "✗ ERROR: Found 'ref/' directory (should be 'references/')"
    file_count=$(find "$SKILL_DIR/ref" -maxdepth 1 -name "*.md" | wc -l)
    echo "  Contains $file_count markdown files"
    validation_failed=1
fi

# Verify correct directory exists if reference files present
if [ -d "$SKILL_DIR/references" ]; then
    ref_count=$(find "$SKILL_DIR/references" -maxdepth 1 -name "*.md" | wc -l)
    
    if [ $ref_count -gt 0 ]; then
        echo "✓ Directory structure valid (references/ with $ref_count files)"
        
        # Check for nested directories (should be flat)
        nested_count=$(find "$SKILL_DIR/references" -mindepth 1 -type d | wc -l)
        if [ $nested_count -gt 0 ]; then
            echo "✗ ERROR: Found $nested_count nested directories inside references/ (should be flat)"
            validation_failed=1
        else
            echo "✓ No nested directories (flat structure correct)"
        fi
    else
        echo "⚠ WARNING: references/ directory exists but contains no .md files"
    fi
else
    # Check if SKILL.md exists (simple skill)
    if [ -f "$SKILL_FILE" ]; then
        line_count=$(wc -l < "$SKILL_FILE")
        if [ $line_count -lt 500 ]; then
            echo "✓ Simple skill detected (SKILL.md: $line_count lines, no references needed)"
        else
            echo "⚠ WARNING: SKILL.md has $line_count lines (>500) but no references/ directory"
            echo "  Consider splitting into complex skill structure"
        fi
    else
        echo "✗ ERROR: Neither SKILL.md nor references/ directory found"
        validation_failed=1
    fi
fi

echo ""

# ============================================
# VALIDATION 2: Reference File Numbering
# ============================================
echo "[2/3] Checking reference file numbering..."

if [ -d "$SKILL_DIR/references" ]; then
    invalid_files=0
    highest_num=0
    found_numbers=()
    
    for file in "$SKILL_DIR/references"/*.md; do
        [ -f "$file" ] || continue
        filename=$(basename "$file")
        
        # Extract prefix number
        if [[ $filename =~ ^([0-9]{2})- ]]; then
            prefix_num=${BASH_REMATCH[1]}
            # Convert to integer (remove leading zeros)
            prefix_int=$((10#$prefix_num))
            found_numbers+=($prefix_int)
            
            if [ $prefix_int -gt $highest_num ]; then
                highest_num=$prefix_int
            fi
            
            echo "  ✓ $filename (prefix: $prefix_num)"
        else
            echo "  ✗ $filename (INVALID: missing or wrong prefix format)"
            invalid_files=$((invalid_files + 1))
        fi
    done
    
    if [ $invalid_files -eq 0 ]; then
        file_count=${#found_numbers[@]}
        if [ $file_count -gt 0 ]; then
            echo "✓ All $file_count reference files have valid numbering (01-$highest_num)"
            
            # Check for gaps in sequence
            expected_count=$highest_num
            if [ $file_count -lt $expected_count ]; then
                echo "⚠ WARNING: Found gaps in numbering (expected $expected_count files, found $file_count)"
            fi
        else
            echo "  (no reference files to check)"
        fi
    else
        echo "✗ ERROR: Found $invalid_files files with invalid numbering"
        validation_failed=1
    fi
else
    echo "  (skipped - no references directory)"
fi

echo ""

# ============================================
# VALIDATION 3: YAML Header Validity
# ============================================
echo "[3/3] Checking YAML header in SKILL.md..."

if [ ! -f "$SKILL_FILE" ]; then
    echo "✗ ERROR: SKILL.md not found"
    validation_failed=1
else
    # Check file starts with ---
    first_line=$(head -n1 "$SKILL_FILE")
    if [ "$first_line" != "---" ]; then
        echo "✗ ERROR: SKILL.md does not start with '---' (found: $first_line)"
        validation_failed=1
    else
        echo "✓ File starts with YAML delimiter"
        
        # Extract and validate YAML frontmatter
        # Find the closing ---
        yaml_end=$(grep -n '^---$' "$SKILL_FILE" | head -n2 | tail -n1 | cut -d: -f1)
        if [ -z "$yaml_end" ] || [ "$yaml_end" -lt 2 ]; then
            echo "✗ ERROR: YAML header not properly closed with '---'"
            validation_failed=1
        else
            echo "✓ YAML header properly delimited (lines 1-$yaml_end)"
            
            # Extract frontmatter content (between first and second ---)
            frontmatter=$(sed -n "2,$((yaml_end - 1))p" "$SKILL_FILE")
            
            # Check required field: name
            if echo "$frontmatter" | grep -q '^name:'; then
                name_value=$(echo "$frontmatter" | grep '^name:' | sed 's/name:[[:space:]]*//')
                echo "✓ Required field 'name' present: $name_value"
                
                # Validate name format (lowercase, hyphens only)
                if echo "$name_value" | grep -qE '^[a-z0-9]+(-[a-z0-9]+)*$'; then
                    echo "  ✓ Name format valid (matches ^[a-z0-9]+(-[a-z0-9]+)*$)"
                else
                    echo "  ✗ Name format INVALID"
                    echo "    Must match: ^[a-z0-9]+(-[a-z0-9]+)*$"
                    echo "    Found: $name_value"
                    validation_failed=1
                fi
                
                # Check name matches directory name
                if [ "$name_value" != "$SKILL_NAME" ]; then
                    echo "  ✗ Name does not match directory name"
                    echo "    Expected: $SKILL_NAME"
                    echo "    Found: $name_value"
                    validation_failed=1
                fi
            else
                echo "✗ ERROR: Required field 'name' missing"
                validation_failed=1
            fi
            
            # Check required field: description
            if echo "$frontmatter" | grep -q '^description:'; then
                desc_value=$(echo "$frontmatter" | grep '^description:' | sed 's/description:[[:space:]]*//')
                desc_length=${#desc_value}
                echo "✓ Required field 'description' present ($desc_length chars)"
                
                if [ $desc_length -ge 1 ] && [ $desc_length -le 1024 ]; then
                    echo "  ✓ Description length valid (1-1024 chars)"
                else
                    echo "  ✗ Description length INVALID ($desc_length chars, must be 1-1024)"
                    validation_failed=1
                fi
                
                # Check for first person pronouns (should use third person)
                if echo "$desc_value" | grep -qiE '\b(I|you|we|our)\b'; then
                    echo "  ⚠ WARNING: Description may contain first/second person pronouns"
                    echo "    Should use third person (no 'I', 'you', 'we', 'our')"
                fi
            else
                echo "✗ ERROR: Required field 'description' missing"
                validation_failed=1
            fi
            
            # Check optional but recommended fields
            if echo "$frontmatter" | grep -q '^version:'; then
                echo "✓ Recommended field 'version' present"
            else
                echo "⚠ WARNING: Recommended field 'version' missing"
            fi
            
            if echo "$frontmatter" | grep -q '^license:'; then
                echo "✓ Recommended field 'license' present"
            else
                echo "⚠ WARNING: Recommended field 'license' missing"
            fi
        fi
    fi
fi

echo ""

# ============================================
# FINAL SUMMARY
# ============================================
echo "========================================="
echo "  Validation Summary"
echo "========================================="

if [ $validation_failed -eq 1 ]; then
    echo "✗ VALIDATION FAILED"
    echo ""
    echo "Do not present this skill for review. Fix the errors above first."
    echo ""
    echo "Quick fix commands:"
    
    if [ -d "$SKILL_DIR/refs" ]; then
        echo "  # Fix refs/ directory"
        echo "  mv $SKILL_DIR/refs $SKILL_DIR/references"
        echo "  sed -i 's|refs/|references/|g' $SKILL_FILE"
    fi
    
    if [ -d "$SKILL_DIR/ref" ]; then
        echo "  # Fix ref/ directory"
        echo "  mv $SKILL_DIR/ref $SKILL_DIR/references"
        echo "  sed -i 's|\\bref/|references/|g' $SKILL_FILE"
    fi
    
    exit 1
else
    echo "✓ ALL VALIDATIONS PASSED"
    echo "✓ Skill is ready for review"
    echo ""
    echo "Validated:"
    echo "  - Directory structure: OK"
    echo "  - Reference numbering: OK"
    echo "  - YAML header: OK"
    exit 0
fi
```

## Quick Validation Snippets

For embedding in workflow steps, use these shorter inline snippets:

### Quick Directory Check

```bash
# Inline directory validation
skill_dir=".agents/skills/<skill-name>"

if [ -d "$skill_dir/refs" ] || [ -d "$skill_dir/ref" ]; then
    echo "✗ ERROR: Found incorrect directory (refs/ or ref/)"
    exit 1
fi

if [ -d "$skill_dir/references" ]; then
    ref_count=$(find "$skill_dir/references" -maxdepth 1 -name "*.md" | wc -l)
    if [ $ref_count -gt 0 ]; then
        echo "✓ Directory structure valid ($ref_count reference files)"
    else
        echo "⚠ WARNING: references/ exists but empty"
    fi
else
    echo "✓ Simple skill (no references needed)"
fi
```

### Quick Numbering Check

```bash
# Inline numbering validation
skill_dir=".agents/skills/<skill-name>"

if [ -d "$skill_dir/references" ]; then
    invalid=$(find "$skill_dir/references" -maxdepth 1 -name "*.md" ! -regex ".*/[0-9][0-9]-.*\.md" | wc -l)
    if [ $invalid -eq 0 ]; then
        echo "✓ All reference files have valid numbering"
    else
        echo "✗ ERROR: Found $invalid files with invalid numbering"
        exit 1
    fi
fi
```

### Quick YAML Check

```bash
# Inline YAML validation
skill_file=".agents/skills/<skill-name>/SKILL.md"

if [ ! -f "$skill_file" ]; then
    echo "✗ ERROR: SKILL.md not found"
    exit 1
fi

first_line=$(head -n1 "$skill_file")
if [ "$first_line" != "---" ]; then
    echo "✗ ERROR: SKILL.md does not start with ---"
    exit 1
fi

if grep -q '^name:' "$skill_file" && grep -q '^description:' "$skill_file"; then
    echo "✓ YAML header has required fields"
else
    echo "✗ ERROR: YAML header missing required fields"
    exit 1
fi
```

## Auto-Fix Commands

If validation fails, use these commands to fix common issues:

### Fix Directory Structure

```bash
# If refs/ directory found:
skill_dir=".agents/skills/<skill-name>"
[ -d "$skill_dir/refs" ] && {
    echo "Fixing refs/ -> references/..."
    mv "$skill_dir/refs" "$skill_dir/references"
    sed -i 's|refs/|references/|g' "$skill_dir/SKILL.md"
    echo "✓ Fixed"
}

# If ref/ directory found:
[ -d "$skill_dir/ref" ] && {
    echo "Fixing ref/ -> references/..."
    mv "$skill_dir/ref" "$skill_dir/references"
    sed -i 's|\bref/|references/|g' "$skill_dir/SKILL.md"
    echo "✓ Fixed"
}
```

### Fix Reference Numbering

```bash
# Manual fix for incorrectly numbered files
skill_dir=".agents/skills/<skill-name>"

# List files with invalid numbering
find "$skill_dir/references" -maxdepth 1 -name "*.md" ! -regex ".*/[0-9][0-9]-.*\.md" -exec basename {} \;

# Rename manually (example):
# mv "$skill_dir/references/1-topic.md" "$skill_dir/references/01-topic.md"
```

### Fix YAML Header

```bash
# Add missing YAML header if completely absent
skill_file=".agents/skills/<skill-name>/SKILL.md"

if ! head -n1 "$skill_file" | grep -q '^---$'; then
    # Create new file with header
    tmp_file=$(mktemp)
    cat > "$tmp_file" << 'EOF'
---
name: <skill-name>
description: <add description here>
version: "0.1.0"
license: MIT
---
EOF
    cat "$skill_file" >> "$tmp_file"
    mv "$tmp_file" "$skill_file"
    echo "✓ Added YAML header (edit to complete)"
fi
```

## Integration into Skill Generation Workflow

### When to Run Validation

1. **After writing SKILL.md** - Run YAML header validation
2. **After creating reference files** - Run numbering validation
3. **Before presenting skill for review** - Run complete validation

### Example Workflow Integration

```bash
# Step 1: Create skill directory and files
mkdir -p ".agents/skills/my-skill/references"
# ... write SKILL.md and reference files ...

# Step 2: Run comprehensive validation
skill_dir=".agents/skills/my-skill"

# Generate and execute validation script inline
bash << 'VALIDATION_SCRIPT'
SKILL_NAME="my-skill"
SKILL_DIR=".agents/skills/$SKILL_NAME"
SKILL_FILE="$SKILL_DIR/SKILL.md"

# ... (complete validation script from above) ...
VALIDATION_SCRIPT

# Step 3: Check exit code
if [ $? -eq 0 ]; then
    echo "✓ Validation passed - skill ready for review"
else
    echo "✗ Validation failed - fix errors before proceeding"
    exit 1
fi
```

## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Found 'refs/' directory` | Used wrong directory name | `mv refs/ references/` + update SKILL.md links |
| `INVALID: missing or wrong prefix format` | File named `1-topic.md` instead of `01-topic.md` | Rename file with 2-digit prefix |
| `SKILL.md does not start with '---'` | Missing YAML header | Add `---` as first line with frontmatter |
| `Required field 'name' missing` | Incomplete YAML header | Add `name: <skill-name>` to frontmatter |
| `Name format INVALID` | Name contains uppercase or special chars | Use only lowercase letters, numbers, hyphens |
| `Description length INVALID` | Description too short or too long | Keep between 1-1024 characters |
| `Found nested directories` | Created subdirectories inside references/ | Flatten structure, move files to references/ root |

## Testing Validation Against Existing Skills

To test all existing skills with the new validation:

```bash
#!/bin/bash
# Test validation against all skills

echo "=== Testing All Skills ==="
total=0
passed=0
failed=0

for skill_dir in .agents/skills/*/; do
    skill_name=$(basename "$skill_dir")
    total=$((total + 1))
    
    # Run inline validation (simplified version)
    if [ -d "${skill_dir}refs" ] || [ -d "${skill_dir}ref" ]; then
        echo "✗ $skill_name: Has incorrect directory"
        failed=$((failed + 1))
        continue
    fi
    
    skill_file="${skill_dir}SKILL.md"
    if [ -f "$skill_file" ]; then
        if ! head -n1 "$skill_file" | grep -q '^---$'; then
            echo "✗ $skill_name: Missing YAML header"
            failed=$((failed + 1))
            continue
        fi
        
        if ! grep -q '^name:' "$skill_file" || ! grep -q '^description:' "$skill_file"; then
            echo "✗ $skill_name: Missing required fields"
            failed=$((failed + 1))
            continue
        fi
    else
        echo "✗ $skill_name: No SKILL.md"
        failed=$((failed + 1))
        continue
    fi
    
    passed=$((passed + 1))
done

echo ""
echo "=== Summary ==="
echo "Total: $total"
echo "Passed: $passed"
echo "Failed: $failed"
```

## Summary

- **Three-way validation**: Directory structure, reference numbering, YAML header
- **On-the-fly execution**: No separate .sh files, all bash embedded in markdown
- **Comprehensive coverage**: Catches 7+ types of common errors
- **Clear error messages**: Shows exactly what's wrong and how to fix
- **Quick snippets**: Short inline versions for workflow integration
- **Auto-fix commands**: Manual fix instructions for each error type

**Remember:** Always run validation before presenting a skill for review. A skill that fails validation should not be shown to users.

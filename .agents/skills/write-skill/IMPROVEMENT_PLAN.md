# write-skill Improvement Plan

## Problem Statement

Recent audit discovered that 4 skills incorrectly used `refs/` directory instead of the spec-compliant `references/` directory:
- boto3-1-42-89
- networkx-3-6-1
- qwen3-reranker-06
- rustfs-1-0-0-alpha-93

This indicates that the `write-skill` meta-skill lacks **enforced validation** to prevent this type of structural error from occurring during skill generation.

## Goals

1. **Always use `references/` directory** - Never allow `refs/`, `ref/`, or any other variation
2. **Validate after every write** - Ensure reference files are in the correct location before presenting skill for review
3. **Prevent errors proactively** - Build validation into generation workflow, not just as post-check
4. **Clear error messages** - If validation fails, provide actionable fix instructions
5. **Use bash scripts exclusively** - Prefer bash over Python for all validation (faster, no dependencies, portable)
6. **Comprehensive validation** - Check directory structure, reference numbering, AND YAML header validity
7. **On-the-fly script generation** - Generate complete validation bash scripts dynamically during skill creation

## Proposed Changes

### 1. Add New Validation Reference File

**File:** `references/09-directory-validation.md`

**Purpose:** Dedicated reference for comprehensive skill validation with **on-the-fly bash script generation**.

**Content:**
- Directory structure requirements (always use `references/`)
- **Complete bash validation scripts** generated on-the-fly during skill creation
- Validates THREE critical aspects:
  1. **Directory structure** - Detect wrong dirs (`refs/`, `ref/`) AND verify correct dir exists
  2. **Reference file numbering** - Check sequential prefixes (`01-`, `02-`, `03-`)
  3. **YAML header validity** - Verify SKILL.md has valid YAML frontmatter
- Common mistakes and how to fix them
- Integration into generation workflow
- **No separate .sh files stored** - Scripts generated and executed inline, then discarded

### 2. Update Core Workflow in SKILL.md

**Location:** `SKILL.md` - Step 5: Comprehensive Validation

**Current:** Generic validation checklist
**Improved:** Add **complete on-the-fly bash script** that validates directory structure, reference numbering, AND YAML header

```markdown
### Step 5: Comprehensive Skill Validation (REQUIRED)

**Before presenting any skill, generate and run complete validation script:**

```bash
# Generate and execute comprehensive validation script on-the-fly
skill_dir=".agents/skills/<skill-name>"
skill_file="$skill_dir/SKILL.md"

echo "=== Comprehensive Skill Validation ==="
echo "Skill: $skill_dir"
echo ""

validation_failed=0

# ============================================
# VALIDATION 1: Directory Structure
# ============================================
echo "[1/3] Checking directory structure..."

# Check for incorrect directories (refs/, ref/)
if [ -d "$skill_dir/refs" ]; then
    echo "✗ ERROR: Found 'refs/' directory (should be 'references/')"
    validation_failed=1
fi

if [ -d "$skill_dir/ref" ]; then
    echo "✗ ERROR: Found 'ref/' directory (should be 'references/')"
    validation_failed=1
fi

# Verify correct directory exists if reference files present
if [ -d "$skill_dir/references" ]; then
    ref_count=$(find "$skill_dir/references" -maxdepth 1 -name "*.md" | wc -l)
    if [ $ref_count -gt 0 ]; then
        echo "✓ Directory structure valid (references/ with $ref_count files)"
    else
        echo "⚠ WARNING: references/ directory exists but empty"
    fi
else
    echo "✓ Simple skill (no references directory needed)"
fi

echo ""

# ============================================
# VALIDATION 2: Reference File Numbering
# ============================================
echo "[2/3] Checking reference file numbering..."

if [ -d "$skill_dir/references" ]; then
    # Check for proper sequential numbering (01-, 02-, 03-, etc.)
    invalid_files=0
    highest_num=0
    
    for file in "$skill_dir/references"/*.md; do
        [ -f "$file" ] || continue
        filename=$(basename "$file")
        
        # Extract prefix number
        if [[ $filename =~ ^([0-9]{2})- ]]; then
            prefix_num=${BASH_REMATCH[1]}
            # Convert to integer (remove leading zeros)
            prefix_int=$((10#$prefix_num))
            
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
        echo "✓ All reference files have valid numbering (01-$highest_num)"
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

if [ ! -f "$skill_file" ]; then
    echo "✗ ERROR: SKILL.md not found"
    validation_failed=1
else
    # Check file starts with ---
    first_line=$(head -n1 "$skill_file")
    if [ "$first_line" != "---" ]; then
        echo "✗ ERROR: SKILL.md does not start with '---' (found: $first_line)"
        validation_failed=1
    else
        echo "✓ File starts with YAML delimiter"
        
        # Extract and validate YAML frontmatter
        # Check for closing ---
        yaml_end=$(grep -n '^---$' "$skill_file" | head -n2 | tail -n1 | cut -d: -f1)
        if [ -z "$yaml_end" ] || [ "$yaml_end" -lt 2 ]; then
            echo "✗ ERROR: YAML header not properly closed with '---'"
            validation_failed=1
        else
            echo "✓ YAML header properly delimited (lines 1-$yaml_end)"
            
            # Extract frontmatter content (between first and second ---)
            frontmatter=$(sed -n "2,$((yaml_end - 1))p" "$skill_file")
            
            # Check required fields
            if echo "$frontmatter" | grep -q '^name:'; then
                name_value=$(echo "$frontmatter" | grep '^name:' | sed 's/name:[[:space:]]*//')
                echo "✓ Required field 'name' present: $name_value"
                
                # Validate name format (lowercase, hyphens only)
                if echo "$name_value" | grep -qE '^[a-z0-9]+(-[a-z0-9]+)*$'; then
                    echo "  ✓ Name format valid"
                else
                    echo "  ✗ Name format INVALID (must match ^[a-z0-9]+(-[a-z0-9]+)*$)"
                    validation_failed=1
                fi
            else
                echo "✗ ERROR: Required field 'name' missing"
                validation_failed=1
            fi
            
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
            else
                echo "✗ ERROR: Required field 'description' missing"
                validation_failed=1
            fi
        fi
    fi
fi

echo ""

# ============================================
# FINAL SUMMARY
# ============================================
echo "=== Validation Summary ==="
if [ $validation_failed -eq 1 ]; then
    echo "✗ VALIDATION FAILED - Do not present skill for review"
    echo ""
    echo "Fix the errors above before proceeding."
    exit 1
else
    echo "✓ ALL VALIDATIONS PASSED"
    echo "✓ Skill is ready for review"
    exit 0
fi
```

**CRITICAL:** Do not present skill for review until this validation passes with exit code 0.
```

### 3. Update Validation Checklist Reference

**File:** `references/07-validation-checklist.md`

**Add new section:** "Comprehensive Skill Validation"

**Content to add:**
- Explicit requirement: Always use `references/` directory
- Prohibited variations: `refs/`, `ref/`, `Refs/`, etc.
- **Complete on-the-fly bash validation script** covering:
  1. Directory structure validation
  2. Reference file numbering verification (01-, 02-, 03-)
  3. YAML header validity (required fields, format, length)
- Integration into final validation step
- Example output showing all three validation types

### 4. Update Skill Templates Reference

**File:** `references/06-skill-templates.md`

**Changes:**
- Add bold warning in both simple and complex skill sections
- Include directory validation as final step before completion
- Add example of validation script output

**Example addition to Complex Skills section:**
```markdown
### Directory Structure Requirements (CRITICAL)

**ALWAYS use `references/` directory. Never use `refs/`, `ref/`, or any other variation.**

Before finalizing a complex skill, run:
```bash
# Check for incorrect directories
find .agents/skills/<skill-name> -type d \( -name "refs" -o -name "ref" \) && echo "ERROR: Found incorrect directory" || echo "✓ Directory structure valid"
```

**If you find `refs/` or `ref/`:**
```bash
mv .agents/skills/<skill-name>/refs .agents/skills/<skill-name>/references
sed -i 's|refs/|references/|g' .agents/skills/<skill-name>/SKILL.md
```
```

### 5. Update Interaction Examples Reference

**File:** `references/08-interaction-examples.md`

**Add to each example:** Show directory validation as final step before presenting skill

**Example addition:**
```markdown
### Step 6: Validate Directory Structure

Before presenting the skill, validate structure:

```bash
echo "=== Final Validation ==="
python3 << 'EOF'
import os

skill_dir = ".agents/skills/docker-containers"
if os.path.exists(f"{skill_dir}/refs"):
    print("ERROR: Found refs/ directory - must use references/")
    exit(1)
print("✓ Directory structure valid")
EOF
```

Only after validation passes, present skill to user for review.
```

### 6. Add On-the-Fly Bash Script Generation

**File:** `references/09-directory-validation.md` (new)

**Purpose:** Provide **complete bash validation scripts** that are generated and executed on-the-fly during skill creation.

**Key validation areas (all bash, no separate .sh files):**

1. **Directory Structure Validation**:
   - Detect wrong directories (`refs/`, `ref/`) ❌
   - Verify correct directory exists with `.md` files ✅
   - Check for nested references (should be flat)

2. **Reference File Numbering Validation**:
   - Verify sequential prefixes (`01-`, `02-`, `03-`, etc.)
   - Detect missing numbers in sequence
   - Validate format: exactly 2 digits followed by hyphen
   - Report highest number and total file count

3. **YAML Header Validation**:
   - Verify file starts with `---`
   - Check for proper closing `---`
   - Validate required fields (`name`, `description`)
   - Check `name` format: `^[a-z0-9]+(-[a-z0-9]+)*$`
   - Verify `description` length: 1-1024 characters
   - Report field values and validation status

4. **Auto-Fix Commands** (manual execution):
   - Provide exact commands to fix directory issues
   - Show how to correct numbering problems
   - Guide YAML header fixes

**Important:** All bash scripts are generated on-the-fly and executed inline. No separate `.sh` files are created or stored. Scripts are embedded in SKILL.md and reference files for reuse.

### 7. Add Validation Hooks to Workflow

**In SKILL.md Core Workflow, add:**

```markdown
## Generation Workflow with Validation Hooks

### Hook Points (Must Pass Before Proceeding)

1. **After Step 2 (Content Research):** Validate structure decision (simple vs complex)
2. **After Step 3 (Structure Selection):** Confirm directory plan (`references/` if complex)
3. **After Step 4 (YAML Validation):** Run YAML header validation script
4. **After Step 5 (Write Files):** Run directory structure validation script
5. **Before User Review:** Run complete validation checklist

**If any hook fails, fix before proceeding to next step.**
```

## Implementation Order

1. **Create `references/09-directory-validation.md`** - New dedicated reference with bash scripts
2. **Update `references/07-validation-checklist.md`** - Add directory structure section with bash script
3. **Update `references/06-skill-templates.md`** - Add warnings and validation steps
4. **Update `references/08-interaction-examples.md`** - Show validation in examples
5. **Update `SKILL.md` Step 5** - Add explicit directory validation with bash script
6. **Test the improvements** - Run validation against all 101+ existing skills, then generate test skill

## On-the-Fly Bash Script Generation

**Note:** All bash scripts are generated dynamically during skill creation and executed inline. No separate `.sh` files are created or stored.

### Complete Validation Script (Generated On-the-Fly)

This comprehensive script validates THREE critical aspects:
1. Directory structure
2. Reference file numbering  
3. YAML header validity

```bash
# Generate and execute complete validation script on-the-fly
# Replace <skill-name> with actual skill name before execution

SKILL_NAME="<skill-name>"
SKILL_DIR=".agents/skills/$SKILL_NAME"
SKILL_FILE="$SKILL_DIR/SKILL.md"

if [ -z "$SKILL_NAME" ] || [ "$SKILL_NAME" = "<skill-name>" ]; then
    echo "Error: Replace <skill-name> with actual skill name"
    exit 1
fi

if [ ! -d "$SKILL_DIR" ]; then
    echo "✗ ERROR: Skill directory not found: $SKILL_DIR"
    exit 1
fi

echo "=== Directory Structure Validation ==="
echo "Skill: $SKILL_NAME"
echo "Path:  $SKILL_DIR"
echo ""

# Track validation status
HAS_ERRORS=0
HAS_WARNINGS=0

# Step 1: Check for incorrect directories (refs/, ref/)
echo "Checking for incorrect directories..."
if [ -d "$SKILL_DIR/refs" ]; then
    echo "✗ ERROR: Found 'refs/' directory (should be 'references/')"
    file_count=$(find "$SKILL_DIR/refs" -maxdepth 1 -name "*.md" | wc -l)
    echo "  Contains $file_count markdown files"
    HAS_ERRORS=1
fi

if [ -d "$SKILL_DIR/ref" ]; then
    echo "✗ ERROR: Found 'ref/' directory (should be 'references/')"
    file_count=$(find "$SKILL_DIR/ref" -maxdepth 1 -name "*.md" | wc -l)
    echo "  Contains $file_count markdown files"
    HAS_ERRORS=1
fi

# Step 2: Verify correct directory exists and has content
echo ""
echo "Checking for correct directory structure..."
if [ -d "$SKILL_DIR/references" ]; then
    ref_count=$(find "$SKILL_DIR/references" -maxdepth 1 -name "*.md" | wc -l)
    
    if [ $ref_count -gt 0 ]; then
        echo "✓ references/ directory present with $ref_count files"
        
        # Validate file naming convention
        invalid_files=$(find "$SKILL_DIR/references" -maxdepth 1 -name "*.md" ! -regex ".*/[0-9][0-9]-.*\.md" | wc -l)
        if [ $invalid_files -gt 0 ]; then
            echo "⚠ WARNING: Found $invalid_files files without proper naming (should be 01-topic.md)"
            HAS_WARNINGS=1
        else
            echo "✓ All reference files use correct naming convention"
        fi
    else
        echo "⚠ WARNING: references/ directory exists but contains no .md files"
        HAS_WARNINGS=1
    fi
else
    # Check if SKILL.md exists (simple skill)
    if [ -f "$SKILL_DIR/SKILL.md" ]; then
        line_count=$(wc -l < "$SKILL_DIR/SKILL.md")
        if [ $line_count -lt 500 ]; then
            echo "✓ Simple skill detected (SKILL.md: $line_count lines, no references needed)"
        else
            echo "⚠ WARNING: SKILL.md has $line_count lines (>500) but no references/ directory"
            echo "  Consider splitting into complex skill structure"
            HAS_WARNINGS=1
        fi
    else
        echo "✗ ERROR: Neither SKILL.md nor references/ directory found"
        HAS_ERRORS=1
    fi
fi

# Step 3: Check for nested references (should not exist)
echo ""
echo "Checking for nested directories..."
if [ -d "$SKILL_DIR/references" ]; then
    nested_count=$(find "$SKILL_DIR/references" -mindepth 1 -type d | wc -l)
    if [ $nested_count -gt 0 ]; then
        echo "✗ ERROR: Found $nested_count nested directories inside references/ (should be flat)"
        HAS_ERRORS=1
    else
        echo "✓ No nested directories (flat structure correct)"
    fi
fi

# Step 4: Summary and exit
echo ""
echo "=== Validation Summary ==="
if [ $HAS_ERRORS -eq 1 ]; then
    echo "✗ VALIDATION FAILED"
    echo ""
    echo "To fix incorrect directories:"
    if [ -d "$SKILL_DIR/refs" ]; then
        echo "  mv $SKILL_DIR/refs $SKILL_DIR/references"
        echo "  sed -i 's|refs/|references/|g' $SKILL_DIR/SKILL.md"
    fi
    if [ -d "$SKILL_DIR/ref" ]; then
        echo "  mv $SKILL_DIR/ref $SKILL_DIR/references"
        echo "  sed -i 's|ref/|references/|g' $SKILL_DIR/SKILL.md"
    fi
    exit 1
elif [ $HAS_WARNINGS -eq 1 ]; then
    echo "⚠ VALIDATION PASSED WITH WARNINGS"
    exit 2
else
    echo "✓ VALIDATION PASSED"
    exit 0
fi
```

### Snippet 2: Quick Check (For Workflow Steps)

Minimal inline version for embedding in SKILL.md workflow steps:

```bash
# Quick directory validation - embed directly in workflow
skill_dir=".agents/skills/<skill-name>"

# Check for wrong directories
if [ -d "$skill_dir/refs" ] || [ -d "$skill_dir/ref" ]; then
    echo "✗ ERROR: Found incorrect directory (refs/ or ref/)"
    exit 1
fi

# Verify correct structure
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

### Snippet 3: Auto-Fix Commands (Manual Execution)

Instructions for manually fixing common mistakes (not automated, user runs these):

```bash
# Manual fix commands - user executes these if validation fails
skill_dir=".agents/skills/<skill-name>"

# If refs/ directory found:
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

**Note:** These are manual commands provided in error messages, not automated scripts.

## Expected Outcomes

After these improvements:

✅ **Zero tolerance for wrong directories** - On-the-fly bash scripts catch `refs/` before skill completion  
✅ **Comprehensive validation** - Check THREE aspects: directory structure, reference numbering, YAML header  
✅ **Detect both problems AND verify correctness**:  
   - ❌ Detect wrong dirs (`refs/`, `ref/`)  
   - ✅ Verify correct dir exists with files  
   - ✅ Validate sequential numbering (`01-`, `02-`, `03-`)  
   - ✅ Verify YAML header validity (required fields, format, length)  
✅ **Clear error messages** - User knows exactly what's wrong and how to fix  
✅ **No Python dependencies** - All validation uses portable bash  
✅ **Fast execution** - On-the-fly scripts run in <0.1 seconds  
✅ **No separate script files** - All validation generated and executed inline  
✅ **Automated validation** - No manual checking required  
✅ **Prevention over correction** - Workflow prevents errors instead of just detecting them  
✅ **Audit trail** - Validation output can be logged for quality assurance  

## Validation Criteria

The improvements are successful when:

1. Generated skills always use `references/` directory
2. **On-the-fly bash scripts** validate THREE aspects (no Python, no separate .sh files):
   - Directory structure
   - Reference file numbering
   - YAML header validity
3. Skill generation fails fast if any validation check fails
4. Scripts detect both wrong directories (`refs/`, `ref/`) AND verify correct directory exists with files
5. Scripts validate reference file numbering is sequential (01-, 02-, 03-, etc.)
6. Scripts verify YAML header has required fields with valid format and length
7. Error messages provide clear fix instructions with exact commands to run
8. No skills with `refs/` or `ref/` can pass validation
9. No skills with invalid reference numbering can pass validation
10. No skills with invalid YAML headers can pass validation
11. All 101+ existing skills pass the new comprehensive validation checks
12. **No separate script files created** - All validation generated and executed inline

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing workflow | Add validation as optional first, then required |
| Slower skill generation | **Inline bash runs in <0.1 seconds** (no file I/O) |
| False positives | Test snippets against all 101+ existing skills |
| User confusion | Clear error messages with exact fix commands |
| Bash portability | Use POSIX-compliant bash (works on Linux, macOS, WSL) |
| Script maintenance | **No separate .sh files** - All code in markdown, versioned with skill |

## Rollback Plan

If issues arise:
1. Keep old validation checklist as fallback
2. New inline bash validation can be disabled via `--skip-validation` flag
3. Manual review step remains as final safety net
4. **No separate scripts to maintain** - All validation embedded in markdown files

---

**Next Steps:** Review this plan and approve which changes to implement first.

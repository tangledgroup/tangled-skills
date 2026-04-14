# Validation Checklist and Cross-Platform Compatibility

This reference covers complete validation requirements for generated skills and cross-platform compatibility notes.

## Frontmatter Validation (Required for All Skills)

Before finalizing any skill, verify all frontmatter requirements:

### Required Fields (All Platforms)

- [ ] `name` matches parent directory exactly (lowercase, hyphens only)
- [ ] `name` passes regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
- [ ] `description` is 1-1024 characters
- [ ] `description` uses third person (no "I", "you", "we")
- [ ] `description` includes both WHAT the skill does and WHEN to use it

### Recommended Fields (For Best Compatibility)

- [ ] `license: MIT` is present (or user-specified license)
- [ ] `author: Your Name <email@example.com>` is present (unless user specified otherwise)
- [ ] `version: "0.x.0"` is present (e.g., `"0.2.0"`)
- [ ] `tags:` array includes relevant keywords (auto-generated or user-specified)
- [ ] `category:` field specifies skill category (e.g., `tooling`, `development`, `devops`)
- [ ] `external_references:` includes only **user-provided starting URLs** (not all crawled URLs)

### Frontmatter Validation Script

```bash
#!/bin/bash
# Validate skill frontmatter

SKILL_FILE="$1"

echo "=== Validating Frontmatter ==="

# Extract frontmatter
frontmatter=$(sed -n '/^---$/,/^---$/p' "$SKILL_FILE" | tail -n +2 | head -n -1)

# Check required fields
for field in name description; do
  if echo "$frontmatter" | grep -q "^$field:"; then
    echo "✓ $field present"
  else
    echo "✗ $field MISSING (required)"
  fi
done

# Validate name format
name=$(echo "$frontmatter" | grep "^name:" | sed 's/name:\s*//')
if echo "$name" | grep -qE '^[a-z0-9]+(-[a-z0-9]+)*$'; then
  echo "✓ name format valid: $name"
else
  echo "✗ name format INVALID: $name (must match ^[a-z0-9]+(-[a-z0-9]+)*$)"
fi

# Validate description length
desc=$(echo "$frontmatter" | grep "^description:" | sed 's/description:\s*//')
desc_length=${#desc}
if [ $desc_length -ge 1 ] && [ $desc_length -le 1024 ]; then
  echo "✓ description length valid: $desc_length chars"
else
  echo "✗ description length INVALID: $desc_length chars (must be 1-1024)"
fi

echo ""
echo "=== Frontmatter Validation Complete ==="
```

## Structure Validation (Simple Skills - SKILL.md < 500 lines)

For simple skills with single-file structure:

- [ ] All content inline in SKILL.md (no references directory)
- [ ] Focused on one specific task or workflow
- [ ] Total line count under 500 lines
- [ ] No unnecessary sections or empty headings
- [ ] Complete examples included directly in main file
- [ ] Troubleshooting section present with common issues

### Simple Skill Validation Script

```bash
#!/bin/bash
# Validate simple skill structure

SKILL_FILE="$1"
LINE_COUNT=$(wc -l < "$SKILL_FILE")

echo "=== Validating Simple Skill Structure ==="

# Check line count
if [ $LINE_COUNT -lt 500 ]; then
  echo "✓ Line count valid: $LINE_COUNT lines (< 500)"
else
  echo "✗ Line count INVALID: $LINE_COUNT lines (should be < 500 for simple skill)"
  echo "  Consider converting to complex skill with references/"
fi

# Check no references directory
if [ -d "references" ]; then
  echo "✗ references/ directory exists (simple skills should not have references)"
else
  echo "✓ No references/ directory (correct for simple skill)"
fi

# Check for key sections
for section in "## When to Use" "## Setup" "## Usage"; do
  if grep -q "$section" "$SKILL_FILE"; then
    echo "✓ Section present: $section"
  else
    echo "✗ Section MISSING: $section"
  fi
done

echo ""
echo "=== Structure Validation Complete ==="
```

## Structure Validation (Complex Skills - SKILL.md > 500 lines)

For complex skills with multi-file structure:

- [ ] Main SKILL.md acts as overview + navigation hub (under 500 lines)
- [ ] Reference files organized in `references/` directory only (flat structure, no nested references)
- [ ] Reference files use numbered prefixes (`01-`, `02-`, `03-`) for consistent ordering
- [ ] Reference files use lowercase with hyphens (e.g., `api-reference.md` not `API_Reference.md`)
- [ ] All relative links resolve correctly: `[Topic](references/01-topic.md)`
- [ ] Each reference file focused on single topic (can exceed 500 lines if needed)
- [ ] Progressive disclosure applied (high-level in SKILL.md, details in references/)
- [ ] Complex skills have clear navigation with descriptive link text
- [ ] **No nested references** - all reference files one level deep from SKILL.md

### Complex Skill Validation Script

```bash
#!/bin/bash
# Validate complex skill structure

SKILL_FILE="SKILL.md"
REF_DIR="references"

echo "=== Validating Complex Skill Structure ==="

# Check main file line count
LINE_COUNT=$(wc -l < "$SKILL_FILE")
if [ $LINE_COUNT -lt 500 ]; then
  echo "✓ SKILL.md line count valid: $LINE_COUNT lines (< 500)"
else
  echo "✗ SKILL.md too long: $LINE_COUNT lines (should be < 500 for navigation hub)"
fi

# Check for nested references (should not exist)
nested_refs=$(find "$REF_DIR" -type d ! -path "$REF_DIR" 2>/dev/null | wc -l)
if [ $nested_refs -eq 0 ]; then
  echo "✓ No nested reference directories (flat structure)"
else
  echo "✗ Found $nested_refs nested directories (should be flat structure only)"
fi

# Check references directory exists
if [ -d "$REF_DIR" ]; then
  echo "✓ references/ directory present"
  
  # Check numbered files
  ref_files=$(ls "$REF_DIR"/*.md 2>/dev/null | wc -l)
  if [ $ref_files -gt 0 ]; then
    echo "✓ Reference files found: $ref_files files"
    
    # Validate naming convention
    for file in "$REF_DIR"/*.md; do
      filename=$(basename "$file")
      if echo "$filename" | grep -qE '^[0-9]{2}-[a-z]+(-[a-z]+)*\.md$'; then
        echo "  ✓ $filename (valid naming)"
      else
        echo "  ✗ $filename (INVALID naming - should be 01-topic-name.md)"
      fi
      
      # Check line count per file
      file_lines=$(wc -l < "$file")
      if [ $file_lines -ge 200 ] && [ $file_lines -le 400 ]; then
        echo "    ✓ Line count ideal: $file_lines lines"
      elif [ $file_lines -gt 400 ]; then
        echo "    ⚠ File may be too long: $file_lines lines (consider splitting)"
      fi
    done
  else
    echo "✗ No reference files found in references/"
  fi
else
  echo "✗ references/ directory MISSING (required for complex skills)"
fi

# Check relative links resolve
echo ""
echo "Checking relative links..."
broken_links=0
while IFS= read -r link; do
  target=$(echo "$link" | grep -oP '\(references/\K[^)]+')
  if [ -n "$target" ] && [ ! -f "references/$target" ]; then
    echo "  ✗ Broken link: $target (file not found)"
    broken_links=$((broken_links + 1))
  fi
done < <(grep -oP '\[[^]]+\]\(references/[^\)]+\)' "$SKILL_FILE")

if [ $broken_links -eq 0 ]; then
  echo "✓ All relative links resolve correctly"
else
  echo "✗ Found $broken_links broken links"
fi

echo ""
echo "=== Structure Validation Complete ==="
```

## Content Quality Validation (Required for All Skills)

Verify content meets quality standards:

- [ ] Actionable instructions with concrete examples
- [ ] Clear trigger conditions in "When to Use" section
- [ ] No marketing fluff or vague statements
- [ ] Code snippets are complete, valid, and tested
- [ ] Configuration patterns shown with real values (not placeholders like `<your-key>`)
- [ ] Error handling and troubleshooting included where relevant
- [ ] Dependencies and prerequisites clearly documented

### Content Quality Checks

```bash
#!/bin/bash
# Check content quality

SKILL_FILE="$1"

echo "=== Content Quality Validation ==="

# Check for placeholder values
placeholder_count=$(grep -cE '<[a-z-]+>|{[a-z-]+}|\$[A-Z_]+' "$SKILL_FILE" 2>/dev/null || echo "0")
if [ $placeholder_count -gt 0 ]; then
  echo "⚠ Found $placeholder_count potential placeholders (ensure real values in examples)"
else
  echo "✓ No obvious placeholders in content"
fi

# Check for code examples
code_blocks=$(grep -c '```' "$SKILL_FILE" 2>/dev/null || echo "0")
if [ $((code_blocks / 2)) -ge 3 ]; then
  echo "✓ Sufficient code examples: $((code_blocks / 2)) code blocks"
else
  echo "⚠ Few code examples: $((code_blocks / 2)) blocks (consider adding more)"
fi

# Check for "When to Use" section
if grep -q "## When to Use" "$SKILL_FILE"; then
  trigger_count=$(grep -c "^\s*-" "$SKILL_FILE" | head -5)
  if [ $trigger_count -ge 3 ]; then
    echo "✓ Clear trigger conditions present"
  else
    echo "⚠ Few trigger conditions in 'When to Use' section"
  fi
else
  echo "✗ 'When to Use' section MISSING"
fi

# Check for troubleshooting
if grep -qE "(## Troubleshooting|## Common Issues|## Debug)" "$SKILL_FILE"; then
  echo "✓ Troubleshooting section present"
else
  echo "⚠ No troubleshooting section found"
fi

echo ""
echo "=== Content Quality Validation Complete ==="
```

## Cross-Platform Compatibility Notes

Generated skills should be compatible across these platforms:

### Platform-Specific Requirements

| Platform | Validation Strictness | Key Requirements | Notes |
|----------|----------------------|------------------|-------|
| **pi** | Lenient | `name`, `description` required | Warns on violations but loads skill anyway |
| **opencode** | Strict | `name`, `description` required | Skills with missing `description` are not loaded |
| **claude** | Strict | `name`, `description` required | Validates frontmatter format |
| **codex** | Strict | `name`, `description` required | Requires valid name regex and description length |

### Platform Compatibility Checklist

- [ ] `name` passes regex: `^[a-z0-9]+(-[a-z0-9]+)*$` (all platforms)
- [ ] `description` is 1-1024 characters (all platforms)
- [ ] Valid YAML syntax (all platforms)
- [ ] Relative paths for references (portable across platforms)

### Platform-Specific Optional Fields (Union)

For enhanced platform compatibility, consider adding optional fields:

```yaml
---
name: my-skill
description: <required description>
# ... other recommended fields ...

# Optional: License (pi, opencode)
license: MIT

# Optional: Compatibility notes (pi, opencode)
compatibility: |
  Requires bash and curl for web operations

# Optional: Metadata (pi, opencode) - string-to-string map
metadata:
  audience: developers
  workflow: automation

# Optional: Allowed tools (pi - experimental)
allowed-tools: bash curl read write edit

# Optional: Disable model invocation (pi)
disable-model-invocation: false
---
```

## Content Processing Validation (If URL/Directory Research Performed)

When research was performed, verify:

- [ ] HTML content converted to clean markdown when pandoc available
- [ ] PDF content properly extracted using best available method (pdftotext > ghostscript > strings)
- [ ] Optional tool detection completed and logged (pandoc, poppler-utils, ghostscript)
- [ ] robots.txt checked before crawling domains
- [ ] Rate limiting applied during URL fetching (respect crawl-delay)
- [ ] Same-domain/subdomain URLs discovered using BFS/DFS strategies
- [ ] Extracted content organized into logical reference files

## Final Validation Summary

Before presenting generated skill for review:

```bash
#!/bin/bash
# Complete validation summary

echo "=== FINAL VALIDATION SUMMARY ==="
echo ""

# Run all validations
./validate_frontmatter.sh SKILL.md
./validate_structure.sh SKILL.md  # or validate_complex_structure.sh
./validate_content.sh SKILL.md

echo ""
echo "=== READY FOR REVIEW ==="
echo "If all checks pass, skill is ready for user review and deployment."
```

## Summary

- **Frontmatter:** `name` and `description` required, valid format, specific description for proper matching
- **Structure:** Matches type (simple < 500 lines, complex > 500 lines with flat references/)
- **Content:** Actionable examples, no placeholders, troubleshooting included
- **Cross-platform:** Compatible with pi, opencode, claude, and codex
- **Links:** All relative links resolve correctly in complex skills (flat structure only)
- **Validation:** Run checklist before presenting skill for user approval

See [Interaction Examples](08-interaction-examples.md) for complete workflow examples including validation steps.

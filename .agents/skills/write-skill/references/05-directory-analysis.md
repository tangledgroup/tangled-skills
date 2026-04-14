# Directory Analysis and Pattern Detection

This reference covers directory scanning, pattern detection, and auto-detection heuristics for analyzing codebases and extracting workflows.

**First step in codebase analysis**: Run directory scanning to discover configs, scripts, env vars, and extract patterns. After this initial scan, optionally run [Git Introspection](04-git-introspection.md) to validate findings and prioritize which files to read deeply based on git history.

## Directory Scanning with Bash Commands

When user provides directories to analyze, use **bash commands as primary method**:

### Find All Relevant Files

```bash
# Find configuration files
find ./project -type f \( \
  -name "*.yaml" -o \
  -name "*.yml" -o \
  -name "*.json" -o \
  -name "*.toml" -o \
  -name "*.ini" -o \
  -name "*.cfg" -o \
  -name "*.conf" \
\) | head -50

# Find containerization files
find ./project -type f \( \
  -name "Dockerfile*" -o \
  -name "*.dockerfile" -o \
  -name "docker-compose*.yml" -o \
  -name "docker-compose*.yaml" \
\)

# Find build and automation files
find ./project -type f \( \
  -name "Makefile*" -o \
  -name "*.mk" -o \
  -name "Gemfile" -o \
  -name "Cargo.toml" -o \
  -name "go.mod" -o \
  -name "package.json" -o \
  -name "requirements*.txt" -o \
  -name "pyproject.toml" \
\)

# Find CI/CD workflows
find ./project -path "*/.github/workflows/*.yml" -o \
           -path "*/.gitlab-ci.yml" -o \
           -path "*/.circleci/config.yml" -o \
           -path "*/Jenkinsfile*"

# Find shell scripts
find ./project -type f \( \
  -name "*.sh" -o \
  -name "*.bash" -o \
  -name "*.zsh" \
\) -executable
```

### List Directory Structure

```bash
# Full tree view (if tree available)
tree -L 3 -I 'node_modules|__pycache__|.git' ./project

# Alternative with find
find ./project -type f | head -100 | sort

# Count files by type
echo "=== File Type Distribution ==="
find ./project -type f -name "*.js" | wc -l | xargs -I {} echo "JavaScript files: {}"
find ./project -type f -name "*.py" | wc -l | xargs -I {} echo "Python files: {}"
find ./project -type f -name "*.go" | wc -l | xargs -I {} echo "Go files: {}"
find ./project -type f -name "*.rs" | wc -l | xargs -I {} echo "Rust files: {}"

# Show directory sizes
du -sh ./project/* 2>/dev/null | sort -hr | head -10
```

### Search for Patterns Across Files

```bash
# Find environment variable usage (JavaScript/Node.js)
grep -r "process\.env\[" ./project --include="*.js" --include="*.ts" | head -20
grep -r "process\.env\." ./project --include="*.js" --include="*.ts" | head -20

# Find environment variable usage (Python)
grep -r "os\.environ\[" ./project --include="*.py" | head -20
grep -r "os\.getenv(" ./project --include="*.py" | head -20
grep -r "django.conf.settings" ./project --include="*.py" | head -20

# Find secrets and credentials patterns
grep -rE "(API_KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL|PRIVATE_KEY)" ./project \
  --include="*.js" --include="*.py" --include="*.go" --include="*.yaml" \
  | grep -v "test\|spec\|example" | head -30

# Find database connection strings
grep -rE "(mongodb://|postgres://|mysql://|redis://|amqp://)" ./project | head -20

# Find API endpoints and service calls
grep -rE "(fetch\(|axios\.|requests\.|http\.client)" ./project \
  --include="*.js" --include="*.py" --include="*.go" | head -30

# Find import statements (dependency discovery)
grep -r "^import " ./project --include="*.js" --include="*.ts" | sed 's/.*import .* from [\'"]//' | sed 's/[\'"].*//' | sort | uniq -c | sort -rn | head -20
grep -r "^from " ./project --include="*.py" | sed 's/^from \(.\+\) import.*/\1/' | sort | uniq -c | sort -rn | head -20
```

### Read Specific Files

```bash
# Package/dependency manifests
cat ./project/package.json 2>/dev/null | head -50
cat ./project/requirements.txt 2>/dev/null | head -50
cat ./project/go.mod 2>/dev/null | head -30

# Containerization configs
cat ./project/Dockerfile 2>/dev/null
cat ./project/docker-compose.yml 2>/dev/null | head -100

# CI/CD workflows
find ./project -path "*/.github/workflows/*.yml" -exec echo "=== {} ===" \; -exec head -50 {} \;

# README and documentation
head -100 ./project/README.md 2>/dev/null
head -100 ./project/CONTRIBUTING.md 2>/dev/null
head -100 ./project/CHANGELOG.md 2>/dev/null

# Configuration files
cat ./project/.env.example 2>/dev/null
cat ./project/.env.template 2>/dev/null
head -50 ./project/config/*.json 2>/dev/null
head -50 ./project/config/*.yaml 2>/dev/null
```

## Auto-Detection Heuristics

Apply these patterns when analyzing content to auto-detect skill requirements:

| Pattern Found | Interpretation | Action |
|--------------|----------------|--------|
| `API_KEY`, `SECRET`, `TOKEN`, `AUTH` | Required credentials | Add to `required_environment_variables` in frontmatter |
| `curl https://`, `fetch('https://` | API endpoints | Document in usage examples with endpoint URLs |
| `npm install`, `pip install`, `go get` | Dependencies | Add to Setup section with installation commands |
| `.yaml`, `.yml`, `.json` configs | Configuration patterns | Document in references/ with example configs |
| `.md` documentation files | Reference content | Save to `references/` directory as extracted docs |
| Shell scripts, Makefiles | Helper workflows | Document commands in references/ |
| Rate limit headers/docs | API constraints | Add notes to SKILL.md limitations section |
| `Dockerfile`, `docker-compose` | Containerization | Add Docker setup to skill documentation |
| `.github/workflows` | CI/CD patterns | Document deployment automation workflows |
| `process.env`, `os.environ` | Environment variables | Extract var names for required_environment_variables |
| `try/catch`, `error handling` | Error patterns | Include in troubleshooting section |
| `@deprecated`, `deprecated` | Legacy features | Note version compatibility issues |

## Environment Variable Discovery

```bash
# Comprehensive env var discovery
echo "=== Discovering Environment Variables ==="

# JavaScript/TypeScript
echo ""
echo "JavaScript/TypeScript:"
grep -roh "process\.env\.[A-Z_][A-Z0-9_]*" ./project --include="*.js" --include="*.ts" 2>/dev/null | \
  sed 's/process\.env\.//' | sort | uniq

# Python
echo ""
echo "Python:"
grep -roh "os\.getenv\(['\"][A-Z_][A-Z0-9_]*['\"]" ./project --include="*.py" 2>/dev/null | \
  sed "s/os\.getenv(['\"]//" | sed "s/['\"]//" | sort | uniq

grep -roh "os\.environ\[[\'\\\"][A-Z_][A-Z0-9_]*[\'\\\"]" ./project --include="*.py" 2>/dev/null | \
  sed "s/os\.environ\[[\'\\\"]//" | sed "s/[\'\\\"]//" | sort | uniq

# Docker/docker-compose
echo ""
echo "Docker environment:"
grep -rh "ENV\s\+" ./project --include="Dockerfile*" 2>/dev/null | \
  sed 's/ENV\s*//' | cut -d'=' -f1 | sort | uniq

grep -rh "\-\s[A-Z_][A-Z0-9_]*:" ./project --include="docker-compose*.yml" 2>/dev/null | \
  sed 's/.*-\s//' | sed 's/://' | sort | uniq

# .env files
echo ""
echo ".env files:"
find ./project -name ".env*" -type f -exec echo "=== {} ===" \; -exec grep -v '^#' {} \; 2>/dev/null | \
  cut -d'=' -f1 | sort | uniq

# Configuration files
echo ""
echo "Config files:"
grep -roh "[A-Z_][A-Z0-9_]*:\s*${" ./project --include="*.yaml" --include="*.yml" 2>/dev/null | \
  sed 's/://' | sort | uniq
```

## Dependency Discovery

```bash
# Node.js dependencies
echo "=== Node.js Dependencies ==="
if [ -f ./project/package.json ]; then
  echo "Production dependencies:"
  cat ./project/package.json | grep -A 100 '"dependencies":' | grep -B 100 '"devDependencies":' | \
    grep ':' | sed 's/[",]//' | awk '{print $1}' | sort
  
  echo ""
  echo "Dev dependencies:"
  cat ./project/package.json | grep -A 100 '"devDependencies":' | grep -B 100 '"peerDependencies":' | \
    grep ':' | sed 's/[",]//' | awk '{print $1}' | sort
fi

# Python dependencies
echo ""
echo "=== Python Dependencies ==="
if [ -f ./project/requirements.txt ]; then
  echo "From requirements.txt:"
  grep -v '^#' ./project/requirements.txt | grep -v '^$' | grep -v '^-' | head -20
fi

if [ -f ./project/pyproject.toml ]; then
  echo ""
  echo "From pyproject.toml:"
  grep -A 50 'dependencies\s*=' ./project/pyproject.toml | grep '"' | \
    sed 's/[\"[\],]//' | awk '{print $1}' | sort
fi

# Go dependencies
echo ""
echo "=== Go Dependencies ==="
if [ -f ./project/go.mod ]; then
  echo "From go.mod:"
  grep '^require' -A 100 ./project/go.mod | grep -v '^require' | \
    sed 's/^\s*//' | sed 's/\s*\/\/.*//' | grep -v ')^$' | head -20
fi

# Rust dependencies
echo ""
echo "=== Rust Dependencies ==="
if [ -f ./project/Cargo.toml ]; then
  echo "From Cargo.toml:"
  grep -A 100 '\[dependencies\]' ./project/Cargo.toml | grep -v '\[' | \
    grep '=' | cut -d'=' -f1 | sort
fi
```

## Workflow Discovery from Scripts

```bash
# Analyze shell scripts for workflow patterns
echo "=== Shell Script Analysis ==="
find ./project -name "*.sh" -type f | while read -r script; do
  echo ""
  echo "=== $(basename "$script") ==="
  
  # Extract commands used
  echo "Commands found:"
  grep -oP '^\s*\K[a-z]+\s' "$script" 2>/dev/null | sort | uniq -c | sort -rn | head -10
  
  # Look for deployment patterns
  if grep -qE '(kubectl|docker|helm|terraform|ansible)' "$script"; then
    echo "Deployment tools detected:"
    grep -oE '(kubectl|docker|helm|terraform|ansible)[^\s]*' "$script" | sort | uniq
  fi
  
  # Look for environment checks
  if grep -q 'ENV\|environment\|stage' "$script"; then
    echo "Environment variables used:"
    grep -oP '\$\{?[A-Z_][A-Z0-9_]*\}?' "$script" | sort | uniq
  fi
done

# Analyze Makefile targets
echo ""
echo "=== Makefile Targets ==="
if [ -f ./project/Makefile ]; then
  grep -E '^[a-zA-Z_-]+:' ./project/Makefile | sed 's/:.*//' | sort
fi

# Analyze package.json scripts
echo ""
echo "=== npm Scripts ==="
if [ -f ./project/package.json ]; then
  cat ./project/package.json | grep -A 20 '"scripts":' | grep ':' | \
    sed 's/[",]//' | awk '{print $1}'
fi
```

## Alternative: Read Tool (If Bash Unavailable)

```
Read file: ./project/package.json
Read file: ./project/Dockerfile
Read file: ./project/.github/workflows/ci.yml
Read file: ./project/README.md
Read file: ./project/requirements.txt
Read file: ./project/config/*.yaml
```

## What to Discover

Focus on extracting these key elements:

1. **Environment variables used** - For `required_environment_variables` in frontmatter
2. **API endpoints and service calls** - For usage examples
3. **Dependencies** (package.json, requirements.txt, go.mod) - For Setup section
4. **CI/CD workflows** (.github/workflows, Makefile targets) - For automation docs
5. **Configuration templates** - For reference files
6. **Helper scripts and utilities** - For workflow documentation

## Summary

- **Primary method**: Use bash with find/grep/cat for comprehensive analysis
- **Focus areas**: Env vars, dependencies, configs, scripts, CI/CD
- **Pattern matching**: Auto-detect required credentials, endpoints, and constraints
- **Fallback**: Use read tool if bash unavailable (less efficient)
- **Output**: Organize discovered patterns into skill frontmatter and references

See [Skill Templates](06-skill-templates.md) for how to incorporate discovered information into generated skills.

# Interaction Examples

This reference provides detailed interaction examples with expected outputs and common pitfalls for various skill generation scenarios.

## Example 1: Minimal Prompt

### User Request

```
User: "Create a skill for managing Docker containers"
```

### Agent Workflow

1. **Check available tools** (bash/curl preferred)
2. **Fetch documentation** via curl from official sources
3. **Extract commands and patterns** from crawled content
4. **Generate validated skill** with appropriate structure
5. **Present for review** before writing files

### Step-by-Step Execution

```bash
# Step 1: Tool detection
echo "=== Checking Available Tools ==="
curl --version  # Should work
command -v pandoc  # Optional enhancement
command -v pdftotext  # Optional for PDFs

# Step 2: Fetch documentation
BASE_URL="https://docs.docker.com"
curl -sL "$BASE_URL/cli/" > /tmp/docker_cli.html
curl -sL "$BASE_URL/compose/" > /tmp/docker_compose.html

# Step 3: Convert to markdown (if pandoc available)
if command -v pandoc &>/dev/null; then
  pandoc -f html -t markdown --wrap=auto /tmp/docker_cli.html > /tmp/docker_cli.md
  pandoc -f html -t markdown --wrap=auto /tmp/docker_compose.html > /tmp/docker_compose.md
fi

# Step 4: Extract key patterns
echo "=== Extracting Docker Commands ==="
grep -oP 'docker\s+\K[a-z]+' /tmp/docker_cli.md | sort | uniq -c | sort -rn | head -20

# Step 5: Detect required environment variables
echo "=== Checking for Required Env Vars ==="
grep -iE '(DOCKER_HOST|DOCKER_CERT_PATH|DOCKER_TLS_VERIFY)' /tmp/docker_cli.md

# Step 6: Estimate skill complexity
line_count=$(wc -l /tmp/docker_cli.md /tmp/docker_compose.md | tail -1 | awk '{print $1}')
echo "Total content lines: $line_count"
# If > 400 lines, use complex structure with references/
```

### Expected Output Structure

**Simple skill** (if focused on basic commands):

```
docker-containers/
└── SKILL.md  # ~350 lines with common commands inline
```

**Complex skill** (if comprehensive coverage):

```
docker-containers/
├── SKILL.md  # Overview + navigation (~450 lines)
└── references/
    ├── 01-container-lifecycle.md  # run, start, stop, rm
    ├── 02-image-management.md  # build, pull, push
    ├── 03-networking-volumes.md  # networks, volumes
    └── 04-troubleshooting.md  # common issues
```

### Frontmatter with external_references

```yaml
---
name: docker-containers
description: Manage Docker containers for building, running, and orchestrating containerized applications...
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - docker
  - containers
  - devops
category: devops
external_references:
  - url: https://docs.docker.com
    description: Official Docker documentation (user-provided starting point)
---
```

**Note:** Only the user-provided URL `https://docs.docker.com` is included, not all discovered pages during crawling.

### Common Pitfalls

- ❌ **Skipping tool detection** - Always check for bash/curl first
- ❌ **Assuming simple structure** - Estimate content size before deciding
- ❌ **Missing env vars** - Docker often needs DOCKER_HOST for remote operations
- ❌ **Incomplete examples** - Ensure all code snippets are complete and tested

---

## Example 2: With URL Research (BFS Crawling)

### User Request

```
User: "Create a skill for GitHub Actions. Check https://docs.github.com/en/actions"
```

### Agent Workflow

1. **Test bash/curl availability** (preferred method)
2. **Extract base domain**: docs.github.com
3. **Run BFS crawl** (depth 0-2) to discover all /en/actions/* pages
4. **Run DFS** on key sections (/actions/reference/) for deep coverage
5. **Convert HTML to markdown** (pandoc if available)
6. **Discover required env vars** (GH_TOKEN, etc.)
7. **Generate complete skill** with references/ containing organized docs

### Step-by-Step Execution

```bash
# Step 1: Test tools
echo "=== Testing Tools ==="
curl --version
echo "✓ curl available"

# Step 2: Extract domain
BASE_URL="https://docs.github.com/en/actions"
BASE_DOMAIN=$(echo "$BASE_URL" | sed -E 's|^https?://||' | sed -E 's|/.*||')
ROOT_DOMAIN=$(echo "$BASE_DOMAIN" | grep -oP '(?<=[.])[^.]+\.[^.]+$')
echo "Base domain: $BASE_DOMAIN"
echo "Root domain: $ROOT_DOMAIN"

# Step 3: Check robots.txt
curl -s "https://$BASE_DOMAIN/robots.txt" > /tmp/robots.txt
if grep -q "Crawl-delay:" /tmp/robots.txt; then
  crawl_delay=$(grep -oP 'Crawl-delay:\s*\K[0-9.]+' /tmp/robots.txt)
  echo "Respecting crawl-delay: $crawl_delay"
else
  crawl_delay="0.5"
fi

# Step 4: BFS crawl (depth 0-2)
echo "=== Phase 1: BFS for Structure Discovery ==="
# Use BFS script from references/02-url-crawling.md
# Expected to discover ~50 pages across /en/actions/*

# Step 5: DFS on key sections
echo "=== Phase 2: DFS for Deep Coverage ==="
for section in "/actions/reference" "/actions/guides"; do
  echo "Deep diving into: $section"
  # Use DFS script from references/02-url-crawling.md
done

# Step 6: Convert all HTML to markdown
echo "=== Converting HTML to Markdown ==="
for html_file in /tmp/bfs_results_$$/*.html; do
  basename=$(basename "$html_file" .html)
  if command -v pandoc &>/dev/null; then
    pandoc -f html -t markdown --wrap=auto "$html_file" > "/tmp/${basename}.md"
  else
    sed 's/<[^>]*>//g' "$html_file" | tr -s ' \n' > "/tmp/${basename}.txt"
  fi
done

# Step 7: Extract patterns
echo "=== Extracting GitHub Actions Patterns ==="
grep -oP 'on:\s*\K[^\\n]+' /tmp/*.md | head -20  # Triggers
grep -oP '-\s\K[a-z]+:' /tmp/*.md | sort | uniq -c | sort -rn  # Steps
grep -oP 'GH_[A-Z_]+' /tmp/*.md | sort | uniq  # Env vars

# Step 8: Estimate complexity
total_lines=$(wc -l /tmp/*.md | tail -1 | awk '{print $1}')
echo "Total extracted lines: $total_lines"
# Likely > 400 lines → complex skill with references/
```

### Expected Output Structure

```
github-actions/
├── SKILL.md  # Overview + quick start (~480 lines)
└── references/
    ├── 01-workflow-syntax.md  # YAML structure, triggers, jobs
    ├── 02-common-tasks.md  # Build, test, deploy patterns
    ├── 03-reference-api.md  # Actions, events, contexts (from deep crawl)
    ├── 04-security-best-practices.md  # Secrets, token permissions
    └── 05-troubleshooting.md  # Common workflow issues
```

### Discovery Results

**Required environment variables detected:**
- `GH_TOKEN` - GitHub API token for authentication
- `DEPLOY_KEY` - SSH key for repository access
- Various secrets referenced in workflows

**Key patterns extracted:**
- Workflow triggers: `push`, `pull_request`, `workflow_dispatch`
- Common actions: `actions/checkout`, `actions/setup-node`, `heroku/cli`
- Configuration patterns: `env` blocks, `secrets` usage, `matrix` strategies

### external_references in Generated Skill

```yaml
---
name: github-actions
description: Automate workflows with GitHub Actions for CI/CD, testing, and deployment...
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - github-actions
  - ci-cd
  - automation
category: devops
external_references:
  - url: https://docs.github.com/en/actions
    description: Official GitHub Actions documentation (user-provided starting point)
---
```

**Important:** Only the original URL `https://docs.github.com/en/actions` is included, not the ~50 pages discovered during BFS/DFS crawling.

### Common Pitfalls

- ❌ **Skipping robots.txt** - GitHub has crawl-delay requirements
- ❌ **Crawling external domains** - Stay within docs.github.com
- ❌ **Missing reference sections** - /actions/reference/ contains critical API docs
- ❌ **Not converting HTML** - Raw HTML confuses LLMs, always convert to markdown

---

## Example 3: With Directory Analysis

### User Request

```
User: "Create a skill for our deployment workflow. Analyze ./infra and ./deploy-scripts"
```

### Agent Workflow

1. **Use bash commands** for comprehensive analysis
2. **Discover configs, scripts, env vars** across directories
3. **Extract patterns and workflows** from shell scripts and YAML
4. **Generate skill** with discovered requirements and references

### Step-by-Step Execution

```bash
# Step 1: Directory structure overview
echo "=== Directory Structure ==="
find ./infra ./deploy-scripts -type f | head -50

# Step 2: Find configuration files
echo ""
echo "=== Configuration Files ==="
find ./infra -name "*.yaml" -o -name "*.yml" -o -name "*.json" | head -20

# Step 3: Discover environment variables
echo ""
echo "=== Environment Variables ==="
grep -rE "(API_KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)" ./infra ./deploy-scripts \
  --include="*.yaml" --include="*.sh" --include="*.json" | head -30

# Step 4: Analyze deployment scripts
echo ""
echo "=== Deployment Script Analysis ==="
for script in ./deploy-scripts/*.sh; do
  echo "=== $(basename "$script") ==="
  grep -oP '^\s*\K[a-z]+\s' "$script" | sort | uniq -c | sort -rn | head -10
done

# Step 5: Extract Kubernetes manifests (if present)
echo ""
echo "=== Kubernetes Resources ==="
grep -h "^kind:" ./infra/*.yaml 2>/dev/null | sort | uniq -c

# Step 6: Discover dependencies
echo ""
echo "=== Dependencies ==="
if [ -f ./infra/Dockerfile ]; then
  grep 'FROM\|RUN pip\|RUN npm' ./infra/Dockerfile
fi

# Step 7: Read key files for context
echo ""
echo "=== Key Configuration Files ==="
head -50 ./infra/k8s/*.yaml 2>/dev/null
head -100 ./deploy-scripts/deploy.sh 2>/dev/null

# Step 8: Estimate skill complexity
config_files=$(find ./infra -name "*.yaml" | wc -l)
script_files=$(find ./deploy-scripts -name "*.sh" | wc -l)
echo "Configuration files: $config_files"
echo "Script files: $script_files"
# Multiple configs + scripts → likely complex skill
```

### Expected Output Structure

```
deployment-workflow/
├── SKILL.md  # Overview of deployment process (~450 lines)
└── references/
    ├── 01-infrastructure-setup.md  # K8s manifests, configs
    ├── 02-deployment-scripts.md  # Script workflows and commands
    ├── 03-environment-configuration.md  # Required env vars and secrets
    └── 04-rollback-recovery.md  # Troubleshooting and rollback procedures
```

### Discovery Results

**Required environment variables detected:**
- `KUBECONFIG` - Kubernetes configuration path
- `DEPLOY_ENVIRONMENT` - Target environment (staging/production)
- `DOCKER_REGISTRY_TOKEN` - Container registry authentication
- Various application-specific secrets

**Key workflows extracted:**
- Build and push container images
- Apply Kubernetes manifests with kubectl
- Run health checks and validation
- Rollback procedures for failed deployments

### Common Pitfalls

- ❌ **Missing sensitive data handling** - Don't include actual secrets in skill
- ❌ **Incomplete workflow coverage** - Ensure rollback/recovery documented
- ❌ **Skipping script analysis** - Shell scripts contain critical deployment logic
- ❌ **Not checking dependencies** - Dockerfile and package manifests reveal requirements

---

## Example 4: Comprehensive Domain Crawling (Hybrid BFS+DFS)

### User Request

```
User: "Create a skill for Kubernetes. Crawl all docs at https://kubernetes.io/docs/"
```

### Agent Workflow

1. **Extract base domain**: kubernetes.io
2. **Phase 1 - BFS** (depth 0-2): Discover main documentation structure
3. **Phase 2 - DFS**: Deep dives into critical sections
4. **Respect robots.txt and rate limits** (crawl-delay: 1s)
5. **Convert all HTML to clean markdown**
6. **Generate comprehensive skill** with organized references

### Step-by-Step Execution

```bash
# Step 1: Domain extraction
BASE_URL="https://kubernetes.io/docs"
BASE_DOMAIN=$(echo "$BASE_URL" | sed -E 's|^https?://||' | sed -E 's|/.*||')
echo "Crawling domain: $BASE_DOMAIN"

# Step 2: Check robots.txt
curl -s "https://$BASE_DOMAIN/robots.txt" > /tmp/robots.txt
crawl_delay=$(grep -oP 'Crawl-delay:\s*\K[0-9.]+' /tmp/robots.txt || echo "1")
echo "Using crawl delay: ${crawl_delay}s"

# Step 3: Phase 1 - BFS for structure (depth 0-2)
echo "=== Phase 1: BFS Structure Discovery ==="
# Expected to discover:
# - /docs/concepts/ (architecture, workloads, services)
# - /docs/tasks/ (common operations)
# - /docs/reference/ (API reference)
# - /docs/tutorials/ (learning materials)
# ~30-40 pages at top levels

# Step 4: Phase 2 - DFS into critical sections
echo "=== Phase 2: DFS Deep Coverage ==="
for section in "/docs/reference/kubernetes-api" "/docs/tasks/configure-pod-container"; do
  echo "Deep diving into: $section"
  # DFS to depth 5 for comprehensive API coverage
done

# Step 5: Convert HTML to markdown
echo "=== Converting ${page_count} pages to markdown ==="
for html_file in /tmp/hybrid_results_$$/*.html; do
  if command -v pandoc &>/dev/null; then
    pandoc -f html -t markdown --wrap=auto "$html_file" > "${html_file%.html}.md"
  fi
done

# Step 6: Organize by topic
echo "=== Organizing Content ==="
# API reference docs → references/02-api-reference.md
# Concepts → references/01-core-concepts.md
# Tasks → references/03-common-tasks.md
# Troubleshooting → references/04-troubleshooting.md

# Step 7: Estimate final size
total_lines=$(wc -l /tmp/*.md | tail -1 | awk '{print $1}')
echo "Total extracted content: $total_lines lines"
# Definitely > 400 lines → complex skill with multiple reference files
```

### Expected Output Structure

```
kubernetes/
├── SKILL.md  # Overview + quick start (~500 lines)
└── references/
    ├── 01-core-concepts.md  # Pods, Deployments, Services, ConfigMaps
    ├── 02-api-reference.md  # All API objects from deep crawl (~800 lines)
    ├── 03-common-tasks.md  # Deployment, scaling, debugging patterns
    ├── 04-networking-storage.md  # NetworkPolicies, PersistentVolumes
    └── 05-troubleshooting.md  # Debugging pods, logs, events
```

### Discovery Results

**Key concepts extracted:**
- Core objects: Pod, Deployment, Service, ConfigMap, Secret
- Advanced objects: StatefulSet, DaemonSet, Job, CronJob
- Networking: Service types, Ingress, NetworkPolicy
- Storage: PersistentVolume, PersistentVolumeClaim, StorageClass

**Common patterns documented:**
- 12-factor app deployment patterns
- Rolling update strategies
- Health checks (liveness/readiness probes)
- Resource limits and requests
- Multi-namespace organization

### Common Pitfalls

- ❌ **Skipping rate limiting** - kubernetes.io has crawl-delay: 1
- ❌ **Missing API reference** - Critical for comprehensive skill
- ❌ **Not following subdomains** - Some docs on different kubernetes.io subdomains
- ❌ **Incomplete conversion** - All HTML must be converted to markdown

---

## Example 5: Complex Requirements

### User Request

```
User: "I need a skill that:
- Deploys to Kubernetes using Helm
- Reads configs from values.yaml files
- Handles secrets via external-secrets operator
- Monitors deployments with Prometheus"
```

### Agent Workflow

1. **Test bash/curl availability** (preferred method)
2. **Research each component** with targeted crawling:
   - curl https://helm.sh/docs/ (Helm deployment patterns)
   - curl https://external-secrets.io/ (secrets operator setup)
   - curl https://prometheus.io/docs/ (monitoring configs)
3. **Generate comprehensive skill** covering all requirements
4. **Create references/** with extracted documentation from each source

### Step-by-Step Execution

```bash
# Step 1: Research Helm
echo "=== Researching Helm ==="
curl -sL "https://helm.sh/docs/" > /tmp/helm_index.html
# Extract key pages
grep -oP 'href="\K/docs/[^\"]*' /tmp/helm_index.html | while read path; do
  curl -sL "https://helm.sh$path" > "/tmp/helm_${path//\//_}.html"
done

# Step 2: Research External Secrets Operator
echo "=== Researching External Secrets ==="
curl -sL "https://external-secrets.io/" > /tmp/external_secrets_index.html
curl -sL "https://external-secrets.io/latest/" > /tmp/external_secrets_docs.html

# Step 3: Research Prometheus
echo "=== Researching Prometheus ==="
curl -sL "https://prometheus.io/docs/introduction/overview/" > /tmp/prometheus_intro.html
curl -sL "https://prometheus.io/docs/prometheus/latest/configuration/configuration/" > /tmp/prometheus_config.html

# Step 4: Convert all to markdown
for html_file in /tmp/*.html; do
  if command -v pandoc &>/dev/null; then
    pandoc -f html -t markdown --wrap=auto "$html_file" > "${html_file%.html}.md"
  fi
done

# Step 5: Extract integration patterns
echo "=== Extracting Integration Patterns ==="
grep -h -oP 'helm\s+\Kinstall|values\.yaml|ExternalSecret|ServiceMonitor' /tmp/*.md | sort | uniq

# Step 6: Detect required env vars across all tools
echo "=== Required Environment Variables ==="
grep -h -oE '(HELM_|EXTERNAL_SECRETS_|PROMETHEUS_|KUBE_)' /tmp/*.md | sort | uniq

# Step 7: Estimate complexity
total_lines=$(wc -l /tmp/*.md | tail -1 | awk '{print $1}')
echo "Total content: $total_lines lines"
# Multiple tools + integrations → complex skill
```

### Expected Output Structure

```
kubernetes-helm-secrets-monitoring/
├── SKILL.md  # Overview of complete workflow (~500 lines)
└── references/
    ├── 01-helm-fundamentals.md  # Helm charts, values.yaml, releases
    ├── 02-external-secrets-setup.md  # Operator installation, ExternalSecret CRDs
    ├── 03-prometheus-monitoring.md  # ServiceMonitors, PodMonitors, alerting
    ├── 04-integration-patterns.md  # How tools work together
    └── 05-troubleshooting.md  # Debugging deployments, secrets, metrics
```

### Discovery Results

**Integration patterns extracted:**
- Helm chart structure with values.yaml templating
- ExternalSecret CRD definitions and sync strategies
- Prometheus ServiceMonitor discovery via label selectors
- Secret injection into pods via mounts or environment variables

**Required components:**
- Helm 3.x installed locally
- External Secrets Operator deployed in cluster
- Prometheus Operator (or manual Prometheus) for monitoring
- Kubernetes RBAC for secret access

### Common Pitfalls

- ❌ **Researching tools in isolation** - Must document how they integrate
- ❌ **Missing version compatibility** - Helm 3 vs 2, operator versions
- ❌ **Incomplete RBAC documentation** - Critical for secrets operator
- ❌ **Skipping monitoring setup** - Prometheus requires specific CRDs

---

## Summary of Best Practices

### Always Do

✅ Check available tools first (bash/curl preferred)  
✅ Respect robots.txt and rate limits  
✅ Convert HTML to markdown before processing  
✅ Estimate content size before choosing structure  
✅ Extract required environment variables  
✅ Include troubleshooting sections  
✅ Validate before presenting for review  

### Never Do

❌ Skip tool detection or assume availability  
❌ Crawl without checking robots.txt  
❌ Present raw HTML in skills (always convert)  
❌ Use placeholders in examples (<your-key>)  
❌ Include first/second person in descriptions  
❌ Create overlapping reference files  
❌ Skip validation checklist  

### Common Success Patterns

**Simple skills work best for:**
- Single command-line tools
- Focused workflows (one specific task)
- Small libraries with limited scope

**Complex skills needed for:**
- Frameworks with many features
- APIs with extensive documentation
- Multi-tool integrations
- Platforms with concepts + tasks + references

See [Validation Checklist](06-validation-checklist.md) for complete validation requirements before finalizing any generated skill.

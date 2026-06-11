# Search and API

## Search Commands

`gh search` provides full-text search across GitHub from the terminal. Supports code, issues, PRs, commits, and repositories.

### Searching Issues

```bash
# Search for issues
gh search issues "login bug"

# Filter by state
gh search issues "authentication" --state open

# Search with labels
gh search issues --label bug --label priority:high
```

### Searching Pull Requests

```bash
# Search PRs
gh search prs "refactor api"

# Search merged PRs
gh search prs "migration" --state merged
```

### Searching Code

```bash
# Search code across repositories
gh search code "TODO" --repo owner/repo

# Search by language
gh search code "class User" --language typescript
```

### Searching Commits

```bash
# Search commits by message
gh search commits "fix memory leak"

# Search by author
gh search commits "refactor" --author monalisa
```

### Searching Repositories

```bash
# Search repositories
gh search repos "machine learning" --language python --stars >=1000

# Search topics
gh search repos --topic devops
```

### Common Search Flags

```bash
--json fields    # JSON output with specified fields
--jq expression  # Filter with jq syntax
--limit N        # Maximum results (default 30)
--order asc|desc # Sort order
--sort field     # Sort field
--template tmpl  # Go template formatting
--web            # Open search in browser
```

## REST API

`gh api` provides direct access to the GitHub REST API:

```bash
# Basic GET request (auto-resolves {owner} and {repo})
gh api repos/{owner}/{repo}/releases

# POST with form fields
gh api repos/{owner}/{repo}/issues/123/comments \
  -f body='Hi from CLI'

# Raw string field
gh api repos/{owner}/{repo}/issues \
  -f title='New issue' \
  -f body='Description here'

# Custom HTTP method
gh api -X PATCH repos/{owner}/{repo} -f description='Updated'

# Read body from file
gh api repos/{owner}/{repo}/rulesets --input file.json

# Read body from stdin
echo '{"name":"test"}' | gh api endpoint --input -

# Custom headers
gh api -H 'Accept: application/vnd.github.v3.raw+json' \
  repos/{owner}/{repo}/contents/README.md
```

### API Response Options

```bash
# Include HTTP response headers
gh api repos/{owner}/{repo} -i

# Silent mode (no body output)
gh api repos/{owner}/{repo} --silent

# Verbose mode (full request and response)
gh api repos/{owner}/{repo} --verbose
```

### Pagination

```bash
# Fetch all pages
gh api search/issues --paginate -f q='repo:cli/cli is:open'

# Slurp all pages into array
gh api graphql --paginate --slurp -f query='
  query($endCursor: String) {
    viewer {
      repositories(first: 100, after: $endCursor) {
        nodes { nameWithOwner }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
'
```

### Caching

```bash
# Cache response for duration
gh api repos/{owner}/{repo} --cache 3600s
gh api repos/{owner}/{repo} --cache 1h
```

## GraphQL API

```bash
# Basic GraphQL query
gh api graphql -f query='
  query {
    viewer {
      login
      repositories(first: 10) {
        nodes { nameWithOwner }
      }
    }
  }
'

# With variables
gh api graphql \
  -F owner='{owner}' \
  -F name='{repo}' \
  -f query='
    query($name: String!, $owner: String!) {
      repository(owner: $owner, name: $name) {
        releases(last: 3) {
          nodes { tagName }
        }
      }
    }
  '
```

Auto-resolved variables: `{owner}`, `{repo}`, `{branch}` are replaced with values from the current repository context or `GH_REPO`.

## API Previews

Opt into GitHub API preview features:

```bash
gh api --preview baptiste,nebula repos/{owner}/{repo}
```

## Nested Parameters

Build nested JSON structures with dot notation:

```bash
# Nested object
gh api gists -F 'files[myfile.txt][content]=@myfile.txt'

# Array of values
gh api -X PATCH /orgs/{org}/properties/schema \
  -F 'properties[][property_name]=environment' \
  -F 'properties[][allowed_values][]=staging' \
  -F 'properties[][allowed_values][]=production'
```

## Attestation API

Verify software supply chain attestations:

```bash
# Verify a downloaded artifact
gh attestation verify gh_2.91.0_macOS_arm64.zip -R cli/cli

# Download attestations
gh attestation download my-artifact.tar.gz --repo owner/repo

# Filter by predicate type
gh attestation download my-artifact.tar.gz \
  --predicate-type https://slsa.dev/provenance/v1

# Verify with custom constraints
gh attestation verify artifact.bin \
  --signer-workflow cli/cli/.github/workflows/build.yml \
  --source-ref refs/tags/v1.0.0

# Download trusted root for offline verification
gh attestation trusted-root
```

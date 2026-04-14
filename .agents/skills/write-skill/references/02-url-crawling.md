# URL Crawling Strategies

This reference covers comprehensive documentation crawling strategies including BFS, DFS, and hybrid approaches for discovering and extracting content from documentation sites.

## Domain Extraction

First, extract the base domain from the provided URL to identify same-domain/subdomain URLs:

```bash
# Extract base domain (e.g., "docs.example.com" from "https://docs.example.com/guide")
BASE_URL="https://docs.example.com/guide"
BASE_DOMAIN=$(echo "$BASE_URL" | sed -E 's|^https?://||' | sed -E 's|/.*||')
echo "Crawling domain: $BASE_DOMAIN"

# For subdomain matching (include *.example.com)
ROOT_DOMAIN=$(echo "$BASE_DOMAIN" | grep -oP '(?<=[.])[^.]+\.[^.]+$' || echo "$BASE_DOMAIN")
echo "Root domain pattern: *.$ROOT_DOMAIN or $BASE_DOMAIN"

# Example outputs:
# Input: https://docs.github.com/en/actions
# BASE_DOMAIN: docs.github.com
# ROOT_DOMAIN: github.com
# Matches: docs.github.com, help.github.com, *.github.com
```

## Breadth-First Search (BFS) - Wide Coverage

**Use BFS when:** User wants comprehensive coverage of all documentation pages at similar depth levels.

**Strategy:** Discover all links from current level before going deeper. Good for mapping entire documentation structure.

### Complete BFS Crawler Script

```bash
#!/bin/bash
# BFS Crawler: Explore all pages at each depth level before going deeper

BASE_URL="https://docs.example.com"
BASE_DOMAIN=$(echo "$BASE_URL" | sed -E 's|^https?://||' | sed -E 's|/.*||')
ROOT_DOMAIN=$(echo "$BASE_DOMAIN" | grep -oP '(?<=[.])[^.]+\.[^.]+$' || echo "$BASE_DOMAIN")
MAX_DEPTH=3
MAX_PAGES=50
VISITED_FILE="/tmp/bfs_visited_$$"
QUEUE_FILE="/tmp/bfs_queue_$$"
RESULTS_DIR="/tmp/bfs_results_$$"

mkdir -p "$RESULTS_DIR"
touch "$VISITED_FILE" "$QUEUE_FILE"

# Initialize queue with base URL
echo "$BASE_URL|0" >> "$QUEUE_FILE"  # URL|depth

crawl_bfs() {
    local page_count=0
    
    while [ -s "$QUEUE_FILE" ] && [ $page_count -lt $MAX_PAGES ]; do
        # Dequeue first item (FIFO for BFS)
        current=$(head -1 "$QUEUE_FILE")
        sed -i '1d' "$QUEUE_FILE"
        
        url=$(echo "$current" | cut -d'|' -f1)
        depth=$(echo "$current" | cut -d'|' -f2)
        
        # Skip if exceeds max depth
        [ $depth -ge $MAX_DEPTH ] && continue
        
        # Skip if already visited
        grep -qF "$url" "$VISITED_FILE" 2>/dev/null && continue
        echo "$url" >> "$VISITED_FILE"
        
        # Check if URL is from same domain or subdomain
        url_domain=$(echo "$url" | sed -E 's|^https?://||' | sed -E 's|/.*||')
        if ! echo "$url_domain" | grep -qE "(^$BASE_DOMAIN$|^[^.]+\\.$ROOT_DOMAIN)"; then
            continue  # Skip external domains
        fi
        
        echo "[BFS Depth $depth] Fetching: $url"
        
        # Fetch and save content
        curl -sL "$url" > "$RESULTS_DIR/$(echo "$url" | sed 's|[^a-zA-Z0-9]|_|g').html" 2>/dev/null
        page_count=$((page_count + 1))
        
        # Extract same-domain links and add to queue
        curl -sL "$url" 2>/dev/null | grep -oP 'href="\K[^"]*' | while read -r link; do
            # Skip non-HTTP links
            [[ "$link" == \#* ]] && continue
            [[ "$link" == mailto:* ]] && continue
            [[ "$link" == tel:* ]] && continue
            
            # Convert relative to absolute URLs
            if [[ "$link" == http* ]]; then
                full_url="$link"
            elif [[ "$link" == /* ]]; then
                full_url="https://$url_domain$link"
            else
                full_url="https://$url_domain$link"
            fi
            
            # Only queue same-domain URLs not yet visited
            link_domain=$(echo "$full_url" | sed -E 's|^https?://||' | sed -E 's|/.*||')
            if echo "$link_domain" | grep -qE "(^$BASE_DOMAIN$|^[^.]+\\.$ROOT_DOMAIN)"; then
                if ! grep -qF "$full_url" "$VISITED_FILE" 2>/dev/null; then
                    new_depth=$((depth + 1))
                    echo "$full_url|$new_depth" >> "$QUEUE_FILE"
                fi
            fi
        done
        
        # Rate limiting: respect robots.txt and be polite
        sleep 0.5
    done
    
    echo "BFS complete: $page_count pages crawled"
    echo "Results saved to: $RESULTS_DIR"
}

crawl_bfs
```

### BFS Benefits

- Discovers documentation structure breadth-first
- Finds all top-level sections before diving deep
- Good for understanding overall documentation organization
- Prevents getting stuck in deep rabbit holes
- Ideal for initial site mapping

## Depth-First Search (DFS) - Deep Exploration

**Use DFS when:** User wants complete coverage of specific topic branches, following related content deeply.

**Strategy:** Follow each link chain to its fullest depth before backtracking. Good for comprehensive topic coverage.

### Complete DFS Crawler Script

```bash
#!/bin/bash
# DFS Crawler: Explore each branch deeply before moving to next

BASE_URL="https://docs.example.com/guide"
BASE_DOMAIN=$(echo "$BASE_URL" | sed -E 's|^https?://||' | sed -E 's|/.*||')
ROOT_DOMAIN=$(echo "$BASE_DOMAIN" | grep -oP '(?<=[.])[^.]+\.[^.]+$' || echo "$BASE_DOMAIN")
MAX_DEPTH=5
MAX_PAGES=100
VISITED_FILE="/tmp/dfs_visited_$$"
RESULTS_DIR="/tmp/dfs_results_$$"

mkdir -p "$RESULTS_DIR"
touch "$VISITED_FILE"

crawl_dfs() {
    local url="$1"
    local depth="${2:-0}"
    local page_count=$(wc -l < "$VISITED_FILE")
    
    # Stop conditions
    [ $depth -ge $MAX_DEPTH ] && return
    [ $page_count -ge $MAX_PAGES ] && return
    
    # Skip if already visited
    grep -qF "$url" "$VISITED_FILE" 2>/dev/null && return
    echo "$url" >> "$VISITED_FILE"
    
    # Check if URL is from same domain or subdomain
    url_domain=$(echo "$url" | sed -E 's|^https?://||' | sed -E 's|/.*||')
    if ! echo "$url_domain" | grep -qE "(^$BASE_DOMAIN$|^[^.]+\\.$ROOT_DOMAIN)"; then
        return  # Skip external domains
    fi
    
    echo "[DFS Depth $depth] Fetching: $url"
    
    # Fetch and save content
    curl -sL "$url" > "$RESULTS_DIR/$(echo "$url" | sed 's|[^a-zA-Z0-9]|_|g').html" 2>/dev/null
    
    # Extract same-domain links
    local links=$(curl -sL "$url" 2>/dev/null | grep -oP 'href="\K[^"]*')
    
    # Process links in reverse order (so first link is processed first in recursion)
    echo "$links" | tac | while read -r link; do
        # Skip non-HTTP links
        [[ "$link" == \#* ]] && continue
        [[ "$link" == mailto:* ]] && continue
        
        # Convert relative to absolute URLs
        if [[ "$link" == http* ]]; then
            full_url="$link"
        elif [[ "$link" == /* ]]; then
            full_url="https://$url_domain$link"
        else
            full_url="https://$url_domain$link"
        fi
        
        # Only recurse into same-domain URLs
        link_domain=$(echo "$full_url" | sed -E 's|^https?://||' | sed -E 's|/.*||')
        if echo "$link_domain" | grep -qE "(^$BASE_DOMAIN$|^[^.]+\\.$ROOT_DOMAIN)"; then
            if ! grep -qF "$full_url" "$VISITED_FILE" 2>/dev/null; then
                new_depth=$((depth + 1))
                crawl_dfs "$full_url" $new_depth
            fi
        fi
    done
    
    # Rate limiting
    sleep 0.3
}

crawl_dfs "$BASE_URL" 0
echo "DFS complete: $(wc -l < "$VISITED_FILE") pages crawled"
echo "Results saved to: $RESULTS_DIR"
```

### DFS Benefits

- Follows topic threads to completion
- Captures deeply nested documentation
- Good for tutorials with sequential pages
- Ensures complete coverage of specific branches
- Ideal for deep dives into API references or guides

## Hybrid Approach (Recommended)

**Use hybrid when:** Best results - combine BFS for structure discovery with DFS for deep topic coverage.

### Complete Hybrid Crawler Script

```bash
#!/bin/bash
# HYBRID Crawler: BFS for top-level, DFS for important sections

BASE_URL="https://docs.example.com"
BASE_DOMAIN=$(echo "$BASE_URL" | sed -E 's|^https?://||' | sed -E 's|/.*||')
ROOT_DOMAIN=$(echo "$BASE_DOMAIN" | grep -oP '(?<=[.])[^.]+\.[^.]+$' || echo "$BASE_DOMAIN")
VISITED_FILE="/tmp/hybrid_visited_$$"
RESULTS_DIR="/tmp/hybrid_results_$$"

mkdir -p "$RESULTS_DIR"
touch "$VISITED_FILE"

# Phase 1: BFS to discover main sections (depth 0-2)
echo "=== Phase 1: BFS for structure discovery ==="

bfs_phase() {
    local max_depth=2
    local queue_file="/tmp/hybrid_bfs_queue_$$"
    echo "$BASE_URL|0" >> "$queue_file"
    
    while [ -s "$queue_file" ]; do
        current=$(head -1 "$queue_file")
        sed -i '1d' "$queue_file"
        
        url=$(echo "$current" | cut -d'|' -f1)
        depth=$(echo "$current" | cut -d'|' -f2)
        
        [ $depth -ge $max_depth ] && continue
        grep -qF "$url" "$VISITED_FILE" 2>/dev/null && continue
        echo "$url" >> "$VISITED_FILE"
        
        url_domain=$(echo "$url" | sed -E 's|^https?://||' | sed -E 's|/.*||')
        if ! echo "$url_domain" | grep -qE "(^$BASE_DOMAIN$|^[^.]+\\.$ROOT_DOMAIN)"; then
            continue
        fi
        
        echo "[BFS Depth $depth] Fetching: $url"
        curl -sL "$url" > "$RESULTS_DIR/$(echo "$url" | sed 's|[^a-zA-Z0-9]|_|g').html" 2>/dev/null
        
        # Extract and queue links
        curl -sL "$url" 2>/dev/null | grep -oP 'href="\K[^"]*' | while read -r link; do
            [[ "$link" == \#* ]] && continue
            
            if [[ "$link" == http* ]]; then
                full_url="$link"
            elif [[ "$link" == /* ]]; then
                full_url="https://$url_domain$link"
            else
                full_url="https://$url_domain$link"
            fi
            
            link_domain=$(echo "$full_url" | sed -E 's|^https?://||' | sed -E 's|/.*||')
            if echo "$link_domain" | grep -qE "(^$BASE_DOMAIN$|^[^.]+\\.$ROOT_DOMAIN)"; then
                if ! grep -qF "$full_url" "$VISITED_FILE" 2>/dev/null; then
                    new_depth=$((depth + 1))
                    echo "$full_url|$new_depth" >> "$queue_file"
                fi
            fi
        done
        
        sleep 0.5
    done
    
    rm -f "$queue_file"
    echo "BFS phase complete: $(wc -l < "$VISITED_FILE") pages discovered"
}

# Phase 2: DFS into important sections
echo ""
echo "=== Phase 2: DFS for deep coverage ==="

dfs_phase() {
    local section_url="$1"
    local max_depth=5
    
    dfs_recursive() {
        local url="$1"
        local depth="${2:-0}"
        
        [ $depth -ge $max_depth ] && return
        grep -qF "$url" "$VISITED_FILE" 2>/dev/null && return
        echo "$url" >> "$VISITED_FILE"
        
        url_domain=$(echo "$url" | sed -E 's|^https?://||' | sed -E 's|/.*||')
        if ! echo "$url_domain" | grep -qE "(^$BASE_DOMAIN$|^[^.]+\\.$ROOT_DOMAIN)"; then
            return
        fi
        
        echo "[DFS Depth $depth] Deep diving: $url"
        curl -sL "$url" > "$RESULTS_DIR/$(echo "$url" | sed 's|[^a-zA-Z0-9]|_|g').html" 2>/dev/null
        
        curl -sL "$url" 2>/dev/null | grep -oP 'href="\K[^"]*' | tac | while read -r link; do
            [[ "$link" == \#* ]] && continue
            
            if [[ "$link" == http* ]]; then
                full_url="$link"
            elif [[ "$link" == /* ]]; then
                full_url="https://$url_domain$link"
            else
                full_url="https://$url_domain$link"
            fi
            
            link_domain=$(echo "$full_url" | sed -E 's|^https?://||' | sed -E 's|/.*||')
            if echo "$link_domain" | grep -qE "(^$BASE_DOMAIN$|^[^.]+\\.$ROOT_DOMAIN)"; then
                if ! grep -qF "$full_url" "$VISITED_FILE" 2>/dev/null; then
                    dfs_recursive "$full_url" $((depth + 1))
                fi
            fi
        done
        
        sleep 0.3
    }
    
    dfs_recursive "$section_url" 0
}

# Run BFS first
bfs_phase

# Identify key sections from BFS results and deep dive
echo ""
echo "Identifying important sections for deep crawl..."
for section_pattern in "/guide" "/api" "/tutorial" "/examples" "/reference" "/docs/"; do
    matching_files=$(ls "$RESULTS_DIR"/*$section_pattern* 2>/dev/null | head -3)
    if [ -n "$matching_files" ]; then
        echo "Found section: $section_pattern"
        # Extract URLs from filenames and deep dive
        for file in $matching_files; do
            basename_file=$(basename "$file" .html)
            # Reconstruct URL (simplified)
            section_url=$(echo "$BASE_URL$section_pattern" | sed 's|//|/|g')
            if ! grep -qF "$section_url" "$VISITED_FILE" 2>/dev/null; then
                echo "Deep diving into: $section_url"
                dfs_phase "$section_url"
            fi
        done
    fi
done

echo ""
echo "=== Hybrid crawl complete ==="
echo "Total pages: $(wc -l < "$VISITED_FILE")"
echo "Results saved to: $RESULTS_DIR"
```

## Robots.txt and Rate Limiting

**Always check robots.txt before crawling:**

```bash
# Check if crawling is allowed
ROBOTS_URL="https://$BASE_DOMAIN/robots.txt"
curl -s "$ROBOTS_URL" > /tmp/robots.txt

# Parse disallow rules (simple check)
if grep -q "Disallow: /" /tmp/robots.txt; then
    echo "WARNING: Site disallows crawling entire site"
    echo "Consider manual URL list or web_search tool instead"
elif grep -q "Disallow:" /tmp/robots.txt; then
    echo "NOTE: Some paths are disallowed:"
    grep "Disallow:" /tmp/robots.txt | head -10
fi

# Check for crawl-delay
crawl_delay=$(grep -oP 'Crawl-delay:\s*\K[0-9.]+' /tmp/robots.txt 2>/dev/null || echo "0.5")
echo "Using crawl delay: ${crawl_delay}s"

# Apply rate limiting in crawlers
sleep "$crawl_delay"
```

### Rate Limiting Best Practices

```bash
# Be polite: add delays between requests
sleep 0.5  # Between BFS level requests
sleep 0.3  # Between DFS recursive calls

# Respect Crawl-delay from robots.txt
crawl_delay=$(grep -oP 'Crawl-delay:\s*\K[0-9.]+' /tmp/robots.txt 2>/dev/null || echo "0.5")
sleep "$crawl_delay"

# Add random jitter to avoid synchronized crawls
sleep $(echo "scale=2; $crawl_delay + ($RANDOM % 100) / 100" | bc)
```

## HTML to Markdown Conversion

After crawling, convert HTML files to clean markdown:

```bash
# Batch convert all crawled HTML files to markdown
for html_file in "$RESULTS_DIR"/*.html; do
    basename=$(basename "$html_file" .html)
    
    if [ -n "$PANDOC_CMD" ]; then
        # Pandoc preserves structure: headings, lists, tables, code blocks
        $PANDOC_CMD -f html -t markdown --wrap=auto "$html_file" > "$RESULTS_DIR/${basename}.md" 2>/dev/null
        echo "Converted with pandoc: $basename"
    else
        # Fallback: basic HTML tag stripping (loses some structure)
        sed 's/<[^>]*>//g' "$html_file" | tr -s ' \n' > "$RESULTS_DIR/${basename}.txt"
        echo "Converted with basic extraction: $basename"
    fi
done

# Cleanup: remove HTML files after conversion
# rm "$RESULTS_DIR"/*.html
```

### Benefits of pandoc Conversion

- Preserves document structure (headings, lists, tables)
- Removes CSS clutter that confuses LLMs
- Handles complex layouts better than text extraction
- Converts HTML entities properly

## Alternative: web_search/web_fetch Tools

If bash/curl unavailable, use specialized tools:

```
web_search: "service-name API documentation examples site:docs.example.com"
web_fetch: "https://docs.example.com/guide"
```

### Priority Order for Crawling

1. Try bash/curl with BFS+DFS hybrid approach (most comprehensive)
2. Fall back to web_search/web_fetch if curl fails
3. Never skip research just because specialized tools missing

## What to Extract from Crawled Content

From all crawled pages, extract:
- Command syntax and examples
- Configuration patterns (YAML, JSON, env vars)
- Authentication methods and required credentials
- Rate limits and constraints
- Error handling patterns
- Troubleshooting guides
- API endpoints and usage examples
- Best practices and recommendations

### Tracking Source URLs for Frontmatter

**Important:** Only the **original URLs provided by the user** should be included in the generated skill's `external_references` frontmatter field. Do not include every crawled URL.

```bash
# Store user-provided starting URLs
USER_URLS_FILE="/tmp/user_urls.txt"
echo "https://docs.example.com" > "$USER_URLS_FILE"
echo "https://github.com/example/repo" >> "$USER_URLS_FILE"

# During crawling, track which URLs came from user input vs discovered
echo "=== User-provided starting points ==="  
cat "$USER_URLS_FILE"

# These are the only URLs that go into external_references frontmatter
# Discovered URLs during BFS/DFS should NOT be included
```

**Example:**
- User provides: `https://kubernetes.io/docs/` and `https://github.com/kubernetes/kubernetes`
- Crawler discovers: 200+ additional pages during BFS/DFS
- **external_references should contain:** Only the 2 user-provided URLs
- **NOT include:** The 200+ discovered URLs

See [Content Extraction](03-content-extraction.md) for detailed extraction workflows.

# Examples

## Contents
- Quick Search
- Batch Search
- Search with Fallback
- HTML Search
- Scrapling Search
- CAPTCHA Detection
- Pretty JSON

## Quick Search

Run `assets/example-quick-search.sh` for a single query summary:

```bash
bash assets/example-quick-search.sh "Rust programming language"
```

## Batch Search

Run `assets/example-batch-search.sh` to search multiple terms at once:

```bash
bash assets/example-batch-search.sh
```

## Search with Fallback

Run `assets/example-with-fallback.sh` for search with existence check and conditional output:

```bash
bash assets/example-with-fallback.sh "some query"
```

## HTML Search

Run `assets/example-html-search.sh` for HTML endpoint → markdown conversion (auto backend):

```bash
bash assets/example-html-search.sh "Rust programming language"
```

## Scrapling Search

Run `assets/example-scrapling-search.sh` for anti-bot HTML search using scrapling:

```bash
bash assets/example-scrapling-search.sh "Rust programming language"
```

## CAPTCHA Detection

Run `assets/example-captcha-detect.sh` to test if the HTML endpoint is blocked:

```bash
bash assets/example-captcha-detect.sh "test query"
```

Exit code 0 = clean, exit code 1 = blocked. When blocked, use the JSON API instead.

## Pretty JSON

Run `assets/example-json-pretty.sh` for pretty-printed JSON output:

```bash
bash assets/example-json-pretty.sh "AI agents"
```

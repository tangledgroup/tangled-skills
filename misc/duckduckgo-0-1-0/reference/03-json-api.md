# JSON API

## Contents
- Endpoint
- Query Parameters
- Response Fields
- Recommended jq Selectors

## Endpoint

```
http://api.duckduckgo.com/?q={query}&format=json
```

## Query Parameters

| Parameter | Description |
|-----------|-------------|
| `q` | Search query (URL-encoded) |
| `format` | Output format — `json` or `js` (JSONP) |
| `no_redirect` | Set to `1` to prevent auto-redirect on exact matches |
| `skip_disambig` | Set to `1` to skip disambiguation pages |
| `dl` | Language variant: `en-us`, `zh-cn`, etc. |
| `ka` | Set to `w` for Wikipedia-style answer box |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `Heading` | string | Title of the matched entity |
| `AbstractText` | string | Wikipedia-style summary paragraph |
| `AbstractSource` | string | Source name (e.g., "Wikipedia") |
| `AbstractURL` | string | URL to the source article |
| `Answer` | string | Direct answer for math, conversion, etc. |
| `AnswerType` | string | Type of direct answer |
| `Definition` | string | Dictionary definition (for word queries) |
| `DefinitionSource` | string | Source of the definition |
| `DefinitionURL` | string | URL to the dictionary entry |
| `Entity` | string | Entity type classification |
| `Image` | string | Relative URL to entity image/logo |
| `Infobox` | object | Structured data table (Wikipedia infobox) |
| `OfficialDomain` | string | Official domain of the entity |
| `OfficialWebsite` | string | Full official website URL |
| `Redirect` | string | Redirect target if query was disambiguated |
| `Results` | array | Search result links with text and URLs |
| `RelatedTopics` | array | Related topics with summaries and links |
| `Type` | string | Result type: `A` (abstract), `D` (definition), `R` (results), or empty |

## Recommended jq Selectors by Use Case

| Use Case | jq Filter |
|----------|-----------|
| Quick summary | `{heading: .Heading, abstract: .AbstractText}` |
| With source attribution | `{heading: .Heading, abstract: .AbstractText, source: .AbstractSource, url: .AbstractURL}` |
| Result links only | `.Results[]? \| {text: .Text, url: .FirstURL}` |
| Related topics (top 5) | `.RelatedTopics[:5][]? \| {text: .Text, url: .FirstURL}` |
| Dictionary definition | `{word: .Heading, definition: .Definition, source: .DefinitionSource}` |

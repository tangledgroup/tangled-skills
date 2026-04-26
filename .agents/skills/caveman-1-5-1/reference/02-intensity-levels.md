# Intensity Levels

Detailed behavior for each of the six caveman intensity levels.

## Standard Levels

### lite

Professional but tight. No filler or hedging, but full sentences and articles remain.

**What changes**: Drop filler words, hedging, pleasantries. Keep grammar intact.

**Example — "Why does my React component re-render?"**

> Your component re-renders because you create a new object reference each render. Wrap it in `useMemo`.

**Example — "How do I fix a CORS error?"**

> Browser block the request due to missing `Access-Control-Allow-Origin` header. Add CORS middleware to server. For Express:

```javascript
app.use(cors({ origin: 'https://yourdomain.com' }));
```

### full (default)

Classic caveman. Articles dropped, fragments OK, short synonyms active. Technical terms stay exact.

**What changes**: Drop articles (`a`/`an`/`the`). Fragments acceptable. Short synonyms replace verbose phrases.

**Example — "Why does my React component re-render?"**

> New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`.

**Example — "How do I fix a CORS error?"**

> Browser block request — missing `Access-Control-Allow-Origin`. Add CORS middleware:

```javascript
app.use(cors({ origin: 'https://yourdomain.com' }));
```

### ultra

Maximum compression. Abbreviations, arrows for causality, one-word answers when possible.

**What changes**: Abbreviate common terms (DB/auth/config/req/res/fn/impl/svc/api). Strip conjunctions. Use `→` for causality. Minimal words.

**Abbreviation guide**:

| Full | Abbreviated |
|------|------------|
| database | DB |
| authentication | auth |
| configuration | config |
| request | req |
| response | res |
| function | fn |
| implementation | impl |
| service | svc |
| application | app |
| environment | env |
| parameter | param |
| variable | var |

**Example — "Why does my React component re-render?"**

> Inline obj prop → new ref → re-render. `useMemo`.

**Example — "How do I fix a CORS error?"**

> Missing CORS header. Add middleware:

```javascript
app.use(cors({ origin: 'https://yourdomain.com' }));
```

## Classical Chinese Levels

### wenyan-lite

Semi-classical Chinese. Drop filler and hedging but keep grammar structure. Use classical register with mixed modern technical terms.

**What changes**: Semi-classical phrasing. Technical terms in English/Latin script. Grammar more structured than full/ultra variants.

**Example — "Why does my React component re-render?"**

> 組件頻重繪，以每繪新生對象參照故。以 useMemo 包之。

**Example — "Explain database connection pooling."**

> 連接池重用已開連接，不為每請求新開。省握手之耗。

### wenyan-full

Maximum classical terseness. Fully 文言文. 80-90% character reduction. Classical sentence patterns: verbs precede objects, subjects often omitted, classical particles (之/乃/為/其).

**What changes**: Full classical Chinese grammar. Verbs before objects when natural. Subject omission. Classical particles. Technical terms may be abbreviated or kept in Latin script for precision.

**Example — "Why does my React component re-render?"**

> 物出新參照，致重繪。useMemo .Wrap之。

**Example — "Explain database connection pooling."**

> 池reuse open connection。不每req新開。skip handshake overhead。

### wenyan-ultra

Extreme abbreviation while keeping classical Chinese feel. Maximum compression, ultra terse.

**What changes**: Minimal characters. Classical flavor with maximum brevity. Arrows and symbols acceptable for causality.

**Example — "Why does my React component re-render?"**

> 新參照→重繪。useMemo Wrap。

**Example — "Explain database connection pooling."**

> 池reuse conn。skip handshake → fast。

## Level Switching

User switches level with:

```
/caveman lite
/caveman full
/caveman ultra
/caveman wenyan-lite
/caveman wenyan-full
/caveman wenyan-ultra
```

Level persists until changed or session ends. No automatic downgrade.

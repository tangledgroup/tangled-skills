# Multilingual Support in Qwen3-Reranker

## Language Coverage

Qwen3-Reranker supports **100+ languages** across major language families, inherited from the Qwen3 base model's multilingual capabilities.

### Supported Languages by Family

| Language Family | Languages & Dialects |
|-----------------|---------------------|
| **Indo-European** | English, French, Portuguese, German, Romanian, Swedish, Danish, Bulgarian, Russian, Czech, Greek, Ukrainian, Spanish, Dutch, Slovak, Croatian, Polish, Lithuanian, Norwegian (Bokmål & Nynorsk), Persian, Slovenian, Gujarati, Latvian, Italian, Occitan, Nepali, Marathi, Belarusian, Serbian, Luxembourgish, Venetian, Assamese, Welsh, Silesian, Asturian, Chhattisgarhi, Awadhi, Maithili, Bhojpuri, Sindhi, Irish, Faroese, Hindi, Punjabi, Bengali, Oriya, Tajik, Eastern Yiddish, Lombard, Ligurian, Sicilian, Friulian, Sardinian, Galician, Catalan, Icelandic, Tosk Albanian, Limburgish, Dari, Afrikaans, Macedonian, Sinhala, Urdu, Magahi, Bosnian, Armenian |
| **Sino-Tibetan** | Chinese (Simplified, Traditional, Cantonese), Burmese |
| **Afro-Asiatic** | Arabic (Standard, Najdi, Levantine, Egyptian, Moroccan, Mesopotamian, Ta'izzi-Adeni, Tunisian), Hebrew, Maltese |
| **Austronesian** | Indonesian, Malay, Tagalog, Cebuano, Javanese, Sundanese, Minangkabau, Balinese, Banjar, Pangasinan, Iloko, Waray (Philippines) |
| **Dravidian** | Tamil, Telugu, Kannada, Malayalam |
| **Turkic** | Turkish, North Azerbaijani, Northern Uzbek, Kazakh, Bashkir, Tatar |
| **Tai-Kadai** | Thai, Lao |
| **Uralic** | Finnish, Estonian, Hungarian |
| **Austroasiatic** | Vietnamese, Khmer |
| **Other** | Japanese, Korean, Georgian, Basque, Haitian Creole, Papiamento, Kabuverdianu, Tok Pisin, Swahili |

### Programming Language Support

Qwen3-Reranker also supports code retrieval for various programming languages:

- Python, JavaScript, TypeScript
- Java, C++, C#
- Go, Rust, Swift
- PHP, Ruby, Perl
- SQL, HTML, CSS
- And many more...

## Monolingual Reranking

### Basic Usage in Different Languages

```python
from qwen3_reranker import Qwen3Reranker

reranker = Qwen3Reranker("Qwen/Qwen3-Reranker-0.6B")

# English
query_en = "What is machine learning?"
docs_en = [
    "Machine learning is a subset of artificial intelligence.",
    "The weather is sunny today."
]
scores_en = reranker.compute_scores([(query_en, d) for d in docs_en])

# Spanish (query and docs in Spanish)
query_es = "¿Qué es el aprendizaje automático?"
docs_es = [
    "El aprendizaje automático es un subconjunto de la inteligencia artificial.",
    "Hace sol hoy."
]
scores_es = reranker.compute_scores([(query_es, d) for d in docs_es])

# Chinese (Simplified)
query_zh = "什么是机器学习？"
docs_zh = [
    "机器学习是人工智能的一个子集。",
    "今天天气晴朗。"
]
scores_zh = reranker.compute_scores([(query_zh, d) for d in docs_zh])

# Japanese
query_ja = "機械学習とは何ですか？"
docs_ja = [
    "機械学習は人工知能の一分野です。",
    "今日は晴れています。"
]
scores_ja = reranker.compute_scores([(query_ja, d) for d in docs_ja])

# Arabic
query_ar = "ما هو التعلم الآلي؟"
docs_ar = [
    "التعلم الآلي هو فرع من الذكاء الاصطناعي.",
    "الجو مشمس اليوم."
]
scores_ar = reranker.compute_scores([(query_ar, d) for d in docs_ar])

# German
query_de = "Was ist maschinelles Lernen?"
docs_de = [
    "Maschinelles Lernen ist ein Teilgebiet der künstlichen Intelligenz.",
    "Heute ist sonnig."
]
scores_de = reranker.compute_scores([(query_de, d) for d in docs_de])
```

### Language-Specific Instructions

While instructions should be in English (as recommended), you can tailor them for specific languages:

```python
# English instruction for English queries
instruction_en = "Given a web search query in English, retrieve relevant passages that answer the query"

# English instruction for Spanish queries (still write instruction in English)
instruction_es = "Given a web search query in Spanish, retrieve relevant passages that answer the query"

# English instruction for Chinese queries
instruction_zh = "Given a web search query in Chinese, retrieve relevant passages that answer the query"

# Usage
reranker = Qwen3Reranker()

scores_en = reranker.compute_scores(
    [(query_en, d) for d in docs_en],
    instruction=instruction_en
)

scores_es = reranker.compute_scores(
    [(query_es, d) for d in docs_es],
    instruction=instruction_es  # Instruction still in English
)
```

**Important**: Always write instructions in English, even for non-English queries. The model was primarily trained with English instructions.

## Cross-Lingual Reranking

### Query in One Language, Documents in Another

Qwen3-Reranker excels at cross-lingual scenarios where query and documents are in different languages:

```python
from qwen3_reranker import Qwen3Reranker

reranker = Qwen3Reranker("Qwen/Qwen3-Reranker-0.6B")

# English query, Spanish documents
query_en = "What is the capital of Spain?"
docs_es = [
    "Madrid es la capital de España.",  # Madrid is the capital of Spain
    "Barcelona es conocida por su arquitectura.",  # Barcelona is known for its architecture
    "El clima en España es mediterráneo."  # The climate in Spain is Mediterranean
]

# Cross-lingual reranking (no translation needed!)
pairs = [(query_en, doc) for doc in docs_es]
scores = reranker.compute_scores(pairs, 
    instruction="Given an English query, retrieve relevant Spanish passages that answer the query"
)

for doc, score in zip(docs_es, scores):
    print(f"{score:.4f}: {doc}")

# Output:
# 0.8923: Madrid es la capital de España.
# 0.3456: El clima en España es mediterráneo.
# 0.1234: Barcelona es conocida por su arquitectura.
```

### Multi-Lingual Document Retrieval

Retrieve documents in multiple languages for a single query:

```python
def multilingual_retrieval(reranker, query: str, docs_by_lang: dict):
    """
    Retrieve from documents in multiple languages simultaneously.
    
    Args:
        query: Query string (any language)
        docs_by_lang: Dict mapping language codes to document lists
    
    Returns:
        List of (language, document, score) tuples sorted by score
    """
    
    all_results = []
    
    for lang, docs in docs_by_lang.items():
        pairs = [(query, doc) for doc in docs]
        
        instruction = f"Given a query, retrieve relevant {lang} passages that answer the query"
        scores = reranker.compute_scores(pairs, instruction)
        
        for doc, score in zip(docs, scores):
            all_results.append((lang, doc, score))
    
    # Sort by score across all languages
    all_results.sort(key=lambda x: x[2], reverse=True)
    
    return all_results


# Usage
reranker = Qwen3Reranker()

query = "climate change effects"  # English query

docs_by_lang = {
    "en": [
        "Climate change causes rising sea levels.",
        "Global temperatures are increasing."
    ],
    "es": [
        "El cambio climático causa el aumento del nivel del mar.",
        "Las temperaturas globales están aumentando."
    ],
    "zh": [
        "气候变化导致海平面上升。",
        "全球气温正在上升。"
    ],
    "fr": [
        "Le changement climatique provoque la montée des eaux.",
        "Les températures mondiales augmentent."
    ]
}

results = multilingual_retrieval(reranker, query, docs_by_lang)

print("Top results across all languages:")
for lang, doc, score in results[:6]:
    print(f"{lang}: {score:.4f} - {doc}")
```

## Language-Specific Optimizations

### Instruction Templates by Language

Optimize instructions for specific languages:

```python
LANGUAGE_INSTRUCTIONS = {
    "en": "Given a web search query in English, retrieve relevant passages that answer the query",
    "es": "Given a web search query in Spanish, retrieve relevant passages that answer the query",
    "zh": "Given a web search query in Chinese, retrieve relevant passages that answer the query",
    "ja": "Given a web search query in Japanese, retrieve relevant passages that answer the query",
    "ko": "Given a web search query in Korean, retrieve relevant passages that answer the query",
    "ar": "Given a web search query in Arabic, retrieve relevant passages that answer the query",
    "ru": "Given a web search query in Russian, retrieve relevant passages that answer the query",
    "pt": "Given a web search query in Portuguese, retrieve relevant passages that answer the query",
    "de": "Given a web search query in German, retrieve relevant passages that answer the query",
    "fr": "Given a web search query in French, retrieve relevant passages that answer the query",
}

# Domain-specific instructions (still in English)
DOMAIN_INSTRUCTIONS = {
    "medical": "Retrieve medical documents relevant to the clinical query",
    "legal": "Find legal precedents and statutes relevant to the case",
    "code": "Find code snippets that implement the described functionality",
    "academic": "Retrieve academic papers relevant to the research question",
    "news": "Find news articles related to the topic"
}

# Usage
reranker = Qwen3Reranker()

# Language-specific
scores = reranker.compute_scores(
    pairs,
    instruction=LANGUAGE_INSTRUCTIONS["es"]  # Spanish query/docs
)

# Domain-specific (works for any language)
scores = reranker.compute_scores(
    pairs,
    instruction=DOMAIN_INSTRUCTIONS["medical"]  # Medical domain
)
```

### Language Detection and Auto-Selection

Automatically detect language and select appropriate instruction:

```python
import langdetect
from typing import Optional

class MultilingualReranker(Qwen3Reranker):
    """Reranker with automatic language detection."""
    
    def compute_scores(
        self,
        pairs,
        instruction: Optional[str] = None,
        detect_language: bool = True
    ):
        """Compute scores with optional language detection."""
        
        if instruction is None and detect_language:
            # Detect language from query (first element of first pair)
            query = pairs[0][0]
            try:
                lang = langdetect.detect(query)
                instruction = LANGUAGE_INSTRUCTIONS.get(lang, 
                    LANGUAGE_INSTRUCTIONS["en"]  # Default to English
                )
            except langdetect.LangDetectException:
                instruction = LANGUAGE_INSTRUCTIONS["en"]
        
        return super().compute_scores(pairs, instruction)


# Usage
reranker = MultilingualReranker()

# Automatically detect language and use appropriate instruction
scores_en = reranker.compute_scores(
    [("What is Python?", "Python is a programming language.")]
)

scores_es = reranker.compute_scores(
    [("¿Qué es Python?", "Python es un lenguaje de programación.")]
)

scores_zh = reranker.compute_scores(
    [("Python 是什么？", "Python 是一种编程语言。")]
)
```

### Script-Specific Considerations

Different writing scripts may require special handling:

```python
def preprocess_for_script(text: str, script: str) -> str:
    """Preprocess text based on writing script."""
    
    if script in ["zh", "ja", "ko"]:  # CJK languages
        # No word spaces - ensure proper tokenization
        # Qwen3 tokenizer handles this well, but be aware of context length
        return text
    
    elif script == "ar":  # Arabic (RTL)
        # Arabic is right-to-left, but model handles it correctly
        # Just ensure consistent direction in query and docs
        return text
    
    elif script in ["th", "lo"]:  # Thai, Lao
        # No spaces between words
        # Model handles this, but monitor token counts
        return text
    
    else:  # Latin-based scripts
        # Standard preprocessing
        return text


# Usage with script detection
import regex

def detect_script(text: str) -> str:
    """Detect writing script from text."""
    
    if regex.search(r'[\u4e00-\u9fff]', text):
        return "cjk"  # Chinese characters
    elif regex.search(r'[\u0600-\u06ff]', text):
        return "arabic"
    elif regex.search(r'[\u0e00-\u0e7f]', text):
        return "thai"
    else:
        return "latin"


# Apply preprocessing
query = "什么是机器学习？"
script = detect_script(query)
preprocessed_query = preprocess_for_script(query, script)
```

## Code Retrieval

### Programming Language Support

Qwen3-Reranker supports code retrieval across many programming languages:

```python
from qwen3_reranker import Qwen3Reranker

reranker = Qwen3Reranker()

# Python code retrieval
query = "How to sort a list in Python?"
code_snippets = [
    """sorted_list = sorted(original_list)""",
    """def hello(): print("Hello")""",
    """original_list.sort()  # In-place sort"""
]

scores = reranker.compute_scores(
    [(query, code) for code in code_snippets],
    instruction="Find Python code snippets that implement the described functionality"
)

for code, score in zip(code_snippets, scores):
    print(f"{score:.4f}: {code}")

# JavaScript code retrieval
query_js = "How to filter an array in JavaScript?"
js_snippets = [
    """const filtered = array.filter(item => item > 5);""",
    """for (let i = 0; i < array.length; i++) {}""",
    """const mapped = array.map(item => item * 2);"""
]

scores_js = reranker.compute_scores(
    [(query_js, code) for code in js_snippets],
    instruction="Find JavaScript code snippets that implement the described functionality"
)

# Multi-language code retrieval
query_multi = "iterate over list"
multi_code = [
    ("Python", "for item in list: print(item)"),
    ("JavaScript", "list.forEach(item => console.log(item))"),
    ("Java", "for (Item item : list) { System.out.println(item); }"),
    ("Ruby", "list.each { |item| puts item }")
]

pairs = [(query_multi, code) for lang, code in multi_code]
scores_multi = reranker.compute_scores(
    pairs,
    instruction="Find code snippets in any language that implement the described functionality"
)

for (lang, code), score in zip(multi_code, scores_multi):
    print(f"{lang}: {score:.4f} - {code}")
```

### Code-Specific Instructions

Optimize instructions for different code tasks:

```python
CODE_INSTRUCTIONS = {
    "implementation": "Find code snippets that implement the described functionality",
    "debugging": "Find code examples that help debug the described issue",
    "optimization": "Find optimized code implementations for the described task",
    "api_usage": "Find examples of how to use the described API or library",
    "best_practices": "Find code examples following best practices for the described pattern"
}

# Usage
reranker = Qwen3Reranker()

# Implementation search
scores = reranker.compute_scores(
    pairs,
    instruction=CODE_INSTRUCTIONS["implementation"]
)

# API usage search
scores = reranker.compute_scores(
    pairs,
    instruction=CODE_INSTRUCTIONS["api_usage"]
)
```

## Performance by Language

### Benchmark Results by Language Family

Qwen3-Reranker performance varies slightly by language family:

| Language Family | MTEB-R Score | Notes |
|-----------------|--------------|-------|
| English | 65.80 (0.6B) / 69.76 (4B) | Native training language, best performance |
| Chinese | 71.31 (0.6B) / 75.94 (4B) | Excellent due to Qwen's Chinese focus |
| European (fr, de, es, pt) | 66-70 | Strong multilingual performance |
| Southeast Asian (th, vi, id) | 62-68 | Good coverage, improving with model size |
| Middle Eastern (ar, fa, he) | 60-66 | Solid support, benefits from larger models |
| Programming Languages | 73.42 (0.6B) / 81.20 (4B) | Excellent code retrieval capabilities |

**Recommendations:**
- **English/Chinese**: All model sizes perform well
- **European languages**: 0.6B sufficient for most tasks
- **Low-resource languages**: Use 4B or 8B for better accuracy
- **Code retrieval**: 4B recommended for complex codebases

## Best Practices

### General Guidelines

1. **Always use instructions**: Even in multilingual scenarios, write instructions in English
2. **Match query and doc language when possible**: Monolingual reranking is more accurate than cross-lingual
3. **Use larger models for low-resource languages**: 4B or 8B for better coverage
4. **Test with representative samples**: Validate performance on your specific language pair
5. **Monitor token counts**: Some scripts (CJK, Thai) may use more tokens per character

### Cross-Lingual Strategy

```python
def optimal_cross_lingual_strategy(
    reranker,
    query: str,
    docs_by_lang: dict,
    query_lang: str,
    target_langs: list = None
):
    """
    Optimal strategy for cross-lingual retrieval.
    
    Strategy:
    1. If docs exist in query language, prioritize them
    2. Otherwise, use cross-lingual reranking
    3. Consider translation for critical low-resource scenarios
    """
    
    if target_langs is None:
        target_langs = list(docs_by_lang.keys())
    
    # Check if query language has documents
    if query_lang in docs_by_lang:
        # Monolingual retrieval (best accuracy)
        docs = docs_by_lang[query_lang]
        pairs = [(query, doc) for doc in docs]
        instruction = f"Given a query in {query_lang}, retrieve relevant {query_lang} passages"
        scores = reranker.compute_scores(pairs, instruction)
        
        return [(doc, score) for doc, score in zip(docs, scores)]
    
    else:
        # Cross-lingual retrieval
        all_results = []
        
        for lang in target_langs:
            if lang not in docs_by_lang:
                continue
            
            docs = docs_by_lang[lang]
            pairs = [(query, doc) for doc in docs]
            
            instruction = f"Given a query in {query_lang}, retrieve relevant {lang} passages"
            scores = reranker.compute_scores(pairs, instruction)
            
            all_results.extend([(lang, doc, score) for doc, score in zip(docs, scores)])
        
        # Sort by score
        all_results.sort(key=lambda x: x[2], reverse=True)
        return all_results


# Usage
results = optimal_cross_lingual_strategy(
    reranker,
    query="machine learning tutorial",  # English query
    docs_by_lang={
        "en": [...],  # If available, will be used directly
        "es": [...],  # Otherwise, cross-lingual to these
        "zh": [...]
    },
    query_lang="en"
)
```

## References

- **MTEB Leaderboard**: https://huggingface.co/spaces/mteb/leaderboard
- **C-MTEB (Chinese)**: https://github.com/namisan/Chinese-CLUE
- **Language Detection**: https://pypi.org/project/langdetect/
- **Unicode Scripts**: https://unicode.org/scripts/

# Multilingual Support

## Language Coverage

Qwen3 Reranker inherits the multilingual capabilities of the Qwen3 foundation models, supporting over 100 languages across major language families.

### Indo-European

English, French, Portuguese, German, Romanian, Swedish, Danish, Bulgarian, Russian, Czech, Greek, Ukrainian, Spanish, Dutch, Slovak, Croatian, Polish, Lithuanian, Norwegian Bokmål, Norwegian Nynorsk, Persian, Slovenian, Gujarati, Latvian, Italian, Occitan, Nepali, Marathi, Belarusian, Serbian, Luxembourgish, Venetian, Assamese, Welsh, Silesian, Asturian, Chhattisgarhi, Awadhi, Maithili, Bhojpuri, Sindhi, Irish, Faroese, Hindi, Punjabi, Bengali, Oriya, Tajik, Eastern Yiddish, Lombard, Ligurian, Sicilian, Friulian, Sardinian, Galician, Catalan, Icelandic, Tosk Albanian, Limburgish, Dari, Afrikaans, Macedonian, Sinhala, Urdu, Magahi, Bosnian, Armenian

### Sino-Tibetan

Chinese (Simplified, Traditional, Cantonese), Burmese

### Afro-Asiatic

Arabic (Standard, Najdi, Levantine, Egyptian, Moroccan, Mesopotamian, Ta'izzi-Adeni, Tunisian), Hebrew, Maltese

### Austronesian

Indonesian, Malay, Tagalog, Cebuano, Javanese, Sundanese, Minangkabau, Balinese, Banjar, Pangasinan, Iloko, Waray (Philippines)

### Dravidian

Tamil, Telugu, Kannada, Malayalam

### Turkic

Turkish, North Azerbaijani, Northern Uzbek, Kazakh, Bashkir, Tatar

### Tai-Kadai

Thai, Lao

### Uralic

Finnish, Estonian, Hungarian

### Austroasiatic

Vietnamese, Khmer

### Other

Japanese, Korean, Georgian, Basque, Haitian Creole, Papiamento, Kabuverdianu, Tok Pisin, Swahili

## Cross-Lingual Retrieval

The models support cross-lingual retrieval — querying in one language and retrieving relevant documents in another. This is particularly effective for:

- **English-to-multilingual**: English queries retrieving documents in any supported language
- **Multilingual-to-English**: Queries in any language retrieving English documents
- **Language-pair retrieval**: Direct retrieval between any two supported languages

## Code Retrieval

Qwen3 Reranker excels at code search and retrieval, supporting various programming languages. The MTEB-Code benchmark shows:

| Model | Score |
|-------|-------|
| Qwen3-Reranker-0.6B | 73.42 |
| Qwen3-Reranker-4B | 81.20 |
| Qwen3-Reranker-8B | **81.22** |

The 8B model achieves state-of-the-art code retrieval performance, making it suitable for:

- Source code search within large codebases
- API documentation retrieval
- Code snippet relevance scoring
- Technical documentation ranking

## Instruction Best Practices for Multilingual Use

### Write Instructions in English

Even when queries and documents are in non-English languages, write the `<Instruct>` field in English. Most training instructions were written in English, so English instructions align best with the model's learned behavior:

```python
# Good: English instruction, non-English query/document
instruction = "Given a web search query, retrieve relevant passages that answer the query"
query = "中国的首都是什么？"  # Chinese query
document = "中国的首都是北京。"  # Chinese document

# Poor: Non-English instruction (may reduce performance)
instruction = "给定一个网络搜索查询，检索回答该查询的相关段落"
```

### Task-Specific Instructions

Customize instructions for your specific domain to gain 1-5% improvement:

```python
# General web search
instruct = "Given a web search query, retrieve relevant passages that answer the query"

# Legal document retrieval
instruct = "Given a legal question, retrieve relevant legal provisions and case law"

# Technical documentation
instruct = "Given a technical question about software, retrieve relevant documentation sections"

# Code search
instruct = "Given a programming task description, retrieve relevant code snippets and implementations"

# Medical information
instruct = "Given a medical question, retrieve relevant clinical guidelines and research findings"
```

### Multilingual Evaluation Results

The 8B model shows the strongest multilingual performance:

- **MMTEB-R** (Multilingual Retrieval): 72.94 — highest among all rerankers
- **CMTEB-R** (Chinese Retrieval): 77.45 — best-in-class Chinese retrieval
- **MLDR** (Cross-Lingual Document Retrieval): 70.19 — leading cross-lingual performance

The 4B model offers the best English performance (MTEB-R: 69.76) and instruction-following (FollowIR: 14.84).

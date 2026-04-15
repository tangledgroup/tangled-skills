# Multilingual Support in Qwen3 Embedding

Guide to using Qwen3 Embedding models for multilingual and cross-lingual applications.

## Language Coverage

Qwen3 Embedding models support 100+ languages with varying levels of performance:

### Primary Languages (Excellent Performance)
- **English**: Native training data, best performance
- **Chinese**: Extensive training, near-native quality
- **Japanese, Korean**: Strong Asian language support

### Secondary Languages (Good Performance)
- European: German, French, Spanish, Italian, Portuguese
- Southeast Asian: Vietnamese, Thai, Indonesian, Malay
- Other: Arabic, Hindi, Russian

### Supported Languages (Adequate Performance)
- 90+ additional languages with varying quality

## Monolingual Embeddings

### Encoding in Different Languages

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# English
text_en = "The cat sits on the mat."
emb_en = model.encode(text_en)

# Chinese
text_zh = "猫坐在垫子上。"
emb_zh = model.encode(text_zh)

# Spanish
text_es = "El gato está sentado en la alfombra."
emb_es = model.encode(text_es)

print(f"All embeddings have same dimension: {emb_en.shape[0]}")
```

### Language-Specific Optimization

```python
# Some languages benefit from explicit language markers
def encode_with_language(text, language):
    """Add language prefix for better encoding"""
    language_prefixes = {
        'en': '[ENG] ',
        'zh': '[CHN] ',
        'es': '[ESP] ',
        'fr': '[FRA] ',
        'de': '[GER] ',
        # Add more as needed
    }
    prefix = language_prefixes.get(language, '')
    return model.encode(f"{prefix}{text}")

# Usage
emb_en = encode_with_language("Hello world", 'en')
emb_zh = encode_with_language("你好世界", 'zh')
```

## Cross-Lingual Retrieval

### Query in One Language, Documents in Another

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# English query
query_en = "How to make coffee?"

# Multilingual corpus
corpus_multilingual = [
    ("English: Brew ground coffee with hot water.", "en"),
    ("Chinese: 将研磨好的咖啡粉用热水冲泡。", "zh"),
    ("Spanish: Prepara café molido con agua caliente.", "es"),
    ("French: Infusez le café moulu avec de l'eau chaude.", "fr"),
]

# Encode all texts
corpus_texts = [text for text, lang in corpus_multilingual]
corpus_embeddings = model.encode(corpus_texts, normalize_embeddings=True)
query_embedding = model.encode(query_en, normalize_embeddings=True)

# Compute cross-lingual similarities
similarities = corpus_embeddings @ query_embedding

for (text, lang), sim in zip(corpus_multilingual, similarities):
    print(f"{lang}: {sim:.3f} - {text[:50]}...")
```

### Language-Agnostic Search

```python
def multilingual_search(query, corpus_with_langs, top_k=5):
    """
    Search across languages without specifying query language.
    
    Args:
        query: Query text in any language
        corpus_with_langs: List of (text, language_code) tuples
        top_k: Number of results to return
    
    Returns:
        List of (text, language, similarity) sorted by similarity
    """
    model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
    
    # Encode corpus
    corpus_texts = [text for text, lang in corpus_with_langs]
    corpus_embeddings = model.encode(corpus_texts, normalize_embeddings=True)
    
    # Encode query
    query_embedding = model.encode(query, normalize_embeddings=True)
    
    # Compute similarities
    similarities = corpus_embeddings @ query_embedding
    
    # Get top-k results
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        text, lang = corpus_with_langs[idx]
        sim = similarities[idx].item()
        results.append((text, lang, sim))
    
    return results

# Usage
corpus = [
    ("Python programming tutorial", "en"),
    ("Python 编程教程", "zh"),
    ("Tutoriel de programmation Python", "fr"),
    ("Python プログラミング チュートリアル", "ja"),
]

results = multilingual_search("如何学习 Python?", corpus, top_k=3)
for text, lang, sim in results:
    print(f"{lang} ({sim:.3f}): {text}")
```

## Language Detection

### Automatic Language Identification

```python
from langdetect import detect
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

def encode_auto_detect(text):
    """Encode text with automatic language detection"""
    try:
        lang = detect(text)
        print(f"Detected language: {lang}")
    except:
        lang = "unknown"
    
    return model.encode(text)

# Usage
texts = ["Hello world", "你好世界", "Hola mundo", "Bonjour le monde"]
for text in texts:
    embedding = encode_auto_detect(text)
```

### Language-Specific Models

```python
# For critical applications, use language-optimized prompts
def smart_encode(text, detected_language=None):
    """
    Encode with language-aware prompting for better results.
    """
    model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
    
    # Language-specific optimization
    if detected_language in ['zh', 'ja', 'ko']:
        # Asian languages: no special handling needed for Qwen3
        return model.encode(text)
    elif detected_language in ['ar', 'he']:
        # RTL languages: ensure proper encoding
        return model.encode(text, truncate=True)
    else:
        # Default encoding
        return model.encode(text)
```

## Multilingual Clustering

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Multilingual documents
documents = [
    ("The weather is nice today.", "en"),
    ("今天天气很好。", "zh"),
    ("El clima está bonito hoy.", "es"),
    ("Il fait beau aujourd'hui.", "fr"),
    ("Tomorrow will be rainy.", "en"),
    ("明天会下雨。", "zh"),
    # ... more documents
]

# Encode all documents
texts = [doc for doc, lang in documents]
embeddings = model.encode(texts)

# Cluster (language-agnostic)
kmeans = KMeans(n_clusters=2, random_state=42)
clusters = kmeans.fit_predict(embeddings)

# Display clusters
for cluster_id in range(2):
    cluster_docs = [(documents[i][0], documents[i][1]) 
                    for i in range(len(documents)) if clusters[i] == cluster_id]
    print(f"\nCluster {cluster_id}:")
    for text, lang in cluster_docs:
        print(f"  [{lang}] {text}")
```

## Cross-Lingual Evaluation

### Parallel Data Evaluation

```python
from sentence_transformers import evaluation
import numpy as np

# Parallel sentences in different languages
parallel_data = [
    [("Hello world", "en"), ("你好世界", "zh")],
    [("How are you?", "en"), ("你好吗？", "zh")],
    [("Thank you", "en"), ("谢谢", "zh")],
]

model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

# Compute cross-lingual similarity
def evaluate_cross_lingual(model, parallel_pairs):
    similarities = []
    
    for pair in parallel_pairs:
        text1, lang1 = pair[0]
        text2, lang2 = pair[1]
        
        emb1 = model.encode(text1)
        emb2 = model.encode(text2)
        
        # Cosine similarity
        sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        similarities.append(sim)
    
    return np.mean(similarities), np.std(similarities)

mean_sim, std_sim = evaluate_cross_lingual(model, parallel_data)
print(f"Cross-lingual similarity: {mean_sim:.3f} ± {std_sim:.3f}")
```

## Best Practices

### 1. Model Selection for Multilingual Tasks

| Task | Recommended Model | Reason |
|------|-------------------|--------|
| English-only | 0.6B or 4B | Efficiency |
| English + Chinese | 4B | Balanced bilingual |
| 10+ languages | 8B | Best cross-lingual alignment |
| Low-resource languages | 8B | Better generalization |

### 2. Consistent Encoding

```python
# Always use same settings for query and corpus
model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")

query_emb = model.encode(query, normalize_embeddings=True, batch_size=32)
corpus_emb = model.encode(corpus, normalize_embeddings=True, batch_size=32)
```

### 3. Handle Mixed-Language Documents

```python
def encode_mixed_language(text):
    """Handle documents with multiple languages"""
    model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")
    
    # Qwen3 handles code-switching well
    # No special preprocessing needed
    return model.encode(text)

# Example: Code-switching text
mixed_text = "Hello 世界，welcome to Python 编程!"
embedding = encode_mixed_language(mixed_text)
```

### 4. Language-Balanced Datasets

When fine-tuning for multilingual tasks, ensure balanced representation:

```python
from sentence_transformers import InputExample

# Create balanced training examples
train_examples = []

# English pairs
train_examples.append(InputExample(texts=["hello", "hi"]))
train_examples.append(InputExample(texts=["goodbye", "see you"]))

# Chinese pairs  
train_examples.append(InputExample(texts=["你好", "您好"]))
train_examples.append(InputExample(texts=["再见", "拜拜"]))

# Cross-lingual pairs
train_examples.append(InputExample(texts=["hello", "你好"]))
train_examples.append(InputExample(texts=["goodbye", "再见"]))
```

## Troubleshooting

### Issue: Poor Cross-Lingual Performance

**Solutions**:
1. Upgrade to 4B or 8B model
2. Use parallel data for evaluation
3. Consider fine-tuning on multilingual data
4. Check language detection accuracy

### Issue: Inconsistent Results Across Languages

**Solutions**:
1. Ensure consistent normalization
2. Use same batch size for all languages  
3. Check for encoding/decoding issues
4. Verify tokenizer handles all scripts correctly

## See Also

- [`references/01-model-variants.md`](01-model-variants.md) - Model selection guide
- [`references/11-finetuning.md`](11-finetuning.md) - Multilingual fine-tuning
- [`references/06-semantic-search.md`](06-semantic-search.md) - Search applications

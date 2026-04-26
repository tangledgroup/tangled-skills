# Model Comparison & Benchmarks

## Embedding Models

| Model | Size | Layers | Seq Length | Embedding Dim | MRL | Instruction Aware |
|-------|------|--------|------------|---------------|-----|-------------------|
| Qwen3-Embedding-0.6B | 0.6B | 28 | 32K | 1024 | Yes | Yes |
| Qwen3-Embedding-4B | 4B | 36 | 32K | 2560 | Yes | Yes |
| Qwen3-Embedding-8B | 8B | 36 | 32K | 4096 | Yes | Yes |

MRL (Matryoshka Representation Learning) allows truncating embeddings to any dimension from 32 up to the model's native dimension.

## Reranker Models

| Model | Size | Layers | Seq Length | Instruction Aware |
|-------|------|--------|------------|-------------------|
| Qwen3-Reranker-0.6B | 0.6B | 28 | 32K | Yes |
| Qwen3-Reranker-4B | 4B | 36 | 32K | Yes |
| Qwen3-Reranker-8B | 8B | 36 | 32K | Yes |

## MTEB Multilingual Leaderboard

Qwen3-Embedding-8B ranks No.1 on the MTEB multilingual leaderboard (as of June 5, 2025).

| Model | Size | Mean (Task) | Bitext Mining | Classification | Clustering | Retrieval | STS |
|-------|------|-------------|---------------|----------------|------------|-----------|-----|
| Qwen3-Embedding-8B | 8B | **70.58** | **80.89** | **74.00** | **57.65** | **70.88** | **81.08** |
| Qwen3-Embedding-4B | 4B | 69.45 | 79.36 | 72.33 | 57.15 | 69.60 | 80.86 |
| gemini-embedding-exp-03-07 | - | 68.37 | 79.28 | 71.82 | 54.59 | 67.71 | 79.40 |
| Qwen3-Embedding-0.6B | 0.6B | 64.33 | 72.22 | 66.83 | 52.33 | 64.64 | 76.17 |
| gte-Qwen2-7B-Instruct | 7B | 62.51 | 73.92 | 61.55 | 52.77 | 60.08 | 73.98 |
| Cohere-embed-multilingual-v3.0 | - | 61.12 | 70.50 | 62.95 | 46.89 | 59.16 | 74.80 |

## MTEB English v2

| Model | Params | Mean (Task) | Classification | Clustering | Retrieval | STS |
|-------|--------|-------------|----------------|------------|-----------|-----|
| **Qwen3-Embedding-8B** | 8B | **75.22** | **90.43** | 58.57 | **69.44** | 88.58 |
| Qwen3-Embedding-4B | 4B | 74.60 | 89.84 | 57.51 | 68.46 | **88.72** |
| gemini-embedding-exp-03-07 | - | 73.30 | 90.05 | **59.39** | 64.35 | 85.29 |
| Qwen3-Embedding-0.6B | 0.6B | 70.70 | 85.76 | 54.05 | 61.83 | 86.57 |
| gte-Qwen2-7B-instruct | 7.6B | 70.72 | 88.52 | 58.97 | 58.09 | 82.69 |

## C-MTEB (Chinese)

| Model | Params | Mean (Task) | Classification | Clustering | Retrieval | STS |
|-------|--------|-------------|----------------|------------|-----------|-----|
| **Qwen3-Embedding-8B** | 8B | **73.84** | **76.97** | **80.08** | **78.21** | 63.53 |
| Qwen3-Embedding-4B | 4B | 72.27 | 75.46 | 77.89 | 77.03 | 61.26 |
| ritrieve_zh_v1 | 0.3B | 72.71 | 76.88 | 66.50 | 76.97 | **63.92** |
| Qwen3-Embedding-0.6B | 0.6B | 66.33 | 71.40 | 68.74 | 71.03 | 54.52 |

## Reranker Benchmarks

Scores based on top-100 candidates retrieved by Qwen3-Embedding-0.6B:

| Model | Params | MTEB-R | CMTEB-R | MMTEB-R | MLDR | MTEB-Code | FollowIR |
|-------|--------|--------|---------|---------|------|-----------|----------|
| Qwen3-Reranker-4B | 4B | **69.76** | 75.94 | 72.74 | 69.97 | 81.20 | **14.84** |
| Qwen3-Reranker-8B | 8B | 69.02 | **77.45** | **72.94** | **70.19** | **81.22** | 8.05 |
| Qwen3-Reranker-0.6B | 0.6B | 65.80 | 71.31 | 66.36 | 67.28 | 73.42 | 5.41 |
| Qwen3-Embedding-0.6B | 0.6B | 61.82 | 71.02 | 64.64 | 50.26 | 75.41 | 5.09 |
| BGE-reranker-v2-m3 | 0.6B | 57.03 | 72.16 | 58.36 | 59.51 | 41.38 | -0.01 |

## Supported Languages

Qwen3 Embedding supports over 100 languages across these families:

- **Indo-European**: English, French, German, Spanish, Portuguese, Russian, Hindi, Bengali, Persian, Arabic variants, and 60+ more
- **Sino-Tibetan**: Chinese (Simplified, Traditional, Cantonese), Burmese
- **Afro-Asiatic**: Arabic (Standard, Najdi, Levantine, Egyptian, Moroccan, etc.), Hebrew, Maltese
- **Austronesian**: Indonesian, Malay, Tagalog, Javanese, Sundanese
- **Dravidian**: Tamil, Telugu, Kannada, Malayalam
- **Turkic**: Turkish, Azerbaijani, Uzbek, Kazakh
- **Tai-Kadai**: Thai, Lao
- **Uralic**: Finnish, Estonian, Hungarian
- **Austroasiatic**: Vietnamese, Khmer
- **Other**: Japanese, Korean, Georgian, Basque, Swahili

Plus various programming languages for code retrieval.

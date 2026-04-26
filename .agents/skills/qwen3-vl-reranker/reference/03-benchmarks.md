# Benchmarks and Performance

## MMEB-v2 Retrieval Results

The Multimodal Massive Embedding Benchmark v2 evaluates retrieval across image, video, and visual document tasks. Rerankers are evaluated on the retrieval subset:

**Qwen3-VL-Reranker-2B** (2B):
- MMEB-v2 Retrieval Avg: 75.1
- Image Retrieval: 73.8
- Video Retrieval: 52.1
- Visual Document Retrieval: 83.4
- MMTEB Retrieval: 70.0
- JinaVDR: 80.9
- ViDoRe v3: 60.8

**Qwen3-VL-Reranker-8B** (8B):
- MMEB-v2 Retrieval Avg: 79.2
- Image Retrieval: 80.7
- Video Retrieval: 55.8
- Visual Document Retrieval: 86.3
- MMTEB Retrieval: 74.9
- JinaVDR: 83.6
- ViDoRe v3: 66.7

Both reranker variants consistently outperform their base embedding model (Qwen3-VL-Embedding-2B, which scores 73.4 on MMEB-v2 Retrieval Avg). The 8B variant achieves the best performance across most tasks.

## Comparison with Baseline Rerankers

**jina-reranker-m0** (2B) as a reference point:
- MMEB-v2 Image Retrieval: 68.2
- Visual Document Retrieval: 85.2
- JinaVDR: 82.2
- ViDoRe v3: 57.8

Qwen3-VL-Reranker-2B matches or exceeds jina-reranker-m0 on most metrics while also supporting video and mixed-modality inputs that the baseline does not handle. Qwen3-VL-Reranker-8B leads across all reported benchmarks.

## Key Observations

- The reranking stage provides a 1–6 point absolute improvement over embedding-only retrieval on MMEB-v2
- Visual document retrieval benefits most from reranking (VisDoc scores jump from ~79 to ~83–86)
- Video retrieval remains the weakest modality for all models, though Qwen3-VL-Reranker-8B leads at 55.8
- The 8B model provides the largest gains on image retrieval (+4 points over 2B reranker)

## Reproducing Evaluations

Evaluation code is available in the official GitHub repository:

1. Download evaluation data:
   ```bash
   bash data/evaluation/mmeb_v2/download_data.sh
   ```

2. Run reranker evaluation:
   ```bash
   bash scripts/evaluation/mmeb_v2/eval_reranker.sh
   ```

Run the script without arguments to see required parameters. Results are collected automatically.

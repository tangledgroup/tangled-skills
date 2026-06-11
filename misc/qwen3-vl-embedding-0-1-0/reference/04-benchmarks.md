# Benchmarks

## MMEB-V2 Results

The Multimodal Massive Embedding Benchmark V2 evaluates across 78 datasets spanning image, video, and visual document tasks. Qwen3-VL-Embedding-8B ranks first overall among all models (as of January 2026).

### Overall Scores

| Model | Size | Image Overall | Video Overall | VisDoc Overall | All |
|-------|------|---------------|---------------|----------------|-----|
| Qwen3-VL-Embedding-2B | 2B | 75.0 | 61.9 | 79.2 | **73.2** |
| Qwen3-VL-Embedding-8B | 8B | **80.1** | **67.1** | **82.4** | **77.8** |
| Seed-1.6-embedding-1215 | ? | 78.0 | 67.7 | 82.2 | 76.9 |
| IFM-TTE | 8B | 77.9 | 59.2 | 79.5 | 74.1 |
| RzenEmbed | 8B | 75.9 | 55.7 | 81.3 | 72.9 |
| Ops-MM-embedding-v1 | 8B | 72.7 | 53.8 | 74.4 | 68.9 |

### Image Task Breakdown (Qwen3-VL-Embedding-8B)

- Image Classification: 74.2
- Image Question Answering: **81.1**
- Image Retrieval: **80.0**
- Image Grounding: **92.2**
- Image Overall: **80.1**

### Video Task Breakdown (Qwen3-VL-Embedding-8B)

- Video Classification: 78.4
- Video Question Answering: **71.0**
- Video Retrieval: 58.7
- Video Moment Retrieval: **56.1**
- Video Overall: 67.1

### Visual Document Task Breakdown (Qwen3-VL-Embedding-8B)

- ViDoRe v1: 87.2
- ViDoRe v2: **69.9**
- VisRAG: 88.7
- Out-of-Distribution: **73.3**
- VisDoc Overall: **82.4**

## MMTEB Results

The Multimodal Massive Text Embedding Benchmark evaluates text-oriented embedding tasks with multimodal models compared against text-only baselines.

| Model | Size | Mean (Task) | Retrieval | STS |
|-------|------|-------------|-----------|-----|
| Qwen3-Embedding-8B | 8B | **70.6** | **70.9** | **81.1** |
| Qwen3-VL-Embedding-8B | 8B | 67.9 | 69.4 | 75.4 |
| Gemini Embedding | ? | 68.4 | 67.7 | 79.4 |
| Qwen3-Embedding-4B | 4B | 69.5 | 69.6 | 80.9 |
| Qwen3-VL-Embedding-2B | 2B | 63.9 | 67.1 | 74.3 |

Note: The text-only Qwen3-Embedding models score higher on pure text MMTEB tasks. Use Qwen3-VL-Embedding when multimodal capability is needed; use Qwen3-Embedding for text-only workloads.

## Key Takeaways

- **Qwen3-VL-Embedding-8B** achieves state-of-the-art overall MMEB-V2 score of 77.8, leading across image and visual document categories
- **Qwen3-VL-Embedding-2B** delivers strong 2B-class performance at 73.2 overall, surpassing larger competitors
- The 8B model dominates Image QA (81.1), Image Retrieval (80.0), and Image Grounding (92.2)
- For pure text tasks, the text-only Qwen3-Embedding series remains competitive; choose VL variant for multimodal needs
- Instruction usage typically adds 1-5% improvement across tasks

## Reproducing Evaluations

### MMEB-V2 Embedding Evaluation

```bash
# Download evaluation data
bash data/evaluation/mmeb_v2/download_data.sh

# Run evaluation
bash scripts/evaluation/mmeb_v2/eval_embedding.sh
```

Run the script without arguments to see required parameters. The script evaluates all tasks and collects results automatically.

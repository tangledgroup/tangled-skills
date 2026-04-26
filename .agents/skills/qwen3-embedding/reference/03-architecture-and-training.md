# Architecture & Training

## Model Architecture

Qwen3 Embedding models are built on the Qwen3 dense foundation LLMs. Two architectural patterns are used:

### Dual-Encoder (Embedding Models)

The embedding model processes a single text segment as input. The semantic representation is extracted from the hidden state vector corresponding to the final `[EOS]` token position (last-token pooling). This dual-encoder design enables efficient approximate nearest neighbor search via cosine similarity on pre-computed embeddings.

Key architectural choices:
- Last-token pooling (not mean-pooling)
- L2 normalization of output vectors
- Matryoshka Representation Learning for flexible dimension truncation
- Instruction-aware input formatting

### Cross-Encoder (Reranking Models)

The reranking model takes text pairs (query + document) as input and calculates a relevance score. It uses the full cross-attention between query and document tokens, enabling more precise scoring at the cost of higher compute during inference. The output is a probability distribution over "yes"/"no" (relevant/not relevant), converted to a continuous score via softmax.

## Training Pipeline

### Embedding Model: Three-Stage Training

**Stage 1 — Contrastive Pre-Training**: Large-scale weakly supervised contrastive learning on massive text pairs. The Qwen3 foundation model itself was used to synthesize high-quality, diverse training data across multiple domains and languages. A novel multi-task adaptable prompt system dynamically generated weakly supervised text pairs tailored to different task types and languages, overcoming the limitations of traditional community-forum-based data collection.

**Stage 2 — Supervised Fine-Tuning**: High-quality labeled data for supervised training on specific downstream tasks including retrieval, classification, clustering, and bitext mining.

**Stage 3 — Model Merging**: Multiple candidate models from Stage 2 are integrated through a merging strategy to enhance overall performance and robustness.

### Reranking Model: Direct Supervised Training

The reranker uses a simpler pipeline — directly trained on high-quality labeled data without the contrastive pre-training stage. This was chosen based on empirical validation showing it significantly improved training efficiency for cross-encoder architectures.

### LoRA Fine-Tuning

Both embedding and reranking models use LoRA (Low-Rank Adaptation) fine-tuning on top of the frozen Qwen3 foundation model. This preserves the base model's text understanding capabilities while adapting it specifically for embedding/reranking tasks.

## Key Design Decisions

**Why Last-Token Pooling**: The `[EOS]` token position aggregates information from the entire sequence through self-attention, making it a natural summary vector. This is more effective than mean-pooling for instruction-aware models where the instruction provides task context.

**Why Matryoshka Dimensions**: MRL allows deploying the same model at different embedding sizes depending on storage and latency constraints. A 4096-dim embedding from the 8B model can be truncated to 512 or 256 dimensions with minimal quality degradation for many tasks, enabling significant storage savings in vector databases.

**Why Instruction-Aware**: Instructions allow a single model to adapt to different retrieval scenarios (web search, code retrieval, legal documents) without fine-tuning. The instruction acts as a task-conditioning signal that shifts the embedding space appropriately.

## Citation

```bibtex
@article{qwen3embedding,
  title={Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models},
  author={Zhang, Yanzhao and Li, Mingxin and Long, Dingkun and Zhang, Xin and Lin, Huan and Yang, Baosong and Xie, Pengjun and Yang, An and Liu, Dayiheng and Lin, Junyang and Huang, Fei and Zhou, Jingren},
  journal={arXiv preprint arXiv:2506.05176},
  year={2025}
}
```

## Resources

- GitHub: https://github.com/QwenLM/Qwen3-Embedding
- Hugging Face Collection: https://huggingface.co/collections/Qwen/qwen3-embedding-6841b2055b99c44d9a4c371f
- ModelScope: https://modelscope.cn/collections/Qwen3-Embedding-3edc3762d50f48
- Blog: https://qwenlm.github.io/blog/qwen3-embedding/
- Paper: https://arxiv.org/abs/2506.05176
- API: https://bailian.console.aliyun.com/?tab=model#/model-market/detail/text-embedding-v4
- Discord: https://discord.gg/yPEP2vHTu4

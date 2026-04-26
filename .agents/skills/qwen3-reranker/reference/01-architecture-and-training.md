# Architecture and Training

## Cross-Encoder Design

Qwen3 Reranker uses a cross-encoder architecture built on top of Qwen3 dense foundation models. Unlike dual-encoder (bi-encoder) embedding models that independently encode queries and documents, the cross-encoder processes the full concatenated input through all transformer layers, allowing every query token to attend to every document token.

This joint encoding produces significantly more accurate relevance judgments but is computationally more expensive per pair — hence its role as a reranker in two-stage retrieval rather than a primary retriever over large corpora.

### Input Format

The model expects inputs formatted with explicit XML-like tags:

```
<Instruct>: {instruction text}
<Query>: {query text}
<Document>: {document text}
```

The instruction provides task context. The default instruction is:

> Given a web search query, retrieve relevant passages that answer the query

### Output Mechanism

The model functions as a binary classifier with a "yes" or "no" head. At inference:

1. The full prompt (system + user message with Instruct/Query/Document) is tokenized
2. The model generates logits for the next token position
3. Logits for the tokens "yes" and "no" are extracted
4. A softmax over these two logits gives the probability that the document is relevant

The internal chat template wraps this as:

```
<|im_start|>system
Judge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>
<|im_start|>user
<Instruct>: {instruction}
<Query>: {query}
<Document>: {document}<|im_end|>
<|im_start|>assistant
<think>

</think>


```

The `<think>` tags are part of the Qwen3 reasoning template but are left empty for reranking — the model directly outputs the yes/no judgment.

### Token Architecture

- **Architecture class**: `Qwen3ForCausalLM` (loaded via `AutoModelForCausalLM`)
- **Model type**: `qwen3`
- **EOS token**: `<|im_end|>`
- **Pad token**: `<|endoftext|>`
- **No BOS token**

## Training Pipeline

### Foundation Models

Each reranker is fine-tuned from the corresponding Qwen3 Base model:

| Reranker | Base Model |
|----------|-----------|
| Qwen3-Reranker-0.6B | Qwen/Qwen3-0.6B-Base (28 layers) |
| Qwen3-Reranker-4B | Qwen/Qwen3-4B-Base (36 layers) |
| Qwen3-Reranker-8B | Qwen/Qwen3-8B-Base (36 layers) |

### LoRA Fine-Tuning

The rerankers use LoRA (Low-Rank Adaptation) fine-tuning to adapt the base models for relevance scoring. This approach:

- Preserves the full text understanding capabilities of the foundation model
- Requires training only a small number of additional parameters
- Enables efficient multi-task adaptation

### Training Data

Unlike the embedding models which use a three-stage pipeline (contrastive pre-training → supervised fine-tuning → model merging), the reranking models use a simpler approach:

1. **Direct supervised training** on high-quality labeled relevance data
2. Training pairs cover multiple domains, languages, and task types
3. The Qwen3 LLMs themselves are used to synthesize high-quality training data across domains and languages

This direct supervised approach was chosen based on empirical validation — it produces strong results with simpler training infrastructure.

### Model Merging

For the embedding models in the series, effective model merging strategies are applied to integrate multiple candidate models. The reranking models benefit from this same methodology where applicable.

## Performance Characteristics

- **Context length**: 32K tokens (supports long documents and queries)
- **Batch processing**: Full padding and batching support via standard tokenizer
- **Memory requirements**: Scales with model size — 0.6B fits on consumer GPUs, 8B requires multi-GPU or large VRAM
- **Throughput**: Cross-encoder design means each query-document pair is a full forward pass; vLLM with prefix caching provides significant acceleration when reranking multiple documents against the same query

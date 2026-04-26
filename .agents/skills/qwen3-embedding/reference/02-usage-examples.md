# Usage Examples

## Requirements

All Qwen3 Embedding models require `transformers>=4.51.0`. Using earlier versions produces `KeyError: 'qwen3'`.

## Embedding with Sentence Transformers

The simplest integration path. Requires `sentence-transformers>=2.7.0`.

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")

# For better performance, enable flash attention and left padding:
# model = SentenceTransformer(
#     "Qwen/Qwen3-Embedding-0.6B",
#     model_kwargs={"attn_implementation": "flash_attention_2", "device_map": "auto"},
#     tokenizer_kwargs={"padding_side": "left"},
# )

queries = ["What is the capital of China?", "Explain gravity"]
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other.",
]

# Use prompt_name="query" for queries to apply the built-in instruction prefix
query_embeddings = model.encode(queries, prompt_name="query")
document_embeddings = model.encode(documents)

similarity = model.similarity(query_embeddings, document_embeddings)
print(similarity)
# tensor([[0.7646, 0.1414],
#         [0.1355, 0.6000]])
```

## Embedding with Raw Transformers

Full control over tokenization and pooling. Requires manual last-token pooling and L2 normalization.

```python
import torch
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel

def last_token_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]

def get_detailed_instruct(task_description: str, query: str) -> str:
    return f'Instruct: {task_description}\nQuery:{query}'

task = 'Given a web search query, retrieve relevant passages that answer the query'
queries = [
    get_detailed_instruct(task, 'What is the capital of China?'),
    get_detailed_instruct(task, 'Explain gravity'),
]
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other.",
]
input_texts = queries + documents

tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-Embedding-0.6B', padding_side='left')
model = AutoModel.from_pretrained('Qwen/Qwen3-Embedding-0.6B')

# Recommended for GPU:
# model = AutoModel.from_pretrained(
#     'Qwen/Qwen3-Embedding-0.6B',
#     attn_implementation="flash_attention_2",
#     torch_dtype=torch.float16
# ).cuda()

batch_dict = tokenizer(input_texts, padding=True, truncation=True, max_length=8192, return_tensors="pt")
batch_dict = {k: v.to(model.device) for k, v in batch_dict.items()}

with torch.no_grad():
    outputs = model(**batch_dict)
    embeddings = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
    embeddings = F.normalize(embeddings, p=2, dim=1)

scores = (embeddings[:2] @ embeddings[2:].T)
print(scores.tolist())
# [[0.7645568251609802, 0.14142508804798126],
#  [0.13549736142158508, 0.5999549627304077]]
```

## Embedding with vLLM

Requires `vllm>=0.8.5`. Best for high-throughput serving.

```python
import torch
from vllm import LLM

def get_detailed_instruct(task_description: str, query: str) -> str:
    return f'Instruct: {task_description}\nQuery:{query}'

task = 'Given a web search query, retrieve relevant passages that answer the query'
queries = [
    get_detailed_instruct(task, 'What is the capital of China?'),
    get_detailed_instruct(task, 'Explain gravity'),
]
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other.",
]
input_texts = queries + documents

model = LLM(model="Qwen/Qwen3-Embedding-0.6B", task="embed")
outputs = model.embed(input_texts)
embeddings = torch.tensor([o.outputs.embedding for o in outputs])
scores = (embeddings[:2] @ embeddings[2:].T)
print(scores.tolist())
# [[0.7620252966880798, 0.14078938961029053],
#  [0.1358368694782257, 0.6013815999031067]]
```

## Embedding with Text Embeddings Inference (TEI)

Deploy as a REST API service via Docker.

GPU deployment:
```bash
docker run --gpus all -p 8080:80 -v hf_cache:/data \
  --pull always ghcr.io/huggingface/text-embeddings-inference:1.7.2 \
  --model-id Qwen/Qwen3-Embedding-0.6B --dtype float16
```

CPU deployment:
```bash
docker run -p 8080:80 -v hf_cache:/data \
  --pull always ghcr.io/huggingface/text-embeddings-inference:cpu-1.7.2 \
  --model-id Qwen/Qwen3-Embedding-0.6B --dtype float16
```

Query the API:
```bash
curl http://localhost:8080/embed \
  -X POST \
  -d '{"inputs": ["Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: What is the capital of China?"]}' \
  -H "Content-Type: application/json"
```

## Matryoshka (MRL) — Custom Output Dimensions

Truncate embeddings to any dimension for storage/compute trade-offs. With raw Transformers, slice the output after pooling:

```python
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-Embedding-8B', padding_side='left')
model = AutoModel.from_pretrained('Qwen/Qwen3-Embedding-8B')

texts = ["Example document for embedding"]
batch_dict = tokenizer(texts, padding=True, truncation=True, max_length=8192, return_tensors="pt")
batch_dict = {k: v.to(model.device) for k, v in batch_dict.items()}

with torch.no_grad():
    outputs = model(**batch_dict)
    embeddings = outputs.last_hidden_state[:, -1, :]  # last token

# Full 4096-dim embedding
full_embed = F.normalize(embeddings, p=2, dim=1)

# Truncated to 512 dimensions
reduced_embed = F.normalize(embeddings[:, :512], p=2, dim=1)

print(full_embed.shape)   # torch.Size([1, 4096])
print(reduced_embed.shape) # torch.Size([1, 512])
```

With Sentence Transformers, use the `truncate_dim` parameter:
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Qwen/Qwen3-Embedding-8B")
embeddings = model.encode(["Example text"], truncate_dim=256)
print(embeddings.shape)  # (1, 256)
```

## Reranker with Transformers

The reranker uses a cross-encoder architecture with chat-template formatting.

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def format_instruction(instruction, query, doc):
    if instruction is None:
        instruction = 'Given a web search query, retrieve relevant passages that answer the query'
    return f"<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}"

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-Reranker-0.6B", padding_side='left')
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-Reranker-0.6B").eval()

# Recommended for GPU:
# model = AutoModelForCausalLM.from_pretrained(
#     "Qwen/Qwen3-Reranker-0.6B",
#     torch_dtype=torch.float16,
#     attn_implementation="flash_attention_2"
# ).cuda().eval()

token_false_id = tokenizer.convert_tokens_to_ids("no")
token_true_id = tokenizer.convert_tokens_to_ids("yes")
max_length = 8192

prefix = """<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".\n<|im_end|>\n<|im_start|>user\n"""
suffix = """<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n"""
prefix_tokens = tokenizer.encode(prefix, add_special_tokens=False)
suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

task = 'Given a web search query, retrieve relevant passages that answer the query'
queries = ["What is the capital of China?", "Explain gravity"]
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other.",
]

pairs = [format_instruction(task, q, d) for q, d in zip(queries, documents)]

# Build inputs with prefix/suffix tokens
inputs_list = []
for text in pairs:
    encoded = tokenizer(text, padding=False, truncation='longest_first',
                        return_attention_mask=False,
                        max_length=max_length - len(prefix_tokens) - len(suffix_tokens))
    full_ids = prefix_tokens + encoded['input_ids'] + suffix_tokens
    inputs_list.append(full_ids)

inputs = tokenizer.pad(inputs_list, padding=True, return_tensors="pt", max_length=max_length)
inputs = {k: v.to(model.device) for k, v in inputs.items()}

with torch.no_grad():
    batch_scores = model(**inputs).logits[:, -1, :]
    true_vector = batch_scores[:, token_true_id]
    false_vector = batch_scores[:, token_false_id]
    batch_scores = torch.stack([false_vector, true_vector], dim=1)
    batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
    scores = batch_scores[:, 1].exp().tolist()

print("scores:", scores)
```

## Two-Stage Retrieval Pipeline

Combine embedding (recall) with reranker (precision):

```python
# Stage 1: Dense retrieval with embedding model
from sentence_transformers import SentenceTransformer

embed_model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
query_emb = embed_model.encode(["What causes rainbows?"], prompt_name="query")
doc_embs = embed_model.encode(candidate_documents)  # thousands of docs
similarity = embed_model.similarity(query_emb, doc_embs)[0]
top_100_indices = similarity.topk(100).indices.tolist()
top_100_docs = [candidate_documents[i] for i in top_100_indices]

# Stage 2: Rerank with cross-encoder
reranker_scores = rerank(query="What causes rainbows?", documents=top_100_docs)
final_ranking = sorted(zip(top_100_docs, reranker_scores), key=lambda x: x[1], reverse=True)
```

## Instruction Customization Tips

- Always add instructions to queries, never to documents
- Write instructions in English even for non-English queries
- Tailor instructions to your specific task:
  - `"Given a programming question, retrieve relevant code snippets"`
  - `"Given a product review query, retrieve similar customer reviews"`
  - `"Given a legal question, retrieve relevant case law passages"`
- Not using instructions typically drops retrieval performance by 1-5%

# vLLM Deployment

## Overview

vLLM provides high-throughput serving for Qwen3 Reranker models with support for prefix caching, tensor parallelism, and GPU memory optimization. This is the recommended approach for production deployments requiring low latency at scale.

Requires `vllm>=0.8.5`.

## Complete vLLM Implementation

```python
import math
import torch
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.distributed.parallel_state import destroy_model_parallel
from vllm.inputs.data import TokensPrompt

# --- Setup ---

model_name = "Qwen/Qwen3-Reranker-0.6B"
number_of_gpu = torch.cuda.device_count()

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.padding_side = "left"
tokenizer.pad_token = tokenizer.eos_token

model = LLM(
    model=model_name,
    tensor_parallel_size=number_of_gpu,
    max_model_len=10000,
    enable_prefix_caching=True,
    gpu_memory_utilization=0.8,
)

# --- Token IDs for yes/no classification ---

true_token = tokenizer("yes", add_special_tokens=False).input_ids[0]
false_token = tokenizer("no", add_special_tokens=False).input_ids[0]

# Suffix tokens: the assistant prefix with empty thinking tags
suffix = "<|im_start|>assistant\n<think>\n\n</think>\n\n"
max_length = 8192
suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

# Sampling params: force output to be only yes or no tokens
sampling_params = SamplingParams(
    temperature=0,
    max_tokens=1,
    logprobs=20,
    allowed_token_ids=[true_token, false_token],
)

# --- Input Formatting ---

def format_instruction(instruction, query, doc):
    return [
        {
            "role": "system",
            "content": 'Judge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".',
        },
        {
            "role": "user",
            "content": f"<Instruct>: {instruction}\n\n<Query>: {query}\n\n<Document>: {doc}",
        },
    ]

def process_inputs(pairs, instruction, max_length, suffix_tokens):
    messages = [format_instruction(instruction, q, d) for q, d in pairs]
    # Apply chat template with thinking disabled
    token_lists = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=False, enable_thinking=False
    )
    # Truncate and append suffix tokens
    token_lists = [ele[:max_length] + suffix_tokens for ele in token_lists]
    return [TokensPrompt(prompt_token_ids=ele) for ele in token_lists]

def compute_logits(model, messages, sampling_params, true_token, false_token):
    outputs = model.generate(messages, sampling_params, use_tqdm=False)
    scores = []
    for output in outputs:
        final_logits = output.outputs[0].logprobs[-1]

        true_logit = final_logits.get(true_token, type(final_logits).keys().__class__()).logprob if true_token in final_logits else -10
        false_logit = final_logits.get(false_token, type(final_logits).keys().__class__()).logprob if false_token in final_logits else -10

        # Fallback for missing tokens
        if true_token not in final_logits:
            true_logit = -10
        else:
            true_logit = final_logits[true_token].logprob
        if false_token not in final_logits:
            false_logit = -10
        else:
            false_logit = final_logits[false_token].logprob

        true_score = math.exp(true_logit)
        false_score = math.exp(false_logit)
        score = true_score / (true_score + false_score)
        scores.append(score)
    return scores

# --- Run Inference ---

instruction = "Given a web search query, retrieve relevant passages that answer the query"
queries = [
    "What is the capital of China?",
    "Explain gravity",
]
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other. It gives weight to physical objects.",
]

pairs = list(zip(queries, documents))
inputs = process_inputs(pairs, instruction, max_length - len(suffix_tokens), suffix_tokens)
scores = compute_logits(model, inputs, sampling_params, true_token, false_token)
print("scores:", scores)

# Cleanup distributed state
destroy_model_parallel()
```

## Key Configuration Parameters

**`enable_prefix_caching=True`**: Critical for reranking efficiency. When reranking multiple documents against the same query, the system and query prefix tokens are cached, so only the document portion requires recomputation. This dramatically reduces per-document latency.

**`tensor_parallel_size`**: Set to the number of available GPUs. The 4B model benefits from 2 GPUs, the 8B model from 2-4 GPUs depending on VRAM.

**`max_model_len`**: Controls maximum sequence length. Default 10000 is sufficient for most reranking; increase to 32768 for full 32K context support (requires more memory).

**`gpu_memory_utilization=0.8`**: Reserves 20% of GPU memory for overhead and KV cache. Adjust based on batch size requirements.

**`allowed_token_ids=[true_token, false_token]`**: Constrains generation to only "yes" or "no" tokens, ensuring valid classification output.

## Performance Tips

- Use `enable_thinking=False` in `apply_chat_template` to skip reasoning step overhead
- Batch documents with the same query together to maximize prefix cache hits
- For the 8B model, consider quantization (AWQ, GPTQ) if VRAM is limited
- Monitor KV cache utilization — large batches with long documents may exceed cache capacity

# libllama C API

## Overview

The `libllama` library provides a C-style API header at `include/llama.h`. It is the core interface for building applications on top of llama.cpp.

## Core Data Structures

### Model Loading

```c
// Default model parameters
struct llama_model_params {
    int32_t n_gpu_layers;       // layers to offload to GPU
    void *cuda_context;         // CUDA context
    bool progress_callback;     // progress callback flag
    void *progress_callback_user_data;
    enum llama_vocab_type vocab_type;
    enum llama_rope_scaling_type rope_scaling_type;
    float rope_freq_base;
    float rope_freq_scale;
    float yarn_ext_factor;
    float yarn_attn_factor;
    float yarn_beta_fast;
    float yarn_beta_slow;
    int32_t yarn_orig_ctx;
    enum llama_pooling_type pooling_type; // 0 = LLAMA_POOLING_TYPE_UNSPECIFIED
    bool main_gpu;
    float *tensor_split;        // split across multiple GPUs
    bool logits_all;            // compute logits for all tokens
    bool embedded_tensors;
    bool offload_k_cache;
    bool offload_v_cache;
    char **rpc_servers;
    bool use_mmap;              // memory-map the model
    bool use_mlock;             // force system to keep model in RAM
    bool use_direct_io;         // use DirectIO for model file
    bool no_alloc;              // don't allocate context buffers
};

// Load a model
struct llama_model *llama_load_model_from_file(
    const char *path_model,
    struct llama_model_params params
);

// Get model info
int32_t llama_n_ctx_train(const struct llama_model *model);
int32_t llama_n_embd(const struct llama_model *model);
int32_t llama_n_vocab(const struct llama_model *model);
```

### Context

```c
struct llama_context_params {
    uint32_t seed;
    int32_t n_ctx;              // context size
    int32_t n_batch;            // logical maximum batch size
    int32_t n_ubatch;           // physical maximum batch size
    int32_t n_seq_max;          // max sequences
    enum llama_rope_scaling_type rope_scaling_type;
    float rope_freq_base;
    float rope_freq_scale;
    int32_t n_threads;          // threads for prompt processing
    int32_t n_threads_batch;    // threads for batch processing
    enum llama_pooling_type pooling_type;
    bool flash_attn;            // Flash Attention
    bool kv_unified;            // unified KV cache
    bool kv_offload;            // KV cache offloading
    bool embeddings;            // enable embeddings
    bool expert_applied;
    bool sweep_context;
    bool defrag_after_tokens;
    bool spm_infill;
    bool harness_dump_pool;
    bool kv_self_shift;
    bool host_override;
    bool cache_controled_output;
    bool svd_precompute;
    bool svd_recurrent;
    bool no_perf;               // disable performance profiling
};

struct llama_context *llama_init_from_model(
    struct llama_model *model,
    struct llama_context_params params
);
```

### Batch Decoding

```c
struct llama_batch {
    int32_t n_tokens;
    llama_token *tokens;
    float *embd;
    int32_t *pos;
    int32_t *n_seq_id;
    int8_t *logits;
    int32_t *cell_padding;

    // For recurrent models
    bool *all_seq_id;
};

// Allocate batch
struct llama_batch llama_batch_init(int32_t n_tokens, int32_t embd, int32_t n_seq_max);

// Decode batch (returns 0 on success)
int32_t llama_decode(struct llama_context *ctx, struct llama_batch batch);
```

### Sampler Chain

The sampling API uses a chain of samplers applied in order:

```c
struct llama_sampler *llama_sampler_chain_init(
    const struct llama_sampler_chain_params *params
);

// Add samplers
llama_sampler_chain_add(chain, llama_sampler_init_top_k(40), LLAMA_SAMPLER_CHAIN_NORMAL);
llama_sampler_chain_add(chain, llama_sampler_init_top_p(0.95, 1), LLAMA_SAMPLER_CHAIN_NORMAL);
llama_sampler_chain_add(chain, llama_sampler_init_temp(0.8f), LLAMA_SAMPLER_CHAIN_NORMAL);

// Sample next token
llama_token llama_sampler_sample(struct llama_sampler *smpl, struct llama_context *ctx, int32_t idx);

// Accept token (important for grammar-constrained generation)
void llama_sampler_accept(struct llama_sampler *smpl, bool apply_repetition_penalties);
```

Available samplers: `top_k`, `top_p`, `min_p`, `temp`, `dry`, `xtc`, `typ_p`, `grammar`, `dist`, `penalties`, `migroustat`.

### Tokenization

```c
// Text to tokens
int32_t llama_tokenize(
    const struct llama_model *model,
    const char *text, int32_t text_len,
    llama_token *tokens, int32_t n_tokens_max,
    bool add_bos, bool special
);

// Token to text (into buffer)
int32_t llama_token_to_piece(
    const struct llama_model *model,
    llama_token token,
    char *buf, int32_t length
);
```

### LoRA Adapters

```c
// Load LoRA adapter
struct llama_lora_adapter *llama_lora_adapter_init(
    struct llama_context *ctx,
    const char *path_lora
);

// Apply to context (scale 0.0-1.0)
int32_t llama_set_adapter_lora(struct llama_context *ctx,
    struct llama_lora_adapter *adapter, float scale);

// Remove adapter
void llama_lora_adapter_free(struct llama_lora_adapter *adapter);
```

### KV Cache

```c
// Clear KV cache
void llama_kv_cache_clear(struct llama_context *ctx);

// Sequence operations
void llama_kv_cache_seq_rm(struct llama_context *ctx, int32_t seq_id, int32_t p0, int32_t p1);
void llama_kv_cache_seq_add(struct llama_context *ctx, int32_t seq_id, int32_t p0, int32_t p1, int32_t shift);
void llama_kv_cache_seq_cp(struct llama_context *ctx, int32_t seq_id_src, int32_t seq_id_dst, int32_t p0, int32_t p1);

// State save/load (for branching)
size_t llama_state_get_size(struct llama_context *ctx);
int64_t llama_state_seq_save_ext(struct llama_context *ctx, uint8_t *dst, size_t size, int32_t seq_id);
int64_t llama_state_seq_load_ext(struct llama_context *ctx, const uint8_t *src, size_t size, int32_t seq_id);
```

### Chat Templates

```c
// Apply chat template
char *llama_model_chat_apply_template(
    const struct llama_model *model,
    const char *template_name,
    const char **names,       // role names
    const char **contents,    // message contents
    bool *add_assistant,      // whether to add assistant prefix
    int32_t n_messages
);
```

### Performance Metrics

```c
struct llama_perf_context_data {
    float t_sample_ms;
    float t_p_eval_ms;
    float t_eval_ms;
    int32_t n_sample;
    int32_t n_p_eval;
    int32_t n_eval;
};

struct llama_perf_context_data llama_perf_context(struct llama_context *ctx);
```

## Thread Pool API

```c
struct llama_threadpool_params {
    int n_threads;
    bool strict_cpu;
    enum ggml_sched_priority priority;
    uint64_t cpu_mask;
    bool poll;
    int poll_mode;
};

struct llama_threadpool *llama_threadpool_init(
    struct llama_threadpool_params params
);
```

## Cleanup

```c
void llama_free(struct llama_context *ctx);
void llama_free_model(struct llama_model *model);
void llama_threadpool_free(struct llama_threadpool *pool);
```

## API Changelog

Track breaking changes at https://github.com/ggml-org/llama.cpp/issues/9289. Recent changes include:

- Removal of `llama_kv_self_*` API (replaced by `llama_kv_cache_*`)
- Addition of `llama_sampler_init_grammar_lazy` for lazy grammars with triggers
- Backend sampling API (`--backend-sampling`)
- New `llama_model_n_embd_inp()` and `llama_model_n_embd_out()`
- `kv_unified` flag in context params
- `swa_full` flag for full-size SWA cache

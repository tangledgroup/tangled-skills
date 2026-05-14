# ☑ Plan: PyTorch 2.12.0 Skill Generation

**Depends On:** NONE
**Created:** 2026-05-14T00:00:00Z
**Updated:** 2026-05-14T00:00:00Z
**Current Phase:** ☑ Phase 5
**Current Task:** ☑ Task 5.3

## ☑ Phase 1 Content Research and Crawling

- ☑ Task 1.1 Fetch PyTorch release blog (2.12) and extract key features, performance changes, deprecations
  - Source: https://pytorch.org/blog/pytorch-2-12-release-blog/
  - Already fetched to /tmp/pytorch-212-blog.md — review for content extraction

- ☑ Task 1.2 Fetch PyTorch docs index (v2.12) and catalog all API packages/modules
  - Source: https://pytorch.org/docs/2.12/index.html
  - Already fetched to /tmp/pytorch-docs-212.md — review for module inventory

- ☑ Task 1.3 Fetch PyTorch main components page for core concepts overview
  - Source: https://pytorch.org/docs/2.12/user_guide/pytorch_main_components.html
  - Already fetched to /tmp/pytorch-components.md — review

- ☑ Task 1.4 Fetch torch.compiler documentation (core concepts, programming model)
  - Source: https://pytorch.org/docs/2.12/user_guide/torch_compiler/core_concepts.html
  - Already fetched to /tmp/pytorch-compiler-core.md — review for compiler content

- ☑ Task 1.5 Fetch torch.export documentation
  - Source: https://pytorch.org/docs/2.12/user_guide/torch_compiler/export.html
  - Already fetched to /tmp/pytorch-export.md — review

- ☑ Task 1.6 Fetch distributed training docs (DDP, FSDP)
  - Sources: https://pytorch.org/docs/2.12/notes/ddp.html, https://pytorch.org/docs/2.12/fsdp.html
  - Already fetched to /tmp/pytorch-ddp.md and /tmp/pytorch-fsdp.md — review

- ☑ Task 1.7 Fetch quantization documentation
  - Source: https://pytorch.org/docs/2.12/quantization.html
  - Already fetched to /tmp/pytorch-quant.md — review

- ☑ Task 1.8 Fetch autograd mechanics and extending PyTorch docs
  - Sources: https://pytorch.org/docs/2.12/notes/autograd.html, https://pytorch.org/docs/2.12/notes/extending.html
  - Already fetched to /tmp/pytorch-autograd-notes.md and /tmp/pytorch-extending.md — review

- ☑ Task 1.9 Fetch GitHub release notes (v2.12.0) for breaking changes and full changelog
  - Source: https://github.com/pytorch/pytorch/releases/tag/v2.12.0
  - Already fetched to /tmp/pytorch-release.md — review

- ☑ Task 1.10 Fetch accelerator integration docs (device management, AMP, profiler)
  - Source: https://pytorch.org/docs/2.12/accelerator/index.html
  - Need to fetch for cross-backend content (CUDA, XPU, MPS, ROCm)

## ☑ Phase 2 Content Analysis and Structure Design

- ☑ Task 2.1 Determine reference file split strategy based on crawled content
  - Analyze which topics form natural reference domains
  - Target: ~6-8 reference files covering distinct subdomains
  - Candidate splits: Tensors & Autograd, Neural Network API, torch.compile, torch.export, Data Loading, Distributed Training, Quantization & AMP, Accelerators

- ☑ Task 2.2 Draft YAML header with name, description, tags, category
  - Name: pytorch-2-12-0
  - Description: Follow formula (WHAT + WHEN + key terms)
  - Tags: 3-7 relevant tags including pytorch, deep-learning, tensors, etc.

- ☑ Task 2.3 Draft SKILL.md outline (Overview, When to Use, Core Concepts, Usage Examples, Advanced Topics navigation)
  - Keep under 500 lines
  - Include quick-start code examples inline
  - Link to reference files from Advanced Topics section

- ☑ Task 2.4 Define each reference file's scope and table of contents
  - List all reference files with their topics
  - Ensure no overlap between files
  - Verify one-level-deep structure (no chained references)

## ☑ Phase 3 Write SKILL.md

- ☑ Task 3.1 Write YAML header block
  - Depends on: Task 2.2
  - Validated name, description, version 0.1.0, MIT license

- ☑ Task 3.2 Write Overview section
  - PyTorch as flexible deep learning framework
  - Core capabilities: tensors, autograd, nn.Module, data loading, compilation, export

- ☑ Task 3.3 Write When to Use section with specific scenarios
  - Model training, research prototyping, production deployment, multi-GPU training, etc.

- ☑ Task 3.4 Write Core Concepts section (concise, high-level)
  - Tensors, Autograd, nn.Module, DataLoaders — brief explanations with code snippets

- ☑ Task 3.5 Write Usage Examples section
  - Quick-start: create tensor → build model → train loop → inference
  - torch.compile example
  - torch.export example

- ☑ Task 3.6 Write Advanced Topics navigation hub
  - Link to all reference files with brief descriptions
  - Depends on: Task 2.4 (reference file definitions)

## ☑ Phase 4 Write Reference Files

- ☑ Task 4.1 Write reference/01-tensors-and-autograd.md
  - Tensor creation, dtypes, device placement, operations
  - Autograd mechanics: computational graph, gradients, backward pass
  - Broadcasting semantics
  - Custom autograd.Function

- ☑ Task 4.2 Write reference/02-neural-network-api.md
  - nn.Module architecture and lifecycle
  - Common layers (Linear, Conv2d, LSTM, Transformer)
  - Loss functions and activation functions
  - Optimizers (SGD, Adam, AdamW, RMSprop, Adagrad fused)
  - Weight initialization

- ☑ Task 4.3 Write reference/03-data-loading.md
  - Dataset and DataLoader APIs
  - Custom datasets and data transforms
  - Sampling strategies and collate functions
  - Multiprocessing data loading best practices

- ☑ Task 4.4 Write reference/04-torch-compile.md
  - torch.compile basics and programming model
  - TorchDynamo tracing and graph breaks
  - Dynamic shapes support
  - Performance profiling and troubleshooting
  - CUDA Graphs integration (including torch.cond in graphs)
  - torch.accelerator.Graph API (new in 2.12)

- ☑ Task 4.5 Write reference/05-torch-export.md
  - torch.export workflow for model serialization
  - Export programming model and IR specification
  - PT2 archive format
  - Control flow operators (cond, while_loop, scan, map)
  - Microscaling (MX) quantization export support (new in 2.12)
  - AOTInductor ahead-of-time compilation

- ☑ Task 4.6 Write reference/06-distributed-training.md
  - Distributed Data Parallel (DDP) patterns
  - FullyShardedDataParallel (FSDP) and fully_shard API
  - ProcessGroup management and collective operations
  - Multi-GPU/multi-node profiling improvements (new in 2.12)
  - torch.distributed.checkpoint for distributed saving
  - Tensor Parallelism and Pipeline Parallelism
  - torchcomms integration preview

- ☑ Task 4.7 Write reference/07-quantization-and-amp.md
  - Automatic Mixed Precision (AMP) with torch.amp
  - Dynamic quantization, static quantization, PTQ
  - Quantization-aware training (QAT)
  - Microscaling (MX) formats: MXFP4, MXFP6, MXFP8
  - Fused optimizers (Adam, AdamW, SGD, Adagrad)

- ☑ Task 4.8 Write reference/08-accelerators-and-platforms.md
  - CUDA support and CUDA Graph kernel annotations (new in 2.12)
  - ROCm features: expandable segments, rocSHMEM, FlexAttention pipelining
  - Apple MPS: Metal-4 offline shader compilation (new in 2.12)
  - Intel XPU support
  - torch.accelerator device management and hooks
  - CUDA Green Context workqueue limit (new in 2.12)

## ☑ Phase 5 Validate and Finalize

- ☑ Task 5.1 Run structural validator on SKILL.md and all reference files
  - bash scripts/validate-skill.sh .agents/skills/pytorch-2-12-0
  - Fix any reported errors

- ☑ Task 5.2 LLM judgment review of all files
  - Check content accuracy against fetched sources
  - Verify no hallucinated APIs or features
  - Ensure consistent terminology
  - Confirm concise writing without over-explanation
  - Verify single recommended approach per topic

- ☑ Task 5.3 Run gen-skills-table.sh to update README.md
  - bash scripts/gen-skills-table.sh .agents/skills README.md

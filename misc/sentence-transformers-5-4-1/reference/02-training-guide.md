# Training Guide

Sentence Transformers 5.4.1 uses the `SentenceTransformerTrainer` API (Hugging Face Trainer-compatible) for training. The legacy `model.fit()` API is deprecated but available as `model.old_fit()` for backward compatibility.

## Training Overview

### Basic Training Pattern

```python
from sentence_transformers import SentenceTransformer, SentenceTransformerTrainer, SentenceTransformerTrainingArguments
from sentence_transformers.losses import CosineSimilarityLoss
from sentence_transformers.datasets import SentencesDataset
from datasets import Dataset

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Prepare training data as a Hugging Face Dataset
train_dataset = Dataset.from_dict({
    "sentence_1": ["I love programming", "The weather is nice"],
    "sentence_2": ["Coding is fun", "It's beautiful outside"],
    "label": [0.9, 0.85],
})

# Define loss function
loss = CosineSimilarityLoss()

# Configure training
args = SentenceTransformerTrainingArguments(
    output_dir="output/my-model",
    num_train_epochs=4,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
    warmup_ratio=0.1,
    fp16=False,          # set True for mixed precision
    bf16=True,           # set True for bfloat16 (AMP GPUs)
    logging_steps=100,
    eval_strategy="steps",
    eval_steps=100,
    save_strategy="steps",
    save_steps=500,
)

# Create trainer
trainer = SentenceTransformerTrainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    loss=loss,
)

# Train
trainer.train()
```

### Training with Prompts

Prompts can be specified per dataset column during training:

```python
args = SentenceTransformerTrainingArguments(
    output_dir="output/my-model",
    num_train_epochs=4,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
    prompts={"sentence_1": "query: ", "sentence_2": "passage: "},
)
```

Four prompt formats are accepted:
1. `str` — single prompt for all columns
2. `Dict[str, str]` — column name → prompt mapping
3. `Dict[str, str]` (dataset-level) — dataset name → prompts
4. `Dict[str, Dict[str, str]]` — dataset name → column name → prompt

## Loss Functions

### Embedding Model Losses (SentenceTransformer)

30+ loss functions available:

**Similarity-based:**
- `CosineSimilarityLoss` — cosine similarity regression, standard for STS tasks
- `MSELoss` — mean squared error between predicted and target similarity
- `MarginMSELoss` — MSE with margin for positive/negative pairs
- `CoSENTLoss` — combines cosine and Euclidean similarity
- `AnglELoss` — angle-based embedding loss

**Contrastive:**
- `ContrastiveLoss` — pushes dissimilar pairs apart, similar pairs together
- `OnlineContrastiveLoss` — online variant with margin
- `MultipleNegativesRankingLoss` — in-batch negative sampling, ideal for large batches
- `MultipleNegativesSymmetricRankingLoss` — symmetric variant (both directions)
- `CachedMultipleNegativesRankingLoss` — cached version for efficiency
- `CachedMultipleNegativesSymmetricRankingLoss`

**Triplet:**
- `TripletLoss` — standard triplet (anchor, positive, negative)
- `BatchHardTripletLoss` — hardest examples in batch
- `BatchSemiHardTripletLoss` — semi-hard mining
- `BatchAllTripletLoss` — all triplets in batch
- `BatchHardSoftMarginTripletLoss` — soft margin variant

**Advanced:**
- `MatryoshkaLoss` — trains embeddings at multiple dimensions (Matryoshka representation)
- `Matryoshka2dLoss` — 2D Matryoshka for asymmetric query/document
- `SoftmaxLoss` — classification-style softmax over labels
- `DenoisingAutoEncoderLoss` — denoising autoencoder objective
- `GISTEmbedLoss` — GIST-based embedding loss
- `CachedGISTEmbedLoss`
- `ContrastiveTensionLoss` — contrastive tension with hard negatives
- `ContrastiveTensionLossInBatchNegatives`
- `GlobalOrthogonalRegularizationLoss` — encourages orthogonal representations
- `MegaBatchMarginLoss` — margin loss over mega-batches
- `DistillKLDivLoss` — KL divergence for knowledge distillation
- `AdaptiveLayerLoss` — adaptive layer-wise training

### CrossEncoder Losses

15+ loss functions:

- `BinaryCrossEntropyLoss` — binary classification
- `CrossEntropyLoss` — multi-class classification
- `MultipleNegativesRankingLoss` — in-batch negatives
- `CachedMultipleNegativesRankingLoss`
- `MarginMSELoss` — margin-based regression
- `MSELoss` — standard MSE
- `ListNetLoss` — listwise ranking
- `ListMLELoss` — maximum likelihood estimation for lists
- `PListMLELoss` — probabilistic list MLE
- `LambdaLoss` — lambda-ranking with NDCG schemes
- `RankNetLoss` — pairwise ranking

LambdaRank schemes: `NoWeightingScheme`, `NDCGLoss1Scheme`, `NDCGLoss2Scheme`, `NDCGLoss2PPScheme`.

### SparseEncoder Losses

13+ loss functions:

- `SpladeLoss` — SPLADE-specific objective
- `CachedSpladeLoss`
- `SparseMultipleNegativesRankingLoss`
- `SparseTripletLoss`
- `SparseMarginMSELoss`
- `SparseCosineSimilarityLoss`
- `SparseMSELoss`
- `SparseAnglELoss`
- `SparseCoSENTLoss`
- `SparseDistillKLDivLoss`
- `CSRLoss` — CSR (Compressed Sparse Row) objective
- `CSRReconstructionLoss`
- `FlopsLoss` — computational complexity regularization

## Evaluators

Evaluators run during training to monitor model quality:

```python
from sentence_transformers.evaluation import (
    EmbeddingSimilarityEvaluator,
    InformationRetrievalEvaluator,
    ParaphraseMiningEvaluator,
    RerankingEvaluator,
    TripletEvaluator,
    BinaryClassificationEvaluator,
    LabelAccuracyEvaluator,
    MSEEvaluator,
    TranslationEvaluator,
    NanoBEIREvaluator,
)
from sentence_transformers.evaluation import SequentialEvaluator

evaluator = EmbeddingSimilarityEvaluator(
    sentences1=val_data["sentence_1"],
    sentences2=val_data["sentence_2"],
    labels=val_data["scores"],
    name="validation",
)

args = SentenceTransformerTrainingArguments(
    output_dir="output/my-model",
    num_train_epochs=4,
    eval_strategy="steps",
    eval_steps=100,
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    loss=loss,
    evaluator=evaluator,
)
```

Run multiple evaluators with `SequentialEvaluator([eval1, eval2, ...])`.

## Datasets

### Hugging Face Datasets (Recommended)

Standard `datasets.Dataset` objects work directly:

```python
from datasets import load_dataset

dataset = load_dataset("sentence-transformers/natural-questions")
```

### SentencesDataset

For simple sentence-pair training:

```python
from sentence_transformers.datasets import SentencesDataset, ParallelSentencesDataset
from sentence_transformers.readers import InputExample

# From InputExamples
examples = [
    InputExample(texts=["sentence A", "sentence B"], label=0.8),
    InputExample(texts=["sentence C", "sentence D"], label=0.3),
]
dataset = SentencesDataset(model=model, samples=examples)

# Parallel sentences (for multilingual training)
parallel_dataset = ParallelSentencesDataset(sentences={
    "en": ["Hello", "World"],
    "de": ["Hallo", "Welt"],
})
```

### Data Readers (Legacy)

Deprecated data readers available in `sentence_transformers.readers`: `STSBenchmarkDataReader`, `NLIDataReader`, `TripletReader`, `PairedFilesReader`. These are for backward compatibility with v2.x training.

## Batch Samplers

Control how samples are grouped into batches:

```python
from sentence_transformers.training_args import BatchSamplers

args = SentenceTransformerTrainingArguments(
    output_dir="output/my-model",
    batch_sampler=BatchSamplers.NO_DUPLICATES,  # avoid duplicate sentences in batch
    # Other options: BATCH_SAMPLER (default), ADE_BATCH_SAMPLER
)
```

For multi-dataset training:

```python
from sentence_transformers.training_args import MultiDatasetBatchSamplers

args = SentenceTransformerTrainingArguments(
    output_dir="output/my-model",
    multi_dataset_batch_sampler=MultiDatasetBatchSamplers.PROPORTIONAL,
    # Other options: ROUND_ROBIN
)
```

## Multi-task and Multi-dataset Training

Train on multiple datasets simultaneously using `DatasetDict`:

```python
from datasets import DatasetDict

train_datasets = DatasetDict({
    "sts": sts_dataset,
    "nli": nli_dataset,
    "paraphrases": paraphrase_dataset,
})

# Different loss per dataset
losses = {
    "sts": CosineSimilarityLoss(),
    "nli": MultipleNegativesRankingLoss(),
    "paraphrases": ContrastiveLoss(),
}

trainer = SentenceTransformerTrainer(
    model=model,
    args=args,
    train_dataset=train_datasets,
    loss=losses,
)
```

## CrossEncoder and SparseEncoder Training

Same Trainer pattern applies:

```python
from sentence_transformers import CrossEncoder, CrossEncoderTrainer, CrossEncoderTrainingArguments
from sentence_transformers.cross_encoder.losses import BinaryCrossEntropyLoss

ce_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
ce_loss = BinaryCrossEntropyLoss()

ce_args = CrossEncoderTrainingArguments(
    output_dir="output/cross-encoder",
    num_train_epochs=4,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
)

ce_trainer = CrossEncoderTrainer(
    model=ce_model,
    args=ce_args,
    train_dataset=train_dataset,
    loss=ce_loss,
)
ce_trainer.train()
```

SparseEncoder uses `SparseEncoderTrainer` and `SparseEncoderTrainingArguments` with the same pattern.

## Learning Rate Mapping

Set different learning rates for different model parts:

```python
args = SentenceTransformerTrainingArguments(
    output_dir="output/my-model",
    learning_rate_mapping={
        r"SparseStaticEmbedding\.*": 1e-3,
        r"Transformer\.*": 2e-5,
    },
)
```

## PEFT Support

Parameter-Efficient Fine-Tuning (PEFT/LoRA) is supported through the `PeftAdapterMixin` on all model types. Pass PEFT configuration via `model_kwargs`.

## Hard Negative Mining

```python
from sentence_transformers import mine_hard_negatives

hard_negatives = mine_hard_negatives(
    model=model,
    corpus=corpus_texts,
    queries=query_texts,
    positives=positive_texts,
    top_k=10,
)
```

## Multi-GPU and Distributed Training

The Trainer integrates with Hugging Face Accelerate for multi-GPU training. Set `num_processes` or use the `accelerate` CLI launcher. The `all_gather` and `all_gather_with_grad` utilities support distributed contrastive losses.
